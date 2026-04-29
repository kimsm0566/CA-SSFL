# 2026-04-15 v01 w/o semantic mask ablation spec

## 목적

`w/o semantic mask only`를 채널별 best hyperparameter 기준으로 측정한다.

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

- algorithm: `SSFLv6`
- `beta=0.05`
- `pruning_threshold=0.0`
- `film_max_t=0.7`
- `film_min_t=0.2`

### Rayleigh

- algorithm: `SSFLv6`
- `beta=0.1`
- `pruning_threshold=0.0`
- `film_max_t=0.7`
- `film_min_t=0.4`

## 비교 대상

### baseline 재사용

- `CA-SSFL`
  - AWGN: `beta=0.05`, `tau=1.0`, `film=0.7/0.2`
  - Rayleigh: `beta=0.1`, `tau=1.0`, `film=0.7/0.4`

### 기존 ablation 재사용

- `SSFLv6_w_o_film`
  - 동일 seed set, 동일 channel-specific best setting

### 새 실행

- `SSFLv6`, `pruning_threshold=0.0`

## 결과 저장 경로

- result root:
  - `/workspace/tmp/2026-04-15/2026-04-15-cifar10-wo-semantic-mask-ablation`

## 예상 실행 수

- `2 channels x 4 seeds = 8 runs`

## 예상 시간

- run당 약 `7~8분`
- 총 약 `60~75분`

## 시간 추정 전제

- 최근 동일 조건 `cifar10` 런타임 기준
- 큐 중단 없이 연속 실행되는 경우

## 검증

- `bash -n` on runner
- artifact skip/continue 동작 확인
- 결과 비교는 아래 지표로 수행

## 보고 지표

- final accuracy
- total communication
- `-6 dB`
- `12 dB`

## 해석 규칙

- 이 ablation은 `semantic mask only`의 기여를 본다
- `VIB loss`, sampling, FiLM은 제거되지 않았으므로 `w/o VIB`로 표기하지 않는다
- 결과 문서와 표에서는 `w/o semantic mask`로 표기한다
