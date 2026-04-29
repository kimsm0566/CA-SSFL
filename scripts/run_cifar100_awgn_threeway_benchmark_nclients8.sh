#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/home/sunmin/SFL_Semantic"
RESULT_ROOT="/workspace/tmp/2026-04-11/2026-04-11-cifar100-awgn-threeway-benchmark-nclients8"
HOST_RESULT_ROOT="${REPO_ROOT}/tmp/2026-04-11/2026-04-11-cifar100-awgn-threeway-benchmark-nclients8"
DOC_ROOT="${REPO_ROOT}/docs/experiments/2026-04-11/2026-04-11_22-20_v01_cifar100-cross-benchmark-plan"
LOG_FILE="${DOC_ROOT}/RUNLOG_AWGN.md"

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
  printf "%s/cifar100/n_clients_8/n_client_data_3000/batch_size_100/data_partition_type_class/model_type_resnetv2/major_percent_0.8/n_epochs_1/beta_0.01/pruning_threshold_1.0/film_max_t_0.7/film_min_t_0.4/semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0/latent_mixing_0/latent_mixing_strength_0.0/latent_mixing_groups_8/encoder_downsample_0/encoder_downsample_mode_stride2_proj/encoder_downsample_proj_dim_4096/semidense_0/semidense_group_size_16/semidense_group_topk_4/support_floor_0/support_floor_min_active_256/support_floor_snr_db_0.0/importance_repetition_0/importance_repetition_topk_32/base_refinement_0/base_refinement_variable_0/base_refinement_semantic_aware_0/base_support_k_128/refinement_support_k_128/refinement_semantic_weight_0.7/refinement_channel_weight_0.3/csi_source_mask_0/server_feature_impute_0/%s/snr_10/compress_%s/channel_type_awgn/seed_%s.npz" \
    "${HOST_RESULT_ROOT}" "${algorithm}" "${compressed_dim}" "${seed}"
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

  run_exp \
    "${label}" \
    --dataset cifar100 --partition_type class --algorithm "${algorithm}" --model_type resnetv2 \
    --channel_type awgn --n_clients 8 --n_client_data 3000 --batch_size 100 \
    --n_epochs 1 --n_rounds 200 --compressed_dim "${compressed_dim}" --beta 0.01 \
    --pruning_threshold 1.0 --film_max_t 0.7 --film_min_t 0.4 \
    --semantic_spreading_enable 0 --snr_adaptive_beta_enable 0 --semantic_power_enable 0 \
    --latent_mixing_enable 0 --encoder_downsample_enable 0 --semidense_enable 0 \
    --support_floor_enable 0 --importance_repetition_enable 0 --base_refinement_enable 0 \
    --csi_source_mask_enable 0 --server_feature_impute_enable 0 --mpi_trace_enable 0 \
    --result_path "${RESULT_ROOT}" --seed "${seed}"
}

main() {
  touch "${LOG_FILE}"
  log "cifar100 awgn three-way benchmark 시작"

  for seed in 1 2 3 4; do
    run_one "cifar100_awgn_sfl_seed_${seed}" "SFL" "4096" "${seed}"
  done

  for seed in 1 2 3 4; do
    run_one "cifar100_awgn_scusfl_seed_${seed}" "SC-USFL" "1352" "${seed}"
  done

  for seed in 1 2 3 4; do
    run_one "cifar100_awgn_ca_ssfl_seed_${seed}" "SSFLv6" "4096" "${seed}"
  done

  log "cifar100 awgn three-way benchmark 완료"
}

main "$@"
