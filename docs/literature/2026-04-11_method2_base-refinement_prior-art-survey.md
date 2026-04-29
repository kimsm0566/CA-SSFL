# method2 및 fixed-base variable-refinement 선행연구 조사

> 중요:
> 이 문서는 `method2` 계열의 선행연구 충돌만 정리한 문서다.
> 프로젝트 전체의 메인 노벨티는 `base/refinement`가 아니라
> [PROJECT_NOVELTY.md](/home/sunmin/SFL_Semantic/docs/PROJECT_NOVELTY.md)에 정리한
> `split/federated semantic transmission + VIB/SNR dual masking` 프레임이다.

## 조사 대상 고정

### A. 기존 고정형 `method2`

- 기준 실험:
  - `2026-04-11 08:19 KST`에 ledger에 기록된 `2026-04-11_07-10_v01_rayleigh-literature-four-method-suite`
- 주의:
  - `2026-04-10 22:54 KST` suite의 `method2`는 `latent mixing`이므로 이번 조사 대상이 아님
- 구현 요약:
  - 기존 `CA-SSFL` mask를 유지한 채
  - `support_scores`로 중요도를 정렬하고
  - 상위 `base_support_k=128`를 `base`
  - 그다음 상위 `refinement_support_k=128`를 `refinement`
  - 으로 고르는 `고정형 one-shot 2계층 support selection`

### B. 후속안 `fixed-base variable-refinement`

- 기준 문서:
  - [PLAN.md](/home/sunmin/SFL_Semantic/docs/experiments/2026-04-11/2026-04-11_08-40_v01_rayleigh-fixed-base-variable-refinement/PLAN.md)
  - [SPEC.md](/home/sunmin/SFL_Semantic/docs/experiments/2026-04-11/2026-04-11_08-40_v01_rayleigh-fixed-base-variable-refinement/SPEC.md)
- 구현 의도:
  - `base support`는 semantic core로 고정
  - `refinement support`는 channel condition에 따라 가변
- 현재 문서에 고정된 v1 규칙:
  - `K_base = 128`
  - `base source = KL mean`
  - `refinement source = SNR-conditioned channel score`
  - `K_ref_max = 128`
  - `K_ref = round(K_ref_max * snr_normalized)`
  - `snr_normalized = (current_snr_db - (-5)) / 20`
  - `K_ref`는 `[0, 128]`로 clamp
- 한 줄 요약:
  - `semantic importance로 고정 core를 확보`하고, `channel-aware gate로 추가 support 예산을 가변 배분`하려는 구조

## 먼저 확인된 기존 in-repo 문헌

- 이미 저장소에 기록된 가장 직접적인 유사 문헌:
  - [2019_kurka_successive-refinement-deep-jscc.md](./papers/2019_kurka_successive-refinement-deep-jscc.md)
- 이 문헌이 이미 말하는 것:
  - `base layer`와 `refinement layer`를 나눠 progressive하게 보내면 일부 정보 손상 시에도 기본 semantic quality를 방어할 수 있다는 점
- 1차 판정:
  - `base + refinement`라는 큰 발상 자체는 이미 prior art가 존재한다
  - 따라서 기존 고정형 `method2`든, 후속 `fixed-base variable-refinement`든 둘 다 개념 레벨 novelty를 크게 주장하기 어렵다

## 미기록 또는 재강조가 필요한 유사 문헌

### 1. Linear Progressive Coding for Semantic Communication using Deep Neural Networks

- 저자:
  - Eva Riherd, Raghu Mudumbai, Weiyu Xu
- 연도:
  - 2023
- 원문:
  - https://arxiv.org/abs/2309.15959
- 왜 유사한가:
  - semantic information을 coarse 단계와 추가 refinement 단계로 점진 전송한다
  - 전송 측정 수를 단계적으로 늘려 semantic fidelity를 보강한다
- 기존 고정형 `method2`와의 거리:
  - 가깝다
  - 이유: `coarse first, refine later`라는 핵심 framing이 거의 같다
