#!/usr/bin/env bash
set -euo pipefail

cd /workspace/src
check-gpu

n_clients=2
args=()

while [ "$#" -gt 0 ]; do
    case "$1" in
        --n_clients=*)
            n_clients="${1#*=}"
            args+=("$1")
            shift
            ;;
        --n_clients)
            if [ "$#" -lt 2 ]; then
                echo "Error: --n_clients requires a value" >&2
                exit 1
            fi
            n_clients="$2"
            args+=("$1" "$2")
            shift 2
            ;;
        *)
            args+=("$1")
            shift
            ;;
    esac
done

world_size=$((n_clients + 1))

exec mpiexec --allow-run-as-root -n "$world_size" python run_exp_main.py "${args[@]}"
