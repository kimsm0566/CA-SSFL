# 실험 명세

## 메타데이터

- 실험 id: `2026-04-03_22-00_v01_reasoning-triggered-comm`
- 기준 문서:
  `docs/literature/papers/2026_seo_reasoning-native-agentic-communication.md`
- 상태: 구현중
- 담당자: Codex

## 고정 조건

- dataset:
  1차 스모크는 `mnist` 또는 기존 smoke dataset
- partition type:
  1차 스모크는 `iid`
- n_clients:
  2
- n_client_data:
  작은 smoke budget
- batch_size:
  작은 smoke budget
- n_epochs:
  1
- n_rounds:
  1 또는 짧은 smoke round
- algorithm:
  `SSFLv6`
- model type:
  기존 `ClientResNet18v2` / `ServerResNet18v2`
- channel type:
  smoke 단계에서는 기존 설정 유지
- snr setting:
  기존 trainer 내부 sampled SNR 유지
- compressed dimension:
  baseline과 동일 유지
- pruning threshold:
  baseline과 동일 유지
- beta schedule:
  baseline과 동일 유지
- seed set:
  smoke 단계에서는 단일 seed

## 변경 변수

- `--reasoning_trigger_enable`
- `--reasoning_trigger_threshold`
- `--reasoning_trigger_warmup_rounds`

## 구현 명세

### 목표

논문의 exact reproduction이 아니라, 현재 `SSFLv6` 코드 경로에 맞는 `belief-divergence proxy` 기반 전송 gating을 추가한다.

### 선택한 proxy

현재 코드 경로에서는 클라이언트 측 class prediction이나 server-side decision disagreement를 바로 얻기 어렵다. 따라서 1차 구현은 `latent summary drift`를 reasoning divergence proxy로 사용한다.

- 현재 batch의 latent summary:
  `z.mean(dim=0)`
- reference summary:
  마지막으로 실제 전송한 batch의 latent summary
- divergence score:
  두 summary 사이의 cosine distance

### 전송 규칙

- warmup round 동안은 항상 전송
- 그 이후에는
  - `drift_score >= threshold` 이면 기존 payload 전송
  - `drift_score < threshold` 이면 이번 batch payload를 zero-mask 처리하여 침묵

### 구현 위치

- `src/utils/option.py`
  - reasoning trigger CLI 인자 추가
- `src/utils/trainer.py`
  - cosine-distance 기반 score 함수 추가
  - `_run_clientv6`에서 `latent_summary` 계산
  - gating 여부에 따라 mask zero-out
  - trigger 로그 추가

### baseline 비교

- baseline:
  `SSFLv6` with `--reasoning_trigger_enable 0`
- candidate:
  `SSFLv6` with `--reasoning_trigger_enable 1`

### 기대 효과

- representation drift가 작은 batch에서는 payload 전송이 줄어 cumulative communication cost가 감소
- accuracy 저하가 제한적이면 exploratory candidate로 유지

### known limitations

- 논문이 말한 reasoning state를 직접 추정하지 않는다.
- 마지막 전송 summary 기반이라 batch composition 변화에 민감할 수 있다.
- class-level disagreement 대신 latent drift를 쓰므로 reasoning proxy로는 약하다.

## 검증 계획

- static validation:
  `python -m py_compile src/utils/option.py src/utils/trainer.py`
- smoke run:
  `mpiexec`와 `mpi4py`가 있는 환경에서 1-round MPI run
- matched comparison:
  smoke 성공 후 same seed and budget로 baseline 대비 비교
- robustness extension:
  threshold sweep과 multi-seed 비교

## 산출물

- result path:
  기존 result 저장 규칙 사용
- notes path:
  `docs/experiments/2026-04-03_22-00_v01_reasoning-triggered-comm/`

## 판정 기준

- promotion rule:
  matched 조건에서 baseline 대비 comm 감소와 허용 가능한 accuracy 유지 확인
- rejection rule:
  random drift proxy가 불안정하여 accuracy regression이 크거나 comm 감소가 미미한 경우
- exploratory label condition:
  smoke-only 또는 single-seed short-budget 결과는 모두 exploratory

