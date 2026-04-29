# 실험 스펙

## 메타데이터

- 실험 id: `2026-03-29_20-32_v01_ssflv6-ablations`
- 시작 일시: `2026-03-29 20:32 KST`
- 상태: `seed=1 trend/full 완료, 추가 seed 대기`
- 담당자: `Codex + 사용자`

## 요약

이 시도는 Docker GPU 경로를 canonical 실행기로 고정한 상태에서 `SSFLv6` baseline과 세 가지 ablation(`w_o_vib`, `w_o_film`, `w_o_beta`)을 동일 조건으로 다시 실행해 비교하는 실험이다. 각 설정은 full run 전에 개별 smoke test를 먼저 통과해야 하며, raw artifact는 새 실험 폴더 아래 분리 저장한다.

현재 실행 단계에서는 comm-debug 중 들어간 threshold 수정을 제거하고, 원래 threshold 식으로 되돌린 뒤 `seed=1`, `n_rounds=20` exploratory trend run과 `seed=1`, `n_rounds=200` full run을 모두 완료했다. 남은 범위는 필요 시 `seed 2,3,4` 확장이다.

## 질문

현재 코드베이스에서 `SSFLv6`의 VIB, FiLM, beta scheduler 중 어떤 구성요소가 정확도와 누적 통신량에 가장 큰 기여를 하는가?

## 가설

동일한 Docker GPU 실행 경로와 matched 설정에서 baseline `SSFLv6`는 세 ablation보다 더 나은 communication-performance trade-off를 보일 가능성이 높다.

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
  - `beta=0.0005`
  - `pruning_threshold=1.0`
  - `seed_set=1,2,3,4`
- 기준선 산출물 경로:
  - `/workspace/docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/ssflv6/full`
- 이 비교가 적절한 이유:
  - 세 ablation은 모두 `SSFLv6` 내부 구성요소 제거 실험이므로 baseline `SSFLv6`가 직접 비교 기준이다.

## 고정 조건

- dataset: `cifar10`
- partition_type: `class`
- n_clients:
  - smoke: `2`
  - full: `9`
- n_client_data:
  - smoke: `10`
  - full: `3000`
- batch_size:
  - smoke: `10`
  - full: `100`
- n_epochs: `1`
- n_rounds:
  - smoke: `1`
  - trend rerun: `20`
  - full: `200`
- channel_type: `rayleigh`
- snr_db: `12`
- use_private_SGD: `0`
- optimizer: `adam`
- lr: `0.001`
- seed_set:
  - smoke: `1`
  - trend rerun: `1`
  - full sweep target: `1,2,3,4`
- evaluation_path:
  - Docker GPU `run-exp` wrapper only
  - smoke 후 full run
  - 학습 종료 후 기본 multi-SNR evaluation 포함

## 변경 변수

- 대상 코드 경로:
  - 코드 변경 없음이 기본
  - 실행 및 기록 경로:
    - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/`
- 바꾸는 변수:
  - `algorithm`만 변경:
    - `SSFLv6`
    - `SSFLv6_w_o_vib`
    - `SSFLv6_w_o_film`
    - `SSFLv6_w_o_beta`
- 탐색 범위:
  - 알고리즘 ablation 비교만 수행
  - 하이퍼파라미터 탐색은 이번 범위 밖

## 지표

### 주요 지표

- 최종 테스트 정확도
- 누적 통신량

### 보조 지표

- multi-SNR 정확도
- seed 평균 및 표준편차
- 학습 안정성

## 검증 계획

### 스모크 체크

- 명령어:
  - `docker compose run --rm sfl-semantic check-gpu`
  - 각 알고리즘별:
    - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=<algo> --channel_type=rayleigh --partition_type=class --n_clients=2 --n_client_data=10 --batch_size=10 --n_epochs=1 --n_rounds=1 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/<algo>/smoke`
- 성공 신호:
  - 종료 코드 `0`
  - `.npz` 저장 성공
  - 서버/클라이언트 로그 생성

### 매칭 비교

- 명령어:
  - 각 알고리즘별 seed `1,2,3,4`:
    - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=<algo> --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=200 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=<seed> --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/<algo>/full`
- 예상 산출물 경로:
  - `/workspace/docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/ssflv6/full`
  - `/workspace/docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/ssflv6_w_o_vib/full`
  - `/workspace/docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/ssflv6_w_o_film/full`
  - `/workspace/docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/ssflv6_w_o_beta/full`

### 강건성 후속 검증

- 추가 seed:
  - 이번 범위에서 `1,2,3,4`까지만 사용
- 추가 SNR:
  - 학습 후 기본 multi-SNR evaluation 결과만 사용
- 추가 channel 설정:
  - 이번 범위 밖

## 승격 기준

이번 시도는 ablation 비교 실험이므로 바로 default 승격을 목표로 하지 않는다. 다만 baseline `SSFLv6`가 반복 실행에서도 세 ablation보다 일관되게 더 나은 communication-performance trade-off를 보이면, 후속 intervention 우선순위를 정하는 근거로 승격한다.

## 중단 기준

다음 중 하나가 발생하면 해당 설정의 full run은 중단 또는 보류한다.

- smoke test 실패
- Docker GPU 경로에서 재현 가능한 실행 오류 발생
- artifact 저장 구조가 비교 가능성을 깨뜨릴 정도로 어긋남

## 리스크와 교란 요인

- 가능한 교란 요인:
  - 긴 Docker 실행 시간
  - 단일 GPU에서 MPI rank 10개가 `cuda:0`를 공유하는 구조
  - 기존 코드의 결과 저장 스키마가 알고리즘별로 완전히 동일하지 않을 가능성
- 예상 실패 모드:
  - smoke는 통과하지만 full run에서 메모리 또는 시간 이슈 발생
  - Docker runtime 또는 MPI 종료 오류
- 결과를 무효화할 수 있는 요소:
  - 설정 간 고정 조건 불일치
  - smoke 결과를 final comparison처럼 해석하는 경우
