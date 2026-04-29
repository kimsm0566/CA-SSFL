# 실험 스펙

## 메타데이터

- 실험 id: `2026-04-11_07-10_v01_rayleigh-literature-four-method-suite`
- 시작 일시: `2026-04-11 07:10 KST`
- 상태: 진행중
- 담당자: Codex

## 요약

Rayleigh에서 `CA-SSFL Orig`의 핵심 취약점인 “깨진 semantic feature를 대체할 redundancy 부족”을 겨냥해, 문헌 기반 4개 새 메커니즘을 representative setting으로 구현하고 seed `1,2` exploratory suite를 수행한다.

## 질문

문헌 기반 4개 방향 중 어떤 메커니즘이 baseline 대비 더 유망한 Rayleigh robustness 개선 후보인가?

## 가설

importance-aware protection 계열(방법 1, 2)은 representation을 크게 뒤흔들지 않으면서 직접 redundancy를 추가하므로, learned masking이나 server-side restoration보다 먼저 baseline을 넘을 가능성이 높다.

## 기준선

- 기준선 알고리즘:
  - `CA-SSFL Orig`
- 기준선 설정:
  - `cifar10`, `class`, `rayleigh`, `n_clients=8`, `n_client_data=3000`, `batch_size=100`, `n_epochs=1`, `n_rounds=200`, `beta=0.01`, `pruning_threshold=1.0`, `film_max_t=0.7`, `film_min_t=0.4`, `compressed_dim=4096`, `seed 1,2`
- 기준선 산출물 경로:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-09/2026-04-09-rayleigh-cross-benchmark-nclients8/.../semantic_spreading_0/.../SSFLv6/.../channel_type_rayleigh/seed_{1,2}.npz`
- 이 비교가 적절한 이유:
  - 현재 repository의 최신 `Rayleigh n_clients=8` matched baseline

## 고정 조건

- dataset: `cifar10`
- partition_type: `class`
- n_clients: `8`
- n_client_data: `3000`
- batch_size: `100`
- n_epochs: `1`
- n_rounds: `200`
- channel_type: `rayleigh`
- seed_set: `1,2`
- evaluation_path: 기존 `run_exp_main.py` + `evaluate_global_snr`

## 변경 변수

- 대상 코드 경로:
  - `src/utils/option.py`
  - `src/run_exp_main.py`
  - `src/models/model.py`
  - `src/utils/trainer.py`
  - `scripts/run_rayleigh_literature_four_method_suite_nclients8.sh`
- 바꾸는 변수:
  - 방법 1: `importance-aware repetition`
    - `repetition_topk=32`
  - 방법 2: `base-support + refinement-support`
    - `base_support_k=128`, `refinement_support_k=128`
  - 방법 3: `learned CSI-aware masking`
    - source summary + SNR를 함께 입력받는 FiLM mask head
  - 방법 4: `server-side feature denoising / imputation`
    - semantic decoder 앞단 residual denoiser
- 탐색 범위:
  - 이번 suite는 방법당 representative config 1개만 실행

## 지표

### 주요 지표

- 최종 테스트 정확도
- 누적 통신량

### 보조 지표

- multi-SNR 정확도
- `-6 dB` 정확도
- seed 평균 및 표준편차
- 학습 안정성

## 검증 계획

### 스모크 체크

- 명령어:
  - 방법 `1,2,3,4` 각각 `n_rounds=1`, `seed=1`
- 성공 신호:
  - 각 방법 경로에서 `seed_1.npz` 생성

### 매칭 비교

- 명령어:
  - `scripts/run_rayleigh_literature_four_method_suite_nclients8.sh`
- 예상 산출물 경로:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-11/2026-04-11-rayleigh-literature-four-method-suite`

### 강건성 후속 검증

- 추가 seed:
  - 이번 단계는 `1,2`
- 추가 SNR:
  - 기본 multi-SNR eval
- 추가 channel 설정:
  - 없음

## 승격 기준

- representative setting 기준으로 baseline 대비 final accuracy와 `-6 dB`가 같이 개선되거나,
- 통신량 증가가 작으면서 `-6 dB`가 분명히 좋아지면 다음 정식 sweep 후보로 승격

## 중단 기준

- 대표 설정에서 baseline 대비 accuracy, `-6 dB`, comm가 모두 불리하면 해당 방향은 중단한다.
- 구현 복잡도에 비해 이득이 미미하면 exploratory에서 종료한다.

## 리스크와 교란 요인

- 가능한 교란 요인:
  - repetition이 actual redundancy가 아니라 사실상 power reallocation처럼 작동할 수 있음
  - learned masking이 너무 약하면 baseline과 거의 같아질 수 있음
- 예상 실패 모드:
  - method 1 packet metadata bug
  - method 4 denoiser가 overfit 또는 불안정 학습
- 결과를 무효화할 수 있는 요소:
  - smoke 실패
  - gradient routing 오류
