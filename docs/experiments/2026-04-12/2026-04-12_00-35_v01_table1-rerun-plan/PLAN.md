# Table I 재실험 계획

## 배경

원고의 `Table I`는 `CA-SSFL`의 하이퍼파라미터 민감도 분석을 요약한다.
구체적으로는 두 축을 본다.

- 좌측: `beta`와 `tau_VIB(pruning_threshold)`의 조합 효과
- 우측: `film_max_t`, `film_min_t`의 조합 효과

현재 저장소에서는 이후 여러 재실험과 비교군 정리가 진행되면서,
원고의 `Table I` 수치가 지금 코드 경로에서 그대로 재현되는지 다시 확인할 필요가 있다.

## 목표

현재 canonical Docker GPU 경로에서 `Table I`를 다시 측정 가능한 형태로 재구성한다.

이번 단계의 목적은 두 가지다.

1. 원고 `Table I`의 수치가 현재 코드/환경에서 얼마나 재현되는지 확인
2. 논문에 넣을 수 있는 최신 `Table I updated` 후보를 만들기 위한 실험 기반 마련

## 핵심 질문

1. `beta`와 `pruning_threshold`의 trade-off는 현재 코드에서도 같은 방향으로 나타나는가?
2. `film_max_t`, `film_min_t`의 최적 조합은 현재 코드에서도 여전히 `0.7 / 0.4` 근처인가?
3. 채널별 최적 조합이 원고와 동일한가?
   - AWGN
   - Rayleigh

## 비교 대상

대상은 `CA-SSFL Orig`만 사용한다.

즉 다음 설정을 고정한다.

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

## 기본 고정 조건

- dataset: 우선 `cifar10`
- partition: `class`
- `n_clients=8`
- `n_client_data=3000`
- `batch_size=100`
- `n_epochs=1`
- `n_rounds=200`
- `model_type=resnetv2`
- `compressed_dim=4096`
- `train_snr=10`
- seed:
  - 탐색: `1,2`
  - 필요 시 확장: `1,2,3,4`

## 채널

- `AWGN`
- `Rayleigh`

## 실험 블록

### Block A: beta-threshold grid

목적:

- `beta`와 `pruning_threshold`의 상호작용 재확인

고정:

- `film_max_t=0.7`
- `film_min_t=0.4`

후보:

- `beta`: 원고 Table I에 맞는 소수 개 후보
- `pruning_threshold`: 원고 Table I에 맞는 소수 개 후보

주의:

- 논문용 표이므로 값 간격은 지나치게 미세하게 두지 않는다.

### Block B: film threshold grid

목적:

- `film_max_t`, `film_min_t` 조합의 trade-off 재확인

고정:

- `beta=0.01`
- `pruning_threshold=1.0`

후보:

- 원고 Table I 오른쪽 블록에 맞는 대표 조합

## 실행 순서

1. 원고 Table I에 실린 정확한 후보 집합 추출
2. `SPEC.md`에 grid를 고정
3. `AWGN`에서 Block A, Block B 실행
4. `Rayleigh`에서 Block A, Block B 실행
5. 각 블록별 `accuracy / communication` 정리
6. 원고 Table I와 현재 재실험 수치 비교

## 성공 기준

- 현재 코드 경로에서 `Table I` 재작성 가능한 데이터 확보
- 각 후보의 `final acc`와 `comm`를 채널별로 정리 가능
- 원고 대비 어떤 값이 유지/변화했는지 설명 가능

## 리스크

- 원고 시점 실험은 `n_clients=9` 또는 다른 hidden condition을 사용했을 가능성이 있다.
- 따라서 현재 조건이 조금 다르면 완전 일치보다 “방향성 재현”이 더 현실적일 수 있다.
- 특히 `Rayleigh` 쪽은 seed 민감도가 더 크므로 exploratory 결과만으로 claim하면 안 된다.

## 다음 단계

이 계획 승인 후 `SPEC.md`에서 다음을 고정한다.

- 정확한 grid 값
- AWGN/Rayleigh별 실행 순서
- 결과 저장 루트
- exploratory와 claim-making 구분
