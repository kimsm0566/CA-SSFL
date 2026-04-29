import os
import torch
import random

import numpy as np
from mpi4py import MPI
from data.data import get_data, partition_data
from utils.client import Client, Server 
from utils.trainer import Trainer
from utils.option import args_parser
from utils.logger import get_logger
from utils.eval import snr_eval


args = args_parser()
torch.cuda.empty_cache()



result_path = os.path.join(args.result_path,
                           args.dataset,
                           f'n_clients_{args.n_clients}',
                           f'n_client_data_{args.n_client_data}',
                           f'batch_size_{args.batch_size}',
                           f'data_partition_type_{args.partition_type}',
                           f'model_type_{args.model_type}',
                           f'major_percent_{args.major_percent}',
                           f'n_epochs_{args.n_epochs}', 
                           f'beta_{args.beta}',
                           f'pruning_threshold_{args.pruning_threshold}',
                           f'film_max_t_{args.film_max_t}',
                           f'film_min_t_{args.film_min_t}',
                           f'channel_mask_allpass_{args.channel_mask_allpass_enable}',
                           f'semantic_spreading_{args.semantic_spreading_enable}',
                           f'snr_adaptive_beta_{args.snr_adaptive_beta_enable}',
                           f'semantic_power_{args.semantic_power_enable}',
                           f'semantic_power_alpha_{args.semantic_power_alpha}',
                           f'latent_mixing_{args.latent_mixing_enable}',
                           f'latent_mixing_strength_{args.latent_mixing_strength}',
                           f'latent_mixing_groups_{args.latent_mixing_groups}',
                           f'encoder_downsample_{args.encoder_downsample_enable}',
                           f'encoder_downsample_mode_{args.encoder_downsample_mode}',
                           f'encoder_downsample_proj_dim_{args.encoder_downsample_proj_dim}',
                           f'semidense_{args.semidense_enable}',
                           f'semidense_group_size_{args.semidense_group_size}',
                           f'semidense_group_topk_{args.semidense_group_topk}',
                           f'support_floor_{args.support_floor_enable}',
                           f'support_floor_min_active_{args.support_floor_min_active}',
                           f'support_floor_snr_db_{args.support_floor_snr_db}',
                           f'importance_repetition_{args.importance_repetition_enable}',
                           f'importance_repetition_topk_{args.importance_repetition_topk}',
                           f'base_refinement_{args.base_refinement_enable}',
                           f'base_refinement_variable_{args.base_refinement_variable_enable}',
                           f'base_refinement_semantic_aware_{args.base_refinement_semantic_aware_enable}',
                           f'base_support_k_{args.base_support_k}',
                           f'refinement_support_k_{args.refinement_support_k}',
                           f'refinement_semantic_weight_{args.refinement_semantic_weight}',
                           f'refinement_channel_weight_{args.refinement_channel_weight}',
                           f'csi_source_mask_{args.csi_source_mask_enable}',
                           f'server_feature_impute_{args.server_feature_impute_enable}',
                           args.algorithm,
                           f'snr_{args.snr_db}',
                           f'compress_{args.compressed_dim}',
                           f'channel_type_{args.channel_type}'
                           )


def seed_everything(seed: int = 42):
    # 1. 파이썬 내장 랜덤 시드 고정
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    
    # 2. Numpy 시드 고정
    np.random.seed(seed)
    
    # 3. PyTorch 시드 고정 (CPU & GPU)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed) # 멀티 GPU 사용 시
    
    # 4. ★ GPU 연산(cuDNN)을 강제로 결정론적(Deterministic)으로 변경 ★
    # (주의: 연산 속도가 약 10~20% 느려질 수 있으나 100% 똑같은 결과 보장)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

# 메인 코드 시작 부분에 시드 고정 함수 호출
# (예: 시드 1번으로 고정)
seed_everything(args.seed)


np.random.seed(args.seed)
torch.manual_seed(args.seed)


# --- MPI 초기화 ---
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if not os.path.exists(result_path) and comm.rank == 0:
    os.makedirs(result_path)

