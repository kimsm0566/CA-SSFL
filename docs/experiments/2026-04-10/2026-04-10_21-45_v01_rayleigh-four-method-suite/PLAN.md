# 실험 계획

## 메타데이터

- 실험 id: `2026-04-10_21-45_v01_rayleigh-four-method-suite`
- 초안 일시: `2026-04-10 21:45 KST`
- 상태: 승인
- 담당자: Codex

## 목표

`CA-SSFL Orig`의 Rayleigh 강건성 문제를 겨냥한 4개 방법을 동일한 고정 조건에서 순차 실행하고, 같은 seed set으로 직접 비교 가능한 exploratory 결과를 만든다.

## 지금 하는 이유

지금까지의 개별 피벗 실험은 서로 다른 시점과 결과 루트에서 수행되어 비교가 분산되어 있다. 사용자는 이제 `1,2,3,4` 방법을 모두 후보군으로 유지하길 원하고 있으므로, 같은 실행 계약 아래에서 한 번에 정리된 suite가 필요하다.

## 제안 변경사항

- 대상 코드 경로:
  - `src/utils/option.py`
  - `src/run_exp_main.py`
  - `src/utils/trainer.py`
  - `scripts/`
- 의도한 동작 변화:
  - 기존 `1`(semi-dense), `2`(latent mixing), `4`(importance-aware protection = semantic power) 구현을 재사용한다.
  - 새로 `3`(low-SNR minimum support floor)을 추가한다.
  - 4개 방법을 같은 `Rayleigh`, `n_clients=8`, `seed 1,2` 조건에서 순차 실행하는 suite runner를 추가한다.
- 유지할 조건:
  - dataset=`cifar10`
  - partition=`class`
  - algorithm=`SSFLv6`
  - `beta=0.01`, `pruning_threshold=1.0`, `film_max_t=0.7`, `film_min_t=0.4`
  - `compressed_dim=4096`, `n_rounds=200`

## 후보 접근법

- 접근 A:
  - 개별 옛 실험 결과를 재활용하고 표만 다시 만든다.
- 접근 B:
  - 같은 spec으로 4개 방법을 한 queue에서 재실행한다.
- 우선 접근법과 그 이유:
  - 접근 B.
  - 현재 목표는 “모두 순서대로 실행”이며, claim 전 단계라도 비교축을 정리하려면 같은 spec의 새 산출물이 필요하다.

## 계획된 검증

- 스모크 체크:
  - 새로 추가되는 `support floor`만 1-round smoke를 수행한다.
- 비교 대상:
  - 기준선은 기존 `CA-SSFL Orig`의 `Rayleigh n_clients=8 seed 1,2` matched baseline이다.
  - 실행 후보는 방법 `1,2,3,4` 각각 1개 대표 설정이다.
- 예상 산출물 경로:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-10/2026-04-10-rayleigh-four-method-suite`

## 리스크와 열린 질문

- 기술적 리스크:
  - `support floor`가 active count를 올리면서 통신량을 과도하게 증가시킬 수 있다.
  - 이전처럼 특정 조합이 MPI hang를 유발할 가능성은 남아 있다.
- 평가상 리스크:
  - `1,2`는 이전 pilot에서 이미 약한 결과를 보였으므로 이번 suite에서도 개선이 없을 수 있다.
- 검토가 필요한 질문:
  - 방법 `4`는 현재 구현된 `semantic power`를 first executable version으로 간주한다.

## 사용자 검토 메모

- 피드백:
  - 사용자가 `1,2,3,4 방법들 모두 실행`과 `모두 순서대로 실행`을 요청함.
- 합의된 결정:
  - 네 방법을 모두 같은 suite 아래 순차 실행한다.
- 남은 쟁점:
  - 없음. exploratory suite부터 실행한다.

## 실행 게이트

- 구현 시작 가능?: 예
- 아니라면 먼저 명확히 할 점:
  - 없음
