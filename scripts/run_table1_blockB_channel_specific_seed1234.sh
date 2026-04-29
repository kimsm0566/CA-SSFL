#!/usr/bin/env bash
set -uo pipefail

REPO_ROOT="/home/sunmin/SFL_Semantic"
RESULT_ROOT="/workspace/tmp/2026-04-14/2026-04-14-table1-blockB-channel-specific-rerun"
HOST_RESULT_ROOT="${REPO_ROOT}/tmp/2026-04-14/2026-04-14-table1-blockB-channel-specific-rerun"
DOC_ROOT="${REPO_ROOT}/docs/experiments/2026-04-14/2026-04-14_23-32_v01_table1-blockB-channel-specific-rerun"
LOG_FILE="${DOC_ROOT}/RUNLOG.md"
LAUNCHER_LOG="${DOC_ROOT}/launcher.log"
SUDO_PASSWORD="${SUDO_PASSWORD:-a}"

mkdir -p "${DOC_ROOT}"
if [ ! -d "${HOST_RESULT_ROOT}" ]; then
  printf '%s\n' "${SUDO_PASSWORD}" | sudo -S mkdir -p "${HOST_RESULT_ROOT}"
  printf '%s\n' "${SUDO_PASSWORD}" | sudo -S chown -R sunmin:sunmin "${HOST_RESULT_ROOT}"
fi

log() {
  local ts
  ts="$(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf -- "- [%s] %s\n" "${ts}" "$1" | tee -a "${LOG_FILE}"
}

canon_num() {
  local v="$1"
  python3 - "$v" <<'PY'
import sys
v = float(sys.argv[1])
print(f"{v:g}")
PY
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
    printf '%s\n' "${SUDO_PASSWORD}" | sudo -S docker compose run --rm sfl-semantic bash -lc "run-exp $*"
  ) >>"${LAUNCHER_LOG}" 2>&1; then
    log "END ${label}"
    return 0
  fi
  return 1
}

npz_path() {
  local channel="$1"
  local beta="$2"
  local threshold="$3"
  local fmax="$4"
  local fmin="$5"
  local seed="$6"
  local beta_dir threshold_dir fmax_dir fmin_dir
  beta_dir="$(canon_num "${beta}")"
  threshold_dir="$(canon_num "${threshold}")"
  fmax_dir="$(canon_num "${fmax}")"
  fmin_dir="$(canon_num "${fmin}")"

  printf "%s/cifar10/n_clients_8/n_client_data_3000/batch_size_100/data_partition_type_class/model_type_resnetv2/major_percent_0.8/n_epochs_1/beta_%s/pruning_threshold_%s/film_max_t_%s/film_min_t_%s/semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0/latent_mixing_0/latent_mixing_strength_0.0/latent_mixing_groups_8/encoder_downsample_0/encoder_downsample_mode_stride2_proj/encoder_downsample_proj_dim_4096/semidense_0/semidense_group_size_16/semidense_group_topk_4/support_floor_0/support_floor_min_active_256/support_floor_snr_db_0.0/importance_repetition_0/importance_repetition_topk_32/base_refinement_0/base_refinement_variable_0/base_refinement_semantic_aware_0/base_support_k_128/refinement_support_k_128/refinement_semantic_weight_0.5/refinement_channel_weight_0.5/csi_source_mask_0/server_feature_impute_0/SSFLv6/snr_10/compress_4096/channel_type_%s/seed_%s.npz" \
    "${HOST_RESULT_ROOT}" "${beta_dir}" "${threshold_dir}" "${fmax_dir}" "${fmin_dir}" "${channel}" "${seed}"
}

run_one() {
  local label="$1"
  local channel="$2"
  local beta="$3"
  local threshold="$4"
  local fmax="$5"
  local fmin="$6"
  local seed="$7"
  local expected_npz

  expected_npz="$(npz_path "${channel}" "${beta}" "${threshold}" "${fmax}" "${fmin}" "${seed}")"
  if wait_for_artifact "${expected_npz}" 2 1; then
    log "SKIP ${label} (existing artifact: ${expected_npz})"
    return 0
  fi

  if run_exp \
    "${label}" \
    --dataset cifar10 --partition_type class --algorithm SSFLv6 --model_type resnetv2 \
    --channel_type "${channel}" --n_clients 8 --n_client_data 3000 --batch_size 100 \
    --n_epochs 1 --n_rounds 200 --compressed_dim 4096 --beta "${beta}" \
    --pruning_threshold "${threshold}" --film_max_t "${fmax}" --film_min_t "${fmin}" \
    --semantic_spreading_enable 0 --snr_adaptive_beta_enable 0 --semantic_power_enable 0 \
    --latent_mixing_enable 0 --encoder_downsample_enable 0 --semidense_enable 0 \
    --support_floor_enable 0 --importance_repetition_enable 0 --base_refinement_enable 0 \
    --csi_source_mask_enable 0 --server_feature_impute_enable 0 --mpi_trace_enable 0 \
    --result_path "${RESULT_ROOT}" --seed "${seed}"; then
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
  touch "${LOG_FILE}" "${LAUNCHER_LOG}"
  log "table1 blockB channel-specific rerun seed1,2,3,4 시작"

  local seeds=(1 2 3 4)
  local film_pairs=("0.7 0.2" "0.7 0.3" "0.7 0.4" "0.8 0.2" "0.8 0.3" "0.8 0.4" "0.9 0.2" "0.9 0.3" "0.9 0.4")

  for pair in "${film_pairs[@]}"; do
    set -- ${pair}
    local fmax="$1"
    local fmin="$2"
    for seed in "${seeds[@]}"; do
      run_one \
        "table1_blockB_awgn_beta0.05_tau1.0_fmax${fmax}_fmin${fmin}_seed${seed}" \
        "awgn" "0.05" "1.0" "${fmax}" "${fmin}" "${seed}" || true
    done
  done

  for pair in "${film_pairs[@]}"; do
    set -- ${pair}
    local fmax="$1"
    local fmin="$2"
    for seed in "${seeds[@]}"; do
      run_one \
        "table1_blockB_rayleigh_beta0.1_tau1.0_fmax${fmax}_fmin${fmin}_seed${seed}" \
        "rayleigh" "0.1" "1.0" "${fmax}" "${fmin}" "${seed}" || true
    done
  done

  log "table1 blockB channel-specific rerun seed1,2,3,4 완료"
}

main "$@"
