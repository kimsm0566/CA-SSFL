# 실험 계획

## 메타데이터

- 실험 id: `2026-04-09_16-40_v01_cross-benchmark-rayleigh-awgn`
- 시작 일시: `2026-04-09 16:40 KST`
- 상태: `완료`
- 담당자: `Codex`

## 목적

현재 `SSFLv6` 계열 후보를 `SFL`, `SC-USFL`과 동일한 Docker GPU 실행 경로에서 다시 비교해, 논문용 표의 기준이 되는 matched multi-seed benchmark를 구축한다.

## 질문

1. 현재 코드 기준에서 `Rayleigh` 채널에서 `SFL`, `SC-USFL`, `SSFLv6 baseline`, `SSFLv6 + spreading + snr-adaptive beta`의 상대 위치는 어떻게 되는가?
2. `AWGN` 채널에서 적어도 `SFL`, `SC-USFL`를 같은 seed set으로 재측정했을 때 기존 기록과 얼마나 일치하는가?

## 실행 범위

- 채널:
  - `rayleigh`
  - `awgn`
- 알고리즘:
  - `SFL`
  - `SC-USFL`
  - `SSFLv6` baseline
  - `SSFLv6 + semantic_spreading + snr_adaptive_beta`
- 단, `AWGN`에서는 우선 사용자 요청에 따라 `SFL`, `SC-USFL`만 실행
- seed set:
  - `1,2,3,4`

## 고정 조건

- dataset: `cifar10`
- partition_type: `class`
- n_clients: `9`
- n_client_data: `3000`
- batch_size: `100`
- n_epochs: `1`
- n_rounds: `200`
- Docker GPU runtime 사용

## 알고리즘별 실행 설정

- `SFL`
  - `algorithm=SFL`
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
- `SSFLv6 candidate`
  - 위와 동일하되
  - `semantic_spreading_enable=1`
  - `snr_adaptive_beta_enable=1`

## 산출물 경로

- 기본 루트:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-09-cross-benchmark`

## 성공 기준

- 지정된 조합이 모두 Docker GPU 경로에서 완료
- 각 조합별 `seed_*.npz`가 저장
- 이후 seed 평균/표준편차 비교 가능
