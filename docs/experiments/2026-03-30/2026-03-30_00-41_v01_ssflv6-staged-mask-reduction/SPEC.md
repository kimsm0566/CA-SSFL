# 실험 스펙

## 메타데이터

- 실험 id: `2026-03-30_00-41_v01_ssflv6-staged-mask-reduction`
- 시작 일시: `2026-03-30 00:41 KST`
- 상태: 완료
- 담당자: Codex

## 요약

`SSFLv6` 통신량 절감 후보를 단계적으로 적용한다. 이 시도에서는 stage 1, stage 2, stage 3 후보를 모두 `seed=2`, `200`라운드 full run으로 baseline과 비교했다. `20`라운드 trend는 비교 근거로 사용하지 않는다.

## 질문

batch 평균 VIB mask를 샘플별 VIB mask로 바꾸면 현재 wire format을 유지한 상태에서도 active 차원과 통신량이 줄어드는가?

## 가설

샘플별 VIB mask를 만들고 배치 내 union indices만 전송하면, 현재 batch-shared mask 대비 active 차원과 `data comm`가 감소한다.

## 기준선

- 기준선 알고리즘: `SSFLv6`
- 기준선 설정:
  - 현재 active 코드, `seed=2`, `beta=0.0005`, `pruning_threshold=1.0`
  - baseline 비교점은 current full run의 round `20`, `200`
- 기준선 산출물 경로:
  - `docs/experiments/2026-03-30_00-18_v01_ssflv6-seed2-oldcode-repro/artifacts/full/`
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-rerun-seed2/SSFLv6/full/`
- 이 비교가 적절한 이유:
  - 알고리즘, seed, 데이터, 채널, beta, threshold가 일치한다

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
  - stage 1: `vib_mask` 생성 방식과 `active_indices` 산출 방식
  - stage 2: FiLM gate 구조
  - stage 3: `beta`
- 탐색 범위:
  - stage 1, stage 2, stage 3를 각각 독립적으로 baseline과 비교

## 지표

### 주요 지표

- 최종 테스트 정확도
- 누적 통신량

### 보조 지표

- `Total data comm`
- `Total model comm`
- `avg_active_indices`
- client active ratio 로그

## 검증 계획

### 스모크 체크

- 명령어:
  - `python -m py_compile src/utils/trainer.py`
- 성공 신호:
  - 문법 오류 없음

### 매칭 비교

- 명령어:
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=200 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=2 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/artifacts/stage1-samplewise-union-full200`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=200 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=2 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/artifacts/stage2-small-film-gate-full200`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=200 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.00075 --pruning_threshold=1.0 --major_percent=0.7 --seed=2 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/artifacts/stage3-beta-00075-full200`
- 예상 산출물 경로:
  - `docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/artifacts/`

### 강건성 후속 검증

- 추가 seed: `1,3,4`는 stage 1 통과 후
- 추가 SNR: 없음
- 추가 channel 설정: 없음

## 승격 기준

round `200` 기준으로 baseline보다 communication-performance trade-off가 좋아야 한다. short trend 결과는 참고용으로만 취급한다.

## 중단 기준

통신량 감소가 없거나 accuracy가 크게 무너지면 stage 1 접근은 중단한다.

## 리스크와 교란 요인

- 가능한 교란 요인:
  - union indices 방식이 완전한 샘플별 sparsity 이득을 제한할 수 있음
- 예상 실패 모드:
  - `indices` shape mismatch
  - gradient 복원 오류
- 결과를 무효화할 수 있는 요소:
  - 현재 `8x8/4096` encoder 영향이 stage 1 효과를 덮을 수 있음
