# 2026-04-15 v01 w/o channel mask only ablation spec

## 메타데이터

- 실험 id: `2026-04-15_18-15_v01_wo-channel-mask-only-ablation-plan`
- 문서 폴더: `docs/experiments/2026-04-15/2026-04-15_18-15_v01_wo-channel-mask-only-ablation-plan/`
- 시작 일시: `2026-04-15 18:25 KST`
- 종료 일시: `2026-04-15 19:49 KST`
- 상태: `완료`
- 담당자: `Codex`

## 요약

`SSFLv6`의 encoder 내부 `FiLM` gating과 `VIB`는 유지한 채, 최종 전송 support를 만드는 `SNR-conditioned channel mask`만 all-pass로 강제하는 exact ablation을 실행한다. 구현은 `--channel_mask_allpass_enable=1` 스위치로 제어하며, 기본 동작은 유지한다.

## 질문

논문 Table II 하단의 `w/o Channel Masking`을 기존 `SSFLv6_w_o_film` stronger proxy 대신, exact한 `channel mask only off` 실험으로 대체할 수 있는가?

## 가설

`--channel_mask_allpass_enable=1`은 baseline `CA-SSFL` 대비 통신량을 증가시키지만, 기존 `SSFLv6_w_o_film`보다 덜 강한 ablation이므로 정확도 및 통신량 모두에서 더 해석 가능한 intermediate 결과를 낼 것이다.

## 기준선

- 기준선 알고리즘:
  - `CA-SSFL` (`SSFLv6`)
- 기준선 설정:
  - `AWGN`: `beta=0.05`, `pruning_threshold=1.0`, `film_max_t=0.7`, `film_min_t=0.2`
  - `Rayleigh`: `beta=0.1`, `pruning_threshold=1.0`, `film_max_t=0.7`, `film_min_t=0.4`
- 기준선 산출물 경로:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-14/2026-04-14-table1-blockB-channel-specific-rerun`
- 이 비교가 적절한 이유:
  - dataset, partition, client 수, training budget, seed set, evaluation path를 동일하게 맞출 수 있고
  - 변경점이 `final channel mask all-pass` 하나로 국한되기 때문이다

## 고정 조건

- dataset: `cifar10`
- partition_type: `class`
- n_clients: `8`
- n_client_data: `3000`
- batch_size: `100`
- n_epochs: `1`
- n_rounds: `200`
- channel_type: `awgn`, `rayleigh`
- seed_set: `1,2,3,4`
- evaluation_path:
  - canonical Docker GPU runtime
  - `docker compose run --rm sfl-semantic run-exp ...`
- 추가 고정 조건:
  - `model_type=resnetv2`
  - `compressed_dim=4096`
  - `major_percent=0.8`
  - `semantic_spreading_enable=0`
  - `snr_adaptive_beta_enable=0`
  - `semantic_power_enable=0`
  - `latent_mixing_enable=0`
  - `encoder_downsample_enable=0`
  - `semidense_enable=0`
  - `support_floor_enable=0`
  - `importance_repetition_enable=0`
  - `base_refinement_enable=0`
  - `csi_source_mask_enable=0`
  - `server_feature_impute_enable=0`
  - `snr_db=10`

## 변경 변수

- 대상 코드 경로:
  - `src/utils/option.py`
  - `src/run_exp_main.py`
  - `src/utils/trainer.py`
  - `src/utils/eval.py`
- 바꾸는 변수:
  - `--channel_mask_allpass_enable`
- 탐색 범위:
  - `0`: baseline behavior
  - `1`: final `chan_mask = ones`

## 지표

### 주요 지표

- 최종 테스트 정확도
- 누적 통신량

### 보조 지표

- `-6 dB` 정확도
- `12 dB` 정확도
- multi-SNR 정확도
- seed 평균 및 표준편차
- 학습 안정성

## 검증 계획

### 스모크 체크

- 명령어:
  - `docker compose run --rm sfl-semantic check-gpu`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=awgn --partition_type=class --n_clients=2 --n_client_data=10 --batch_size=10 --n_epochs=1 --n_rounds=1 --model_type=resnetv2 --snr_db=10 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.05 --pruning_threshold=1.0 --film_max_t=0.7 --film_min_t=0.2 --major_percent=0.8 --channel_mask_allpass_enable=1 --seed=1 --verbose=1 --result_path=/workspace/tmp/2026-04-15/2026-04-15-cifar10-wo-channel-mask-only-ablation-smoke-awgn`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=2 --n_client_data=10 --batch_size=10 --n_epochs=1 --n_rounds=1 --model_type=resnetv2 --snr_db=10 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.1 --pruning_threshold=1.0 --film_max_t=0.7 --film_min_t=0.4 --major_percent=0.8 --channel_mask_allpass_enable=1 --seed=1 --verbose=1 --result_path=/workspace/tmp/2026-04-15/2026-04-15-cifar10-wo-channel-mask-only-ablation-smoke-rayleigh`
- 성공 신호:
  - 두 채널 모두 `seed_1.npz` 저장
  - 서버 로그가 끝까지 기록됨
  - baseline 대비 active support가 줄어들지 않음

### 매칭 비교

- 명령어:
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=<awgn|rayleigh> --partition_type=class --n_clients=8 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=200 --model_type=resnetv2 --snr_db=10 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=<channel-specific> --pruning_threshold=1.0 --film_max_t=0.7 --film_min_t=<channel-specific> --major_percent=0.8 --channel_mask_allpass_enable=1 --seed=<1..4> --verbose=1 --result_path=/workspace/tmp/2026-04-15/2026-04-15-cifar10-wo-channel-mask-only-ablation`
- 예상 산출물 경로:
  - `/workspace/tmp/2026-04-15/2026-04-15-cifar10-wo-channel-mask-only-ablation`

### 강건성 후속 검증

- 추가 seed:
  - 없음, 이번 실행 자체가 canonical seed `1,2,3,4`
- 추가 SNR:
  - multi-SNR evaluation은 기본 저장 결과 재사용
- 추가 channel 설정:
  - `AWGN`, `Rayleigh` 둘 다 실행

## 예상 실행 규모와 시간

- 총 실행 수:
  - smoke `2`
  - main `8`
  - total `10`
- run당 예상 시간:
  - smoke run 약 `5~10분`
  - main run 약 `7~8분`
- 총 예상 시간:
  - 약 `70~90분`
- 시간 추정 전제:
  - Docker GPU runtime 정상
  - 큐 중단 없이 순차 실행

## 승격 기준

- baseline 대비 통신량 증가가 관측되어야 한다
- 기존 `SSFLv6_w_o_film` proxy와 다른 수치가 나와야 한다
- 정확도와 통신량 변화가 `channel mask only off` 해석과 일치해야 한다

## 중단 기준

- smoke run 실패
- train/eval semantics 불일치
- 결과가 기존 `w_o_film` proxy와 완전히 indistinguishable하여 exact ablation 실익이 매우 낮다고 판단되는 경우

## 리스크와 교란 요인

- 가능한 교란 요인:
  - 기존 baseline artifact와 major percent 또는 결과 경로 구성이 어긋나는 경우
- 예상 실패 모드:
  - Docker runtime 미가동
  - MPI/Docker 종료 코드와 artifact 생성 상태가 어긋남
- 결과를 무효화할 수 있는 요소:
  - `channel_mask_allpass_enable`가 train/eval 모두에 일관되게 적용되지 않는 경우
