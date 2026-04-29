# 평가용 데이터 로더
# (utils/trainer.py에 있는 get_dataloader 함수 필요, import 확인)
from utils.trainer import get_dataloader
import torch
import numpy as np
from models.model import AWGNChannel, RayleighChannel, apply_semantic_spreading


def compute_channel_kl(mu, log_var):
    kl = -0.5 * (1 + log_var - mu.pow(2) - log_var.exp())
    return kl


# ===================================================================
# 4. Evaluation Helper
# ===================================================================

class EvalNetworkStatusMonitor:
    def __init__(self):
        self.candidate_dims = [328, 492, 696, 1352]
        
    def get_optimal_dimension(self, snr_db):
        """
        평가 시에는 대역폭 경쟁이 없으므로, 절대적인 SNR 환경을 기준으로 
        가장 합리적인 차원(압축률)을 독립적으로 선택합니다.
        (논문의 SNR vs Accuracy 트렌드를 반영한 Thresholding)
        """
        if snr_db < 0.0:
            return 328   # 최악의 환경 (CR=1/12, 고압축)
        elif snr_db < 5.0:
            return 492   # 나쁜 환경 (CR=1/8)
        elif snr_db < 10.0:
            return 696   # 보통 환경 (CR=1/6)
        else:
            return 1352  # 좋은 환경 (CR=1/3, 저압축 고화질)

