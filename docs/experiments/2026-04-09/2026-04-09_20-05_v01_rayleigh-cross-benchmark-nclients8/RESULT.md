# 결과 요약

## 메타데이터

- 실험 id: `2026-04-09_20-05_v01_rayleigh-cross-benchmark-nclients8`
- 상태: `completed`

## 무엇을 테스트했는가

`Rayleigh` 채널에서 `n_clients=8` 기준으로 아래 네 알고리즘을 seed `1,2,3,4`에 대해 다시 측정했다.

- `SFL`
- `SC-USFL`
- `CA-SSFL Orig`
- `CA-SSFL New`

## 산출물

- 결과 루트:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-09-rayleigh-cross-benchmark-nclients8`
- 로그:
  - `RUNLOG.md`
- 요약 json:
  - `summary.json`

## 비고

- `CA-SSFL Orig`는 `semantic_spreading=0`, `snr_adaptive_beta=0`
- `CA-SSFL New`는 `semantic_spreading=1`, `snr_adaptive_beta=1`

## 주요 지표

- `SFL`
  - final acc mean/std: `47.44 / 2.14`
  - total comm mean: `153673.56 MB`
  - `-6 dB` mean: `41.59%`
- `SC-USFL`
  - final acc mean/std: `38.64 / 2.78`
  - total comm mean: `21177.45 MB`
  - `-6 dB` mean: `38.49%`
- `CA-SSFL Orig`
  - final acc mean/std: `39.50 / 3.49`
  - total comm mean: `19616.33 MB`
  - `-6 dB` mean: `37.49%`
- `CA-SSFL New`
  - final acc mean/std: `39.09 / 4.30`
  - total comm mean: `21337.20 MB`
  - `-6 dB` mean: `37.30%`

## 해석

- `n_clients=8` 기준에서는 `CA-SSFL New`가 `CA-SSFL Orig`를 명확히 이기지 못했다.
- `SC-USFL`와 비교해도 현재 `CA-SSFL New`는 accuracy, `-6 dB`, communication에서 모두 우세라고 말하기 어렵다.
- 즉 `n_clients=9`에서 보였던 개선 효과는 `n_clients=8` 재실행에서는 재현되지 않았다.
- 이후 claim은 `n_clients=8` 결과를 기준으로 다시 정리해야 한다.
