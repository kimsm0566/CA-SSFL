# Codebase Map

This file is a quick orientation guide for the active parts of the repository.

## Top-Level Layout

- `src/`
  - all executable code, datasets, checkpoints, scripts, and result artifacts
  - `src/README.md` is legacy upstream context and not the canonical runtime guide for this repository
- `docs/`
  - durable documentation for agent-assisted research workflows
- `tmp/`
  - scratch and active experiment outputs
  - new directories should use `tmp/YYYY-MM-DD/<run-slug>/`

## Core Execution Flow

### 1. Experiment Entry

- `src/run_exp_main.py`
  - parses CLI arguments
  - initializes MPI
  - creates server and client nodes
  - launches training through `Trainer`
  - runs a post-training multi-SNR evaluation
  - saves `.npz` artifacts

### 2. Configuration

- `src/utils/option.py`
  - canonical command-line arguments for algorithms, datasets, channel type, compression, thresholds, and training budget

### 3. Data

- `src/data/data.py`
  - dataset loading for MNIST, Fashion-MNIST, and CIFAR-10
  - client-side data partitioning
  - PyTorch dataloader construction

### 4. Node Construction

- `src/utils/client.py`
  - creates the client-side model and server-side model based on `args.algorithm`
  - wraps them in lightweight `Client` and `Server` objects

### 5. Models

- `src/models/model.py`
  - channel simulators: `AWGNChannel`, `RayleighChannel`
  - SC-USFL encoder and decoder
  - FiLM and VIB based semantic encoders and decoders
  - split client and server ResNet variants
  - resource monitor for SC-USFL dimension decisions

### 6. Training Logic

- `src/utils/trainer.py`
  - contains the main server and client loops
  - handles forward and backward MPI exchange
  - computes communication cost
  - performs aggregation
  - dispatches to algorithm-specific routines:
    - `SFL`
    - `SSFLv4`
    - `SSFLv5`
    - `SSFLv6`
    - `SC-USFL`
    - `FL`

### 7. Evaluation

- `src/utils/eval.py`
  - round-level evaluation
  - channel-aware global evaluation
  - SNR sweep evaluation after training

## Experiment Scripts And Analysis

- `src/run_exp_cuda0.sh`
  - current sweep script for repeated MPI experiments
- `src/plot_copy.py`
  - reads stored `.npz` results and generates comparison plots
- `src/comp.py`, `src/latency.py`, `src/test.py`
  - analysis helpers and ad hoc measurement scripts

## Output And Artifact Directories

- `tmp/`
  - active smoke outputs and exploratory run artifacts
  - prefer `tmp/YYYY-MM-DD/<run-slug>/` over new top-level run folders
- `src/results/`
  - current experiment outputs
- `src/old_results/`
- `src/old_results2/`
  - historical outputs retained for comparison
- `src/checkpoints/`
  - pretrained semantic communication model weights
- `src/datasets/`
  - dataset artifacts

These directories should be treated as protected unless the user explicitly asks to modify them.

## What To Read Before Changing Behavior

- training behavior: `src/utils/trainer.py`
- architecture behavior: `src/models/model.py`
- evaluation behavior: `src/utils/eval.py`
- experiment defaults and axes: `src/utils/option.py`, `src/run_exp_cuda0.sh`
