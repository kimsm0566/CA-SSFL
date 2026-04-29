# Seed 4 붕괴 원인 분석

## 결론

현재 후보 `fixed base + variable refinement`의 `seed 4` 붕괴는 **통신량이 너무 적어서 생긴 문제라기보다, 현재 support selection rule이 어려운 seed에서 semantic core를 잘못 고정하는 구조적 문제**로 보는 것이 맞다.

핵심 요약:

- `seed 4`는 `seed 3`보다 평균 전송량이 거의 같다.
- `seed 4`는 `seed 3`보다 평균 refinement 사용량도 특별히 적지 않다.
- 그런데도 `seed 4`는 전 SNR 구간에서 거의 평평하게 낮은 성능을 보인다.
- 따라서 문제는 `Rayleigh 저 SNR에서 refinement가 부족했다`라기보다, **학습된 representation 자체가 약해졌고 그 약화가 전 SNR 구간에 걸쳐 나타난 것**이다.

## 관찰 1. seed 4는 late-round에서만 무너지는 것이 아니라, 전반적으로 약하다

`seed 3`와 `seed 4`의 server log 비교:

- `seed 3`
  - round 50: `32.08`
  - round 100: `38.85`
  - round 150: `40.39`
  - round 200: `42.54`
- `seed 4`
  - round 50: `25.79`
  - round 100: `29.69`
  - round 150: `32.42`
  - round 200: `28.31`

즉 `seed 4`는 마지막에만 떨어지는 것이 아니라, **중반 이후 전체 구간이 낮다**. 다만 round `181`에서 `34.38`까지 잠깐 올라간 뒤 다시 final `28.31`로 떨어지므로, late-stage instability도 함께 존재한다.

## 관찰 2. seed 4 붕괴는 단순한 communication budget 부족이 아니다

late round data communication:

- `seed 3` round 200 data comm: `7006.88 MB`
- `seed 4` round 200 data comm: `7041.84 MB`

즉 `seed 4`가 `seed 3`보다 덜 보내서 망한 것이 아니다. 오히려 누적 data comm은 비슷하거나 약간 더 높다.

`seed 3`와 `seed 4`의 clean client log 기준 late-round refinement 사용량도 유사하다.

- `seed 3`
  - client 0 late ref mean: `62.25`
  - client 5 late ref mean: `67.73`
  - client 8 late ref mean: `55.10`
- `seed 4`
  - client 0 late ref mean: `64.08`
  - client 4 late ref mean: `68.92`
  - client 8 late ref mean: `66.43`

즉 `seed 4`는 refinement budget을 특별히 덜 받은 것도 아니다.

## 관찰 3. seed 4는 특정 SNR만 망한 것이 아니라 전 SNR 구간이 같이 낮다

`npz` 기준 SNR별 정확도:

- `seed 3`
  - `-6 dB`: `39.34`
  - `0 dB`: `41.80`
  - `12 dB`: `42.74`
- `seed 4`
  - `-6 dB`: `27.86`
  - `0 dB`: `28.59`
  - `12 dB`: `27.29`

이 패턴은 중요하다.

- 만약 원인이 단순히 `저 SNR에서 refinement가 부족`한 것이었다면 `-6 dB` 쪽이 특히 망하고 고 SNR은 어느 정도 살아야 한다.
- 실제 `seed 4`는 고 SNR까지 같이 낮다.

따라서 `seed 4`는 **channel robustness만의 문제가 아니라, representation quality 자체가 약한 상태**라고 보는 것이 맞다.

## 코드상 직접적인 원인 후보

현재 variable refinement rule은 [trainer.py](/home/sunmin/SFL_Semantic/src/utils/trainer.py)에서 이렇게 작동한다.

