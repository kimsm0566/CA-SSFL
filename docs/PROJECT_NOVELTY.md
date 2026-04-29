# Project Novelty

이 문서는 현재 프로젝트에서 가장 방어 가능한 노벨티가 무엇인지 정리하는 작업 문서다.

목표는 과장된 claim을 쓰는 것이 아니라, 문헌과 현재 코드 기준으로 **무엇을 메인 노벨티로 잡아야 안전한지**를 명확히 하는 것이다.

관련 선행연구 조사:

- [2026-04-11_project-novelty_prior-art-survey.md](/home/sunmin/SFL_Semantic/docs/literature/2026-04-11_project-novelty_prior-art-survey.md)

## 문서 역할

- 이 문서는 [PROJECT_DEFINITION.md](/home/sunmin/SFL_Semantic/docs/PROJECT_DEFINITION.md)에 정의된 프로젝트 범위를 전제로 한다.
- 여기서의 초점은 "이 프로젝트가 무엇인가"가 아니라, "무엇을 방어 가능한 novelty로 말할 수 있는가"다.
- 따라서 프로젝트 범위, 문제 설정, 메커니즘 설명은 가능하면 정의 문서를 우선 참조하고, 이 문서는 선행연구 대비 남는 주장과 피해야 할 과장을 정리한다.

## 한 줄 정리

이 프로젝트의 가장 큰 노벨티 후보는 `base/refinement` 자체가 아니라,

- `split / federated learning`의 중간 semantic feature 통신을 줄이기 위해
- semantic communication을 도입하고
- 그 전송 집합을 `VIB 기반 semantic importance`와 `SNR 값으로 조절되는 channel-aware mask`의 `dual masking`으로 결정한다는 점

에 있다.

## 무엇이 메인 노벨티가 아닌가

다음은 프로젝트의 보조 설계이거나, 이미 기존 문헌과 직접 겹치는 축이다.

- `base + refinement` 계층 아이디어 자체
- `fixed base + variable refinement`라는 큰 framing 자체
- VIB 자체
- channel-aware masking 자체
- semantic communication 자체

즉, 각 부품을 따로 떼면 대부분 선행연구가 있다.  
프로젝트의 핵심은 **이 부품들을 split/federated semantic transmission 문제에 맞게 결합한 방식**에 있다.

## 현재 코드 기준으로 보는 핵심 노벨티

### 1. 문제 설정의 차이

이 프로젝트는 일반적인 이미지 semantic transmission이나 reconstruction 문제가 아니라,

- split learning / federated learning 구조 안에서
- 클라이언트와 서버 사이에 오가는 **중간 semantic feature**
- 또는 semantic activation 수준의 payload

를 줄이면서 정확도를 유지하려는 문제를 다룬다.

즉 노벨티의 첫 번째 축은 **semantic communication을 학습용 중간 표현 통신 절감 문제에 적용한 점**이다.

관련 코드 경로:

- [src/utils/trainer.py](/home/sunmin/SFL_Semantic/src/utils/trainer.py)
- [src/utils/client.py](/home/sunmin/SFL_Semantic/src/utils/client.py)
- [src/run_exp_main.py](/home/sunmin/SFL_Semantic/src/run_exp_main.py)

### 2. Dual Masking 구조

현재 코드에서 semantic feature 선택은 사실상 두 축으로 이루어진다.

- `VIB/KL` 기반 semantic mask
  - 무엇이 task 관점에서 본질적으로 중요한가
- `SNR-conditioned` channel mask
  - 현재 채널 상태에서 무엇을 안정적으로 보낼 수 있는가

그리고 실제 전송 support는 이 둘의 결합으로 결정된다.

문서상 표현으로는:

- `vib_mask`
- `chan_mask`
- `mask = vib_mask * chan_mask`

라는 구조다.

이 점이 프로젝트의 가장 중요한 기술적 노벨티 축이다.  
즉 핵심은 `dual masking`이다.

주의:

- 현재 코드에는 과거 실험 이름의 흔적으로 `film_mask`, `film_max_t`, `film_min_t`, `snr_to_film` 같은 명칭이 남아 있다.
- 하지만 claim-level 서술에서는 이를 `FiLM` 메커니즘의 novelty로 밀기보다, **SNR 값으로 조절되는 channel-aware mask**로 설명하는 편이 현재 프로젝트 설명과 더 잘 맞는다.

관련 코드 경로:

- [src/models/model.py](/home/sunmin/SFL_Semantic/src/models/model.py)
- [src/utils/trainer.py](/home/sunmin/SFL_Semantic/src/utils/trainer.py)
- [src/utils/option.py](/home/sunmin/SFL_Semantic/src/utils/option.py)

