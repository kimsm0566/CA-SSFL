# 실험 계획

## 메타데이터

- 실험 id: `2026-04-03_22-00_v01_reasoning-triggered-comm`
- 초안 일시: `2026-04-03 22:00 KST`
- 상태: 초안
- 담당자: Codex

## 목표

`Reasoning-Native Agentic Communication for 6G`의 핵심 아이디어를 현재 저장소에 맞는 최소 가설로 번역한다. 구체적으로는 매 라운드 또는 매 스텝에서 고정적으로 semantic feature를 전송하는 대신, 계산 가능한 `belief divergence proxy`가 클 때만 추가 전송 또는 고정 예산 전송을 수행하는 규칙이 `accuracy-communication` trade-off를 개선할 가능성이 있는지 확인한다.

## 지금 하는 이유

현재 저장소의 주요 관심사는 정확도를 유지하거나 높이면서 누적 통신량을 줄이는 것이다. 최근 실험들은 주로 `beta`, pruning, active dimension 축소 같은 표현 압축 축에 집중되어 있었고, "언제 전송할 것인가"라는 통신 트리거 축은 아직 본격적으로 다루지 않았다. 이번 시도는 기존 압축 축과 직교하는 새 가설을 작은 범위에서 검증할 수 있다는 점에서 우선순위가 있다.

## 제안 변경사항

- 대상 코드 경로:
  - `src/utils/trainer.py`
  - `src/utils/eval.py`
  - 필요 시 `src/models/model.py`
- 의도한 동작 변화:
  - 서버-클라이언트 간 현재 예측 또는 latent 기반 불일치 정도를 계산한다.
  - 이 불일치가 임계값보다 작으면 전송을 생략하거나 약한 전송 정책을 사용한다.
  - 이 불일치가 임계값보다 크면 기존 semantic transmission 또는 강화된 전송 정책을 사용한다.
- 유지할 조건:
  - baseline 알고리즘은 우선 현재 canonical 비교축과 가까운 `SSFLv6` 계열에서 시작한다.
  - matched comparison에서는 `cifar10`, `class`, `rayleigh`, `snr_db=12`, `n_clients=9`, `n_client_data=3000`, `batch_size=100`, `n_epochs=1`, `n_rounds=200`, `compressed_dim=4096`를 유지한다.
  - 통신량 비교는 기존 accounting 로직을 바꾸지 않고, candidate가 기존 accounting 위에서 실제 누적 MB를 줄이는지로 판단한다.
  - claim-making 전에는 seed set을 baseline과 동일하게 맞춘다.

## 후보 접근법

- 접근 A: `prediction disagreement` 기반 event-trigger
  - 클라이언트 로컬 예측과 서버측 또는 직전 라운드 기준 예측이 크게 다를 때만 semantic feature를 추가 전송한다.
  - 장점은 구현이 단순하고 해석이 쉽다는 점이다.
  - 단점은 disagreement 신호를 얻기 위한 추가 forward 또는 bookkeeping이 필요할 수 있다.
- 접근 B: `uncertainty gap` 기반 adaptive transmission
  - entropy, max-softmax confidence, logit margin 등 불확실도 기반 지표가 나쁠 때만 더 많은 차원 또는 full transmission을 허용한다.
  - 장점은 belief divergence를 근사하는 계산 가능한 proxy를 쉽게 정의할 수 있다는 점이다.
  - 단점은 불확실도가 실제 misalignment를 항상 잘 반영하지 않을 수 있다.
- 접근 C: `representation drift` 기반 round trigger
  - 이전 라운드 대비 latent drift가 작으면 전송 빈도를 낮추고, drift가 커질 때만 전송한다.
  - 장점은 label-free하게 적용 가능하다.
  - 단점은 현재 코드 경로에서 drift 측정과 buffering 추가가 필요하다.
- 우선 접근법과 그 이유:
  - 접근 B를 1순위, 접근 A를 2순위로 둔다.
  - 이유는 접근 B가 현재 supervised classification loop에 가장 쉽게 맞고, `belief divergence`를 완전한 reasoning state가 아니라 계산 가능한 decision-risk proxy로 내릴 수 있기 때문이다.

## 계획된 검증

- 스모크 체크:
  - 수정된 Python 파일에 대해 `python -m py_compile`
  - 짧은 round 수 실행으로 code path가 end-to-end로 동작하는지 확인
- 비교 대상:
  - 현재 matched baseline `SSFLv6` 또는 직계 baseline
  - 필요 시 기존 `beta=0.00075` 후보와도 exploratory 비교
- 평가 수준:
  - 1단계: Level 1 smoke run으로 divergence-aware trigger가 정상 동작하는지 확인
  - 2단계: Level 2 matched comparison으로 `200` rounds 단일 seed 비교
  - 3단계: promising할 경우 동일 seed set 및 multi-SNR 확장
- 예상 산출물 경로:
  - `docs/experiments/2026-04-03_22-00_v01_reasoning-triggered-comm/`
  - 실행 artifact는 기존 결과 저장 규칙을 따르되, 이 실험 id를 명시적으로 남긴다.

## 리스크와 열린 질문

- 기술적 리스크:
  - `belief divergence`를 직접 측정할 수 없으므로 proxy 정의가 임의적일 수 있다.
  - 통신을 생략할 경우 현재 trainer flow가 가정하는 tensor shape나 aggregation path와 충돌할 수 있다.
  - trigger 로직이 추가 bookkeeping 때문에 오히려 model/data communication 외의 overhead를 늘릴 수 있다.
- 평가상 리스크:
  - 단일 seed에서만 좋아 보이는 gating 규칙일 수 있다.
  - accuracy 저하 없이 통신을 줄였는지, 혹은 accounting 방식 때문에 절감된 것처럼 보이는지 구분이 필요하다.
  - baseline과 다른 default가 섞이면 exploratory 결과로만 봐야 한다.
- 검토가 필요한 질문:
  - 첫 구현 단위는 "전송 여부 이진 gating"으로 할지, "전송 강도 다단계 조절"로 할지
  - divergence proxy는 `entropy`, `logit KL`, `top-1 disagreement`, `margin` 중 무엇을 1차 지표로 둘지
  - gating이 sample-level인지 batch-level인지 round-level인지 먼저 고정할지

## 사용자 검토 메모

- 피드백:
  - 논문 기반 아이디어를 실험 계획으로 구체화
- 합의된 결정:
  - 아직 없음
- 남은 쟁점:
  - 첫 후보 proxy와 baseline 범위 확정
  - 결과를 claim-making 비교로 바로 가져갈지, exploratory smoke부터 시작할지 결정

## 실행 게이트

- 구현 시작 가능?: 아니오
- 아니라면 먼저 명확히 할 점:
  - 첫 시도에서 사용할 divergence proxy 1개
  - 적용 단위: sample / batch / round
  - baseline 대상: `SSFLv6` only인지, `SSFLv6_w_o_beta`까지 포함할지
