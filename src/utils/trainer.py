import os
import torch
import torch.nn as nn
import copy
import wandb
import numpy as np
import random # ★ 추가됨
from mpi4py import MPI

import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import torchvision.models as models

from torch.utils.data import DataLoader

from data.data import get_dataloader, get_next_batch
from utils.eval import evaluate_global_snr, evaluate_global_fl
from models.model import AWGNChannel, RayleighChannel, ClientResNet18v2, ServerResNet18, SCM_Pretraining_Model, SCMLoss, GlobalNetworkStatusMonitor, apply_semantic_spreading

# MPI 태그 정의
TAG_FORWARD = 1
TAG_BACKWARD = 2
TAG_AGG_REQ = 3
TAG_AGG_RES = 4


def _mpi_trace_enabled(args, batch_idx=None):
    if not getattr(args, "mpi_trace_enable", 0):
        return False
    if batch_idx is None:
        return True
    return batch_idx == 0


def _mpi_trace(logger, message):
    formatted = f"[MPI TRACE] {message}"
    if logger:
        logger.info(formatted)
    else:
        print(formatted)

def compute_channel_kl(mu, log_var):
    """
    각 채널(차원)별 KL Divergence를 계산
    Return shape: [Batch_size, Channel_dim]
    """
    kl = -0.5 * (1 + log_var - mu.pow(2) - log_var.exp())
    return kl


def compute_semantic_power_scales(active_kl, alpha):
    if active_kl.numel() == 0:
        return active_kl

    centered_kl = active_kl - active_kl.mean()
    normalized_kl = centered_kl / (active_kl.std(unbiased=False) + 1e-6)
    power_weights = torch.softmax(alpha * normalized_kl, dim=0) * active_kl.numel()
    return torch.sqrt(power_weights + 1e-8)


