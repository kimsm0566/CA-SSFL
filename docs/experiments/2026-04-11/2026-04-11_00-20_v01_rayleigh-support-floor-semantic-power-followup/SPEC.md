# 실험 스펙

## 메타데이터

- 실험 id: `2026-04-11_00-20_v01_rayleigh-support-floor-semantic-power-followup`
- 시작 일시: `2026-04-11 00:20 KST`
- 상태: 진행중
- 담당자: Codex

## 요약

직전 4-method suite에서 상대적으로 가능성이 남은 `support floor`와 `semantic power`를 더 보수적인 하이퍼파라미터로 재탐색한다. 목적은 정확도 붕괴를 막으면서도 baseline 대비 통신량을 줄이는 것이다.

## 질문

`support floor`와 `semantic power`를 약하게 적용하면 baseline `CA-SSFL Orig` 대비 더 나은 communication-performance trade-off가 나오는가?

## 가설

`support floor`는 아주 낮은 SNR 구간에서만 작은 floor를 주면 baseline 대비 평균 통신량을 크게 늘리지 않고 정확도 손실을 줄일 수 있고, `semantic power`는 alpha를 충분히 낮추면 핵심 좌표 보호 효과만 남기고 accuracy 붕괴를 피할 수 있다.

## 기준선

- 기준선 알고리즘:
  - `CA-SSFL Orig`
- 기준선 설정:
  - `cifar10`, `class`, `rayleigh`, `n_clients=8`, `n_client_data=3000`, `batch_size=100`, `n_epochs=1`, `n_rounds=200`, `beta=0.01`, `pruning_threshold=1.0`, `film_max_t=0.7`, `film_min_t=0.4`, `compressed_dim=4096`, `seed 1,2`
- 기준선 산출물 경로:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-09/2026-04-09-rayleigh-cross-benchmark-nclients8/.../semantic_spreading_0/.../SSFLv6/.../channel_type_rayleigh/seed_{1,2}.npz`
- 이 비교가 적절한 이유:
  - 같은 조건의 최신 Rayleigh baseline

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
  - `scripts/run_rayleigh_support_floor_semantic_power_followup_nclients8.sh`
- 바꾸는 변수:
  - support floor:
    - `min_active`: `96`, `128`, `192`
    - `trigger_snr_db`: `-4.0`, `-2.0`
  - semantic power:
    - `alpha`: `0.25`, `0.5`, `1.0`
- 탐색 범위:
  - 총 `6 + 3 = 9` 설정, seed `1,2`, 총 `18` runs

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
  - 없음. 직전 suite와 동일 코드 경로
- 성공 신호:
  - 첫 설정의 `seed_1.npz` 생성

### 매칭 비교

- 명령어:
  - `scripts/run_rayleigh_support_floor_semantic_power_followup_nclients8.sh`
- 예상 산출물 경로:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-11/2026-04-11-rayleigh-support-floor-semantic-power-followup`

### 강건성 후속 검증

- 추가 seed:
  - 이번 단계는 `1,2`
- 추가 SNR:
  - 기본 multi-SNR eval 사용
- 추가 channel 설정:
  - 없음

## 승격 기준

- baseline 대비 final accuracy 손실이 매우 작거나 없으면서 통신량이 유의미하게 낮아야 한다.
- 또는 `-6 dB`가 개선되면서 통신량 증가가 작아야 한다.

## 중단 기준

- baseline 대비 accuracy가 계속 낮고 comm 절감도 미미하면 중단한다.
- semantic power가 low-alpha에서도 큰 정확도 붕괴를 보이면 해당 방향은 종료한다.

## 리스크와 교란 요인

- 가능한 교란 요인:
  - support floor와 semantic power가 모두 active support 분포를 바꾸므로 평균 comm만 보면 오해할 수 있음
- 예상 실패 모드:
  - support floor가 너무 약해서 baseline과 동일
  - semantic power가 낮은 alpha에서도 accuracy를 깎음
- 결과를 무효화할 수 있는 요소:
  - seed 불완전
  - 산출물 누락
