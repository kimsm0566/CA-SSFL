# RESULT

## 요약

`Rayleigh`, `n_clients=8`, `seed=1,2` 기준에서 이번 literature-inspired 4개 방법 중 가장 좋은 결과는 `method2: base-support + refinement-support`였다.

- baseline `CA-SSFL Orig` 대비
  - final acc: `41.91 -> 42.28` (`+0.37%p`)
  - total comm: `19608.50 MB -> 17364.44 MB` (`-2244.06 MB`)
  - `-6 dB`: `39.37 -> 39.83` (`+0.46%p`)
  - `12 dB`: `42.52 -> 42.88` (`+0.36%p`)

즉, 이번 suite에서는 `method2`만이 정확도와 Rayleigh 저 SNR 강건성을 유지 또는 개선하면서 통신량도 줄이는 방향을 보였다.

## 방법별 결과

### Baseline: `CA-SSFL Orig`

- seed 1: final `41.85`, comm `18826.68 MB`, `-6 dB 39.34`, `12 dB 42.31`
- seed 2: final `41.97`, comm `20390.32 MB`, `-6 dB 39.40`, `12 dB 42.72`
- mean: final `41.91`, comm `19608.50 MB`, `-6 dB 39.37`, `12 dB 42.52`

### Method 1: Importance-Aware Repetition

- 설정: `importance_repetition_enable=1`, `importance_repetition_topk=32`
- seed 1: final `38.61`, comm `20716.35 MB`, `-6 dB 36.44`, `12 dB 38.88`
- seed 2: final `39.89`, comm `21829.83 MB`, `-6 dB 38.50`, `12 dB 40.12`
- mean: final `39.25`, comm `21273.09 MB`, `-6 dB 37.47`, `12 dB 39.50`

판단:

- baseline 대비 정확도와 강건성이 모두 하락했고 comm도 증가했다.
- 현재 설정의 `topk=32` repetition은 승격 후보가 아니다.

### Method 2: Base-Support + Refinement-Support

- 설정: `base_refinement_enable=1`, `base_support_k=128`, `refinement_support_k=128`
- seed 1: final `41.71`, comm `17246.44 MB`, `-6 dB 39.03`, `12 dB 42.35`
- seed 2: final `42.85`, comm `17482.44 MB`, `-6 dB 40.62`, `12 dB 43.40`
- mean: final `42.28`, comm `17364.44 MB`, `-6 dB 39.83`, `12 dB 42.88`

판단:

- baseline 대비 final acc, `-6 dB`, `12 dB`가 모두 개선되었다.
- 동시에 total comm가 `~2.24 GB` 감소했다.
- 이번 suite의 1차 승격 후보는 `method2`다.

### Method 3: Learned CSI-Aware Masking

- 설정: `csi_source_mask_enable=1`
- seed 1: final `39.90`, comm `18544.15 MB`, `-6 dB 37.37`, `12 dB 40.72`
- seed 2: final `39.97`, comm `18889.65 MB`, `-6 dB 38.48`, `12 dB 40.25`
- mean: final `39.94`, comm `18716.90 MB`, `-6 dB 37.92`, `12 dB 40.48`

판단:

- comm는 baseline보다 줄었지만 정확도와 강건성 손실이 컸다.
- 현재 구현 상태에서는 승격 후보가 아니다.

### Method 4: Server-Side Feature Denoising / Imputation

- 설정: `server_feature_impute_enable=1`
- seed 1: final `40.47`, comm `19417.60 MB`, `-6 dB 38.21`, `12 dB 41.14`
- seed 2: final `40.97`, comm `20178.02 MB`, `-6 dB 39.55`, `12 dB 41.17`
- mean: final `40.72`, comm `19797.81 MB`, `-6 dB 38.88`, `12 dB 41.16`

판단:

- baseline과 매우 가깝지만, 정확도와 `-6 dB`는 약간 낮고 comm는 약간 높다.
- 현 단계에선 baseline 대체 후보로 보기 어렵다.

## 외부 기준과의 비교

기존 `Rayleigh n_clients=8` benchmark 기준:

- `SC-USFL`: final `39.99`, comm `21170.89 MB`, `-6 dB 39.69`, `12 dB 40.79`
- `SFL`: final `48.67`, comm `153673.56 MB`, `-6 dB 42.71`, `12 dB 50.46`

`method2`는 `SC-USFL`와 비교하면:

- final acc: `42.28 > 39.99`
- comm: `17364.44 MB < 21170.89 MB`
- `-6 dB`: `39.83 > 39.69`
- `12 dB`: `42.88 > 40.79`

즉, `method2`는 현재 확인된 범위에서 `SC-USFL`를 전반적으로 앞선다.

반면 `SFL`과 비교하면:

- accuracy / robustness는 아직 낮다.
- 하지만 comm는 압도적으로 적다.

## 결론

- 이번 suite는 완료되었고, 4개 방법 모두 `seed=1,2`가 생성되었다.
- `method2: base-support + refinement-support`만이 baseline 대비 일관된 개선 신호를 보였다.
- 다음 단계는 `method2`를 단독 후보로 승격해서
  - seed 확장
  - AWGN 재현
  - `base_support_k`, `refinement_support_k` sweep
  으로 넘어가는 것이 맞다.