def build_semidense_active_indices(score_vector, base_mask, group_size, group_topk):
    active_indices = torch.nonzero(base_mask > 0).squeeze(-1)
    active_budget = int(active_indices.numel())
    if active_budget == 0:
        return active_indices

    total_dim = int(base_mask.numel())
    if group_size <= 1 or total_dim % group_size != 0:
        return active_indices

    n_groups = total_dim // group_size
    group_topk = max(1, min(int(group_topk), int(group_size)))
    n_target_groups = max(1, min(n_groups, (active_budget + group_topk - 1) // group_topk))

    scores = score_vector.detach().float()
    scores = torch.where(base_mask > 0, scores, torch.full_like(scores, -1e9))
    grouped_scores = scores.view(n_groups, group_size)
    group_strength = grouped_scores.max(dim=1).values

    top_groups = torch.topk(group_strength, k=n_target_groups).indices
    candidate_indices = []
    for group_idx in top_groups.tolist():
        start = group_idx * group_size
        local_scores = grouped_scores[group_idx]
        local_k = min(group_topk, int(torch.sum(local_scores > -1e8).item()))
        if local_k <= 0:
            continue
        local_top = torch.topk(local_scores, k=local_k).indices + start
        candidate_indices.append(local_top)

    if candidate_indices:
        candidate_indices = torch.unique(torch.cat(candidate_indices))
    else:
        candidate_indices = active_indices

    if candidate_indices.numel() < active_budget:
        selected_mask = torch.zeros(total_dim, dtype=torch.bool, device=scores.device)
        selected_mask[candidate_indices] = True
        remaining_scores = torch.where(~selected_mask, scores, torch.full_like(scores, -1e9))
        extra_k = min(active_budget - int(candidate_indices.numel()), int(torch.sum(remaining_scores > -1e8).item()))
        if extra_k > 0:
            extra_indices = torch.topk(remaining_scores, k=extra_k).indices
            candidate_indices = torch.unique(torch.cat([candidate_indices, extra_indices]))

    candidate_scores = scores[candidate_indices]
    final_k = min(active_budget, int(candidate_indices.numel()))
    final_indices = candidate_indices[torch.topk(candidate_scores, k=final_k).indices]
    return torch.sort(final_indices).values


def apply_support_floor_mask(score_vector, current_mask, min_active):
    current_indices = torch.nonzero(current_mask > 0).squeeze(-1)
    current_active = int(current_indices.numel())
    min_active = int(min_active)
    if min_active <= 0 or current_active >= min_active:
        return current_mask

    total_dim = int(current_mask.numel())
    target_active = min(min_active, total_dim)
    scores = score_vector.detach().float()

    selected_mask = current_mask > 0
    remaining_scores = torch.where(~selected_mask, scores, torch.full_like(scores, -1e9))
    extra_k = min(target_active - current_active, int(torch.sum(remaining_scores > -1e8).item()))
    if extra_k <= 0:
        return current_mask

    extra_indices = torch.topk(remaining_scores, k=extra_k).indices
    updated_mask = current_mask.clone()
    updated_mask[extra_indices] = 1.0
    return updated_mask


def build_base_refinement_indices(score_vector, base_mask, base_support_k, refinement_support_k):
    total_dim = int(base_mask.numel())
    scores = score_vector.detach().float()
    base_support_k = max(0, min(int(base_support_k), total_dim))
    refinement_support_k = max(0, min(int(refinement_support_k), total_dim))

    if base_support_k == 0 and refinement_support_k == 0:
        return torch.nonzero(base_mask > 0).squeeze(-1)

    selected = []
    if base_support_k > 0:
        base_indices = torch.topk(scores, k=base_support_k).indices
        selected.append(base_indices)

    if refinement_support_k > 0:
        base_selected_mask = torch.zeros(total_dim, dtype=torch.bool, device=scores.device)
        if selected:
            base_selected_mask[torch.cat(selected)] = True
        remaining_scores = torch.where((base_mask > 0) & (~base_selected_mask), scores, torch.full_like(scores, -1e9))
        valid_refine = int(torch.sum(remaining_scores > -1e8).item())
        if valid_refine > 0:
            refinement_indices = torch.topk(remaining_scores, k=min(refinement_support_k, valid_refine)).indices
            selected.append(refinement_indices)

    if not selected:
        return torch.nonzero(base_mask > 0).squeeze(-1)

    return torch.sort(torch.unique(torch.cat(selected))).values


def build_fixed_base_variable_refinement_indices(
    semantic_scores,
    semantic_candidate_mask,
    channel_scores,
    base_support_k,
    refinement_support_max_k,
    snr_normalized,
):
    total_dim = int(semantic_candidate_mask.numel())
    semantic_scores = semantic_scores.detach().float()
    channel_scores = channel_scores.detach().float()
    semantic_candidate_mask = semantic_candidate_mask > 0

    base_support_k = max(0, min(int(base_support_k), total_dim))
    refinement_support_max_k = max(0, min(int(refinement_support_max_k), total_dim))
    snr_normalized = float(max(0.0, min(1.0, snr_normalized)))

    base_indices = semantic_scores.new_empty(0, dtype=torch.long)
    if base_support_k > 0:
        base_indices = torch.topk(semantic_scores, k=base_support_k).indices

    refinement_budget = int(round(refinement_support_max_k * snr_normalized))
    if refinement_budget <= 0:
        return torch.sort(base_indices).values, int(base_indices.numel()), 0

    refine_candidate_mask = semantic_candidate_mask.clone()
    if base_indices.numel() > 0:
        refine_candidate_mask[base_indices] = False

    remaining_scores = torch.where(refine_candidate_mask, channel_scores, torch.full_like(channel_scores, -1e9))
    valid_refine = int(torch.sum(remaining_scores > -1e8).item())
    if valid_refine <= 0:
        return torch.sort(base_indices).values, int(base_indices.numel()), 0

    refinement_budget = min(refinement_budget, valid_refine)
    refinement_indices = torch.topk(remaining_scores, k=refinement_budget).indices
    final_indices = torch.sort(torch.unique(torch.cat([base_indices, refinement_indices]))).values
    return final_indices, int(base_indices.numel()), int(refinement_indices.numel())


def _minmax_normalize(score_vector):
    score_vector = score_vector.detach().float()
    min_val = torch.min(score_vector)
    max_val = torch.max(score_vector)
    range_val = max_val - min_val
    if float(range_val.item()) <= 1e-12:
        return torch.zeros_like(score_vector)
    return (score_vector - min_val) / range_val


def _mean_normalize(score_vector):
    score_vector = score_vector.detach().float()
    return score_vector / (score_vector.mean() + 1e-6)


def build_topk_mask(score_vector, candidate_mask, topk):
    total_dim = int(candidate_mask.numel())
    topk = max(0, min(int(topk), total_dim))
    candidate_mask = candidate_mask > 0
    if topk <= 0 or int(torch.sum(candidate_mask).item()) <= 0:
        return torch.zeros_like(score_vector, dtype=torch.float32)

    scores = score_vector.detach().float()
    masked_scores = torch.where(candidate_mask, scores, torch.full_like(scores, -1e9))
    valid_k = min(topk, int(torch.sum(masked_scores > -1e8).item()))
    if valid_k <= 0:
        return torch.zeros_like(score_vector, dtype=torch.float32)

    selected_indices = torch.topk(masked_scores, k=valid_k).indices
    selected_mask = torch.zeros_like(score_vector, dtype=torch.float32)
    selected_mask[selected_indices] = 1.0
    return selected_mask


def build_semantic_aware_fixed_base_variable_refinement_indices(
    semantic_scores,
    semantic_candidate_mask,
    channel_scores,
    channel_candidate_mask,
    base_support_k,
    refinement_support_max_k,
    snr_normalized,
    semantic_weight,
    channel_weight,
):
    total_dim = int(semantic_scores.numel())
    semantic_scores = semantic_scores.detach().float()
    channel_scores = channel_scores.detach().float()
    semantic_candidate_mask = semantic_candidate_mask > 0
    channel_candidate_mask = channel_candidate_mask > 0

    base_support_k = max(0, min(int(base_support_k), total_dim))
    refinement_support_max_k = max(0, min(int(refinement_support_max_k), total_dim))
    snr_normalized = float(max(0.0, min(1.0, snr_normalized)))
    semantic_weight = float(semantic_weight)
    channel_weight = float(channel_weight)

    base_indices = semantic_scores.new_empty(0, dtype=torch.long)
    semantic_candidate_count = int(torch.sum(semantic_candidate_mask).item())
    if base_support_k > 0:
        if semantic_candidate_count > 0:
            candidate_scores = torch.where(
                semantic_candidate_mask,
                semantic_scores,
                torch.full_like(semantic_scores, -1e9),
            )
            base_from_mask = min(base_support_k, semantic_candidate_count)
            if base_from_mask > 0:
                base_indices = torch.topk(candidate_scores, k=base_from_mask).indices

        if int(base_indices.numel()) < base_support_k:
            fallback_k = base_support_k - int(base_indices.numel())
            fallback_mask = torch.ones(total_dim, dtype=torch.bool, device=semantic_scores.device)
            if base_indices.numel() > 0:
                fallback_mask[base_indices] = False
            fallback_scores = torch.where(
                fallback_mask,
                semantic_scores,
                torch.full_like(semantic_scores, -1e9),
            )
            valid_fallback = int(torch.sum(fallback_scores > -1e8).item())
            if valid_fallback > 0:
                extra_indices = torch.topk(fallback_scores, k=min(fallback_k, valid_fallback)).indices
                base_indices = torch.sort(torch.unique(torch.cat([base_indices, extra_indices]))).values

    refinement_budget = int(round(refinement_support_max_k * snr_normalized))
    if refinement_budget <= 0:
        return torch.sort(base_indices).values, int(base_indices.numel()), 0

    semantic_norm = _minmax_normalize(semantic_scores)
    channel_norm = _minmax_normalize(channel_scores)
    mixed_scores = (semantic_weight * semantic_norm) + (channel_weight * channel_norm)

    base_selected_mask = torch.zeros(total_dim, dtype=torch.bool, device=semantic_scores.device)
    if base_indices.numel() > 0:
        base_selected_mask[base_indices] = True

    candidate_masks = [
        semantic_candidate_mask & channel_candidate_mask & (~base_selected_mask),
        semantic_candidate_mask & (~base_selected_mask),
        ~base_selected_mask,
    ]

    refinement_indices = semantic_scores.new_empty(0, dtype=torch.long)
    for candidate_mask in candidate_masks:
        remaining_scores = torch.where(
            candidate_mask,
            mixed_scores,
            torch.full_like(mixed_scores, -1e9),
        )
        valid_refine = int(torch.sum(remaining_scores > -1e8).item())
        if valid_refine <= 0:
            continue
        refinement_budget = min(refinement_budget, valid_refine)
        refinement_indices = torch.topk(remaining_scores, k=refinement_budget).indices
        break

    final_indices = torch.sort(torch.unique(torch.cat([base_indices, refinement_indices]))).values
    return final_indices, int(base_indices.numel()), int(refinement_indices.numel())


def build_importance_repetition_plan(score_vector, active_indices, base_mask, repetition_topk):
    if active_indices.numel() == 0 or repetition_topk <= 0:
        empty = active_indices.new_empty(0)
        return empty, empty, empty

    inactive_indices = torch.nonzero(base_mask <= 0).squeeze(-1)
    rep_k = min(int(repetition_topk), int(active_indices.numel()), int(inactive_indices.numel()))
    if rep_k <= 0:
        empty = active_indices.new_empty(0)
        return empty, empty, empty

    active_scores = torch.index_select(score_vector.detach().float(), 0, active_indices)
    rep_source_pos = torch.topk(active_scores, k=rep_k).indices
    rep_target_indices = torch.index_select(active_indices, 0, rep_source_pos)
    rep_aux_indices = inactive_indices[:rep_k]
    return rep_target_indices, rep_aux_indices, rep_source_pos

# ===================================================================
# 2. Server Logic
# ===================================================================
def _run_server(comm, server, num_clients, args, logger):
    criterion = torch.nn.CrossEntropyLoss()
    test_loader = get_dataloader(server.test_data, batch_size=250, is_train=False)
    
    if args.channel_type == 'awgn':
        test_channel = AWGNChannel(snr_db =args.snr_db).to(args.device)
    elif args.channel_type == 'rayleigh':
        test_channel = RayleighChannel(snr_db =args.snr_db).to(args.device)
    
    
    list_accuracies = []
    list_loss = []
    list_comm_cost = [] 
    list_mask = []
    
    total_comm_bytes = 0
    total_data_comm = 0  # 데이터(Smashed+Grad) 통신량
    total_model_comm = 0 # 모델(Weights) 통신량

    for round_idx in range(args.n_rounds):
        if logger: logger.info(f"[Server] Round {round_idx+1} Start")
        else: print(f"[Server] Round {round_idx+1} Start")
        
        server.model.train()
        num_batches = args.n_client_data // args.batch_size 
        epoch_loss = 0
        round_data_comm = 0
        round_model_comm = 0
        
        # ★ [추가] Local Epoch Loop (Aggregation 전에 3번 반복)
        for local_epoch in range(args.n_epochs):
        
            # --- [Step 1: Split Learning Loop] ---
            for batch_idx in range(num_batches):
                server.optimizer.zero_grad()
                
                smashed_data_list = []
                labels_list = []
                snr_list = [] 
                indices_list = [] 
                repetition_meta_list = []

                # 1. Receive Data from Clients
                for i in range(1, num_clients + 1):
                    if _mpi_trace_enabled(args, batch_idx):
                        _mpi_trace(logger, f"server round={round_idx+1} batch={batch_idx} waiting_forward_from={i}")
                    data_packet = comm.recv(source=i, tag=TAG_FORWARD)
                    if _mpi_trace_enabled(args, batch_idx):
                        recv_indices = data_packet.get('indices', None)
                        recv_k = int(recv_indices.numel()) if recv_indices is not None else -1
                        _mpi_trace(logger, f"server round={round_idx+1} batch={batch_idx} received_forward_from={i} k={recv_k}")
                    
                    s_data = data_packet['data'].to(args.device).requires_grad_(True)
                    label = data_packet['label'].to(args.device)
                    
                    if 'snr' in data_packet:
                        snr_list.append(data_packet['snr'].to(args.device))
                    
                    if 'indices' in data_packet:
                        # 클라이언트별 인덱스를 보관
                        indices_list.append(data_packet['indices'].to(args.device))

                    repeat_target_indices = data_packet.get('repeat_target_indices', None)
                    repeat_aux_indices = data_packet.get('repeat_aux_indices', None)
                    if repeat_target_indices is not None and repeat_aux_indices is not None:
                        repeat_target_indices = repeat_target_indices.to(args.device)
                        repeat_aux_indices = repeat_aux_indices.to(args.device)
                        if repeat_target_indices.numel() > 0 and repeat_aux_indices.numel() > 0:
                            target_exp = repeat_target_indices.unsqueeze(0).expand(s_data.size(0), -1)
                            aux_exp = repeat_aux_indices.unsqueeze(0).expand(s_data.size(0), -1)
                            repeat_avg = 0.5 * (
                                torch.index_select(s_data, 1, repeat_target_indices) +
                                torch.index_select(s_data, 1, repeat_aux_indices)
                            )
                            s_data = s_data.scatter(1, target_exp, repeat_avg)
                            s_data = s_data.scatter(1, aux_exp, torch.zeros_like(repeat_avg))
                            repetition_meta_list.append((repeat_target_indices, repeat_aux_indices))
                        else:
                            repetition_meta_list.append(None)
                    else:
                        repetition_meta_list.append(None)
                    
                    smashed_data_list.append(s_data)
                    labels_list.append(label)
                    
                # 2. Concatenate
                server_input = torch.cat(smashed_data_list, dim=0)
                server_input.retain_grad()
                server_labels = torch.cat(labels_list, dim=0)
                server_snr = torch.cat(snr_list, dim=0) if len(snr_list) > 0 else None
                
                # 3. Forward
                # ★ 수정: indices_list[0] 대신 전체 indices_list를 넘겨줍니다.
                # (디코더가 리스트를 받아 배치별로 처리할 수 있도록 모델 쪽도 확인이 필요합니다)
                if len(indices_list) > 0:
                    outputs = server.model(server_input, snr_val=server_snr, indices=indices_list)
                else:
                    outputs = server.model(server_input, snr_val=server_snr)

                loss = criterion(outputs, server_labels) 
                
                # 4. Backward
                loss.backward()
                server.optimizer.step()
                
                # [Server Logic - Step 5 수정]
                # 5. Send Gradients & 통신량 계산
                server_grads = server_input.grad.chunk(num_clients, dim=0)
                
                for i in range(1, num_clients + 1):
                    grad_full = server_grads[i-1] # [Batch, 4096]
                    repetition_meta = repetition_meta_list[i-1]
                    if repetition_meta is not None:
                        repeat_target_indices, repeat_aux_indices = repetition_meta
                        target_exp = repeat_target_indices.unsqueeze(0).expand(grad_full.size(0), -1)
                        aux_exp = repeat_aux_indices.unsqueeze(0).expand(grad_full.size(0), -1)
                        repeat_target_grad = 0.5 * torch.index_select(grad_full, 1, repeat_target_indices)
                        grad_full = grad_full.scatter(1, target_exp, repeat_target_grad)
                        grad_full = grad_full.scatter(1, aux_exp, repeat_target_grad)
                    
                    # =======================================================
                    # ★ 수정 포인트: 인덱스가 있을 때와 없을 때를 구분 ★
                    # =======================================================
                    if len(indices_list) > 0:
                        # SSFLv6 (우리 모델): 인덱스를 사용하여 슬라이싱 전송
                        current_indices = indices_list[i-1].reshape(-1)
                        grad_to_send = torch.index_select(grad_full, 1, current_indices)
                        index_overhead_bytes = current_indices.numel() * 2
                    else:
                        # Standard SFL: 인덱스가 없으므로 전체 기울기 전송
                        grad_to_send = grad_full
                        index_overhead_bytes = 0
                    
                    # 기울기 전송
                    if _mpi_trace_enabled(args, batch_idx):
                        _mpi_trace(logger, f"server round={round_idx+1} batch={batch_idx} sending_backward_to={i} grad_shape={tuple(grad_to_send.shape)}")
                    comm.send(grad_to_send.cpu(), dest=i, tag=TAG_BACKWARD)
                    
                    # =======================================================
                    # 통신량 계산 (Payload + Overhead)
                    # =======================================================
                    # Forward Data: 실제 전송된 0이 아닌 요소의 개수
                    forward_elements = torch.count_nonzero(smashed_data_list[i-1]).item()
                    
                    # Backward Data: 서버가 보낸 기울기 요소 개수
                    backward_elements = grad_to_send.numel() 
                    
                    # 합계 계산
                    batch_comm_bytes = (forward_elements * 4) + index_overhead_bytes + (backward_elements * 4)
                    
                    total_data_comm += batch_comm_bytes
                    round_data_comm += batch_comm_bytes

                epoch_loss += loss.item()

        # --- [Step 2: Aggregation Phase] ---
        if logger: logger.info("[Server] Aggregating Models...")
        else: print("[Server] Aggregating Models...")
        
        local_weights = []
        
        for i in range(1, num_clients + 1):
            comm.send("REQ", dest=i, tag=TAG_AGG_REQ)
            w = comm.recv(source=i, tag=TAG_AGG_RES)
            local_weights.append(w)
            
            for param in w.values():
                total_model_comm += param.numel() * 4
                round_model_comm += param.numel() * 4
                
        global_weights = server.global_client_model.state_dict()
        avg_weights = {}
        
        for key in local_weights[0].keys():
            # ★ 'w_o_cbfa' 가 알고리즘 이름에 없으면 특수 병합 수행
            if 'prior_mu.weight' in key and 'w_o_cbfa' not in args.algorithm:
                # 1. Class-Balanced Prior 전용 Aggregation
                num_classes = global_weights[key].size(0)
                
                new_weight = torch.zeros_like(global_weights[key]).to(args.device)
                update_counts = torch.zeros(num_classes, 1).to(args.device)

                for i in range(num_clients):
                    local_w = local_weights[i][key].to(args.device)
                    diff = torch.norm(local_w - global_weights[key], dim=1, keepdim=True)
                    mask = (diff > 1e-5).float() 
                    
                    new_weight += local_w * mask
                    update_counts += mask

                safe_counts = update_counts.clone()
                safe_counts[safe_counts == 0] = 1.0
                avg_w = new_weight / safe_counts
                
                no_update_mask = (update_counts == 0).float()
                result_w = avg_w * (1 - no_update_mask) + global_weights[key] * no_update_mask
                avg_weights[key] = result_w.cpu()

            else:
                # 2. 일반 가중치 FedAvg (w_o_cbfa일 경우 prior_mu.weight도 이쪽으로 빠짐)
                avg_weights[key] = copy.deepcopy(local_weights[0][key])
                for i in range(1, num_clients):
                    avg_weights[key] += local_weights[i][key]
                avg_weights[key] = torch.div(avg_weights[key], num_clients)
                
        server.global_client_model.load_state_dict(avg_weights)
        
        for i in range(1, num_clients + 1):
            comm.send(avg_weights, dest=i, tag=TAG_AGG_RES)
            
            for param in avg_weights.values():
                total_model_comm += param.numel() * 4
                round_model_comm += param.numel() * 4
                
        # --- Evaluation & Logging ---
        test_acc, test_loss, avg_mask_overlap = evaluate_global_snr(
            args,
            server.global_client_model, 
            server.model, 
            test_loader, 
            criterion,
            comm,
            channel=test_channel
        )
        avg_loss = epoch_loss / num_batches
        
        # MB 단위 변환
        total_comm = total_data_comm + total_model_comm
        comm_mb = total_comm / (1024 * 1024)
        data_mb = total_data_comm / (1024 * 1024)
        model_mb = total_model_comm / (1024 * 1024)
        
        round_data_mb = round_data_comm / (1024 * 1024)
        round_model_mb = round_model_comm / (1024 * 1024)
        print(f"[Round {round_idx+1}] Acc: {test_acc:.2f}%, Loss: {test_loss:.4f}, Total comm: {comm_mb:.2f} MB Total data comm: {data_mb:.2f} MB, Total model comm: {model_mb:.2f} MB (Data: {round_data_mb:.2f} MB, Model: {round_model_mb:.2f} MB)")

        log_msg = f"[Round {round_idx+1}] Acc: {test_acc:.2f}%, Loss: {test_loss:.4f}, Total comm: {comm_mb:.2f} MB, Total data comm: {data_mb:.2f} MB, Total model comm: {model_mb:.2f} (Data: {round_data_mb:.2f} MB, Model: {round_model_mb:.2f} MB, avg_mask_overlap: {avg_mask_overlap})"

        if logger: logger.info(log_msg)
        else: print(log_msg)

        list_mask.append(avg_mask_overlap)
        list_accuracies.append(test_acc)
        list_loss.append(test_loss)
        list_comm_cost.append(comm_mb)
        
    return list_accuracies, list_loss, list_comm_cost, list_mask


def _run_server_sc_usfl(comm, server, num_clients, args, logger):
    criterion = torch.nn.CrossEntropyLoss()
    test_loader = get_dataloader(server.test_data, batch_size=250, is_train=False)
    
    if args.channel_type == 'awgn':
        test_channel = AWGNChannel(snr_db=args.snr_db).to(args.device)
    elif args.channel_type == 'rayleigh':
        test_channel = RayleighChannel(snr_db=args.snr_db).to(args.device)
    
    list_accuracies = []
    list_loss = []
    list_comm_cost = [] 
    
    total_comm_bytes = 0
    total_data_comm = 0  
    total_model_comm = 0 

    # ★ [추가 1] 서버용 Global NSM 초기화
    # (앞서 제공해드린 GlobalNetworkStatusMonitor 클래스가 임포트되어 있어야 합니다)
    global_nsm = GlobalNetworkStatusMonitor(num_clients=num_clients, b_max_mhz=50.0, p_max_w=0.1)
        
    # MPI 통신용 신규 태그 정의 (클라이언트 코드와 동일하게 맞춰주세요)
    TAG_SNR_REPORT = 101
    TAG_DIM_CMD = 102

    for round_idx in range(args.n_rounds):
        if logger: logger.info(f"[Server] Round {round_idx+1} Start")
        else: print(f"[Server] Round {round_idx+1} Start")
        
        server.model.train()
        num_batches = args.n_client_data // args.batch_size 
        epoch_loss = 0
        round_data_comm = 0
        round_model_comm = 0
        
        for local_epoch in range(args.n_epochs):
        
            for batch_idx in range(num_batches):
                server.optimizer.zero_grad()

                snr_db_list = []
                
                # 1. 모든 클라이언트로부터 현재 SNR(dB) 수집
                for i in range(1, num_clients + 1):
                    snr_db_val = comm.recv(source=i, tag=TAG_SNR_REPORT)
                    snr_db_list.append(snr_db_val)
                
                # 2. 서버 중앙 집중식 최적화 수행 (논문의 알고리즘 2, 3)
                optimal_dims = global_nsm.optimize_resources(snr_db_list)
                
                # 3. 계산된 최적 차원을 각 클라이언트에게 하달
                for i in range(1, num_clients + 1):
                    optimal_dim_for_client = int(optimal_dims[i-1])
                    comm.send(optimal_dim_for_client, dest=i, tag=TAG_DIM_CMD)
                # =========================================================

                smashed_data_list = []
                labels_list = []
                snr_list = [] 
                client_dims = [] 
                MAX_DIM = 1352

                # 1. Receive Data from Clients (기존 로직 그대로 유지)
                for i in range(1, num_clients + 1):
                    # 클라이언트는 TAG_DIM_CMD를 받은 후 데이터를 잘라서 보냅니다.
                    data_packet = comm.recv(source=i, tag=TAG_FORWARD)
                    
                    s_data = data_packet['data'].to(args.device).requires_grad_(True)
                    label = data_packet['label'].to(args.device)
                    
                    # Padding Logic (SC-USFL)
                    current_dim = s_data.size(1) # 클라이언트가 잘라 보낸 실제 차원
                    client_dims.append(current_dim) 
                    
                    if current_dim < MAX_DIM:
                        padding = torch.zeros(s_data.size(0), MAX_DIM - current_dim).to(args.device)
                        s_data_padded = torch.cat([s_data, padding], dim=1)
                        smashed_data_list.append(s_data_padded)
                    else:
                        smashed_data_list.append(s_data)

                    labels_list.append(label)
                
                # 2. Concatenate
                server_input = torch.cat(smashed_data_list, dim=0)
                server_input.retain_grad()
                server_labels = torch.cat(labels_list, dim=0)

                outputs = server.model(server_input)

                loss = criterion(outputs, server_labels)
                
                # 4. Backward
                loss.backward()
                server.optimizer.step()
                
                # 5. Send Gradients (기존 Slicing Logic 그대로 유지)
                server_grads = server_input.grad.chunk(num_clients, dim=0)
                
                for i in range(1, num_clients + 1):
                    grad_to_send = server_grads[i-1]
                    
                    original_dim = client_dims[i-1]
                    if original_dim < MAX_DIM:
                        grad_to_send = grad_to_send[:, :original_dim]
                    
                    comm.send(grad_to_send.cpu(), dest=i, tag=TAG_BACKWARD)
                    
                    # ★ [수정] 통신량은 텐서의 전체 크기(numel)로 계산해야 정확함
                    # Uplink (클라이언트 -> 서버): s_data (실제로 클라이언트가 보낸 차원 크기)
                    # Downlink (서버 -> 클라이언트): grad_to_send (서버가 잘라서 돌려준 차원 크기)
                    total_data_comm += grad_to_send.numel() * 4
                    round_data_comm += s_data.numel() * 4

                epoch_loss += loss.item()

        # --- [Step 2: Aggregation Phase] --- (이하 완전 동일하여 생략 없이 유지)
        if logger: logger.info("[Server] Aggregating Models...")
        else: print("[Server] Aggregating Models...")
        
        local_weights = []
        for i in range(1, num_clients + 1):
            comm.send("REQ", dest=i, tag=TAG_AGG_REQ)
            w = comm.recv(source=i, tag=TAG_AGG_RES)
            local_weights.append(w)
            for param in w.values():
                total_model_comm += param.numel() * 4
                round_model_comm += param.numel() * 4
                
        avg_weights = copy.deepcopy(local_weights[0])
        for key in avg_weights.keys():
            for i in range(1, num_clients):
                avg_weights[key] += local_weights[i][key]
            avg_weights[key] = torch.div(avg_weights[key], num_clients)
        
        server.global_client_model.load_state_dict(avg_weights)
        
        for i in range(1, num_clients + 1):
            comm.send(avg_weights, dest=i, tag=TAG_AGG_RES)
            for param in avg_weights.values():
                total_model_comm += param.numel() * 4
                round_model_comm += param.numel() * 4
                
        test_acc, test_loss, _ = evaluate_global_snr(args, server.global_client_model, server.model, test_loader, criterion, comm, channel=test_channel)
        avg_loss = epoch_loss / num_batches
        
        comm_mb = (total_data_comm + total_model_comm) / (1024 * 1024)
        round_data_mb = round_data_comm / (1024 * 1024)
        round_model_mb = round_model_comm / (1024 * 1024)
        
        print(f"[Round {round_idx+1}] Acc: {test_acc:.2f}%, Loss: {test_loss:.4f}, Total comm: {comm_mb:.2f} MB")
        logger.info(f"[Round {round_idx+1}] Acc: {test_acc:.2f}%, Loss: {test_loss:.4f}, Total comm: {comm_mb:.2f} MB")
        
        list_accuracies.append(test_acc)
        list_loss.append(test_loss)
        list_comm_cost.append(comm_mb)
        
    return list_accuracies, list_loss, list_comm_cost

def _run_server_fl(comm, server, num_clients, args, logger):
    if args.channel_type == 'awgn':
        test_channel = AWGNChannel(snr_db =args.snr_db).to(args.device)
    elif args.channel_type == 'rayleigh':
        test_channel = RayleighChannel(snr_db =args.snr_db).to(args.device)
    
    criterion = torch.nn.CrossEntropyLoss()
    test_loader = get_dataloader(server.test_data, batch_size=250, is_train=False)
    
    list_accuracies = []
    list_loss = []
    list_comm_cost = [] 
    
    total_comm_bytes = 0
    total_data_comm = 0  # 데이터(Smashed+Grad) 통신량
    total_model_comm = 0 # 모델(Weights) 통신량

    for round_idx in range(args.n_rounds):
        if logger: logger.info(f"[Server] Round {round_idx+1} Start")
        else: print(f"[Server] Round {round_idx+1} Start")
        
        num_batches = args.n_client_data // args.batch_size 
        epoch_loss = 0
        round_data_comm = 0
        round_model_comm = 0    

        # --- [Step 2: Aggregation Phase] ---
        if logger: logger.info("[Server] Aggregating Models...")
        else: print("[Server] Aggregating Models...")
        
        local_weights = []
        
        for i in range(1, num_clients + 1):
            comm.send("REQ", dest=i, tag=TAG_AGG_REQ)
            w = comm.recv(source=i, tag=TAG_AGG_RES)
            local_weights.append(w)
            
            for param in w.values():
                total_model_comm += param.numel() * 4
                round_model_comm += param.numel() * 4
                
        # FedAvg
        avg_weights = copy.deepcopy(local_weights[0])
        for key in avg_weights.keys():
            for i in range(1, num_clients):
                avg_weights[key] += local_weights[i][key]
            avg_weights[key] = torch.div(avg_weights[key], num_clients)
        
        server.global_client_model.load_state_dict(avg_weights)
        
        for i in range(1, num_clients + 1):
            comm.send(avg_weights, dest=i, tag=TAG_AGG_RES)
            
            for param in avg_weights.values():
                total_model_comm += param.numel() * 4
                round_model_comm += param.numel() * 4
                
        # --- Evaluation & Logging ---
        test_acc, test_loss = evaluate_global_fl(
            args,
            server.global_client_model,
            test_loader, 
            criterion,
            comm
        )
        avg_loss = epoch_loss / num_batches
        
        # MB 단위 변환
        total_comm = total_data_comm + total_model_comm
        comm_mb = total_comm / (1024 * 1024)
        data_mb = total_data_comm / (1024 * 1024)
        model_mb = total_model_comm / (1024 * 1024)
        
        round_data_mb = round_data_comm / (1024 * 1024)
        round_model_mb = round_model_comm / (1024 * 1024)
        
        print(f"[Round {round_idx+1}] Acc: {test_acc:.2f}%, Loss: {test_loss:.4f}, Total comm: {comm_mb:.2f} MB (Data: {round_data_mb:.2f} MB, Model: {round_model_mb:.2f} MB)")

        log_msg = f"[Round {round_idx+1}] Acc: {test_acc:.2f}%, Loss: {test_loss:.4f}, Total comm: {comm_mb:.2f} MB (Data: {round_data_mb:.2f} MB, Model: {round_model_mb:.2f} MB)"

        if logger: logger.info(log_msg)
        else: print(log_msg)
    
        list_accuracies.append(test_acc)
        list_loss.append(test_loss)
        list_comm_cost.append(comm_mb)
        
    return list_accuracies, list_loss, list_comm_cost

# ===================================================================
# 3. Client Logic
# ===================================================================
def _run_client(comm, client, args, logger):
    # 학습 데이터 로더 생성 (drop_last=True로 설정됨)
    train_loader = get_dataloader(client.data, batch_size=args.batch_size, is_train=True)
    train_iter = iter(train_loader)
    
    TRAIN_MIN_SNR = -5.0
    TRAIN_MAX_SNR = 15.0
    
    client_seed = args.seed + comm.Get_rank()
    client_rng = np.random.RandomState(seed=client_seed)
    
    
    for round_idx in range(args.n_rounds):
        client.model.train()
        num_batches = args.n_client_data//args.batch_size  # 서버와 동일하게 맞춤
        
        # ★ [추가] Local Epoch Loop (Aggregation 전에 3번 반복)
        for local_epoch in range(args.n_epochs):
            # --- [Step 1: Split Learning Loop] ---
            for batch_idx in range(num_batches):
                # 안전하게 다음 배치 가져오기 (StopIteration 방지)
                images, labels, train_iter = get_next_batch(train_loader, train_iter)           

                images, labels = images.to(args.device), labels.to(args.device)
                
                
                client.optimizer.zero_grad()
                
                current_snr_db = client_rng.uniform(TRAIN_MIN_SNR, TRAIN_MAX_SNR)                
                # current_snr_db = args.snr_db
                
                # 1. Forward & Channel
                z = client.model(images)
                noisy_output = client.channel(z, snr_db=current_snr_db)
                
                # 2. Send to Server
                data_to_send = noisy_output.detach().cpu()
                packet = {'data': data_to_send, 'label': labels.cpu()}
                comm.send(packet, dest=0, tag=TAG_FORWARD)
                
                # 3. Receive Gradient
                grad = comm.recv(source=0, tag=TAG_BACKWARD)
                grad = grad.to(args.device)
                
                # 4. Backward 
                noisy_output.backward(grad*10.0)
                # -------------------------------------------------

                client.optimizer.step()
                
            print(f"[Round {round_idx} Client {comm.rank}, epoch {local_epoch}, SNR {current_snr_db}]")
        # --- [Step 2: Aggregation Phase] ---
        _ = comm.recv(source=0, tag=TAG_AGG_REQ)
        
        # Send Weights
        my_weights = {k: v.cpu() for k, v in client.model.state_dict().items()}
        comm.send(my_weights, dest=0, tag=TAG_AGG_RES)
        
        # Receive Global Weights
        new_weights = comm.recv(source=0, tag=TAG_AGG_RES)
        client.model.load_state_dict(new_weights)
        client.model.to(args.device)

def _run_clientv4(comm, client, args, logger):
    # 학습 데이터 로더 생성
    train_loader = get_dataloader(client.data, batch_size=args.batch_size, is_train=True)
    train_iter = iter(train_loader)
    
    TRAIN_MIN_SNR = -5.0
    TRAIN_MAX_SNR = 15.0

    client_seed = args.seed + comm.Get_rank()
    client_rng = np.random.RandomState(seed=client_seed)
    
    current_snr_db = args.snr_db # <--- 무조건 12dB로 고정

    total_comm_bytes = 0 
    
    pruning_threshold = args.pruning_threshold 

    target_beta = args.beta

    for round_idx in range(args.n_rounds):
        client.model.train()
        num_batches = args.n_client_data // args.batch_size
        # current_beta = target_beta
        
        if args.algorithm == 'SSFL_w_o_beta':
            current_beta = target_beta
        else:
            if round_idx < 50:
                current_beta = 0.0 
            elif round_idx < 150:
                progress = (round_idx - 50) / 100.0
                current_beta = target_beta * progress
            else:
                current_beta = target_beta

        for local_epoch in range(args.n_epochs):
            for batch_idx in range(num_batches):
                images, labels, train_iter = get_next_batch(train_loader, train_iter)
                images, labels = images.to(args.device), labels.to(args.device)
                
                client.optimizer.zero_grad()
                
                # current_snr_db = client_rng.uniform(TRAIN_MIN_SNR, TRAIN_MAX_SNR)
                snr_normalized = (current_snr_db - TRAIN_MIN_SNR) / (TRAIN_MAX_SNR - TRAIN_MIN_SNR)
                snr_input = torch.tensor([[snr_normalized]] * images.size(0)).to(args.device)
                
                z, mu, log_var = client.model(images, snr_val=snr_input)
                
                if args.algorithm == 'SSFL_w_o_vib':
                    mask = torch.ones_like(z).detach() 
                    active_elements = z.numel()
                else:
                    kl_per_channel = compute_channel_kl(mu, log_var)
                    mask = (kl_per_channel > pruning_threshold).float().detach()
                    active_elements = mask.sum().item()

                z_masked = z * mask
                active_ratio = (active_elements / z.numel()) * 100.0
                total_comm_bytes += active_elements * 4

                noisy_z = client.channel(z_masked, snr_db=current_snr_db) * mask 
                
                packet = {
                    'data': noisy_z.detach().cpu(), 
                    'label': labels.cpu(), 
                    'snr': snr_input.cpu()
                }
                comm.send(packet, dest=0, tag=TAG_FORWARD)

                grad = comm.recv(source=0, tag=TAG_BACKWARD)
                grad = grad.to(args.device)
                grad = grad * 100.0

                if args.algorithm != 'SSFL_w_o_vib':
                    avg_kl_loss = torch.mean(kl_per_channel)
                    kl_loss_weighted = current_beta * avg_kl_loss
                    kl_loss_weighted.backward(retain_graph=True)
                
                noisy_z.backward(grad)
                
                torch.nn.utils.clip_grad_norm_(client.model.parameters(), max_norm=5.0)
                client.optimizer.step()
                
                # =========================================================
                # [Logging] - 분포 및 비율 확인용 보강
                # =========================================================
                if batch_idx % 50 == 0:
                    if args.algorithm != 'SSFL_w_o_vib':
                        # KL 분포 상세 계산
                        kl_min = kl_per_channel.min().item()
                        kl_mean = kl_per_channel.mean().item()
                        kl_max = kl_per_channel.max().item()
                        kl_std = kl_per_channel.std().item()
                        
                        # Task Grad(1.0) 대비 KL Term의 실제 크기 (Force Ratio)
                        kl_force = kl_loss_weighted.item()

                        log_msg = (f"[Round {round_idx} Client {comm.rank}, epoch {local_epoch}] "
                                   f"SNR: {current_snr_db:.2f}dB | Active: {active_ratio:.2f}%, beta: {current_beta:.6f}\n"
                                   f"KL Dist: [Min:{kl_min:.4f}, Mean:{kl_mean:.4f}, Max:{kl_max:.4f}, Std:{kl_std:.4f}]\n"
                                   f"Force Ratio: KL Term: {kl_force:.6f}]")
                    else:
                        log_msg = (f"[Round {round_idx} Client {comm.rank}, epoch {local_epoch}] "
                                   f"SNR: {current_snr_db:.2f}dB | Active: {active_ratio:.2f}%, beta: {current_beta:.6f}")
                    
                    if logger: logger.info(log_msg)
                    else: print(log_msg)
                
        _ = comm.recv(source=0, tag=TAG_AGG_REQ)
        my_weights = {k: v.cpu() for k, v in client.model.state_dict().items()}
        comm.send(my_weights, dest=0, tag=TAG_AGG_RES)
        new_weights = comm.recv(source=0, tag=TAG_AGG_RES)
        client.model.load_state_dict(new_weights)
        client.model.to(args.device)

    # --- 종료 로직 ---
    print(f"[Client {comm.rank}] Training loop finished. Waiting for Server...")
    msg = comm.recv(source=0, tag=999) 
    print(f"[Client {comm.rank}] Received {msg}. Shutting down.")
    return


def _run_clientv5(comm, client, args, logger):
    # 학습 데이터 로더 생성
    train_loader = get_dataloader(client.data, batch_size=args.batch_size, is_train=True)
    train_iter = iter(train_loader)
    
    # 학습은 12dB 고정
    current_snr_db = args.snr_db 

    client_seed = args.seed + comm.Get_rank()
    client_rng = np.random.RandomState(seed=client_seed)
    
    total_comm_bytes = 0 
    
    # 고정된 beta 사용
    # current_beta = args.beta
    target_beta = args.beta

    for round_idx in range(args.n_rounds):
        client.model.train()
        num_batches = args.n_client_data // args.batch_size
        # current_beta = target_beta
        
        if 'w_o_beta' in args.algorithm:
            current_beta = target_beta
        else:
            if round_idx < 50:
                current_beta = 0.0 
            elif round_idx < 150:
                progress = (round_idx - 50) / 100.0
                current_beta = target_beta * progress
            else:
                current_beta = target_beta
        
        for local_epoch in range(args.n_epochs):
            for batch_idx in range(num_batches):
                images, labels, train_iter = get_next_batch(train_loader, train_iter)
                images, labels = images.to(args.device), labels.to(args.device)
                
                client.optimizer.zero_grad()
                
                # SNR Input (FiLM이 있다면 사용, 없으면 무시됨)
                snr_normalized = (current_snr_db - (-5.0)) / (15.0 - (-5.0))
                snr_input = torch.tensor([[snr_normalized]] * images.size(0)).to(args.device)
                
                # Forward
                z, mu, log_var = client.model(images, snr_val=snr_input)
                
                # =========================================================
                # ★ 동적 슬라이싱 제거: 마스크 없이 전체 전송
                # =========================================================
                active_elements = z.numel() # 전체 차원수
                total_comm_bytes += active_elements * 4

                # 채널 통과
                noisy_z = client.channel(z, snr_db=current_snr_db)
                
                # 서버로 전송 (SNR 데이터 제외)
                packet = {
                    'data': noisy_z.detach().cpu(), 
                    'label': labels.cpu()
                }
                comm.send(packet, dest=0, tag=TAG_FORWARD)

                # Gradient 수신
                grad = comm.recv(source=0, tag=TAG_BACKWARD)
                grad = grad.to(args.device)
                grad = grad * 100.0

                # VIB Loss 역전파 (w_o_vib가 아닐 때만)
                if 'w_o_vib' not in args.algorithm:
                    kl_per_channel = compute_channel_kl(mu, log_var)
                    avg_kl_loss = torch.mean(kl_per_channel)
                    kl_loss_weighted = current_beta * avg_kl_loss
                    kl_loss_weighted.backward(retain_graph=True)
                
                # 서버 그래디언트 역전파
                noisy_z.backward(grad)
                
                torch.nn.utils.clip_grad_norm_(client.model.parameters(), max_norm=5.0)
                client.optimizer.step()
                
                # 로깅
                if batch_idx % 50 == 0:
                    log_msg = f"[Round {round_idx} Client {comm.rank}, epoch {local_epoch}] SNR: {current_snr_db:.2f}dB | Total Comm: {total_comm_bytes / (1024*1024):.2f} MB"
                    if logger: logger.info(log_msg)
                    else: print(log_msg)
                
        # --- Aggregation Phase ---
        _ = comm.recv(source=0, tag=TAG_AGG_REQ)
        my_weights = {k: v.cpu() for k, v in client.model.state_dict().items()}
        comm.send(my_weights, dest=0, tag=TAG_AGG_RES)
        new_weights = comm.recv(source=0, tag=TAG_AGG_RES)
        client.model.load_state_dict(new_weights)
        client.model.to(args.device)

    # --- 종료 로직 ---
    print(f"[Client {comm.rank}] Training loop finished. Waiting for Server...")
    msg = comm.recv(source=0, tag=999) 
    print(f"[Client {comm.rank}] Received {msg}. Shutting down.")
    return

def _run_clientv6(comm, client, args, logger):
    # 학습 데이터 로더 생성
    train_loader = get_dataloader(client.data, batch_size=args.batch_size, is_train=True)
    train_iter = iter(train_loader)
    
    TRAIN_MIN_SNR = -5.0
    TRAIN_MAX_SNR = 15.0

    client_seed = args.seed + comm.Get_rank()
    client_rng = np.random.RandomState(seed=client_seed)

    total_comm_bytes = 0 
    pruning_threshold = args.pruning_threshold 
    target_beta = args.beta

    for round_idx in range(args.n_rounds):
        client.model.train()
        num_batches = args.n_client_data // args.batch_size
        current_beta = target_beta

        # Beta Scheduler (25 ~ 75 라운드 동안 가속하여 일찍 압축 학습)
        # if 'w_o_beta' in args.algorithm:
        #     current_beta = target_beta
        # else:
        #     if round_idx < 25:
        #         current_beta = 0.0 
        #     elif round_idx < 75: # 100에서 75로 단축 (빠른 수렴 유도)
        #         progress = (round_idx - 25) / (75 - 25) 
        #         current_beta = target_beta * progress
        #     else:
        #         current_beta = target_beta

        for local_epoch in range(args.n_epochs):
            for batch_idx in range(num_batches):
                images, labels, train_iter = get_next_batch(train_loader, train_iter)
                images, labels = images.to(args.device), labels.to(args.device)
                
                client.optimizer.zero_grad()
                current_snr_db = client_rng.uniform(TRAIN_MIN_SNR, TRAIN_MAX_SNR)
                snr_normalized = (current_snr_db - TRAIN_MIN_SNR) / (TRAIN_MAX_SNR - TRAIN_MIN_SNR)
                snr_input = torch.tensor([[snr_normalized]] * images.size(0)).to(args.device)
                
                # 모델 추론
                z, mu, log_var, film_mask = client.model(images, snr_val=snr_input)

                fair_wo_vib = 'w_o_vib_fair' in args.algorithm

                # 1. FiLM / channel mask 먼저 준비
                if getattr(args, 'channel_mask_allpass_enable', 0):
                    chan_mask = torch.ones(z.size(1), device=args.device)
                elif 'w_o_film' not in args.algorithm:
                    dynamic_range = args.film_max_t - args.film_min_t
                    dynamic_threshold = args.film_max_t - (snr_normalized * dynamic_range)
                    chan_mask = (film_mask[0] > dynamic_threshold).float()
                else:
                    chan_mask = torch.ones(z.size(1), device=args.device)

                # 2. semantic mask 준비
                if 'w_o_vib' not in args.algorithm:
                    kl_per_channel = compute_channel_kl(mu, log_var) # [Batch, 4096]
                    
                    # ★ 핵심 수정: 배치 내 모든 이미지의 KL을 평균 내어 [4096] 1차원 벡터로 만듦
                    kl_mean_batch = kl_per_channel.mean(dim=0) 
                    
                    vib_mask = (kl_mean_batch > pruning_threshold).float()
                elif fair_wo_vib:
                    proxy_semantic_scores = _mean_normalize(mu.detach().abs().mean(dim=0))
                    target_active = max(1, int(round(float(getattr(args, 'fair_vib_reference_topk', 256)) / max(pruning_threshold, 1e-6))))
                    vib_mask = build_topk_mask(
                        proxy_semantic_scores,
                        chan_mask,
                        target_active,
                    )
                else:
                    # VIB가 없는 경우, 모든 차원이 다 중요하다고 가정 (1차원 벡터)
                    vib_mask = torch.ones(z.size(1), device=args.device)
                
                # 최종 마스크는 완벽한 [4096] 1차원 벡터가 됨!
                mask = (vib_mask * chan_mask).detach()
                base_selected_count = 0
                refinement_selected_count = 0

                if 'w_o_vib' not in args.algorithm:
                    support_scores = kl_mean_batch.detach() * chan_mask
                elif fair_wo_vib:
                    support_scores = proxy_semantic_scores * chan_mask
                else:
                    support_scores = chan_mask.detach().float()

                if getattr(args, 'semidense_enable', 0):
                    semidense_indices = build_semidense_active_indices(
                        support_scores,
                        mask,
                        getattr(args, 'semidense_group_size', 16),
                        getattr(args, 'semidense_group_topk', 4),
                    )
                    semidense_mask = torch.zeros_like(mask)
                    if semidense_indices.numel() > 0:
                        semidense_mask[semidense_indices] = 1.0
                    mask = semidense_mask

                if getattr(args, 'base_refinement_enable', 0):
                    if getattr(args, 'base_refinement_variable_enable', 0):
                        semantic_scores = kl_mean_batch.detach() if 'w_o_vib' not in args.algorithm else support_scores
                        semantic_candidate_mask = vib_mask if 'w_o_vib' not in args.algorithm else torch.ones_like(mask)
                        channel_scores = film_mask[0].detach() if 'w_o_film' not in args.algorithm else support_scores
                        if getattr(args, 'base_refinement_semantic_aware_enable', 0):
                            channel_candidate_mask = chan_mask if 'w_o_film' not in args.algorithm else torch.ones_like(mask)
                            base_refinement_indices, base_selected_count, refinement_selected_count = build_semantic_aware_fixed_base_variable_refinement_indices(
                                semantic_scores,
                                semantic_candidate_mask,
                                channel_scores,
                                channel_candidate_mask,
                                getattr(args, 'base_support_k', 128),
                                getattr(args, 'refinement_support_k', 128),
                                snr_normalized,
                                getattr(args, 'refinement_semantic_weight', 0.5),
                                getattr(args, 'refinement_channel_weight', 0.5),
                            )
                        else:
                            base_refinement_indices, base_selected_count, refinement_selected_count = build_fixed_base_variable_refinement_indices(
                                semantic_scores,
                                semantic_candidate_mask,
                                channel_scores,
                                getattr(args, 'base_support_k', 128),
                                getattr(args, 'refinement_support_k', 128),
                                snr_normalized,
                            )
                    else:
                        base_refinement_indices = build_base_refinement_indices(
                            support_scores,
                            mask,
                            getattr(args, 'base_support_k', 128),
                            getattr(args, 'refinement_support_k', 128),
                        )
                        base_selected_count = min(getattr(args, 'base_support_k', 128), int(base_refinement_indices.numel()))
                        refinement_selected_count = max(0, int(base_refinement_indices.numel()) - base_selected_count)
                    base_refinement_mask = torch.zeros_like(mask)
                    if base_refinement_indices.numel() > 0:
                        base_refinement_mask[base_refinement_indices] = 1.0
                    mask = base_refinement_mask

                if getattr(args, 'support_floor_enable', 0) and current_snr_db <= float(getattr(args, 'support_floor_snr_db', 0.0)):
                    mask = apply_support_floor_mask(
                        support_scores,
                        mask,
                        getattr(args, 'support_floor_min_active', 256),
                    )

                # [아래부터는 기존 코드와 동일]
                num_active_per_sample = torch.sum(mask > 0).item() 
                total_dim = mask.numel()                          
                active_ratio = (num_active_per_sample / total_dim) * 100.0

                # 2. 배치 전체 활성화 요소 (통신량 계산용 - 데이터 크기)
                active_elements = num_active_per_sample * images.size(0)

                # 3. 통신량 계산 (Bytes)
                active_indices = torch.nonzero(mask > 0).squeeze(-1)
                tx_indices = active_indices
                
                # 4. z_masked 정의 및 채널 통과
                repeated_target_indices = active_indices.new_empty(0)
                repeated_aux_indices = active_indices.new_empty(0)
                repetition_source_pos = active_indices.new_empty(0)
                if active_indices.numel() > 0:
                    active_z = torch.index_select(z, 1, active_indices)

                    if args.semantic_power_enable:
                        if 'w_o_vib' not in args.algorithm:
                            active_kl = torch.index_select(kl_mean_batch.detach(), 0, active_indices)
                        else:
                            active_kl = torch.ones_like(active_indices, dtype=z.dtype, device=args.device)
                        power_scales = compute_semantic_power_scales(active_kl, args.semantic_power_alpha)
                        active_z = active_z * power_scales.unsqueeze(0)

                    if getattr(args, 'importance_repetition_enable', 0):
                        repeated_target_indices, repeated_aux_indices, repetition_source_pos = build_importance_repetition_plan(
                            support_scores,
                            active_indices,
                            mask,
                            getattr(args, 'importance_repetition_topk', 32),
                        )
                        if repeated_aux_indices.numel() > 0:
                            repeated_z = torch.index_select(active_z, 1, repetition_source_pos)
                            active_z = torch.cat([active_z, repeated_z], dim=1)
                            tx_indices = torch.cat([active_indices, repeated_aux_indices], dim=0)

                tx_count_per_sample = int(tx_indices.numel())
                tx_active_ratio = (tx_count_per_sample / total_dim) * 100.0
                active_elements = tx_count_per_sample * images.size(0)
                data_bytes = active_elements * 4
                index_bytes = tx_indices.numel() * 2
                total_comm_bytes += (data_bytes + index_bytes)
                tx_mask = torch.zeros_like(mask)
                if tx_indices.numel() > 0:
                    tx_mask[tx_indices] = 1.0

                if args.semantic_spreading_enable and active_indices.numel() > 0:
                    spread_active_z = apply_semantic_spreading(active_z)
                    expanded_indices = tx_indices.unsqueeze(0).expand(images.size(0), -1)
                    z_masked = torch.zeros_like(z)
                    z_masked.scatter_(1, expanded_indices, spread_active_z)
                elif tx_indices.numel() > 0 and (args.semantic_power_enable or getattr(args, 'importance_repetition_enable', 0)):
                    expanded_indices = tx_indices.unsqueeze(0).expand(images.size(0), -1)
                    z_masked = torch.zeros_like(z)
                    z_masked.scatter_(1, expanded_indices, active_z)
                else:
                    z_masked = z * mask
                noisy_z = client.channel(z_masked, snr_db=current_snr_db) * tx_mask 

                # 5. 서버로 패킷 전송
                packet = {
                    'data': noisy_z.detach().cpu(), 
                    'label': labels.cpu(), 
                    'snr': snr_input.cpu(),
                    'indices': tx_indices.cpu(),
                    'repeat_target_indices': repeated_target_indices.cpu(),
                    'repeat_aux_indices': repeated_aux_indices.cpu(),
                }
                if _mpi_trace_enabled(args, batch_idx):
                    _mpi_trace(logger, f"client rank={comm.rank} round={round_idx+1} batch={batch_idx} sending_forward k={tx_indices.numel()} data_shape={tuple(packet['data'].shape)}")
                comm.send(packet, dest=0, tag=TAG_FORWARD)

                # 6. 서버로부터 슬라이싱된 Gradient 수신
                if _mpi_trace_enabled(args, batch_idx):
                    _mpi_trace(logger, f"client rank={comm.rank} round={round_idx+1} batch={batch_idx} waiting_backward")
                grad_compressed = comm.recv(source=0, tag=TAG_BACKWARD)
                if _mpi_trace_enabled(args, batch_idx):
                    _mpi_trace(logger, f"client rank={comm.rank} round={round_idx+1} batch={batch_idx} received_backward grad_shape={tuple(grad_compressed.shape)}")
                
                # 예외 처리: 데이터가 아예 전송되지 않은 경우 역전파 패스
                if num_active_per_sample == 0:
                    continue

                grad_compressed = grad_compressed.to(args.device)

                # 슬라이싱된 기울기를 원래 4096차원으로 복원 (Zero-filling)
                grad_full = torch.zeros(noisy_z.shape, device=args.device)
                expanded_indices = active_indices.unsqueeze(0).expand(images.size(0), -1)
                grad_full.scatter_(1, expanded_indices, grad_compressed)

                if 'w_o_vib' not in args.algorithm:
                    avg_kl_loss = torch.mean(kl_per_channel)
                    beta_for_step = current_beta
                    if args.snr_adaptive_beta_enable:
                        beta_for_step = current_beta * (1.0 - snr_normalized)
                    kl_loss_weighted = beta_for_step * avg_kl_loss 
                    kl_loss_weighted.backward(retain_graph=True)
                
                # ★ Sparsity-Aware Gradient Compensation (동적 스케일링)
                keep_prob = num_active_per_sample / total_dim 
                keep_prob = max(keep_prob, 0.01) # 하한선 보장
                dynamic_scale = 1.0 / keep_prob

                # 역전파 실행
                noisy_z.backward(grad_full * dynamic_scale)
                
                torch.nn.utils.clip_grad_norm_(client.model.parameters(), max_norm=5.0)
                client.optimizer.step()
                
                # [로깅부]
                if batch_idx % 50 == 0:
                    if 'w_o_vib' not in args.algorithm:
                        kl_mean = kl_per_channel.mean().item()
                        logged_beta = current_beta
                        if args.snr_adaptive_beta_enable:
                            logged_beta = current_beta * (1.0 - snr_normalized)
                        log_msg = (f"[Round {round_idx} Client {comm.rank}] SNR: {current_snr_db:.2f}dB | "
                                f"Active: {tx_count_per_sample}/{total_dim} ({tx_active_ratio:.2f}%) | "
                                f"KL_Mean: {kl_mean:.4f} | Beta: {logged_beta:.6f}")
                    else:
                        log_msg = (f"[Round {round_idx} Client {comm.rank}] SNR: {current_snr_db:.2f}dB | "
                                f"Active: {tx_count_per_sample}/{total_dim} ({tx_active_ratio:.2f}%)")

                    if getattr(args, 'base_refinement_enable', 0):
                        log_msg += f" | Base: {base_selected_count} | Refinement: {refinement_selected_count}"
                    
                    if logger: logger.info(log_msg)
                    else: print(log_msg)
                
        # 가중치 Aggregation (기존 로직 유지)
        if _mpi_trace_enabled(args):
            _mpi_trace(logger, f"client rank={comm.rank} round={round_idx+1} waiting_agg_req")
        _ = comm.recv(source=0, tag=TAG_AGG_REQ)
        my_weights = {k: v.cpu() for k, v in client.model.state_dict().items()}
        if _mpi_trace_enabled(args):
            _mpi_trace(logger, f"client rank={comm.rank} round={round_idx+1} sending_agg_res")
        comm.send(my_weights, dest=0, tag=TAG_AGG_RES)
        if _mpi_trace_enabled(args):
            _mpi_trace(logger, f"client rank={comm.rank} round={round_idx+1} waiting_new_weights")
        new_weights = comm.recv(source=0, tag=TAG_AGG_RES)
        client.model.load_state_dict(new_weights)
        client.model.to(args.device)

    # --- 종료 로직 ---
    print(f"[Client {comm.rank}] Training loop finished. Waiting for Server...")
    msg = comm.recv(source=0, tag=999) 
    print(f"[Client {comm.rank}] Received {msg}. Shutting down.")
    return

# def _run_clientv6(comm, client, args, logger):
#     # 학습 데이터 로더 생성
#     train_loader = get_dataloader(client.data, batch_size=args.batch_size, is_train=True)
#     train_iter = iter(train_loader)
    
#     TRAIN_MIN_SNR = -5.0
#     TRAIN_MAX_SNR = 15.0

#     client_seed = args.seed + comm.Get_rank()
#     client_rng = np.random.RandomState(seed=client_seed)
    
#     # current_snr_db = args.snr_db 

#     total_comm_bytes = 0 
#     pruning_threshold = args.pruning_threshold 
#     target_beta = args.beta

#     for round_idx in range(args.n_rounds):
#         client.model.train()
#         num_batches = args.n_client_data // args.batch_size
        
#         # Beta Scheduler
#         if 'w_o_beta' in args.algorithm:
#             current_beta = target_beta
#         else:
#             if round_idx < 25:
#                 current_beta = 0.0 
#             elif round_idx < 100:
#                 # 25라운드부터 100라운드까지 '75단계' 동안 선형적으로 증가
#                 progress = (round_idx - 25) / (100 - 25) 
#                 current_beta = target_beta * progress
#             else:
#                 current_beta = target_beta

#         for local_epoch in range(args.n_epochs):
#             for batch_idx in range(num_batches):
#                 images, labels, train_iter = get_next_batch(train_loader, train_iter)
#                 images, labels = images.to(args.device), labels.to(args.device)
                
#                 client.optimizer.zero_grad()
#                 current_snr_db = client_rng.uniform(TRAIN_MIN_SNR, TRAIN_MAX_SNR)
#                 snr_normalized = (current_snr_db - TRAIN_MIN_SNR) / (TRAIN_MAX_SNR - TRAIN_MIN_SNR)
#                 snr_input = torch.tensor([[snr_normalized]] * images.size(0)).to(args.device)
                
#                 # 모델 추론 (4개 반환)
#                 z, mu, log_var, film_mask = client.model(images, snr_val=snr_input)

#                 # 1. VIB 마스크 준비 (만약 VIB가 활성화된 경우만)
#                 if 'w_o_vib' not in args.algorithm:
#                     kl_per_channel = compute_channel_kl(mu, log_var)
#                     vib_mask = (kl_per_channel > pruning_threshold).float()
#                 else:
#                     # VIB가 없는 경우, 모든 차원이 다 중요하다고 가정(All 1)
#                     vib_mask = torch.ones(z.size(1), device=args.device)

#                 # 2. FiLM 마스크 준비 (만약 FiLM이 활성화된 경우만)
#                 if 'w_o_film' not in args.algorithm:
#                     dynamic_threshold = 0.5 - (snr_normalized * 0.3)
#                     chan_mask = (film_mask[0] > dynamic_threshold).float()
#                 else:
#                     # FiLM이 없는 경우, 모든 채널이 다 열려있다고 가정(All 1)
#                     chan_mask = torch.ones(z.size(1)).to(args.device)
                
#                 mask = (vib_mask * chan_mask).detach()

#                 # [수정된 계산부]
#                 # 1. 한 샘플(4096차원) 기준 실제로 살아남은 개수 계산
#                 num_active_per_sample = torch.sum(mask[0] > 0).item() # 4096개 중 몇 개인지 (예: 1024)
#                 total_dim = mask[0].numel()                          # 전체 차원 (4096)
#                 active_ratio = (num_active_per_sample / total_dim) * 100.0

#                 # 2. 배치 전체 활성화 요소 (통신량 계산용 - 데이터 크기)
#                 active_elements = num_active_per_sample * images.size(0)

#                 # 3. 통신량 계산 (Bytes)
#                 data_bytes = active_elements * 4
#                 active_indices = torch.nonzero(mask[0] > 0).squeeze(-1)
#                 index_bytes = active_indices.numel() * 2 
#                 total_comm_bytes += (data_bytes + index_bytes)
                
#                 # ★ [중요] z_masked 정의 ★
#                 z_masked = z * mask
#                 # 채널 통과
#                 noisy_z = client.channel(z_masked, snr_db=current_snr_db) * mask 

#                 # 4. 서버로 패킷 전송
#                 packet = {
#                     'data': noisy_z.detach().cpu(), 
#                     'label': labels.cpu(), 
#                     'snr': snr_input.cpu(),
#                     'indices': active_indices.cpu() 
#                 }
#                 comm.send(packet, dest=0, tag=TAG_FORWARD)

#                 # 5. 서버로부터 Gradient 수신 및 역전파
#                 # 5. 서버로부터 슬라이싱된 Gradient 수신
#                 grad_compressed = comm.recv(source=0, tag=TAG_BACKWARD)
#                 grad_compressed = grad_compressed.to(args.device)

#                 # ★ 핵심: 슬라이싱된 기울기를 원래 4096차원으로 복원 (Zero-filling)
#                 # noisy_z와 동일한 크기의 영행렬 생성 [Batch, 4096]
#                 grad_full = torch.zeros(noisy_z.shape, device=args.device)

#                 # active_indices를 배치 크기에 맞게 확장 [Batch, K]
#                 expanded_indices = active_indices.unsqueeze(0).expand(images.size(0), -1)

#                 # 받은 기울기를 원래 위치에 쏙쏙 꽂아넣음
#                 grad_full.scatter_(1, expanded_indices, grad_compressed)

#                 # SNR이 좋을수록(1에 가까울수록) Beta가 0에 가까워지게 설계
#                 snr_factor = (1.0 - snr_normalized) 
#                 adaptive_beta = current_beta * snr_factor 

#                 # 역전파 시 적용
#                 if 'w_o_vib' not in args.algorithm:
#                     avg_kl_loss = torch.mean(kl_per_channel)
#                     # 기존 current_beta 대신 adaptive_beta 사용
#                     kl_loss_weighted = adaptive_beta * avg_kl_loss 
#                     kl_loss_weighted.backward(retain_graph=True)
                
#                 # [수정 후 코드: 1/keep_prob 적용]
#                 # 1. 보존 확률(keep_prob) 계산
#                 # num_active_per_sample(살아남은 개수)을 total_dim(4096)으로 나눈 값
#                 keep_prob = num_active_per_sample / total_dim 
#                 keep_prob = max(keep_prob, 0.01)

#                 dynamic_scale = 1.0 / keep_prob

#                 noisy_z.backward(grad_full * dynamic_scale)
                
#                 torch.nn.utils.clip_grad_norm_(client.model.parameters(), max_norm=5.0)
#                 client.optimizer.step()
                
#                 # [수정된 로깅부]
#                 if batch_idx % 50 == 0:
#                     if 'w_o_vib' not in args.algorithm:
#                         kl_mean = kl_per_channel.mean().item()
#                         # ★ 로그 메시지에 실제 개수(num_active_per_sample) 추가 ★
#                         log_msg = (f"[Round {round_idx} Client {comm.rank}] SNR: {current_snr_db}dB | "
#                                 f"Active: {num_active_per_sample}/{total_dim} ({active_ratio:.2f}%) | "
#                                 f"KL_Mean: {kl_mean:.4f} | Beta: {adaptive_beta:.6f}")
#                     else:
#                         log_msg = (f"[Round {round_idx} Client {comm.rank}] SNR: {current_snr_db}dB | "
#                                 f"Active: {num_active_per_sample}/{total_dim} ({active_ratio:.2f}%)")
                    
#                     if logger: logger.info(log_msg)
#                     else: print(log_msg)
                
#         # 가중치 Aggregation (기존 로직 유지)
#         _ = comm.recv(source=0, tag=TAG_AGG_REQ)
#         my_weights = {k: v.cpu() for k, v in client.model.state_dict().items()}
#         comm.send(my_weights, dest=0, tag=TAG_AGG_RES)
#         new_weights = comm.recv(source=0, tag=TAG_AGG_RES)
#         client.model.load_state_dict(new_weights)
#         client.model.to(args.device)

#     # --- 종료 로직 ---
#     print(f"[Client {comm.rank}] Training loop finished. Waiting for Server...")
#     msg = comm.recv(source=0, tag=999) 
#     print(f"[Client {comm.rank}] Received {msg}. Shutting down.")
#     import os
#     os._exit(0)

# ------------------------------------------------------------------------------
# Client Logic (Local Training)
# ------------------------------------------------------------------------------
def _run_client_fl(comm, client, args, logger):
# 학습 데이터 로더 생성
    train_loader = get_dataloader(client.data, batch_size=args.batch_size, is_train=True)
    train_iter = iter(train_loader)
    criterion = nn.CrossEntropyLoss()
    # ★ 가변 압축을 위한 임계값
    pruning_threshold = 1e-2 
    
    # ★ 학습용 SNR 범위 설정 (-5dB ~ 15dB 추천)
    TRAIN_MIN_SNR = -5.0
    TRAIN_MAX_SNR = 15.0

    client_seed = args.seed + comm.Get_rank()
    client_rng = np.random.RandomState(seed=client_seed)
    
    total_comm_bytes = 0 

    dim_scale_factor = args.compressed_dim / 32
    target_beta = args.beta / dim_scale_factor

    for round_idx in range(args.n_rounds):
        client.model.train()
        num_batches = args.n_client_data // args.batch_size

        # ★ [추가] Local Epoch Loop (Aggregation 전에 3번 반복)
        for local_epoch in range(args.n_epochs):
        
            for batch_idx in range(num_batches):
                images, labels, train_iter = get_next_batch(train_loader, train_iter)
                images, labels = images.to(args.device), labels.to(args.device)
                
                client.optimizer.zero_grad()

                z = client.model(images)
                loss = criterion(z, labels)
                loss.backward()
                
                client.optimizer.step()

        # --- Aggregation Phase (변경 없음) ---
        _ = comm.recv(source=0, tag=TAG_AGG_REQ)
        my_weights = {k: v.cpu() for k, v in client.model.state_dict().items()}
        comm.send(my_weights, dest=0, tag=TAG_AGG_RES)
        new_weights = comm.recv(source=0, tag=TAG_AGG_RES)
        client.model.load_state_dict(new_weights)
        client.model.to(args.device)


    print("[Client] Training loop finished. Waiting for Server...")

    # [수정] Barrier 대신, 서버가 보낼 EXIT 신호를 기다림
    TAG_EXIT = 999
    
    msg = comm.recv(source=0, tag=TAG_EXIT)
    
    print(f"[Client] Received {msg}. Shutting down.")
    return

# def pretrain_scm(args, logger=None):
#     device = args.device
#     print(f"=== [Phase 1] Start SCM Pre-training with **Random Slicing** on {device} ===")
    
#     # 1. 데이터셋 로드
#     transform = transforms.Compose([
#         transforms.ToTensor(),
#         transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
#     ])
    
#     trainset = torchvision.datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
#     trainloader = DataLoader(trainset, batch_size=128, shuffle=True, num_workers=2)
    
#     testset = torchvision.datasets.CIFAR10(root='./data', train=False, download=True, transform=transform)
#     testloader = DataLoader(testset, batch_size=128, shuffle=False, num_workers=2)

#     # 2. 모델 준비
#     MAX_DIM = 1352
#     CANDIDATE_DIMS = [328, 492, 696, 1352]

#     client_model = ClientResNet18v2(args).to(device)
#     server_model = ServerResNet18(args).to(device) 
    
#     semantic_decoder = server_model.semantic_decoder
#     server_body = server_model.layers 
#     server_tail = server_model.fc

#     # =========================================================
#     # ★ [수정 1] Optimizer: 모델 전체를 End-to-End로 학습 (매우 중요)
#     # =========================================================
#     optimizer = optim.Adam([
#             {'params': client_model.parameters()},  # Head + Encoder
#             {'params': server_model.parameters()}   # Decoder + Body + Tail
#         ], lr=1e-3)

#     criterion = SCMLoss(lambda_task=4.0, lambda_recon=4.0, lambda_semantic=2.0)

#     epochs = 200
#     patience = 20        
#     counter = 0          
#     best_val_loss = float('inf') 
    
#     os.makedirs("./checkpoints", exist_ok=True)
#     # 추후 연합학습에서 불러올 가중치들
#     save_path_client = f"./checkpoints/client_pretrained_{args.channel_type}_{args.dataset}.pth"
#     save_path_server = f"./checkpoints/server_pretrained_{args.channel_type}_{args.dataset}.pth"
#     TRAIN_MIN_SNR = -5.0
#     TRAIN_MAX_SNR = 15.0

#     client_seed = args.seed + 9999 # Pre-training 전용 시드 (연합학습 시드와 겹치지 않도록)
#     client_rng = np.random.RandomState(seed=client_seed)

#     for epoch in range(epochs):
#         # --- [Training Phase] ---
#         client_model.train()
#         server_model.train() # 전체 모델 Train 모드
#         running_loss = 0.0
        
#         for i, (inputs, labels) in enumerate(trainloader):
#             inputs, labels = inputs.to(device), labels.to(device)
#             optimizer.zero_grad()
            
#             # [Step 1] SNR Sampling & Normalization
#             current_snr_db = client_rng.uniform(TRAIN_MIN_SNR, TRAIN_MAX_SNR)                

#             # 1. Feature Extraction (Head)
#             # target_feat이 의미 있는 값을 갖도록 학습됩니다.
#             orig_feat = client_model.features(inputs)
            
#             # 2. Encoding
#             z_full = client_model.semantic_encoder(orig_feat)
            
#             # 3. Random Slicing
#             current_dim = random.choice(CANDIDATE_DIMS)
#             z_sliced = z_full[:, :current_dim]
            
#             # =========================================================
#             # ★ [수정 2] 정확한 Power Normalization 및 19dB 고정 노이즈
#             # =========================================================
#             sig_power = torch.mean(z_sliced ** 2, dim=1, keepdim=True)
#             z_sliced = z_sliced / torch.sqrt(sig_power + 1e-9)
            
#             # 논문 명세: Pre-training은 19dB 환경에서 수행
#             noise_std = 10 ** (-current_snr_db / 20.0) 
#             noise = torch.randn_like(z_sliced) * noise_std
#             z_noisy = z_sliced + noise
            
#             # 4. Zero Padding
#             if current_dim < MAX_DIM:
#                 padding = torch.zeros(inputs.size(0), MAX_DIM - current_dim).to(device)
#                 z_padded = torch.cat([z_noisy, padding], dim=1)
#             else:
#                 z_padded = z_noisy
                
#             # 5. Decoder & Body & Tail
#             recon_feat = semantic_decoder(z_padded)
#             logits = server_body(recon_feat)
#             logits = torch.flatten(logits, 1) 
#             logits = server_tail(logits)
            
#             # Loss 계산 및 역전파
#             # orig_feat은 계산 그래프에 연결되어 있으므로 분리(detach)할지 말지 결정해야 함
#             # 일반적으로 원본 피처 추출기(Head)도 Task Loss의 영향을 받아야 하므로 연결 유지
#             loss, _, _ = criterion(logits, labels, orig_feat, recon_feat)
#             loss.backward()
#             optimizer.step()
            
#             running_loss += loss.item()
            
#         avg_train_loss = running_loss / len(trainloader)

#         # --- [Validation Phase] ---
#         client_model.eval()
#         server_model.eval()
#         val_running_loss = 0.0
        
#         with torch.no_grad():
#             for inputs, labels in testloader:
#                 inputs, labels = inputs.to(device), labels.to(device)
                
#                 orig_feat = client_model.features(inputs)
#                 z_full = client_model.semantic_encoder(orig_feat)
                
#                 current_dim = random.choice(CANDIDATE_DIMS)
#                 z_sliced = z_full[:, :current_dim]
                
#                 # Validation 시에도 동일한 19dB 노이즈 적용
#                 sig_power = torch.mean(z_sliced ** 2, dim=1, keepdim=True)
#                 z_sliced = z_sliced / torch.sqrt(sig_power + 1e-9)
                
#                 noise = torch.randn_like(z_sliced) * noise_std
#                 z_noisy = z_sliced + noise
                
#                 if current_dim < MAX_DIM:
#                     padding = torch.zeros(inputs.size(0), MAX_DIM - current_dim).to(device)
#                     z_padded = torch.cat([z_noisy, padding], dim=1)
#                 else:
#                     z_padded = z_noisy
                    
#                 recon_feat = semantic_decoder(z_padded)
#                 logits = server_body(recon_feat)
#                 logits = torch.flatten(logits, 1)
#                 logits = server_tail(logits)
                
#                 loss, _, _ = criterion(logits, labels, orig_feat, recon_feat)
#                 val_running_loss += loss.item()

#         avg_val_loss = val_running_loss / len(testloader)
        
#         print(f"[Epoch {epoch+1}/{epochs}] Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f} (Best: {best_val_loss:.4f})")

#         # --- [Early Stopping Logic] ---
#         if avg_val_loss < best_val_loss:
#             best_val_loss = avg_val_loss
#             counter = 0 
            
#             # ★ [수정 3] 인코더/디코더만 저장하지 말고 전체 가중치 저장
#             # 연합학습 라운드가 시작될 때 이 가중치를 클라이언트와 서버에 뿌려줘야 합니다.
#             torch.save(client_model.semantic_encoder.state_dict(), save_path_client)
#             torch.save(semantic_decoder.state_dict(), save_path_server)
#             print(f"  -> Model Saved! (New Best Score)")
            
#         else:
#             counter += 1
#             print(f"  -> EarlyStopping Counter: {counter}/{patience}")
            
#             if counter >= patience:
#                 print("Early Stopping Triggered! Training finished.")
#                 break

#     print("=== [Phase 1] SCM Pre-training Finished ===")

def pretrain_scm(args, logger=None):
    device = args.device
    dataset_name = args.dataset.lower()
    print(f"=== [Phase 1] Start SCM Pre-training with **Random Slicing** on {device} ===")
    print(f"=== Dataset: {dataset_name.upper()} ===")
    
    # =========================================================
    # ★ [수정] 데이터셋 동적 로드 (CIFAR-10, CIFAR-100, Fashion-MNIST)
    # =========================================================
    if dataset_name == 'cifar10':
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
        ])
        trainset = torchvision.datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
        testset = torchvision.datasets.CIFAR10(root='./data', train=False, download=True, transform=transform)
        num_classes = 10

    elif dataset_name == 'cifar100':
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5071, 0.4867, 0.4408), (0.2675, 0.2565, 0.2761)),
        ])
        trainset = torchvision.datasets.CIFAR100(root='./data', train=True, download=True, transform=transform)
        testset = torchvision.datasets.CIFAR100(root='./data', train=False, download=True, transform=transform)
        num_classes = 100

    elif dataset_name in ['fashion-mnist', 'fmnist']:
        transform = transforms.Compose([
            # CIFAR 해상도(32x32)와 맞추기 위해 Resize 적용 (ResNet 차원 붕괴 방지)
            transforms.Resize((32, 32)), 
            transforms.ToTensor(),
            transforms.Normalize((0.2860,), (0.3530,)), # 1채널 정규화
        ])
        trainset = torchvision.datasets.FashionMNIST(root='./data', train=True, download=True, transform=transform)
        testset = torchvision.datasets.FashionMNIST(root='./data', train=False, download=True, transform=transform)
        num_classes = 10
        
    else:
        raise ValueError(f"지원하지 않는 데이터셋입니다: {dataset_name}")

    trainloader = DataLoader(trainset, batch_size=128, shuffle=True, num_workers=2)
    testloader = DataLoader(testset, batch_size=128, shuffle=False, num_workers=2)

    # =========================================================
    # 2. 모델 준비 (num_classes 동적 할당)
    # =========================================================
    MAX_DIM = 1352
    CANDIDATE_DIMS = [328, 492, 696, 1352]

    # 주의: 모델 초기화 시 num_classes를 전달할 수 있도록 구현되어 있어야 합니다.
    client_model = ClientResNet18v2(args).to(device)
    server_model = ServerResNet18(args).to(device) 
    
    semantic_decoder = server_model.semantic_decoder
    server_body = server_model.layers 
    server_tail = server_model.fc

    # Optimizer: 모델 전체를 End-to-End로 학습 (매우 중요)
    optimizer = optim.Adam([
            {'params': client_model.parameters()},  # Head + Encoder
            {'params': server_model.parameters()}   # Decoder + Body + Tail
        ], lr=1e-3)

    criterion = SCMLoss(lambda_task=4.0, lambda_recon=4.0, lambda_semantic=2.0)

    epochs = 200
    patience = 20        
    counter = 0          
    best_val_loss = float('inf') 
    
    os.makedirs("./checkpoints", exist_ok=True)
    # 데이터셋 이름이 포함된 저장 경로
    save_path_client = f"./checkpoints/client_pretrained_{args.channel_type}_{dataset_name}.pth"
    save_path_server = f"./checkpoints/server_pretrained_{args.channel_type}_{dataset_name}.pth"
    
    TRAIN_MIN_SNR = -5.0
    TRAIN_MAX_SNR = 15.0

    client_seed = args.seed + 9999 # Pre-training 전용 시드
    client_rng = np.random.RandomState(seed=client_seed)

    for epoch in range(epochs):
        # --- [Training Phase] ---
        client_model.train()
        server_model.train() 
        running_loss = 0.0
        
        for i, (inputs, labels) in enumerate(trainloader):
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            
            # [Step 1] SNR Sampling
            current_snr_db = client_rng.uniform(TRAIN_MIN_SNR, TRAIN_MAX_SNR)                

            # 1. Feature Extraction (Head)
            orig_feat = client_model.features(inputs)
            
            # 2. Encoding
            z_full = client_model.semantic_encoder(orig_feat)
            
            # 3. Random Slicing
            current_dim = random.choice(CANDIDATE_DIMS)
            z_sliced = z_full[:, :current_dim]
            
            # 정확한 Power Normalization 및 19dB 고정 노이즈
            sig_power = torch.mean(z_sliced ** 2, dim=1, keepdim=True)
            z_sliced = z_sliced / torch.sqrt(sig_power + 1e-9)
            
            noise_std = 10 ** (-current_snr_db / 20.0) 
            noise = torch.randn_like(z_sliced) * noise_std
            z_noisy = z_sliced + noise
            
            # 4. Zero Padding
            if current_dim < MAX_DIM:
                padding = torch.zeros(inputs.size(0), MAX_DIM - current_dim).to(device)
                z_padded = torch.cat([z_noisy, padding], dim=1)
            else:
                z_padded = z_noisy
                
            # 5. Decoder & Body & Tail
            recon_feat = semantic_decoder(z_padded)
            logits = server_body(recon_feat)
            logits = torch.flatten(logits, 1) 
            logits = server_tail(logits)
            
            loss, _, _ = criterion(logits, labels, orig_feat, recon_feat)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            
        avg_train_loss = running_loss / len(trainloader)

        # --- [Validation Phase] ---
        client_model.eval()
        server_model.eval()
        val_running_loss = 0.0
        
        with torch.no_grad():
            for inputs, labels in testloader:
                inputs, labels = inputs.to(device), labels.to(device)
                
                orig_feat = client_model.features(inputs)
                z_full = client_model.semantic_encoder(orig_feat)
                
                current_dim = random.choice(CANDIDATE_DIMS)
                z_sliced = z_full[:, :current_dim]
                
                sig_power = torch.mean(z_sliced ** 2, dim=1, keepdim=True)
                z_sliced = z_sliced / torch.sqrt(sig_power + 1e-9)
                
                noise = torch.randn_like(z_sliced) * noise_std
                z_noisy = z_sliced + noise
                
                if current_dim < MAX_DIM:
                    padding = torch.zeros(inputs.size(0), MAX_DIM - current_dim).to(device)
                    z_padded = torch.cat([z_noisy, padding], dim=1)
                else:
                    z_padded = z_noisy
                    
                recon_feat = semantic_decoder(z_padded)
                logits = server_body(recon_feat)
                logits = torch.flatten(logits, 1)
                logits = server_tail(logits)
                
                loss, _, _ = criterion(logits, labels, orig_feat, recon_feat)
                val_running_loss += loss.item()

        avg_val_loss = val_running_loss / len(testloader)
        
        print(f"[Epoch {epoch+1}/{epochs}] Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f} (Best: {best_val_loss:.4f})")

        # --- [Early Stopping Logic] ---
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            counter = 0 
            
            # 인코더/디코더 저장
            torch.save(client_model.semantic_encoder.state_dict(), save_path_client)
            torch.save(semantic_decoder.state_dict(), save_path_server)
            print(f"  -> Model Saved! (New Best Score)")
            
        else:
            counter += 1
            print(f"  -> EarlyStopping Counter: {counter}/{patience}")
            
            if counter >= patience:
                print("Early Stopping Triggered! Training finished.")
                break

    print("=== [Phase 1] SCM Pre-training Finished ===")

