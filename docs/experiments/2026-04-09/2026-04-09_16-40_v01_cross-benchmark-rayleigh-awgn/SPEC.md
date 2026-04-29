# 실험 스펙

## 메타데이터

- 실험 id: `2026-04-09_16-40_v01_cross-benchmark-rayleigh-awgn`
- 상태: `완료`

## 실행 매트릭스

### Rayleigh

- `SFL`, seed `1,2,3,4`
- `SC-USFL`, seed `1,2,3,4`
- `SSFLv6 baseline`, seed `1,2,3,4`
- `SSFLv6 candidate`, seed `1,2,3,4`

### AWGN

- `SFL`, seed `1,2,3,4`
- `SC-USFL`, seed `1,2,3,4`

## 공통 고정 조건

- dataset: `cifar10`
- partition_type: `class`
- n_clients: `9`
- n_client_data: `3000`
- batch_size: `100`
- n_epochs: `1`
- n_rounds: `200`
- result_path: `/workspace/tmp/2026-04-09-cross-benchmark`

## 주요 비교

- Rayleigh:
  - `SFL` vs `SC-USFL` vs `SSFLv6 baseline` vs `SSFLv6 candidate`
- AWGN:
  - `SFL` vs `SC-USFL`

## 지표

- final accuracy
- cumulative communication cost
- multi-SNR accuracy
- seed mean/std
