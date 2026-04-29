# Reasoning-Native Agentic Communication for 6G

## 서지 정보

- 저자: Hyowoon Seo, Joonho Seon, Jin Young Kim, Mehdi Bennis, Wan Choi, Dong In Kim
- 학회/저널 및 연도: arXiv preprint, 2026
- 원문 링크:
  - arXiv abs: https://arxiv.org/abs/2602.17738
  - DOI: https://doi.org/10.48550/arXiv.2602.17738
- 로컬 파일 경로: 미저장

## 한 줄 요약

- 이 논문은 6G 자율 에이전트 환경에서 통신 목표를 비트 전달이나 semantic preservation이 아니라 에이전트 간 추론 상태와 믿음 상태의 정렬로 재정의해야 한다고 주장한다.

## 문제 설정

- 학습 설정: 구체적 학습 알고리즘 제안 논문이라기보다 6G multi-agent coordination을 위한 통신 패러다임 제안
- 데이터셋: 확인 가능한 공개 정보 기준 명시적 benchmark dataset 없음
- 파티션 방식: 해당 없음 또는 비공개
- 클라이언트 수: 고정된 federated client setting으로 정의되지 않음
- 로컬 학습 예산: 해당 없음
- 채널 모델: 전통적 physical channel 세부 모델이 중심이 아니라 agent coordination 관점의 개념 아키텍처가 중심
- SNR 설정: 공개 초록 기준 명시적 SNR sweep 또는 고정 SNR 실험 조건 확인 불가
- 통신 제약: 채널 용량 자체보다 belief divergence를 언제 줄이기 위해 통신할지에 초점

## 방법 요약

- 저자들은 semantic communication만으로는 충분하지 않다고 본다. 동일한 의미를 전달받아도 각 에이전트의 내부 추론이 다르게 전개되면 최종 행동이 어긋날 수 있기 때문이다.
- 이 현상을 `belief divergence`로 정의하고, 미래 6G에서는 이 divergence를 제어하는 것이 핵심 통신 목적이 되어야 한다고 주장한다.
- 제안 구조는 기존 통신 스택 위에 coordination plane을 추가하는 형태다.
- 이 coordination plane은 shared knowledge structure와 bounded belief modeling을 기반으로, 현재 또는 미래의 reasoning misalignment를 예측하고 필요한 순간에만 통신을 유발한다.
- 즉, 데이터 relevance나 채널 상태만으로 송신 여부를 결정하지 않고, 상대 에이전트와의 내부 belief misalignment risk를 통신 트리거로 사용한다.
- 논문은 이를 통해 네트워크가 단순 전달자가 아니라 distributed reasoning의 harmonizer로 동작해야 한다는 방향을 제시한다.

## 보고된 결과

- 주요 지표: 공개 초록 기준 정량 벤치마크 지표보다 개념적 효과와 representative scenario 설명이 중심
- 비교 기준선: Shannon communication, semantic communication, task-oriented communication 대비 상위 개념으로 positioning
- 핵심 성과:
  - belief divergence라는 문제를 명시적으로 정의한다.
  - semantic alignment와 behavioral alignment가 다르다는 점을 6G agentic communication 맥락에서 구조화한다.
  - reasoning-native architecture와 coordination plane이라는 설계 방향을 제안한다.
- 강건성 점검:
  - 공개 초록 기준 다중 seed, multi-SNR, matched communication budget 하 정량 강건성 평가는 확인되지 않는다.
  - 따라서 현재 단계에서는 성능 우위 입증 논문이라기보다 문제 정의와 시스템 비전에 가깝다.

## 이 프로젝트와의 연관성

- 저장소 내 대응 영역:
  - [src/utils/trainer.py](/home/sunmin/SFL_Semantic/src/utils/trainer.py)
  - [src/utils/eval.py](/home/sunmin/SFL_Semantic/src/utils/eval.py)
  - [src/models/model.py](/home/sunmin/SFL_Semantic/src/models/model.py)
