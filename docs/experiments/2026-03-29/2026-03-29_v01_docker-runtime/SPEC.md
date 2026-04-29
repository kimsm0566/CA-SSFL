# Experiment Spec

## Metadata

- Experiment id: 2026-03-29_v01_docker-runtime
- Start date: 2026-03-29
- Status: completed
- Owner: agent-assisted setup

## Summary

Create a Docker-based runtime so the `src` code can be executed in a repeatable environment with OpenMPI and the main Python dependencies preinstalled.

## Question

Can we package the current codebase into a practical Docker workflow that supports the main training entrypoint without relying on the user's local Python environment?

## Hypothesis

If we provide a Docker image with OpenMPI, PyTorch, and the main runtime dependencies, plus wrappers for MPI execution, then the repository will be easier to execute and validate consistently across machines.

## Baseline

- Baseline algorithm: not applicable
- Baseline config: not applicable
- Baseline artifact path: not applicable
- Why this is the right comparison: this is an execution-environment change, not a model comparison

## Fixed Conditions

- repository scope: `/home/sunmin/SFL_Semantic`
- code path: `src/run_exp_main.py`
- execution style: Docker plus bind-mounted repository

## Change Under Test

- intended code paths: runtime packaging and documentation only
- changed variable(s): execution environment
- search space: minimal Docker setup that supports the main experiment path

## Metrics

### Primary

- image can provide MPI runtime
- container can resolve the main Python dependencies
- users get a simple command to run `run_exp_main.py`

### Secondary

- lower onboarding friction
- clearer runtime assumptions

## Validation Plan

### Smoke Check

- command: inspect generated Docker files and shell wrappers, run shell syntax checks
- expected signal of success: files are internally consistent and shell scripts are valid

### Matched Comparison

- command(s): not applicable
- expected artifact path: not applicable

### Robustness Follow-Up

- extra seeds: not applicable
- extra SNRs: not applicable
- extra channel settings: not applicable

## Promotion Criteria

The repository should have a documented Docker path with a build file, compose file, and wrappers for MPI execution.

## Stop Criteria

Stop once the runtime files and docs exist and are internally consistent.

## Risks And Confounders

- possible confounders: dependency mismatch between old README pins and current code
- likely failure modes: package incompatibility, Docker GPU differences, missing datasets on host
- what could invalidate the result: if the runtime cannot execute the main path on a real machine
