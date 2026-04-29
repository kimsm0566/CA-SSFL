# Table I Block B 채널별 재실험 계획

## 배경

`Table I`의 왼쪽 블록(`beta x tau_VIB`)을 `seed 1,2,3,4`로 다시 맞춘 결과, 채널별 최적 고정점이 달라졌다.

- `AWGN`: `beta=0.05`, `tau_VIB=1.0`
- `Rayleigh`: `beta=0.1`, `tau_VIB=1.0`

기존 `Block B`는 두 채널 모두 `beta=0.01`, `tau_VIB=1.0`으로 고정하고 `film_max_t`, `film_min_t`를 비교했다. 이 설정은 초기 exploratory 기준으로는 무난했지만, 현재 `4-seed` 결과와는 맞지 않는다.

따라서 `Block B`는 채널별 `Block A` 최적 고정점을 반영해 다시 측정해야 한다.

## 목적

채널별 `Block A` 최적점을 반영한 상태에서 `film_max_t`, `film_min_t`를 다시 측정해, `AWGN`과 `Rayleigh` 각각의 최신 `Table I` 오른쪽 블록 수치를 재작성한다.

## 가설

1. `AWGN`에서는 `beta=0.05`, `tau_VIB=1.0`을 고정했을 때 기존 공통점(`0.01`, `1.0`)보다 더 높은 정확도 구간이 유지될 것이다.
2. `Rayleigh`에서는 `beta=0.1`, `tau_VIB=1.0`을 고정했을 때 저 SNR과 최종 정확도 모두 기존 공통점보다 더 높은 기준선이 형성될 것이다.
3. `film_max_t`, `film_min_t`의 상대 순위는 일부 유지되더라도, 채널별 최적 고정점이 바뀌면 절대 수치는 달라질 수 있다.

## 실험 범위

공통 고정:

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

채널별 고정:

- `AWGN`: `beta=0.05`, `tau_VIB=1.0`
- `Rayleigh`: `beta=0.1`, `tau_VIB=1.0`

대상 grid:

- `(film_max_t, film_min_t) ∈ {(0.7, 0.2), (0.7, 0.3), (0.7, 0.4), (0.8, 0.2), (0.8, 0.3), (0.8, 0.4), (0.9, 0.2), (0.9, 0.3), (0.9, 0.4)}`

## 비교 기준

채널별로 같은 seed set `1,2,3,4` 평균을 사용한다.

- `AWGN`: `beta=0.05`, `tau_VIB=1.0` 하에서 `film` 비교
- `Rayleigh`: `beta=0.1`, `tau_VIB=1.0` 하에서 `film` 비교

주 비교 지표:

- final accuracy
- total communication cost
- `-6 dB` accuracy
- `12 dB` accuracy

## 실행 규모와 예상 시간

- 총 조합 수: `9 film pairs x 2 channels x 4 seeds = 72 runs`
- run당 예상 시간: 약 `7~8분`
- 총 예상 시간: 약 `8시간 30분 ~ 10시간`
- 시간 추정 전제:
  - Docker GPU 단일 큐 순차 실행
  - 현재 `cifar10 / SSFLv6` 기준 최근 런타임 패턴 사용
  - 비정상 종료 없이 artifact-first skip/retry 하네스가 정상 동작할 때 기준

## 산출물 계획

- `SPEC.md`
- `RUNLOG.md`
- `launcher.log`
- `RESULT.md`
- `summary_blockB_seed1234.tsv`

## 메모

- 이번 계획은 기존 `Block B`의 공통 고정점 버전을 대체하지 않는다.
- 목적은 채널별 최적 고정점 기준의 최신 수치를 별도로 만드는 것이다.
