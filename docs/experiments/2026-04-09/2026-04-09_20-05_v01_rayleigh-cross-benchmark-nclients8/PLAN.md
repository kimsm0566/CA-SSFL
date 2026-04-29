# 실험 계획

## 메타데이터

- 실험 id: `2026-04-09_20-05_v01_rayleigh-cross-benchmark-nclients8`
- 시작 일시: `2026-04-09 20:05 KST`
- 상태: `planned`
- 담당자: `Codex`

## 목적

기존 `Rayleigh` 9-client benchmark를 `n_clients=8`로 다시 맞춰 재실행한다. 기존 9-client 결과는 채널 비교 참고용으로만 남기고, 이후 주 비교는 8-client 기준으로 통일한다.

## 질문

1. `n_clients=8`로 다시 맞추면 `SFL`, `SC-USFL`, `SSFLv6 baseline`, `SSFLv6 candidate`의 상대 순위가 어떻게 바뀌는가?
2. `SSFLv6 candidate`는 `Rayleigh`에서도 `SC-USFL` 대비 정확도, 저 SNR 강건성, 통신량 우위를 유지하는가?
3. `AWGN n_clients=8` 결과와 같은 client count 기준으로 두 채널 비교가 가능해지는가?

## 실행 범위

- 채널:
  - `rayleigh`
- 알고리즘:
  - `SFL`
  - `SC-USFL`
  - `SSFLv6 baseline`
  - `SSFLv6 candidate`
- seed set:
  - `1,2,3,4`

## 고정 조건

- dataset: `cifar10`
- partition_type: `class`
- n_clients: `8`
- n_client_data: `3000`
- batch_size: `100`
- n_epochs: `1`
- n_rounds: `200`
- Docker GPU runtime 사용

## 알고리즘별 설정

- `SFL`
  - `algorithm=SFL`
  - `compressed_dim=4096`
- `SC-USFL`
  - `algorithm=SC-USFL`
  - `compressed_dim=1352`
- `SSFLv6 baseline`
  - `algorithm=SSFLv6`
  - `compressed_dim=4096`
  - `beta=0.01`
  - `pruning_threshold=1.0`
  - `film_max_t=0.7`
  - `film_min_t=0.4`
  - `semantic_spreading_enable=0`
  - `snr_adaptive_beta_enable=0`
  - `semantic_power_enable=0`
- `SSFLv6 candidate`
  - 위와 동일하되
  - `semantic_spreading_enable=1`
  - `snr_adaptive_beta_enable=1`

## 산출물 경로

- 결과 루트:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-09-rayleigh-cross-benchmark-nclients8`

## 성공 기준

- 16개 런이 모두 완료
- 각 조합의 `seed_*.npz`가 모두 생성
- 평균/분산 및 `-6 dB` 비교가 가능
