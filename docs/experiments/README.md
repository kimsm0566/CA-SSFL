# Experiments Directory

This directory is organized first by local start date, then by attempt.

Each substantial research attempt should have its own folder so that we can:

- name the idea clearly
- track versions of the same idea
- keep planning, execution notes, and outcomes together
- let future agents resume work from repository-local artifacts

## Folder Naming Rule

Create experiment folders with this pattern:

- `YYYY-MM-DD_HH-MM_vNN_short-slug`

Where:

- `YYYY-MM-DD` is the local start date of the attempt
- `HH-MM` is the local start time of the attempt in 24-hour format
- `vNN` is a two-digit attempt version such as `v01`, `v02`, `v03`
- `short-slug` is a short summary of the idea

Examples:

- `2026-03-29_20-01_v01_harness-bootstrap`
- `2026-03-30_09-30_v01_ssflv6-mask-overhead`
- `2026-04-02_14-10_v02_ssflv6-mask-overhead`
- `2026-04-05_08-45_v01_sc-usfl-dim-policy`

Older folders that already use `YYYY-MM-DD_vNN_short-slug` may remain as legacy records, but new folders should include `HH-MM`.

## Top-Level Organization

To keep `docs/experiments/` readable as the number of attempts grows:

- keep shared files at the top level:
  - `README.md`
  - `ACTIVE_PLAN.md`
  - `ACTIVE_PLAN_HISTORY.md`
  - `RESULTS_LEDGER.md`
  - `_template/`
- place every new experiment folder under its date bucket:
  - `docs/experiments/YYYY-MM-DD/<experiment-folder>/`
- do not create new experiment folders directly under `docs/experiments/`

Legacy top-level experiment folders may remain as historical records, but active folders should be moved into their date bucket when feasible.

## Matching `tmp/` Layout

When an experiment produces scratch outputs, smoke outputs, or run artifacts under `tmp/`, mirror the same date bucket:

- host path:
  - `tmp/YYYY-MM-DD/<run-slug>/`
- Docker path:
  - `/workspace/tmp/YYYY-MM-DD/<run-slug>/`

Examples:

- `docs/experiments/2026-04-11/2026-04-11_07-10_v01_rayleigh-literature-four-method-suite/`
- `tmp/2026-04-11/2026-04-11-rayleigh-literature-four-method-suite/`
- `/workspace/tmp/2026-04-11/2026-04-11-rayleigh-literature-four-method-suite/`

Legacy top-level `tmp/` directories may remain if they already contain historical outputs, but do not create new ones outside a date bucket.

## When To Create A Folder

Create a dated experiment folder when:

- the change is more than a tiny refactor
- the work introduces a new hypothesis
- the task needs repeated runs or decisions over time
- the work may continue across multiple sessions

Do not create a new folder for:

- typo-only documentation edits
- tiny mechanical cleanup with no research relevance
- one-off path fixes with no experimental meaning

## Standard Files Inside Each Folder

Each experiment folder should usually contain:

- `PLAN.md`
  - collaboration-first draft plan to review with the user before execution
- `SPEC.md`
  - the agreed execution spec after the plan has been reviewed
  - should include the expected run count and time estimate whenever prediction is feasible
- `WORKLOG.md`
  - running notes, commands, decisions, blockers, and next actions
- `RESULT.md`
  - final or current outcome summary

Optional extra files are allowed if useful, but do not replace these four by default.

## Core And Auxiliary Files

### Core Files

- `PLAN.md`
  - collaboration-first proposal used to shape the attempt before execution
- `SPEC.md`
  - execution contract with fixed conditions, changed variables, metrics, and validation path
- `WORKLOG.md`
  - human-facing progress log for decisions, blockers, and next actions
- `RESULT.md`
  - compact interpretation of the outcome and the decision

### Auxiliary Files

- `RUNLOG.md`, `RUNLOG_AWGN.md`, `RUNLOG_RAYLEIGH.md`, `RUNLOG_SMOKE.md`
  - execution-oriented logs for launched commands, channel-specific batches, and run status
- `QUEUE_LOG.md`
  - queue planning and long-running batch status
- `WATCHDOG_LOG.md`
  - stall, hang, restart, or watchdog observations during long runs
- `ANALYSIS.md`
  - post-run analysis that is too detailed or too specific for `RESULT.md`
