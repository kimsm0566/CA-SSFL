import torch
import torch.nn as nn
import math
import numpy as np
import cvxpy as cp
from torchvision import models
import torch.nn.functional as F

# ==========================================
# 1. 유틸리티: 채널 노이즈 & 정규화
# ==========================================

_DCT_MATRIX_CACHE = {}


def _get_orthonormal_dct_matrix(size, device, dtype):
    cache_key = (size, str(device), str(dtype))
    if cache_key not in _DCT_MATRIX_CACHE:
        n = torch.arange(size, device=device, dtype=dtype)
        k = torch.arange(size, device=device, dtype=dtype).unsqueeze(1)
        dct = torch.cos(math.pi / size * (n + 0.5) * k)
        dct[0] *= math.sqrt(1.0 / size)
        if size > 1:
            dct[1:] *= math.sqrt(2.0 / size)
        _DCT_MATRIX_CACHE[cache_key] = dct
    return _DCT_MATRIX_CACHE[cache_key]


def apply_semantic_spreading(active_z):
    if active_z.size(1) == 0:
        return active_z
    dct = _get_orthonormal_dct_matrix(active_z.size(1), active_z.device, active_z.dtype)
    return torch.matmul(active_z, dct.t())


def invert_semantic_spreading(active_z):
    if active_z.size(1) == 0:
        return active_z
    dct = _get_orthonormal_dct_matrix(active_z.size(1), active_z.device, active_z.dtype)
    return torch.matmul(active_z, dct)

class AWGNChannel(nn.Module):
    def __init__(self, snr_db=12):
        super(AWGNChannel, self).__init__()
        self.snr_db = snr_db

    def forward(self, x, snr_db=None):
        current_snr = snr_db if snr_db is not None else self.snr_db
        batch_size = x.size(0)
        original_shape = x.shape
        
        x_flat = x.view(batch_size, -1)
        
        # =================================================================
        # ★ 핵심 수정: 0이 아닌 (실제 전송되는) 요소들만의 평균 전력을 구합니다.
        # =================================================================
        # x_flat != 0 인 요소의 개수를 구함 (배치별로 다를 수 있음)
        active_elements = torch.sum(x_flat != 0, dim=1, keepdim=True).float()
        
        # 복소수 심볼 개수이므로 2로 나누고, 0 나누기 방지를 위해 최소값 1.0 보장
        K_active = (active_elements / 2.0).clamp(min=1.0)
        
        # 실제 전송되는 심볼들의 평균 전력이 1이 되도록 정규화
        signal_power = torch.sum(x_flat ** 2, dim=1, keepdim=True) / K_active
        norm_factor = torch.sqrt(signal_power + 1e-8)
        x_norm = x_flat / norm_factor
        
        # Noise 생성 및 추가 (기존과 동일)
        noise_power = 10 ** (-current_snr / 10.0)
        noise_std = math.sqrt(noise_power / 2.0)
        
        noise = torch.randn_like(x_norm) * noise_std
        y = x_norm + noise
        
        return y.view(original_shape)


class RayleighChannel(nn.Module):
    def __init__(self, snr_db=12):
        super(RayleighChannel, self).__init__()
        self.snr_db = snr_db

    def forward(self, x, snr_db=None):
        current_snr = snr_db if snr_db is not None else self.snr_db
        
        batch_size = x.size(0)
        original_shape = x.shape
        
        x_flat = x.view(batch_size, -1)
        K = x_flat.size(1) // 2
        
        # Power Normalization (AWGN과 동일)
        active_elements = torch.sum(x_flat != 0, dim=1, keepdim=True).float()
        K_active = (active_elements / 2.0).clamp(min=1.0)
        
        signal_power = torch.sum(x_flat ** 2, dim=1, keepdim=True) / K_active
        norm_factor = torch.sqrt(signal_power + 1e-8)
        x_norm = x_flat / norm_factor
        
        x_complex = x_norm.view(batch_size, K, 2)
        x_r = x_complex[:, :, 0]
        x_i = x_complex[:, :, 1]
        
        # ==============================================================
        # ★ 수정 1: Slow Rayleigh Fading (블록 페이딩)
        # 이미지(Batch)당 1개의 채널 상태(h)를 가짐
        # ==============================================================
        h_r = torch.randn(batch_size, 1, device=x.device) * math.sqrt(0.5)
        h_i = torch.randn(batch_size, 1, device=x.device) * math.sqrt(0.5)
        
        # 3. 복소수 채널 통과 (y = h * x) (Broadcasting 됨)
        y_r = h_r * x_r - h_i * x_i
        y_i = h_r * x_i + h_i * x_r
        
        # 4. Complex AWGN 노이즈 추가
        noise_power = 10 ** (-current_snr / 10.0)
        noise_std = math.sqrt(noise_power / 2.0)
        
        y_r = y_r + torch.randn_like(y_r) * noise_std
        y_i = y_i + torch.randn_like(y_i) * noise_std
        
        # ==============================================================
        # ★ 수정 2: 수신단 등화 (Zero-Forcing Equalization)
        # 수신기가 완벽한 CSI(채널 상태 정보, h)를 안다고 가정하고 위상과 크기를 복구.
        # 이 과정 없이 CNN에 넣으면 성능이 비정상적으로 폭락합니다.
        # ==============================================================
        h_mag_sq = h_r**2 + h_i**2 + 1e-8 # 0 나누기 방지
        
        # y_eq = y * conj(h) / |h|^2
        y_r_eq = (y_r * h_r + y_i * h_i) / h_mag_sq
        y_i_eq = (y_i * h_r - y_r * h_i) / h_mag_sq
        
        # 6. 다시 실수 텐서로 조립 후 원래 모양으로 복구
        y_complex = torch.stack([y_r_eq, y_i_eq], dim=-1)
        y_out = y_complex.view(original_shape)
        
        return y_out
    
    
class SC_USFL_Encoder(nn.Module):
    def __init__(self, input_channels=64, max_compressed_dim=1352):
        super(SC_USFL_Encoder, self).__init__()
        
        # DeepJSCC 논문 규격 엄수: 5x5 커널, Stride(2,2,1,1,1), PReLU, No BatchNorm
        # 입력: [Batch, 64, 8, 8]
        self.layer1 = nn.Sequential(nn.Conv2d(input_channels, 16, 5, stride=2, padding=2), nn.PReLU()) # -> 4x4
        self.layer2 = nn.Sequential(nn.Conv2d(16, 32, 5, stride=2, padding=2), nn.PReLU())             # -> 2x2
        self.layer3 = nn.Sequential(nn.Conv2d(32, 32, 5, stride=1, padding=2), nn.PReLU())             # -> 2x2
        self.layer4 = nn.Sequential(nn.Conv2d(32, 32, 5, stride=1, padding=2), nn.PReLU())             # -> 2x2
        
        # 마지막 Layer 5
        # 최종적으로 1352차원을 만들어야 함. 현재 공간 크기가 2x2(총 4칸)이므로,
        # 채널 수는 1352 / 4 = 338 이 되어야 함.
        out_channels = max_compressed_dim // 4 
        self.layer5 = nn.Conv2d(32, out_channels, 5, stride=1, padding=2) # -> [Batch, 338, 2, 2]
        # (DeepJSCC 원본에 따라 마지막 레이어는 활성화 함수를 쓰지 않습니다)

    def forward(self, x, active_dim=None):
        # 1. 5층 CNN 특징 추출
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.layer5(x) #[Batch, 338, 2, 2]
        
        # 2. Flatten (1차원 벡터로 변환)
        z_full = x.view(x.size(0), -1) #[Batch, 1352]
        
        # 3. SC-USFL의 핵심: 외부 NSM 알고리즘 명령에 따라 가위로 싹둑 자르기 (Slicing)
        if active_dim is not None:
            z = z_full[:, :active_dim]
        else:
            z = z_full
            
        return z # VIB가 아니므로 mu, var 없이 z만 리턴

