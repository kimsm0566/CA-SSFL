# PLAN

## 실험 이름

`Rayleigh fixed-base variable-refinement`

## 파일 저장 및 경로

- 실험 문서 경로:
  - `/home/sunmin/SFL_Semantic/docs/experiments/2026-04-11/2026-04-11_08-40_v01_rayleigh-fixed-base-variable-refinement`
- 실행 로그:
  - `/home/sunmin/SFL_Semantic/docs/experiments/2026-04-11/2026-04-11_08-40_v01_rayleigh-fixed-base-variable-refinement/RUNLOG.md`
- 결과 저장 루트:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-11/2026-04-11-rayleigh-fixed-base-variable-refinement`
- smoke 결과 저장 루트:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-11/2026-04-11-rayleigh-fixed-base-variable-refinement-smoke`
- 아카이브 메모:
  - `2026-04-11 16:22 KST`에 시작한 live run은 initially top-level `tmp` 경로에 기록되었고, run 종료 후 날짜 bucket 경로로 병합 정리되었다.

## 배경

이전 `method2`는 `base_support_k=128`, `refinement_support_k=128`으로 동작했고, 실제로는 `최대 256차원`에 가까운 고정 예산 방식으로 작동했다.

이 방식은 `Rayleigh`, `n_clients=8`, `seed=1,2` 기준으로 baseline `CA-SSFL Orig`보다 좋은 결과를 보였다.

- final acc: `41.91 -> 42.28`
- total comm: `19608.50 MB -> 17364.44 MB`
- `-6 dB`: `39.37 -> 39.83`

하지만 현재 구조는 `base`와 `refinement`가 둘 다 거의 고정 예산으로 작동해서, 문헌에서 기대한 `base는 항상 유지되고, refinement는 채널 상태에 따라 유연하게 붙는 구조`와는 아직 거리가 있다.

## 문제 정의

현재 `CA-SSFL`는 Rayleigh에서

- 핵심 semantic feature가 일부 좌표에 몰리고
- deep fade 시 그 좌표가 흔들리면 대체할 support가 부족하며
- support budget도 현재는 충분히 channel-adaptive하지 않다.

따라서 다음 단계에서는

- `base support`는 semantic core로 고정
- `refinement support`는 channel condition에 따라 가변

인 구조로 바꿔, `핵심 정보 보장`과 `채널 적응`의 역할을 분리해서 확인한다.

## 핵심 가설

`VIB`를 이용해 고른 고정 `base support`와, `FiLM/SNR-aware gating`을 이용해 고르는 가변 `refinement support`를 결합하면, 현재의 `고정 256-budget` method2보다 Rayleigh 저 SNR 강건성을 유지하면서 통신량을 더 줄이거나, 같은 통신량에서 성능을 더 높일 수 있다.

## 제안 구조

### 1. Base support

- `KL` 기반 semantic 중요도만 사용
- top-`K_base`를 항상 선택
- 의미:
  - 채널이 나빠도 유지해야 하는 semantic core

### 2. Refinement support

- base를 제외한 차원 중에서 선택
- `FiLM` 또는 `KL x FiLM` score를 사용
- refinement 개수 `K_ref`는 SNR에 따라 가변
- 의미:
  - 채널이 허용하는 범위에서만 추가 정보 전송

### 3. 최종 support

- `final = base ∪ refinement`

즉 역할 분리는 다음처럼 명시한다.

- `VIB`: 무엇이 본질적으로 중요한가
- `FiLM/SNR-aware gating`: 현재 채널에서 어떤 추가 정보를 더 실을 수 있는가

## 첫 구현 원칙

- 기존 `method2` 구현을 완전히 버리지 않고 최소 수정
- `base_refinement_enable` 경로를 확장하거나 별도 flag 추가
- 기존 baseline 및 기존 `method2`와 직접 비교 가능하게 유지
- 먼저 `Rayleigh`에서만 exploratory

## 비교 기준

주 비교 baseline:

- `CA-SSFL Orig`

부 비교 baseline:

- 현재 고정형 `method2` (`base=128`, `refinement=128`)

즉 다음 질문을 본다.

1. 기존 baseline보다 좋은가?
2. 기존 고정형 `method2`보다 더 좋은가?
3. `SC-USFL` 대비 우위를 유지하는가?

## 고정 조건

초기 exploratory에서는 다음을 고정한다.

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
- seeds: `1,2`

## 성공 기준

1차 exploratory 성공 기준:

- baseline 대비 final acc 비열화 또는 개선
- baseline 대비 `-6 dB` 비열화 또는 개선
- baseline 대비 total comm 감소

추가로 현재 고정형 `method2` 대비 아래 중 하나를 만족하면 의미 있다.

- final acc 또는 `-6 dB` 개선
- 비슷한 성능에서 comm 추가 감소

## 예상 리스크

### 1. refinement가 너무 적어질 수 있음

- low SNR에서 refinement가 거의 사라지면 base-only와 비슷해질 수 있다.

### 2. refinement score 설계가 부적절할 수 있음

- `KL x FiLM`가 너무 공격적이면 오히려 중요한 차원이 빠질 수 있다.

### 3. 구현상 예산 추적이 꼬일 수 있음

- `K_base`와 `K_ref`를 분리하면 현재 comm accounting 및 logging이 기대와 다르게 보일 수 있다.

## 실행 순서

1. `SPEC.md`에서 selection rule과 `K_ref(SNR)` 공식을 고정
2. 최소 구현
3. `1-round smoke`
4. `seed=1,2` exploratory
5. baseline / 기존 method2 / SC-USFL와 비교

## 지금 단계의 결정

이번 계획에서는 아직 코드를 바꾸지 않는다.

먼저 아래를 `SPEC.md`에서 고정해야 한다.

- `K_base`
- `K_ref` 최대값
- `K_ref(SNR)` 계산 방식
- refinement score 정의
- 결과 경로 slug
