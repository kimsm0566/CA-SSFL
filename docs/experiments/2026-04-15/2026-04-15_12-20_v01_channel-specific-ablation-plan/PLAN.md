# 채널별 대표 설정 기반 CA-SSFL Ablation 계획

## 배경

현재 `cifar10` 기준 대표 설정은 채널별로 다음처럼 정리됐다.

- `AWGN`
  - `beta=0.05`
  - `pruning_threshold=1.0`
  - `film_max_t=0.7`
  - `film_min_t=0.2`
- `Rayleigh`
  - `beta=0.1`
  - `pruning_threshold=1.0`
  - `film_max_t=0.7`
  - `film_min_t=0.4`

이제 필요한 것은 **대표 설정을 기준으로 CA-SSFL의 핵심 구성요소가 실제로 얼마나 기여하는지**를 채널별로 분해하는 것이다.

## 목적

채널별 best 하이퍼파라미터를 고정한 뒤, 기존에 확보된 `CA-SSFL` baseline artifact를 기준으로 핵심 메커니즘을 ablation으로 분해한다.

핵심 질문:

1. `AWGN`에서 성능/통신 trade-off를 실제로 만드는 주된 요소는 `VIB`인가, `FiLM`인가?
2. `Rayleigh`에서 강건성을 지탱하는 주된 요소는 `VIB`인가, `FiLM`인가?
3. 채널별 대표 설정이 달라진 뒤에도 기존 “dual masking” 해석이 여전히 유지되는가?

## 이번 단계에서 다룰 ablation 축

### 주요 ablation

- `CA-SSFL w/o VIB`
  - code path: `SSFLv6_w_o_vib`
- `CA-SSFL w/o FiLM`
  - code path: `SSFLv6_w_o_film`

### 비교 기준 baseline

- `CA-SSFL`
  - 새로 재실행하지 않고, 이미 확보된 채널별 best artifact를 재사용한다.
  - `AWGN`: `beta=0.05`, `tau_VIB=1.0`, `film=0.7/0.2`
  - `Rayleigh`: `beta=0.1`, `tau_VIB=1.0`, `film=0.7/0.4`

## 이번 단계에서 제외하는 축

- `w/o beta`
  - 현재 채널별 best 설정은 이미 fixed `beta`를 쓰고 있어, `beta schedule` 제거 축이 구조적으로 의미가 약하다.
- 새 후보 메커니즘
  - repetition, base/refinement, support floor 등은 이번 ablation 목적과 다르므로 제외한다.

## 실험 범위

- dataset: `cifar10`
- channels:
  - `AWGN`
  - `Rayleigh`
- methods:
  - `CA-SSFL w/o VIB`
  - `CA-SSFL w/o FiLM`
- seeds:
  - `1,2,3,4`

## 채널별 고정 하이퍼파라미터

### AWGN

- `beta=0.05`
- `pruning_threshold=1.0`
- `film_max_t=0.7`
- `film_min_t=0.2`

### Rayleigh

- `beta=0.1`
- `pruning_threshold=1.0`
- `film_max_t=0.7`
- `film_min_t=0.4`

## 기본 가설

1. `AWGN`에서는 `FiLM` 제거보다 `VIB` 제거가 통신량을 더 크게 악화시킬 가능성이 높다.
2. `Rayleigh`에서는 `FiLM` 제거가 `-6 dB` 정확도와 전체 강건성에 더 직접적인 손실을 만들 가능성이 높다.
3. 두 채널 모두 `w/o VIB`, `w/o FiLM`가 baseline `CA-SSFL`보다 열화해야 현재 메커니즘 해석이 깔끔해진다.

## 실행 전략

1. `SPEC.md`에서 채널별 대표 설정과 결과 루트를 고정한다.
2. code change 없이 기존 알고리즘 플래그만 사용한다.
3. `AWGN`에서 `w/o VIB`, `w/o FiLM`만 실행한다.
4. `Rayleigh`에서 `w/o VIB`, `w/o FiLM`만 실행한다.
5. 기존 baseline artifact와 결합해 평균/표준편차와 `-6 dB`를 포함한 표로 정리한다.

## 예상 실행 수

- `2 channels x 2 methods x 4 seeds = 16 runs`

## 예상 소요 시간

- run당 약 `7~8분`
- 총 약 `2시간 ~ 2시간 20분`

## 시간 추정 전제

- 기존 `cifar10` benchmark와 동일한 Docker GPU runtime 사용
- artifact 저장 후 non-zero exit가 나올 수 있으므로 artifact-first 판정 적용
- 중간 stall 없이 순차 실행된다는 가정

## 산출물

- `SPEC.md`
- `RUNLOG_AWGN.md`
- `RUNLOG_RAYLEIGH.md`
- `RESULT.md`
- 필요 시 ablation 그래프

## 성공 기준

- 각 채널에서 `w/o VIB`, `w/o FiLM`가 `seed 1,2,3,4`로 재현될 것
- `Acc`, `Comm`, `-6 dB` 비교가 가능한 결과 표가 만들어질 것
- 기존 baseline artifact와 새로운 ablation 결과가 충돌 없이 비교 가능할 것