- 가장 가까운 in-repo 알고리즘 또는 baseline:
  - semantic feature를 압축하거나 일부 차원만 전송하는 `SSFL`, `SSFLv6`, pruning/VIB 계열 baseline
- 바로 재사용 가능해 보이는 점:
  - 모든 라운드에 고정적으로 전송하지 않고, prediction disagreement 또는 uncertainty gap이 커질 때만 통신하는 event-triggered communication 가설
  - semantic similarity 대신 decision inconsistency proxy를 전송 기준으로 쓰는 관점
  - 전송량 절감과 함께 최종 task consistency를 같이 보는 평가 축
- 저장소 관점의 핵심 차이:
  - 현재 저장소는 image classification 기반 semantic/split/federated learning 실험 코드이고, 이 논문은 보다 상위의 6G multi-agent reasoning coordination 패러다임을 다룬다.
  - 따라서 논문의 개념을 바로 코드에 넣기보다는, `belief divergence proxy`를 정의해 작은 실험 가설로 내리는 번역 작업이 먼저 필요하다.

## 약점과 재현 리스크

- 공개된 정보 기준으로 정량 실험이 제한적이거나 부재하므로, communication-performance frontier 개선을 실증한 논문으로 해석하면 과장이다.
- belief divergence는 직관적으로 중요하지만, 실제 학습 시스템에서 어떻게 측정할지 정의가 어렵다.
- shared ontology, bounded belief modeling, coordination plane은 개념적으로 타당하지만 구현 복잡도와 오버헤드가 크다.
- 이 저장소가 다루는 CIFAR 기반 semantic/split/federated training과 논문이 상정하는 autonomous agent coordination 사이에는 설정 간극이 크다.
- 채널 조건, SNR, seed variation에 대한 재현 가능성 판단 자료가 부족하다.
- 통신량 절감 주장도 wire-level byte accounting이나 matched baseline이 없으면 이 저장소 기준 개선으로 인정하기 어렵다.

## 가능한 개선점

- belief divergence를 추상 개념에 머무르게 두지 말고, 이 저장소에서는 `logit divergence`, `entropy gap`, `server-client prediction disagreement`, `round-to-round representation drift` 같은 계산 가능한 proxy로 내려야 한다.
- coordination plane 전체를 구현하기보다, 먼저 communication trigger만 divergence-aware rule로 바꾸는 최소 실험이 적절하다.
- semantic compression baseline과 비교할 때는 정확도뿐 아니라 실제 누적 MB, 인덱스 오버헤드, seed variance를 같이 기록해야 한다.
- multi-agent reasoning이라는 큰 비전을 그대로 가져오기보다, 현재 저장소의 supervised classification loop에 맞는 작은 형태의 decision-alignment metric부터 정의해야 한다.

## 이 코드베이스에서 검증할 가설

- 서버와 클라이언트 간 `logit KL` 또는 top-1 disagreement risk가 큰 샘플/라운드에서만 추가 semantic feature를 전송하면, 동일 정확도에서 누적 통신량을 줄일 수 있다.
- 고정 차원 전송보다 uncertainty-conditioned adaptive transmission이 low-SNR 구간에서 더 나은 accuracy-communication trade-off를 만들 수 있다.
- semantic reconstruction loss가 낮아도 prediction disagreement가 큰 경우가 존재하며, 이 구간을 별도로 제어하면 평균 정확도보다 worst-case accuracy 또는 seed robustness가 개선될 수 있다.
- belief divergence proxy를 통신 트리거로 쓰는 규칙은 pruning/VIB 기반 중요도 추정보다 적은 라운드 수 또는 적은 전송 빈도로 비슷한 성능을 낼 수 있다.

## 액션 상태

- 상태: 문헌 노트 작성 완료, 구현 및 실험 미착수
- 다음 단계: 이 논문 아이디어를 실제로 시험하려면 `docs/experiments/` 아래에 한국어 `PLAN.md`를 만들고, 어떤 divergence proxy를 통신 트리거로 쓸지 먼저 고정해야 한다.
