# CIFAR-100 CA-SSFL 채널별 대표 설정 재실험 계획

## 배경

`cifar10` 재탐색 결과 현재 `CA-SSFL`의 채널별 대표 설정은 아래로 정리됐다.

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

하지만 `cifar100`에는 아직 위 설정으로 실행한 `CA-SSFL` 결과가 없다. 기존 `cifar100` benchmark는 `beta=0.01`, `film=0.7/0.2` 공통점만 반영돼 있다.

## 목적

`cifar100`에서 `CA-SSFL`만 채널별 최신 대표 설정으로 다시 실행해, 기존 `SFL`, `SC-USFL` 결과와 합쳐 최신 그래프와 표를 만들 수 있게 한다.

## 범위

- dataset: `cifar100`
- methods rerun:
  - `CA-SSFL` only
- channels:
  - `AWGN`
  - `Rayleigh`
- seeds:
  - `1,2,3,4`

기존 `SFL`, `SC-USFL` 결과는 재사용한다.

## 핵심 질문

1. `cifar100`에서도 채널별 최신 대표 설정이 기존 `CA-SSFL` 공통 설정보다 더 나은가?
2. 새 설정을 반영했을 때 `SFL`, `SC-USFL`, `CA-SSFL` 3-way 그래프가 어떻게 바뀌는가?

## 실행 전략

1. 새 결과 루트를 날짜별로 분리한다.
2. `CA-SSFL`만 `AWGN -> Rayleigh` 순서로 실행한다.
3. `seed_*.npz`를 1차 성공 기준으로 삼는다.
4. 완료 후 기존 `SFL`, `SC-USFL` benchmark와 결합해 `cifar100` 그래프를 다시 만든다.

## 예상 실행 수

- `2 channels x 4 seeds = 8 runs`

## 예상 소요 시간

- run당 약 `8~10분`
- 총 약 `70~100분`

## 시간 추정 전제

- 기존 `cifar100` benchmark와 동일한 Docker GPU runtime 사용
- `run-exp`가 artifact 저장 후 비정상 종료할 수 있으므로, artifact 기준으로 성공 판정
- 중간 stall이 없다는 가정의 추정치

## 산출물

- `SPEC.md`
- `RUNLOG.md`
- 새 `CA-SSFL` 결과 루트
- 완료 후 `RESULT.md`

