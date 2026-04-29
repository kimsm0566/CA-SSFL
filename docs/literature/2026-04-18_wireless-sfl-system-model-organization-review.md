# 무선 환경 SFL/SL 논문의 System Model 구성 방식 메모

## 목적

- 우리 논문의 `II. System Model`을 어떻게 구성하는 것이 자연스러운지 판단하기 위해,
- 무선 환경을 고려한 SFL/SL 계열 선행연구에서 `System Model` 또는 그에 준하는 섹션이 어떤 역할을 맡는지 비교했다.

## 확인한 논문

### 1. SplitMAC: Wireless Split Learning over Multiple Access Channels

- 저자: Seonjung Kim, Yongjeong Oh, Yo-Seb Jeon
- 출처:
  - arXiv abs: https://arxiv.org/abs/2311.02405
  - PDF: https://arxiv.org/pdf/2311.02405.pdf
- 관련 섹션 구조:
  - `II. System Model`
  - `III. SplitMAC: Split Learning over Multiple Access Channels`
  - `IV. Optimization of Device Grouping for SplitMAC`
- 관찰:
  - `System Model`에서는 무선 SL 시나리오, AP/디바이스, 데이터셋 분포, global loss 정의, 기존 SL 학습 접근 요약만 둔다.
  - 제안 내용인 `SplitMAC`, grouping, training procedure, latency analysis는 다음 섹션부터 시작한다.
  - 즉, `System Model`은 foundation이고 novelty는 별도 섹션에서 연다.

### 2. Communication-Efficient Split Learning via Adaptive Feature-Wise Compression

- 저자: Yongjeong Oh, Jaeho Lee, Christopher G. Brinton, Yo-Seb Jeon
- 출처:
  - arXiv abs: https://arxiv.org/abs/2307.10805
  - PDF: https://arxiv.org/pdf/2307.10805.pdf
- 관련 섹션 구조:
  - `III. System Model`
  - `III-A. A Typical SL Framework`
  - `III-B. Key Challenge in SL`
  - `IV. Motivation of SplitFC`
  - `V-VI. Proposed compression strategies`
- 관찰:
  - `System Model`에는 전형적 SL setup, global/local loss, round-robin training procedure, communication bottleneck만 들어간다.
  - 제안 방법의 이름 `SplitFC`는 다음 섹션(`IV`)에서 본격적으로 등장한다.
  - `generic framework + key challenge`를 먼저 두고, 방법론은 뒤에서 열어 reviewer가 novelty를 명확히 인식하게 한다.

### 3. Model Partition and Resource Allocation for Split Learning in Vehicular Edge Networks

- 저자: Lu Yu, Zheng Chang, Yunjian Jia, Geyong Min
- 출처:
  - arXiv abs: https://arxiv.org/abs/2411.06773
  - PDF: https://arxiv.org/pdf/2411.06773.pdf
- 관련 섹션 구조:
  - `III. System model`
  - `III-A. Vehicular Network Architecture`
  - `III-B. U-shaped Split Federated Learning Model`
  - `III-C. Semantic-aware Communication for U-SFL`
  - `IV. Computation and Communication Modeling with Problem Formulation`
- 관찰:
  - 이 논문은 `System model` 아래에 네트워크 아키텍처뿐 아니라 `U-SFL model`, `semantic-aware communication`까지 넣는다.
  - 즉 system setup과 proposed architecture가 한 섹션에 섞여 있다.
  - reviewer 입장에서는 기여가 `System model`에 묻히는 인상을 줄 수 있는 구조다.

### 4. Semantic Communication-Enhanced Split Federated Learning for Vehicular Networks: Architecture, Challenges, and Case Study

- 저자: Lu Yu, Zheng Chang, Ying-Chang Liang
- 출처:
  - arXiv abs: https://arxiv.org/abs/2603.04936
  - PDF: https://arxiv.org/pdf/2603.04936.pdf
- 관련 섹션 구조:
  - `II. Distributed Learning and Semantic Communications for VEI: Convergence and Challenges`
  - `III. SC-USFL: Semantic-Enhanced and Adaptive U-Shaped Split Federated Learning`
  - `IV. Performance Evaluation`
- 관찰:
  - 이 논문은 아예 `System Model`이라는 이름 대신, 먼저 distributed learning evolution / communication bottleneck / semantic communication background를 정리한다.
  - 그 다음 섹션에서 `SC-USFL` case study를 여는 방식이다.
  - 즉, 배경/문제정의와 제안 프레임워크를 강하게 분리한다.

## 공통 패턴

### 패턴 A: `System Model`은 generic foundation만 둔다

- `SplitMAC`, `SplitFC`는 공통적으로 다음만 둔다.
  - 참여 주체(client/device/server/AP)
  - 데이터 보유 가정
  - model split notation
  - 기본 training objective 또는 global loss
  - 통신 병목/채널 모델
- 반대로 제안 모듈명, 제안 알고리즘명, 세부 설계는 다음 섹션부터 설명한다.

### 패턴 B: challenge/motivation을 `System Model` 뒤에 두거나 그 안에서 최소한으로만 연결한다

- `SplitFC`는 `A Typical SL Framework`와 `Key Challenge in SL`까지 `System Model`에 넣고,
- 실제 proposed method는 다음 섹션에서 시작한다.
- 즉, `왜 새 방법이 필요한가`까지는 system-side narrative로 허용되지만,
- `어떻게 새 방법을 설계했는가`는 method 섹션으로 넘긴다.

### 패턴 C: proposed architecture를 `System Model`에 넣으면 경계가 흐려진다

- `U-SFL 2024`는 network architecture, U-SFL model, semantic-aware communication을 하나의 `System model`에 묶는다.
- 이 구조는 우리 논문 reviewer 코멘트와 같은 지적을 받을 가능성이 높다.

### 패턴 D: 더 보수적인 구성은 background/problem section 후에 proposed framework를 여는 방식이다

- `SC-USFL 2026`은 background/challenges를 먼저 두고,
- `SC-USFL framework`는 별도 섹션에서 case study로 연다.
- reviewer가 novelty separation을 강하게 요구할 때 가장 안전한 방식이다.

## 우리 원고에 대한 시사점

### 권장 방향

- `II. System Model`에는 다음만 두는 것이 안전하다.
  - generic wireless SFL setup
  - `f = \phi_c(x)` 같은 smashed data notation
  - uplink channel model `f' = h f + n`
  - server prediction `\hat{y} = \phi_s(f')`
  - 기본 supervised task loss `\mathcal{L}_{task}`
  - high-dimensional smashed data로 인한 communication bottleneck

### Section III로 넘겨야 할 것

- semantic encoder / decoder
- dual masking
- VIB semantic masking
- SNR-driven channel masking
- dynamic slicing
- sparsity-aware gradient compensation
- proposed total loss (`beta`, IB/VIB term 포함)

### 구조 판단

- reviewer 코멘트를 고려하면,
- 우리 논문은 `U-SFL 2024`식 혼합 구조보다 `SplitMAC`/`SplitFC`/`SC-USFL 2026` 쪽 구성 원칙을 따르는 편이 낫다.
- 즉 `System Model`은 generic하고 짧더라도 괜찮고,
- novelty는 `III. Proposed Method`에서 명시적으로 여는 것이 더 설득력 있다.

## 한 줄 결론

- 무선 환경 SFL/SL 문헌에서 가장 reviewer-friendly한 패턴은
  - `System Model = generic setup + notation + channel/loss/challenge`
  - `Proposed Method = 제안 구조와 모듈`
- 이 분리를 유지하는 것이다.
