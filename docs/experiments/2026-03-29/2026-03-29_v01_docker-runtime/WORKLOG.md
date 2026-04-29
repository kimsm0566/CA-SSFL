# Worklog

Use this file as the running collaboration log for the attempt.

## Context

- Current status: completed
- Current blocker: Docker execution was not run in this sandbox
- Next concrete action: validate the image on a machine with Docker available

## Log

- Date: 2026-03-29
- Action: inspected current Python and MPI dependency expectations
- Files changed: none
- Commands run: repository inspection commands only
- Artifacts produced: dependency notes
- Observation: the README pins are stale relative to the current code, especially for PyTorch
- Decision: target a modern PyTorch runtime for Docker rather than mirror the stale README exactly

- Date: 2026-03-29
- Action: created Docker runtime files
- Files changed: `.dockerignore`, `Dockerfile`, `docker-compose.yml`, `docker/requirements.txt`, `docker/run-mpi.sh`, `docker/run-exp.sh`
- Commands run: repository inspection commands only
- Artifacts produced: Docker build and runtime setup
- Observation: a wrapper was useful because `run_exp_main.py` expects one server process in addition to `n_clients`
- Decision: add `run-exp` so users pass `--n_clients` and the wrapper computes `world_size`

- Date: 2026-03-29
- Action: documented Docker usage
- Files changed: `docs/DOCKER.md`
- Commands run: repository inspection commands only
- Artifacts produced: Docker usage guide
- Observation: the repository already contains datasets and checkpoints, so bind-mounting the repo is the simplest workflow
- Decision: make the compose service mount the full repository root at `/workspace`

## Open Questions

- should there be a separate GPU-specific compose override later?
- should dataset bootstrap be scripted explicitly for clean clones without local data?

## Pending Next Steps

- run `docker compose build`
- run a one-round smoke experiment inside the container