class SC_USFL_Decoder(nn.Module):
    def __init__(self, compressed_dim=1352, output_channels=64):
        super(SC_USFL_Decoder, self).__init__()
        self.compressed_dim = compressed_dim
        
        # 입력 차원을 2x2 피처맵으로 만들기 위한 채널 수 계산 (1352 / 4 = 338)
        in_channels = compressed_dim // 4
        
        # DeepJSCC 논문 규격 엄수: 인코더의 정확한 역순 (TransConv 5층)
        self.layer1 = nn.Sequential(nn.ConvTranspose2d(in_channels, 32, 5, stride=1, padding=2), nn.PReLU()) # -> 2x2
        self.layer2 = nn.Sequential(nn.ConvTranspose2d(32, 32, 5, stride=1, padding=2), nn.PReLU())          # -> 2x2
        self.layer3 = nn.Sequential(nn.ConvTranspose2d(32, 32, 5, stride=1, padding=2), nn.PReLU())          # -> 2x2
        
        # 크기를 키우는 레이어 (stride=2, output_padding=1 필수)
        self.layer4 = nn.Sequential(nn.ConvTranspose2d(32, 16, 5, stride=2, padding=2, output_padding=1), nn.PReLU()) # -> 4x4
        self.layer5 = nn.ConvTranspose2d(16, output_channels, 5, stride=2, padding=2, output_padding=1)               # -> 8x8

    def forward(self, z):
        # 1. Zero Padding (클라이언트가 328개만 보냈어도 서버는 1352개로 채워 넣음)
        curr_dim = z.size(1)
        if curr_dim < self.compressed_dim:
            padding = torch.zeros(z.size(0), self.compressed_dim - curr_dim, device=z.device)
            z = torch.cat([z, padding], dim=1) # [Batch, 1352] 복구 완료
            
        # 2. Reshape (벡터를 다시 3D 피처맵으로 변환)
        # 1352 = 338 채널 * 2 * 2
        in_channels = self.compressed_dim // 4
        x = z.view(-1, in_channels, 2, 2)
        
        # 3. 5층 역합성곱 복원
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.layer5(x) # [Batch, 64, 8, 8]
        
        return x

# ==============================================================================
# 1. FiLM + VIB 기반 시맨틱 인코더 (클라이언트용)
# ==============================================================================
# 기존 인코더
# class FiLMChannelAwareEncoder(nn.Module):
#     def __init__(self, args, input_channels=64, compressed_dim=256):
#         """
#         Input: [Batch, 64, 8, 8] (ResNet Layer1 output)
#         Output: z [Batch, compressed_dim]
#         """
#         self.use_film = True
#         self.use_vib = True
#         # ★ Ablation Flag 설정
#         if args.algorithm == 'SSFL_w_o_film':
#             self.use_film = False
#         if args.algorithm == 'SSFL_w_o_vib':
#             self.use_vib = False
        
#         super(FiLMChannelAwareEncoder, self).__init__()
        
#         # 1. DeepJSCC Backbone
#         self.layer1 = nn.Sequential(nn.Conv2d(input_channels, 16, 5, stride=2, padding=2), nn.PReLU())
#         self.layer2 = nn.Sequential(nn.Conv2d(16, 32, 5, stride=2, padding=2), nn.PReLU())
#         self.layer3 = nn.Sequential(nn.Conv2d(32, 32, 5, stride=1, padding=2), nn.PReLU())
#         self.layer4 = nn.Sequential(nn.Conv2d(32, 32, 5, stride=1, padding=2), nn.PReLU())
        
#         # 2. Layer 5
#         self.layer5_conv = nn.Conv2d(32, 64, 5, stride=1, padding=2)
#         self.layer5_bn = nn.BatchNorm2d(64)
#         self.layer5_prelu = nn.PReLU()
        
#         # 3. FiLM Generator (use_film일 때만 사용하지만, 구조 유지를 위해 선언은 해둠)
#         self.snr_to_film = nn.Sequential(
#             nn.Linear(4, 64), # 입력이 1차원에서 4차원(Fourier)으로 바뀜
#             nn.SiLU(),        # ReLU보다 조건부 변조에 훨씬 강력한 SiLU(Swish) 사용
#             nn.Linear(64, 64),
#             nn.SiLU(),
#             nn.Linear(64, 64 * 2)
#         )
        
#         # self.snr_to_film[-1].weight.data.fill_(0)
#         # self.snr_to_film[-1].bias.data[:64].fill_(1)
#         # self.snr_to_film[-1].bias.data[64:].fill_(0)

#         nn.init.normal_(self.snr_to_film[-1].weight, std=0.01)
#         nn.init.constant_(self.snr_to_film[-1].bias, 0.0) 
        
#         # # 4. VIB Heads
#         # self.flatten_dim = 64 * 2 * 2 
#         # self.fc_mu = nn.Linear(self.flatten_dim, compressed_dim)
        
#         # if self.use_vib:
#         #     self.fc_var = nn.Linear(self.flatten_dim, compressed_dim)
#         # =======================================================
#         # 4. ★ VIB Heads 경량화 (Shared Base 구조) ★
#         # =======================================================
#         self.flatten_dim = 64 * 2 * 2 # 256
        
#         # 공통 특징 추출 레이어 (Shared Feature Extractor)
#         self.fc_shared = nn.Sequential(
#             nn.Linear(self.flatten_dim, compressed_dim),
#             nn.PReLU()
#         )
#         # 평균(μ) 예측
#         self.fc_mu = nn.Linear(compressed_dim, compressed_dim)
        
#         if self.use_vib:
#             # 분산(σ^2) 예측 - VIB가 켜져 있을 때만 사용
#             self.fc_var = nn.Linear(compressed_dim, compressed_dim)
#             nn.init.constant_(self.fc_var.bias, -5.0)
    
#     def embed_snr(self, snr_val):
#         """ 1개의 스칼라 SNR을 4개의 특성으로 쪼개서 민감도를 극대화 """
#         # snr_val:[Batch, 1]
#         freqs = torch.exp(torch.arange(0, 2, dtype=torch.float32, device=snr_val.device) * math.log(10.0))
#         #[Batch, 2]
#         x = snr_val * freqs 
#         # sin, cos을 섞어서 [Batch, 4]로 만듦
#         return torch.cat([torch.sin(x), torch.cos(x)], dim=-1)
    
#     def reparameterize(self, mu, log_var):
#         std = torch.exp(0.5 * log_var)
#         eps = torch.randn_like(std)
#         return mu + eps * std

#     def forward(self, x, snr_val):
#         # A. Feature Extraction
#         x = self.layer1(x)
#         x = self.layer2(x)
#         x = self.layer3(x)
#         x = self.layer4(x)
#         x = self.layer5_conv(x)
#         x = self.layer5_bn(x)
        
#         # B. ★ 강력해진 FiLM 분기 처리 ★
#         if self.use_film:
#             # 1. SNR 임베딩 (스칼라 1개 -> 벡터 4개)
#             snr_emb = self.embed_snr(snr_val)
            
#             # 2. FiLM 파라미터 생성
#             film_params = self.snr_to_film(snr_emb)
#             delta_gamma, beta = torch.split(film_params, 64, dim=1)
            
#             # 3. Residual FiLM 적용 (감마를 1 + delta_gamma 로 설정)
#             # 이렇게 하면 초반에는 delta_gamma가 0에 가까워 x가 보존되지만, 
#             # 학습되면서 delta_gamma가 적극적으로 개입하게 됩니다.
#             gamma = 1.0 + delta_gamma
            
#             x = (gamma.view(-1, 64, 1, 1) * x) + beta.view(-1, 64, 1, 1)
            
#         x = self.layer5_prelu(x)
        
#         # C. ★ 경량화된 VIB 로직 ★
#         x_flat = x.flatten(1)
        
#         # 공통 특징 추출
#         shared_feat = self.fc_shared(x_flat)
        
#         # 평균 계산
#         mu = self.fc_mu(shared_feat)
        
#         if self.use_vib:
#             # 분산 계산 및 샘플링
#             log_var = self.fc_var(shared_feat)
#             log_var_full = torch.clamp(log_var, min=-10.0, max=10.0) 
#             z = self.reparameterize(mu, log_var_full) if self.training else mu
#             return z, mu, log_var_full
#         else:
#             # VIB가 없을 때 (결정론적 인코더)
#             z = mu
#             dummy_log_var = torch.zeros_like(mu)
#             return z, mu, dummy_log_var

# class FiLMChannelAwareEncoder(nn.Module):
#     def __init__(self, args, input_channels=64, compressed_dim=256):
#         """
#         [Flow] Feature(CNN) -> VIB(Mu, Var) -> Sampling(z) -> FiLM(Modulation)
#         Input:[Batch, 64, 8, 8]
#         """
#         super(FiLMChannelAwareEncoder, self).__init__()
#         self.use_film = 'w_o_film' not in args.algorithm
#         self.use_vib = 'w_o_vib' not in args.algorithm
#         self.compressed_dim = compressed_dim
        
