#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/home/sunmin/SFL_Semantic"
RESULT_ROOT="/workspace/tmp/2026-04-12/2026-04-12-table1-rerun"
HOST_RESULT_ROOT="${REPO_ROOT}/tmp/2026-04-12/2026-04-12-table1-rerun"
DOC_ROOT="${REPO_ROOT}/docs/experiments/2026-04-12/2026-04-12_00-35_v01_table1-rerun-plan"
LOG_FILE="${DOC_ROOT}/RUNLOG.md"
BLOCK_SELECTOR="${BLOCK_SELECTOR:-ALL}"

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
  local beta="$2"
  local threshold="$3"
  local fmax="$4"
  local fmin="$5"
  local seed="$6"
  local beta_dir
  local threshold_dir
  local fmax_dir
  local fmin_dir

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
  if [ -f "${expected_npz}" ]; then
    log "SKIP ${label} (existing artifact: ${expected_npz})"
    return 0
  fi

  run_exp \
    "${label}" \
    --dataset cifar10 --partition_type class --algorithm SSFLv6 --model_type resnetv2 \
    --channel_type "${channel}" --n_clients 8 --n_client_data 3000 --batch_size 100 \
    --n_epochs 1 --n_rounds 200 --compressed_dim 4096 --beta "${beta}" \
    --pruning_threshold "${threshold}" --film_max_t "${fmax}" --film_min_t "${fmin}" \
    --semantic_spreading_enable 0 --snr_adaptive_beta_enable 0 --semantic_power_enable 0 \
    --latent_mixing_enable 0 --encoder_downsample_enable 0 --semidense_enable 0 \
    --support_floor_enable 0 --importance_repetition_enable 0 --base_refinement_enable 0 \
    --csi_source_mask_enable 0 --server_feature_impute_enable 0 --mpi_trace_enable 0 \
    --result_path "${RESULT_ROOT}" --seed "${seed}"
}

main() {
  touch "${LOG_FILE}"
  log "table1 rerun exploratory seed1,2 시작 (BLOCK_SELECTOR=${BLOCK_SELECTOR})"

  local seeds=(1 2)
  local channels=(awgn rayleigh)
  local betas=(0.100 0.050 0.010 0.005 0.001)
  local thresholds=(1.5 1.0 0.5)
  local film_pairs=("0.7 0.2" "0.7 0.3" "0.7 0.4" "0.8 0.2" "0.8 0.3" "0.8 0.4" "0.9 0.2" "0.9 0.3" "0.9 0.4")

  if [ "${BLOCK_SELECTOR}" = "ALL" ] || [ "${BLOCK_SELECTOR}" = "A" ]; then
    for channel in "${channels[@]}"; do
      for seed in "${seeds[@]}"; do
        for beta in "${betas[@]}"; do
          for threshold in "${thresholds[@]}"; do
            run_one \
              "table1_blockA_${channel}_beta${beta}_tau${threshold}_seed${seed}" \
              "${channel}" "${beta}" "${threshold}" "0.7" "0.4" "${seed}"
          done
        done
      done
    done
  fi

  if [ "${BLOCK_SELECTOR}" = "ALL" ] || [ "${BLOCK_SELECTOR}" = "B" ]; then
    for channel in "${channels[@]}"; do
      for seed in "${seeds[@]}"; do
        for pair in "${film_pairs[@]}"; do
          # shellcheck disable=SC2086
          set -- ${pair}
          local fmax="$1"
          local fmin="$2"
          run_one \
            "table1_blockB_${channel}_fmax${fmax}_fmin${fmin}_seed${seed}" \
            "${channel}" "0.010" "1.0" "${fmax}" "${fmin}" "${seed}"
        done
      done
    done
  fi

  log "table1 rerun exploratory seed1,2 완료"
}

main "$@"