- 후속 `fixed-base variable-refinement`와의 거리:
  - 중간 이상
  - 이유: refinement 예산을 단계적으로 늘린다는 점은 비슷하지만, 현재 후속안처럼 `KL로 고정 base`, `SNR-conditioned rule로 channel-adaptive refinement`를 분리하진 않는다

### 2. Semantic Multi-Resolution Communications

- 저자:
  - Matin Mortaheb, Mohammad A. Amir Khojastepour, Srimat T. Chakradhar, Sennur Ulukus
- 연도:
  - 2023
- 원문:
  - https://arxiv.org/abs/2308.11604
- 왜 유사한가:
  - hierarchical layers를 통해 semantic/resolution 정보를 점진적으로 제공한다
  - successive layers에서 semantic classifier precision이 progressively improved된다고 주장한다
- 기존 고정형 `method2`와의 거리:
  - 가깝다
  - 이유: semantic quality를 `계층`으로 쪼개는 점이 직접 겹친다
- 후속 `fixed-base variable-refinement`와의 거리:
  - 중간 이상
  - 이유: 계층성과 가변 정보량은 비슷하지만, channel-aware rule과 sparse support selector는 현재 계획안 쪽이 더 구체적이다

### 3. Semantic Communications with Explicit Semantic Base for Image Transmission

- 저자:
  - Yuan Zheng, Fengyu Wang, Wenjun Xu, Miao Pan, Ping Zhang
- 연도:
  - 2023
- 원문:
  - https://arxiv.org/abs/2308.06599
- 왜 유사한가:
  - explicit semantic base를 공유 지식으로 두고
  - 그 위에 residual information을 encode/decode하는 구조를 쓴다
  - 즉 `기본 semantic part + 추가 보정 part`라는 분해가 존재한다
- 기존 고정형 `method2`와의 거리:
  - 중간 이상
  - 이유: `base + residual refinement` 구조는 가깝지만, 현재 방법처럼 support index를 직접 다시 고르진 않는다
- 후속 `fixed-base variable-refinement`와의 거리:
  - 중간 이상
  - 이유: `fixed semantic base + extra residual`은 후속안의 `fixed core + variable extra info`와 더 잘 맞지만, 채널 적응 자체는 핵심 축이 아니다

### 4. Learned Image Transmission with Hierarchical Variational Autoencoder

- 저자:
  - Guangyi Zhang, Hanlei Li, Yunlong Cai, Qiyu Hu, Guanding Yu, Runmin Zhang
- 연도:
  - 2024
- 원문:
  - https://arxiv.org/abs/2408.16340
- 왜 유사한가:
  - hierarchical VAE로 multiple hierarchical representations를 만들고
  - representation hierarchy에 맞춰 transmission bandwidth를 가변 조절한다
- 기존 고정형 `method2`와의 거리:
  - 중간
  - 이유: 계층형 representation은 비슷하지만, 현재 고정형 `128+128`처럼 정적인 sparse selector는 아니다
- 후속 `fixed-base variable-refinement`와의 거리:
  - 높음
  - 이유: 후속안의 핵심인 `fixed core + variable budget`과 가장 잘 맞는 prior art 중 하나다

### 5. Feature Allocation for Semantic Communication with Space-Time Importance Awareness

- 저자:
  - Kequan Zhou, Guangyi Zhang, Yunlong Cai, Qiyu Hu, Guanding Yu, A. Lee Swindlehurst
- 연도:
  - 2024 preprint, 2025 `IEEE Transactions on Wireless Communications`
- 원문:
  - https://arxiv.org/abs/2401.14614
- 왜 유사한가:
  - importance evaluator로 feature 중요도를 먼저 구하고
  - channel prediction을 바탕으로 더 중요한 feature를 더 적절한 slot/subchannel에 배치한다
- 기존 고정형 `method2`와의 거리:
  - 중간
  - 이유: importance-first 철학은 같지만, `base/refinement` 계층보다는 allocation 문제다
