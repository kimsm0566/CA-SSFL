# 실험 스펙

## 메타데이터

- 실험 id: `2026-04-08_23-36_v01_ssflv6-rayleigh-robustness`
- 시작 일시: `2026-04-08 23:36 KST`
- 상태: `진행중`
- 담당자: `Codex`

## 요약

`SSFLv6`의 현재 `K` 선택 정책은 유지하고, 선택된 활성 semantic feature에만 DCT 기반 spreading을 적용해 `Rayleigh` 채널에서의 강건성을 개선할 수 있는지 확인한다. 초기 구현 범위는 `Sliced Feature Spreading` 단독이었고, exploratory single-seed 결과를 반영해 후속 matched 비교는 `baseline(semantic_spreading=0, snr_adaptive_beta=0)`와 `candidate(semantic_spreading=1, snr_adaptive_beta=1)`의 `3-seed` 비교로 확장한다. 실험 파라미터는 `beta=0.01`, `pruning_threshold=1.0`, `film_max_t=0.7`, `film_min_t=0.4`로 고정한다.

## 질문

현재 `SSFLv6`의 `Rayleigh` 취약성이 `K` 자체보다도 선택된 active feature의 국소적 취약성에서 오는 경우, 전송 전 spreading만으로 통신량 증가 없이 robustness를 회복할 수 있는가? 또한 exploratory 결과에서 보인 것처럼 `SNR-adaptive beta`가 결합될 때만 이득이 난다면, 이 결합 효과가 matched multi-seed에서도 유지되는가?

## 가설

- `A 단독`: `SSFLv6`에서 기존 `K` 선택 정책을 유지한 채 선택된 active feature에만 orthonormal DCT spreading을 적용하면, `Rayleigh + ZF` 환경에서 특정 좌표 손상을 전체 좌표에 분산시켜 baseline 대비 multi-SNR accuracy를 개선할 수 있다.
- `A + SNR-adaptive beta`: 단독 spreading이 불안정하더라도, `SNR-adaptive beta`가 고 SNR 구간에서 더 넓은 active set과 덜 압축된 표현을 허용하면 spreading의 이득이 살아나고, matched multi-seed에서도 baseline 대비 정확도 이득이 유지될 수 있다.

## 기준선

- 기준선 알고리즘: `SSFLv6`
- 기준선 설정:
  - `dataset=cifar10`
  - `partition_type=class`
  - `channel_type=rayleigh`
  - `n_clients=9`
  - `n_client_data=3000`
  - `batch_size=100`
  - `n_epochs=1`
  - `n_rounds=200`
  - `compressed_dim=4096`
  - `beta=0.01`
  - `pruning_threshold=1.0`
  - `film_max_t=0.7`
  - `film_min_t=0.4`
  - `semantic_spreading_enable=0`
- 기준선 산출물 경로:
  - `results/.../beta_0.01/pruning_threshold_1.0/film_max_t_0.7/film_min_t_0.4/semantic_spreading_0/...`
- 이 비교가 적절한 이유:
  - `K` 선택 정책과 전체 학습 budget을 유지한 채 전송 방식만 바꾸기 때문이다.

## 고정 조건

- dataset: `cifar10`
- partition_type: `class`
- n_clients: `9`
- n_client_data: `3000`
- batch_size: `100`
- n_epochs: `1`
- n_rounds: `200`
- channel_type: `rayleigh`
- seed_set: `우선 smoke는 single seed`, 이후 matched 비교는 canonical seed set으로 확장
- evaluation_path: 기존 `run_exp_main.py` 및 post-training `snr_eval`

## 변경 변수

- 대상 코드 경로:
  - `src/models/model.py`
  - `src/utils/trainer.py`
  - `src/utils/option.py`
  - `src/run_exp_main.py`
- 바꾸는 변수:
  - `semantic_spreading_enable in {0, 1}`
  - `snr_adaptive_beta_enable in {0, 1}`
- 탐색 범위:
  - exploratory phase:
    - `semantic_spreading_enable=1`, `snr_adaptive_beta_enable=0`
    - `semantic_spreading_enable=1`, `snr_adaptive_beta_enable=1`
  - matched follow-up phase:
    - baseline: `semantic_spreading_enable=0`, `snr_adaptive_beta_enable=0`
    - candidate: `semantic_spreading_enable=1`, `snr_adaptive_beta_enable=1`

