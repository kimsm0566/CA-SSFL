# Table 1 Block A Seed 3,4 확장 계획

## 목적

- `Table 1`의 왼쪽 블록 `(\beta, \tau_{VIB})` 결과를 `seed 1,2,3,4` 기준으로 통일한다.
- 기존 `seed 1,2` 결과와 결합해 논문용 `4-seed` 표를 다시 만든다.

## 배경

- 현재 `Block A` 재실험 결과는 `seed 1,2`만 존재한다.
- `Block B`는 이미 `seed 1,2,3,4`로 완료됐다.
- 따라서 같은 조건 `(beta=0.01, tau=1.0, film=0.7/0.4)`에서도 좌우 블록이 서로 다른 seed set 평균을 보고 있어 표가 일관되지 않는다.

## 가설

- `seed 3,4`를 추가하면 `Block A`도 `4-seed` 기준으로 재집계 가능해지고, `Table 1`의 좌우 블록을 동일한 seed policy로 맞출 수 있다.
- 현재 대표 기본점 `beta=0.01, pruning_threshold=1.0`의 상대적 위치도 `4-seed` 기준에서 다시 확인할 수 있다.

## 범위

- dataset: `cifar10`
- channel: `AWGN`, `Rayleigh`
- algorithm: `SSFLv6`
- grid:
  - `beta ∈ {0.100, 0.050, 0.010, 0.005, 0.001}`
  - `pruning_threshold ∈ {1.5, 1.0, 0.5}`
- 고정값:
  - `film_max_t=0.7`
  - `film_min_t=0.4`
- 신규 seed:
  - `3,4`

## 실행 수

- 총 `60 runs`
- 계산:
  - `2 channels × 5 betas × 3 thresholds × 2 seeds`

## 예상 시간

- run당 예상 `6~8분`
- 총 예상 `6~8시간`

## 시간 추정 전제

- Docker GPU runtime 사용
- `n_clients=8`, `n_rounds=200`
- 중간 stall 없이 순차 실행
- artifact-first skip/retry 하네스 사용

## 산출물

- 새 결과 루트:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-14/2026-04-14-table1-blockA-seed34`
- 새 문서 루트:
  - `/home/sunmin/SFL_Semantic/docs/experiments/2026-04-14/2026-04-14_15-28_v01_table1-blockA-seed34-extension`

## 후속

1. `Block A seed 3,4` 완료
2. 기존 `Block A seed 1,2`와 합쳐 `4-seed` 재집계
3. `Block B 4-seed`와 함께 `AWGN`, `Rayleigh` 표 스니펫 재작성
