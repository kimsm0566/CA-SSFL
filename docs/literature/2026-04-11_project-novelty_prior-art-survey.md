# 프로젝트 노벨티 기준 선행연구 조사

## 조사 목적

이 문서는 `method2` 같은 파생 기법이 아니라, 현재 프로젝트 전체에서 가장 크게 주장하려는 노벨티

- `split / federated learning`
- `semantic intermediate representation communication reduction`
- `VIB-based semantic mask`
- `SNR-conditioned channel-aware mask`
- `dual masking support selection`

의 관점에서 선행연구를 다시 정리한 문서다.

관련 프로젝트 노벨티 문서:

- [PROJECT_NOVELTY.md](/home/sunmin/SFL_Semantic/docs/PROJECT_NOVELTY.md)

## 현재 코드/설명 기준 문제 설정

현재 프로젝트는 일반적인 이미지 재구성용 semantic communication이 아니라,

- split learning 또는 split federated learning 구조 안에서
- 클라이언트가 서버로 보내는 intermediate feature 또는 smashed data의 통신량을 줄이면서
- accuracy를 유지하거나 개선하고
- AWGN / Rayleigh 및 SNR 변화에 대한 robustness도 같이 보는

학습-통신 결합 문제를 다룬다.

현재 설명 기준 핵심 rule은 아래처럼 요약된다.

- `VIB/KL`로 semantic importance를 추정
- `SNR` 값으로 channel-aware mask를 조절
- `mask = semantic_mask * channel_mask`

주의:

- 코드 변수 이름에는 `film_mask`, `film_max_t`, `film_min_t`, `snr_to_film` 같은 과거 명칭이 남아 있다.
- 하지만 현재 claim-level 설명에서는 이를 `FiLM novelty`로 잡기보다, `SNR-conditioned channel mask`로 서술하는 편이 맞다.

## 조사 기준

이번 조사에서는 비슷한 분야를 아래 네 그룹으로 나눴다.

1. `split / split federated learning`에서 통신량을 줄이는 연구
2. `semantic communication + federated/distributed setting` 연구
3. `task-oriented / semantic edge inference`에서 `IB/VIB`를 쓰는 연구
4. `channel-aware masking / dynamic channel adaptation` 연구

## 가장 가까운 논문들

### 1. Semantic Communication-Enhanced Split Federated Learning for Vehicular Networks: Architecture, Challenges, and Case Study

- 저자:
  - Lu Yu, Zheng Chang, Ying-Chang Liang
- 연도:
  - 2026-03-05 제출, IEEE Communications Magazine 게재 예정
- 원문:
  - https://arxiv.org/abs/2603.04936
- 왜 중요한가:
  - `semantic communication + split federated learning`을 직접 결합한 현재 기준 최인접 선행연구다
  - 초록에서 `high-dimensional intermediate features`가 SFL의 통신 병목이라고 명시한다
  - `SCM`으로 task-relevant semantic information만 uplink에 보내고, `NSM`으로 channel condition에 따라 semantic compression rate를 조절한다고 적는다
- 우리 프로젝트와 겹치는 점:
  - split federated learning
  - intermediate feature 통신 병목
  - semantic communication로 uplink 통신량 절감
  - channel 상태에 따른 적응형 통신
- 우리 프로젝트와 다른 점:
  - pre-trained / frozen semantic communication module 중심
  - per-dimension `VIB` importance mask를 전면에 두지 않는다
  - `semantic mask * channel mask` 형태의 explicit dual masking을 전면 claim으로 내세우지 않는다
- 신규성 리스크:
  - 매우 높음
  - 이유: `semantic communication을 split federated learning에 적용했다`는 큰 문장은 더 이상 단독 novelty가 아니다

### 2. Model Partition and Resource Allocation for Split Learning in Vehicular Edge Networks

- 저자:
  - Lu Yu, Zheng Chang, Yunjian Jia, Geyong Min
- 연도:
  - 2024-11-11
- 원문:
  - https://arxiv.org/abs/2411.06773
