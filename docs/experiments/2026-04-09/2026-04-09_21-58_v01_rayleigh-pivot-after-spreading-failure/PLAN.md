# 실험 계획

## 메타데이터

- 실험 id: `2026-04-09_21-58_v01_rayleigh-pivot-after-spreading-failure`
- 시작 일시: `2026-04-09 21:58 KST`
- 상태: `planned`
- 담당자: `Codex`

## 배경

`n_clients=8` 기준 재실행 결과, `CA-SSFL New`(`semantic_spreading + snr_adaptive_beta`)는 `CA-SSFL Orig`를 이기지 못했다.

- final acc delta: `-0.41%p`
- `-6 dB` delta: `-0.19%p`
- total comm delta: `+1720.87 MB`

즉 현재 `spreading` 방향은 Rayleigh 개선 방향으로 채택할 수 없다.

## 목적

`CA-SSFL Orig`를 다시 기준점으로 두고, Rayleigh에서 실제로 강건성과 효율을 개선할 다른 방향을 우선순위화한다.

## 핵심 질문

1. `spreading` 없이도 Rayleigh에서 중요한 좌표를 더 잘 보호할 수 있는가?
2. 성능 저하 없이 통신량을 비슷하게 유지하거나 줄이면서 `SC-USFL` 대비 우위를 만들 수 있는가?
3. 다음 실험은 어떤 intervention부터 시작해야 risk가 가장 낮고 해석이 쉬운가?

## 방향 재설정

### 탈락

- `semantic_spreading + snr_adaptive_beta`
  - 이유:
    - `n_clients=8` 기준 재현 실패
    - accuracy 이득 없음
    - comm 증가

### 우선순위 1

- `Semantic Power Allocation on top of CA-SSFL Orig`
  - 설명:
    - active feature 개수 정책은 유지
    - 선택된 좌표들 사이에서만 중요도 기반 전력 재할당
  - 이유:
    - Rayleigh deep fade에서 중요한 좌표 보호에 직접적
    - selection policy를 크게 흔들지 않음
    - `Orig/New`처럼 representation 자체를 뒤흔들지 않음

### 우선순위 2

- `Low-SNR importance floor`
  - 설명:
    - low-SNR일 때 완전한 spreading 대신, KL 상위 일부 좌표에 대해 최소 보장 active set을 유지
  - 이유:
    - “무조건 더 많이”가 아니라 중요한 좌표 하한만 보장
    - 해석이 쉬움

### 우선순위 3

- `Rayleigh-specific robustness regularizer`
  - 설명:
    - 학습 중 channel perturbation을 더 직접 반영하는 보조 손실
  - 이유:
    - 연구적으로 의미는 있지만 구현/해석 난도가 높음
    - 1차 pivot 후보로는 우선순위 낮음

## 권장 1차 실험

`CA-SSFL Orig + semantic_power_enable`

- 비교:
  - `CA-SSFL Orig`
  - `CA-SSFL Orig + semantic_power_alpha sweep`
- 고정:
  - `n_clients=8`
  - `cifar10`
  - `class`
  - `rayleigh`
  - `beta=0.01`
  - `threshold=1.0`
  - `film_max_t=0.7`
  - `film_min_t=0.4`

## 기대 관측

- 성공 시:
  - `-6 dB`와 final acc가 `Orig`보다 상승하거나 유지
  - comm는 거의 유지
- 실패 시:
  - 중요도 편중으로 과도한 brittle behavior가 생김
  - 그러면 다음 단계는 `importance floor`로 이동

## 다음 단계 제안

이 `PLAN` 승인 후, 바로 `SPEC.md`에서

- `semantic_power_alpha` 후보값
- seed set
- retention rule
- claim-making 기준

을 고정하고 실행으로 넘어간다.
