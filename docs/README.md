# Docs Index

This directory is the documentation system of record for agent-assisted research in this project.

The goal is not to write a large manual. The goal is to keep the minimum set of durable, versioned artifacts that let a new agent or researcher understand the project, design controlled experiments, run them, and evaluate them consistently.

## Document Map

- `CODEBASE_MAP.md`
  - high-level map of the code structure and the responsibility of each core module
- `HARNESS.md`
  - research workflow and durable artifact expectations
- `DOCKER.md`
  - canonical GPU-first execution path and runtime rules
- `HARNESS_BEST_PRACTICES.md`
  - rationale behind the harness rules; explanatory, not the operating contract
- `PROJECT_NOVELTY.md`
  - claim-safe novelty framing and prior-work boundary
- `PROJECT_DEFINITION.md`
  - paper-grounded and current-state definition of what this project is actually studying
- `literature/README.md`
  - literature review workflow, storage rules, and paper-note expectations
- `experiments/README.md`
  - experiment folder structure plus core and auxiliary experiment-document types
- `experiments/ACTIVE_PLAN.md`
  - current working research snapshot and next actions only
- `experiments/ACTIVE_PLAN_HISTORY.md`
  - archived phase notes and older priority snapshots
- `experiments/EXPERIMENT_TEMPLATE.md`
  - pointer to the folder-based experiment template
- `experiments/RESULTS_LEDGER.md`
  - append-only log of meaningful experiment runs and decisions
- `evals/EVAL_PROTOCOL.md`
  - evaluation contract, metrics, comparison rules, and reporting guidance

## Source Of Truth By Topic

- Entry point and repository guardrails:
  - `../AGENTS.md`
- Workflow and artifact lifecycle:
  - `HARNESS.md`
- Runtime and command form:
  - `DOCKER.md`
- Evaluation levels, seed policy, matched-comparison rules, and claim language:
  - `evals/EVAL_PROTOCOL.md`
- Experiment folder layout and per-attempt file conventions:
  - `experiments/README.md`
- Current research priorities only:
  - `experiments/ACTIVE_PLAN.md`
- Archived priorities and completed phase notes:
  - `experiments/ACTIVE_PLAN_HISTORY.md`
- Project scope and mechanism framing:
  - `PROJECT_DEFINITION.md`
- Prior-work boundary and novelty framing:
  - `PROJECT_NOVELTY.md`
- Rationale for the harness design:
  - `HARNESS_BEST_PRACTICES.md`

`src/README.md` is preserved as legacy upstream context only. Do not use it as the canonical runtime or experiment guide for this repository.

## Working Rules

- Keep new Markdown documentation here under `docs/`.
- Keep new experiment attempts under `docs/experiments/YYYY-MM-DD/`.
- Keep new scratch or result directories for active work under `tmp/YYYY-MM-DD/`.
- Prefer small, durable documents over one large instruction file.
- If code behavior changes in a way that affects experiments or evaluation, update the relevant docs in the same task.
- If a document becomes stale, update it or delete it. Do not let contradictory docs accumulate.
- For seed policy, comparison rules, and claim language, defer to `evals/EVAL_PROTOCOL.md` rather than restating local copies.

## Recommended Read Order For A New Agent

1. `../AGENTS.md`
2. `CODEBASE_MAP.md`
3. `HARNESS.md`
4. `DOCKER.md`
5. `evals/EVAL_PROTOCOL.md`
6. `experiments/README.md`
7. `experiments/ACTIVE_PLAN.md`
8. `PROJECT_DEFINITION.md` when the task involves project framing or paper alignment
9. `PROJECT_NOVELTY.md` when the task involves positioning, related work, or claim framing
10. `literature/README.md` when the task involves paper review or related work
11. `experiments/ACTIVE_PLAN_HISTORY.md` when historical context is needed

## Maintenance Policy

- `AGENTS.md` is the short entrypoint.
- `docs/` contains the detailed, durable context.
- Plans, evaluation rules, and experiment logs should be treated as first-class project artifacts.
