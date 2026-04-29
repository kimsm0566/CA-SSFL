# Method2 Explainer

## 개요

이번 suite의 `method2`는 `base-support + refinement-support` 방식이다.

핵심 아이디어는 단순하다.

- 모든 active feature를 한 덩어리로 보지 않고
- `항상 남겨야 하는 base support`
- `추가로 보내는 refinement support`
로 나눠서 선택한다.

이 방식은 `successive refinement` 계열 문헌에서 가져온 아이디어를 현재 `CA-SSFL`의 sparse semantic feature 선택 구조에 맞게 단순화한 버전이다.

## 왜 이 방법을 넣었나

현재 `CA-SSFL`의 Rayleigh 취약점은 다음처럼 정리할 수 있었다.

- 중요한 semantic feature가 너무 몇 개 좌표에 몰린다.
- 저 SNR 또는 deep fade에서 그 좌표가 손상되면 대체할 feature가 부족하다.
- 현재 hard mask는 선택된 차원을 한 단계로만 다룬다.

그래서 `method2`는

- 중요도가 가장 높은 일부는 무조건 남기고
- 그 다음 중요도 feature는 추가층으로 붙이는

2계층 support 구조를 만들어, 완전히 brittle한 단일 support보다 더 안정적인 전송 집합을 만들려는 시도다.

## 코드에서 실제로 어떻게 동작하나

관련 코드:

- [trainer.py](/home/sunmin/SFL_Semantic/src/utils/trainer.py)
- [option.py](/home/sunmin/SFL_Semantic/src/utils/option.py)

CLI 옵션은 다음 3개다.

- `--base_refinement_enable`
- `--base_support_k`
- `--refinement_support_k`

현재 실험에서 쓴 설정은:

- `base_refinement_enable=1`
- `base_support_k=128`
- `refinement_support_k=128`

즉 총 최대 `256`차원을 보낸다.

## 선택 절차

`method2`는 클라이언트에서 아래 순서로 동작한다.

### 1. 기본 mask 생성

기존 `CA-SSFL`와 동일하게 먼저 기본 mask를 만든다.

- `vib_mask`: `KL > pruning_threshold`
- `chan_mask`: FiLM 출력이 현재 SNR 기반 threshold를 넘는지
- 최종 기본 mask: `mask = vib_mask * chan_mask`

즉 `method2`는 기존 semantic selection을 완전히 버리는 게 아니라, 그 위에 support 구조를 다시 정리하는 방식이다.

### 2. support score 계산

그 다음 각 차원의 중요도를 나타내는 `support_scores`를 만든다.

- VIB가 있을 때: `support_scores = kl_mean_batch * chan_mask`
- VIB가 없을 때: `support_scores = chan_mask`

즉 score는 사실상

- semantic 중요도(KL)
- 현재 channel gate 통과 여부

를 같이 반영한 값이다.

### 3. base support 선택

`build_base_refinement_indices(...)`에서 전체 4096차원 중 score가 가장 큰 상위 `base_support_k`개를 먼저 뽑는다.

현재 설정에선:

- top-128 차원이 `base support`

가 된다.

이 부분이 “최소한 이 정보는 항상 남긴다”에 해당한다.

### 4. refinement support 선택

그 다음 이미 뽑힌 base support를 제외하고,
기존 기본 mask 안에 남아 있는 차원들 중 score가 높은 상위 `refinement_support_k`개를 추가로 뽑는다.

현재 설정에선:

- 추가 top-128 차원이 `refinement support`

가 된다.

즉 최종 전송 집합은:

- 가장 중요한 128개
- 그 다음으로 중요한 128개

의 합집합이다.

코드상 구현은 이 함수에 있다.

- [trainer.py](/home/sunmin/SFL_Semantic/src/utils/trainer.py)

핵심 로직은 다음과 같다.

- base는 전체 score 기준 top-k
- refinement는 `기존 base 제외 + 기존 mask 내부`에서 top-k
- 마지막엔 둘을 합쳐 정렬 후 전송

## 중요한 점

이 방법은 “두 번 전송”이 아니다.

이름만 보면 base와 refinement를 두 단계에 걸쳐 따로 보내는 것처럼 보일 수 있는데,
현재 구현은 한 라운드 안에서 최종 전송 support를 2계층 규칙으로 고르는 방식이다.

즉:

- 전송 phase를 2번 나누는 것은 아님
- feature 선택 규칙을 2계층으로 나눈 것임

그래서 현재 코드 기준으론 `successive refinement`의 완전한 구현이 아니라,
그 아이디어를 sparse support selection으로 옮긴 경량화 버전이라고 보는 게 맞다.

## 왜 이게 Rayleigh에 도움이 될 수 있나

이 방식의 의도는 다음과 같다.

### 1. 정말 중요한 feature를 따로 보호한다

기존 방식은 “살아남은 support 전체”가 사실상 한 계층이었다.

반면 `method2`는

- 최상위 중요 feature를 base로 먼저 고정
- 나머지를 refinement로 추가

하므로, support budget이 제한돼도 핵심 정보가 먼저 보장된다.

### 2. 불필요한 저중요도 차원 전송을 줄인다

기존 mask는 어떤 라운드나 SNR에서는 상대적으로 덜 중요한 차원이 섞여 들어갈 수 있다.

`method2`는 score 정렬 기반으로 support를 재구성하므로,
현재 budget 안에서 더 “핵심적인 차원” 위주로 전송하게 된다.

### 3. 통신량을 더 잘 제어할 수 있다

현재 설정에선 `128 + 128 = 256`으로 support budget이 비교적 명시적으로 정해진다.

그래서 baseline보다

- 전송 차원 수가 더 일정해지고
- total communication도 줄어들 수 있다

는 장점이 있다.

## 이번 실험에서 왜 잘 나왔나

이번 `seed=1,2` 결과에선 `method2`가 다음처럼 baseline보다 좋았다.

- final acc: `41.91 -> 42.28`
- total comm: `19608.50 MB -> 17364.44 MB`
- `-6 dB`: `39.37 -> 39.83`

즉 이번 설정에서는

- 중요 feature를 먼저 확보하는 규칙이
- Rayleigh에서의 brittle함을 줄이면서
- 전체 support를 좀 더 경제적으로 쓰는 쪽으로 작동했다

고 해석할 수 있다.

특히 `method1`처럼 repetition으로 중복 전송하지 않았기 때문에,
통신량이 오히려 줄어든 점이 중요하다.

## 현재 한계

### 1. 아직 진짜 multi-stage transmission은 아니다

현재는 base와 refinement를 실제로 시간적으로 나눠 보내지 않는다.

즉 이름은 비슷하지만,
문헌의 `successive refinement`를 완전히 구현한 것은 아니다.

### 2. `k` 값이 hand-tuned 상태다

지금 결과는 `128 / 128` 설정에서 나온 것이다.

따라서 다음 단계에선 적어도 다음을 확인해야 한다.

- `base_support_k`
- `refinement_support_k`
- total budget 고정 vs 가변

### 3. seed가 아직 2개다

현재는 `seed=1,2` exploratory 결과다.

claim용으로 쓰려면

- seed 확장
- AWGN 재현
- SC-USFL / SFL 대비 비교표 갱신

이 필요하다.

## 한 줄 요약

`method2`는 기존 sparse semantic mask 위에서 가장 중요한 차원을 먼저 확보하는 `2계층 support selection`을 적용해, Rayleigh에서 핵심 semantic feature를 더 안정적으로 남기면서 통신량도 줄인 방법이다.