def _run_client_sc_usfl(comm, client, args, logger):
    # 1. 데이터 로더 설정
    train_loader = get_dataloader(client.data, batch_size=args.batch_size, is_train=True)
    train_iter = iter(train_loader)
        
    # 2. 학습용 SNR 환경 설정 (-5dB ~ 15dB)
    TRAIN_MIN_SNR = -5.0
    TRAIN_MAX_SNR = 15.0
    
    client_seed = args.seed + comm.Get_rank()
    client_rng = np.random.RandomState(seed=client_seed)
    
    total_comm_bytes = 0 
    log_interval = 50

    # ★ [추가] MPI 통신용 태그 정의 (서버와 동일하게 맞춰야 함)
    # 기존 태그들이 전역변수라면 그대로 쓰시고, 신규 태그 2개는 꼭 정의해야 합니다.
    TAG_FORWARD = 1
    TAG_BACKWARD = 2
    TAG_AGG_REQ = 3
    TAG_AGG_RES = 4
    TAG_SNR_REPORT = 101 # 신규
    TAG_DIM_CMD = 102    # 신규

    for round_idx in range(args.n_rounds):
        client.model.train()
        num_batches = args.n_client_data // args.batch_size
        
        # ★ [Outer Loop 2] Local Epochs (Aggregation 전 반복 학습) ★
        for local_epoch in range(args.n_epochs):
            
            # [Inner Loop] Batches
            for batch_idx in range(num_batches):
                # 안전하게 다음 배치 데이터 가져오기
                images, labels, train_iter = get_next_batch(train_loader, train_iter)
                images, labels = images.to(args.device), labels.to(args.device)
                
                client.optimizer.zero_grad()
                
                # =========================================================
                # [Step 1] SNR Sampling & Handshake (환경 감지 및 차원 할당)
                # =========================================================
                # 배치마다 랜덤한 SNR 생성
                current_snr_db = client_rng.uniform(TRAIN_MIN_SNR, TRAIN_MAX_SNR) 
                # current_snr_db = args.snr_db               
                # 모델 입력용 정규화 (0.0 ~ 1.0 사이 값으로 변환)
                snr_normalized = (current_snr_db - TRAIN_MIN_SNR) / (TRAIN_MAX_SNR - TRAIN_MIN_SNR)
                
                # 텐서 변환 (Batch 크기만큼 복사)
                # shape: [Batch_size, 1]
                snr_input = torch.tensor([[snr_normalized]] * images.size(0)).to(args.device)

                # 1. 서버로 내 SNR 보고
                comm.send(current_snr_db, dest=0, tag=TAG_SNR_REPORT)
                
                # 2. 서버가 전체 최적화를 돌리고 정해준 차원 수신
                optimal_dim = comm.recv(source=0, tag=TAG_DIM_CMD)

                # =========================================================
                # [Step 2] Forward (Variable Compression & Channel Simulation)
                # =========================================================
                # 서버가 정해준 차원(optimal_dim)으로 자르기 (Adaptive Slicing)
                z = client.model(images, active_dim=optimal_dim)
                
                # 채널 통과 (노이즈 추가)
                noisy_output = client.channel(z, snr_db=current_snr_db)
                
                # 서버 모델의 디코더(FiLM 등) 입력용으로 SNR 정규화
                snr_normalized = (current_snr_db - TRAIN_MIN_SNR) / (TRAIN_MAX_SNR - TRAIN_MIN_SNR)
                snr_input = torch.tensor([[snr_normalized]] * images.size(0)).to(args.device)
                
                # =========================================================
                # [Step 3] 패킷 구성 및 서버 전송
                # =========================================================
                data_to_send = noisy_output.detach().cpu()
                
                current_comm_bytes = optimal_dim * 4
                total_comm_bytes += current_comm_bytes
                
                packet = {
                    'data': data_to_send, 
                    'label': labels.cpu(),
                    'snr': snr_input.cpu() 
                }
                comm.send(packet, dest=0, tag=TAG_FORWARD)
                
                # =========================================================
                # [Step 4] Backward (Gradient 수신 및 역전파)
                # =========================================================
                grad = comm.recv(source=0, tag=TAG_BACKWARD)
                grad = grad.to(args.device)
                
                noisy_output.backward(grad)
                client.optimizer.step()
                
                # =========================================================
                # [Logging]
                # =========================================================
            # 로그 출력
                if batch_idx % 50 == 0:
                    log_msg = (f"[Client {comm.rank}] Round: {round_idx+1} Epoch: {local_epoch+1}/{args.n_epochs} SNR: {current_snr_db:.2f}dB Dim: {optimal_dim}")
                    logger.info(log_msg)
                    print(log_msg)
                
        # --- Aggregation Phase ---
        _ = comm.recv(source=0, tag=TAG_AGG_REQ)
        my_weights = {k: v.cpu() for k, v in client.model.state_dict().items()}
        comm.send(my_weights, dest=0, tag=TAG_AGG_RES)
        new_weights = comm.recv(source=0, tag=TAG_AGG_RES)
        client.model.load_state_dict(new_weights)
        client.model.to(args.device)
        
    TAG_EXIT = 999
    print(f"Rank {comm.rank}: Training finished. Waiting for Server's EXIT signal...")
    
    msg = comm.recv(source=0, tag=TAG_EXIT)
    print(f"Rank {comm.rank}: Received {msg}. Shutting down.")
    return

 
