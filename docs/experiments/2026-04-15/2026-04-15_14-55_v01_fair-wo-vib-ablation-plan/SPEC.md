# 2026-04-15 v01 fair w/o VIB ablation spec

## 목적

기존 `SSFLv6_w_o_vib`가 과도하게 많은 기능을 동시에 제거하고 있어 공정한 ablation으로 해석하기 어렵다는 문제를 수정한다.

이번 실행에서는 새 알고리즘 `SSFLv6_w_o_vib_fair`를 도입한다.

## 고정 조건

- dataset: `cifar10`
- partition: `class`
- `n_clients=8`
- `n_client_data=3000`
- `batch_size=100`
- `n_epochs=1`
- `n_rounds=200`
- `compressed_dim=4096`
- seed: `1,2,3,4`

## 채널별 대표 설정

### AWGN

- `beta=0.05`
- `pruning_threshold=1.0`
- `film_max_t=0.7`
- `film_min_t=0.2`

### Rayleigh

- `beta=0.1`
- `pruning_threshold=1.0`
- `film_max_t=0.7`
- `film_min_t=0.4`

## 알고리즘 정의

### baseline 재사용

- `SSFLv6`
- 기존 채널별 best artifact 재사용

### 비교 대상

- `SSFLv6_w_o_film`
  - 기존 ablation artifact 재사용
- `SSFLv6_w_o_vib_fair`
  - 이번에 새로 실행

## `SSFLv6_w_o_vib_fair` 정의

- `KL loss` 제거
- stochastic reparameterization 제거
- latent는 deterministic하게 `z = mu`
- semantic score는 `mean(abs(mu), dim=batch)`를 사용
- semantic score는 `score / mean(score)`로 정규화
- semantic mask는 `normalized_score > pruning_threshold`
- support score는 `normalized_score * chan_mask`

즉 `VIB regularization`은 제거하되, semantic selection 경로 자체는 deterministic proxy로 유지한다.

## 구현 제약

- 기존 `SSFLv6_w_o_vib` 의미는 바꾸지 않는다
- 새 알고리즘 이름으로 분리하여 재현성 보존
- 결과 경로는 알고리즘 이름 기준으로 분리 저장

## 검증

### 정적 검증

- `python3 -m py_compile` on touched files
- `bash -n` on new runner

### smoke

- `AWGN`
- `SSFLv6_w_o_vib_fair`
- `seed=1`
- `n_rounds=1`

확인 항목:

- 실행 정상 종료
- artifact 저장
- active/support 경로가 channel-only all-ones가 아닌지 로그로 확인
- 통신량이 기존 `w_o_vib`처럼 비정상적으로 폭증하지 않는지 확인

### 본 실행

- `AWGN`, `Rayleigh`
- 각각 `seed 1,2,3,4`
- 총 `8 runs`

## 결과 비교 기준

- final accuracy
- total communication
- `-6 dB`
- `12 dB`

비교 대상:

- `CA-SSFL` baseline
- `SSFLv6_w_o_film`
- `SSFLv6_w_o_vib_fair`

## 예상 실행 수

- smoke: `1 run`
- main: `8 runs`
- 총 `9 runs`

## 예상 시간

- smoke: 약 `5~10분`
- main: run당 `7~8분`, 총 `60~80분`
- 전체: 약 `1시간 10분 ~ 1시간 30분`

## 시간 추정 전제

- 최근 `cifar10`, `n_clients=8`, `200 rounds` 기준
- Docker GPU runtime 정상
- 하네스 재시작 없이 연속 실행되는 경우
