# 실험 스펙

## 공통 고정 조건

- dataset: `cifar10`
- partition_type: `class`
- n_clients: `8`
- n_client_data: `3000`
- batch_size: `100`
- n_epochs: `1`
- n_rounds: `200`
- algorithm: `SSFLv6`
- compressed_dim: `4096`
- semantic_spreading_enable: `1`
- snr_adaptive_beta_enable: `1`
- semantic_power_enable: `0`
- semantic_power_alpha: `2.0`
- result_path: `/workspace/tmp/2026-04-09-comm-reduction-followup-nclients8`

## Stage A: Rayleigh sweep

- channel_type: `rayleigh`
- seeds: `1,2`
- sweep grid:
  - `beta=0.1`, `film_max_t=0.7`, `film_min_t=0.4`
  - `beta=0.1`, `film_max_t=0.8`, `film_min_t=0.5`
  - `beta=0.1`, `film_max_t=0.9`, `film_min_t=0.6`
  - `beta=0.01`, `film_max_t=0.7`, `film_min_t=0.4`
  - `beta=0.01`, `film_max_t=0.8`, `film_min_t=0.5`
  - `beta=0.01`, `film_max_t=0.9`, `film_min_t=0.6`
  - `beta=0.001`, `film_max_t=0.7`, `film_min_t=0.4`
  - `beta=0.001`, `film_max_t=0.8`, `film_min_t=0.5`
  - `beta=0.001`, `film_max_t=0.9`, `film_min_t=0.6`
  - `beta=0.0001`, `film_max_t=0.7`, `film_min_t=0.4`
  - `beta=0.0001`, `film_max_t=0.8`, `film_min_t=0.5`
  - `beta=0.0001`, `film_max_t=0.9`, `film_min_t=0.6`
## Stage B: AWGN validation

- channel_type: `awgn`
- seeds: `1,2`
- config:
  - Stage A에서 선택된 best config 1개

## 참조 기준

- current candidate reference:
  - source:
    - `/home/sunmin/SFL_Semantic/tmp/2026-04-09-rayleigh-seq-full/.../semantic_spreading_1/snr_adaptive_beta_1/.../seed_1.npz`
    - `/home/sunmin/SFL_Semantic/tmp/2026-04-09-rayleigh-seq-full/.../semantic_spreading_1/snr_adaptive_beta_1/.../seed_2.npz`
- 비교 지표:
  - final accuracy
  - total communication cost
  - `-6 dB` accuracy
  - `12 dB` accuracy
