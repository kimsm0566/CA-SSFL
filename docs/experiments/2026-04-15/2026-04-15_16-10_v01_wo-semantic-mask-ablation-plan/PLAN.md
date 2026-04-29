# 2026-04-15 v01 w/o semantic mask ablation plan

## 배경

직전 `w/o VIB` ablation은 사용자의 의도와 달랐다.

사용자 의도:

- `semantic mask`만 제거한 경우를 보고 싶음

직전 구현:

- `KL loss`
- stochastic sampling
- `KL` 기반 semantic mask
- `KL` 기반 support score

를 함께 제거하는 강한 ablation이었다.

따라서 해당 결과는 `w/o semantic mask` 해석에 적합하지 않다.

## 목표

`w/o semantic mask only`를 공정하게 측정한다.

즉 아래는 유지한다.

- `KL loss`
- VIB parameterization
- stochastic sampling
- FiLM
- backbone / decoder / split 구조

그리고 semantic pruning mask만 사실상 끈다.

## 구현 방식

현재 코드에서 semantic mask는:

- `vib_mask = (kl_mean_batch > pruning_threshold).float()`

로 정의된다.

따라서 이번 ablation은:

- `SSFLv6` 알고리즘 그대로 사용
- `pruning_threshold = 0.0`

으로 두어 `vib_mask ≈ all ones`가 되도록 한다.

이 방식은 새로운 알고리즘 분기를 만들지 않아도 되며, 사용자의 의도와 가장 가깝다.

## 비교 대상

### baseline 재사용

- `CA-SSFL`

### 기존 ablation 재사용

- `w/o FiLM`

### 새 실행

- `w/o semantic mask only`
  - 구현: `SSFLv6`, `pruning_threshold=0.0`

## 채널별 고정점

### AWGN

- `beta=0.05`
- `film_max_t=0.7`
- `film_min_t=0.2`

### Rayleigh

- `beta=0.1`
- `film_max_t=0.7`
- `film_min_t=0.4`

## 실행 범위

- dataset: `cifar10`
- `n_clients=8`
- seed: `1,2,3,4`
- channel: `AWGN`, `Rayleigh`

새로 필요한 실행은 총 `8 runs`이다.

## 검증

1. runner 문법 검증
2. artifact path 검증
3. 본 실행 `8 runs`

코드 변경은 없으므로 별도 py_compile은 불필요하다.

## 예상 실행 수

- main only: `8 runs`

## 예상 시간

- run당 약 `7~8분`
- 총 약 `60~75분`

## 시간 추정 전제

- 최근 `cifar10`, `n_clients=8`, `200 rounds` 기준
- 하네스 재시작 없이 연속 종료되는 경우

## 성공 기준

`w/o semantic mask only`는 최소한 다음을 보여야 해석 가치가 있다.

- `w/o VIB`처럼 `10%` 수준으로 붕괴하지 않을 것
- baseline 대비 정확도 하락이 있더라도 해석 가능한 범위일 것
- 통신량은 semantic mask 제거에 따라 증가하는 방향으로 일관될 것
