# CIFAR-100 교차 벤치마크 실행 스펙 (업데이트된 CA-SSFL 대표 설정)

## 목적

`cifar100`에서 최신 대표 설정을 반영한 `CA-SSFL`를 `SFL`, `SC-USFL`와 동일 조건으로 다시 비교한다.

## 비교 대상

- `SFL`
- `SC-USFL`
- `CA-SSFL`

## CA-SSFL 고정 설정

- `algorithm=SSFLv6`
- `beta=0.010`
- `pruning_threshold=1.0`
- `film_max_t=0.7`
- `film_min_t=0.2`
- `compressed_dim=4096`
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
- `train_snr=10`
- seeds: `1,2,3,4`

## 채널

- `AWGN`
- `Rayleigh`

## 실행 매트릭스

각 채널에 대해 아래 3-way benchmark를 실행한다.

- `SFL`
- `SC-USFL`
- `CA-SSFL`

즉 총 실행 수는:

- `2 channels x 3 methods x 4 seeds = 24 runs`

## 결과 루트

- AWGN:
  - `/workspace/tmp/2026-04-14/2026-04-14-cifar100-awgn-threeway-benchmark-updated-ca-ssfl`
- Rayleigh:
  - `/workspace/tmp/2026-04-14/2026-04-14-cifar100-rayleigh-threeway-benchmark-updated-ca-ssfl`

호스트 기준 경로:

- AWGN:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-14/2026-04-14-cifar100-awgn-threeway-benchmark-updated-ca-ssfl`
- Rayleigh:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-14/2026-04-14-cifar100-rayleigh-threeway-benchmark-updated-ca-ssfl`

## 검증

실행 전:

- 러너 `bash -n`
- 필요시 최소 smoke

실행 후:

- `24`개 `seed_*.npz` 존재 확인
- `RESULT.md`에 평균/표준편차 정리
- 필요 시 `SNR vs Accuracy`, `Round vs Accuracy` 그래프 갱신

## 비교 규칙

- `SFL`, `SC-USFL`, `CA-SSFL`는 동일 seed set `1,2,3,4`로 비교한다.
- 정확도만 아니라 통신량도 함께 보고한다.
- 이번 버전은 `2026-04-11`의 구버전 CIFAR100 benchmark를 덮어쓰지 않고 별도 결과로 유지한다.