# ===================================================================
# 5. Main Entry Point
# ===================================================================

def train_ssfl(comm, node, args, logger):
    rank = comm.Get_rank()
    size = comm.Get_size()
    num_clients = size - 1
    
    if rank == 0:
        return _run_server(comm, node, num_clients, args, logger)
    else:
        _run_client(comm, node, args, logger)
        return [], []

def train_ssflv4(comm, node, args, logger):
    rank = comm.Get_rank()
    size = comm.Get_size()
    num_clients = size - 1
    
    if rank == 0:
        return _run_server(comm, node, num_clients, args, logger)
    else:
        _run_clientv4(comm, node, args, logger)
        return [], []

def train_ssflv5(comm, node, args, logger):
    rank = comm.Get_rank()
    size = comm.Get_size()
    num_clients = size - 1
    
    if rank == 0:
        return _run_server(comm, node, num_clients, args, logger)
    else:
        _run_clientv5(comm, node, args, logger)
        return [], []

def train_ssflv6(comm, node, args, logger):
    rank = comm.Get_rank()
    size = comm.Get_size()
    num_clients = size - 1
    
    if rank == 0:
        return _run_server(comm, node, num_clients, args, logger)
    else:
        _run_clientv6(comm, node, args, logger)
        return [], []
    
def train_sc_usfl(comm, node, args, logger):
    rank = comm.Get_rank()
    size = comm.Get_size()
    num_clients = size - 1
    
    if rank == 0:
        return _run_server_sc_usfl(comm, node, num_clients, args, logger)
    else:
        _run_client_sc_usfl(comm, node, args, logger)
        return [], []

