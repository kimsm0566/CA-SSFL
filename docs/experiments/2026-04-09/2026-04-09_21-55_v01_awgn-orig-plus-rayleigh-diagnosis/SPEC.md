# 실험 스펙

## 메타데이터

- 실험 id: `2026-04-09_21-55_v01_awgn-orig-plus-rayleigh-diagnosis`
- 상태: `active`

## 실행 매트릭스

### AWGN 실행

- `CA-SSFL Orig`, seed `1,2,3,4`

### Rayleigh 분석

- `CA-SSFL Orig`, seed `1,2,3,4`
- `CA-SSFL New`, seed `1,2,3,4`

## 공통 고정 조건

- dataset: `cifar10`
- partition_type: `class`
- n_clients: `8`
- n_client_data: `3000`
- batch_size: `100`
- n_epochs: `1`
- n_rounds: `200`

## 알고리즘 정의

- `CA-SSFL Orig`
  - `algorithm=SSFLv6`
  - `beta=0.01`
  - `pruning_threshold=1.0`
  - `film_max_t=0.7`
  - `film_min_t=0.4`
  - `semantic_spreading_enable=0`
  - `snr_adaptive_beta_enable=0`
  - `semantic_power_enable=0`
- `CA-SSFL New`
  - 위와 동일하되
  - `semantic_spreading_enable=1`
  - `snr_adaptive_beta_enable=1`

## 분석 지표

- final accuracy mean/std
- total communication mean/std
- `-6 dB`, `12 dB` accuracy
- round-wise mean accuracy gap
- round-wise mean communication gap

## 검증

- Python 변경 시 `python3 -m py_compile`
- 실행은 Docker GPU 경로
