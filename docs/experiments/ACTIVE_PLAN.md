# Active Plan

This file stores only the current research snapshot for the repository.

Historical phase notes and older dated priority snapshots live in [ACTIVE_PLAN_HISTORY.md](/home/sunmin/SFL_Semantic/docs/experiments/ACTIVE_PLAN_HISTORY.md).

## Current Objective

Establish a reliable and claim-safe research loop that improves the communication-performance frontier under matched conditions.

## Active Baselines And Defaults

- keep `CA-SSFL Orig` as the active Rayleigh baseline
- use the canonical Docker GPU runtime from `docs/DOCKER.md`
- use the seed policy and comparison rules from `docs/evals/EVAL_PROTOCOL.md`

## Immediate Next Actions

- rerun `CA-SSFL` on `cifar100` with the newly selected channel-specific representative settings:
  - `AWGN`: `beta=0.05`, `tau_VIB=1.0`, `film_max_t=0.7`, `film_min_t=0.2`
  - `Rayleigh`: `beta=0.1`, `tau_VIB=1.0`, `film_max_t=0.7`, `film_min_t=0.4`
- regenerate `cifar100` integrated graphs after the new `CA-SSFL` artifacts are complete
- keep `semi-dense`, `latent mixing`, and first-pass repetition / CSI-mask / imputation variants demoted from active candidate status
- keep the MPI trace option for any future SSFL stall reproduction

## Current Research Questions

1. `base`를 semantic mask 내부로 제한하고 `refinement`를 semantic-aware mixed score로 바꾸면, 직전 variable refinement의 seed collapse를 줄일 수 있는가?
2. `cifar100`에서 최신 대표 `CA-SSFL` 설정이 `SFL`, `SC-USFL` 대비 어떤 communication-performance frontier를 만드는가?
3. `low-SNR support floor`를 더 보수적으로 적용하면 accuracy 손실 없이 Rayleigh 통신량을 줄일 수 있는가?
4. `semantic power`를 low-alpha로 약하게 적용하면 현재의 accuracy 붕괴 없이 핵심 좌표 보호 이득을 얻을 수 있는가?
5. 현재 `SSFLv6` 계열의 model communication 회귀를 accuracy 손상 없이 줄일 수 있는가?
6. 어떤 수준의 seed variance를 noise로 보고 promotion 결정을 내려야 하는가?
7. latent-summary drift를 trigger로 쓰는 reasoning-aware silence가 exploratory smoke에서도 comm를 줄일 수 있는가?

## Recently Locked Decisions

- stop treating fixed-budget `method2` as a promoted direction
- keep older phase notes and dated priority snapshots in `ACTIVE_PLAN_HISTORY.md`

## Update Rule

Update this file when:

- the top research priority changes
- a baseline is promoted or rejected
- a new bottleneck becomes the main focus
- the next concrete actions change
