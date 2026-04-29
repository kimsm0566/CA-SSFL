# Table 1 Block A Seed 3,4 확장 스펙

## 목적

- `Table 1` 왼쪽 블록 `(\beta, \tau_{VIB})`을 `seed 1,2,3,4` 기준으로 통일하기 위한 `seed 3,4` 추가 실행

## 고정 조건

- dataset: `cifar10`
- partition: `class`
- algorithm: `SSFLv6`
- model_type: `resnetv2`
- `n_clients=8`
- `n_client_data=3000`
- `batch_size=100`
- `n_epochs=1`
- `n_rounds=200`
- `compressed_dim=4096`
- `train_snr=10`
- `channel ∈ {awgn, rayleigh}`
- `film_max_t=0.7`
- `film_min_t=0.4`
- `semantic_spreading_enable=0`
- `snr_adaptive_beta_enable=0`
- `semantic_power_enable=0`
- `latent_mixing_enable=0`
- `encoder_downsample_enable=0`
- `semidense_enable=0`
- `support_floor_enable=0`
- `importance_repetition_enable=0`
- `base_refinement_enable=0`
- `csi_source_mask_enable=0`
- `server_feature_impute_enable=0`
- `mpi_trace_enable=0`

## 탐색 축

- `beta ∈ {0.100, 0.050, 0.010, 0.005, 0.001}`
- `pruning_threshold ∈ {1.5, 1.0, 0.5}`
- `seed ∈ {3,4}`

## 실행 수

- 총 `60 runs`

## 예상 시간

- run당 예상 `6~8분`
- 총 예상 `6~8시간`

## 시간 추정 전제

- Docker GPU canonical runtime
- `run-exp` 종료코드보다 artifact 존재를 우선 신뢰
- 하네스가 중복 artifact는 skip

## 결과 루트

- host:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-14/2026-04-14-table1-blockA-seed34`
- container:
  - `/workspace/tmp/2026-04-14/2026-04-14-table1-blockA-seed34`

## 문서 루트

- `/home/sunmin/SFL_Semantic/docs/experiments/2026-04-14/2026-04-14_15-28_v01_table1-blockA-seed34-extension`

## 검증

- 러너 셸 문법 검사
- `python -m py_compile`는 코드 변경이 없으므로 생략 가능
- 실행 중에는 `RUNLOG.md`와 결과 개수로 진행률 확인

## 비교 규칙

- 이번 실험 단독으로 claim하지 않는다.
- 완료 후 기존 `seed 1,2` 결과와 결합하여 `4-seed` 평균을 다시 계산한다.
- 이후 `Block B 4-seed`와 같은 seed policy로 `Table 1`을 재작성한다.
