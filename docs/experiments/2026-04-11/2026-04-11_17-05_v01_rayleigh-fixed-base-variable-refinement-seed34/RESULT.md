# RESULT

## 요약

`Rayleigh`, `n_clients=8`, `seed=3,4` 확장 및 `seed=1,2,3,4` matched comparison 결과, `fixed base + variable refinement`는 더 이상 baseline 우위라고 보기 어렵다.

핵심:

- `seed=1,2`에서는 유망했다.
- 하지만 `seed=4`에서 후보가 크게 붕괴했다.
- 그 결과 `seed=1,2,3,4` 평균 기준으로는
  - baseline 대비 정확도와 `-6 dB`가 모두 낮아졌다.

즉 이 후보는 `통신량 절감형 exploratory candidate`로는 의미가 있지만, 현재 단계에서 안정적인 승격 후보는 아니다.

## Seed 3,4 결과

### Baseline: `CA-SSFL Orig`

- seed 3: final `40.65`, comm `20515.52 MB`, `-6 dB 38.90`, `12 dB 41.02`, best `42.30`
- seed 4: final `33.53`, comm `18732.81 MB`, `-6 dB 32.31`, `12 dB 34.06`, best `39.22`
- mean: final `37.09`, comm `19624.16 MB`, `-6 dB 35.61`, `12 dB 37.54`, best `40.76`

### `SC-USFL`

- seed 3: final `40.20`, comm `21189.58 MB`, `-6 dB 39.46`, `12 dB 40.31`, best `41.53`
- seed 4: final `34.36`, comm `21178.43 MB`, `-6 dB 35.14`, `12 dB 35.62`, best `37.14`
- mean: final `37.28`, comm `21184.01 MB`, `-6 dB 37.30`, `12 dB 37.97`, best `39.34`

### Candidate: `fixed base + variable refinement`

- seed 3: final `42.54`, comm `15357.66 MB`, `-6 dB 39.34`, `12 dB 42.74`, best `42.54`
- seed 4: final `28.31`, comm `15392.62 MB`, `-6 dB 27.86`, `12 dB 27.29`, best `34.38`
- mean: final `35.42`, comm `15375.14 MB`, `-6 dB 33.60`, `12 dB 35.02`, best `38.46`

## Seed 1,2,3,4 Matched Comparison

### Baseline: `CA-SSFL Orig`

- mean: final `39.50 ± 3.49`
- comm: `19616.33 ± 838.41 MB`
- `-6 dB`: `37.49 ± 3.00`
- `12 dB`: `40.03 ± 3.50`
- best: `41.95 ± 1.61`

### `SC-USFL`

- mean: final `38.63 ± 2.78`
- comm: `21177.45 ± 7.68 MB`
- `-6 dB`: `38.49 ± 2.50`
- `12 dB`: `39.38 ± 2.66`
- best: `40.44 ± 2.08`

### Candidate: `fixed base + variable refinement`

- mean: final `38.64 ± 5.97`
- comm: `15328.20 ± 77.26 MB`
- `-6 dB`: `36.65 ± 5.08`
- `12 dB`: `38.66 ± 6.58`
- best: `41.69 ± 4.40`

## 비교 해석

### Candidate vs Baseline

- final acc: `39.50 -> 38.64` (`-0.86%p`)
- comm: `19616.33 -> 15328.20 MB` (`-4288.13 MB`)
- `-6 dB`: `37.49 -> 36.65` (`-0.84%p`)
- `12 dB`: `40.03 -> 38.66` (`-1.36%p`)

해석:

- comm 절감은 크다.
- 하지만 정확도와 강건성 손실이 함께 발생한다.
- 따라서 `정확도 거의 유지하면서 comm 절감`이라는 `seed=1,2` 결론은 `seed=1,2,3,4`까지 확장하면 유지되지 않는다.

### Candidate vs `SC-USFL`

- final acc: `38.64 vs 38.63` (`+0.01%p`)
- comm: `15328.20 MB vs 21177.45 MB` (`-5849.24 MB`)
- `-6 dB`: `36.65 vs 38.49` (`-1.84%p`)
- `12 dB`: `38.66 vs 39.38` (`-0.71%p`)

해석:

- final acc는 사실상 같다.
- comm는 후보가 훨씬 낮다.
- 하지만 Rayleigh 저 SNR 강건성은 `SC-USFL`가 더 낫다.

즉 `SC-USFL`를 전반적으로 이긴다고 말하기도 어렵다.

## 결론

- 사용자 관찰대로 `seed=3,4`, 특히 `seed=4`에서 후보가 크게 흔들렸다.
- 그래서 그래프에서 `CA-SSFL`가 `SC-USFL`보다 낮아 보인 현상은 단순 seed mismatch만의 문제는 아니다.
- `fixed base + variable refinement`는 `comm-lean exploratory` 후보로는 의미가 있지만,
  - 현재 4-seed 기준으로는
  - baseline 대체 후보나 명확한 개선안으로 승격할 수 없다.

현재 판단:

- `seed=1,2` 결과만으로 promote 하면 안 됨
- `seed=1,2,3,4` 기준에선 `iterate`
- 다음 단계는
  - 왜 `seed=4`가 붕괴했는지 로그/active support 분포 분석
  - 또는 고정형 `method2`를 `seed=3,4`까지 확장해 진짜로 더 안정적인지 확인

