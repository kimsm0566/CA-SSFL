# 실험 스펙

## 메타데이터

- 실험 id: `2026-04-10_21-45_v01_rayleigh-four-method-suite`
- 시작 일시: `2026-04-10 21:45 KST`
- 상태: 진행중
- 담당자: Codex

## 요약

Rayleigh 채널에서 `CA-SSFL Orig`의 강건성을 높이기 위해 제안된 네 가지 방법을 동일한 실행 조건에서 순차 실행한다. `1`은 semi-dense support balancing, `2`는 latent mixing, `3`은 low-SNR minimum support floor, `4`는 semantic power 기반 importance-aware protection이다.

## 질문

같은 `Rayleigh`, `n_clients=8`, `seed 1,2` 조건에서 네 방법 중 어느 쪽이 `CA-SSFL Orig`보다 더 나은 communication-performance trade-off를 보이는가?

## 가설

`low-SNR minimum support floor`와 `semantic power`는 representation 자체를 크게 흔들지 않기 때문에, `semi-dense`나 `latent mixing`보다 통신량 증가를 더 잘 통제하면서 Rayleigh 저 SNR 성능을 방어할 가능성이 높다.

## 기준선

- 기준선 알고리즘:
  - `CA-SSFL Orig` (`SSFLv6`, no spreading, no snr-adaptive-beta, no semantic power, no latent mixing, no semidense, no support floor)
- 기준선 설정:
  - `cifar10`, `class`, `rayleigh`, `n_clients=8`, `n_client_data=3000`, `batch_size=100`, `n_epochs=1`, `n_rounds=200`, `beta=0.01`, `pruning_threshold=1.0`, `film_max_t=0.7`, `film_min_t=0.4`, `compressed_dim=4096`, `seed 1,2`
- 기준선 산출물 경로:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-09/2026-04-09-rayleigh-cross-benchmark-nclients8/.../semantic_spreading_0/.../SSFLv6/.../channel_type_rayleigh/seed_{1,2}.npz`
- 이 비교가 적절한 이유:
  - 동일 조건의 최신 `n_clients=8` Rayleigh baseline이며, 이후 모든 exploratory 방법이 이 기준과 비교된다.

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
  - `src/utils/trainer.py`
  - `src/utils/option.py`
  - `src/run_exp_main.py`
  - `scripts/run_rayleigh_four_method_suite_nclients8.sh`
- 바꾸는 변수:
  - 방법 1: `semidense_enable=1`, `semidense_group_size=32`, `semidense_group_topk=8`
  - 방법 2: `latent_mixing_enable=1`, `latent_mixing_strength=0.1`, `latent_mixing_groups=8`
  - 방법 3: `support_floor_enable=1`, `support_floor_min_active=256`, `support_floor_snr_db=0.0`
  - 방법 4: `semantic_power_enable=1`, `semantic_power_alpha=2.0`
- 탐색 범위:
  - 이번 suite는 각 방법당 대표 설정 1개만 실행한다.

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
  - Docker GPU에서 `support_floor` 설정으로 `n_rounds=1`, `seed=1`
- 성공 신호:
  - 컨테이너가 정상 종료되고 `seed_1.npz`가 생성됨

### 매칭 비교

- 명령어:
  - `scripts/run_rayleigh_four_method_suite_nclients8.sh`
- 예상 산출물 경로:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-10/2026-04-10-rayleigh-four-method-suite`

### 강건성 후속 검증

- 추가 seed:
  - 이번 단계는 `1,2`까지
- 추가 SNR:
  - 기본 multi-SNR eval 사용
- 추가 channel 설정:
  - 없음. 먼저 Rayleigh exploratory만 수행

## 승격 기준

- exploratory 단계에서는 아래 둘 중 하나를 만족하면 후속 다중 seed 확장 후보로 본다.
  - 기준선 대비 최종 정확도가 같거나 높으면서 통신량이 같거나 낮음
  - 통신량 증가가 작고 `-6 dB` 성능이 뚜렷하게 개선됨

## 중단 기준

- 기준선 대비 정확도와 `-6 dB`가 모두 악화되고 통신량도 증가하면 해당 방법은 중단한다.
- MPI hang가 반복 재현되면 해당 설정은 blacklist 후보로 둔다.

## 리스크와 교란 요인

- 가능한 교란 요인:
  - 이전 실험 루트와 새 suite 루트 혼동
  - active support 관련 옵션 조합으로 인한 예상치 못한 통신량 변화
- 예상 실패 모드:
  - 방법 `1,2`의 재현 실패 또는 무의미한 차이
  - 방법 `3`의 과도한 active floor로 comm 급증
- 결과를 무효화할 수 있는 요소:
  - 스모크 실패
  - `.npz` 미생성 또는 logging/schema 불일치
