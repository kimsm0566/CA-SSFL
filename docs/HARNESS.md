# Research Harness

This project should use harness engineering to make agent-assisted research reliable, legible, and reproducible.

In this repository, the harness is not just the model code. It includes:

- task framing
- experiment plans
- fixed-condition control
- execution commands
- validation steps
- result storage
- evaluation protocol
- experiment ledger

## Scope Of This File

This document defines the workflow and artifact model for research work in this repository.

- runtime and command examples live in `docs/DOCKER.md`
- evaluation levels, seed policy, comparison contract, and claim language live in `docs/evals/EVAL_PROTOCOL.md`
- experiment folder layout and experiment-document types live in `docs/experiments/README.md`

If these documents appear to overlap, the topic-owner document above should be treated as the source of truth for that topic.

## Project Objective

The research objective is to improve the communication-performance frontier for semantic, split, and federated learning methods under channel constraints.

In practice, that means:

- reduce communication cost without unacceptable performance loss
- increase performance without unjustified communication growth
- improve robustness across channel conditions and seeds

## Harness Principles

### 1. Use Docs As The Durable Memory

Agents do not retain long-term memory by default. Durable project knowledge must live in the repository.

Required durable artifacts:

- a short root `AGENTS.md`
- an active plan
- a folder-based experiment template
- an evaluation protocol
- a results ledger

### 2. One Hypothesis At A Time

Prefer one experimental idea per code change. Avoid bundles of unrelated tweaks that make attribution impossible.

### 3. Preserve A Canonical Path

Keep canonical training and evaluation logic understandable and stable.

- exploratory shortcuts belong in clearly labeled code paths or temporary scripts
- claim-making evaluations should use the canonical path
- in this repository, the canonical execution path for training, smoke tests, and matched experiments is defined in `docs/DOCKER.md`
- host-side execution should be limited to static validation unless the user explicitly approves another path

### 4. Treat Plans As First-Class Artifacts

Before broad experimentation, write down:

- the hypothesis
- the baseline
- fixed conditions
- changed variables
- metrics
- promotion criteria
- stop conditions

### 5. Separate Smoke Tests From Claims

- smoke tests answer: "does the code run?"
- matched experiments answer: "is this better than baseline?"
- robustness experiments answer: "does the gain survive channel and seed variation?"

Do not use smoke-test outcomes as performance claims.

### 6. Log Meaningful Outcomes

A meaningful run should leave a ledger entry with:

- experiment id
- hypothesis
- changed code path
- config summary
- seed set
- artifact path
- main result
- decision

### 7. Keep The Repo Legible

If a future agent cannot tell why a change was made, the harness is incomplete.

Good legibility means:

- stable file names
- limited hidden assumptions
- explicit evaluation rules
- documented comparison contracts

## Standard Research Loop

1. Read `AGENTS.md`, this file, `docs/DOCKER.md`, `docs/experiments/README.md`, `docs/experiments/ACTIVE_PLAN.md`, and `docs/evals/EVAL_PROTOCOL.md`.
2. Choose one concrete bottleneck or hypothesis.
3. Create `docs/experiments/YYYY-MM-DD/<experiment-folder>/` if the task is substantial.
4. Reserve a matching `tmp/YYYY-MM-DD/<run-slug>/` path for scratch or result outputs.
5. Copy the starter files from `experiments/_template/`.
6. Make the smallest code change that tests the hypothesis.
7. Run a Docker GPU smoke check.
8. Run a matched Docker GPU experiment if the smoke check passes.
9. Record the outcome in `experiments/RESULTS_LEDGER.md`.
10. Update `experiments/ACTIVE_PLAN.md` if priorities changed.

## Promotion Rules

A candidate change should not become the new default unless one of the following is true under matched conditions:

- it improves performance at equal or lower communication cost
- it lowers communication cost with only negligible and justified performance loss
- it improves the Pareto frontier across repeated runs

And it should not introduce obvious regressions in:

- SNR robustness
- seed stability
- reproducibility
- result interpretability

## What This Harness Should Eventually Support

- consistent baseline replication
- controlled ablations
- small smoke runs for quick validation
- matched multi-seed comparisons
- robustness sweeps across SNR and channel type
- append-only result logging
- clear promotion and rollback decisions
