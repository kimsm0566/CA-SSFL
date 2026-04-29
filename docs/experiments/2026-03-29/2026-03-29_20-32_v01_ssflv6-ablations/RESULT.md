# 결과 요약

## 결과

- 상태: `부분 완료`
- 결정: `반복`

## 무엇을 테스트했는가

Docker GPU 경로에서 원래 threshold 식으로 되돌린 뒤 `SSFLv6` baseline과 세 가지 ablation(`w_o_vib`, `w_o_film`, `w_o_beta`)을 비교했다. 현재는 `seed=1` 기준으로 trend `20`라운드와 full `200`라운드 결과까지 확보했다.

## 최종 비교

- baseline: `SSFLv6`
- candidate: `SSFLv6_w_o_vib`, `SSFLv6_w_o_film`, `SSFLv6_w_o_beta`
- 고정 조건 일치 여부: `예`
- seeds: `trend=1`, `full completed=1`, `full target=1,2,3,4`
- 산출물 경로:
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-trend20/`
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-full200/`

## 주요 지표

- 정확도:
  - trend `20`:
    - `SSFLv6` round `20` acc `20.30%`, `Test SNR 12dB 16.48%`
    - `SSFLv6_w_o_vib` round `20` acc `14.93%`, `Test SNR 12dB 12.35%`
    - `SSFLv6_w_o_film` round `20` acc `21.26%`, `Test SNR 12dB 22.13%`
    - `SSFLv6_w_o_beta` round `20` acc `19.24%`, `Test SNR 12dB 19.73%`
  - full `200`:
    - `SSFLv6` round `200` acc `43.17%`, `Test SNR 12dB 43.29%`
    - `SSFLv6_w_o_vib` round `200` acc `21.51%`, `Test SNR 12dB 20.93%`
    - `SSFLv6_w_o_film` round `200` acc `42.58%`, `Test SNR 12dB 42.43%`
    - `SSFLv6_w_o_beta` round `200` acc `45.29%`, `Test SNR 12dB 47.09%`
- 통신량:
  - trend `20`:
    - `SSFLv6` `3234.32 MB`
    - `SSFLv6_w_o_vib` `17100.88 MB`
    - `SSFLv6_w_o_film` `17490.85 MB`
    - `SSFLv6_w_o_beta` `3586.46 MB`
  - full `200`:
    - `SSFLv6` `28386.97 MB`
    - `SSFLv6_w_o_vib` `177271.38 MB`
    - `SSFLv6_w_o_film` `93566.85 MB`
    - `SSFLv6_w_o_beta` `29419.54 MB`
- SNR 강건성: `12dB 단일 점과 기본 multi-SNR 로그만 확인`
- seed 분산: `미평가`

## 해석

짧은 horizon과 full `200` 결과가 같은 방향을 가리킨다. `w_o_vib`와 `w_o_film`는 통신량이 크게 튀어 communication-performance trade-off가 명확히 나쁘다. `w_o_beta`는 accuracy는 가장 높지만 통신량도 baseline보다 더 크다. 따라서 원래 threshold 기준 `seed=1` 결과만 보면 baseline `SSFLv6`가 가장 낮은 통신량으로 강한 성능을 유지하는 쪽이다.

## 알려진 한계

- full `200` 비교는 아직 `seed=1` 한 개뿐이다.
- seed 평균과 분산은 아직 없다.

## 다음 권장 행동

- baseline `SSFLv6`와 `SSFLv6_w_o_beta`를 우선순위로 `seed 2,3,4`까지 확장
- `w_o_vib`, `w_o_film`는 통신량 회귀가 커 후순위로 두고 필요 시에만 추가 seed 검증
- `RESULTS_LEDGER.md`에 `seed=1` full 결과 반영