- 왜 중요한가:
  - `U-SFL`에서 semantic-aware auto-encoder로 transmitted data dimension을 줄이고, DRL로 split point / resource allocation을 조절한다
- 우리 프로젝트와 겹치는 점:
  - split federated learning 계열
  - intermediate representation 통신량 절감
  - semantic-aware compression 사용
- 우리 프로젝트와 다른 점:
  - autoencoder 기반 dense compression
  - `VIB` 기반 importance mask 없음
  - `SNR-conditioned dual masking` 없음
- 신규성 리스크:
  - 높음
  - 이유: `semantic-aware compression for U-SFL`은 이미 존재한다

### 3. Communication-Efficient Split Learning via Adaptive Feature-Wise Compression

- 저자:
  - Yongjeong Oh, Jaeho Lee, Christopher G. Brinton, Yo-Seb Jeon
- 연도:
  - 2023
- 원문:
  - https://arxiv.org/abs/2307.10805
- 왜 중요한가:
  - split learning의 intermediate feature / gradient 통신량을 줄이기 위해 adaptive feature-wise dropout과 adaptive quantization을 사용한다
- 우리 프로젝트와 겹치는 점:
  - split learning에서 smashed data 통신량 절감
  - per-feature adaptive selection
- 우리 프로젝트와 다른 점:
  - semantic communication 아님
  - channel-aware mask 아님
  - `VIB`나 task-relevant semantic sufficiency를 전면에 두지 않음
- 신규성 리스크:
  - 중간
  - 이유: `split learning communication reduction` 자체는 이미 오래된 문제다

### 4. Communication and Computation Reduction for Split Learning using Asynchronous Training

- 저자:
  - Xing Chen, Jingtao Li, Chaitali Chakrabarti
- 연도:
  - 2021
- 원문:
  - https://arxiv.org/abs/2107.09786
- 왜 중요한가:
  - split learning에서 activation / gradient 전송을 매 epoch 선택적으로 줄여 통신량을 절감한다
- 우리 프로젝트와 겹치는 점:
  - split learning 통신 비용이 핵심 병목이라는 인식
- 우리 프로젝트와 다른 점:
  - semantic communication 아님
  - intermediate feature의 semantic relevance 추정 없음
  - channel/SNR 적응 없음
- 신규성 리스크:
  - 중간
  - 이유: split learning 통신 절감 프레임의 고전적 선행연구로 봐야 한다

### 5. SplitMAC: Wireless Split Learning over Multiple Access Channels

- 저자:
  - Seonjung Kim, Yongjeong Oh, Yo-Seb Jeon
- 연도:
  - 2023
- 원문:
  - https://arxiv.org/abs/2311.02405
- 왜 중요한가:
  - split learning을 실제 wireless MAC / fading 환경에 놓고 SNR에 따른 grouping과 latency를 최적화한다
- 우리 프로젝트와 겹치는 점:
  - split learning + wireless/SNR/fading
  - communication-aware system design
- 우리 프로젝트와 다른 점:
  - semantic communication 아님
  - feature selection보다 transmission scheduling에 가깝다
  - `VIB` 없음
- 신규성 리스크:
  - 중간
  - 이유: `split learning + wireless channel condition` 자체는 이미 다뤄지고 있다

### 6. Communication-Efficient Framework for Distributed Image Semantic Wireless Transmission

- 저자:
  - Bingyan Xie, Yongpeng Wu, Yuxuan Shi, Derrick Wing Kwan Ng, Wenjun Zhang
- 연도:
  - 2023
- 원문:
  - https://arxiv.org/abs/2308.03713
- 왜 중요한가:
  - federated learning 기반 semantic communication framework를 제안하고 CSI-based MIMO transmission module까지 포함한다
- 우리 프로젝트와 겹치는 점:
  - federated/distributed setting
  - semantic communication
  - channel state를 고려한 transmission
- 우리 프로젝트와 다른 점:
  - image semantic wireless transmission 문제
  - 학습 중 intermediate feature transmission 문제는 아님
  - split learning 구조가 아님
