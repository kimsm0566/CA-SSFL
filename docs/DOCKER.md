# Docker Runtime

This repository is configured for GPU-first Docker execution.
This is the canonical runtime for all experiments, smoke runs, and matched comparisons in this project.
Host-side execution should be treated as static-validation-only unless the user explicitly asks otherwise.

This file is the source of truth for runtime and command-form rules. Other documents should link here instead of restating execution policy in detail.

## Prerequisites

Before using this setup, the host must satisfy all of the following:

- NVIDIA driver is installed and `nvidia-smi` works on the host
- Docker can expose GPUs
- `nvidia-container-toolkit` is installed
- Docker daemon has the `nvidia` runtime registered

Useful checks:

```bash
docker info | rg -i "runtimes|default runtime|nvidia"
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu20.04 nvidia-smi
```

## What Is Included

- `Dockerfile`
  - NVIDIA CUDA runtime base image
  - OpenMPI
  - CUDA-enabled PyTorch
  - Python dependencies needed for the main training and evaluation path
- `docker-compose.yml`
  - development-style runtime with the repository mounted at `/workspace`
  - GPU access enabled by default
- `check-gpu`
  - quick preflight check for CUDA visibility inside the container
- `run-exp`
  - wrapper that launches `run_exp_main.py` with `world_size = n_clients + 1`
- `run-mpi`
  - lower-level wrapper around `mpiexec`

## Important Behavior

- the container works from `/workspace/src`
- the repository root is bind-mounted, so host-side datasets, checkpoints, and results are visible inside the container
- `WANDB_MODE=offline` is set by default
- `MPLBACKEND=Agg` is set for headless plotting
- GPU access is expected to be available without passing `--gpus all` manually on each `docker compose run`
- `run-exp` and `run-mpi` perform a CUDA preflight before launching MPI so experiments fail fast if the container cannot see a GPU

## Policy

- Use `docker compose build` to prepare the runtime.
- Use `docker compose run --rm sfl-semantic check-gpu` before the first experiment on a machine or after runtime changes.
- Use `docker compose run --rm sfl-semantic run-exp ...` for normal experiment entrypoint execution.
- Record experiment commands in docs using the Docker form, not raw host-side `python` or `mpiexec`.
- Do not treat a host-side run as canonical evidence for claim-making comparisons.

## Build

```bash
docker compose build
```

## GPU Preflight

Run this first after build:

```bash
docker compose run --rm sfl-semantic check-gpu
```

Expected behavior:

- CUDA is reported as available
- at least one GPU device name is printed

## Start An Interactive Shell

```bash
docker compose run --rm sfl-semantic bash
```

## Run The Main Experiment Entry

The `run-exp` wrapper reads `--n_clients` and automatically adds one server process.

Example:

```bash
docker compose run --rm sfl-semantic \
  run-exp \
  --dataset=mnist \
  --algorithm=SSFLv6 \
  --channel_type=awgn \
  --n_clients=2 \
  --n_client_data=10 \
  --batch_size=10 \
  --n_epochs=1 \
  --n_rounds=1 \
  --compressed_dim=4096 \
  --result_path=/workspace/tmp/YYYY-MM-DD/docker-gpu-smoke-results \
  --seed=0
```

In that example:

- `--n_clients=2` means two client processes
- `run-exp` launches `mpiexec -n 3 ...` because one extra server process is required
- replace `YYYY-MM-DD` with the local run date before execution
- keep new outputs under `/workspace/tmp/YYYY-MM-DD/<run-slug>`
- the result path is outside protected historical result directories

## Run MPI Manually

Use `run-mpi` if you want direct control over world size:

```bash
docker compose run --rm sfl-semantic \
  run-mpi -n 3 python run_exp_main.py \
  --dataset=mnist \
  --algorithm=SSFLv6 \
  --channel_type=awgn \
  --n_clients=2 \
  --n_client_data=10 \
  --batch_size=10 \
  --n_epochs=1 \
  --n_rounds=1 \
  --compressed_dim=4096 \
  --result_path=/workspace/tmp/YYYY-MM-DD/docker-gpu-smoke-results \
  --seed=0
```

## Data And Checkpoints

- training code expects to run from `/workspace/src`
- default dataset path is `./datasets` relative to `/workspace/src`
- checkpoint paths are resolved relative to `/workspace/src`

Because `docker-compose.yml` bind-mounts the repository root, existing host-side files under:

- `src/datasets/`
- `src/checkpoints/`
- `src/results/`

remain available inside the container.

## Notes

- This setup is designed for the current codebase rather than the stale environment in the original README.
- GPU visibility does not guarantee that every experiment is efficient on a single GPU when using MPI with multiple ranks.
- This document describes runtime setup only. It does not make any performance claim about the algorithms.