#         # 1. DeepJSCC Backbone (경량화 버전: 8x8 -> 2x2)
#         self.layer1 = nn.Sequential(nn.Conv2d(input_channels, 16, 5, stride=2, padding=2), nn.PReLU()) # -> 4x4
#         self.layer2 = nn.Sequential(nn.Conv2d(16, 32, 5, stride=2, padding=2), nn.PReLU())             # -> 2x2
#         self.layer3 = nn.Sequential(nn.Conv2d(32, 32, 5, stride=1, padding=2), nn.PReLU())             # -> 2x2
#         self.layer4 = nn.Sequential(nn.Conv2d(32, 32, 5, stride=1, padding=2), nn.PReLU())             # -> 2x2
        
#         # 2. Layer 5
#         # ★ 수정: layer4의 출력 채널인 32를 받도록 수정
#         self.layer5_conv = nn.Conv2d(32, 64, 3, 1, 1)                                                  # -> 2x2
#         self.layer5_bn = nn.BatchNorm2d(64)
#         self.layer5_prelu = nn.PReLU()
        
#         # 3. VIB Heads
#         # ★ 수정: 최종 크기가 2x2이므로 64 * 2 * 2 = 256
#         self.flatten_dim = 64 * 2 * 2  
        
#         self.fc_shared = nn.Sequential(nn.Linear(self.flatten_dim, compressed_dim), nn.PReLU())
#         self.fc_mu = nn.Linear(compressed_dim, compressed_dim)
        
#         if self.use_vib:
#             self.fc_var = nn.Linear(compressed_dim, compressed_dim)
#             nn.init.constant_(self.fc_var.bias, -5.0)

#         # 4. FiLM Generator (z 차원에 직접 곱해짐)
#         if self.use_film:
#             self.snr_to_film = nn.Sequential(
#                 nn.Linear(1, 32),
#                 nn.ReLU(),
#                 nn.Linear(32, compressed_dim * 2)
#             )
#             self.snr_to_film[-1].weight.data.fill_(0)
#             self.snr_to_film[-1].bias.data[:compressed_dim].fill_(1) 
#             self.snr_to_film[-1].bias.data[compressed_dim:].fill_(0) 

#     def reparameterize(self, mu, log_var):
#         std = torch.exp(0.5 * log_var)
#         eps = torch.randn_like(std)
#         return mu + eps * std

#     def forward(self, x, snr_val):
#         # A. Feature Extraction
#         x = self.layer1(x)
#         x = self.layer2(x)
#         x = self.layer3(x)
#         x = self.layer4(x)
#         x = self.layer5_conv(x)
#         x = self.layer5_bn(x)
#         x = self.layer5_prelu(x)
        
#         # B. VIB (KL Loss 계산용)
#         x_flat = x.flatten(1) 
#         shared_feat = self.fc_shared(x_flat)
#         mu = self.fc_mu(shared_feat)
        
#         if self.use_vib:
#             log_var = self.fc_var(shared_feat)
#             log_var_full = torch.clamp(log_var, min=-10.0, max=10.0) 
#             z_latent = self.reparameterize(mu, log_var_full) if self.training else mu
#         else:
#             z_latent = mu
#             log_var_full = torch.zeros_like(mu)

#         # C. FiLM (샘플링 된 이후에 채널 적응)
#         if self.use_film:
#             film_params = self.snr_to_film(snr_val)
#             gamma, beta = torch.split(film_params, self.compressed_dim, dim=1)
#             z = (gamma * z_latent) + beta
#         else:
#             z = z_latent

#         return z, mu, log_var_full

#new 필름 인코더
# class FiLMChannelAwareEncoder(nn.Module):
#     def __init__(self, args, input_channels=64, compressed_dim=256):
#         super(FiLMChannelAwareEncoder, self).__init__()
#         self.use_film = 'w_o_film' not in args.algorithm
#         self.use_vib = 'w_o_vib' not in args.algorithm
#         self.compressed_dim = compressed_dim
        
#         # 1. DeepJSCC Backbone
#         self.layer1 = nn.Sequential(nn.Conv2d(input_channels, 16, 5, stride=2, padding=2), nn.PReLU())
#         self.layer2 = nn.Sequential(nn.Conv2d(16, 32, 5, stride=2, padding=2), nn.PReLU())
#         self.layer3 = nn.Sequential(nn.Conv2d(32, 32, 5, stride=1, padding=2), nn.PReLU())
#         self.layer4 = nn.Sequential(nn.Conv2d(32, 32, 5, stride=1, padding=2), nn.PReLU())
        
#         # 2. Layer 5
#         self.layer5_conv = nn.Conv2d(32, 64, 3, 1, 1)
#         self.layer5_bn = nn.BatchNorm2d(64)
#         self.layer5_prelu = nn.PReLU()
        
#         # 3. VIB Heads
#         self.flatten_dim = 64 * 2 * 2  
        
#         self.fc_shared = nn.Sequential(nn.Linear(self.flatten_dim, compressed_dim), nn.PReLU())
#         self.fc_mu = nn.Linear(compressed_dim, compressed_dim)
        
#         if self.use_vib:
#             self.fc_var = nn.Linear(compressed_dim, compressed_dim)
#             nn.init.constant_(self.fc_var.bias, -5.0)

#         # 4. 수정된 FiLM Generator (Gating Network 역할)
#         if self.use_film:
#             self.snr_to_film = nn.Sequential(
#                 nn.Linear(1, 32),
#                 nn.ReLU(),
#                 # beta 없이 gamma(Mask)만 출력하도록 차원 축소
#                 nn.Linear(32, compressed_dim), 
#                 # 핵심! 0~1 사이의 마스크 값으로 변환
#                 nn.Sigmoid() 
#             )

#     def reparameterize(self, mu, log_var):
#         std = torch.exp(0.5 * log_var)
#         eps = torch.randn_like(std)
#         return mu + eps * std

#     def forward(self, x, snr_val):
#         # A. Feature Extraction
#         x = self.layer1(x)
#         x = self.layer2(x)
#         x = self.layer3(x)
#         x = self.layer4(x)
#         x = self.layer5_conv(x)
#         x = self.layer5_bn(x)
#         x = self.layer5_prelu(x)
        
#         x_flat = x.flatten(1) 
#         shared_feat = self.fc_shared(x_flat)
        
#         # B. FiLM (Gating Mask 생성)
#         if self.use_film:
#             # snr_val에 따라 0~1 사이의 마스크 생성
#             film_mask = self.snr_to_film(snr_val) # Shape: [Batch, 256]
            
#             # (선택) 추론(Test) 시에는 확실한 차원 압축을 위해 Hard Mask(0 또는 1)로 변환
#             if not self.training:
#                 # 임계값 0.5 이하는 통신에서 아예 제외(0으로 만듦)
#                 film_mask = (film_mask > 0.5).float() 
#         else:
#             film_mask = torch.ones(x.size(0), self.compressed_dim, device=x.device)

#         # C. VIB 연산 (Mask 적용)
#         mu = self.fc_mu(shared_feat)
        
#         # 핵심 변경: mu에 직접 마스크를 씌워 정보량을 통제함
#         mu = mu * film_mask 
        
#         if self.use_vib:
#             log_var = self.fc_var(shared_feat)
#             log_var_full = torch.clamp(log_var, min=-10.0, max=10.0)
            
#             # 마스크된 차원(버려진 차원)은 분산을 1(log_var=0)로 강제하여 KL Loss를 0으로 만듦 (정보량 0)
#             log_var_full = log_var_full * film_mask 
            
#             # Reparameterization
#             z_latent = self.reparameterize(mu, log_var_full) if self.training else mu
#         else:
#             z_latent = mu
#             log_var_full = torch.zeros_like(mu)

#         return z_latent, mu, log_var_full, film_mask

class FiLMChannelAwareEncoder(nn.Module):
    def __init__(self, args, input_channels=64, compressed_dim=4096):
        super(FiLMChannelAwareEncoder, self).__init__()
        self.use_film = 'w_o_film' not in args.algorithm
        self.use_vib = 'w_o_vib' not in args.algorithm
        self.use_latent_mixing = bool(getattr(args, 'latent_mixing_enable', 0))
        self.latent_mixing_strength = float(getattr(args, 'latent_mixing_strength', 0.0))
        self.use_encoder_downsample = bool(getattr(args, 'encoder_downsample_enable', 0))
        self.encoder_downsample_mode = getattr(args, 'encoder_downsample_mode', 'stride2_proj')
        self.encoder_downsample_proj_dim = int(getattr(args, 'encoder_downsample_proj_dim', compressed_dim))
        self.use_csi_source_mask = bool(getattr(args, 'csi_source_mask_enable', 0))
        self.feature_dim = compressed_dim # 4096 (64 * 8 * 8)
        
        # 1. Backbone (stride=2를 모두 stride=1로 변경하여 8x8 크기 유지!)
        self.layer1 = nn.Sequential(nn.Conv2d(input_channels, 16, 5, stride=1, padding=2), nn.PReLU())
        self.layer2 = nn.Sequential(nn.Conv2d(16, 32, 5, stride=1, padding=2), nn.PReLU())
        self.layer3 = nn.Sequential(nn.Conv2d(32, 32, 5, stride=1, padding=2), nn.PReLU())
        self.layer4 = nn.Sequential(nn.Conv2d(32, 32, 5, stride=1, padding=2), nn.PReLU())
        self.layer5_conv = nn.Conv2d(32, 64, 3, stride=1, padding=1)
        self.layer5_bn = nn.BatchNorm2d(64)
        self.layer5_prelu = nn.PReLU()

        if self.use_latent_mixing:
            mix_groups = max(1, int(getattr(args, 'latent_mixing_groups', 8)))
            if 64 % mix_groups != 0:
                mix_groups = 1
            self.latent_mixer = nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1, groups=mix_groups, bias=False)
            nn.init.kaiming_normal_(self.latent_mixer.weight, nonlinearity='linear')

        if self.use_encoder_downsample:
            self.downsample_block = nn.Sequential(
                nn.Conv2d(64, 64, kernel_size=3, stride=2, padding=1),
                nn.BatchNorm2d(64),
                nn.PReLU(),
            )
            self.upsample_block = nn.Sequential(
                nn.ConvTranspose2d(64, 64, kernel_size=4, stride=2, padding=1),
                nn.BatchNorm2d(64),
                nn.PReLU(),
            )

        # 2. 파라미터 폭발을 막는 1x1 Conv VIB Heads (출력: [Batch, 64, 8, 8])
        self.conv_mu = nn.Conv2d(64, 64, kernel_size=1)
        if self.use_vib:
            self.conv_var = nn.Conv2d(64, 64, kernel_size=1)
            nn.init.constant_(self.conv_var.bias, -5.0)

        # 3. FiLM Generator (4096 차원 출력)
        if self.use_film:
            film_input_dim = 3 if self.use_csi_source_mask else 1
            self.snr_to_film = nn.Sequential(
                nn.Linear(film_input_dim, 64),
                nn.ReLU(),
                nn.Linear(64, self.feature_dim), # 4096개의 마스크
                nn.Sigmoid()
            )

    def reparameterize(self, mu, log_var):
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        return mu + eps * std

    def forward(self, x, snr_val):
        # A. Feature Extraction
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.layer5_conv(x)
        x = self.layer5_bn(x)
        x = self.layer5_prelu(x) # [Batch, 64, 8, 8] 크기 유지됨

        if self.use_latent_mixing and self.latent_mixing_strength > 0.0:
            mixed_x = self.latent_mixer(x)
            x = x + (self.latent_mixing_strength * mixed_x)

        if self.use_encoder_downsample:
            x = self.downsample_block(x)
            x = self.upsample_block(x)

        # B. Latent parameterization
        mu_2d = self.conv_mu(x)       #[Batch, 64, 8, 8]
        mu = mu_2d.flatten(1)         #[Batch, 4096] 차원 완벽 일치!
        
        # C. FiLM Gating Mask 적용
        if self.use_film:
            if self.use_csi_source_mask:
                feat_mean = x.abs().mean(dim=(1, 2, 3), keepdim=False).unsqueeze(1)
                feat_std = x.flatten(1).std(dim=1, keepdim=True, unbiased=False)
                film_input = torch.cat([snr_val, feat_mean, feat_std], dim=1)
            else:
                film_input = snr_val
            film_mask = self.snr_to_film(film_input) # [Batch, 4096]
            if not self.training:
                film_mask = (film_mask > 0.5).float()
        else:
            film_mask = torch.ones_like(mu)

        # 이제 mu와 film_mask 모두 4096차원이므로 에러 없이 곱해집니다.
        mu = mu * film_mask 
        
        # D. Reparameterization
        if self.use_vib:
            log_var_2d = self.conv_var(x)
            log_var_full = torch.clamp(log_var_2d.flatten(1), min=-10.0, max=10.0)
            log_var_full = log_var_full * film_mask 
            z_latent = self.reparameterize(mu, log_var_full) if self.training else mu
        else:
            z_latent = mu
            log_var_full = torch.zeros_like(mu)

        # 통신에 사용될 차원의 위치 인덱스도 반환 (Decoder에서 복원 시 필요할 수 있음)
        return z_latent, mu, log_var_full, film_mask


# ==============================================================================
# 2. FiLM + DeepJSCC 기반 시맨틱 디코더 (서버용)
# ==============================================================================
# class FiLMCNNSemanticDecoder(nn.Module):
#     def __init__(self, args, compressed_dim=256, output_channels=64):
#         super(FiLMCNNSemanticDecoder, self).__init__()
#         self.compressed_dim = compressed_dim
#         self.use_film = True
#         self.device = args.device
        
#         # ★ Ablation Flag 설정
#         self.use_film = 'w/o_film' not in args.algorithm
    
#         # 1. Vector to Feature Map
#         self.fc_expand = nn.Linear(self.compressed_dim, 64 * 2 * 2)
        
#         # =======================================================
#         # 2. ★ 강화된 SNR Embedding & FiLM Generator ★
#         # =======================================================
#         # 기존: Linear(1, 32) -> ReLU -> Linear(32, 128)
#         # 변경: 푸리에 특징(4차원) -> SiLU -> 64 -> SiLU -> 128
#         self.snr_to_film = nn.Sequential(
#             nn.Linear(4, 64), 
#             nn.SiLU(),        # ReLU보다 조건부 변조에 강력한 SiLU
#             nn.Linear(64, 64),
#             nn.SiLU(),
#             nn.Linear(64, 64 * 2)
#         )
        
#         # 안정적인 학습 시작을 위해 마지막 레이어 가중치를 작게 초기화 (Residual FiLM용)
#         nn.init.normal_(self.snr_to_film[-1].weight, std=0.01)
#         nn.init.constant_(self.snr_to_film[-1].bias, 0.0)

#         # 3. DeepJSCC Transpose Backbone
#         self.layer1 = nn.Sequential(nn.ConvTranspose2d(64, 64, 5, stride=1, padding=2), nn.PReLU())
#         self.layer2 = nn.Sequential(nn.ConvTranspose2d(64, 32, 5, stride=1, padding=2), nn.PReLU())
#         self.layer3 = nn.Sequential(nn.ConvTranspose2d(32, 32, 5, stride=1, padding=2), nn.PReLU())
#         self.layer4 = nn.Sequential(nn.ConvTranspose2d(32, 16, 5, stride=2, padding=2, output_padding=1), nn.PReLU())
#         self.layer5 = nn.Sequential(nn.ConvTranspose2d(16, output_channels, 5, stride=2, padding=2, output_padding=1))

#     # =======================================================
#     # ★ SNR 임베딩 헬퍼 함수 (스칼라 -> 4차원 주파수 벡터)
#     # =======================================================
#     def embed_snr(self, snr_val):
#         # snr_val: [Batch, 1]
#         freqs = torch.exp(torch.arange(0, 2, dtype=torch.float32, device=self.device) * math.log(10.0))
#         x = snr_val * freqs  # [Batch, 2]
#         return torch.cat([torch.sin(x), torch.cos(x)], dim=-1) #[Batch, 4]

#     def forward(self, z, snr_val):
#         # A. Zero Padding (Variable-rate 지원 - 이 부분은 VIB 유무 상관없이 구조적 안정성을 위해 유지)
#         curr_dim = z.size(1)
#         if curr_dim < self.compressed_dim:
#             padding = torch.zeros(z.size(0), self.compressed_dim - curr_dim, device=z.device)
#             z = torch.cat([z, padding], dim=1)
            
#         # B. Map to Feature Space
#         x = self.fc_expand(z)
#         x = x.view(-1, 64, 2, 2)
        
#         # C. ★ 강화된 Decoder FiLM 분기 처리 (Residual FiLM) ★
#         if self.use_film:
#             # 1. 스칼라 SNR을 4차원 주파수 특징으로 임베딩 (민감도 극대화)
#             snr_emb = self.embed_snr(snr_val)
            
