# 실험 스펙

## 메타데이터

- 실험 id: `2026-04-10_01-17_v01_rayleigh-latent-mixing-pilot`
- 상태: `active`

## 실행 매트릭스

- `SSFLv6 + latent_mixing_strength=0.1`, seed `1,2`
- `SSFLv6 + latent_mixing_strength=0.25`, seed `1,2`
- `SSFLv6 + latent_mixing_strength=0.5`, seed `1,2`

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
- latent_mixing_enable: `1`
- latent_mixing_groups: `8`
- mpi_trace_enable: `0`
- result_path: `/workspace/tmp/2026-04-10-rayleigh-latent-mixing-pilot`

## 비교 기준

- baseline artifact root:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-09-rayleigh-cross-benchmark-nclients8`
- baseline config:
  - `SSFLv6`
  - `semantic_spreading=0`
  - `snr_adaptive_beta=0`
  - `semantic_power=0`
  - `latent_mixing=0`

## 수집 지표

- final accuracy
- cumulative communication cost
- multi-SNR accuracy
- `-6 dB` accuracy
- round-wise accuracy history

## 검증

- `python3 -m py_compile`:
  - `src/run_exp_main.py`
  - `src/utils/option.py`
  - `src/models/model.py`
- Docker GPU smoke:
  - `latent_mixing_strength=0.1`, seed `1`, `n_rounds=1`
