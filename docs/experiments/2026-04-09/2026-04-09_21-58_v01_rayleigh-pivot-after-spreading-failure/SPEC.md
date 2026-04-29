# 실험 스펙

## 메타데이터

- 실험 id: `2026-04-09_21-58_v01_rayleigh-pivot-after-spreading-failure`
- 상태: `active`

## 실행 매트릭스

### Baseline Reference

- `CA-SSFL Orig`
  - 기존 완료 결과 재사용
  - source: `2026-04-09-rayleigh-cross-benchmark-nclients8`
  - seeds: `1,2`

### Stage A: Semantic Power Sweep

- `CA-SSFL Orig + semantic_power_enable=1`
- `semantic_power_alpha`:
  - `0.5`
  - `1.0`
  - `2.0`
  - `4.0`
- seeds:
  - `1,2`

## 공통 고정 조건

- dataset: `cifar10`
- partition_type: `class`
- channel_type: `rayleigh`
- n_clients: `8`
- n_client_data: `3000`
- batch_size: `100`
- n_epochs: `1`
- n_rounds: `200`
- model_type: `resnetv2`
- compressed_dim: `4096`
- beta: `0.01`
- pruning_threshold: `1.0`
- film_max_t: `0.7`
- film_min_t: `0.4`
- semantic_spreading_enable: `0`
- snr_adaptive_beta_enable: `0`
- mpi_trace_enable: `0`

## 결과 경로

- exploratory result_path:
  - `/workspace/tmp/2026-04-09-rayleigh-semantic-power-sweep-nclients8`

## 선택 규칙

- exploratory stage에서는 claim-making promotion을 하지 않음
- 우선 관찰 항목:
  - final acc가 baseline 대비 유지/상승하는지
  - `-6 dB`가 baseline 대비 유지/상승하는지
  - total comm가 거의 유지되는지

## 성공 기준

- 8런 완료
- `alpha`별 final acc / `-6 dB` / comm 비교 가능
- 유망한 alpha가 보이면 다음 단계에서 seed `3,4` 확장