- 후속 `fixed-base variable-refinement`와의 거리:
  - 높음
  - 이유: 후속안이 하려는 `semantic importance + channel state를 분리 사용`하는 사고와 가장 직접적으로 맞닿아 있다

### 6. Hybrid Semantic-Complementary Transmission for High-Fidelity Image Reconstruction

- 저자:
  - Hyelin Nam, Jihong Park, Jinho Choi, Seong-Lyun Kim
- 연도:
  - 2025
- 원문:
  - https://arxiv.org/abs/2507.17196
- 왜 유사한가:
  - 고정된 semantic representation(`SR`)에 더해
  - residual image-specific complementary representation(`CR`)를 추가로 보낸다
  - 초록이 `fixed load of SR + flexible load of CR`를 명시한다
- 기존 고정형 `method2`와의 거리:
  - 중간 이상
  - 이유: `core + extra detail` 구조는 가깝지만, 현재 고정형 `method2`는 fixed/fixed라 flexible complement까지는 아니다
- 후속 `fixed-base variable-refinement`와의 거리:
  - 매우 높음
  - 이유: 후속안의 문구인 `fixed base + variable refinement`와 구조적 표현이 거의 정면으로 겹친다

### 7. Diffusion Based Scalable Semantic Communication Framework For Image Compression And Transmission

- 저자:
  - Namesh Pannigala Gamage, Thanuj Fernando, Anil Fernando
- 연도:
  - 2025 IEEE ICIPW, 2026 공개본
- 원문:
  - https://strathprints.strath.ac.uk/95677/1/Gamage-etal-2025-Diffusion-based-scalable-semantic-communication-framework.pdf
  - DOI: https://doi.org/10.1109/icipw68931.2025.11385841
- 왜 유사한가:
  - dynamic weighting으로 중요한 semantic content를 우선시한다
  - bandwidth와 latency 제약에 맞춰 semantic granularity를 조절한다
  - multiple scalable layers를 통해 detail을 progressive하게 refine한다
- 기존 고정형 `method2`와의 거리:
  - 중간
  - 이유: 중요도 기반 전송은 가깝지만, 현재 고정형은 SNR에 따라 refinement 양이 변하지 않는다
- 후속 `fixed-base variable-refinement`와의 거리:
  - 높음
  - 이유: `중요도 기반 + network-condition adaptive granularity`라는 점이 후속안과 직접 맞물린다

### 8. Object-Attribute-Relation Model Driven Adaptive Hierarchical Transmission for Multimodal Semantic Communication

- 저자:
  - Chenxing Li, Yiping Duan, Han Jiao, Xiaoming Tao, Weiyao Lin, Mingquan Lu
- 연도:
  - 2026
- 원문:
  - https://arxiv.org/abs/2604.07859
- 왜 유사한가:
  - adaptive hierarchy를 두고
  - semantic priority에 따라 bandwidth를 동적으로 배분하며
  - deep fading에서도 foundational object anchors를 우선 보존한다고 명시한다
- 기존 고정형 `method2`와의 거리:
  - 중간
  - 이유: `foundational anchor 보존`은 가깝지만, multimodal topological graph 기반이라 구현 층위가 많이 다르다
- 후속 `fixed-base variable-refinement`와의 거리:
  - 높음
  - 이유: `foundation은 반드시 지키고, 추가 자원은 채널/대역폭 상태에 맞게 가변 배정`한다는 철학이 거의 동일하다

## 후속안 기준으로 다시 정리한 핵심 비교

### 기존 고정형 `method2`와 가장 직접적으로 겹치는 축

- `2019 Kurka`
  - `base layer + refinement layer`
- `2023 Riherd`
  - `coarse semantic first, extra semantic later`
- `2023 Mortaheb`
  - `semantic multi-resolution layering`
- `2023 Zheng`
  - `semantic base + residual`

### 후속 `fixed-base variable-refinement`와 가장 직접적으로 겹치는 축

- `2024 Zhang`
  - hierarchical representation + dynamic transmission bandwidth
- `2024/2025 Zhou`
  - semantic importance + channel-aware resource allocation
