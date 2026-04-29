# Table I 재실험 스펙

## 목적

원고 `Table I`를 현재 canonical Docker GPU 경로에서 다시 측정한다.

이번 단계는 `claim-making`이 아니라 `exploratory rerun`이다.
즉, 원고 시점 수치와 현재 코드/환경의 차이를 먼저 정리하는 것이 목적이다.

## 실험 대상

`CA-SSFL Orig`만 사용한다.

고정:

- `algorithm=SSFLv6`
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

## 공통 고정 조건

- dataset: `cifar10`
- partition: `class`
- `n_clients=8`
- `n_client_data=3000`
- `batch_size=100`
- `n_epochs=1`
- `n_rounds=200`
- `model_type=resnetv2`
- `compressed_dim=4096`
- `train_snr=10`
- seeds: `1,2`

## 채널

- `AWGN`
- `Rayleigh`

## Block A: beta-threshold grid

설명:

- 원고 Table I 왼쪽 블록을 그대로 따른다.
- `film_max_t=0.7`, `film_min_t=0.4` 고정
- `beta`와 `pruning_threshold` 조합을 측정

고정:

- `film_max_t=0.7`
- `film_min_t=0.4`

grid:

- `beta ∈ {0.100, 0.050, 0.010, 0.005, 0.001}`
- `pruning_threshold ∈ {1.5, 1.0, 0.5}`

총 조합:

- `5 x 3 = 15` per channel

## Block B: film range grid

설명:

- 원고 Table I 오른쪽 블록을 그대로 따른다.
- `beta=0.010`, `pruning_threshold=1.0` 고정
- `film_max_t`, `film_min_t` 조합을 측정

고정:

- `beta=0.010`
- `pruning_threshold=1.0`

grid:

- `(film_max_t, film_min_t) ∈ {(0.7, 0.2), (0.7, 0.3), (0.7, 0.4), (0.8, 0.2), (0.8, 0.3), (0.8, 0.4), (0.9, 0.2), (0.9, 0.3), (0.9, 0.4)}`

총 조합:

- `9` per channel

## 총 런 수

per seed:

- Block A: `15 x 2 channels = 30`
- Block B: `9 x 2 channels = 18`
- total: `48`

seed `1,2` exploratory:

- total `96 runs`

## 실행 순서

1. `AWGN Block A`
2. `AWGN Block B`
3. `Rayleigh Block A`
4. `Rayleigh Block B`

## 결과 루트

- `/workspace/tmp/2026-04-12/2026-04-12-table1-rerun`

문서 루트:

- `/home/sunmin/SFL_Semantic/docs/experiments/2026-04-12/2026-04-12_00-35_v01_table1-rerun-plan`

## 산출물

- `RUNLOG.md`
- `RESULT.md`
- block별 summary json/csv

## 판정 기준

이번 단계에서는 다음을 본다.

1. 원고와 동일한 최적점이 현재도 나오는가?
2. AWGN 최적점:
   - 원고 기준 `beta=0.010`, `pruning_threshold=1.0`, `film_max_t=0.7`, `film_min_t=0.4`
3. Rayleigh 최적점:
   - 원고 본문 기준 `beta=0.005`, `film_max_t=0.8`, `film_min_t=0.3`

## 주의

- 현재 코드의 FiLM threshold 식과 원고 서술이 완전히 일치하지 않을 수 있다.
- 따라서 이번 재실험은 “현재 코드 기준 재현”으로 해석한다.
- exploratory `seed 1,2`에서 유망점이 보이면 그 후보만 `seed 3,4` 확장한다.
