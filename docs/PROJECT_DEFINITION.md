# Project Definition

이 문서는 현재 작성 중인 논문

- [IEEE_WCL_SSFL (9).pdf](/home/sunmin/SFL_Semantic/IEEE_WCL_SSFL%20%289%29.pdf)

를 기준으로 프로젝트를 어떻게 정의할지 정리한 작업 문서다.

주의:

- 위 논문은 현재 실험 중인 최신 아이디어를 모두 반영한 버전은 아니다.
- 따라서 이 문서는
  - `논문 버전에서의 프로젝트 정의`
  - `현재 연구 기준으로 업데이트한 프로젝트 정의`
  를 함께 적는다.

## 문서 역할

- 이 문서는 프로젝트의 문제 설정, 범위, 핵심 메커니즘, 평가 축을 정의한다.
- 즉, "이 프로젝트가 정확히 무엇을 연구하는가"를 정리하는 문서다.
- 선행연구 대비 novelty, 과장하면 안 되는 claim boundary, 방어 가능한 기여 서술은 [PROJECT_NOVELTY.md](/home/sunmin/SFL_Semantic/docs/PROJECT_NOVELTY.md)가 담당한다.
- 따라서 범위 정의는 이 문서를 우선 보고, claim-safe positioning은 novelty 문서를 본다.

## 1. 논문 버전에서의 프로젝트 정의

논문 버전에서 이 프로젝트는 다음처럼 정의된다.

- 문제:
  - `Split Federated Learning (SFL)`은 클라이언트 계산 부담을 줄여주지만,
  - 매 배치마다 고차원 intermediate feature, 즉 `smashed data`를 서버로 보내야 해서
  - 심각한 통신 병목과 무선 채널 노이즈 취약성을 가진다.
- 핵심 아이디어:
  - 이 intermediate feature를 그냥 보내지 않고
  - semantic communication 방식으로 의미 있는 부분만 선택적으로 보내자.
- 제안 프레임:
  - `CA-SSFL (Channel-Aware Semantic Split Federated Learning)`
- 기술 요약:
  - `VIB` 기반 semantic mask로 task-relevant feature를 가린다.
  - `SNR` 기반 channel mask로 현재 채널 상태에서 보낼 수 있는 feature budget을 정한다.
  - 두 마스크를 결합해 dynamic slicing을 수행한다.
- 목표:
  - 정확도를 유지하거나 높이면서
  - smashed data 통신량을 줄이고
  - AWGN / Rayleigh 채널에서 robustness를 확보한다.

즉 논문 버전의 한 줄 정의는 아래에 가깝다.

- `CA-SSFL는 split federated learning에서 intermediate smashed data를 semantic relevance와 channel state를 함께 고려해 동적으로 slice하여 통신 효율과 강건성을 높이는 프레임워크다.`

## 2. 현재 연구 기준으로 업데이트한 프로젝트 정의

현재 실험과 문서까지 포함하면, 프로젝트는 단순히 `CA-SSFL 논문 1편`보다 조금 더 넓게 정의하는 편이 맞다.

현재 기준에서 이 프로젝트는:

- split learning / split federated learning 환경에서
- intermediate semantic feature 통신이 병목이 되는 문제를 다루고
- semantic communication 관점으로 task-relevant feature만 남기며
- 현재 채널 상태에 맞는 전송 집합을 선택해
- `accuracy - communication cost - channel robustness`의 trade-off를 개선하려는 연구 프로그램

이다.

즉 현재 프로젝트의 중심 질문은 아래다.

- 어떤 intermediate feature를 보내야 downstream task 성능에 가장 중요한가?
- 현재 채널 상태에서 어떤 feature를 보내는 것이 가장 효율적인가?
- 두 기준을 결합하면 실제 누적 통신량(MB)을 줄이면서도 정확도와 robustness를 유지할 수 있는가?

## 3. 이 프로젝트의 핵심 구조

현재 프로젝트를 구성하는 핵심 블록은 아래처럼 보는 것이 가장 자연스럽다.

### A. 문제 설정

- 대상:
  - resource-constrained client + server 구조
- 학습 방식:
  - split learning / split federated learning
- 병목:
  - intermediate feature transmission

### B. semantic relevance 추정

- `VIB/KL` 기반으로 각 latent dimension의 semantic importance를 측정한다.
- 즉 무엇이 downstream classification에 본질적으로 중요한지를 본다.

