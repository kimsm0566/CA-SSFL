# 결과 요약

## 결과

- 상태: `미실행`
- 결정: `반복`

## 무엇을 테스트했는가

`beta=0.001` 조건에서 `SSFLv6` baseline과 세 가지 ablation(`w_o_vib`, `w_o_film`, `w_o_beta`)을 full `200` run으로 비교한다.

## 최종 비교

- baseline: `SSFLv6 @ beta=0.001`
- candidate: `SSFLv6_w_o_vib`, `SSFLv6_w_o_film`, `SSFLv6_w_o_beta`
- 고정 조건 일치 여부: `예정`
- seeds: `1`
- 산출물 경로:
  - `docs/experiments/2026-03-29_23-21_v01_ssflv6-beta-x2-ablations/artifacts/`

## 주요 지표

- 정확도: `미실행`
- 통신량: `미실행`
- SNR 강건성: `미실행`
- seed 분산: `미평가`

## 해석

실행 전 상태다. full run 완료 후 기존 `beta=0.0005` 결과와 함께 비교를 기록한다.

## 알려진 한계

- 아직 어떤 설정도 실행되지 않았다.

## 다음 권장 행동

- Docker GPU preflight
- 설정별 full run
- 결과 취합 후 기존 `beta=0.0005` 결과와 비교