# --- 설정 ---
args = args_parser()
args.device = torch.device(f"cuda:{args.device}" if torch.cuda.is_available() else "cpu")

if args.dataset == 'cifar100':
    args.n_class = 100
else :
    args.n_class = 10

# Non-semantic baselines must not enter semantic encoder/decoder paths.
if args.algorithm in ['SFL', 'FL']:
    args.semantic_enable = 0
    

# 데이터 로드 (공통)
train_X, train_y, test_X, test_y = get_data(args)
test_data = (test_X, test_y)
client_data_list = partition_data(train_X, train_y, args)
logger = get_logger(os.path.join(result_path,
                                       f"seed_{args.seed}_client_{comm.rank}.log"))
# --- 객체 생성 (분기) ---
node = None # Server 또는 Client 객체를 담을 변수

if rank == 0:
    # [Server Process]
    print(f"Rank {rank}: Initializing Server...")
    print(args)
    node = Server(data=test_data, args=args, rank=rank)
    
    if args.algorithm == 'SC-USFL':
        scm_dec_path = f"checkpoints/server_pretrained_{args.channel_type}_{args.dataset}.pth"
        if os.path.exists(scm_dec_path):
            node.model.semantic_decoder.load_state_dict(torch.load(scm_dec_path, weights_only=True))

        # 2. SCM Decoder 파라미터 얼리기
        for param in node.model.semantic_decoder.parameters():
            param.requires_grad = False
    
    logger = get_logger(os.path.join(result_path,
                                       f"seed_{args.seed}_server.log"))
else:
    # [Client Process]
    client_id = rank - 1
    print(f"Rank {rank}: Initializing Client {client_id}...")
    my_dataset = client_data_list[client_id]
    # Private Test Data는 필요시 생성 (여기선 생략하거나 더미)
    node = Client(data=my_dataset, private_test_data=None, args=args, rank=client_id)
    
    if args.algorithm == 'SC-USFL':
        scm_enc_path = f"checkpoints/client_pretrained_{args.channel_type}_{args.dataset}.pth"
        if os.path.exists(scm_enc_path):
            node.model.semantic_encoder.load_state_dict(torch.load(scm_enc_path, weights_only=True))
            print(f"Loaded SCM Encoder from {scm_enc_path}")
        else:
            print("Warning: SCM Pretrained weights not found! (Random Init)")

        # 2. SCM Encoder 파라미터 얼리기 (핵심!)
        # 이렇게 하면 optimizer.step()을 해도 이 부분은 업데이트되지 않습니다.
        for param in node.model.semantic_encoder.parameters():
            param.requires_grad = False
            
    logger = get_logger(os.path.join(result_path,
                                       f"seed_{args.seed}_client_{client_id}.log"))


# --- 학습 시작 ---
# node 변수에 서버 혹은 클라이언트 객체가 담겨있음
trainer = Trainer(args)
# train 함수 내부에서 rank를 체크하여 로직 분기
results = trainer.train(node, test_data, comm, logger, args)

TAG_EXIT=999

# =========================================================
# ★ 추가된 부분: 학습된 모델로 여러 SNR 테스트 (Evaluation Only)
# =========================================================
if rank == 0:
    print("\n>>> Start Multi-SNR Testing with Trained Model <<<")
    test_snr_list = [-6, -4, -2, 0, 2, 4, 6, 8, 10, 12]

    snr_accuracies = snr_eval(args, node, test_data, test_snr_list)

    # 결과 저장 (기존 학습 결과 + SNR 테스트 결과)
    if not os.path.exists(result_path): 
        os.makedirs(result_path)
    
    np.savez(
        os.path.join(result_path, f"seed_{args.seed}.npz"), 
        train_acc=results[0], 
        train_loss=results[1],
        comm=results[2],
        # mask=results[3],
        test_snrs=test_snr_list,      # X축
        snr_accs=snr_accuracies       # Y축
    )
    print("All Finished & Saved.")

    print("[Server] Sending EXIT signal to all clients...")
    
    for i in range(1, size):
        comm.send("EXIT", dest=i, tag=TAG_EXIT)

    print("[Server] Bye!")
