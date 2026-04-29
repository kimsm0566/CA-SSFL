#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/home/sunmin/SFL_Semantic"
RESULT_ROOT="/workspace/tmp/2026-04-09-awgn-threeway-benchmark-nclients8"
HOST_RESULT_ROOT="${REPO_ROOT}/tmp/2026-04-09-awgn-threeway-benchmark-nclients8"
DOC_ROOT="${REPO_ROOT}/docs/experiments/2026-04-09_18-45_v01_awgn-threeway-benchmark-nclients8"
LOG_FILE="${DOC_ROOT}/RUNLOG.md"

mkdir -p "${DOC_ROOT}"

log() {
  local ts
  ts="$(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf -- "- [%s] %s\n" "${ts}" "$1" | tee -a "${LOG_FILE}"
}

run_exp() {
  local label="$1"
  shift
  log "START ${label}"
  (
    cd "${REPO_ROOT}" &&
    docker compose run --rm sfl-semantic bash -lc "run-exp $*"
  )
  log "END ${label}"
}

npz_path() {
  local algorithm="$1"
  local seed="$2"
  local compressed_dim="$3"

  printf "%s/cifar10/n_clients_8/n_client_data_3000/batch_size_100/data_partition_type_class/model_type_resnetv2/major_percent_0.8/n_epochs_1/beta_0.01/pruning_threshold_1.0/film_max_t_0.7/film_min_t_0.4" \
    "${HOST_RESULT_ROOT}"

  if [ "${algorithm}" = "SSFLv6" ]; then
    printf "/semantic_spreading_1/snr_adaptive_beta_1/semantic_power_0/semantic_power_alpha_2.0"
  fi

  printf "/%s/snr_10/compress_%s/channel_type_awgn/seed_%s.npz" "${algorithm}" "${compressed_dim}" "${seed}"
}

run_one() {
  local label="$1"
  local algorithm="$2"
  local compressed_dim="$3"
  local seed="$4"
  local expected_npz

  expected_npz="$(npz_path "${algorithm}" "${seed}" "${compressed_dim}")"
  if [ -f "${expected_npz}" ]; then
    log "SKIP ${label} (existing artifact: ${expected_npz})"
    return 0
  fi

  local extra=""
  if [ "${algorithm}" = "SSFLv6" ]; then
    extra="--semantic_spreading_enable 1 --snr_adaptive_beta_enable 1 --semantic_power_enable 0 --semantic_power_alpha 2.0 --mpi_trace_enable 0"
  fi

  run_exp \
    "${label}" \
    --dataset cifar10 --partition_type class --algorithm "${algorithm}" --model_type resnetv2 \
    --channel_type awgn --n_clients 8 --n_client_data 3000 --batch_size 100 \
    --n_epochs 1 --n_rounds 200 --compressed_dim "${compressed_dim}" --beta 0.01 \
    --pruning_threshold 1.0 --film_max_t 0.7 --film_min_t 0.4 \
    --result_path "${RESULT_ROOT}" --seed "${seed}" ${extra}
}

main() {
  touch "${LOG_FILE}"
  log "awgn three-way benchmark 시작"

  for seed in 1 2 3 4; do
    run_one "awgn_sfl_seed_${seed}" "SFL" "4096" "${seed}"
  done

  for seed in 1 2 3 4; do
    run_one "awgn_scusfl_seed_${seed}" "SC-USFL" "1352" "${seed}"
  done

  for seed in 1 2 3 4; do
    run_one "awgn_ssflv6_candidate_seed_${seed}" "SSFLv6" "4096" "${seed}"
  done

  log "awgn three-way benchmark 완료"
}

main "$@"
