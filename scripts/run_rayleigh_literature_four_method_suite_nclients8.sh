#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/home/sunmin/SFL_Semantic"
RESULT_ROOT="/workspace/tmp/2026-04-11/2026-04-11-rayleigh-literature-four-method-suite"
SMOKE_RESULT_ROOT="/workspace/tmp/2026-04-11/2026-04-11-rayleigh-literature-four-method-suite-smoke"
HOST_RESULT_ROOT="${REPO_ROOT}/tmp/2026-04-11/2026-04-11-rayleigh-literature-four-method-suite"
DOC_ROOT="${REPO_ROOT}/docs/experiments/2026-04-11/2026-04-11_07-10_v01_rayleigh-literature-four-method-suite"
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

run_smoke() {
  local label="$1"
  shift
  run_exp "${label}" \
    --dataset cifar10 --partition_type class --algorithm SSFLv6 --model_type resnetv2 \
    --channel_type rayleigh --n_clients 8 --n_client_data 3000 --batch_size 100 \
    --n_epochs 1 --n_rounds 1 --compressed_dim 4096 --beta 0.01 \
    --pruning_threshold 1.0 --film_max_t 0.7 --film_min_t 0.4 \
    --semantic_spreading_enable 0 --snr_adaptive_beta_enable 0 \
    --semantic_power_enable 0 --semantic_power_alpha 2.0 \
    --latent_mixing_enable 0 --latent_mixing_strength 0.0 --latent_mixing_groups 8 \
    --encoder_downsample_enable 0 --encoder_downsample_mode stride2_proj --encoder_downsample_proj_dim 4096 \
    --semidense_enable 0 --semidense_group_size 16 --semidense_group_topk 4 \
    --support_floor_enable 0 --support_floor_min_active 256 --support_floor_snr_db 0.0 \
    --importance_repetition_enable 0 --importance_repetition_topk 32 \
    --base_refinement_enable 0 --base_support_k 128 --refinement_support_k 128 \
    --csi_source_mask_enable 0 --server_feature_impute_enable 0 \
    --mpi_trace_enable 0 --result_path "${SMOKE_RESULT_ROOT}" --seed 1 \
    "$@"
}

npz_path() {
  local slug="$1"
  local seed="$2"
  printf "%s/cifar10/n_clients_8/n_client_data_3000/batch_size_100/data_partition_type_class/model_type_resnetv2/major_percent_0.8/n_epochs_1/beta_0.01/pruning_threshold_1.0/film_max_t_0.7/film_min_t_0.4/%s/SSFLv6/snr_10/compress_4096/channel_type_rayleigh/seed_%s.npz" \
    "${HOST_RESULT_ROOT}" "${slug}" "${seed}"
}

run_one() {
  local label="$1"
  local slug="$2"
  local seed="$3"
  shift 3

  local expected_npz
  expected_npz="$(npz_path "${slug}" "${seed}")"
  if [ -f "${expected_npz}" ]; then
    log "SKIP ${label} (existing artifact: ${expected_npz})"
    return 0
  fi

  run_exp "${label}" \
    --dataset cifar10 --partition_type class --algorithm SSFLv6 --model_type resnetv2 \
    --channel_type rayleigh --n_clients 8 --n_client_data 3000 --batch_size 100 \
    --n_epochs 1 --n_rounds 200 --compressed_dim 4096 --beta 0.01 \
    --pruning_threshold 1.0 --film_max_t 0.7 --film_min_t 0.4 \
    --semantic_spreading_enable 0 --snr_adaptive_beta_enable 0 \
    --semantic_power_enable 0 --semantic_power_alpha 2.0 \
    --latent_mixing_enable 0 --latent_mixing_strength 0.0 --latent_mixing_groups 8 \
    --encoder_downsample_enable 0 --encoder_downsample_mode stride2_proj --encoder_downsample_proj_dim 4096 \
    --semidense_enable 0 --semidense_group_size 16 --semidense_group_topk 4 \
    --support_floor_enable 0 --support_floor_min_active 256 --support_floor_snr_db 0.0 \
    --importance_repetition_enable 0 --importance_repetition_topk 32 \
    --base_refinement_enable 0 --base_support_k 128 --refinement_support_k 128 \
    --csi_source_mask_enable 0 --server_feature_impute_enable 0 \
    --mpi_trace_enable 0 --result_path "${RESULT_ROOT}" --seed "${seed}" \
    "$@"
}

