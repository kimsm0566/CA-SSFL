# 결과 요약

## 결과

- 상태: `진단 완료`
- 결정: `수정 미채택`

## 무엇을 테스트했는가

현재 `SSFLv6` 통신량 회귀의 원인을 찾기 위해 baseline 로그, 현재 모델 크기, threshold-only 최소 수정, 그리고 hidden-width 축소 기반 model comm 후보 2개를 진단했다. 이후 ablation full run은 원래 threshold 기준으로 다시 수행했고, debug 중 시도한 수정은 채택하지 않았다.

## 최종 비교

- baseline: 과거 matched `SSFLv6` artifact와 현재 Docker `SSFLv6`
- candidate:
  - threshold-only 수정 `SSFLv6`
  - `model32 + threshold1`
  - `model32 + threshold2`
- 고정 조건 일치 여부: `예`
- seeds: `1`
- 산출물 경로:
  - `docs/experiments/2026-03-29_21-02_v01_ssflv6-comm-debug/`

## 주요 지표

- 정확도: `threshold-only 5라운드 진단에서는 성능 판단 불가`
- 통신량:
  - 현재 baseline `28386.97 MB @ 200 rounds`
  - 과거 matched baseline `41.75 MB/round model comm`, `55~69 MB/round data comm`
  - threshold-only 수정 후 `46.97 MB/round model comm`, `61.63~68.10 MB/round data comm`
  - `model32 + threshold1` 후 `37.97 MB/round model comm`, `77.05~83.32 MB/round data comm`
  - `model32 + threshold2` 후 `37.97 MB/round model comm`, `70.00~76.74 MB/round data comm`
- SNR 강건성: `아직 미평가`
- seed 분산: `아직 미평가`

## 해석

현재 단계에서는 model comm 증가와 data comm 증가가 둘 다 존재한다는 점이 확인됐다. threshold-only 수정으로 data comm는 과거 matched baseline 범위에 거의 복귀했지만, 이 수정은 canonical 경로에 채택하지 않았다. 반대로 hidden-width 축소는 model comm를 `37.97 MB/round`까지 낮췄지만 mask 분포와 초기 정확도를 함께 흔들었다. 따라서 현재 결론은 "원인은 식별됐지만 바로 승격할 수정은 아직 없다"이다.

## 알려진 한계

- threshold-only 수정은 5라운드 진단까지만 확인했다.
- model32 후보 2개도 5라운드 진단까지만 확인했다.
- `<21000 MB @ 200 rounds` 달성 여부는 full run으로 아직 검증하지 않았다.

## 다음 권장 행동

- `semantic_encoder.snr_to_film.*`를 중심으로 model comm 회귀를 직접 줄이되, hidden width를 급격히 줄이지 않는 후보 설계
- 후보 적용 후 5라운드 진단으로 `model comm/round`와 `data comm/round`를 동시에 확인
- 통신량과 초기 정확도가 함께 유지되면 그때만 별도 실험 폴더에서 full run으로 `<21000 MB` 가능성 재검증
