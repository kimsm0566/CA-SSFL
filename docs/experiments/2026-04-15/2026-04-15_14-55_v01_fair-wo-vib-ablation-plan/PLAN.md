# 2026-04-15 v01 fair w/o VIB ablation plan

## 배경

현재 `SSFLv6_w_o_vib` 결과는 `10%`대 정확도로 사실상 붕괴했다.  
코드 확인 결과, 이 설정은 단순히 `KL loss`만 제거한 것이 아니라 아래를 동시에 제거한다.

- `conv_var` head 제거
- reparameterization 제거
- `KL loss` 제거
- `KL` 기반 semantic mask 제거
- `KL` 기반 support score 제거

즉 현재 `w/o VIB`는 `w/o FiLM`과 같은 수준의 단일 ablation이 아니라, semantic bottleneck 전체를 사실상 비활성화한 강한 제거 실험이다. 이 결과를 그대로 `VIB ablation`으로 해석하는 것은 공정하지 않다.

## 목표

`w/o FiLM`과 같은 수준의 공정한 `w/o VIB` ablation을 다시 정의한다.

구체적으로는:

- `FiLM` ablation이 "channel-aware gating만 제거"하는 것처럼
- `VIB` ablation도 "VIB regularization/stochasticity만 제거"하고
- semantic selection 기능 자체는 유지되도록 구성한다.

## 설계 원칙

### 유지할 것

- 동일한 backbone
- 동일한 split learning 구조
- 동일한 decoder / server classifier
- 동일한 communication accounting
- 동일한 `FiLM` 경로
- 동일한 채널별 best hyperparameter

### 제거할 것

- `KL loss`
- stochastic reparameterization

### 유지해야 하는 기능

- semantic score 기반 support selection
- semantic mask 기반 pruning

즉 현재처럼 `vib_mask = all ones`로 두면 안 된다.

## 제안하는 공정한 w/o VIB 정의

### 정의

`w/o VIB (fair)`는 아래로 정의한다.

- latent는 deterministic하게 `z = mu`
- `KL loss`는 사용하지 않음
- semantic score는 `KL` 대신 deterministic proxy로 계산
- proxy semantic score를 이용해 semantic mask와 support selection을 유지

### proxy semantic score 후보

1. `batch_mean(|mu|)`
2. `batch_mean(mu^2)`
3. `batch_mean(|mu|)`를 정규화한 값

현재 우선 후보는 `batch_mean(|mu|)`이다.

이유:

- 구현이 단순함
- deterministic latent importance proxy로 해석 가능
- `KL`이 사라져도 semantic ranking을 유지할 수 있음

## threshold 문제

현재 `pruning_threshold=1.0`은 `KL` 값 기준으로 튜닝된 값이라서, 그대로 `|mu|` score에 쓰면 공정하지 않을 수 있다.

따라서 아래 두 방법 중 하나가 필요하다.

1. `matched-active-budget`
   - baseline `CA-SSFL`의 평균 active count에 맞춰 top-k 선택
2. `score-threshold recalibration`
   - proxy score에 맞는 새 threshold를 별도 탐색

이번 목적은 공정한 ablation이므로, 우선은 `matched-active-budget`이 더 적절하다.

## 1차 구현 방향

### baseline 기준

- `AWGN`: `beta=0.05`, `tau_VIB=1.0`, `film=0.7/0.2`
- `Rayleigh`: `beta=0.1`, `tau_VIB=1.0`, `film=0.7/0.4`

### fair w/o VIB 규칙

- `KL loss` 제거
- `z = mu`
- semantic score = `mean(abs(mu), dim=batch)`
- semantic candidate selection은 `top-k`로 수행
- `k`는 matched baseline active budget으로 맞춤

## 검증 계획

1. 작은 smoke
   - `AWGN`, `seed=1`, `1 round`
   - active count와 comm가 baseline과 같은 scale인지 확인
2. exploratory
   - `AWGN`, `Rayleigh`
   - `seed 1,2,3,4`
   - baseline vs `w/o VIB (fair)` 비교
3. 평가 지표
   - final accuracy
   - total comm
   - `-6 dB`
   - active count distribution

## 예상 실행 수

- smoke: `1 run`
- exploratory: `2 channels x 4 seeds = 8 runs`

## 예상 시간

- smoke: 약 `5~10분`
- exploratory: run당 `7~8분`, 총 `60~80분`
- 전체: 약 `1시간 10분 ~ 1시간 30분`

## 시간 추정 전제

- 최근 `cifar10`, `n_clients=8`, `200 rounds` 런타임 기준
- 큐 중단/재시작 없이 정상 종료되는 경우

## 성공 기준

공정한 ablation으로 받아들이려면:

- 정확도가 현재 `10%`대 붕괴에서 벗어나야 함
- 통신량이 baseline 대비 크게 비정상적으로 튀지 않아야 함
- active count가 baseline과 비교 가능한 scale이어야 함

이 조건을 만족해야 `VIB의 실제 기여`를 해석할 수 있다.
