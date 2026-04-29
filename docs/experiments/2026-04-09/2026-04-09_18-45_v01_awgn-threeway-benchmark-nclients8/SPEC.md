# 실험 스펙

## 메타데이터

- 실험 id: `2026-04-09_18-45_v01_awgn-threeway-benchmark-nclients8`
- 상태: `active`

## 실행 매트릭스

- `SFL`, seed `1,2,3,4`
- `SC-USFL`, seed `1,2,3,4`
- `SSFLv6 candidate`, seed `1,2,3,4`

## 공통 고정 조건

- dataset: `cifar10`
- partition_type: `class`
- channel_type: `awgn`
- n_clients: `8`
- n_client_data: `3000`
- batch_size: `100`
- n_epochs: `1`
- n_rounds: `200`
- result_path: `/workspace/tmp/2026-04-09-awgn-threeway-benchmark-nclients8`

## 알고리즘별 인자

- `SFL`
  - `algorithm=SFL`
  - `compressed_dim=4096`
- `SC-USFL`
  - `algorithm=SC-USFL`
  - `compressed_dim=1352`
- `SSFLv6 candidate`
  - `algorithm=SSFLv6`
  - `compressed_dim=4096`
  - `beta=0.01`
  - `pruning_threshold=1.0`
  - `film_max_t=0.7`
  - `film_min_t=0.4`
  - `semantic_spreading_enable=1`
  - `snr_adaptive_beta_enable=1`
  - `semantic_power_enable=0`
  - `mpi_trace_enable=0`

## 검증

- 정적 검증:
  - `python3 -m py_compile` on touched Python files
- smoke:
  - Docker GPU에서 `SSFLv6 candidate`, `awgn`, `n_rounds=1`, `seed=1`, `mpi_trace_enable=1`

## 지표

- final accuracy
- cumulative communication cost
- multi-SNR accuracy
- seed mean/std