## 지표

### 주요 지표

- 최종 테스트 정확도
- 누적 통신량

### 보조 지표

- multi-SNR 정확도
- 최악 SNR 정확도
- seed 평균 및 표준편차
- 학습 안정성

## 검증 계획

### 스모크 체크

- 명령어:
  - 정적 검증:
    - `python -m py_compile src/run_exp_main.py src/models/model.py src/utils/option.py src/utils/trainer.py`
  - Docker GPU smoke:
    - `docker compose run --rm sfl-semantic run-exp --dataset cifar10 --algorithm SSFLv6 --model_type resnetv2 --channel_type rayleigh --n_clients 2 --n_client_data 10 --batch_size 10 --n_epochs 1 --n_rounds 1 --compressed_dim 4096 --beta 0.01 --pruning_threshold 1.0 --film_max_t 0.7 --film_min_t 0.4 --semantic_spreading_enable 1 --result_path /workspace/tmp/2026-04-08-rayleigh-spreading-smoke --seed 0`
- 성공 신호:
  - 문법 오류 없음
  - 컨테이너 내부 `check-gpu` 통과
  - 1-round MPI 학습/저장 경로 정상 종료

### 매칭 비교

- 명령어:
  - baseline:
    - `docker compose run --rm sfl-semantic run-exp --algorithm SSFLv6 --dataset cifar10 --partition_type class --n_clients 9 --n_client_data 3000 --batch_size 100 --n_epochs 1 --n_rounds 200 --model_type resnetv2 --channel_type rayleigh --snr_db 12 --compressed_dim 4096 --beta 0.01 --pruning_threshold 1.0 --film_max_t 0.7 --film_min_t 0.4 --semantic_spreading_enable 0 --snr_adaptive_beta_enable 0 --seed <seed>`
  - candidate:
    - `docker compose run --rm sfl-semantic run-exp --algorithm SSFLv6 --dataset cifar10 --partition_type class --n_clients 9 --n_client_data 3000 --batch_size 100 --n_epochs 1 --n_rounds 200 --model_type resnetv2 --channel_type rayleigh --snr_db 12 --compressed_dim 4096 --beta 0.01 --pruning_threshold 1.0 --film_max_t 0.7 --film_min_t 0.4 --semantic_spreading_enable 1 --snr_adaptive_beta_enable 1 --seed <seed>`
- 예상 산출물 경로:
  - `results/.../semantic_spreading_0/snr_adaptive_beta_0/...`
  - `results/.../semantic_spreading_1/snr_adaptive_beta_1/...`
- seed 정책:
  - exploratory single-seed `seed=0`은 이미 확보된 산출물을 재사용
  - matched follow-up은 `seed in {0,1,2}`를 canonical set으로 사용

### 강건성 후속 검증

- 추가 seed:
  - canonical seed set 확정 후 동일 set 사용
- 추가 SNR:
  - post-training multi-SNR sweep 활용
- 추가 channel 설정:
  - 1차 단계에서는 `rayleigh`만

## 승격 기준

동일 고정 조건에서 `candidate(semantic_spreading_enable=1, snr_adaptive_beta_enable=1)`가 baseline 대비 seed 평균 기준으로 저 SNR accuracy 또는 multi-SNR 평균 accuracy를 개선하면 유망 후보로 본다. 단, exploratory `seed=0` 단독 결과는 방향성 확인으로만 해석한다.

## 중단 기준

문법 또는 smoke 단계에서 역전파/shape 오류가 발생하거나, short exploratory run에서 accuracy가 전 SNR 구간에 걸쳐 일관되게 악화되면 이 설계를 중단하거나 변형한다.

## 리스크와 교란 요인

- 가능한 교란 요인:
  - 기존 `K` 정책이 이미 저 SNR에서 지나치게 공격적으로 축소될 수 있음
  - DCT spreading이 decoder 복원 구조와 충돌할 수 있음
- 예상 실패 모드:
  - inverse spreading 위치가 잘못되어 decoder 입력 표현이 깨짐
  - shape mismatch 또는 gradient 경로 손상
- 결과를 무효화할 수 있는 요소:
  - Docker daemon 또는 GPU runtime 접근 불가
  - 컨테이너 내부 CUDA 비가용
