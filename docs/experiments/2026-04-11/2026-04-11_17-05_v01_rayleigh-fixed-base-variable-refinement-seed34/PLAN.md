# PLAN

## 실험명

`2026-04-11_17-05_v01_rayleigh-fixed-base-variable-refinement-seed34`

## 배경

현재 `fixed base + variable refinement` 후보는 `Rayleigh`, `n_clients=8`, `seed=1,2` 기준으로

- baseline `CA-SSFL Orig` 대비 정확도는 거의 유지
- `-6 dB`는 소폭 개선
- total communication은 크게 감소

하는 결과를 보였다.

다만 현재 비교는 `seed=1,2`에 한정돼 있고, 사용자 관찰대로 `seed=3,4`에서 성능이 흔들릴 가능성을 확인해야 한다.

또, 일부 그래프에서 `CA-SSFL`이 `SC-USFL`보다 낮게 보이는 현상은 seed 집합이 일치하지 않은 평균 때문일 수 있으므로, 후보 쪽도 `seed=3,4`를 추가해 같은 seed 집합으로 다시 비교할 필요가 있다.

## 목표

기존 `fixed base + variable refinement` 후보를 동일한 고정 조건에서 `seed=3,4`까지 확장 실행하고, 이후

- baseline `CA-SSFL Orig`
- `SC-USFL`
- 필요 시 고정형 `method2`

와 `seed=1,2,3,4` 또는 `seed=3,4` 기준으로 matched comparison이 가능하도록 만든다.

## 핵심 질문

1. `seed=3,4`에서도 후보가 baseline 대비 `정확도 비열화 + comm 절감`을 유지하는가?
2. `seed=3,4`에서도 후보가 `SC-USFL` 대비 우세한가?
3. 기존 그래프의 역전 현상이 seed mismatch 때문인지, 실제 후보 열화 때문인지 구분되는가?

## 범위

이번 단계는 실행 확장만 한다.

- 새 알고리즘 변경 없음
- 새 코드 경로 변경 없음
- 기존 후보 설정 그대로 사용
- `seed=3,4`만 추가 실행

## 결과물

- `seed=3,4` `.npz` 아티팩트
- 실행 로그
- 후속 matched analysis에 쓸 비교 요약
