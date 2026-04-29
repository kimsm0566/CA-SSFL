# Deep Variational Information Bottleneck

## 서지 정보

- 저자: Alexander A. Alemi, Ian Fischer, Joshua V. Dillon, Kevin P. Murphy
- 학회/저널 및 연도: ICLR 2017
- 원문 링크:
  - OpenReview 포럼: https://openreview.net/forum?id=HyxQzBceg
  - PDF: https://openreview.net/pdf?id=HyxQzBceg
  - Google Research: https://research.google/pubs/deep-variational-information-bottleneck/
- 로컬 파일 경로: 미저장

## 한 줄 요약

- VIB는 `I(Z;Y)`는 유지하고 `I(Z;X)`는 줄이도록 확률적 latent bottleneck을 학습해, 분류 성능을 유지하거나 높이면서 입력의 불필요한 정보를 버리려는 방법이다.

## 문제 설정

- 학습 설정: 중앙집중형 지도학습 이미지 분류; semantic learning, split learning, federated learning 설정은 아님
- 데이터셋: permutation-invariant MNIST, ImageNet feature-based classification
- 파티션 방식: 없음
- 클라이언트 수: 해당 없음
- 로컬 학습 예산: 해당 없음
- 채널 모델: 해당 없음
- SNR 설정: 해당 없음
- 통신 제약: 실제 전송 byte 제약은 없고, `I(X;Z)`를 표현 압축 정도의 대리 지표로 사용

## 방법 요약

- 원래 목표는 `max I(Z;Y) - beta * I(Z;X)`이다.
- `p(z|x)`를 확률적 encoder로 두고, `q(y|z)`를 variational decoder로 둬서 `I(Z;Y)`의 하한을 최적화한다.
- `I(Z;X)`는 prior `r(z)`를 사용한 `KL[p(z|x) || r(z)]`로 근사한다.
- 최종 학습식은 실질적으로 `E[-log q(y|z)] + beta * KL[p(z|x) || r(z)]` 꼴이 된다.
- `z`는 Gaussian latent로 샘플링되며 reparameterization trick으로 SGD 학습이 가능하다.
- `beta`가 커질수록 latent는 더 강하게 압축되고, 작은 perturbation을 통과시키기 어려운 확률적 표현이 된다.

## 보고된 결과

- 주요 지표: 분류 error/accuracy, 추정 정보량 `I(X;Z)`, adversarial attack 성공률, perturbation norm
- 비교 기준선: deterministic baseline, dropout, confidence penalty, label smoothing, original Inception-ResNet-v2
- 핵심 성과:
  - MNIST에서 `K=256`, `beta=1e-3`일 때 test error `1.13%`를 기록했고, baseline `1.38%`, dropout `1.34%`, confidence penalty 재현값 `1.36%`보다 낮았다.
  - ImageNet에서는 pretrained Inception-ResNet-v2의 whitened 1536-d feature 위에 얕은 분류기를 얹은 setting에서, `beta=0.01`이 accuracy `80.12%`와 추정 `I(X;Z) ~ 45 bits`를 기록했다.
  - 같은 ImageNet setting에서 `beta=0`은 `78.87%`, deterministic baseline은 `78.75%`였고, 원본 unmodified network는 `80.4%`였다.
- 강건성 점검:
  - MNIST에서는 FGS 및 Carlini-Wagner 계열 공격에 대해 `beta`가 증가할수록 baseline 대비 더 강한 저항성을 보였다고 보고한다.
  - ImageNet targeted `L2` attack에서 target success rate는 Deterministic `1.0`, original IRv2 `1.0`, `VIB(0.01)` `0.567`이었다.
  - 같은 실험에서 평균 perturbation은 `L2`: `6.45 / 14.43 / 43.27`, `L_inf`: `0.18 / 0.44 / 0.92`로, VIB를 속이기 위해 더 큰 교란이 필요했다.

## 이 프로젝트와의 연관성

