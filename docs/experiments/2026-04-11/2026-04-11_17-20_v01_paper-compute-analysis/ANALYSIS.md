# ANALYSIS

## 목적

현재 원고 [IEEE_WCL_SSFL (9).pdf](/home/sunmin/SFL_Semantic/IEEE_WCL_SSFL%20(9).pdf) 의 `Table III: Comparison of Computational Overhead and Model Size`가 현재 코드와 얼마나 일치하는지 확인하고, 최근 후보인 `fixed base + variable refinement`가 추가로 얼마나 연산량을 늘리는지 분석한다.

## 원고 확인 결과

원고에는 이미 다음 서술이 들어가 있다.

- `Table III`에서
  - `SFL`
  - `SC-USFL`
  - `CA-SSFL (Ours)`
  의 `MFLOPs`와 `Model Size (MB)`를 비교함
- 본문에서는
  - `CA-SSFL`가 `SFL`보다 client-side에서 약간의 계산량을 더 요구하지만
  - 통신량 절감 효과가 크므로 실용적이라고 주장함

즉, 현재 논문은 이미 `forward 연산량 + 모델 크기`를 보고 있으며, 최근에 추가한 `method2` 계열이 이 표를 어떻게 바꾸는지만 명확히 하면 된다.

## 측정 기준

현재 코드 기준 측정은 Docker 환경에서 `thop.profile`로 수행했다.

- `thop`가 반환한 값은 `MACs` 기준
- 논문 표의 `MFLOPs`는 관행적으로 `2 x MACs`로 해석하는 것이 맞음
- 따라서 아래 표에서는
  - `MACs`도 적고
  - 논문에 넣을 값은 `FLOPs = 2 x MACs`
  로 읽으면 된다

측정 입력:

- client backbone 입력: `1 x 3 x 32 x 32`
- semantic encoder 입력: `1 x 64 x 8 x 8`
- SSFL decoder 입력: `1 x 4096`, `snr 1 x 1`
- SC-USFL decoder 입력: `1 x 1352`

## 현재 코드 기준 측정값

### 1. SFL

- client params: `149,824` (`0.57 MB`)
- server params: `11,024,138` (`42.05 MB`)
- total params: `42.62 MB`
- client MACs: `10.01 M`
- server MACs: `25.24 M`
- total MACs: `35.25 M`
- total FLOPs 환산: `70.50 MFLOPs`

### 2. SC-USFL

- client params: `510,278` (`1.95 MB`)
- server params: `11,384,318` (`43.43 MB`)
- total params: `45.37 MB`
- client MACs: `11.76 M`
  - semantic encoder MACs: `1.75 M`
- server MACs: `28.37 M`
  - semantic decoder MACs: `3.13 M`
- total MACs: `40.13 M`
- total FLOPs 환산: `80.27 MFLOPs`

### 3. CA-SSFL / Method2 계열

중요:

- `CA-SSFL Orig`
- literature suite의 고정형 `method2`
- 최근의 `fixed base + variable refinement`

이 셋은 **동일한 backbone / encoder / decoder 구조**를 사용한다.  
즉 모델 파라미터와 CNN forward FLOPs는 사실상 같다.

- client params: `532,853` (`2.03 MB`)
- server params: `11,246,238` (`42.90 MB`)
- total params: `44.93 MB`
- client MACs: `17.74 M`
  - semantic encoder MACs: `7.73 M`
- server MACs: `39.18 M`
  - semantic decoder MACs: `13.94 M`
- total MACs: `56.92 M`
- total FLOPs 환산: `113.84 MFLOPs`

## 원고 Table III와의 정합성

원고 Table III 값:

- `SFL`: `70.10 MFLOPs`, `42.62 MB`
- `SC-USFL`: `77.10 MFLOPs`, `45.38 MB`
- `CA-SSFL`: `113.36 MFLOPs`, `44.92 MB`

현재 코드 기준 재측정:

- `SFL`: `70.50 MFLOPs`, `42.62 MB`
- `SC-USFL`: `80.27 MFLOPs`, `45.37 MB`
- `CA-SSFL`: `113.84 MFLOPs`, `44.93 MB`

해석:

- `SFL`와 `CA-SSFL`는 사실상 동일 수준으로 재현된다.
- `SC-USFL`는 약간 높게 측정되지만, 차이는 크지 않다.
- 따라서 현재 원고의 Table III는 **현재 코드와 대체로 일치한다**고 봐도 무방하다.

실무적으로는:

