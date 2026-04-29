# 실험 계획

## 메타데이터

- 실험 id: `2026-03-29_23-50_v01_ssflv6-stronger-channel-mask`
- 초안 일시: `2026-03-29 23:50 KST`
- 상태: `승인`
- 담당자: `Codex + 사용자`

## 목표

현재 canonical `SSFLv6`의 channel mask threshold를 “지금보다 조금 더 강하게” 조정해 data comm를 낮출 수 있는지 확인한다.

## 지금 하는 이유

- current canonical threshold는 `0.5 - (snr_normalized * 0.3)`다.
- 이 설정에서는 `SSFLv6` baseline full `200` 결과가 `28386.97 MB`로 높다.
- 사용자는 극단적 변경이 아니라 현재보다 조금 더 강한 mask를 원했다.

## 제안 변경사항

- 대상 코드 경로:
  - `src/utils/trainer.py`
  - 문서:
    - `docs/experiments/2026-03-29_23-50_v01_ssflv6-stronger-channel-mask/`
- 의도한 동작 변화:
  - FiLM channel mask threshold를 현재보다 한 단계 더 공격적으로 올린다.
  - 먼저 짧은 진단 run으로 active ratio와 data comm 변화를 확인한다.
- 유지할 조건:
  - dataset, partition, client 수, batch size, epochs, rounds, channel, model, compressed_dim, beta, pruning_threshold는 유지한다.

## 후보 접근법

- 접근 A:
  - threshold를 현재보다 소폭만 강화한 식으로 바꾼다.
  - 5라운드 진단으로 통신량 변화를 먼저 본다.
  - 괜찮으면 full run으로 간다.
- 우선 접근법과 그 이유:
  - 접근 A
  - 이유: 사용자가 “조금 더 세게”를 요청했으므로, 이전 aggressive 후보보다 완만한 중간값이 맞다.

## 계획된 검증

- 스모크 체크:
  - `python -m py_compile`
  - `SSFLv6` `seed=1`, `n_rounds=5` 진단 run
- 비교 대상:
  - current canonical `SSFLv6`
  - stronger-mask `SSFLv6`
- 예상 산출물 경로:
  - `docs/experiments/2026-03-29_23-50_v01_ssflv6-stronger-channel-mask/`

## 리스크와 열린 질문

- 기술적 리스크:
  - threshold를 조금만 올려도 accuracy가 흔들릴 수 있다.
- 평가상 리스크:
  - 5라운드 결과만으로 full `200` 결과를 단정할 수 없다.
- 검토가 필요한 질문:
  - 없음

## 사용자 검토 메모

- 피드백:
  - 채널 마스크를 지금보다 더 세게 해본다.
- 합의된 결정:
  - 소폭 강화한 threshold부터 테스트한다.
- 남은 쟁점:
  - full run 승격 여부는 5라운드 결과를 본 뒤 판단

## 실행 게이트

- 구현 시작 가능?: `예`
- 아니라면 먼저 명확히 할 점:
  - 없음