#             # 2. MLP를 통해 델타 감마와 베타 예측
#             film_params = self.snr_to_film(snr_emb)
#             delta_gamma, beta = torch.split(film_params, 64, dim=1)
            
#             # 3. Residual 계산 (기본값 1.0에 델타를 더함)
#             gamma = 1.0 + delta_gamma
            
#             # 4. 피처맵에 적용
#             x = (gamma.view(-1, 64, 1, 1) * x) + beta.view(-1, 64, 1, 1)
        
#         # D. Upsampling
#         x = self.layer1(x)
#         x = self.layer2(x)
#         x = self.layer3(x)
#         x = self.layer4(x)
#         x = self.layer5(x)
        
#         return x
    
# class FiLMCNNSemanticDecoder(nn.Module):
#     def __init__(self, args, compressed_dim=256, output_channels=64):
#         super(FiLMCNNSemanticDecoder, self).__init__()
#         self.compressed_dim = compressed_dim
#         self.use_film = 'w_o_film' not in args.algorithm
    
#         # 1. Vector to Feature Map
#         # 수신된 벡터를 다시 64채널의 2x2 피처맵 크기로 확장
#         self.fc_expand = nn.Linear(self.compressed_dim, 64 * 2 * 2)
        
#         # =======================================================
#         # 2. ★ 기존(Standard) FiLM Generator ★
#         # SNR 스칼라(1차원)를 직접 입력받는 단순 MLP 구조
#         # =======================================================
#         if self.use_film:
#             self.snr_to_film = nn.Sequential(
#                 nn.Linear(1, 32),
#                 nn.ReLU(),
#                 nn.Linear(32, 64 * 2) # Gamma(64개) + Beta(64개)
#             )
            
#             # Identity 초기화: 학습 초반에는 입력 피처를 그대로 보존하도록 설정
#             self.snr_to_film[-1].weight.data.fill_(0)
#             self.snr_to_film[-1].bias.data[:64].fill_(1)  # Gamma 초기값 1
#             self.snr_to_film[-1].bias.data[64:].fill_(0)  # Beta 초기값 0

#         # 3. DeepJSCC Transpose Backbone (2x2 -> 8x8 복원)
#         self.layer1 = nn.Sequential(nn.ConvTranspose2d(64, 64, 5, stride=1, padding=2), nn.PReLU())
#         self.layer2 = nn.Sequential(nn.ConvTranspose2d(64, 32, 5, stride=1, padding=2), nn.PReLU())
#         self.layer3 = nn.Sequential(nn.ConvTranspose2d(32, 32, 5, stride=1, padding=2), nn.PReLU())
#         # 해상도 키우기 (2x2 -> 4x4 -> 8x8)
#         self.layer4 = nn.Sequential(nn.ConvTranspose2d(32, 16, 5, stride=2, padding=2, output_padding=1), nn.PReLU())
#         self.layer5 = nn.Sequential(nn.ConvTranspose2d(16, output_channels, 5, stride=2, padding=2, output_padding=1))

#     def forward(self, z, snr_val):
#         # A. Zero Padding (가변 전송 시 대응)
#         curr_dim = z.size(1)
#         if curr_dim < self.compressed_dim:
#             padding = torch.zeros(z.size(0), self.compressed_dim - curr_dim, device=z.device)
#             z = torch.cat([z, padding], dim=1)
            
#         # B. Map to Feature Space
#         x = self.fc_expand(z)
#         x = x.view(-1, 64, 2, 2)
        
#         # C. ★ 기존(Standard) FiLM 분기 처리 ★
#         if self.use_film:
#             # snr_val: [Batch, 1]
#             film_params = self.snr_to_film(snr_val)
#             gamma, beta = torch.split(film_params, 64, dim=1)
            
#             # 피처맵의 각 채널별로 스케일 조절 및 이동 적용
#             x = (gamma.view(-1, 64, 1, 1) * x) + beta.view(-1, 64, 1, 1)
        
#         # D. Upsampling (DeepJSCC 역과정)
#         x = self.layer1(x)
#         x = self.layer2(x)
#         x = self.layer3(x)
#         x = self.layer4(x)
#         x = self.layer5(x)
        
#         return x

#new 필름 디코더
# class FiLMCNNSemanticDecoder(nn.Module):
#     def __init__(self, args, compressed_dim=256, output_channels=64):
#         super(FiLMCNNSemanticDecoder, self).__init__()
#         self.compressed_dim = compressed_dim
#         self.use_film = 'w_o_film' not in args.algorithm
    
#         # 1. Vector to Feature Map
#         self.fc_expand = nn.Linear(self.compressed_dim, 64 * 2 * 2)
        
#         # 2. ★ 기존(Standard) FiLM Generator ★
#         if self.use_film:
#             self.snr_to_film = nn.Sequential(
#                 nn.Linear(1, 32),
#                 nn.ReLU(),
#                 nn.Linear(32, 64 * 2) # Gamma(64개) + Beta(64개)
#             )
#             # Identity 초기화 (아주 훌륭한 접근입니다!)
#             self.snr_to_film[-1].weight.data.fill_(0)
#             self.snr_to_film[-1].bias.data[:64].fill_(1)  
#             self.snr_to_film[-1].bias.data[64:].fill_(0)  

#         # 3. DeepJSCC Transpose Backbone
#         self.layer1 = nn.Sequential(nn.ConvTranspose2d(64, 64, 5, stride=1, padding=2), nn.PReLU())
#         self.layer2 = nn.Sequential(nn.ConvTranspose2d(64, 32, 5, stride=1, padding=2), nn.PReLU())
#         self.layer3 = nn.Sequential(nn.ConvTranspose2d(32, 32, 5, stride=1, padding=2), nn.PReLU())
#         self.layer4 = nn.Sequential(nn.ConvTranspose2d(32, 16, 5, stride=2, padding=2, output_padding=1), nn.PReLU())
#         self.layer5 = nn.Sequential(nn.ConvTranspose2d(16, output_channels, 5, stride=2, padding=2, output_padding=1))

#     # forward 함수에 인자 추가: indices (실제 가변 전송 시 위치 복원을 위함)
#     def forward(self, z, snr_val, indices=None):
#         # A. Zero Padding (가변 전송 복원 - Alignment 문제 해결)
#         curr_dim = z.size(1)
        
#         # 만약 실제 통신 환경처럼 차원이 깎여서 들어왔다면?
#         if curr_dim < self.compressed_dim:
#             if indices is None:
#                 raise ValueError("압축된 텐서를 복원하려면 원래 피처의 'indices(위치 정보)'가 필요합니다!")
            
#             # 256차원의 빈(Zero) 도화지를 만듦
#             restored_z = torch.zeros(z.size(0), self.compressed_dim, device=z.device)
#             # 수신된 값을 원래 인덱스 위치에 정확히 꽂아넣음 (Scatter)
#             restored_z.scatter_(1, indices, z)
#             z = restored_z
            
#         # (참고) 파이토치 학습 시에는 인코더에서 256차원이 그대로 넘어오므로 위 if문을 타지 않습니다.

#         # B. Map to Feature Space
#         x = self.fc_expand(z)
#         x = x.view(-1, 64, 2, 2)
        
#         # C. ★ 기존(Standard) FiLM 분기 처리 ★
#         if self.use_film:
#             film_params = self.snr_to_film(snr_val)
#             gamma, beta = torch.split(film_params, 64, dim=1)
#             x = (gamma.view(-1, 64, 1, 1) * x) + beta.view(-1, 64, 1, 1)
        
#         # D. Upsampling
#         x = self.layer1(x)
#         x = self.layer2(x)
#         x = self.layer3(x)
#         x = self.layer4(x)
#         x = self.layer5(x)
        
#         return x