- 신규성 리스크:
  - 중간 이상
  - 이유: `federated + semantic communication + channel awareness` 조합의 상위 프레임은 이미 존재한다

### 7. Learning Task-Oriented Communication for Edge Inference: An Information Bottleneck Approach

- 저자:
  - Jiawei Shao, Yuyi Mao, Jun Zhang
- 연도:
  - 2021
- 원문:
  - https://arxiv.org/abs/2102.04170
- 왜 중요한가:
  - edge device가 feature vector를 서버로 보내는 task-oriented communication setting에서
  - `VIB`를 사용해 informative and compact representation을 만들고
  - dynamic channel conditions에서 activated dimension을 가변 조절한다
- 우리 프로젝트와 겹치는 점:
  - feature transmission
  - `VIB`
  - dynamic channel adaptation
  - communication-performance trade-off
- 우리 프로젝트와 다른 점:
  - split/federated learning training loop가 아니다
  - multi-client aggregation, seeds, split/federated reproducibility 문제를 다루지 않는다
  - explicit `dual masking`보다는 variable-length encoding 관점이다
- 신규성 리스크:
  - 높음
  - 이유: `VIB + dynamic channel-aware feature transmission` 조합은 이미 매우 가깝게 존재한다

### 8. Task-Oriented Communication for Multi-Device Cooperative Edge Inference

- 저자:
  - Jiawei Shao, Yuyi Mao, Jun Zhang
- 연도:
  - 2021
- 원문:
  - https://arxiv.org/abs/2109.00172
- 왜 중요한가:
  - distributed feature encoding과 distributed information bottleneck를 사용해 다중 디바이스 edge inference의 rate-relevance trade-off를 다룬다
- 우리 프로젝트와 겹치는 점:
  - multi-device distributed feature communication
  - IB 기반 task-relevant feature selection
- 우리 프로젝트와 다른 점:
  - split/federated learning 아님
  - wireless training loop rather than collaborative inference 아님
- 신규성 리스크:
  - 중간 이상
  - 이유: distributed feature communication + IB 축은 이미 존재한다

### 9. Task-Agnostic Semantic Communications Relying on Information Bottleneck and Federated Meta-Learning

- 저자:
  - Hao Wei, Wen Wang, Wanli Ni, Wenjun Xu, Yongming Huang, Dusit Niyato, Ping Zhang
- 연도:
  - 2025
- 원문:
  - https://arxiv.org/abs/2504.21723
- 왜 중요한가:
  - IB 기반으로 minimal and sufficient information을 학습하고
  - dynamic channel conditions 아래 adaptive semantic feature transmission을 하며
  - federated meta-learning으로 학습한다
- 우리 프로젝트와 겹치는 점:
  - IB
  - federated training flavor
  - dynamic channel-aware adaptive transmission
- 우리 프로젝트와 다른 점:
  - split learning 아님
  - intermediate smashed data 통신을 줄이는 문제가 아님
- 신규성 리스크:
  - 중간 이상
  - 이유: `IB + federated + dynamic channel adaptation` 프레임은 이미 존재한다

### 10. Robust Image Semantic Coding with Learnable CSI Fusion Masking over MIMO Fading Channels

- 저자:
  - Bingyan Xie, Yongpeng Wu, Yuxuan Shi, Wenjun Zhang, Shuguang Cui, Merouane Debbah
- 연도:
  - 2024
- 원문:
  - https://arxiv.org/abs/2406.07389
- 왜 중요한가:
  - source state와 channel state를 함께 쓰는 learnable masking을 통해 fading robustness를 높인다
- 우리 프로젝트와 겹치는 점:
  - source-aware + channel-aware masking
  - fading robustness
  - mask ratio/adaptation
- 우리 프로젝트와 다른 점:
  - MIMO image semantic coding
  - split/federated training 아님
  - `VIB` hard threshold mask가 아님
- 신규성 리스크:
  - 중간 이상
  - 이유: `source-aware + channel-aware mask`라는 큰 철학은 이미 있다

