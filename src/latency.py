import torch
from thop import profile
import copy

def measure_ssfl_latency(model, args, data_size=5000, f_v=2.5e9, n_v=16):
    """
    f_v: 2.5 GHz (주파수)
    n_v: 16 (사이클당 연산량, 하드웨어 특성)
    """
    device = next(model.parameters()).device
    dummy_input = torch.randn(1, 3, 32, 32).to(device)
    dummy_snr = torch.randn(1, 1).to(device)

    # 1. 각 모듈별 Forward FLOPs 측정
    # Head (ResNet Front)
    f_head, _ = profile(copy.deepcopy(model.features), inputs=(dummy_input, ), verbose=False)
    
    # Encoder (FiLM + VIB)
    # forward(x, snr) 형태이므로 inputs 주의
    feat_map = torch.randn(1, 64, 8, 8).to(device)
    f_enc, _ = profile(copy.deepcopy(model.semantic_encoder), inputs=(feat_map, dummy_snr), verbose=False)

    # 2. 논문 방식 적용 (Trainable vs Frozen)
    c = 2 # Backward 가중치
    
    # Head는 학습하므로 (1+2)=3배, Encoder는 Frozen이므로 1배
    total_flops_per_sample = (1 + c) * f_head + (1 * f_enc)
    total_round_flops = total_flops_per_sample * data_size

    # 3. Latency 계산 (초 단위)
    # Latency = Total FLOPs / (Frequency * Capacity)
    latency = total_round_flops / (f_v * n_v)

    print(f"\n--- SSFL Model Execution Cost (Paper Method) ---")
    print(f"1. Head Forward FLOPs: {f_head/1e6:.2f} MFLOPs")
    print(f"2. Encoder Forward FLOPs: {f_enc/1e6:.2f} MFLOPs")
    print(f"3. Total FLOPs per Sample (Incl. Backward): {total_flops_per_sample/1e6:.2f} MFLOPs")
    print(f"4. Total FLOPs per Round (5k images): {total_round_flops/1e9:.2f} GFLOPs")
    print(f"5. Estimated Latency: {latency:.4f} seconds")
    
    return latency