- 표 전체를 당장 갈아엎을 정도의 불일치는 아님
- 다만 카메라레디 수준으로 정리할 때는 현재 코드 기준으로 다시 산출해 표를 갱신하는 것이 더 안전함

## Method2가 추가로 늘리는 연산량

### 결론

`method2`와 `fixed base + variable refinement`는 **논문 Table III를 사실상 바꾸지 않는다.**

이유:

- encoder 구조는 그대로 [FiLMChannelAwareEncoder](/home/sunmin/SFL_Semantic/src/models/model.py#L522)
- decoder 구조도 그대로 [FiLMCNNSemanticDecoder](/home/sunmin/SFL_Semantic/src/models/model.py#L850)
- 바뀌는 것은 [trainer.py](/home/sunmin/SFL_Semantic/src/utils/trainer.py#L1101) 이후의 support selection rule뿐이다

즉 바뀌는 것은

- 어떤 차원을 보낼지 고르는 로직
- 선택된 차원 수

이지, CNN/decoder 자체가 아니다.

### 추가 연산 위치

`fixed base + variable refinement`의 추가 연산은 여기서 발생한다.

- base top-k: [trainer.py](/home/sunmin/SFL_Semantic/src/utils/trainer.py#L183)
- refinement budget 계산: [trainer.py](/home/sunmin/SFL_Semantic/src/utils/trainer.py#L186)
- refinement top-k: [trainer.py](/home/sunmin/SFL_Semantic/src/utils/trainer.py#L200)
- 실제 적용 분기: [trainer.py](/home/sunmin/SFL_Semantic/src/utils/trainer.py#L1102)

즉 per-batch 추가 연산은 대략 다음뿐이다.

- `4096`차원 `KL` score에서 top-128
- 남은 후보에서 channel score top-k
- 몇 번의 boolean mask / scatter / concat

### 왜 무시 가능하다고 볼 수 있는가

client encoder의 지배적 연산은 convolution이다.

- semantic encoder MACs만 해도 `7.73 M`
- client 전체 MACs는 `17.74 M`

반면 `method2` 추가 연산은 `4096`차원 벡터 위 top-k와 mask 조작이다.

느슨한 상계로 보더라도:

- `O(D log K)` 규모 top-k 두 번
- `D=4096`, `K=128`

수만 단위의 비교/선택 연산 수준이다.

즉 convolution 기반 수천만 MACs에 비하면 **1% 미만 수준의 부가 오버헤드**로 보는 것이 합리적이다.

따라서 논문에서는 다음처럼 정리하는 것이 맞다.

- `method2`는 추가 semantic selection logic만 바꾸며
- backbone/encoder/decoder 구조는 동일하므로
- `Table III`의 `CA-SSFL` 계산량/모델 크기를 그대로 대표값으로 사용 가능

## 논문용 해석

### 핵심 메시지

1. `CA-SSFL`는 `SC-USFL`보다 forward FLOPs가 더 크다.
2. 하지만 최근 성능이 좋았던 `method2` 계열은 `CA-SSFL`의 구조를 바꾸지 않으므로 FLOPs를 거의 더 늘리지 않는다.
3. 따라서 `method2`의 이득은 `연산량 증가 없이 support allocation rule을 개선해 communication-performance trade-off를 높인 것`으로 해석할 수 있다.

### 넣기 좋은 문장 초안

`Although the proposed base-support and refinement-support variants modify the feature selection rule, they reuse the same client backbone, semantic encoder, and server-side decoder as CA-SSFL. Hence, their model size and dominant convolutional FLOPs remain essentially identical to those of CA-SSFL in Table III. The additional computational cost is limited to lightweight top-k and masking operations over a 4096-dimensional latent vector, which is negligible compared with the tens of millions of MACs required by the convolutional encoder/decoder path.`

## 현재 관점에서의 정리

- `CA-SSFL Orig`와 `method2` 계열의 차이는 주로 `통신 budget allocation`이다.
- `연산량 절감형 개선`이라고 주장하면 안 된다.
- 대신 다음처럼 주장하는 것이 정확하다.

  - `method2`는 연산량을 거의 유지하면서
  - Rayleigh에서 더 좋은 communication-performance trade-off를 달성했다

## 권고

논문 수정 시 다음이 안전하다.

1. `Table III`는 유지하되, 수치를 현재 코드 기준으로 한 번 재산출
2. `method2` 실험 결과를 넣는다면
   - 새로운 FLOPs 표를 만들기보다
   - `CA-SSFL와 동일한 architecture-level complexity`라는 문장으로 처리
3. `method2`의 강점은
   - low-SNR robustness
   - communication reduction
   - negligible computation overhead
   로 정리
