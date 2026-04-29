#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/home/sunmin/SFL_Semantic"
RESULT_ROOT="/workspace/tmp/2026-04-13/2026-04-13-table1-blockB-rerun"
HOST_RESULT_ROOT="${REPO_ROOT}/tmp/2026-04-13/2026-04-13-table1-blockB-rerun"
DOC_ROOT="${REPO_ROOT}/docs/experiments/2026-04-13/2026-04-13_14-18_v01_table1-blockB-rerun-plan"
LOG_FILE="${DOC_ROOT}/RUNLOG.md"

mkdir -p "${DOC_ROOT}"

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
  local channel="$1"
  local fmax="$2"
  local fmin="$3"
  local seed="$4"

  local fmax_dir
  local fmin_dir
  fmax_dir="$(canon_num "${fmax}")"
  fmin_dir="$(canon_num "${fmin}")"

  printf "%s/cifar10/n_clients_8/n_client_data_3000/batch_size_100/data_partition_type_class/model_type_resnetv2/major_percent_0.8/n_epochs_1/beta_0.01/pruning_threshold_1.0/film_max_t_%s/film_min_t_%s/semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0/latent_mixing_0/latent_mixing_strength_0.0/latent_mixing_groups_8/encoder_downsample_0/encoder_downsample_mode_stride2_proj/encoder_downsample_proj_dim_4096/semidense_0/semidense_group_size_16/semidense_group_topk_4/support_floor_0/support_floor_min_active_256/support_floor_snr_db_0.0/importance_repetition_0/importance_repetition_topk_32/base_refinement_0/base_refinement_variable_0/base_refinement_semantic_aware_0/base_support_k_128/refinement_support_k_128/refinement_semantic_weight_0.5/refinement_channel_weight_0.5/csi_source_mask_0/server_feature_impute_0/SSFLv6/snr_10/compress_4096/channel_type_%s/seed_%s.npz" \
    "${HOST_RESULT_ROOT}" "${fmax_dir}" "${fmin_dir}" "${channel}" "${seed}"
}

run_one() {
  local label="$1"
  local channel="$2"
  local fmax="$3"
  local fmin="$4"
  local seed="$5"

  local expected_npz
  expected_npz="$(npz_path "${channel}" "${fmax}" "${fmin}" "${seed}")"
  if [ -f "${expected_npz}" ]; then
    log "SKIP ${label} (existing artifact: ${expected_npz})"
    return 0
  fi

  run_exp \
    "${label}" \
    --dataset cifar10 --partition_type class --algorithm SSFLv6 --model_type resnetv2 \
    --channel_type "${channel}" --n_clients 8 --n_client_data 3000 --batch_size 100 \
    --n_epochs 1 --n_rounds 200 --compressed_dim 4096 --beta 0.010 \
    --pruning_threshold 1.0 --film_max_t "${fmax}" --film_min_t "${fmin}" \
    --semantic_spreading_enable 0 --snr_adaptive_beta_enable 0 --semantic_power_enable 0 \
    --latent_mixing_enable 0 --encoder_downsample_enable 0 --semidense_enable 0 \
    --support_floor_enable 0 --importance_repetition_enable 0 --base_refinement_enable 0 \
    --csi_source_mask_enable 0 --server_feature_impute_enable 0 --mpi_trace_enable 0 \
    --result_path "${RESULT_ROOT}" --seed "${seed}"
}

main() {
  touch "${LOG_FILE}"
  log "table1 blockB rerun seed1,2,3,4 시작"

  local seeds=(1 2 3 4)
  local channels=(awgn rayleigh)
  local film_pairs=("0.7 0.2" "0.7 0.3" "0.7 0.4" "0.8 0.2" "0.8 0.3" "0.8 0.4" "0.9 0.2" "0.9 0.3" "0.9 0.4")

  for channel in "${channels[@]}"; do
    for pair in "${film_pairs[@]}"; do
      # shellcheck disable=SC2086
      set -- ${pair}
      local fmax="$1"
      local fmin="$2"
      for seed in "${seeds[@]}"; do
        run_one \
          "table1_blockB_${channel}_fmax${fmax}_fmin${fmin}_seed${seed}" \
          "${channel}" "${fmax}" "${fmin}" "${seed}"
      done
    done
  done

  log "table1 blockB rerun seed1,2,3,4 완료"
}

main "$@"