### 3. 역할 분리의 명확성

현재 프로젝트에서 각 모듈의 역할은 비교적 분명하다.

- `VIB`:
  - semantic compression
  - KL-based importance estimation
  - 불필요한 latent 정보 제거
- `SNR-conditioned channel mask`:
  - 현재 SNR 또는 채널 조건 반영
  - 채널 친화적인 전송 차원 선택
- 최종 support rule:
  - semantic importance와 channel reliability를 동시에 만족하는 차원만 남김

이 관점에서 보면 이 프로젝트는 단순 pruning이나 단순 fading-aware scheduling이 아니라,
**semantic relevance와 channel feasibility를 분리해 동시에 반영하는 support selection rule**을 갖는다.

### 4. 평가 계약의 차이

이 프로젝트는 단순 reconstruction metric이 아니라,

- 최종 accuracy
- cumulative communication cost in MB
- multi-SNR behavior
- Rayleigh / AWGN robustness

를 함께 본다.

즉 노벨티는 모델 구조만이 아니라,
**실제 communication-performance frontier 기준으로 split/federated semantic learning을 평가하는 방식**에도 있다.

관련 문서:

- [docs/evals/EVAL_PROTOCOL.md](/home/sunmin/SFL_Semantic/docs/evals/EVAL_PROTOCOL.md)
- [docs/experiments/RESULTS_LEDGER.md](/home/sunmin/SFL_Semantic/docs/experiments/RESULTS_LEDGER.md)

## 문헌과 비교했을 때 방어 가능한 주장

### 문헌에 이미 있는 것

- `VIB`로 latent 중요도를 조절하는 아이디어
- `CSI` 또는 channel-aware masking으로 fading에 대응하는 아이디어
- `SNR` 또는 channel quality에 따라 활성 차원 수를 조절하는 아이디어
- `base/refinement` 또는 progressive semantic transmission 아이디어

### 문헌 대비 프로젝트 쪽에서 남는 주장

문헌 조사 기준으로 현재 가장 방어 가능한 주장은 아래와 같다.

1. semantic communication을 `image transmission`이 아니라 `split/federated learning`의 중간 표현 통신 절감 문제에 적용했다.
2. 전송 support를 `semantic importance(VIB)`와 `channel-aware feasibility(SNR-conditioned mask)`의 dual masking으로 결정한다.
3. 이 구조를 실제 `MB` 통신량과 accuracy trade-off로 평가한다.

즉, 프로젝트의 노벨티는 **새 부품 1개**가 아니라
**문제 설정 + masking rule + evaluation contract의 결합**에 있다.

## `base/refinement`의 위치

`base/refinement`는 메인 노벨티가 아니라,
기존 dual masking 기반 semantic selection 위에 얹는 **후속 support budgeting 전략**으로 보는 편이 맞다.

따라서 논리 순서는 아래가 더 안전하다.

1. 메인 프레임:
   - split/federated semantic transmission reduction
   - VIB + SNR-conditioned channel-aware dual masking
2. 그 위의 파생 전략:
   - support floor
   - semidense
   - repetition
   - base/refinement
   - fixed-base variable-refinement

즉 `method2` 계열은 메인 노벨티가 아니라 **기존 프로젝트 프레임 위에서 탐색하는 ablation family**로 두는 게 적절하다.

## 권장 서술 문구

### 짧은 버전

- 본 프로젝트의 핵심 아이디어는 split/federated learning에서 중간 semantic feature 통신을 줄이기 위해, VIB 기반 semantic importance와 SNR-conditioned channel mask를 결합한 dual masking semantic communication을 사용한다는 점이다.

### 조금 더 안전한 버전

- 본 프로젝트는 semantic communication을 split/federated learning의 intermediate feature transmission 문제로 가져오고, VIB 기반 importance mask와 SNR 값으로 조절되는 channel-aware mask의 결합으로 실제 전송 support를 결정하는 방식에 초점을 둔다.

### 피해야 할 버전

- `base/refinement`를 처음 제안했다
- channel-aware semantic masking을 처음 제안했다
- VIB semantic communication을 처음 제안했다

## 현재 시점의 프로젝트용 결론

현재 프로젝트에서 가장 강하게 밀어야 하는 노벨티는 아래다.

- `Split/Federated learning setting`
- `semantic intermediate representation communication reduction`
- `VIB-based semantic mask + SNR-conditioned channel mask`
- `dual masking support selection`
- `actual communication-performance evaluation under channel variation`

반대로 `base/refinement`는 이 메인 노벨티 위에서 실험하는 설계 변형으로 두는 것이 맞다.
