# Table I Block B 재실험 계획

## 배경

`Table I`의 왼쪽 블록(`beta x pruning_threshold`)을 현재 canonical Docker GPU 경로에서 다시 측정한 결과, 현재 코드 기준으로는 두 채널 모두 `pruning_threshold=1.0`이 가장 안정적이었다.

또한 `beta=0.010, pruning_threshold=1.0` 조합은 다음 이유로 공통 대표 파라미터로 채택할 수 있다.

- `AWGN`에서 정확도-통신량 trade-off가 가장 무난하다.
- `Rayleigh`에서 최종 정확도, `-6 dB`, 통신량의 균형이 가장 무난하다.
- 원고의 기존 기본 설정과도 가장 가깝다.

따라서 `Table I` 오른쪽 블록(`film_max_t`, `film_min_t`)은 아래 대표값을 공통 고정점으로 두고 다시 측정한다.

- `beta=0.010`
- `pruning_threshold=1.0`

## 목적

현재 코드 기준으로 `film_max_t`, `film_min_t` 조합의 상대 성능을 다시 측정하여, 원고 `Table I` 오른쪽 블록을 업데이트할 근거를 만든다.

이번 단계의 목표는 다음과 같다.

1. `AWGN`와 `Rayleigh`에서 `film_max_t`, `film_min_t`의 현재 최적 구간을 확인한다.
2. 원고의 기존 권장 조합이 현재 코드에서도 유지되는지 확인한다.
3. 이후 논문용 `Table I updated` 초안에 들어갈 수치를 정리한다.

## 가설

1. 현재 코드 기준으로도 `film_max_t`, `film_min_t`는 성능에 큰 영향을 준다.
2. `AWGN`에서는 너무 높은 `film_max_t` 또는 너무 낮은 `film_min_t`가 불필요한 통신량 증가 또는 불안정한 gating으로 이어질 수 있다.
3. `Rayleigh`에서는 `film` 범위가 너무 공격적이면 저 SNR에서 표현이 지나치게 줄어들어 `-6 dB` 성능이 악화될 수 있다.
4. `beta=0.010, pruning_threshold=1.0`을 고정하면, `film` 범위 변화의 효과를 더 깨끗하게 볼 수 있다.

## 실험 범위

고정:

- dataset: `cifar10`
- partition: `class`
- `n_clients=8`
- `n_client_data=3000`
- `batch_size=100`
- `n_epochs=1`
- `n_rounds=200`
- `algorithm=SSFLv6`
- `model_type=resnetv2`
- `compressed_dim=4096`
- `train_snr=10`
- `beta=0.010`
- `pruning_threshold=1.0`
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

대상 채널:

- `AWGN`
- `Rayleigh`

대상 grid:

- `(film_max_t, film_min_t) ∈ {(0.7, 0.2), (0.7, 0.3), (0.7, 0.4), (0.8, 0.2), (0.8, 0.3), (0.8, 0.4), (0.9, 0.2), (0.9, 0.3), (0.9, 0.4)}`

seed:

- exploratory: `1,2`

## 비교 기준

주 비교는 같은 `beta=0.010`, `pruning_threshold=1.0`에서 `film` 범위만 바꾼 조합끼리 한다.

참조 기준은 다음 두 점이다.

- `AWGN` 대표점: `beta=0.010, pruning_threshold=1.0, film_max_t=0.7, film_min_t=0.4`
- `Rayleigh` 대표점: `beta=0.010, pruning_threshold=1.0, film_max_t=0.7, film_min_t=0.4`

## 평가지표

- final accuracy
- total communication cost
- `-6 dB` accuracy
- `12 dB` accuracy

## 성공 기준

exploratory 단계에서는 아래를 본다.

1. `AWGN`에서 대표점보다 accuracy가 높거나, accuracy 손실이 매우 작으면서 comm가 더 낮은 조합이 있는가
2. `Rayleigh`에서 대표점보다 `-6 dB`가 높거나, 최종 accuracy와 `-6 dB`를 유지하면서 comm가 더 낮은 조합이 있는가
3. 두 채널에서 공통으로 쓸 수 있는 `film` 범위가 있는가

## 실행 계획

1. `SPEC.md`에서 Block B 고정 조건과 산출물 경로를 확정한다.
2. Docker GPU 기준으로 `seed 1,2` exploratory를 실행한다.
3. 결과를 채널별로 집계해 `Table I updated` 초안을 만든다.
4. 필요하면 유망 조합만 `seed 3,4`로 확장한다.

## 산출물 계획

- `SPEC.md`
- `RUNLOG.md`
- `RESULT.md`
- `summary_blockB_seed12.tsv`

## 메모

- 이번 계획은 `Block B`만 대상으로 한다.
- `Block A` 재실험 결과는 이미 별도 문서에 정리돼 있으며, 그 결과를 바탕으로 `beta=0.010, pruning_threshold=1.0`을 대표값으로 채택한다.
