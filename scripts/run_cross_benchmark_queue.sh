#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/home/sunmin/SFL_Semantic"
RESULT_ROOT="/workspace/tmp/2026-04-09-cross-benchmark"

run_exp() {
  local label="$1"
  shift
  echo "=== START ${label} ==="
  docker compose run --rm sfl-semantic bash -lc "run-exp $*"
  echo "=== END ${label} ==="
}

cd "${REPO_ROOT}"

# Rayleigh baselines
for seed in 1 2 3 4; do
  run_exp \
    "rayleigh_sfl_seed_${seed}" \
    --dataset cifar10 --partition_type class --algorithm SFL --model_type resnetv2 \
    --channel_type rayleigh --n_clients 9 --n_client_data 3000 --batch_size 100 \
    --n_epochs 1 --n_rounds 200 --compressed_dim 4096 --beta 0.01 \
    --pruning_threshold 1.0 --film_max_t 0.7 --film_min_t 0.4 \
    --result_path "${RESULT_ROOT}" --seed "${seed}"
done

for seed in 1 2 3 4; do
  run_exp \
    "rayleigh_scusfl_seed_${seed}" \
    --dataset cifar10 --partition_type class --algorithm SC-USFL --model_type resnetv2 \
    --channel_type rayleigh --n_clients 9 --n_client_data 3000 --batch_size 100 \
    --n_epochs 1 --n_rounds 200 --compressed_dim 1352 --beta 0.01 \
    --pruning_threshold 1.0 --film_max_t 0.7 --film_min_t 0.4 \
    --result_path "${RESULT_ROOT}" --seed "${seed}"
done

# Rayleigh ours: fill seeds 3,4 only because seeds 1,2 already exist in legacy matched runs.
for seed in 3 4; do
  run_exp \
    "rayleigh_ssflv6_baseline_seed_${seed}" \
    --dataset cifar10 --partition_type class --algorithm SSFLv6 --model_type resnetv2 \
    --channel_type rayleigh --n_clients 9 --n_client_data 3000 --batch_size 100 \
    --n_epochs 1 --n_rounds 200 --compressed_dim 4096 --beta 0.01 \
    --pruning_threshold 1.0 --film_max_t 0.7 --film_min_t 0.4 \
    --semantic_spreading_enable 0 --snr_adaptive_beta_enable 0 \
    --semantic_power_enable 0 --semantic_power_alpha 2.0 \
    --result_path "${RESULT_ROOT}" --seed "${seed}"
done

for seed in 3 4; do
  run_exp \
    "rayleigh_ssflv6_candidate_seed_${seed}" \
    --dataset cifar10 --partition_type class --algorithm SSFLv6 --model_type resnetv2 \
    --channel_type rayleigh --n_clients 9 --n_client_data 3000 --batch_size 100 \
    --n_epochs 1 --n_rounds 200 --compressed_dim 4096 --beta 0.01 \
    --pruning_threshold 1.0 --film_max_t 0.7 --film_min_t 0.4 \
    --semantic_spreading_enable 1 --snr_adaptive_beta_enable 1 \
    --semantic_power_enable 0 --semantic_power_alpha 2.0 \
    --result_path "${RESULT_ROOT}" --seed "${seed}"
done

# AWGN baselines
for seed in 1 2 3 4; do
  run_exp \
    "awgn_sfl_seed_${seed}" \
    --dataset cifar10 --partition_type class --algorithm SFL --model_type resnetv2 \
    --channel_type awgn --n_clients 9 --n_client_data 3000 --batch_size 100 \
    --n_epochs 1 --n_rounds 200 --compressed_dim 4096 --beta 0.01 \
    --pruning_threshold 1.0 --film_max_t 0.7 --film_min_t 0.4 \
    --result_path "${RESULT_ROOT}" --seed "${seed}"
done

for seed in 1 2 3 4; do
  run_exp \
    "awgn_scusfl_seed_${seed}" \
    --dataset cifar10 --partition_type class --algorithm SC-USFL --model_type resnetv2 \
    --channel_type awgn --n_clients 9 --n_client_data 3000 --batch_size 100 \
    --n_epochs 1 --n_rounds 200 --compressed_dim 1352 --beta 0.01 \
    --pruning_threshold 1.0 --film_max_t 0.7 --film_min_t 0.4 \
    --result_path "${RESULT_ROOT}" --seed "${seed}"
done