def evaluate_global_snr(args, client_model, server_model, dataloader, criterion, comm, channel=None):
    device = args.device
    algorithm = args.algorithm
    semantic_enable = args.semantic_enable
    
    client_model.eval()
    server_model.eval()
    
    correct = 0
    total = 0
    test_loss = 0.0
    
    # --- 가설 검증용 변수 (SSFLv4 용) ---
    total_overlap_ioU = 0.0
    valid_batches = 0
    
    # 비교를 위한 극단적 SNR 지점
    SNR_LOW = -5.0
    SNR_HIGH = 15.0
    
    # 학습 시 설정했던 SNR 범위
    TRAIN_MIN_SNR = -5.0
    TRAIN_MAX_SNR = 15.0
    MAX_DIM = 1352

    with torch.no_grad():
        for images, labels in dataloader:
            images, labels = images.to(device), labels.to(device)
            
            # 1. 현재 배치를 위한 랜덤 SNR 생성 및 인코딩 (0~1 Normalization)
            current_snr_db = np.random.uniform(TRAIN_MIN_SNR, TRAIN_MAX_SNR)
            snr_norm = (current_snr_db - TRAIN_MIN_SNR) / (TRAIN_MAX_SNR - TRAIN_MIN_SNR)
            snr_input = torch.tensor([[snr_norm]] * images.size(0)).float().to(device)
            
            # --- [가설 검증 로직] SNR 변화에 따른 채널 선택 변화 측정 (SSFLv4 전용) ---
            if 'SSFLv4' in algorithm:
                def get_mask_v4(target_snr_db):
                    # SNR 정규화
                    s_n = (target_snr_db - TRAIN_MIN_SNR) / (TRAIN_MAX_SNR - TRAIN_MIN_SNR)
                    s_in = torch.tensor([[s_n]] * images.size(0)).float().to(device)
                    
                    # v4 인코더는 z, mu, log_var 3개만 반환함
                    _, mu, log_var = client_model(images, snr_val=s_in)
                    
                    # 표준 VIB의 KL Divergence 공식 (Prior = N(0, 1))
                    # KL = -0.5 * (1 + log_var - mu^2 - exp(log_var))
                    kl = -0.5 * (1 + log_var - mu.pow(2) - log_var.exp())
                    
                    # 임계값에 따른 마스크 생성
                    mask = (kl > args.pruning_threshold).float()
                    return mask

                # 동일 이미지에 대해 저-SNR과 고-SNR 마스크 각각 생성
                mask_low = get_mask_v4(SNR_LOW)
                mask_high = get_mask_v4(SNR_HIGH)

                # IoU (Intersection over Union) 계산
                intersection = torch.sum(mask_low * mask_high)
                union = torch.sum(torch.max(mask_low, mask_high))
                
                if union > 0:
                    iou = intersection / union
                    total_overlap_ioU += iou.item()
                    valid_batches += 1
            # --- 가설 검증 로직 끝 ---

            # 2. Client Forward (실제 전송 및 테스트용)
            if semantic_enable == 1:
                if algorithm in ['SC-USFL', 'SC-USFL_SCM']:
                    # SC-USFL은 NSM이 차원을 결정 (이미 구현된 NSM 객체 사용)
                    # 여기서는 간단히 클래스 호출로 예시
                    nsm_eval = EvalNetworkStatusMonitor()
                    opt_dim = nsm_eval.get_optimal_dimension(current_snr_db)
                    z = client_model(images, active_dim=opt_dim)
                elif 'SSFLv6' in algorithm :
                    z, mu, log_var, film_mask = client_model(images, snr_val=snr_input)
                    kl_per_channel = compute_channel_kl(mu, log_var)
                    kl_mean_batch = kl_per_channel.mean(dim=0)
                    vib_mask = (kl_mean_batch > args.pruning_threshold).float()

                    if getattr(args, 'channel_mask_allpass_enable', 0):
                        chan_mask = torch.ones(z.size(1), device=device)
                    else:
                        dynamic_range = args.film_max_t - args.film_min_t
                        dynamic_threshold = args.film_max_t - (snr_norm * dynamic_range)
                        chan_mask = (film_mask[0] > dynamic_threshold).float()
                    mask = (vib_mask * chan_mask).detach()
                    index = torch.nonzero(mask > 0).squeeze(-1)

                    if index.numel() > 0:
                        active_z = torch.index_select(z, 1, index)
                        if args.semantic_spreading_enable:
                            active_z = apply_semantic_spreading(active_z)
                        z_masked = torch.zeros_like(z)
                        z_masked.scatter_(1, index.unsqueeze(0).expand(images.size(0), -1), active_z)
                    else:
                        z_masked = torch.zeros_like(z)
                elif 'SSFL' in algorithm :
                    # v4는 3개 반환 (z, mu, log_var)
                    z, _, _ = client_model(images, snr_val=snr_input)
                else:
                    z = client_model(images)
            else:
                z = client_model(images)
            
            # 3. Channel Simulation (Noise Injection)
            if channel is not None:
                # SNR 정보를 함께 넘겨서 해당 노이즈 환경 시뮬레이션
                if 'SSFLv6' in algorithm:
                    z = channel(z_masked, snr_db=current_snr_db) * mask
                else:
                    z = channel(z, snr_db=current_snr_db)
            
            # 4. Server Padding (SC-USFL 호환성)
            if algorithm in ['SC-USFL', 'SC-USFL_SCM']:
                curr_dim = z.size(1)
                if curr_dim < MAX_DIM:
                    padding = torch.zeros(z.size(0), MAX_DIM - curr_dim, device=device)
                    z = torch.cat([z, padding], dim=1)
            elif 'SSFLv6' in algorithm and index.numel() > 0:
                z = torch.index_select(z, 1, index)
            
            # 5. Server Forward
            # SSFLv4는 서버 디코더에도 FiLM이 있으므로 SNR 주입
            if 'SSFLv6' in algorithm:
                outputs = server_model(z, snr_val=snr_input, indices=index)
            elif 'SSFL' in algorithm:
                outputs = server_model(z, snr_val=snr_input)
            else:
                outputs = server_model(z)
    
            # 6. Metrics
            loss = criterion(outputs, labels)
            test_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
    avg_acc = 100.0 * correct / total
    avg_loss = test_loss / len(dataloader)
    
    # 가설 검증 최종 결과 (Mask IoU %)
    # 이 값이 낮을수록 "채널 상태에 따라 전송하는 정보의 종류를 바꾼다"는 뜻 (능동적 적응)
    avg_mask_overlap = (total_overlap_ioU / valid_batches) * 100.0 if valid_batches > 0 else 100.0
    
    return avg_acc, avg_loss, avg_mask_overlap

# def evaluate_global_snr(args, client_model, server_model, dataloader, criterion, comm, channel=None):
#     device = args.device
#     algorithm = args.algorithm
    
#     client_model.eval()
#     server_model.eval()
    
#     correct = 0
#     total = 0
#     test_loss = 0.0
    
#     # 평가용 파라미터 (학습시와 동일한 범위)
#     TRAIN_MIN_SNR = -5.0
#     TRAIN_MAX_SNR = 15.0
#     MAX_DIM = 1352

