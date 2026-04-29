# 실험 스펙

## 메타데이터

- 실험 id: `2026-03-30_00-18_v01_ssflv6-seed2-oldcode-repro`
- 시작 일시: `2026-03-30 00:18 KST`
- 상태: 진행중
- 담당자: Codex

## 요약

사용자가 최근 되돌린 `_run_clientv6`와 `FiLMChannelAwareEncoder` 기준으로 `SSFLv6` `seed=2`를 Docker GPU 경로에서 full `200`라운드 재실행하고, 과거 raw `seed_2` 및 직전 canonical rerun과 직접 비교한다.

## 질문

사용자가 복원한 예전 실험 코드가 과거 raw `seed=2`의 낮은 통신량과 낮은 active ratio를 다시 만들어내는가?

## 가설

`_run_clientv6`와 `FiLMChannelAwareEncoder`를 예전 실험 코드로 되돌리면 `seed=2`에서 total comm와 active ratio가 직전 canonical rerun보다 유의하게 감소하고, 과거 raw `seed_2`에 가까워진다.

## 기준선

- 기준선 알고리즘: `SSFLv6`
- 기준선 설정:
  - current canonical rerun: `beta=0.0005`, `pruning_threshold=1.0`, `seed=2`
  - historical raw artifact: 동일 nominal setting
- 기준선 산출물 경로:
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-rerun-seed2/SSFLv6/full/`
  - `src/results/cifar10/n_clients_9/n_client_data_3000/batch_size_100/data_partition_type_class/model_type_resnetv2/major_percent_0.7/n_epochs_1/beta_0.0005/pruning_threshold_1.0/SSFLv6/snr_12/compress_4096/channel_type_rayleigh/`
- 이 비교가 적절한 이유:
  - 알고리즘, seed, 데이터, 통신 조건이 nominal하게 일치한다

## 고정 조건

- dataset: `cifar10`
- partition_type: `class`
- n_clients: `9`
- n_client_data: `3000`
- batch_size: `100`
- n_epochs: `1`
- n_rounds: `200`
- channel_type: `rayleigh`
- seed_set: `2`
- evaluation_path: Docker GPU `docker compose run --rm sfl-semantic run-exp`

## 변경 변수

- 대상 코드 경로:
  - `src/utils/trainer.py`
  - `src/models/model.py`
- 바꾸는 변수:
  - `_run_clientv6` 내부 mask/gradient/comm 계산 경로
  - `FiLMChannelAwareEncoder` 구조
- 탐색 범위:
  - 사용자가 이미 반영한 현재 작업트리 상태 그대로 1회 재현

## 지표

### 주요 지표

- 최종 테스트 정확도
- 누적 통신량

### 보조 지표

- `Total data comm`
- `Total model comm`
- round `190~199` client 8 active ratio
- `Test SNR 12dB`

## 검증 계획

### 스모크 체크

- 명령어: 생략
- 성공 신호: 기존 Docker GPU harness가 직전 run들에서 정상 확인됨

### 매칭 비교

- 명령어:
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=200 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=2 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-30_00-18_v01_ssflv6-seed2-oldcode-repro/artifacts/full`
- 예상 산출물 경로:
  - `docs/experiments/2026-03-30_00-18_v01_ssflv6-seed2-oldcode-repro/artifacts/full/`

### 강건성 후속 검증

- 추가 seed: 미정
- 추가 SNR: 없음
- 추가 channel 설정: 없음

## 승격 기준

`seed=2` 결과가 직전 canonical rerun 대비 통신량과 active ratio를 명확히 낮추고, accuracy를 크게 잃지 않으면 재현 성공으로 본다.

## 중단 기준

실험이 shape mismatch 등으로 실패하거나, 결과가 canonical rerun과 거의 같으면 이 경로는 재현 원인으로 보기 어렵다.

## 리스크와 교란 요인

- 가능한 교란 요인:
  - 사용자가 복원한 코드가 정확히 old raw 시점 코드와 다를 수 있음
- 예상 실패 모드:
  - encoder 차원 불일치
  - sparse gradient 복원 shape 오류
- 결과를 무효화할 수 있는 요소:
  - 명시되지 않은 다른 파일 변화