class FiLMCNNSemanticDecoder(nn.Module):
    def __init__(self, args, compressed_dim=4096, output_channels=64):
        super(FiLMCNNSemanticDecoder, self).__init__()
        self.compressed_dim = compressed_dim # 4096
        self.use_film = 'w_o_film' not in args.algorithm
        self.use_semantic_spreading = bool(args.semantic_spreading_enable)
        self.use_server_feature_impute = bool(getattr(args, 'server_feature_impute_enable', 0))
        
        if self.use_film:
            self.snr_to_film = nn.Sequential(
                nn.Linear(1, 32),
                nn.ReLU(),
                nn.Linear(32, 64 * 2) # 채널(64) 단위 Modulation
            )
            self.snr_to_film[-1].weight.data.fill_(0)
            self.snr_to_film[-1].bias.data[:64].fill_(1)  
            self.snr_to_film[-1].bias.data[64:].fill_(0)  

        self.layer1 = nn.Sequential(nn.ConvTranspose2d(64, 64, 5, stride=1, padding=2), nn.PReLU())
        self.layer2 = nn.Sequential(nn.ConvTranspose2d(64, 32, 5, stride=1, padding=2), nn.PReLU())
        self.layer3 = nn.Sequential(nn.ConvTranspose2d(32, 32, 5, stride=1, padding=2), nn.PReLU())
        self.layer4 = nn.Sequential(nn.ConvTranspose2d(32, 16, 5, stride=1, padding=2), nn.PReLU())
        self.layer5 = nn.Sequential(nn.ConvTranspose2d(16, output_channels, 5, stride=1, padding=2))
        if self.use_server_feature_impute:
            self.feature_imputer = nn.Sequential(
                nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
                nn.PReLU(),
                nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            )

    # ★ indices 인자 추가 및 복원 로직 구현
    def forward(self, z, snr_val, indices=None):
        batch_size = z.size(0)

        # A. 가변 압축 복원 및 선택 좌표 inverse spreading
        if indices is not None:
            resorted_z = torch.zeros(batch_size, self.compressed_dim, device=z.device, dtype=z.dtype)

            if isinstance(indices, list):
                items_per_client = batch_size // len(indices)

                for i, idx_per_client in enumerate(indices):
                    start_idx = i * items_per_client
                    end_idx = (i + 1) * items_per_client
                    target_indices = idx_per_client.unsqueeze(0).expand(items_per_client, -1)

                    if z.size(1) < self.compressed_dim:
                        active_z = z[start_idx:end_idx]
                    else:
                        active_z = torch.index_select(z[start_idx:end_idx], 1, idx_per_client)

                    if self.use_semantic_spreading and active_z.size(1) > 0:
                        active_z = invert_semantic_spreading(active_z)

                    resorted_z[start_idx:end_idx].scatter_(1, target_indices, active_z)
                z = resorted_z
            else:
                expanded_indices = indices.unsqueeze(0).expand(batch_size, -1)

                if z.size(1) < self.compressed_dim:
                    active_z = z
                else:
                    active_z = torch.index_select(z, 1, indices)

                if self.use_semantic_spreading and active_z.size(1) > 0:
                    active_z = invert_semantic_spreading(active_z)

                resorted_z.scatter_(1, expanded_indices, active_z)
                z = resorted_z

        # B. 벡터를 피처맵으로 변환 및 FiLM 적용 (기존과 동일)
        x = z.view(-1, 64, 8, 8) 
        
        # C. 디코더측 FiLM 복원
        if self.use_film:
            film_params = self.snr_to_film(snr_val)
            gamma, beta = torch.split(film_params, 64, dim=1)
            x = (gamma.view(-1, 64, 1, 1) * x) + beta.view(-1, 64, 1, 1)

        if self.use_server_feature_impute:
            x = x + self.feature_imputer(x)
        
        # D. 업샘플링 (8x8 크기 유지)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.layer5(x)
        
        return x


# ==============================================================================
# 1. 순수 VIB 기반 시맨틱 인코더 (클라이언트용) - FiLM 완전 제거
# ==============================================================================
class VIBEncoder(nn.Module):
    def __init__(self, args, input_channels=64, compressed_dim=256):
        """
        Input:[Batch, 64, 8, 8] (ResNet Layer1 output)
        Output: z [Batch, compressed_dim]
        """
        super(VIBEncoder, self).__init__()
        
        # Ablation Flag 설정
        self.use_vib = 'w_o_vib' not in args.algorithm

        
        # 1. DeepJSCC Backbone
        self.layer1 = nn.Sequential(nn.Conv2d(input_channels, 16, 5, stride=2, padding=2), nn.PReLU())
        self.layer2 = nn.Sequential(nn.Conv2d(16, 32, 5, stride=2, padding=2), nn.PReLU())
        self.layer3 = nn.Sequential(nn.Conv2d(32, 32, 5, stride=1, padding=2), nn.PReLU())
        self.layer4 = nn.Sequential(nn.Conv2d(32, 32, 5, stride=1, padding=2), nn.PReLU())
        
        # 2. Layer 5
        self.layer5_conv = nn.Conv2d(32, 64, 5, stride=1, padding=2)
        self.layer5_bn = nn.BatchNorm2d(64)
        self.layer5_prelu = nn.PReLU()
        
        # =======================================================
        # 3. ★ 순수 VIB Heads 경량화 (Shared Base 구조) ★
        # =======================================================
        self.flatten_dim = 64 * 2 * 2 # 256
        
        # 공통 특징 추출 레이어 (Shared Feature Extractor)
        self.fc_shared = nn.Sequential(
            nn.Linear(self.flatten_dim, compressed_dim),
            nn.PReLU()
        )
        
        # 평균(μ) 예측
        self.fc_mu = nn.Linear(compressed_dim, compressed_dim)
        
        if self.use_vib:
            # 분산(σ^2) 예측 - VIB가 켜져 있을 때만 사용
            self.fc_var = nn.Linear(compressed_dim, compressed_dim)
            nn.init.constant_(self.fc_var.bias, -5.0) # VIB Collapse 방지용 초기화

    def reparameterize(self, mu, log_var):
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        return mu + eps * std

    def forward(self, x, snr_val=None):
        # A. Feature Extraction
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.layer5_conv(x)
        x = self.layer5_bn(x)
        x = self.layer5_prelu(x)
        
        # B. VIB 로직 (FiLM 과정 없이 바로 평탄화)
        x_flat = x.flatten(1)
        
        # 공통 특징 추출
        shared_feat = self.fc_shared(x_flat)
        
        # 평균 계산
        mu = self.fc_mu(shared_feat)
        
        if self.use_vib:
            # 분산 계산 및 샘플링 (확률적 정규화)
            log_var = self.fc_var(shared_feat)
            log_var_full = torch.clamp(log_var, min=-10.0, max=10.0) 
            z = self.reparameterize(mu, log_var_full) if self.training else mu
            return z, mu, log_var_full
        else:
            # VIB가 없을 때 (결정론적 인코더)
            z = mu
            dummy_log_var = torch.zeros_like(mu)
            return z, mu, dummy_log_var


# ==============================================================================
# 2. 순수 CNN 시맨틱 디코더 (서버용) - FiLM 완전 제거
# ==============================================================================
class VIBDecoder(nn.Module):
    def __init__(self, args, compressed_dim=256, output_channels=64):
        super(VIBDecoder, self).__init__()
        self.compressed_dim = compressed_dim
        
        # 1. Vector to Feature Map
        self.fc_expand = nn.Linear(self.compressed_dim, 64 * 2 * 2)

        # 2. DeepJSCC Transpose Backbone
        self.layer1 = nn.Sequential(nn.ConvTranspose2d(64, 64, 5, stride=1, padding=2), nn.PReLU())
        self.layer2 = nn.Sequential(nn.ConvTranspose2d(64, 32, 5, stride=1, padding=2), nn.PReLU())
        self.layer3 = nn.Sequential(nn.ConvTranspose2d(32, 32, 5, stride=1, padding=2), nn.PReLU())
        self.layer4 = nn.Sequential(nn.ConvTranspose2d(32, 16, 5, stride=2, padding=2, output_padding=1), nn.PReLU())
        self.layer5 = nn.Sequential(nn.ConvTranspose2d(16, output_channels, 5, stride=2, padding=2, output_padding=1))

    def forward(self, z, snr_val=None):
        # A. Zero Padding (VIB 유무 상관없이 구조적 안정성을 위해 유지)
        curr_dim = z.size(1)
        if curr_dim < self.compressed_dim:
            padding = torch.zeros(z.size(0), self.compressed_dim - curr_dim, device=z.device)
            z = torch.cat([z, padding], dim=1)
            
        # B. Map to Feature Space
        x = self.fc_expand(z)
        x = x.view(-1, 64, 2, 2)
        
        # C. Upsampling (FiLM 과정 없이 바로 역합성곱 진행)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.layer5(x)
        
        return x    