#     with torch.no_grad():
#         for images, labels in dataloader:
#             images, labels = images.to(device), labels.to(device)
            
#             # 테스트용 SNR 샘플링
#             current_snr_db = np.random.uniform(TRAIN_MIN_SNR, TRAIN_MAX_SNR)
#             snr_norm = (current_snr_db - TRAIN_MIN_SNR) / (TRAIN_MAX_SNR - TRAIN_MIN_SNR)
#             snr_input = torch.tensor([[snr_norm]] * images.size(0)).float().to(device)
            
#             # --- 1. Client Forward ---
#             if algorithm in ['SC-USFL', 'SC-USFL_SCM']:
#                 nsm = EvalNetworkStatusMonitor()
#                 # SC-USFL은 NSM이 차원을 결정
#                 # nsm 객체가 이 함수 밖에 있거나 어딘가에 정의되어 있어야 합니다.
#                 opt_dim = nsm.get_optimal_dimension(current_snr_db) 
#                 z = client_model(images, active_dim=opt_dim)
#             elif 'SSFLv6' in algorithm:
#                 # SSFL은 FiLM을 위해 SNR 입력 필요
#                 z, _, _ , _, _= client_model(images, snr_val=snr_input, labels=labels)
#             elif 'SSFL' in algorithm:
#                 # SSFL은 FiLM을 위해 SNR 입력 필요
#                 z, _, _= client_model(images, snr_val=snr_input)
#             else:
#                 # Standard SFL
#                 z = client_model(images)
            
#             # --- 2. Channel Injection ---
#             if channel is not None:
#                 # 채널 노이즈 추가 (SSFL/SC-USFL 모두 적용)
#                 z = channel(z, snr_db=current_snr_db)
            
#             # --- 3. Server Padding (SC-USFL만 적용) ---
#             if algorithm in ['SC-USFL', 'SC-USFL_SCM']:
#                 curr_dim = z.size(1)
#                 if curr_dim < MAX_DIM:
#                     padding = torch.zeros(z.size(0), MAX_DIM - curr_dim, device=device)
#                     z = torch.cat([z, padding], dim=1)
            
#             # --- 4. Server Forward ---
#             # ★ 핵심: SSFL 계열만 SNR을 서버 디코더(FiLM)에 전달
#             if 'SSFL' in algorithm and 'w_o_film' not in algorithm:
#                 outputs = server_model(z, snr_val=snr_input)
#             else:
#                 outputs = server_model(z)
    
#             # --- 5. 평가 ---
#             loss = criterion(outputs, labels)
#             test_loss += loss.item()
#             _, predicted = torch.max(outputs.data, 1)
#             total += labels.size(0)
#             correct += (predicted == labels).sum().item()
            
#     return 100.0 * correct / total, test_loss / len(dataloader)

def evaluate_global_fl(args, client_model, dataloader, criterion, comm):

    # 3. Evaluation
    # ★ [수정] evaluate_global_snr 대신 직접 평가 루프 사용
    client_model.eval()
    correct = 0
    total = 0
    test_loss = 0.0
    
    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs, labels = inputs.to(args.device), labels.to(args.device)
            
            # FL 모델은 이미지 -> 결과 바로 나옴
            outputs = client_model(inputs)
            
            # Loss 계산
            loss = criterion(outputs, labels)
            test_loss += loss.item()
            
            # 정확도 계산
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    # 평균 계산
    test_acc = 100 * correct / total
    avg_test_loss = test_loss / len(dataloader)

        
    return test_acc, avg_test_loss # Loss 리스트는 생략 가능

