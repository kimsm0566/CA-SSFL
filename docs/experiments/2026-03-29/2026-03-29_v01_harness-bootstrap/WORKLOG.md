# Worklog

Use this file as the running collaboration log for the attempt.

## Context

- Current status: completed
- Current blocker: none
- Next concrete action: use this structure for the first real model or evaluation change

## Log

- Date: 2026-03-29
- Action: created root `AGENTS.md`
- Files changed: `AGENTS.md`
- Commands run: repository inspection commands only
- Artifacts produced: root agent entrypoint
- Observation: the repository had no prior agent-operating documents
- Decision: keep `AGENTS.md` short and move detailed guidance into `docs/`

- Date: 2026-03-29
- Action: created docs-based harness files
- Files changed: `docs/README.md`, `docs/CODEBASE_MAP.md`, `docs/HARNESS.md`, `docs/evals/EVAL_PROTOCOL.md`, `docs/experiments/ACTIVE_PLAN.md`, `docs/experiments/RESULTS_LEDGER.md`
- Commands run: repository inspection commands only
- Artifacts produced: initial harness document set
- Observation: `docs/` was empty, so a clean structure was possible
- Decision: keep planning and evaluation as first-class repository artifacts

- Date: 2026-03-29
- Action: added public best-practice summary and folder-based experiment structure
- Files changed: `docs/HARNESS_BEST_PRACTICES.md`, `docs/experiments/README.md`, `docs/experiments/_template/*`
- Commands run: repository inspection commands only
- Artifacts produced: best-practice note and per-attempt experiment workflow
- Observation: folder-based attempts fit the project's iterative research style better than one shared experiment template
- Decision: organize substantial work by dated versioned folders with `SPEC.md`, `WORKLOG.md`, and `RESULT.md`

## Open Questions

- what should the canonical baseline matrix be for future claim-making runs?
- what seed set should be treated as canonical for promotion decisions?

## Pending Next Steps

- create the first model-focused experiment folder
- define the baseline comparison matrix