- `*_EXPLAINER.md`, `*_ANALYSIS.md`
  - focused side notes for one method, one failure mode, one seed collapse, or one figure/diagnostic thread

Rules:

- Auxiliary files are optional and should support the core four files, not replace them.
- If both `WORKLOG.md` and `RUNLOG.md` exist, use `WORKLOG.md` for decisions and `RUNLOG.md` for execution traces.
- Keep the current portfolio snapshot in `ACTIVE_PLAN.md`; move older priority snapshots into `ACTIVE_PLAN_HISTORY.md` when the active file starts accumulating history.

## Lifecycle

### Before Execution

1. Create `docs/experiments/YYYY-MM-DD/<experiment-folder>/`.
2. Draft `PLAN.md`.
3. Review and refine the plan with the user.
4. Convert the agreed plan into `SPEC.md`.
5. Confirm the baseline and fixed conditions.
6. Reserve a matching `tmp/YYYY-MM-DD/<run-slug>/` path before execution.
7. If the workload is predictable, record the estimated number of runs and expected wall-clock time in `SPEC.md`.

### During Execution

1. Update `WORKLOG.md` with meaningful progress.
2. Record commands, artifact paths, and decision points.
3. Keep new run outputs under `tmp/YYYY-MM-DD/<run-slug>/`.
4. If the execution contract changes, update `SPEC.md`.
5. If the overall approach changes materially, update `PLAN.md` and re-align before proceeding.
6. If the experiment is a matched algorithm comparison, keep short runs for smoke only and make the actual comparison at the canonical full budget.
7. In this repository, when the matched baseline budget is `200` rounds, candidate-vs-baseline conclusions should also be made at `200` rounds.
8. Record experiment commands using the Docker GPU runtime from `docs/DOCKER.md` unless the user explicitly approves another execution path.
9. Unless the plan explicitly says the run is a smoke or debugging-only pass, follow the canonical seed policy in `docs/evals/EVAL_PROTOCOL.md`.
10. When feasible, log the expected remaining time or total expected duration before launching a long queue.

### After Execution

1. Summarize the outcome in `RESULT.md`.
2. Add a concise row to `RESULTS_LEDGER.md`.
3. Update `ACTIVE_PLAN.md` if priorities changed.
4. If old priority notes no longer belong in the active snapshot, move them into `ACTIVE_PLAN_HISTORY.md`.

## Versioning Guidance

Use a new version folder when:

- the same idea is being retried with a materially different design
- the previous attempt ended inconclusively
- the follow-up should remain comparable but distinct

Use a new slug when:

- the main hypothesis changes
- the baseline changes fundamentally
- the work is no longer the same family of idea

## Relationship To Other Files

- `ACTIVE_PLAN.md`
  - portfolio-level current priorities only
- `ACTIVE_PLAN_HISTORY.md`
  - archived phase notes and older priority snapshots
- dated experiment folders
  - attempt-level planning, agreement, execution, and outcome
- `RESULTS_LEDGER.md`
  - compact global summary across attempts

## Language Policy

- Write new experiment artifacts in Korean by default:
  - `PLAN.md`
  - `SPEC.md`
  - `WORKLOG.md`
  - `RESULT.md`
- Keep folder names and short slugs ASCII-friendly using the existing naming rule.
- Existing older notes may remain mixed-language unless the task explicitly includes translation.

## Seed Policy

- Follow `docs/evals/EVAL_PROTOCOL.md` as the source of truth for the canonical seed policy and claim language.
- New experiments should default to the canonical claim-making seed set defined there.
- If a run uses fewer seeds, the document must explicitly label it as one of:
  - smoke
  - debugging
  - temporary exploratory probe
- Do not treat `seed 1,2` as the default experimental budget anymore.

## Time Estimate Policy

- New `SPEC.md` files should include an execution time estimate whenever the run count and per-run cost are reasonably predictable.
- A useful estimate should include:
  - total number of runs
  - approximate time per run
  - approximate total wall-clock time
  - major assumptions such as channel, rounds, or known stall risk
- If the workload is too uncertain to estimate credibly, say that explicitly instead of omitting the section silently.

## Template

Copy the starter files from:

- `docs/experiments/_template/PLAN.md`
- `docs/experiments/_template/SPEC.md`
- `docs/experiments/_template/WORKLOG.md`
- `docs/experiments/_template/RESULT.md`
