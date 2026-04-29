# RESULT

## 요약

`Rayleigh`, `n_clients=8`, `seed=1,2` 기준에서 `fixed base + variable refinement`는 baseline `CA-SSFL Orig` 대비 정확도를 거의 유지하면서 통신량을 크게 줄였다.

- baseline `CA-SSFL Orig` 대비
  - final acc: `41.91 -> 41.86` (`-0.05%p`)
  - total comm: `19608.50 MB -> 15281.26 MB` (`-4327.24 MB`)
  - `-6 dB`: `39.37 -> 39.70` (`+0.33%p`)
  - `12 dB`: `42.52 -> 42.31` (`-0.20%p`)

즉 이 설정은 정확도 최우수 후보는 아니지만, `저 SNR 강건성은 유지 또는 소폭 개선`하면서 `통신량을 크게 줄이는` 쪽에 가깝다.

## 결과

### Baseline: `CA-SSFL Orig`

- seed 1: final `41.85`, comm `18826.68 MB`, `-6 dB 39.34`, `12 dB 42.31`, best `42.95`
- seed 2: final `41.97`, comm `20390.32 MB`, `-6 dB 39.40`, `12 dB 42.72`, best `43.31`
- mean: final `41.91`, comm `19608.50 MB`, `-6 dB 39.37`, `12 dB 42.52`, best `43.13`

### Candidate: `fixed base + variable refinement`

- 설정:
  - `base_refinement_enable=1`
  - `base_refinement_variable_enable=1`
  - `base_support_k=128`
  - `refinement_support_k=128`
- 동작:
  - `base`는 `KL` 기준 top-128로 고정
  - `refinement`는 남은 `vib_mask` 후보 중 `film_mask` 기준으로 선택
  - refinement 개수는 `snr_normalized`에 비례해 `0~128` 사이에서 가변

- seed 1: final `42.08`, comm `15196.27 MB`, `-6 dB 39.64`, `12 dB 42.80`, best `43.86`
- seed 2: final `41.64`, comm `15366.25 MB`, `-6 dB 39.77`, `12 dB 41.83`, best `45.98`
- mean: final `41.86`, comm `15281.26 MB`, `-6 dB 39.70`, `12 dB 42.31`, best `44.92`

## 비교 해석

### Baseline 대비

- final acc는 사실상 동일하다.
- `-6 dB`는 소폭 개선되었다.
- `12 dB`는 소폭 하락했다.
- total comm는 `4.33 GB` 줄었다.

해석:

- `base=128` 고정이 저 SNR에서 semantic core를 안정적으로 지켜준 것으로 보인다.
- 반면 좋은 채널에서는 refinement를 항상 128까지 꽉 채우지 않기 때문에, 고 SNR에서의 추가 성능 일부를 포기한 것으로 해석할 수 있다.

### 고정형 `method2` 대비

고정형 `method2` (`base=128`, `refinement=128` 고정)의 기존 결과:

- mean: final `42.28`, comm `17364.44 MB`, `-6 dB 39.83`, `12 dB 42.88`, best `44.69`

`variable refinement`는 그 대비:

- final acc: `-0.42%p`
- total comm: `-2083.18 MB`
- `-6 dB`: `-0.13%p`
- `12 dB`: `-0.57%p`

해석:

- 고정형 `method2`는 현재까지의 `정확도 최우수` 후보다.
- `variable refinement`는 정확도를 약간 양보하고 통신량을 더 줄인 `comm-lean` 후보다.

### `SC-USFL` 대비 (`seed=1,2`만 사용)

`SC-USFL` `seed=1,2` 기준:

- seed 1: final `41.79`, comm `21170.01 MB`, `-6 dB 41.92`, `12 dB 42.95`, best `42.74`
- seed 2: final `38.19`, comm `21171.76 MB`, `-6 dB 37.45`, `12 dB 38.63`, best `40.33`
- mean: final `39.99`, comm `21170.89 MB`, `-6 dB 39.69`, `12 dB 40.79`, best `41.53`

`fixed base + variable refinement`는 `SC-USFL seed=1,2` 대비:

- final acc: `41.86 > 39.99`
- total comm: `15281.26 MB < 21170.89 MB`
- `-6 dB`: `39.70 > 39.69`
- `12 dB`: `42.31 > 40.79`

해석:

- 이번 비교 범위에서는 `SC-USFL`를 정확도, 통신량, `-6 dB`, `12 dB` 모두에서 앞섰다.
- 특히 `-6 dB`는 사실상 동률에 가까우면서도 comm가 훨씬 낮다.

## 결론

- `fixed base + variable refinement`는 baseline 대비 `정확도 거의 유지 + comm 대폭 절감`을 달성했다.
- `SC-USFL seed=1,2`와 비교하면 전반적으로 우세하다.
- 다만 현재 최우수 정확도 후보는 여전히 고정형 `method2`다.

현재 판단:

- 정확도 우선 후보: 고정형 `method2`
- 통신 효율 우선 후보: `fixed base + variable refinement`

다음 단계는 두 후보를 나란히 두고

- seed 확장
- AWGN 재현
- `base_support_k`, `refinement_support_k`, refinement budget rule sweep

을 진행하는 것이다.
