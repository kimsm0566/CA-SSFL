# 결과 요약

## 결과

- 상태: `혼합`
- 결정: `반복`

## 무엇을 테스트했는가

`SSFLv6`의 기존 `K` 선택 정책은 유지한 채, 선택된 활성 semantic feature에만 DCT 기반 spreading을 적용하는 1차 구현을 평가했다. 이후 exploratory 결과를 바탕으로 `SNR-adaptive beta`를 결합한 후보를 `3-seed` matched 비교로 추가 검증했다.

## 최종 비교

- exploratory:
  - baseline: `semantic_spreading_enable=0`, `snr_adaptive_beta_enable=0`
  - candidate A: `semantic_spreading_enable=1`, `snr_adaptive_beta_enable=0`
  - candidate B: `semantic_spreading_enable=1`, `snr_adaptive_beta_enable=1`
  - seeds: `0`
- matched:
  - baseline: `semantic_spreading_enable=0`, `snr_adaptive_beta_enable=0`
  - candidate: `semantic_spreading_enable=1`, `snr_adaptive_beta_enable=1`
  - 고정 조건 일치 여부: `예`
  - seeds: `0,1,2`
- 산출물 경로:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-09-rayleigh-seq-full/`

## 주요 지표

- exploratory `seed=0`:
  - baseline final acc: `40.16%`, total comm: `20250.62 MB`
  - spreading-only final acc: `38.48%`, total comm: `20922.25 MB`
  - spreading + snr-adaptive beta final acc: `44.10%`, total comm: `21398.05 MB`
- matched `seed=0,1,2`:
  - baseline final acc mean/std: `43.99 / 3.26`
  - candidate final acc mean/std: `45.26 / 3.45`
  - baseline total comm mean/std: `20917.92 / 492.48 MB`
  - candidate total comm mean/std: `22658.04 / 921.42 MB`
  - low-SNR `-6 dB` mean:
    - baseline: `41.47%`
    - candidate: `42.67%`
  - high-SNR `12 dB` mean:
    - baseline: `44.46%`
    - candidate: `45.85%`

## 해석

핵심은 두 가지다.

- `spreading 단독`은 실패했다. `seed=0`에서 baseline보다 정확도와 통신량이 모두 악화됐다.
- `spreading + SNR-adaptive beta`는 `3-seed` 기준으로 baseline보다 정확도를 올렸지만, 통신량도 함께 증가했다.

즉 이번 시도는 `Rayleigh robustness` 관점에서는 분명한 accuracy 이득이 있었지만, 저장소의 1차 목표인 `communication-performance trade-off 개선` 관점에서는 아직 승격할 수 없다. 현재 후보는 `정확도/강건성 개선형`이지 `trade-off 우위형`은 아니다.

## 알려진 한계

- `seed=3+` 확장 미실행
- 통신량 증가를 상쇄할 추가 제어 실험 미실행
- active dimension, KL, per-round efficiency를 공식 산출물로 정리하지 않음

## 다음 권장 행동

- `candidate`를 기준으로 active budget을 다시 줄이는 후속 실험 수행
- 예: `film_max_t`, `film_min_t`, `beta`를 재탐색해 accuracy 이득을 유지하며 comm를 baseline 근처로 회복
- 또는 `spreading`은 유지하고 `power allocation` 계열 후속 아이디어를 결합
