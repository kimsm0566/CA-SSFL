import torch
import torch.nn as nn
from models.model import ClientResNet18v1, ClientResNet18v2, ServerResNet18, ServerResNet18v2, AWGNChannel, ResNet18_FL, SC_USFL_Encoder, SC_USFL_Decoder, FiLMChannelAwareEncoder, FiLMCNNSemanticDecoder
# ========================================================
# 파라미터 계산 헬퍼 함수
# ========================================================
def count_parameters(model, model_name="Model"):
    # requires_grad=True 인 학습 가능한 파라미터만 계산
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    # MB 단위 변환 (파라미터 1개당 float32 기준 4바이트)
    size_mb = (total_params * 4) / (1024 * 1024)
    
    print(f"{model_name:<30} | 파라미터 수: {total_params:>10,d} 개 | 크기: {size_mb:>6.2f} MB")
    return total_params

# ========================================================
# 더미 Args 객체 (초기화용)
# ========================================================
class DummyArgs:
    def __init__(self, algo, semantic_enable):
        self.algorithm = algo
        self.semantic_enable = semantic_enable
        self.compressed_dim = 256

if __name__ == "__main__":
    print("="*65)
    print(" 딥러닝 모듈별 파라미터 수 (Trainable Parameters) 분석")
    print("="*65)
    
    # 1. Standard SFL
    args_sfl = DummyArgs('SFL', semantic_enable=0)
    client_sfl = ClientResNet18v2(args_sfl)
    server_sfl = ServerResNet18v2(args_sfl)
    
    count_parameters(client_sfl.features, "[SFL] Client Backbone")
    count_parameters(server_sfl.layers,   "[SFL] Server Backbone")
    print("-" * 65)
    
    # 2. SC-USFL
    encoder_sc = SC_USFL_Encoder(input_channels=64, max_compressed_dim=1352)
    decoder_sc = SC_USFL_Decoder(compressed_dim=1352, output_channels=64)
    
    count_parameters(encoder_sc, "[SC-USFL] Encoder (338 Ch)")
    count_parameters(decoder_sc, "[SC-USFL] Decoder (338 Ch)")
    print("-" * 65)

    # 3. SSFLv4 (Proposed - Shared Base 경량화 버전)
    args_ssfl = DummyArgs('SSFLv4', semantic_enable=1)
    encoder_ssfl = FiLMChannelAwareEncoder(args_ssfl, input_channels=64, compressed_dim=256)
    decoder_ssfl = FiLMCNNSemanticDecoder(args_ssfl, compressed_dim=256, output_channels=64)
    
    count_parameters(encoder_ssfl, "[SSFLv4] Encoder (Shared)")
    count_parameters(decoder_ssfl, "[SSFLv4] Decoder (FiLM)")
    
    print("="*65)
    
    # 전체 비교
    print("\n[전체 클라이언트 탑재 모델 크기 비교]")
    count_parameters(client_sfl, "1. SFL Client Total")
    
    # SSFL 클라이언트 = Backbone + SSFLv4 Encoder
    ssfl_client_params = sum(p.numel() for p in client_sfl.parameters()) + sum(p.numel() for p in encoder_ssfl.parameters())
    print(f"2. SSFLv4 Client Total         | 파라미터 수: {ssfl_client_params:>10,d} 개 | 크기: {(ssfl_client_params*4)/(1024*1024):>6.2f} MB")