- 저장소 내 대응 영역:
  - `src/models/model.py`에는 `VIBEncoder`, `VIBDecoder`, 그리고 VIB 기반 semantic encoder 변형이 있다.
  - `src/utils/trainer.py`는 `KL` 항을 별도로 역전파하고, 일부 알고리즘에서는 `KL` 기반 마스크를 만들어 전송 차원을 줄인다.
  - `src/utils/eval.py`도 VIB 기반 `KL` 값을 사용해 채널 선택 패턴을 분석한다.
- 가장 가까운 in-repo 알고리즘 또는 baseline:
  - `SSFL`, `SSFLv6`, `SSFL_w_o_vib`, `SSFLv6_w_o_vib`
- 바로 재사용 가능해 보이는 점:
  - `beta`를 통해 표현 압축 강도를 조절하는 관점
  - `KL` 값을 채널 중요도 추정치로 활용하는 관점
  - 결정론적 latent 대신 확률적 latent를 사용해 노이즈와 입력 섭동에 덜 민감한 표현을 만들려는 관점
- 저장소 관점의 핵심 차이:
  - 이 논문은 실제 통신 byte, 인덱스 오버헤드, multi-SNR 채널, client partition을 다루지 않는다.
  - 따라서 논문의 `I(X;Z)` 감소를 곧바로 이 저장소의 통신량 감소로 해석하면 안 된다.

## 약점과 재현 리스크

- 통신 시스템 관점의 평가가 없다. 실제 전송량, 압축 포맷, 인덱스 오버헤드, aggregation 비용을 다루지 않는다.
- federated/split/semantic setting이 아니라 중앙집중형 분류 실험이므로, 현재 저장소의 주된 문제와는 실험 축이 다르다.
- ImageNet 결과는 end-to-end 이미지 학습이 아니라 pretrained feature + whitening + 얕은 분류기 설정이라 전이 가능성이 제한적이다.
- 저자 스스로도 ImageNet accuracy regression이 training time 또는 hyperparameter 미조정 때문일 수 있다고 적고 있어, `beta` 민감도가 작지 않다.
- adversarial robustness 평가는 표본 수와 공격 종류가 제한적이고, 다중 seed나 채널 조건 강건성은 없다.
- 보고된 `~45 bits`는 variational family와 prior 가정에 의존하는 추정치다. 실제 wire-level communication cost와 동일하지 않다.

## 가능한 개선점

- `KL` 기반 중요도와 실제 전송 byte를 직접 연결하는 masking/quantization/accounting 체계로 확장할 필요가 있다.
- 고정 `beta` 대신 SNR 또는 채널 타입에 따라 조절되는 `beta` 스케줄이 더 적합할 수 있다.
- 표현 압축과 전송 압축이 다르므로, `I(X;Z)`뿐 아니라 실제 누적 MB를 같이 최적화해야 한다.
- richer prior, layer-wise VIB, deterministic fallback을 포함한 ablation이 필요하다.
- robustness 검증도 adversarial attack보다 먼저 AWGN/Rayleigh, seed variation, low-SNR worst-case 성능으로 재정의하는 편이 이 저장소 목적에 맞다.

## 이 코드베이스에서 검증할 가설

- `SSFLv6` 계열에서 `KL` 기반 마스킹을 실제 총 통신량 기준으로 다시 튜닝하면, 정확도를 유지하면서 누적 MB를 더 줄일 수 있다.
- 고정 `beta`보다 SNR-conditioned `beta` 또는 round-dependent `beta`가 multi-SNR 평가에서 더 나은 frontier를 만들 수 있다.
- VIB의 이점이 평균 accuracy보다 low-SNR 구간 정확도나 seed variance 감소에서 더 크게 나타날 수 있다.
- `KL`이 큰 차원만 남기는 규칙은 유효할 수 있지만, 인덱스 오버헤드가 커지면 실제 통신량 기준으로는 이득이 줄어들 수 있으므로 matched comparison이 필요하다.

## 액션 상태

- 상태: 문헌 노트 작성 완료, 구현 및 실험 미착수
- 다음 단계: 이 중 하나를 실험 가설로 채택하려면 `docs/experiments/` 아래에 dated folder를 만들고 `PLAN.md`부터 작성
