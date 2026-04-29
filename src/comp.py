import torch
import torchvision.models as models
from models.model import (
    ClientResNet18v2, ServerResNet18v2, ServerResNet18, 
    ClientResNet18v1, ResNet18_FL
)

class Args:
    def __init__(self, algo):
        self.semantic_enable = 1 if algo != 'SFL' else 0
        self.algorithm = algo
        self.compressed_dim = 1352 if 'SC-USFL' in algo else 256
        self.device = 'cpu'
        self.dataset = 'cifar10'

def count_parameters(model):
    """모델의 전체 파라미터 수를 계산하고 MB 단위로 리턴"""
    # 파라미터 개수
    num_params = sum(p.numel() for p in model.parameters())
    # 보통 파라미터는 float32(4 bytes)를 사용하므로
    return (num_params * 4) / (1024**2) 

def measure_params():
    print(f"=== Model Parameter Size Measurement (MB) ===\n")

    # 1. FedAvg
    fedavg = ResNet18_FL(Args('FedAvg'))
    mem_fed = count_parameters(fedavg)
    
    # 2. Standard SFL
    c_sfl = ClientResNet18v1(Args('SFL'))
    s_sfl = ServerResNet18(Args('SFL'))
    mem_sfl_c = count_parameters(c_sfl)
    mem_sfl_s = count_parameters(sfl_server_only := s_sfl.layers) + count_parameters(s_sfl.fc) # Body + Tail
    
    # 3. SC-USFL
    c_sc = ClientResNet18v2(Args('SC-USFL'))
    s_sc = ServerResNet18(Args('SC-USFL'))
    mem_sc_c = count_parameters(c_sc.features) + count_parameters(c_sc.semantic_encoder)
    mem_sc_s = count_parameters(s_sc.semantic_decoder) + count_parameters(s_sc.layers) + count_parameters(s_sc.fc)

    # 4. SSFL (Ours)
    c_ssfl = ClientResNet18v2(Args('SSFLv4'))
    s_ssfl = ServerResNet18v2(Args('SSFLv4'))
    mem_ssfl_c = count_parameters(c_ssfl.features) + count_parameters(c_ssfl.semantic_encoder)
    mem_ssfl_s = count_parameters(s_ssfl.semantic_decoder) + count_parameters(s_ssfl.layers) + count_parameters(s_ssfl.fc)

    # 출력
    print(f"{'Method':<15} | {'Client Mem (MB)':<16} | {'Server Mem (MB)':<16} | {'Total Mem (MB)'}")
    print("-" * 75)
    print(f"{'FedAvg':<15} | {mem_fed:<16.2f} | {'~0.00':<16} | {mem_fed:<16.2f}")
    print(f"{'Standard SFL':<15} | {mem_sfl_c:<16.2f} | {mem_sfl_s:<16.2f} | {mem_sfl_c + mem_sfl_s:<16.2f}")
    print(f"{'SC-USFL':<15} | {mem_sc_c:<16.2f} | {mem_sc_s:<16.2f} | {mem_sc_c + mem_sc_s:<16.2f}")
    print(f"{'SSFL (Ours)':<15} | {mem_ssfl_c:<16.2f} | {mem_ssfl_s:<16.2f} | {mem_ssfl_c + mem_ssfl_s:<16.2f}")
    print("=" * 75)

if __name__ == "__main__":
    measure_params()