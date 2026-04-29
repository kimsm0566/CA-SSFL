# AGENTS.md

## Mission

This repository is a research codebase for improving the communication-performance trade-off in semantic, split, and federated learning under communication constraints.

Primary objective:

- increase or preserve task performance while reducing communication cost

Secondary objective:

- improve robustness across channel conditions, SNR regimes, and random seeds

Treat all performance claims as comparative. A change is only an improvement if it beats a matched baseline under controlled conditions.

## How To Use This File

- Use this file as the entry point, not the full manual.
- Keep detailed process, experiment, and evaluation guidance under `docs/`.
- Keep Markdown documentation under `docs/`, not under `src/`, unless the user explicitly asks otherwise.

## Operational Ownership

- `docs/DOCKER.md`
  - canonical runtime, command form, and execution-path rules
- `docs/evals/EVAL_PROTOCOL.md`
  - seed policy, evaluation levels, comparison contract, and claim language
- `docs/experiments/README.md`
  - experiment folder structure and experiment-document conventions
- `docs/experiments/ACTIVE_PLAN.md`
  - current research snapshot only
- `docs/experiments/ACTIVE_PLAN_HISTORY.md`
  - archived phase notes and older priority snapshots
- `docs/PROJECT_DEFINITION.md`
  - project scope, problem setting, and mechanism framing
- `docs/PROJECT_NOVELTY.md`
  - claim-safe novelty framing against prior work

## Repository Reality

- Code lives under `src/`.
- Documentation lives under `docs/`.
- This directory is not currently a git repository. Do not assume branches, commits, or git history are available.
- If documentation and code disagree, trust observable code behavior and update the relevant docs in the same task.
- Canonical experiment execution uses the Docker GPU runtime described in `docs/DOCKER.md`. Use host-side execution only for static checks or when the user explicitly asks otherwise.
- `src/README.md` is preserved as legacy upstream context and is not the canonical operating guide for this repository.

## Read First

- `docs/README.md`
- `docs/CODEBASE_MAP.md`
- `docs/HARNESS.md`
- `docs/DOCKER.md`
- `docs/experiments/README.md`
- `docs/experiments/ACTIVE_PLAN.md`
- `docs/evals/EVAL_PROTOCOL.md`

## Important Code Paths

- `src/run_exp_main.py`: experiment entrypoint, MPI setup, result saving, SNR sweep
- `src/utils/trainer.py`: server and client training loops, communication accounting, aggregation
- `src/models/model.py`: channel models, semantic encoders and decoders, client and server networks
- `src/utils/eval.py`: evaluation helpers and multi-SNR testing
- `src/data/data.py`: dataset loading, partitioning, dataloaders
- `src/utils/client.py`: client and server object construction
- `src/run_exp_cuda0.sh`: current experiment sweep script

## Protected Areas

Do not modify the following without explicit user approval:

- `src/datasets/`
- `src/data/cifar-10-batches-py/`
- `src/checkpoints/`
- `src/results/`
- `src/old_results/`
- `src/old_results2/`

If a task needs new outputs, add new artifacts instead of rewriting historical raw artifacts.

## Research Workflow

1. Start from a clear hypothesis.
2. For substantial experiments or behavior-changing code work, use a dated, versioned folder under `docs/experiments/`.
3. Draft `PLAN.md` before execution so the user can review and refine the approach.
4. After alignment, write or update `SPEC.md` with the agreed fixed conditions and validation path.
5. Keep fixed conditions explicit before changing code.
6. Make the smallest code change that tests one concrete idea.
7. Run the smallest feasible validation before broad sweeps.
8. Record meaningful runs in `docs/experiments/RESULTS_LEDGER.md`.
9. Report wins, regressions, and unknowns.

## Plan Review Rule

- For substantial experiments or behavior-changing code changes, do not execute from an implicit plan.
- Write `PLAN.md` first, let the user review it, and use the reviewed plan as the basis for `SPEC.md` and execution.
- `PLAN.md` is the collaboration artifact for shaping the approach.
- `SPEC.md` is the execution artifact for fixed conditions, comparison rules, and validation details.
- Tiny documentation edits and mechanical cleanups do not require a dedicated `PLAN.md` unless the user asks for one.

## Literature Review Workflow

- Store literature review notes under `docs/literature/`.
- Keep one Markdown note per paper under `docs/literature/papers/`.
- Each paper note should include:
  - citation and source link
  - one-line takeaway
  - relation to this project
  - weaknesses and reproducibility risks
  - actionable follow-up ideas or experiment hypotheses
- Keep literature notes separate from experiment plans.
- If a paper motivates a concrete experiment, create or update the matching artifact under `docs/experiments/`.
- Prefer source links in the note. If a local PDF is needed for ongoing review, store it under `docs/literature/sources/` using a matching slug.

## Reproducibility Rules

When changing training or evaluation logic, preserve or explicitly re-document:

- dataset
- partition type
- number of clients
- client data size
- batch size
- number of local epochs
- number of rounds
- algorithm
- model type
- channel type
- training SNR or SNR range
- compressed dimension
- pruning threshold
- beta schedule
- seed set
- result path

Do not silently change defaults that would invalidate earlier comparisons.

## Evaluation Rules

- Use `docs/evals/EVAL_PROTOCOL.md` as the canonical source for seed policy, evaluation levels, comparison contract, and claim language.
- Always report communication cost with accuracy.
- If fixed conditions differ from the baseline, label the run exploratory rather than claim-making.

## Validation Expectations

- Docs-only changes: verify links, paths, and cross-references.
- Python changes: run `python -m py_compile` on touched Python files.
- Training or eval logic changes: run the smallest feasible smoke check and say exactly what was and was not validated.
- If heavy experiments were not run, state that explicitly.

## Good Changes

- tighter experiment controls
- better logging and result schemas
- clearer baseline reproduction
- smaller and more testable experimental diffs
- stronger sanity checks
- cleaner separation between canonical evaluation code and exploratory code

## Risky Changes

- changing default hyperparameters used by existing scripts
- altering data partition semantics
- changing result loading semantics without updating docs
- mixing exploratory shortcuts into canonical evaluation paths
- editing historical results or checkpoints in place

## Documentation Policy

- `AGENTS.md` should stay short and stable.
- Detailed operational knowledge belongs in `docs/`.
- Plans are first-class artifacts.
- New notes under `docs/experiments/` and `docs/literature/` should be written in Korean by default unless the user asks otherwise.
- Keep file and folder names ASCII-friendly even when the document body is written in Korean.
- If you discover new project knowledge that future agents will need, write it down in `docs/` rather than leaving it implicit.
