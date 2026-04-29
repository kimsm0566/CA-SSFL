# CIFAR-100 CA-SSFL 채널별 대표 설정 재실험 스펙

## 목적

`cifar100`에서 `CA-SSFL`를 채널별 최신 대표 설정으로 다시 실행해, 기존 `SFL`, `SC-USFL` 결과와 matched comparison을 가능하게 한다.

## 공통 고정 조건

- dataset: `cifar100`
- partition type: `class`
- `n_clients=8`
- `n_client_data=3000`
- `batch_size=100`
- `n_epochs=1`
- `n_rounds=200`
- `major_percent=0.8`
- `model_type=resnetv2`
- `algorithm=SSFLv6`
- `compressed_dim=4096`
- `pruning_threshold=1.0`
- `semantic_spreading=0`
- `snr_adaptive_beta=0`
- `semantic_power=0`
- `latent_mixing=0`
- `encoder_downsample=0`
- `semidense=0`
- `support_floor=0`
- `importance_repetition=0`
- `base_refinement=0`
- `csi_source_mask=0`
- `server_feature_impute=0`
- `train_snr=10`
- seeds: `1,2,3,4`

## 채널별 대표 설정

### AWGN

- `beta=0.05`
- `film_max_t=0.7`
- `film_min_t=0.2`

### Rayleigh

- `beta=0.1`
- `film_max_t=0.7`
- `film_min_t=0.4`

## 실행 매트릭스

- `AWGN`: seeds `1,2,3,4`
- `Rayleigh`: seeds `1,2,3,4`

총 실행 수:

- `8 runs`

## 예상 시간

- run당 약 `8~10분`
- 총 약 `70~100분`

## 시간 추정 전제

- 기존 `cifar100` benchmark와 같은 GPU/Docker 경로 사용
- artifact-first 판정 적용
- queue stall이 없다는 가정

## 결과 루트

- AWGN
  - container: `/workspace/tmp/2026-04-15/2026-04-15-cifar100-awgn-ca-ssfl-channel-specific-rerun`
  - host: `/home/sunmin/SFL_Semantic/tmp/2026-04-15/2026-04-15-cifar100-awgn-ca-ssfl-channel-specific-rerun`
- Rayleigh
  - container: `/workspace/tmp/2026-04-15/2026-04-15-cifar100-rayleigh-ca-ssfl-channel-specific-rerun`
  - host: `/home/sunmin/SFL_Semantic/tmp/2026-04-15/2026-04-15-cifar100-rayleigh-ca-ssfl-channel-specific-rerun`

## 검증

실행 전:

- 러너 `bash -n`

실행 후:

- `AWGN 4개 + Rayleigh 4개 = 8개` `seed_*.npz` 확인
- 기존 `SFL`, `SC-USFL`와 결합 가능한지 확인
- 후속 그래프 생성

## 비교 규칙

- `SFL`, `SC-USFL`는 기존 `cifar100` benchmark 결과를 재사용한다.
- 새로 생성하는 것은 `CA-SSFL`만이다.
- 이후 비교는 반드시 같은 seed set `1,2,3,4` 기준으로 집계한다.