1. base support는 `KL` 상위 `128`개를 무조건 고른다.
   - [trainer.py](/home/sunmin/SFL_Semantic/src/utils/trainer.py#L183)
2. refinement budget은 `snr_normalized`에 비례해 `0~128` 사이로 정한다.
   - [trainer.py](/home/sunmin/SFL_Semantic/src/utils/trainer.py#L186)
3. refinement는 남은 차원 중 `channel_scores = film_mask` 상위만 고른다.
   - [trainer.py](/home/sunmin/SFL_Semantic/src/utils/trainer.py#L194)
   - [trainer.py](/home/sunmin/SFL_Semantic/src/utils/trainer.py#L200)

문제는 두 부분이다.

### 1. base가 `semantic_candidate_mask`를 무시한다

base는 `semantic_scores` 전체에서 top-k를 뽑는다.

- [trainer.py](/home/sunmin/SFL_Semantic/src/utils/trainer.py#L183)
- [trainer.py](/home/sunmin/SFL_Semantic/src/utils/trainer.py#L184)

즉 현재 구현은:

- `vib_mask`를 통과했는지와 무관하게
- 그냥 상대적으로 `KL`이 큰 `128`개를 base로 강제 전송한다.

이건 baseline과 다르다. baseline은 원래

- `vib_mask * chan_mask`

를 기반으로 active support를 만든다.

- [trainer.py](/home/sunmin/SFL_Semantic/src/utils/trainer.py#L1079)

즉 후보는 baseline보다 더 강한 inductive bias를 갖는다.

- “반드시 보내는 128개”를 너무 일찍 고정한다.
- 이 고정이 쉬운 seed에서는 먹히지만, 어려운 seed에서는 잘못된 semantic core를 계속 유지할 수 있다.

### 2. refinement가 semantic importance보다 channel suitability를 우선한다

variable refinement에서는 refinement score가 `support_scores = KL * chan_mask`가 아니라,

- `channel_scores = film_mask`

기반이다.

- [trainer.py](/home/sunmin/SFL_Semantic/src/utils/trainer.py#L1103)
- [trainer.py](/home/sunmin/SFL_Semantic/src/utils/trainer.py#L1109)

즉 refinement는:

- “남은 차원 중 semantic importance가 높은 것”
이 아니라
- “남은 차원 중 channel-friendly한 것”
을 우선해서 붙인다.

이 구조는 쉬운 seed에서는 base 128이 semantic core를 충분히 담고 있기 때문에 괜찮다.
하지만 어려운 seed에서는:

- base가 semantic core를 충분히 못 담고
- refinement도 semantic 부족분을 채우기보다 channel-friendly feature를 더 싣게 되어
- 결국 전 SNR에서 representation 자체가 약해질 수 있다.

## seed 4를 가장 잘 설명하는 해석

현재 가장 일관된 해석은 아래다.

1. `seed 4`의 partition/optimization 조건에서는 baseline보다 더 다양한 semantic support가 필요했다.
2. 그런데 후보는 base `128`개를 early semantic ranking으로 고정했다.
3. 그 고정 base가 충분히 좋은 semantic core가 아니었고,
4. refinement는 semantic recovery가 아니라 channel-friendly completion으로 동작했다.
5. 그래서 저 SNR만이 아니라 고 SNR에서도 분류 표현 자체가 약해졌다.
6. late round에서는 이 약한 표현이 더 불안정해져 final collapse가 발생했다.

즉 문제를 한 줄로 줄이면:

> 현재 후보는 `base는 너무 경직되고, refinement는 너무 채널 편향적`이라서, 어려운 seed에서 semantic core mis-selection을 복구하지 못한다.

## 그래서 무엇을 버려야 하나

사용자가 이미 정한 대로, **고정형 method2는 더 이상 메인 후보로 쓰지 않는 것이 맞다.**

현재 분석은 그 판단을 지지한다.

- `seed 1,2`에서는 좋아 보일 수 있다.
- 하지만 `seed 4`처럼 어려운 경우에서 semantic core selection 실패를 복구하지 못한다.

## 다음 개선 방향

현재 코드와 이 분석을 같이 보면, 다음 방향이 더 타당하다.

- base는 완전 고정보다 `semantic_candidate_mask` 안에서만 선택
- refinement는 `film_mask` 단독이 아니라 `semantic score + channel score`의 혼합 점수 사용
- 또는 refinement를 semantic recovery 역할로 다시 정의

즉 이후 개선은

- `고정 base + pure channel refinement`

를 유지하는 방향보다,

- `semantic-constrained base + semantic-aware refinement`

쪽으로 가는 것이 맞다.
