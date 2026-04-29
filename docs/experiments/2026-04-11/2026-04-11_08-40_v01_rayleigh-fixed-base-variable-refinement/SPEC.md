# SPEC

## 문서 및 결과 경로

- 문서 폴더:
  - `/home/sunmin/SFL_Semantic/docs/experiments/2026-04-11/2026-04-11_08-40_v01_rayleigh-fixed-base-variable-refinement`
- 실행 로그:
  - `/home/sunmin/SFL_Semantic/docs/experiments/2026-04-11/2026-04-11_08-40_v01_rayleigh-fixed-base-variable-refinement/RUNLOG.md`
- exploratory 결과 루트:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-11/2026-04-11-rayleigh-fixed-base-variable-refinement`
- smoke 결과 루트:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-11/2026-04-11-rayleigh-fixed-base-variable-refinement-smoke`
- 아카이브 메모:
  - `2026-04-11 16:22 KST`에 시작한 run의 결과는 종료 후 dated path로 병합 정리되었다.

## 목적

고정형 `method2`를 `fixed base + variable refinement` 구조로 바꿔, Rayleigh에서

- 핵심 semantic support는 안정적으로 유지하고
- 추가 support는 채널 상태에 따라 가변으로 붙이는

구조가 실제로 baseline 및 기존 고정형 `method2`보다 나은지 확인한다.

## 비교 대상

### 기준 baseline

- `CA-SSFL Orig`

### 부 비교 baseline

- 기존 고정형 `method2`
  - `base_support_k=128`
  - `refinement_support_k=128`
  - 사실상 `최대 256-budget` 방식

### 신규 후보

- `fixed-base variable-refinement v1`

## 고정 조건

- dataset: `cifar10`
- partition: `class`
- channel: `rayleigh`
- `n_clients=8`
- `n_client_data=3000`
- `batch_size=100`
- `n_epochs=1`
- `n_rounds=200`
- `algorithm=SSFLv6`
- `model_type=resnetv2`
- `compressed_dim=4096`
- `beta=0.01`
- `pruning_threshold=1.0`
- `film_max_t=0.7`
- `film_min_t=0.4`
- `semantic_spreading_enable=0`
- `snr_adaptive_beta_enable=0`
- `semantic_power_enable=0`
- seeds: `1,2`

## 구현 규칙

### 1. 활성 support 구조

최종 support는 다음으로 구성한다.

- `base support`
- `refinement support`

최종 전송 차원:

- `final_support = base_support ∪ refinement_support`

### 2. Base support

`base support`는 semantic importance만으로 고른다.

- score: `KL mean`
- 선택 수: `K_base = 128`
- 선택 규칙: top-`128`

즉 base는 현재 채널 상태와 무관하게 유지되는 semantic core다.

### 3. Refinement support

`refinement support`는 channel-aware하게 가변 선택한다.

- 후보 집합: `vib_mask > 0` 이고 `base_support`에 포함되지 않은 차원
- score: `raw FiLM score`
- 최대 선택 수: `K_ref_max = 128`

실제 refinement 수는 현재 training SNR로부터 다음처럼 계산한다.

- `snr_normalized = (current_snr_db - (-5)) / (15 - (-5))`
- `K_ref = round(K_ref_max * snr_normalized)`
- clamp: `0 <= K_ref <= K_ref_max`

즉:

- `-5 dB`에 가까우면 refinement는 거의 0
- `15 dB`에 가까우면 refinement는 최대 `128`

### 4. 역할 분리

이 실험에서 각 모듈의 역할은 명시적으로 다음처럼 둔다.

- `VIB/KL`: base support 결정
- `FiLM`: refinement support 결정

중요한 점:

- base는 `chan_mask threshold`를 무시하고 semantic importance만 본다.
- refinement는 continuous `film_mask`를 사용한다.
- 즉 기존처럼 `KL x chan_mask`로 섞지 않는다.

## 새 옵션

신규 구현 옵션은 아래 최소 집합만 추가한다.

- `base_refinement_variable_enable`

기존 옵션은 그대로 재사용한다.

- `base_refinement_enable`
- `base_support_k`
- `refinement_support_k`

의미는 다음처럼 해석한다.

- `base_refinement_enable=1`
- `base_refinement_variable_enable=0`
  - 기존 고정형 method2
- `base_refinement_enable=1`
- `base_refinement_variable_enable=1`
  - 신규 fixed-base variable-refinement v1

이때

- `base_support_k`는 `K_base`
- `refinement_support_k`는 `K_ref_max`

로 사용한다.

## 결과 경로

기존 `method2`와 충돌하지 않도록 result path slug에 아래를 추가한다.

- `base_refinement_variable_<0|1>`

## 검증

### Level 0

- touched python files에 대해 `python -m py_compile`

### Level 1

- Docker GPU `1-round smoke`
- 확인 항목:
  - 정상 종료 여부
  - 결과 `.npz` 저장 여부
  - 전송 차원 수 로그가 low/high SNR에서 차등적으로 보이는지

### Level 2

- `seed=1,2` exploratory

## 평가지표

- final train acc
- total comm
- test `-6 dB`
- test `12 dB`

## 1차 성공 기준

### baseline 대비

- final acc 비열화 또는 개선
- `-6 dB` 비열화 또는 개선
- total comm 감소

### 기존 고정형 method2 대비

다음 중 하나를 만족하면 의미 있다.

- final acc 개선
- `-6 dB` 개선
- 비슷한 성능에서 comm 감소

## 비목표

이번 단계에서는 아래는 하지 않는다.

- AWGN 재현
- seed 4개 이상 확장
- multi-stage 실제 2회 전송 구현
- repetition, semantic power, support floor와의 조합