def train_sc_usfl_scm(comm, node, args, logger):
    rank = comm.Get_rank()
    size = comm.Get_size()
    num_clients = size - 1
    
    if rank == 0:
        return pretrain_scm(args, logger)

def train_fl(comm, node, args, logger):
    rank = comm.Get_rank()
    size = comm.Get_size()
    num_clients = size - 1
    if comm.rank == 0:
        return _run_server_fl(comm, node, num_clients, args, logger)
    else:
        return _run_client_fl(comm, node, args, logger)

class Trainer(object):
    def __init__(self, args):
        self.args = args

    def train(self, node, test_data, comm, logger, args):
        if args.algorithm == 'SSFLv4' or args.algorithm == 'SSFL_w_o_vib' or args.algorithm == 'SSFL_w_o_film' or args.algorithm == 'SSFL_w_o_beta':
            return train_ssflv4(comm, node, args, logger)
        elif args.algorithm == 'SSFLv5' or args.algorithm == 'SSFLv5_w_o_vib' or args.algorithm == 'SSFLv5_w_o_beta':
            return train_ssflv5(comm, node, args, logger)
        elif args.algorithm == 'SSFLv6' or args.algorithm == 'SSFLv6_w_o_vib' or args.algorithm == 'SSFLv6_w_o_vib_fair' or args.algorithm == 'SSFLv6_w_o_film' or args.algorithm == 'SSFLv6_w_o_beta':
            return train_ssflv6(comm, node, args, logger)
        elif args.algorithm == 'SFL':
            return train_ssfl(comm, node, args, logger)
        elif args.algorithm == 'SC-USFL':
            return train_sc_usfl(comm, node, args, logger)
        elif args.algorithm == 'SC-USFL_SCM':
            return train_sc_usfl_scm(comm, node, args, logger)
        elif args.algorithm == 'FL':
            return train_fl(comm, node, args, logger)
        else:
            raise ValueError("Unknown algorithm")
        