# ==============================================================================
# 4. client model
# ==============================================================================
class ClientResNet18v1(nn.Module):
    def __init__(self, args):
        super(ClientResNet18v1, self).__init__()
        base_model = models.resnet18(weights=None)
        
        if args.dataset == 'mnist' or args.dataset == 'fashion-mnist':
            in_channels = 1
        else:
            in_channels = 3
        
        self.conv1 = nn.Conv2d(in_channels, 64, kernel_size=3, stride=2, padding=1, bias=False)
        self.bn1 = base_model.bn1
        self.relu = base_model.relu
        
        # MaxPool 유지 (16x16 -> 8x8)
        self.maxpool = base_model.maxpool 
        
        self.layer1 = base_model.layer1
        
        # Features 정의
        self.features = nn.Sequential(
            self.conv1, 
            self.bn1, 
            self.relu,
            self.maxpool,
            self.layer1
        )

    def forward(self, x, snr_val=None, active_dim=None):
        # x: [Batch, 3, 32, 32]
        # snr_val: [Batch, 1] (0~1 Normalized SNR)
        
        x = self.features(x)
        
        return x
#기존 모델
class ClientResNet18v2(nn.Module):
    def __init__(self, args):
        super(ClientResNet18v2, self).__init__()
        base_model = models.resnet18(weights=None)
        
        # ★ [수정] stride를 1에서 2로 변경
        # 32x32 -> (stride 2) -> 16x16 -> (MaxPool stride 2) -> 8x8
        
        if args.dataset == 'mnist' or args.dataset == 'fashion-mnist':
            in_channels = 1
        else:
            in_channels = 3
        
        self.conv1 = nn.Conv2d(in_channels, 64, kernel_size=3, stride=2, padding=1, bias=False)
        self.bn1 = base_model.bn1
        self.relu = base_model.relu
        
        # MaxPool 유지 (16x16 -> 8x8)
        self.maxpool = base_model.maxpool 
        
        self.layer1 = base_model.layer1
        
        # Features 정의
        self.features = nn.Sequential(
            self.conv1, 
            self.bn1, 
            self.relu,
            self.maxpool,
            self.layer1
        )
        
        self.semantic = args.semantic_enable
        
        if self.semantic == 1:
            if args.algorithm == 'SC-USFL' or args.algorithm == 'SC-USFL_SCM' :
                # SC-USFL Encoder (8x8 입력을 기대함)
                self.semantic_encoder = SC_USFL_Encoder(
                    input_channels=64,
                    max_compressed_dim=1352
                )
            elif args.algorithm == 'SSFLv5' or args.algorithm == 'SSFLv5_w_o_vib' or args.algorithm == 'SSFLv5_w_o_beta' :
                self.semantic_encoder = VIBEncoder(
                    args,
                    input_channels=64, 
                    compressed_dim=args.compressed_dim
                )
            elif args.algorithm == 'SSFLv4' or args.algorithm == 'SSFLv6' or args.algorithm == 'SSFLv6_w_o_vib' or args.algorithm == 'SSFLv6_w_o_vib_fair' or args.algorithm == 'SSFLv6_w_o_film' or args.algorithm == 'SSFLv6_w_o_beta':
                # SSFL Encoder (8x8 입력을 기대함)
                self.semantic_encoder = FiLMChannelAwareEncoder(
                    args,
                    input_channels=64, 
                    compressed_dim=args.compressed_dim
                )
                

    def forward(self, x, snr_val=None, active_dim=None):
        # x: [Batch, 3, 32, 32]
        # snr_val: [Batch, 1] (0~1 Normalized SNR)
        
        x = self.features(x)
        
        if self.semantic == 1:
            # 현재 사용 중인 인코더가 무엇인지 확인
            encoder_type = type(self.semantic_encoder).__name__
            
            if 'SC_USFL_Encoder' in encoder_type:
                # SC-USFL: SNR 안 받음, active_dim만 받음
                # (주의: forward 정의가 forward(x, active_dim=None) 인지 확인)
                z = self.semantic_encoder(x, active_dim=active_dim)
                # SC-USFL은 z만 리턴함 (VIB 아님)
                return z
            elif 'VIBEncoder' in encoder_type:
                # SSFL: SNR 필수, active_dim 선택
                # (주의: forward 정의가 forward(x, snr_val, active_dim=None) 인지 확인)
                z, mu, log_var = self.semantic_encoder(x, snr_val)
            
                return z, mu, log_var                
            elif 'FiLMChannelAwareEncoder' in encoder_type:
                # SSFL: SNR 필수, active_dim 선택
                # (주의: forward 정의가 forward(x, snr_val, active_dim=None) 인지 확인)
                z, mu, log_var, index = self.semantic_encoder(x, snr_val)
                return z, mu, log_var, index
            
        else: 
            # Semantic SFL이 아닌 경우 (기존 SFL)
            return x
        
# ==============================================================================
# 5. server model
# ==============================================================================
class ServerResNet18(nn.Module):
    def __init__(self,args):
        self.num_classes=args.n_class
        super(ServerResNet18, self).__init__()
        base_model = models.resnet18(weights=None)
        self.semantic = args.semantic_enable

        # ★ CNN 기반 디코더로 교체        
        if self.semantic == 1:
            if args.algorithm == 'SC-USFL' or args.algorithm == 'SC-USFL_SCM' :
                # ★ 수정됨: ChannelAwareEncoder 사용
                self.semantic_decoder = SC_USFL_Decoder(output_channels=64, compressed_dim=args.compressed_dim)

        
        self.layers = nn.Sequential(
            base_model.layer2, base_model.layer3, 
            base_model.layer4, base_model.avgpool
        )
        self.fc = nn.Linear(512, self.num_classes)

    def forward(self, x, snr_val=None):
        if self.semantic == 1 : 
            x = self.semantic_decoder(x) # -> [Batch, 64, 8, 8] 복원
            x = self.layers(x)
            x = torch.flatten(x, 1)
            x = self.fc(x)
            return x
        else : 
            x = self.layers(x)
            x = torch.flatten(x, 1)
            x = self.fc(x)
            return x

class ServerResNet18v2(nn.Module):
    def __init__(self, args):
        super(ServerResNet18v2, self).__init__()
        self.num_classes=args.n_class

        base_model = models.resnet18(weights=None)
        self.semantic = args.semantic_enable

        # 디코더 설정
        if args.algorithm in ['SSFLv5', 'SSFLv5_w_o_vib', 'SSFLv5_w_o_beta']:
            self.semantic_decoder = VIBDecoder(args, output_channels=64, compressed_dim=args.compressed_dim)
        else:
            self.semantic_decoder = FiLMCNNSemanticDecoder(args, output_channels=64, compressed_dim=args.compressed_dim)
        
        self.layers = nn.Sequential(
            base_model.layer2, base_model.layer3, 
            base_model.layer4, base_model.avgpool
        )
        self.fc = nn.Linear(512, self.num_classes)

    # ★ indices 매개변수를 디코더에 전달하도록 수정
    def forward(self, x, snr_val=None, indices=None):
        if self.semantic == 1: 
            # 디코더 호출 시 indices 전달
            x = self.semantic_decoder(x, snr_val, indices=indices) 
            x = self.layers(x)
            x = torch.flatten(x, 1)
            x = self.fc(x)
            return x
        else: 
            x = self.layers(x)
            x = torch.flatten(x, 1)
            x = self.fc(x)
            return x

# ==============================================================================
# 1. SCM Pre-training용 통합 모델 (Client + Server 연결)
# ==============================================================================
class SCM_Pretraining_Model(nn.Module):
    def __init__(self, client_head, semantic_encoder, semantic_decoder, server_body, server_tail):
        super(SCM_Pretraining_Model, self).__init__()
        self.head = client_head         # ResNet Front (Client)
        self.encoder = semantic_encoder # SCM Encoder (Client)
        self.decoder = semantic_decoder # SCM Decoder (Server Side)
        self.body = server_body         # ResNet Back + Classifier (Server)
        self.tail = server_tail
        
        # 19dB 환경을 위한 고정 채널 (학습용)
        # SNR 19dB -> Noise Power approx 0.012 -> Std approx 0.11
        self.fixed_snr_db = 19.0 

    def forward(self, x, input_snr):
        # 1. Head (Feature Extraction)
        # 원본 특징 (Original Features) -> 나중에 MSE Loss 계산용
        original_features = self.head(x) 
        
        # 2. Semantic Encoder (압축)
        # SNR 19dB 정보를 줘서 인코딩 (Pre-training은 깨끗한 환경 기준)
        snr_tensor = torch.tensor([[1.0]] * x.size(0)).to(x.device) # 1.0 = Normalized Max SNR
        z, mu, log_var = self.encoder(original_features, snr_tensor)
        
        # 3. Channel Simulation (19dB Fixed)
        # SCM 학습 시에는 노이즈를 고정해서 안정적으로 학습
        # Power Normalization
        signal_power = torch.mean(z ** 2)
        if signal_power > 0:
            z = z / torch.sqrt(signal_power)
            
        noise_std = 10 ** (-input_snr / 20.0)
        noise = torch.randn_like(z) * noise_std
        received_z = z + noise
        
        # 4. Semantic Decoder (복원)
        reconstructed_features = self.decoder(received_z)
        
        # 5. Body & Tail (Classification)
        # ResNet 뒷단은 보통 features 입력을 기대하므로 shape 확인 필요
        logits = self.body(reconstructed_features)
        logits = torch.flatten(logits, 1)
        logits = self.tail(logits)
        
        return logits, original_features, reconstructed_features, mu, log_var

