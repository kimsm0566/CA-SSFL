# 실험 스펙

## Stage A: 통신량 절감 sweep

- 고정 조건:
  - dataset: `cifar10`
  - partition_type: `class`
  - channel_type: `rayleigh`
  - n_clients: `9`
  - n_client_data: `3000`
  - batch_size: `100`
  - n_epochs: `1`
  - n_rounds: `200`
  - algorithm: `SSFLv6`
  - `semantic_spreading_enable=1`
  - `snr_adaptive_beta_enable=1`
- seed:
  - `1,2`
- sweep grid:
  - `beta=0.0125`, `film_max_t=0.75`, `film_min_t=0.45`
  - `beta=0.0150`, `film_max_t=0.75`, `film_min_t=0.45`
  - `beta=0.0125`, `film_max_t=0.80`, `film_min_t=0.50`
  - `beta=0.0150`, `film_max_t=0.80`, `film_min_t=0.50`

## Stage B: semantic power allocation

- 진입 조건:
  - Stage A best 후보도 `SC-USFL`를 종합적으로 이기지 못할 때
- 고정 조건:
  - Stage A best 설정을 기반
  - `semantic_power_enable=1`
- sweep grid:
  - `semantic_power_alpha=2.0`
  - `semantic_power_alpha=3.0`
- seed:
  - `1,2`

## 산출물 경로

- `/home/sunmin/SFL_Semantic/tmp/2026-04-09-autonomous-followup`
