# 실험 계획

## 메타데이터

- 실험 id: `2026-03-30_00-18_v01_ssflv6-seed2-oldcode-repro`
- 초안 일시: `2026-03-30 00:18 KST`
- 상태: 승인
- 담당자: Codex

## 목표

사용자가 방금 되돌린 `_run_clientv6`와 `FiLMChannelAwareEncoder` 기준으로 `SSFLv6` `seed=2`를 다시 실행해, 과거 raw artifact의 낮은 통신량과 active ratio가 재현되는지 확인한다.

## 지금 하는 이유

직전 재현 run은 current canonical 코드에서 `30541.49 MB`로 끝났고, 과거 raw `seed=2`는 `21128.55 MB`였다. 사용자가 예전 실험 코드를 다시 반영했다고 했으므로, 코드 차이를 먼저 명시한 뒤 동일 조건 재실행으로 원인을 더 좁힐 수 있다.

## 제안 변경사항

- 대상 코드 경로: `src/utils/trainer.py`, `src/models/model.py`
- 의도한 동작 변화:
  - `_run_clientv6`가 샘플별 VIB mask, 적응형 beta, sparse gradient 복원/보상 경로를 사용
  - `FiLMChannelAwareEncoder`가 경량 `2x2 -> compressed_dim` 기반 구조를 사용
- 유지할 조건:
  - `SSFLv6`
  - `cifar10`, `class`
  - `n_clients=9`, `n_client_data=3000`, `batch_size=100`
  - `n_epochs=1`, `n_rounds=200`
  - `model_type=resnetv2`, `channel_type=rayleigh`
  - `snr_db=12`, `compressed_dim=4096`
  - `beta=0.0005`, `pruning_threshold=1.0`, `seed=2`
  - Docker GPU 경로 사용

## 후보 접근법

- 접근 A: 코드 차이를 읽고 바로 full `200` 재실행
- 접근 B: 짧은 smoke 후 full run
- 우선 접근법과 그 이유: 접근 A. 이미 동일 조건 smoke와 full run 기반이 있고, 이번 질문은 재현 여부 확인이 핵심이라 full run이 바로 필요하다.

## 계획된 검증

- 스모크 체크: 생략. 동일 harness와 Docker 경로는 직전 실험에서 이미 검증됨
- 비교 대상:
  - 과거 raw `src/results/.../seed_2_server.log`
  - 직전 current canonical rerun `docs/experiments/.../orig-threshold-rerun-seed2/.../seed_2_server.log`
- 예상 산출물 경로:
  - `docs/experiments/2026-03-30_00-18_v01_ssflv6-seed2-oldcode-repro/artifacts/`

## 리스크와 열린 질문

- 기술적 리스크:
  - 사용자가 바꾼 코드가 과거와 완전히 같은 버전이 아닐 수 있다
  - `compressed_dim=4096`과 encoder 구조가 내부적으로 불일치할 수 있다
- 평가상 리스크:
  - raw artifact와 로그 포맷은 같아도 내부 연산이 다를 수 있다
- 검토가 필요한 질문:
  - active ratio 감소가 encoder 구조 때문인지 `_run_clientv6` mask 처리 때문인지

## 사용자 검토 메모

- 피드백: 사용자가 `_run_clientv6`와 film encoder를 예전 실험 코드로 변경했다고 언급
- 합의된 결정: 차이 분석 후 `seed=2` full rerun 실행
- 남은 쟁점: 재현 성공 시 어느 변경이 결정적이었는지 후속 분리 필요

## 실행 게이트

- 구현 시작 가능?: 예
- 아니라면 먼저 명확히 할 점:
