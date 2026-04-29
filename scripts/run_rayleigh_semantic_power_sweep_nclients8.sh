#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/home/sunmin/SFL_Semantic"
RESULT_ROOT="/workspace/tmp/2026-04-09-rayleigh-semantic-power-sweep-nclients8"
HOST_RESULT_ROOT="${REPO_ROOT}/tmp/2026-04-09-rayleigh-semantic-power-sweep-nclients8"
DOC_ROOT="${REPO_ROOT}/docs/experiments/2026-04-09_21-58_v01_rayleigh-pivot-after-spreading-failure"
LOG_FILE="${DOC_ROOT}/RUNLOG.md"

mkdir -p "${DOC_ROOT}"

log() {
  local ts
  ts="$(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf -- "- [%s] %s\n" "${ts}" "$1" | tee -a "${LOG_FILE}"
}

npz_path() {
  local alpha="$1"
  local seed="$2"
  printf "%s/cifar10/n_clients_8/n_client_data_3000/batch_size_100/data_partition_type_class/model_type_resnetv2/major_percent_0.8/n_epochs_1/beta_0.01/pruning_threshold_1.0/film_max_t_0.7/film_min_t_0.4/semantic_spreading_0/snr_adaptive_beta_0/semantic_power_1/semantic_power_alpha_%s/SSFLv6/snr_10/compress_4096/channel_type_rayleigh/seed_%s.npz" \
    "${HOST_RESULT_ROOT}" "${alpha}" "${seed}"
}

run_one() {
  local alpha="$1"
  local seed="$2"
  local label="rayleigh_semantic_power_alpha_${alpha}_seed_${seed}"
  local expected_npz
  expected_npz="$(npz_path "${alpha}" "${seed}")"

  if [ -f "${expected_npz}" ]; then
    log "SKIP ${label} (existing artifact: ${expected_npz})"
    return 0
  fi

  log "START ${label}"
  (
    cd "${REPO_ROOT}" &&
    docker compose run --rm sfl-semantic bash -lc "run-exp \
      --dataset cifar10 --partition_type class --algorithm SSFLv6 --model_type resnetv2 \
      --channel_type rayleigh --n_clients 8 --n_client_data 3000 --batch_size 100 \
      --n_epochs 1 --n_rounds 200 --compressed_dim 4096 --beta 0.01 \
      --pruning_threshold 1.0 --film_max_t 0.7 --film_min_t 0.4 \
      --semantic_spreading_enable 0 --snr_adaptive_beta_enable 0 \
      --semantic_power_enable 1 --semantic_power_alpha ${alpha} --mpi_trace_enable 0 \
      --result_path ${RESULT_ROOT} --seed ${seed}"
  )
  log "END ${label}"
}

touch "${LOG_FILE}"
log "rayleigh semantic power sweep nclients=8 시작"
for alpha in 0.5 1.0 2.0 4.0; do
  for seed in 1 2; do
    run_one "${alpha}" "${seed}"
  done
done
log "rayleigh semantic power sweep nclients=8 완료"
