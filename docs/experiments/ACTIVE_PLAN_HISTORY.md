# Active Plan History

이 문서는 [ACTIVE_PLAN.md](/home/sunmin/SFL_Semantic/docs/experiments/ACTIVE_PLAN.md)에서 분리한 이력 보관 문서다.

목적은 현재 우선순위 파일을 짧게 유지하고,

- 지난 phase 기록
- 현재 active set에서 내려간 질문
- 날짜별 priority snapshot

을 보존하는 것이다.

## 사용 규칙

- 현재 바로 해야 할 일은 `ACTIVE_PLAN.md`에 둔다.
- 이미 종료된 phase 요약이나 오래된 우선순위 메모는 이 문서로 옮긴다.
- seed policy, claim language, matched-comparison 규칙은 이 문서가 아니라 `docs/evals/EVAL_PROTOCOL.md`를 따른다.

## 2026-04-14 정리 이전 phase 기록

### Phase 0: Harness bootstrap

- done: create root `AGENTS.md`
- done: create docs-based research harness artifacts
- done: use these documents as the default workflow for research changes

### Phase 1: Baseline reproduction

- done: define a provisional baseline comparison set around `SSFLv6`
- done: canonical seed set for experiments is now `1,2,3,4`
- done: confirm a provisional matched setting: `cifar10`, `class`, `rayleigh`, `snr_db=12`, `n_clients=9`, `n_client_data=3000`, `batch_size=100`, `n_epochs=1`, `n_rounds=200`, `compressed_dim=4096`, `beta=0.0005`, `pruning_threshold=1.0`
- todo: verify the current `.npz` schema used by training and plotting

### Phase 2: Bottleneck diagnosis

- done: identify where communication cost is dominated for current `SSFLv6`:
  - data payload and index overhead both increased
  - model transfer also increased to `46.97 MB/round`
- done: identify which algorithms currently define the strongest frontier for `seed=1`
- todo: measure variance across seeds before setting promotion thresholds

### Phase 3: Targeted interventions

- todo: propose and test one change at a time in these buckets:
  - adaptive compression
  - masking and index overhead reduction
  - training stability
  - evaluation and result schema cleanup
- done: diagnose Rayleigh robustness regression of `SSFLv6` relative to `SC-USFL` and validate that `spreading + snr-adaptive beta` can beat `SC-USFL` on matched `Rayleigh` seeds
- in progress at the time: prototype a reasoning-triggered communication gate on the `SSFLv6` client path
- done: rerun staged mask-reduction candidates at matched `200` rounds for `seed=2`
- done: identify the current best single-seed candidate from that staged run:
  - `beta=0.00075` lowered total comm from `30541.49 MB` to `28950.00 MB`
  - accuracy also rose from `42.19%` to `42.71%`

## 보관된 연구 질문

아래 질문들은 과거 `ACTIVE_PLAN.md`에 있었지만, 현재 active snapshot에서는 우선순위를 낮추거나 보다 좁은 현재 질문으로 흡수했다.

1. `beta=0.00075`의 single-seed improvement가 `seed 1,3,4`에서도 유지되는가?
2. `SSFLv6_w_o_beta`의 accuracy 우위와 `SSFLv6 beta=0.00075`의 trade-off 우위 중 어느 쪽이 multi-seed에서 더 안정적인가?
3. 현재 `SSFLv6`의 model comm 회귀를 accuracy 손상 없이 줄일 수 있는가?
4. 어떤 수준의 seed variance를 noise로 보고 promotion 결정을 내려야 하는가?
5. latent-summary drift를 trigger로 쓰는 reasoning-aware silence가 exploratory smoke에서도 comm를 줄일 수 있는가?
6. `base-support + refinement-support` 재구현에서 `base`를 semantic mask 내부로 제한하고 `refinement`를 semantic-aware mixed score로 바꾸면, 직전 variable refinement의 seed collapse를 줄일 수 있는가?
7. `low-SNR support floor`를 더 보수적으로 적용하면 accuracy 손실 없이 Rayleigh 통신량을 줄일 수 있는가?
8. `semantic power`를 low-alpha로 약하게 적용하면 현재의 accuracy 붕괴 없이 핵심 좌표 보호 이득을 얻을 수 있는가?

## 날짜별 우선순위 스냅샷

### 2026-04-13

- `Table I` 오른쪽 블록(`film_max_t`, `film_min_t`) 재실험 계획 수립 완료
- 공통 대표 파라미터는 `beta=0.010`, `pruning_threshold=1.0`
- 다음 실행 후보:
  - `AWGN/Rayleigh`
  - `film_max_t x film_min_t` grid
  - `seed 1,2,3,4`

### 2026-04-14

- `cifar100` 교차 벤치마크를 최신 `CA-SSFL` 대표 설정으로 다시 실행
- `CA-SSFL` 대표 설정:
  - `beta=0.010`
  - `pruning_threshold=1.0`
  - `film_max_t=0.7`
  - `film_min_t=0.2`
- 비교군:
  - `SFL`
  - `SC-USFL`
  - `CA-SSFL`
- 채널:
  - `AWGN`
  - `Rayleigh`
- seed set:
  - `1,2,3,4`
