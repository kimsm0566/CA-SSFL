# 실험 스펙

## 메타데이터

- 실험 id: `2026-04-10_11-02_v01_rayleigh-encoder-downsampling-pivot`
- 상태: `active`

## 구현 범위

이번 1차 시도는 **encoder downsampling + lightweight upsample mixing**의 최소 구조 변경만 다룬다.

- 대상 클래스:
  - `FiLMChannelAwareEncoder`
- baseline 유지 요소:
  - `VIB`
  - `FiLM`
  - masking logic
  - communication accounting
  - decoder 구조
- 변경 요소:
  - encoder 내부에 `4x4` bottleneck을 만드는 stride-2 downsampling path 추가
  - `ConvTranspose2d` 기반 lightweight upsample block으로 다시 `8x8`로 복원
  - 이후 기존 `1x1 conv` heads (`conv_mu`, `conv_var`) 유지

## 구체 구조

### Baseline encoder

- backbone 출력 `64 x 8 x 8`
- `1x1 conv` heads (`conv_mu`, `conv_var`)
- flatten -> `4096`

### Candidate encoder_downsample_v1

- 마지막 feature extraction stage 뒤에 `stride=2` downsampling conv 추가
- feature map을 `64 x 4 x 4`로 축소
- `ConvTranspose2d` 기반 upsample block으로 `64 x 8 x 8`로 복원
- `mu`, `log_var`는 복원된 `8x8` feature 위의 기존 `1x1 conv` head로 생성

### 설계 의도

- spatial mixing을 강제
- 최종 latent 차원과 masking 프레임은 유지
- 거대한 FC head를 피해서 model comm와 GPU 메모리 폭증을 막음

## 새 옵션

- `encoder_downsample_enable`
  - `0/1`
- `encoder_downsample_mode`
  - 초기값: `stride2_proj`
- `encoder_downsample_proj_dim`
  - 초기값: `4096`
  - 경로/설정 호환성은 유지하지만, 현재 구현에서는 실질적으로 사용하지 않음

이번 1차 후보에서는 아래 한 조합만 사용한다.

- `encoder_downsample_enable=1`
- `encoder_downsample_mode=stride2_proj`
- `encoder_downsample_proj_dim=4096`

## 실행 매트릭스

### smoke

- `Rayleigh`
- `seed=1`
- `n_rounds=1`
- baseline과 candidate 각각 1회

### exploratory pilot

- `Rayleigh`
- `SSFLv6` (`CA-SSFL Orig` 기반)
- seed `1,2`
- 비교:
  - baseline
  - `encoder_downsample_v1`

## 공통 고정 조건

- dataset: `cifar10`
- partition_type: `class`
- channel_type: `rayleigh`
- n_clients: `8`
- n_client_data: `3000`
- batch_size: `100`
- n_epochs: `1`
- n_rounds: `200`
- algorithm: `SSFLv6`
- model_type: `resnetv2`
- compressed_dim: `4096`
- beta: `0.01`
- pruning_threshold: `1.0`
- film_max_t: `0.7`
- film_min_t: `0.4`
- semantic_spreading_enable: `0`
- snr_adaptive_beta_enable: `0`
- semantic_power_enable: `0`
- latent_mixing_enable: `0`
- semidense_enable: `0`

## 비교 기준

- baseline artifact root:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-09-rayleigh-cross-benchmark-nclients8`
- baseline config:
  - `CA-SSFL Orig`

## 수집 지표

- final accuracy
- cumulative communication cost
- multi-SNR accuracy
- `-6 dB` accuracy
- `12 dB` accuracy
- round-wise accuracy history
- active feature count 로그

## 성공 판정

exploratory pilot에서 다음을 본다.

- final accuracy:
  - baseline 대비 개선 또는 열세 `0.5%p` 이내
- `-6 dB` accuracy:
  - baseline 대비 개선
- communication cost:
  - 증가가 제한적이거나 동급

## 실패 판정

- final accuracy와 `-6 dB`가 모두 baseline보다 낮음
- communication cost만 증가
- 학습이 불안정하거나 decoder mismatch 발생

## 검증

- `python3 -m py_compile`
  - `src/models/model.py`
  - `src/utils/option.py`
  - `src/run_exp_main.py`
- Docker GPU smoke
  - baseline 1-round: 통과
    - `Acc 10.05%`
    - `Total comm 111.08 MB`
  - candidate 1-round: 통과
    - `Acc 10.02%`
    - `Total comm 125.74 MB`

## 실행 순서

1. smoke 통과 확인
2. `Rayleigh seed 1,2` exploratory 실행
3. baseline seed `1,2`와 matched 비교
