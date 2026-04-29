# Table I Block B 채널별 재실험 결과

## 설정

- `AWGN`: `beta=0.05`, `tau_VIB=1.0`
- `Rayleigh`: `beta=0.1`, `tau_VIB=1.0`
- seeds: `1,2,3,4`

## AWGN

- 최고 final acc: `film_max_t=0.7`, `film_min_t=0.2` -> `Acc 41.71`, `Comm 14.03 GB`
- 최고 `-6 dB`: `film_max_t=0.7`, `film_min_t=0.4` -> `-6 dB 40.85`
- 최저 comm: `film_max_t=0.9`, `film_min_t=0.4` -> `Comm 11.55 GB`

## Rayleigh

- 최고 final acc: `film_max_t=0.7`, `film_min_t=0.4` -> `Acc 40.41`, `Comm 14.59 GB`
- 최고 `-6 dB`: `film_max_t=0.7`, `film_min_t=0.4` -> `-6 dB 37.88`
- 최저 comm: `film_max_t=0.9`, `film_min_t=0.4` -> `Comm 12.48 GB`