- `2025 Nam`
  - fixed semantic core + flexible complementary payload
- `2025 Gamage`
  - scalable semantic granularity + dynamic weighting under network constraints
- `2026 Li`
  - foundational semantic anchors + bandwidth-adaptive hierarchy

## 종합 판단

### 1. 기존 고정형 `method2`

- 결론:
  - `base + refinement` 자체는 이미 prior art가 있다
- 다만 남는 차별점:
  - `CA-SSFL` sparse mask 내부에서
  - `VIB KL + SNR-conditioned channel mask`를 이용해
  - `one-shot support reordering`으로 번역했다는 점

### 2. 후속 `fixed-base variable-refinement`

- 결론:
  - 기존 고정형 `method2`보다 prior art와 더 직접적으로 충돌한다
- 이유:
  - 최근 문헌에는 이미
    - `fixed semantic core + flexible complement`
    - `hierarchical representation + dynamic bandwidth`
    - `importance-aware + channel-aware allocation`
  - 이 세 축이 모두 존재한다
- 따라서 이 후속안을 `새로운 큰 아이디어`로 포지셔닝하는 것은 위험하다

## 현재 기준 신규성 위험도 재평가

### 기존 고정형 `method2`

- 매우 가까움:
  - `2019 Kurka`
  - `2023 Riherd`
  - `2023 Mortaheb`
- 부분적으로 가까움:
  - `2023 Zheng`
  - `2024/2025 Zhou`

### 후속 `fixed-base variable-refinement`

- 매우 가까움:
  - `2025 Nam`
  - `2024 Zhang`
  - `2024/2025 Zhou`
  - `2026 Li`
- 부분적으로 가까움:
  - `2023 Zheng`
  - `2025 Gamage`
  - `2019 Kurka`

## 실무 메모

- 만약 이 방향을 계속 밀 거라면, novelty 중심은 아래처럼 더 좁혀야 한다.
- 피해야 할 포지셔닝:
  - `fixed base + variable refinement` 자체를 처음 제안했다
  - 계층형 semantic transmission을 처음 제안했다
  - semantic core와 complement 분리를 처음 제안했다
- 상대적으로 안전한 포지셔닝:
  - `KL-defined fixed semantic core + SNR-conditioned variable refinement inside sparse CA-SSFL masking`
  - `one-shot sparse support budgeting for Rayleigh-robust split semantic learning`
  - `importance-source / channel-adaptation-source role separation in sparse split semantic transmission`
- 즉 novelty의 중심을
  - `base/refinement`라는 큰 구조가 아니라
  - `현재 SSFL/CA-SSFL 파이프라인에서의 scoring rule, support budgeting rule, comm-aware validation`
  - 로 옮겨야 한다

## 지금 시점의 한 줄 결론

- 기존 고정형 `method2`는 `계층형 support 선택의 in-repo 번역` 정도로 보는 편이 맞다
- 후속 `fixed-base variable-refinement`는 문헌과 더 직접적으로 겹치므로, 만약 구현한다면 `새 아이디어`보다 `문헌 아이디어를 sparse split semantic learning에 맞게 엄밀히 번역한 변형`으로 서술하는 것이 안전하다

## 참고 원문 목록

- Kurka and Gunduz, 2019:
  - https://arxiv.org/abs/1903.06333
- Riherd et al., 2023:
  - https://arxiv.org/abs/2309.15959
- Mortaheb et al., 2023:
  - https://arxiv.org/abs/2308.11604
- Zheng et al., 2023:
  - https://arxiv.org/abs/2308.06599
- Zhang et al., 2024:
  - https://arxiv.org/abs/2408.16340
- Zhou et al., 2024:
  - https://arxiv.org/abs/2401.14614
- Nam et al., 2025:
  - https://arxiv.org/abs/2507.17196
- Gamage et al., 2025:
  - https://doi.org/10.1109/icipw68931.2025.11385841
- Li et al., 2026:
  - https://arxiv.org/abs/2604.07859
