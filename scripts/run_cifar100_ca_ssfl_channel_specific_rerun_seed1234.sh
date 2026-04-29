#!/usr/bin/env bash
set -uo pipefail

REPO_ROOT="/home/sunmin/SFL_Semantic"
DOC_ROOT="${REPO_ROOT}/docs/experiments/2026-04-15/2026-04-15_14-35_v01_cifar100-ca-ssfl-channel-specific-rerun"
LOG_FILE="${DOC_ROOT}/RUNLOG.md"
SUDO_PASSWORD="${SUDO_PASSWORD:-a}"

AWGN_RESULT_ROOT="/workspace/tmp/2026-04-15/2026-04-15-cifar100-awgn-ca-ssfl-channel-specific-rerun"
AWGN_HOST_RESULT_ROOT="${REPO_ROOT}/tmp/2026-04-15/2026-04-15-cifar100-awgn-ca-ssfl-channel-specific-rerun"
RAY_RESULT_ROOT="/workspace/tmp/2026-04-15/2026-04-15-cifar100-rayleigh-ca-ssfl-channel-specific-rerun"
RAY_HOST_RESULT_ROOT="${REPO_ROOT}/tmp/2026-04-15/2026-04-15-cifar100-rayleigh-ca-ssfl-channel-specific-rerun"

mkdir -p "${DOC_ROOT}"

log() {
  local ts
  ts="$(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf -- "- [%s] %s\n" "${ts}" "$1" | tee -a "${LOG_FILE}"
}

wait_for_artifact() {
  local path="$1"
  local tries="${2:-15}"
  local delay="${3:-1}"
  local i
  for ((i=0; i<tries; i++)); do
    if [ -f "${path}" ]; then
      return 0
    fi
    sleep "${delay}"
  done
  return 1
}

run_exp() {
  local label="$1"
  shift
  log "START ${label}"
  if (
    cd "${REPO_ROOT}" &&
    printf '%s\n' "${SUDO_PASSWORD}" | sudo -S docker compose run --rm -T sfl-semantic bash -lc "run-exp $*"
  ); then
    log "END ${label}"
    return 0
  fi
  return 1
}

npz_path() {
  local channel="$1"
  local beta="$2"
  local film_max="$3"
  local film_min="$4"
  local seed="$5"
  local host_root

  if [ "${channel}" = "awgn" ]; then
    host_root="${AWGN_HOST_RESULT_ROOT}"
  else
    host_root="${RAY_HOST_RESULT_ROOT}"
  fi

  printf "%s/cifar100/n_clients_8/n_client_data_3000/batch_size_100/data_partition_type_class/model_type_resnetv2/major_percent_0.8/n_epochs_1/beta_%s/pruning_threshold_1.0/film_max_t_%s/film_min_t_%s/semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0/latent_mixing_0/latent_mixing_strength_0.0/latent_mixing_groups_8/encoder_downsample_0/encoder_downsample_mode_stride2_proj/encoder_downsample_proj_dim_4096/semidense_0/semidense_group_size_16/semidense_group_topk_4/support_floor_0/support_floor_min_active_256/support_floor_snr_db_0.0/importance_repetition_0/importance_repetition_topk_32/base_refinement_0/base_refinement_variable_0/base_refinement_semantic_aware_0/base_support_k_128/refinement_support_k_128/refinement_semantic_weight_0.5/refinement_channel_weight_0.5/csi_source_mask_0/server_feature_impute_0/SSFLv6/snr_10/compress_4096/channel_type_%s/seed_%s.npz" \
    "${host_root}" "${beta}" "${film_max}" "${film_min}" "${channel}" "${seed}"
}

run_one() {
  local channel="$1"
  local beta="$2"
  local film_max="$3"
  local film_min="$4"
  local seed="$5"
  local result_root host_result_root label expected_npz

  if [ "${channel}" = "awgn" ]; then
    result_root="${AWGN_RESULT_ROOT}"
    host_result_root="${AWGN_HOST_RESULT_ROOT}"
  else
    result_root="${RAY_RESULT_ROOT}"
    host_result_root="${RAY_HOST_RESULT_ROOT}"
  fi

  label="cifar100_${channel}_ca_ssfl_seed_${seed}"
  expected_npz="$(npz_path "${channel}" "${beta}" "${film_max}" "${film_min}" "${seed}")"

  if wait_for_artifact "${expected_npz}" 2 1; then
    log "SKIP ${label} (existing artifact: ${expected_npz})"
    return 0
  fi

  if run_exp \
    "${label}" \
    --dataset cifar100 --partition_type class --algorithm SSFLv6 --model_type resnetv2 \
    --channel_type "${channel}" --n_clients 8 --n_client_data 3000 --batch_size 100 \
    --n_epochs 1 --n_rounds 200 --compressed_dim 4096 --beta "${beta}" \
    --pruning_threshold 1.0 --film_max_t "${film_max}" --film_min_t "${film_min}" \
    --semantic_spreading_enable 0 --snr_adaptive_beta_enable 0 --semantic_power_enable 0 \
    --latent_mixing_enable 0 --encoder_downsample_enable 0 --semidense_enable 0 \
    --support_floor_enable 0 --importance_repetition_enable 0 --base_refinement_enable 0 \
    --csi_source_mask_enable 0 --server_feature_impute_enable 0 --mpi_trace_enable 0 \
    --result_path "${result_root}" --seed "${seed}"; then
    return 0
  fi

  if wait_for_artifact "${expected_npz}" 20 1; then
    log "END ${label} (artifact exists despite non-zero exit: ${expected_npz})"
    return 0
  fi

  log "FAIL ${label} (missing artifact after non-zero exit)"
  return 1
}

main() {
  touch "${LOG_FILE}"
  log "cifar100 CA-SSFL channel-specific rerun 시작"

  for seed in 1 2 3 4; do
    run_one "awgn" "0.05" "0.7" "0.2" "${seed}" || true
  done

  for seed in 1 2 3 4; do
    run_one "rayleigh" "0.1" "0.7" "0.4" "${seed}" || true
  done

  log "cifar100 CA-SSFL channel-specific rerun 완료"
}

main "$@"
