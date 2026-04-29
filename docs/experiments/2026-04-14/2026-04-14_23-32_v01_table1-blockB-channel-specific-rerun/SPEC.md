# Table I Block B 채널별 재실험 스펙

## 목적

채널별 `Block A` 최적 고정점을 반영한 상태에서 `film_max_t`, `film_min_t`를 다시 측정한다.

이번 스펙은 다음 두 조건을 분리해서 본다.

- `AWGN`: `beta=0.05`, `tau_VIB=1.0`
- `Rayleigh`: `beta=0.1`, `tau_VIB=1.0`

## 공통 고정 조건

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
- seeds: `1,2,3,4`

## 채널별 고정점

### AWGN

- `beta=0.05`
- `pruning_threshold=1.0`

### Rayleigh

- `beta=0.1`
- `pruning_threshold=1.0`

## Block B grid

- `(film_max_t, film_min_t) ∈ {(0.7, 0.2), (0.7, 0.3), (0.7, 0.4), (0.8, 0.2), (0.8, 0.3), (0.8, 0.4), (0.9, 0.2), (0.9, 0.3), (0.9, 0.4)}`

총 조합:

- `9` per channel

총 런 수:

- `9 x 2 channels x 4 seeds = 72 runs`

## 실행 순서

1. `AWGN`
2. `Rayleigh`

각 채널 안에서는 아래 순서로 진행한다.

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

## 비교 규칙

- 채널별로 같은 seed set `1,2,3,4` 평균을 사용한다.
- `AWGN`에서는 `beta=0.05`, `tau_VIB=1.0` 하에서 `film` 비교를 한다.
- `Rayleigh`에서는 `beta=0.1`, `tau_VIB=1.0` 하에서 `film` 비교를 한다.

## 성공 기준

이번 단계에서는 다음을 본다.

1. `AWGN`에서 기존 공통 고정점 버전보다 accuracy가 높거나, 같은 accuracy에서 comm가 더 낮은 `film` 조합이 있는가
2. `Rayleigh`에서 기존 공통 고정점 버전보다 `-6 dB`와 final accuracy가 높거나, 유지하면서 comm가 더 낮은 `film` 조합이 있는가
3. 채널별 대표 `film` 조합을 각각 다시 고를 수 있는가

## 실행 규모와 예상 시간

- 총 실행 수: `72 runs`
- run당 예상 시간: 약 `7~8분`
- 총 예상 시간: 약 `8시간 30분 ~ 10시간`
- 시간 추정 전제:
  - Docker GPU 단일 순차 큐
  - `cifar10 / SSFLv6 / 200 rounds` 기준 최근 observed runtime 사용
  - 컨테이너 재기동/skip은 artifact-first 하네스가 자동 처리

## 산출물 경로

결과 루트:

- `/workspace/tmp/2026-04-14/2026-04-14-table1-blockB-channel-specific-rerun`

문서 루트:

- `/home/sunmin/SFL_Semantic/docs/experiments/2026-04-14/2026-04-14_23-32_v01_table1-blockB-channel-specific-rerun`

## 검증

- 문서 경로 확인
- 실행 스크립트 `bash -n`
- canonical Docker GPU runtime 실행

## 메모

- 이번 실험은 채널별 최적 고정점 버전이다.
- 기존 공통 고정점 Block B 결과와 별도로 보관한다.
