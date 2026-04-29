# PLAN

## 실험 이름

`Rayleigh semantic-aware variable refinement reimplementation`

## 배경

직전 `fixed base + variable refinement` 후보는 `seed 1,2`에서는 좋아 보였지만, `seed 3,4`, 특히 `seed 4`에서 무너졌다.

후속 분석 결과, 현재 구현은 원래 의도보다 더 경직되고 더 채널 편향적으로 동작하고 있었다.

- `base`는 `semantic candidate mask` 내부가 아니라 전체 `KL top-k`로 고정됨
- `refinement`는 semantic recovery보다 `channel score` 위주로 선택됨

즉 이전 후보는 우리가 의도한

- `semantic-constrained base`
- `semantic-aware refinement`

가 아니라, 실제로는

- `globally fixed base`
- `channel-biased refinement`

에 더 가까웠다.

## 문제 정의

현재 문제는 아이디어 자체의 실패라기보다, **구현이 계획 의도보다 더 강하고 더 편향된 선택 규칙으로 굳어져 있었다**는 점이다.

이 상태에서는 어려운 seed에서 잘못 선택된 semantic core를 refinement가 복구하지 못한다.

## 핵심 가설

다음 두 수정을 적용하면, 이전 후보의 `seed 4` 붕괴 원인을 완화할 수 있다.

1. `base`를 `semantic candidate mask` 내부에서만 선택한다.
2. `refinement`를 `semantic score + channel score`의 혼합 점수로 선택한다.

그러면

- semantic core mis-selection을 줄이고
- refinement가 단순 channel-friendly completion이 아니라 semantic recovery 역할도 수행하게 되어
- Rayleigh에서 더 안정적인 seed robustness를 얻을 수 있다.

## 이번 재구현의 의도

이번 실험은 새로운 큰 아이디어를 넣는 것이 아니라, **이전 variable refinement 아이디어를 원래 계획 의도대로 다시 구현하는 것**이다.

즉 비교 대상은:

- `CA-SSFL Orig`
- 직전 구현된 `fixed base + variable refinement`
- 이번 재구현 버전

이다.

## 재구현 원칙

### 1. Base support

- `semantic_candidate_mask` 내부에서만 선택
- 기본적으로 `vib_mask` 내부 top-`K_base`
- `vib_mask` 유효 차원이 `K_base`보다 적으면 그 부족분만 semantic score 순으로 보충

### 2. Refinement support

- base를 제외한 차원 중에서만 선택
- refinement candidate도 기본적으로 `semantic_candidate_mask` 내부로 제한
- refinement score는 `semantic score`와 `channel score`를 둘 다 반영

### 3. Variable budget

- refinement 예산은 여전히 SNR에 따라 가변
- 단, refinement가 semantic recovery 역할을 하도록 점수 정의를 바꾼다

## 비교 질문

1. 이전 잘못 구현된 variable refinement보다 안정적인가?
2. `seed 4` 같은 어려운 경우의 붕괴를 줄이는가?
3. baseline 대비 comm 이득을 유지하면서 final acc와 `-6 dB`를 덜 희생하는가?

## 고정 조건

1차 exploratory는 아래를 유지한다.

- dataset: `cifar10`
- partition: `class`
- channel: `rayleigh`
- `n_clients=8`
- `n_client_data=3000`
- `batch_size=100`
- `n_epochs=1`
- `n_rounds=200`
- `algorithm=SSFLv6`
- `model_type=resnetv2`
- `compressed_dim=4096`
- `beta=0.01`
- `pruning_threshold=1.0`
- `film_max_t=0.7`
- `film_min_t=0.4`

## 초기 seed 전략

먼저 `seed 1,2` exploratory로 최소 검증을 한다.

이유:

- 이전 버전도 `seed 1,2`에서는 성능이 좋게 나왔기 때문에
- 재구현이 논리적으로 맞게 동작하는지, 그리고 comm/acc scale이 상식적인지 먼저 본다

그 다음:

- `seed 3,4`를 붙여 재현성과 stability를 본다

## 성공 기준

1차 성공 기준:

- 직전 variable refinement 대비 final acc 개선 또는 비열화
- 직전 variable refinement 대비 `-6 dB` 개선
- baseline 대비 comm 절감 유지

2차 승격 기준:

- `seed 1,2,3,4` 기준으로 baseline 대비 final acc와 `-6 dB` 열화를 줄이거나 제거
- `SC-USFL` 대비 comm 우위 유지

## 리스크

- semantic candidate mask를 너무 강하게 걸면 refinement가 충분히 못 붙을 수 있다
- mixed score weighting이 잘못되면 base와 refinement가 사실상 같은 좌표를 선호할 수 있다
- 이전 변수명과 결과 경로를 그대로 쓰면 해석이 혼동될 수 있다

## 실행 순서

1. `SPEC.md`에서 정확한 selection rule 고정
2. 최소 코드 수정
3. `python -m py_compile`
4. Docker GPU `1-round smoke`
5. `seed 1,2` exploratory
6. 결과가 괜찮으면 `seed 3,4`
