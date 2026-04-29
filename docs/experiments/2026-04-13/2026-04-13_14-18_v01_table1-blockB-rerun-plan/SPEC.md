# Table I Block B 재실험 스펙

## 목적

`Table I` 오른쪽 블록(`film_max_t`, `film_min_t`)을 현재 canonical Docker GPU 경로에서 다시 측정한다.

이번 단계는 `beta=0.010`, `pruning_threshold=1.0`을 공통 대표 파라미터로 고정하고, `film` 범위만 비교하는 matched rerun이다.

## 실험 대상

`CA-SSFL`만 사용한다.

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
- `beta=0.010`
- `pruning_threshold=1.0`
- seeds: `1,2,3,4`

## 채널

- `AWGN`
- `Rayleigh`

## Block B grid

- `(film_max_t, film_min_t) ∈ {(0.7, 0.2), (0.7, 0.3), (0.7, 0.4), (0.8, 0.2), (0.8, 0.3), (0.8, 0.4), (0.9, 0.2), (0.9, 0.3), (0.9, 0.4)}`

총 조합:

- `9` per channel

총 런 수:

- `9 x 2 channels x 4 seeds = 72 runs`

## 비교 기준

대표 기준점:

- `beta=0.010`
- `pruning_threshold=1.0`
- `film_max_t=0.7`
- `film_min_t=0.4`

비교 규칙:

- 채널별로 같은 seed set `1,2,3,4` 평균을 사용한다.
- 주 비교는 final accuracy, total communication cost, `-6 dB`, `12 dB`이다.

## 산출물 경로

결과 루트:

- `/workspace/tmp/2026-04-13/2026-04-13-table1-blockB-rerun`

문서 루트:

- `/home/sunmin/SFL_Semantic/docs/experiments/2026-04-13/2026-04-13_14-18_v01_table1-blockB-rerun-plan`

## 실행 순서

1. `AWGN`
2. `Rayleigh`

각 채널 안에서는:

1. `(0.7, 0.2)`
2. `(0.7, 0.3)`
3. `(0.7, 0.4)`
4. `(0.8, 0.2)`
5. `(0.8, 0.3)`
6. `(0.8, 0.4)`
7. `(0.9, 0.2)`
8. `(0.9, 0.3)`
9. `(0.9, 0.4)`

각 조합마다 seed `1,2,3,4`를 순서대로 실행한다.

## 판정 기준

이번 단계에서는 다음을 본다.

1. `AWGN`에서 대표 기준점보다 accuracy가 높거나, accuracy 손실이 작으면서 comm가 더 낮은 조합이 있는가
2. `Rayleigh`에서 대표 기준점보다 `-6 dB`와 final accuracy가 높거나, 둘을 유지하면서 comm가 더 낮은 조합이 있는가
3. 두 채널 모두에서 공통으로 쓸 수 있는 `film` 범위가 있는가

## 검증

- 문서 변경: 링크, 경로 확인
- 실행 스크립트: `bash -n`
- 실험 실행: canonical Docker GPU runtime

## 메모

- 현재 기본 시드 정책은 `1,2,3,4`다.
- 이번 Block B는 exploratory가 아니라 기본 정책을 따르는 full seed-set rerun이다.
