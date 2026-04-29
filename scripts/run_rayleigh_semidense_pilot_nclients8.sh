#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/home/sunmin/SFL_Semantic"
RESULT_ROOT="/workspace/tmp/2026-04-10-rayleigh-semidense-pilot"
HOST_RESULT_ROOT="${REPO_ROOT}/tmp/2026-04-10-rayleigh-semidense-pilot"
DOC_ROOT="${REPO_ROOT}/docs/experiments/2026-04-10_01-28_v01_rayleigh-semidense-pilot"
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
  local group_size="$1"
  local group_topk="$2"
  local seed="$3"

  printf "%s/cifar10/n_clients_8/n_client_data_3000/batch_size_100/data_partition_type_class/model_type_resnetv2/major_percent_0.8/n_epochs_1/beta_0.01/pruning_threshold_1.0/film_max_t_0.7/film_min_t_0.4/semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0/latent_mixing_0/latent_mixing_strength_0.0/latent_mixing_groups_8/semidense_1/semidense_group_size_%s/semidense_group_topk_%s/SSFLv6/snr_10/compress_4096/channel_type_rayleigh/seed_%s.npz" \
    "${HOST_RESULT_ROOT}" "${group_size}" "${group_topk}" "${seed}"
}

run_one() {
  local group_size="$1"
  local group_topk="$2"
  local seed="$3"
  local label="rayleigh_semidense_g${group_size}_k${group_topk}_seed_${seed}"
  local expected_npz
  expected_npz="$(npz_path "${group_size}" "${group_topk}" "${seed}")"

  if [ -f "${expected_npz}" ]; then
    log "SKIP ${label} (existing artifact: ${expected_npz})"
    return 0
  fi

  run_exp \
    "${label}" \
    --dataset cifar10 --partition_type class --algorithm SSFLv6 --model_type resnetv2 \
    --channel_type rayleigh --n_clients 8 --n_client_data 3000 --batch_size 100 \
    --n_epochs 1 --n_rounds 200 --compressed_dim 4096 --beta 0.01 \
    --pruning_threshold 1.0 --film_max_t 0.7 --film_min_t 0.4 \
    --semantic_spreading_enable 0 --snr_adaptive_beta_enable 0 \
    --semantic_power_enable 0 --semantic_power_alpha 2.0 \
    --latent_mixing_enable 0 --latent_mixing_strength 0.0 --latent_mixing_groups 8 \
    --semidense_enable 1 --semidense_group_size "${group_size}" --semidense_group_topk "${group_topk}" \
    --mpi_trace_enable 0 --result_path "${RESULT_ROOT}" --seed "${seed}"
}

main() {
  touch "${LOG_FILE}"
  log "rayleigh semidense pilot nclients=8 시작"

  for cfg in "16 4" "16 8" "32 8"; do
    set -- ${cfg}
    group_size="$1"
    group_topk="$2"
    for seed in 1 2; do
      run_one "${group_size}" "${group_topk}" "${seed}"
    done
  done

  log "rayleigh semidense pilot nclients=8 완료"
}

main "$@"
