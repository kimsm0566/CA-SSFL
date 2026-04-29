# CIFAR-100 교차 벤치마크 계획

## 배경

현재 그래프와 비교 결과는 대부분 `cifar10` 기준으로 정리되어 있다.  
사용자는 동일한 비교 축을 `cifar100`에도 확장해서, `SFL`, `SC-USFL`, `CA-SSFL`의 상대 위치를 다시 확인하고자 한다.

## 목표

`cifar100`에서 다음 세 방법의 성능-통신 trade-off를 동일 조건으로 비교한다.

- `SFL`
- `SC-USFL`
- `CA-SSFL`

채널은 기존 그림과 동일하게 다음 두 환경을 대상으로 한다.

- `AWGN`
- `Rayleigh`

## 핵심 질문

1. `cifar100`에서도 `CA-SSFL`이 `SC-USFL` 대비 통신량 이점을 유지하는가?
2. `cifar100`에서도 `Rayleigh` 저 SNR 구간에서 `CA-SSFL`의 강건성이 어떻게 나타나는가?
3. `cifar10`에서 본 상대 순위가 `cifar100`에서도 재현되는가?

## 기본 가설

- `cifar100`은 클래스 수가 많아져 semantic representation 난도가 올라가므로, 전체 정확도는 `cifar10`보다 낮아질 가능성이 크다.
- 그럼에도 `CA-SSFL`은 `SFL` 대비 통신량 이점은 유지할 가능성이 높다.
- `SC-USFL` 대비 우위 여부는 `Rayleigh`에서 더 불안정할 수 있다.

## 비교 대상

- `SFL`
- `SC-USFL`
- `CA-SSFL Orig`

주의:

- 현재 시점에서는 최근 후보 실험들(`spreading`, `variable refinement`, `semantic-aware refinement` 등)은 포함하지 않는다.
- 먼저 가장 해석이 단순한 3-way baseline 비교를 `cifar100`에서 다시 만든다.

## 제안 고정 조건

- dataset: `cifar100`
- partition: `class`
- `n_clients=8`
- `n_client_data=3000`
- `batch_size=100`
- `n_epochs=1`
- `n_rounds=200`
- model:
  - `SFL`, `SC-USFL`: 기존 baseline 설정 유지
  - `CA-SSFL`: 기존 `Orig` 설정 유지
- seed set: `1,2,3,4`
- 채널:
  - `AWGN`
  - `Rayleigh`

## CA-SSFL 가정 설정

현재 그래프 기준의 `CA-SSFL`은 다음 `Orig` 설정을 의미한다.

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

하이퍼파라미터:

- `beta=0.01`
- `pruning_threshold=1.0`
- `film_max_t=0.7`
- `film_min_t=0.4`
- `compressed_dim=4096`
- `train_snr=10`

## 실행 순서

1. `cifar100` 데이터 로딩과 smoke 가능 여부 확인
2. `AWGN` 3-way benchmark 실행
3. `Rayleigh` 3-way benchmark 실행
4. `seed 1,2,3,4` 평균/분산 정리
5. `SNR vs Accuracy`, `Round vs Accuracy` 그래프 생성

## 성공 기준

이번 단계의 목적은 새 방법 claim이 아니라 `cifar100` 기준 benchmark 구축이다.

따라서 성공 기준은:

- 세 방법 모두 동일 조건에서 재현
- 결과 파일 저장 및 요약 가능
- `AWGN`, `Rayleigh` 그래프 재생성 가능

## 리스크

- `cifar100`은 현재 코드상 지원 흔적은 있으나, 실제 canonical benchmark로는 아직 충분히 검증되지 않았을 수 있다.
- 클래스 수 증가로 학습 수렴이 느려질 수 있다.
- 같은 round budget에서 전체 정확도가 낮아질 수 있다.

## 다음 단계

이 계획 승인 후 `SPEC.md`에서 다음을 고정한다.

- 정확한 실행 명령
- 결과 루트
- smoke 범위
- graph 생성 경로