# =========================================================
# ★ 헬퍼 함수: run_exp_cuda0.py 상단이나 utils/trainer.py에 추가
# =========================================================
def evaluate_with_snr(args, client_model, server_model, test_loader, test_snr):
    # =========================================================
    # ★ [수정 1] args.snr_db가 아니라 현재 테스트하려는 test_snr을 넣습니다!
    # =========================================================
    if args.channel_type == 'awgn':
        test_channel = AWGNChannel(snr_db=test_snr).to(args.device)
    elif args.channel_type == 'rayleigh':
        test_channel = RayleighChannel(snr_db=test_snr).to(args.device)
        
    client_model.eval()
    if server_model is not None:
        server_model.eval()
    
    correct = 0
    total = 0
    
    TRAIN_MIN_SNR = -5.0
    TRAIN_MAX_SNR = 15.0
    snr_normalized = (test_snr - TRAIN_MIN_SNR) / (TRAIN_MAX_SNR - TRAIN_MIN_SNR)
    
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(args.device), labels.to(args.device)
            
            if args.algorithm == 'FL':
                outputs = client_model(images)
                
                # FL은 여기서 끝
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
                continue # FL은 채널 안 거치고 다음 배치로
            
            # SFL / SC-USFL / SSFL 로직
            if 'SSFL' in args.algorithm:
                snr_input = torch.full((images.size(0), 1), snr_normalized).float().to(args.device)
                z, mu, log_var, film_mask = client_model(images, snr_val=snr_input)
                kl_per_channel = compute_channel_kl(mu, log_var)
                kl_mean_batch = kl_per_channel.mean(dim=0)
                vib_mask = (kl_mean_batch > args.pruning_threshold).float()
                if getattr(args, 'channel_mask_allpass_enable', 0):
                    chan_mask = torch.ones(z.size(1), device=args.device)
                else:
                    dynamic_range = args.film_max_t - args.film_min_t
                    dynamic_threshold = args.film_max_t - (snr_normalized * dynamic_range)
                    chan_mask = (film_mask[0] > dynamic_threshold).float()
                mask = (vib_mask * chan_mask).detach()
                index = torch.nonzero(mask > 0).squeeze(-1)
                if index.numel() > 0:
                    active_z = torch.index_select(z, 1, index)
                    if args.semantic_spreading_enable:
                        active_z = apply_semantic_spreading(active_z)
                    z_masked = torch.zeros_like(z)
                    z_masked.scatter_(1, index.unsqueeze(0).expand(images.size(0), -1), active_z)
                else:
                    z_masked = torch.zeros_like(z)
            elif 'SC-USFL' in args.algorithm:
                z = client_model(images)
            else: # Standard SFL
                z = client_model(images)

            # =========================================================
            # ★ [수정 2] 확실하게 test_snr을 한 번 더 명시해줍니다!
            # =========================================================
            if 'SSFLv6' in args.algorithm:
                noisy_z = test_channel(z_masked, snr_db=test_snr) * mask
                if index.numel() > 0:
                    noisy_z = torch.index_select(noisy_z, 1, index)
                else:
                    noisy_z = noisy_z[:, :0]
            else:
                noisy_z = test_channel(z, snr_db=test_snr)

            # 3. Server Forward
            if 'SSFLv6' in args.algorithm:
                outputs = server_model(noisy_z, snr_val=snr_input, indices=index)
            elif 'SSFL' in args.algorithm:
                outputs = server_model(noisy_z, snr_val=snr_input)
            else:
                outputs = server_model(noisy_z)
                
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    acc = 100 * correct / total
    return acc, 0.0



def snr_eval(args, node, test_data, test_snr_list):
    
    # 테스트하고 싶은 SNR 목록
    snr_accuracies = []
    
    # 학습된 모델 가져오기
    # node는 Server 객체이므로, node.global_client_model과 node.model(Server)을 사용
    client_model = node.global_client_model
    server_model = node.model

    test_loader = get_dataloader(test_data, batch_size=100, is_train=False)

    # 평가 루프
    for test_snr in test_snr_list:
        # 1. 채널 노이즈 설정 변경
        # 클라이언트 모델 내부에 있는 채널의 snr_db를 강제로 변경해야 함
        # 하지만 evaluate_global 함수는 채널을 통과하지 않고 바로 모델에 넣는 구조일 수 있음.
        # 따라서, evaluate_global 함수 내부에서 채널을 통과시키도록 수정하거나,
        # 여기서 수동으로 노이즈를 주입해야 함.
        
        # 가장 확실한 방법: evaluate_global 함수를 호출할 때 채널 객체를 같이 넘겨주는 것.
        # 하지만 코드를 최소한으로 고치기 위해, 임시 채널을 생성해서 평가 함수에 적용
        
        # (아래 evaluate_with_snr 함수를 run_exp_cuda0.py 안에 새로 정의하거나 utils에 추가)
        acc, _ = evaluate_with_snr(args, client_model, server_model, test_loader, test_snr)
        
        print(f"[Test SNR {test_snr}dB] Accuracy: {acc:.2f}%")
        snr_accuracies.append(acc)
        
    return snr_accuracies
