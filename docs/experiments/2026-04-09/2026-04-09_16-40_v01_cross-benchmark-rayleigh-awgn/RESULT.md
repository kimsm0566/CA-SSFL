# 결과 요약

## 결과

- 상태: `완료`
- 결정: `반복`

## 무엇을 테스트했는가

`Rayleigh`에서 `SFL`, `SC-USFL`, `SSFLv6 baseline`, `SSFLv6 candidate`를 matched seed set으로 다시 측정했고, `AWGN`에서는 사용자 요청에 따라 `SFL`, `SC-USFL`를 같은 seed set으로 측정했다.

## 최종 비교

- Rayleigh:
  - seeds: `1,2,3,4`
  - 고정 조건 일치 여부: `예`
- AWGN:
  - seeds: `1,2,3,4`
  - 고정 조건 일치 여부: `예`
- 산출물 경로:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-09-cross-benchmark/`

## 주요 지표

### Rayleigh

- `SFL`
  - final acc mean/std: `51.07 / 0.61`
  - total comm mean: `172882.75 MB`
  - `-6 dB` mean: `44.92%`
- `SC-USFL`
  - final acc mean/std: `40.90 / 3.02`
  - total comm mean: `23821.53 MB`
  - `-6 dB` mean: `40.09%`
- `SSFLv6 baseline`
  - final acc mean/std: `42.28 / 3.96`
  - total comm mean: `21336.62 MB`
  - `-6 dB` mean: `39.70%`
- `SSFLv6 candidate`
  - final acc mean/std: `43.67 / 3.64`
  - total comm mean: `23406.29 MB`
  - `-6 dB` mean: `40.98%`

### AWGN

- `SFL`
  - final acc mean/std: `53.70 / 1.54`
  - total comm mean: `172882.75 MB`
- `SC-USFL`
  - final acc mean/std: `39.76 / 2.73`
  - total comm mean: `23821.53 MB`

## 해석

- 현재 `SSFLv6 candidate`는 `Rayleigh`에서 `SC-USFL`를 전반적으로 이긴다.
  - final accuracy 우세
  - 저 SNR `-6 dB` 우세
  - total comm도 소폭 우세
- 그러나 `SFL`은 여전히 accuracy와 robustness 측면에서 크게 앞선다.
  - 다만 통신량은 `SSFLv6 candidate` 대비 약 `7.4x` 수준으로 훨씬 크다.
- 따라서 지금의 가장 현실적인 목표는 `SFL` 직접 추월이 아니라, `SC-USFL` 대비 우세를 유지한 채 `candidate`의 communication cost를 더 줄여 frontier를 다듬는 것이다.

## 알려진 한계

- `AWGN`에서는 아직 `SSFLv6 baseline/candidate`를 재측정하지 않았다.
- overnight autonomous follow-up은 Docker banner가 집계 JSON에 섞이며 파싱에 실패해 Stage A/B까지 진행되지 않았다.

## 다음 권장 행동

- `Rayleigh`에서 `candidate`의 `beta`, `film_max_t`, `film_min_t` 재탐색
- 통신량 절감형 best config를 선별한 뒤 `AWGN`에 같은 설정 재투입

