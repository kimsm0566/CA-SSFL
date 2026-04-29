# 실험 계획

## 메타데이터

- 실험 id: `2026-04-11_07-10_v01_rayleigh-literature-four-method-suite`
- 초안 일시: `2026-04-11 07:10 KST`
- 상태: 승인
- 담당자: Codex

## 목표

문헌 검토를 바탕으로 Rayleigh 강건성 문제를 직접 겨냥하는 4개 새 방향을 같은 조건에서 순차 실행한다.

## 지금 하는 이유

지금까지의 `spreading`, `latent mixing`, `semidense`, `support floor`, `semantic power`는 전부 baseline을 명확히 이기지 못했다. 문헌을 보면 이 문제는 단순 mixing보다 `중요 feature 보호`, `base/refinement 계층`, `채널 인지형 masking`, `수신단 복원`으로 더 자주 다뤄진다. 따라서 연구 방향을 그 네 축으로 재정렬할 시점이다.

## 제안 변경사항

- 대상 코드 경로:
  - `src/utils/option.py`
  - `src/run_exp_main.py`
  - `src/models/model.py`
  - `src/utils/trainer.py`
  - `scripts/`
- 의도한 동작 변화:
  - 방법 1: importance-aware repetition
  - 방법 2: base-support + refinement-support
  - 방법 3: learned CSI-aware masking
  - 방법 4: server-side feature denoising / imputation
- 유지할 조건:
  - `cifar10`, `class`, `rayleigh`, `n_clients=8`, `seed 1,2`
  - baseline hyperparameter는 그대로 유지

## 후보 접근법

- 접근 A:
  - 네 방법을 모두 최소 구현으로 넣고 representative config 1개씩만 exploratory run
- 접근 B:
  - 한두 방법만 먼저 구현
- 우선 접근법과 그 이유:
  - 접근 A
  - 사용자가 `1,2,3,4 모두 실험`을 명시했고, 현재는 후보군 비교가 목적이므로 breadth-first가 맞다.

## 계획된 검증

- 스모크 체크:
  - 각 방법 대표 설정으로 `1-round` smoke
- 비교 대상:
  - `CA-SSFL Orig`
- 예상 산출물 경로:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-11/2026-04-11-rayleigh-literature-four-method-suite`

## 리스크와 열린 질문

- 기술적 리스크:
  - repetition은 packet/gradient 경로에 개입하므로 버그 위험이 있다.
  - learned masking과 server-side imputation은 추가 파라미터가 생긴다.
- 평가상 리스크:
  - representative config가 약하면 방향 자체를 과소평가할 수 있다.
- 검토가 필요한 질문:
  - 없음. exploratory suite부터 실행한다.

## 사용자 검토 메모

- 피드백:
  - 사용자가 현재 실험을 중단하고 새 `1,2,3,4` 모두 실행하라고 요청함.
- 합의된 결정:
  - 이전 follow-up은 중단, 새 4-method suite로 전환
- 남은 쟁점:
  - 없음

## 실행 게이트

- 구현 시작 가능?: 예
- 아니라면 먼저 명확히 할 점:
  - 없음
