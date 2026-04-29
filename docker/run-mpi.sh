#!/usr/bin/env bash
set -euo pipefail

check-gpu

if [ "$#" -eq 0 ]; then
    echo "Usage: run-mpi -n <world_size> python run_exp_main.py [args...]" >&2
    exit 1
fi

exec mpiexec --allow-run-as-root "$@"