### C. channel feasibility 추정

- 현재 `SNR` 값에 따라 전송 가능한 budget 또는 통과시킬 채널 마스크를 조절한다.
- 즉 지금 채널 상태에서 무엇을 보내는 것이 물리적으로 효율적인지를 본다.

### D. dual-mask support selection

- semantic mask와 channel-aware mask를 결합해 최종 전송 support를 정한다.
- 현재 프로젝트의 핵심 동작은 본질적으로 이 `dual masking` rule에 있다.

### E. evaluation contract

- accuracy만 보지 않는다.
- 항상 communication cost와 함께 본다.
- channel robustness까지 같이 본다.

즉 현재 프로젝트는 모델 하나보다,

- `semantic relevance estimation`
- `channel-aware support control`
- `communication-performance evaluation`

의 결합으로 정의되는 편이 맞다.

## 4. 이 프로젝트는 무엇이 아닌가

현재 프로젝트를 과장 없이 정의하려면, 아래와는 구분해야 한다.

- 단순 image semantic communication 연구
- 단순 wireless image reconstruction 연구
- 단순 split learning compression 연구
- 단순 VIB 적용 연구
- 단순 SNR adaptation 연구

이 프로젝트는 위 요소들을 각각 따로 새로 만들었다기보다,

- `split/federated intermediate feature communication`
- `semantic relevance`
- `channel awareness`

를 하나의 학습-통신 프레임으로 묶어 다루는 연구다.

## 5. 현재 기준으로 가장 좋은 프로젝트 정의 문장

### 짧은 정의

- 이 프로젝트는 split/federated learning에서 intermediate semantic feature 통신을 줄이기 위해, semantic relevance와 channel state를 함께 반영하는 adaptive support selection을 연구하는 semantic communication framework다.

### 논문용에 가까운 정의

- This project studies communication-efficient split/federated learning over wireless channels by selectively transmitting task-relevant intermediate semantic features according to both semantic importance and instantaneous channel conditions.

### 현재 연구 전체를 포괄하는 정의

- 본 프로젝트는 split/federated learning의 smashed data transmission 병목을 semantic communication 문제로 재정의하고, semantic importance 추정과 channel-aware masking을 결합한 adaptive slicing/support selection을 통해 accuracy-communication-robustness trade-off를 개선하는 것을 목표로 한다.

## 6. 논문 버전과 현재 프로젝트의 차이

현재 작업 중인 논문은 주로 아래를 중심으로 프로젝트를 정의한다.

- `CA-SSFL`
- `VIB-driven semantic masking`
- `SNR-driven channel masking`
- `dynamic slicing`

반면 현재 실제 프로젝트는 여기서 더 확장되었다.

- `base/refinement`
- `fixed-base variable-refinement`
- `support floor`
- `semidense`
- `importance-aware repetition`
- `server-side imputation`

이런 변형들을 실험하면서, 어떤 support budgeting rule이 가장 좋은 frontier를 만드는지 탐색하고 있다.

따라서 현재 프로젝트를 정의할 때는

- `CA-SSFL`을 출발점 또는 canonical base framework로 두고
- 그 위에서 여러 support-selection variant를 탐색하는 연구 프로그램

으로 설명하는 편이 가장 정확하다.

## 7. 지금 시점의 정리

지금 기준으로 내가 정의한 이 프로젝트는 아래와 같다.

- 출발점:
  - `CA-SSFL`
- 본질:
  - split/federated learning에서 intermediate feature 통신 병목을 semantic communication으로 해결하려는 프로젝트
- 핵심 메커니즘:
  - semantic importance 추정
  - channel-aware mask 조절
  - adaptive slicing / support selection
- 평가 기준:
  - accuracy
  - cumulative communication cost
  - channel robustness
- 현재 상태:
  - 논문 버전의 기본 프레임 위에서 여러 support budgeting 전략을 추가 탐색 중

## 관련 문서

- [PROJECT_NOVELTY.md](/home/sunmin/SFL_Semantic/docs/PROJECT_NOVELTY.md)
- [2026-04-11_project-novelty_prior-art-survey.md](/home/sunmin/SFL_Semantic/docs/literature/2026-04-11_project-novelty_prior-art-survey.md)
- [2026-04-11_method2_base-refinement_prior-art-survey.md](/home/sunmin/SFL_Semantic/docs/literature/2026-04-11_method2_base-refinement_prior-art-survey.md)