# ==============================================================================
# 2. SCM Loss Function (MSE + CE + Perceptual-like)
# ==============================================================================
class SCMLoss(nn.Module):
    def __init__(self, lambda_task=4.0, lambda_recon=4.0, lambda_semantic=2.0):
        super(SCMLoss, self).__init__()
        self.lambda_task = lambda_task
        self.lambda_recon = lambda_recon
        self.lambda_semantic = lambda_semantic
        
        self.ce_loss = nn.CrossEntropyLoss()
        self.mse_loss = nn.MSELoss()

    def forward(self, logits, labels, orig_feat, recon_feat):
        # 1. Task Loss (Cross Entropy) - 분류 정확도
        loss_task = self.ce_loss(logits, labels)
        
        # 2. Reconstruction Loss (MSE) - 특징값 자체의 복원력
        loss_recon = self.mse_loss(recon_feat, orig_feat)
        
        # 3. Semantic (Perceptual-like) Loss - 특징의 '방향(의미)' 일치도
        # Perceptual Loss는 원래 이미지를 VGG에 넣어 비교하지만, 
        # 여기서는 Feature Map 간의 Cosine Similarity를 사용하여 의미적 유사성을 측정합니다.
        # (1 - CosineSim)을 최소화
        orig_flat = orig_feat.view(orig_feat.size(0), -1)
        recon_flat = recon_feat.view(recon_feat.size(0), -1)
        loss_semantic = 1.0 - F.cosine_similarity(orig_flat, recon_flat).mean()

        # Total Loss
        total_loss = (self.lambda_task * loss_task) + \
                     (self.lambda_recon * loss_recon) + \
                     (self.lambda_semantic * loss_semantic)
                     
        return total_loss, loss_task, loss_recon

class GlobalNetworkStatusMonitor:
    def __init__(self, num_clients, b_max_mhz=50.0, p_max_w=0.1):
        """
        수치적 안정성을 위해 모든 단위는 정규화됨:
        Bandwidth: MHz / Power: W / Data: Mbits / Rate: Mbps
        """
        self.I = num_clients
        self.B_max = b_max_mhz      # 50.0 (MHz)
        self.P_max = p_max_w        # 0.1 (W)
        
        self.candidate_dims = [328, 492, 696, 1352] 
        self.C = np.full(self.I, 0.1) # 로컬/서버 연산 지연시간(초)

    def calculate_R(self, B, P, alpha):
        """ 통신 속도 (Mbps) """
        B = max(B, 1e-3) # 최소 대역폭 1kHz 보장
        return B * np.log2(1 + (alpha * P) / B)

    def calculate_gradients(self, B, P, alpha):
        """ 테일러 전개 기울기 """
        B = max(B, 1e-3)
        ln2 = np.log(2)
        term = B + alpha * P
        
        grad_B = np.log2(1 + (alpha * P) / B) - (alpha * P) / (ln2 * term)
        grad_P = (alpha * B) / (ln2 * term)
        
        return grad_B, grad_P

    def optimize_resources(self, snr_db_list, max_bcd_iters=3, max_sca_iters=3):
        """
        수치적으로 안정화된 BCD & SCA 알고리즘
        """
        # B_avg = self.B_max / self.I
        
        # # [핵심] N0 연산을 피하기 위해 SNR -> alpha로 통합 매핑
        # # SNR_linear = (alpha * P) / B 이므로, alpha = SNR_linear * B_avg / P_max
        # alpha_list = [ (10**(snr/10.0)) * B_avg / self.P_max for snr in snr_db_list ]
        
        # B_val = np.full(self.I, B_avg)
        # P_val = np.full(self.I, self.P_max)
        current_dims = np.full(self.I, self.candidate_dims[2])
        
        # T_opt = float('inf')

        # for bcd_iter in range(max_bcd_iters):
            
        #     # --- Continuous Variable Optimization (SCA) ---
        #     for sca_iter in range(max_sca_iters):
        #         B = cp.Variable(self.I)
        #         P = cp.Variable(self.I)
        #         T = cp.Variable(nonneg=True)
                
        #         constraints = [
        #             cp.sum(B) <= self.B_max,
        #             P <= self.P_max,
        #             B >= 1e-3, # 0.001 MHz (1kHz) 하한선
        #             P >= 1e-4  # 0.1 mW 하한선
        #         ]
                
        #         for i in range(self.I):
        #             alpha = alpha_list[i]
        #             D_i_mbits = (current_dims[i] * 32) / 1e6  # 데이터 크기를 Mbits로 변환!
                    
        #             g_val = self.calculate_R(B_val[i], P_val[i], alpha)
        #             grad_B, grad_P = self.calculate_gradients(B_val[i], P_val[i], alpha)
                    
        #             # 선형 근사 (Mbps)
        #             hat_g = g_val + grad_B * (B[i] - B_val[i]) + grad_P * (P[i] - P_val[i])
                    
        #             constraints.append(hat_g >= 1e-3) # 속도가 음수가 되는 것 방지
                    
        #             # 지연시간 제약 (초 단위로 딱 떨어짐)
        #             total_latency = self.C[i] + D_i_mbits * cp.inv_pos(hat_g)
        #             constraints.append(total_latency <= T)
                
        #         prob = cp.Problem(cp.Minimize(T), constraints)
                
        #         try:
        #             # SCS보다 분수 함수(inv_pos)에 훨씬 안정적인 ECOS 솔버 사용
        #             prob.solve(solver=cp.ECOS) 
        #         except Exception:
        #             # ECOS 실패 시 SCS로 Fallback
        #             try:
        #                 prob.solve(solver=cp.SCS)
        #             except Exception:
        #                 break # 솔버 둘 다 터지면 현재 값 유지
                
        #         if prob.status not in ["infeasible", "unbounded"] and B[0].value is not None:
        #             B_val = np.array([b.value for b in B])
        #             P_val = np.array([p.value for p in P])
            
        # --- Discrete Variable Optimization (차원 결정) ---
        max_latency_current_round = 0
        
        for i in range(self.I):
            snr = snr_db_list[i] # 현재 클라이언트의 실제 SNR (dB)
            
            # ★ [수정] 상대 평가(등수)가 아닌 절대 평가(SNR 구간)로 매핑
            # (테스트 환경인 -5dB ~ 15dB에 맞춰 구간 설정)
            if snr < 0.0:
                # 통신 매우 불량 (-5dB ~ 0dB)
                best_dim = self.candidate_dims[0] # 328
            elif snr < 5.0:
                # 통신 약간 불량 (0dB ~ 5dB)
                best_dim = self.candidate_dims[1] # 492
            elif snr < 10.0:
                # 통신 양호 (5dB ~ 10dB)
                best_dim = self.candidate_dims[2] # 696
            else:
                # 통신 매우 우수 (10dB 이상)
                best_dim = self.candidate_dims[3] # 1352
            
            current_dims[i] = best_dim

        return current_dims.astype(int)
    
# ==============================================================================
# 5. Standard FL Model (Client holds Full Model)
# ==============================================================================
class ResNet18_FL(nn.Module):
    def __init__(self, args, num_classes=10):
        super(ResNet18_FL, self).__init__()
        base_model = models.resnet18(weights=None)
        
        # ★ SFL과 동일한 조건: CIFAR-10용 앞단 수정
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=2, padding=1, bias=False)
        self.bn1 = base_model.bn1
        self.relu = base_model.relu
        # self.maxpool 제거
        
        self.layer1 = base_model.layer1
        self.layer2 = base_model.layer2
        self.layer3 = base_model.layer3
        self.layer4 = base_model.layer4
        
        self.avgpool = base_model.avgpool
        self.fc = nn.Linear(512, num_classes)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        # No MaxPool
        
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        return x
