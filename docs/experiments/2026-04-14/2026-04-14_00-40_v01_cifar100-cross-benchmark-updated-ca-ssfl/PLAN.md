# CIFAR-100 교차 벤치마크 계획 (업데이트된 CA-SSFL 대표 설정)

## 배경

`cifar10` 기준 `Table I` 재실험 결과, 현재 코드 기준 `CA-SSFL` 대표 설정은 채널별로 다음처럼 정리됐다.

- `AWGN`: `beta=0.010`, `pruning_threshold=1.0`, `film_max_t=0.7`, `film_min_t=0.2`
- `Rayleigh`: `beta=0.010`, `pruning_threshold=1.0`, `film_max_t=0.7`, `film_min_t=0.2`

즉 이번 시점에서 `CA-SSFL`의 대표 설정은 채널 공통으로 아래를 사용한다.

- `beta=0.010`
- `pruning_threshold=1.0`
- `film_max_t=0.7`
- `film_min_t=0.2`

이제 `cifar100`에서도 같은 대표 설정으로 `SFL`, `SC-USFL`, `CA-SSFL`의 상대 위치를 다시 확인해야 한다.

## 목적

`cifar100`에서 아래 세 방법을 동일 조건으로 다시 비교한다.

- `SFL`
- `SC-USFL`
- `CA-SSFL`

채널:

- `AWGN`
- `Rayleigh`

## 핵심 질문

1. `cifar100`에서도 업데이트된 `CA-SSFL` 대표 설정이 `SC-USFL` 대비 통신량 이점을 유지하는가?
2. `cifar100`의 `Rayleigh`에서도 `CA-SSFL`가 경쟁력 있는 강건성을 보이는가?
3. `cifar10`에서 업데이트된 대표 설정이 `cifar100`에서도 무난한 기본점으로 유지되는가?

## 기본 가설

1. `cifar100`은 클래스 수 증가로 인해 전체 정확도는 `cifar10`보다 낮아질 가능성이 높다.
2. 그래도 `CA-SSFL`는 `SFL` 대비 통신량 이점은 유지할 가능성이 높다.
3. `SC-USFL`와의 우열은 `Rayleigh`에서 더 민감하게 바뀔 수 있다.
4. `film_max_t=0.7`, `film_min_t=0.2`는 현재 코드 기준에서 `CA-SSFL`의 가장 설득력 있는 공통 대표값이다.

## 비교 대상

### SFL

- 기존 canonical benchmark 설정 유지

### SC-USFL

- 기존 canonical benchmark 설정 유지

### CA-SSFL

- `algorithm=SSFLv6`
- `semantic_spreading=0`
- `snr_adaptive_beta=0`
- `semantic_power=0`
- `latent_mixing=0`
- `encoder_downsample=0`
- `semidense=0`
- `support_floor=0`
- `importance_repetition=0`
- `base_refinement=0`
- `csi_source_mask=0`
- `server_feature_impute=0`

대표 하이퍼파라미터:

- `beta=0.010`
- `pruning_threshold=1.0`
- `film_max_t=0.7`
- `film_min_t=0.2`
- `compressed_dim=4096`
- `train_snr=10`

## 공통 고정 조건

- dataset: `cifar100`
- partition: `class`
- `n_clients=8`
- `n_client_data=3000`
- `batch_size=100`
- `n_epochs=1`
- `n_rounds=200`
- `major_percent=0.8`
- `model_type=resnetv2`
- seeds: `1,2,3,4`

## 실행 순서

1. `SPEC.md`에서 업데이트된 `CA-SSFL` 설정과 결과 루트를 확정한다.
2. 필요한 경우 `cifar100` smoke를 새 대표 설정 기준으로 짧게 다시 확인한다.
3. `AWGN` 3-way benchmark 실행
4. `Rayleigh` 3-way benchmark 실행
5. 평균/분산 및 그래프 재생성

## 산출물 계획

- `SPEC.md`
- `RUNLOG_AWGN.md`
- `RUNLOG_RAYLEIGH.md`
- `RESULT.md`
- summary tsv/csv
- 업데이트된 `SNR vs Accuracy`, `Round vs Accuracy` 그래프

## 성공 기준

이번 단계의 목적은 새 방법 claim이 아니라 `cifar100` 기준 benchmark를 업데이트하는 것이다.

따라서 성공 기준은:

- 세 방법 모두 동일 조건에서 재현
- `AWGN`, `Rayleigh` 결과 저장
- 그래프 재생성 가능
- `CA-SSFL` 대표 설정이 최신 `cifar10` 결정과 일관되게 반영

## 메모

- 이번 실험은 이전 `2026-04-11`의 `cifar100` benchmark를 덮어쓰지 않고 별도 버전으로 남긴다.
- 비교 기준은 동일하게 유지하되, `CA-SSFL` 대표 설정만 최신 결정값으로 갱신한다.