### 11. Robust Information Bottleneck for Task-Oriented Communication with Digital Modulation

- 저자:
  - Songjie Xie, Shuai Ma, Ming Ding, Yuanming Shi, Mingjian Tang, Youlong Wu
- 연도:
  - 2022
- 원문:
  - https://arxiv.org/abs/2209.10382
- 왜 중요한가:
  - channel variation 아래 robust encoding을 위해 information bottleneck 계열 robust objective를 도입한다
- 우리 프로젝트와 겹치는 점:
  - task-oriented communication
  - information bottleneck
  - channel robustness
- 우리 프로젝트와 다른 점:
  - split/federated setting 아님
  - intermediate feature sparsification rule이 핵심은 아님
- 신규성 리스크:
  - 중간
  - 이유: `IB를 이용한 channel-robust task communication`은 이미 알려진 축이다

## 정리: 무엇이 이미 있고, 무엇이 남는가

### 이미 있는 것

- split learning 통신량 절감
- split federated learning에 semantic compression/semantic communication 도입
- federated semantic communication
- VIB 또는 IB 기반 feature compactness 유도
- dynamic channel condition에 따른 adaptive transmission
- source-aware + channel-aware masking

### 그래서 더 이상 메인 novelty로 쓰기 어려운 것

- semantic communication을 썼다
- split learning 통신량을 줄였다
- federated learning을 썼다
- VIB를 썼다
- channel-aware mask를 썼다
- SNR에 따라 active budget을 조절했다

## 현재 기준으로 남는 방어 가능한 프로젝트 노벨티

문헌을 다 합치고 나면, 현재 프로젝트가 상대적으로 방어 가능하게 주장할 수 있는 축은 아래로 좁혀진다.

1. `split / federated learning`의 실제 intermediate feature transmission 문제를 대상으로 한다.
2. semantic communication 관점을 학습용 smashed data support selection에 직접 연결한다.
3. `VIB semantic mask`와 `SNR-conditioned channel mask`를 결합한 explicit `dual masking` rule을 쓴다.
4. 이 rule을 실제 `accuracy vs cumulative MB` 기준으로 평가한다.
5. AWGN / Rayleigh / multi-SNR / seed 비교라는 연구 계약 안에서 판단한다.

즉, 가장 안전한 claim은 아래와 같다.

- 새 통신 패러다임 자체를 제안했다기보다,
- 기존의 `semantic communication`, `IB/VIB`, `channel adaptation`, `split/federated learning`을
- intermediate feature transmission 절감이라는 구체 문제에 맞게
- `dual masking support selection` 형태로 결합하고
- 실제 communication-performance frontier로 검증한다.

## 프로젝트용 한 줄 결론

현재 프로젝트의 메인 노벨티는

- `semantic communication in split/federated training`
- `VIB-based semantic masking`
- `SNR-conditioned channel-aware masking`
- `explicit dual-mask support selection for smashed data`

의 결합에 있다.

반대로 아래는 보조 novelty 또는 파생 아이디어로 두는 것이 안전하다.

- `base/refinement`
- `fixed-base variable-refinement`
- `semidense`
- `support floor`
- `importance repetition`

## 참고 원문 목록

- Chen et al., 2021:
  - https://arxiv.org/abs/2107.09786
- Shao et al., 2021a:
  - https://arxiv.org/abs/2102.04170
- Shao et al., 2021b:
  - https://arxiv.org/abs/2109.00172
- Xie et al., 2022:
  - https://arxiv.org/abs/2209.10382
- Oh et al., 2023:
  - https://arxiv.org/abs/2307.10805
- Xie et al., 2023:
  - https://arxiv.org/abs/2308.03713
- Kim et al., 2023:
  - https://arxiv.org/abs/2311.02405
- Xie et al., 2024:
  - https://arxiv.org/abs/2406.07389
- Yu et al., 2024:
  - https://arxiv.org/abs/2411.06773
- Wei et al., 2025:
  - https://arxiv.org/abs/2504.21723
- Yu et al., 2026:
  - https://arxiv.org/abs/2603.04936
