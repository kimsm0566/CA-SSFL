# 결과 요약

## 결과

- 상태: `진단 완료`
- 결정: `미채택`

## 무엇을 테스트했는가

현재 `SSFLv6` canonical threshold보다 조금 더 강한 channel mask threshold 후보를 5라운드 진단으로 비교했다.

## 최종 비교

- baseline: current canonical `SSFLv6`
- candidate: stronger-mask `SSFLv6`
- 고정 조건 일치 여부: `예`
- seeds: `1`
- 산출물 경로:
  - `docs/experiments/2026-03-29_23-50_v01_ssflv6-stronger-channel-mask/`

## 주요 지표

- 정확도:
  - candidate round `5` acc `12.25%`
  - candidate `Test SNR 12dB` `10.79%`
- 통신량:
  - candidate round별 `data comm`: `113.26`, `114.31`, `116.40`, `116.03 MB`
  - candidate round별 `model comm`: `46.97 MB`
  - baseline 참고: current canonical은 같은 5라운드 진단에서 `data comm 119~123 MB`, `model comm 46.97 MB`
- SNR 강건성: `미평가`
- seed 분산: `미평가`

## 해석

threshold를 조금 더 세게 하면 data comm가 아주 약간 줄어들긴 한다. 하지만 감소 폭은 작고 초기 정확도 손실이 더 커서, 현재 후보는 canonical로 채택할 가치가 없다.

## 알려진 한계

- 결과는 `seed=1`, `n_rounds=5` 진단만 기반으로 한다.
- 더 강한 다음 후보는 아직 테스트하지 않았다.

## 다음 권장 행동

- 필요 시 더 공격적인 다음 threshold 후보를 새로 설계
- 다음 후보도 먼저 5라운드 진단으로 `data comm`와 초기 정확도를 같이 확인
