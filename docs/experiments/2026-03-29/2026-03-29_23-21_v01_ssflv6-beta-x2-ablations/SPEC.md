# 실험 스펙

## 메타데이터

- 실험 id: `2026-03-29_23-21_v01_ssflv6-beta-x2-ablations`
- 시작 일시: `2026-03-29 23:21 KST`
- 상태: `진행중`
- 담당자: `Codex + 사용자`

## 요약

이 시도는 기존 `SSFLv6` ablation 비교의 고정 조건을 유지한 채 `beta`만 `0.0005 -> 0.001`로 올려 baseline과 세 ablation을 다시 비교하는 실험이다. 사용자의 지시에 따라 trend/smoke를 생략하고 네 알고리즘 모두 `seed=1`, `n_rounds=200` full run으로 바로 실행한다.

## 질문

`beta=0.001` 조건에서 `SSFLv6` baseline과 `w_o_vib`, `w_o_film`, `w_o_beta`의 communication-performance trade-off는 기존 `beta=0.0005` 대비 어떻게 달라지는가?

## 가설

`beta`를 두 배 올리면 baseline `SSFLv6`의 정보 병목이 더 강해져 통신량이 낮아지거나 정확도-통신량 균형이 이동할 수 있다. 반면 `w_o_beta`는 scheduler 부재 특성상 상대적 이득/손실이 달라질 수 있다.

## 기준선

- 기준선 알고리즘: `SSFLv6`
- 기준선 설정:
  - `dataset=cifar10`
  - `partition_type=class`
  - `n_clients=9`
  - `n_client_data=3000`
  - `batch_size=100`
  - `n_epochs=1`
  - `n_rounds=200`
  - `model_type=resnetv2`
  - `channel_type=rayleigh`
  - `snr_db=12`
  - `use_private_SGD=0`
  - `optimizer=adam`
  - `lr=0.001`
  - `compressed_dim=4096`
  - `beta=0.001`
  - `pruning_threshold=1.0`
  - `seed=1`
- 비교용 기존 결과:
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-full200/...`

## 고정 조건

- dataset: `cifar10`
- partition_type: `class`
- n_clients: `9`
- n_client_data: `3000`
- batch_size: `100`
- n_epochs: `1`
- n_rounds: `200`
- channel_type: `rayleigh`
- snr_db: `12`
- use_private_SGD: `0`
- optimizer: `adam`
- lr: `0.001`
- compressed_dim: `4096`
- pruning_threshold: `1.0`
- seed_set: `1`
- evaluation_path:
  - Docker GPU `run-exp` wrapper only
  - 학습 종료 후 기본 multi-SNR evaluation 포함

## 변경 변수

- 대상 코드 경로:
  - 코드 변경 없음
  - 실행 및 기록 경로:
    - `docs/experiments/2026-03-29_23-21_v01_ssflv6-beta-x2-ablations/`
- 바꾸는 변수:
  - `algorithm`:
    - `SSFLv6`
    - `SSFLv6_w_o_vib`
    - `SSFLv6_w_o_film`
    - `SSFLv6_w_o_beta`
  - `beta=0.001`

## 지표

### 주요 지표

- round `200` 정확도
- round `200` 누적 통신량

### 보조 지표

- `Test SNR 12dB` 정확도
- `Total data comm`
- `Total model comm`

## 검증 계획

### 실행 체크

- 명령어:
  - `docker compose run --rm sfl-semantic check-gpu`
  - 각 알고리즘별 full run:
    - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=<algo> --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=200 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.001 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_23-21_v01_ssflv6-beta-x2-ablations/artifacts/<algo>/full`
- 성공 신호:
  - 종료 코드 `0`
  - `.npz` 저장 성공
  - server log 생성

## 승격 기준

이번 시도는 새 `beta` 강도에 대한 exploratory/full 비교다. `beta=0.001` 조건이 baseline `0.0005`보다 더 나은 communication-performance trade-off를 보일 때만 후속 seed 확장 후보로 승격한다.

## 중단 기준

- Docker GPU 실행 오류
- artifact 저장 구조 오류
- 명백한 학습 비정상 종료

## 리스크와 교란 요인

- `beta=0.001`이 accuracy를 과도하게 깎을 수 있다.
- `seed=1`만으로는 claim-making 비교가 아니다.
- `w_o_beta`는 scheduler 부재로 인해 `beta` 변경 해석이 baseline과 완전히 대칭이 아닐 수 있다.