main() {
  touch "${LOG_FILE}"
  log "rayleigh literature four-method suite nclients=8 시작"

  run_smoke "smoke_method1_repetition" --importance_repetition_enable 1 --importance_repetition_topk 32
  run_smoke "smoke_method2_base_refinement" --base_refinement_enable 1 --base_support_k 128 --refinement_support_k 128
  run_smoke "smoke_method3_csi_source_mask" --csi_source_mask_enable 1
  run_smoke "smoke_method4_server_impute" --server_feature_impute_enable 1

  for seed in 1 2; do
    run_one \
      "method1_repetition_seed_${seed}" \
      "semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0/latent_mixing_0/latent_mixing_strength_0.0/latent_mixing_groups_8/encoder_downsample_0/encoder_downsample_mode_stride2_proj/encoder_downsample_proj_dim_4096/semidense_0/semidense_group_size_16/semidense_group_topk_4/support_floor_0/support_floor_min_active_256/support_floor_snr_db_0.0/importance_repetition_1/importance_repetition_topk_32/base_refinement_0/base_support_k_128/refinement_support_k_128/csi_source_mask_0/server_feature_impute_0" \
      "${seed}" \
      --importance_repetition_enable 1 --importance_repetition_topk 32

    run_one \
      "method2_base_refinement_seed_${seed}" \
      "semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0/latent_mixing_0/latent_mixing_strength_0.0/latent_mixing_groups_8/encoder_downsample_0/encoder_downsample_mode_stride2_proj/encoder_downsample_proj_dim_4096/semidense_0/semidense_group_size_16/semidense_group_topk_4/support_floor_0/support_floor_min_active_256/support_floor_snr_db_0.0/importance_repetition_0/importance_repetition_topk_32/base_refinement_1/base_support_k_128/refinement_support_k_128/csi_source_mask_0/server_feature_impute_0" \
      "${seed}" \
      --base_refinement_enable 1 --base_support_k 128 --refinement_support_k 128

    run_one \
      "method3_csi_source_mask_seed_${seed}" \
      "semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0/latent_mixing_0/latent_mixing_strength_0.0/latent_mixing_groups_8/encoder_downsample_0/encoder_downsample_mode_stride2_proj/encoder_downsample_proj_dim_4096/semidense_0/semidense_group_size_16/semidense_group_topk_4/support_floor_0/support_floor_min_active_256/support_floor_snr_db_0.0/importance_repetition_0/importance_repetition_topk_32/base_refinement_0/base_support_k_128/refinement_support_k_128/csi_source_mask_1/server_feature_impute_0" \
      "${seed}" \
      --csi_source_mask_enable 1

    run_one \
      "method4_server_impute_seed_${seed}" \
      "semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0/latent_mixing_0/latent_mixing_strength_0.0/latent_mixing_groups_8/encoder_downsample_0/encoder_downsample_mode_stride2_proj/encoder_downsample_proj_dim_4096/semidense_0/semidense_group_size_16/semidense_group_topk_4/support_floor_0/support_floor_min_active_256/support_floor_snr_db_0.0/importance_repetition_0/importance_repetition_topk_32/base_refinement_0/base_support_k_128/refinement_support_k_128/csi_source_mask_0/server_feature_impute_1" \
      "${seed}" \
      --server_feature_impute_enable 1
  done

  log "rayleigh literature four-method suite nclients=8 완료"
}

main "$@"
