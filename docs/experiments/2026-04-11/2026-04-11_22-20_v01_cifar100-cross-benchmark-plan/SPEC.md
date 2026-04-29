# CIFAR-100 교차 벤치마크 스펙

## 목적

`cifar100`에서 `SFL`, `SC-USFL`, `CA-SSFL`의 성능-통신량 관계를 `AWGN`, `Rayleigh` 채널에서 동일 조건으로 재측정한다.

## 고정 조건

- dataset: `cifar100`
- partition: `class`
- `n_clients=8`
- `n_client_data=3000`
- `batch_size=100`
- `n_epochs=1`
- `n_rounds=200`
- `major_percent=0.8`
- `model_type=resnetv2`
- `seed set = {1,2,3,4}`
- `train_snr=10`

## 비교군

### SFL

- `algorithm=SFL`
- `compressed_dim=4096`
- `beta=0.01`
- `pruning_threshold=1.0`
- `film_max_t=0.7`
- `film_min_t=0.4`

### SC-USFL

- `algorithm=SC-USFL`
- `compressed_dim=1352`
- `beta=0.01`
- `pruning_threshold=1.0`
- `film_max_t=0.7`
- `film_min_t=0.4`

### CA-SSFL

- `algorithm=SSFLv6`
- `compressed_dim=4096`
- `beta=0.01`
- `pruning_threshold=1.0`
- `film_max_t=0.7`
- `film_min_t=0.4`
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

## 채널

- `AWGN`
- `Rayleigh`

## 결과 루트

- AWGN:
  - `/workspace/tmp/2026-04-11/2026-04-11-cifar100-awgn-threeway-benchmark-nclients8`
- Rayleigh:
  - `/workspace/tmp/2026-04-11/2026-04-11-cifar100-rayleigh-threeway-benchmark-nclients8`

## 문서 루트

- AWGN:
  - `/home/sunmin/SFL_Semantic/docs/experiments/2026-04-11/2026-04-11_22-20_v01_cifar100-cross-benchmark-plan`
- Rayleigh:
  - 동일 폴더 내 `RUNLOG_AWGN.md`, `RUNLOG_RAYLEIGH.md`

## Smoke

목적:

- `cifar100` 데이터 다운로드/로딩 확인
- `100-class` 설정에서 모델/손실/평가 경로 확인
- Docker GPU canonical runtime 확인

범위:

- `AWGN`: `SFL`, `SC-USFL`, `CA-SSFL` 각 1 round, `seed=1`
- `Rayleigh`: `CA-SSFL` 1 round, `seed=1`

smoke 결과 루트:

- `/workspace/tmp/2026-04-11/2026-04-11-cifar100-smoke`

## 본 실험 순서

1. smoke
2. `AWGN` 3-way, seed `1..4`
3. `Rayleigh` 3-way, seed `1..4`
4. summary 및 그래프 생성

## 검증

- touched script/python 파일 `py_compile` 또는 `bash -n`
- Docker GPU smoke 로그 확인
- 본 실험은 `seed_{1..4}.npz` 생성으로 완료 판단
