#!/usr/bin/env bash
set -uo pipefail

REPO_ROOT="/home/sunmin/SFL_Semantic"
DOC_ROOT="${REPO_ROOT}/docs/experiments/2026-04-15/2026-04-15_12-20_v01_channel-specific-ablation-plan"
AWGN_LOG_FILE="${DOC_ROOT}/RUNLOG_AWGN.md"
RAYLEIGH_LOG_FILE="${DOC_ROOT}/RUNLOG_RAYLEIGH.md"
SUDO_PASSWORD="${SUDO_PASSWORD:-a}"

RESULT_ROOT="/workspace/tmp/2026-04-15/2026-04-15-cifar10-channel-specific-ablation"
HOST_RESULT_ROOT="${REPO_ROOT}/tmp/2026-04-15/2026-04-15-cifar10-channel-specific-ablation"

mkdir -p "${DOC_ROOT}"

log_to() {
  local logfile="$1"
  shift
  local ts
  ts="$(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf -- "- [%s] %s\n" "${ts}" "$1" | tee -a "${logfile}"
}

wait_for_artifact() {
  local path="$1"
  local tries="${2:-20}"
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
  local logfile="$1"
  shift
  local label="$1"
  shift
  log_to "${logfile}" "START ${label}"
  if (
    cd "${REPO_ROOT}" &&
    printf '%s\n' "${SUDO_PASSWORD}" | sudo -S docker compose run --rm -T sfl-semantic bash -lc "run-exp $*"
  ); then
    log_to "${logfile}" "END ${label}"
    return 0
  fi
  return 1
}

npz_path() {
  local algorithm="$1"
  local channel="$2"
  local beta="$3"
  local film_max="$4"
  local film_min="$5"
  local seed="$6"

  printf "%s/cifar10/n_clients_8/n_client_data_3000/batch_size_100/data_partition_type_class/model_type_resnetv2/major_percent_0.8/n_epochs_1/beta_%s/pruning_threshold_1.0/film_max_t_%s/film_min_t_%s/semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0/latent_mixing_0/latent_mixing_strength_0.0/latent_mixing_groups_8/encoder_downsample_0/encoder_downsample_mode_stride2_proj/encoder_downsample_proj_dim_4096/semidense_0/semidense_group_size_16/semidense_group_topk_4/support_floor_0/support_floor_min_active_256/support_floor_snr_db_0.0/importance_repetition_0/importance_repetition_topk_32/base_refinement_0/base_refinement_variable_0/base_refinement_semantic_aware_0/base_support_k_128/refinement_support_k_128/refinement_semantic_weight_0.5/refinement_channel_weight_0.5/csi_source_mask_0/server_feature_impute_0/%s/snr_10/compress_4096/channel_type_%s/seed_%s.npz" \
    "${HOST_RESULT_ROOT}" "${beta}" "${film_max}" "${film_min}" "${algorithm}" "${channel}" "${seed}"
}

run_one() {
  local logfile="$1"
  local algorithm="$2"
  local channel="$3"
  local beta="$4"
  local film_max="$5"
  local film_min="$6"
  local seed="$7"
  local label expected_npz

  label="cifar10_${channel}_${algorithm}_seed_${seed}"
  expected_npz="$(npz_path "${algorithm}" "${channel}" "${beta}" "${film_max}" "${film_min}" "${seed}")"

  if wait_for_artifact "${expected_npz}" 2 1; then
    log_to "${logfile}" "SKIP ${label} (existing artifact: ${expected_npz})"
    return 0
  fi

  if run_exp \
    "${logfile}" \
    "${label}" \
    --dataset cifar10 --partition_type class --algorithm "${algorithm}" --model_type resnetv2 \
    --channel_type "${channel}" --n_clients 8 --n_client_data 3000 --batch_size 100 \
    --n_epochs 1 --n_rounds 200 --compressed_dim 4096 --beta "${beta}" \
    --pruning_threshold 1.0 --film_max_t "${film_max}" --film_min_t "${film_min}" \
    --semantic_spreading_enable 0 --snr_adaptive_beta_enable 0 --semantic_power_enable 0 \
    --latent_mixing_enable 0 --encoder_downsample_enable 0 --semidense_enable 0 \
    --support_floor_enable 0 --importance_repetition_enable 0 --base_refinement_enable 0 \
    --csi_source_mask_enable 0 --server_feature_impute_enable 0 --mpi_trace_enable 0 \
    --result_path "${RESULT_ROOT}" --seed "${seed}"; then
    return 0
  fi

  if wait_for_artifact "${expected_npz}" 20 1; then
    log_to "${logfile}" "END ${label} (artifact exists despite non-zero exit: ${expected_npz})"
    return 0
  fi

  log_to "${logfile}" "FAIL ${label} (missing artifact after non-zero exit)"
  return 1
}

main() {
  touch "${AWGN_LOG_FILE}" "${RAYLEIGH_LOG_FILE}"
  log_to "${AWGN_LOG_FILE}" "channel-specific ablation AWGN 시작"
  for algorithm in SSFLv6_w_o_vib SSFLv6_w_o_film; do
    for seed in 1 2 3 4; do
      run_one "${AWGN_LOG_FILE}" "${algorithm}" "awgn" "0.05" "0.7" "0.2" "${seed}" || true
    done
  done
  log_to "${AWGN_LOG_FILE}" "channel-specific ablation AWGN 완료"

  log_to "${RAYLEIGH_LOG_FILE}" "channel-specific ablation Rayleigh 시작"
  for algorithm in SSFLv6_w_o_vib SSFLv6_w_o_film; do
    for seed in 1 2 3 4; do
      run_one "${RAYLEIGH_LOG_FILE}" "${algorithm}" "rayleigh" "0.1" "0.7" "0.4" "${seed}" || true
    done
  done
  log_to "${RAYLEIGH_LOG_FILE}" "channel-specific ablation Rayleigh 완료"
}

main "$@"
