# 실험 계획

## 메타데이터

- 실험 id: `2026-04-09_18-45_v01_awgn-threeway-benchmark-nclients8`
- 시작 일시: `2026-04-09 18:45 KST`
- 상태: `planned`
- 담당자: `Codex`

## 목적

`AWGN` 채널에서 `SFL`, `SC-USFL`, `SSFLv6 candidate`를 같은 Docker GPU 경로와 같은 seed set으로 다시 측정해, 우리 개선 버전의 위치를 동일 조건에서 확인한다.

동시에 `SSFLv6` 경로에는 가벼운 MPI trace 옵션을 추가해, 이후 Rayleigh stall 재현 시 어느 rank, 어느 send/recv 지점에서 멈추는지 바로 확인할 수 있게 한다.

## 질문

1. `AWGN`에서 `SSFLv6 candidate`는 `SFL`, `SC-USFL` 대비 정확도와 통신량에서 어느 위치인가?
2. `n_clients=8` 기준에서도 `SSFLv6 candidate`가 `SC-USFL` 대비 경쟁력을 유지하는가?
3. 추후 Rayleigh stall 디버깅에 필요한 최소 MPI trace가 현재 코드 경로에 안전하게 추가되었는가?

## 실행 범위

- 채널:
  - `awgn`
- 알고리즘:
  - `SFL`
  - `SC-USFL`
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
- `SSFLv6 candidate`
  - `algorithm=SSFLv6`
  - `compressed_dim=4096`
  - `beta=0.01`
  - `pruning_threshold=1.0`
  - `film_max_t=0.7`
  - `film_min_t=0.4`
  - `semantic_spreading_enable=1`
  - `snr_adaptive_beta_enable=1`
  - `semantic_power_enable=0`
  - `mpi_trace_enable=0`

## 산출물 경로

- 결과 루트:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-09-awgn-threeway-benchmark-nclients8`

## 성공 기준

- 각 조합의 `seed_*.npz`가 모두 생성
- seed 평균/분산 표를 만들 수 있음
- MPI trace 옵션 추가가 smoke에서 오류 없이 동작
