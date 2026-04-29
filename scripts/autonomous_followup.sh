#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/home/sunmin/SFL_Semantic"
CROSS_ROOT="/home/sunmin/SFL_Semantic/tmp/2026-04-09-cross-benchmark"
FOLLOWUP_ROOT="/workspace/tmp/2026-04-09-autonomous-followup"
DOC_ROOT="/home/sunmin/SFL_Semantic/docs/experiments/2026-04-09_16-55_v01_autonomous-followup"
LOG_FILE="${DOC_ROOT}/AUTONOMOUS_RUNLOG.md"

mkdir -p "${DOC_ROOT}"

log() {
  local ts
  ts="$(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf -- "- [%s] %s\n" "${ts}" "$1" | tee -a "${LOG_FILE}"
}

run_exp() {
  local label="$1"
  local cmd="$2"
  log "START ${label}"
  (cd "${REPO_ROOT}" && docker compose run --rm sfl-semantic bash -lc "${cmd} || true")
  log "END ${label}"
}

wait_for_cross_benchmark() {
  log "cross-benchmark 완료 대기 시작"
  while true; do
    local npz_count
    npz_count="$(find "${CROSS_ROOT}" -name 'seed_*.npz' 2>/dev/null | wc -l | tr -d ' ')"
    if [[ "${npz_count}" -ge 20 ]]; then
      log "cross-benchmark npz ${npz_count}개 확인"
      break
    fi
    sleep 300
  done
}

aggregate_rayleigh_summary() {
  (cd "${REPO_ROOT}" && docker compose run --rm sfl-semantic python - <<'PY'
import json
import numpy as np
from statistics import mean

cross_base = "/workspace/tmp/2026-04-09-cross-benchmark/cifar10/n_clients_9/n_client_data_3000/batch_size_100/data_partition_type_class/model_type_resnetv2/major_percent_0.8/n_epochs_1"
legacy_base = "/workspace/tmp/2026-04-09-rayleigh-seq-full/cifar10/n_clients_9/n_client_data_3000/batch_size_100/data_partition_type_class/model_type_resnetv2/major_percent_0.8/n_epochs_1/beta_0.01/pruning_threshold_1.0/film_max_t_0.7/film_min_t_0.4"

def load_paths(paths):
    finals, comms, low = [], [], []
    for path in paths:
        d = np.load(path, allow_pickle=True)
        finals.append(float(d["train_acc"][-1]))
        comms.append(float(d["comm"][-1]))
        snr_map = {int(s): float(a) for s, a in zip(d["test_snrs"], d["snr_accs"])}
        low.append(float(snr_map[-6]))
    return {
        "final_acc_mean": mean(finals),
        "comm_mean": mean(comms),
        "snr_m6_mean": mean(low),
        "final_accs": finals,
        "comms": comms,
        "snr_m6": low,
    }

summary = {}
summary["sc_usfl"] = load_paths([
    f"{cross_base}/beta_0.01/pruning_threshold_1.0/film_max_t_0.7/film_min_t_0.4/semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0/SC-USFL/snr_10/compress_1352/channel_type_rayleigh/seed_1.npz",
    f"{cross_base}/beta_0.01/pruning_threshold_1.0/film_max_t_0.7/film_min_t_0.4/semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0/SC-USFL/snr_10/compress_1352/channel_type_rayleigh/seed_2.npz",
    f"{cross_base}/beta_0.01/pruning_threshold_1.0/film_max_t_0.7/film_min_t_0.4/semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0/SC-USFL/snr_10/compress_1352/channel_type_rayleigh/seed_3.npz",
    f"{cross_base}/beta_0.01/pruning_threshold_1.0/film_max_t_0.7/film_min_t_0.4/semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0/SC-USFL/snr_10/compress_1352/channel_type_rayleigh/seed_4.npz",
])
summary["candidate"] = load_paths([
    f"{legacy_base}/semantic_spreading_1/snr_adaptive_beta_1/SSFLv6/snr_10/compress_4096/channel_type_rayleigh/seed_1.npz",
    f"{legacy_base}/semantic_spreading_1/snr_adaptive_beta_1/SSFLv6/snr_10/compress_4096/channel_type_rayleigh/seed_2.npz",
    f"{cross_base}/beta_0.01/pruning_threshold_1.0/film_max_t_0.7/film_min_t_0.4/semantic_spreading_1/snr_adaptive_beta_1/semantic_power_0/semantic_power_alpha_2.0/SSFLv6/snr_10/compress_4096/channel_type_rayleigh/seed_3.npz",
    f"{cross_base}/beta_0.01/pruning_threshold_1.0/film_max_t_0.7/film_min_t_0.4/semantic_spreading_1/snr_adaptive_beta_1/semantic_power_0/semantic_power_alpha_2.0/SSFLv6/snr_10/compress_4096/channel_type_rayleigh/seed_4.npz",
])
print(json.dumps(summary))
PY
)
}

run_stage_a() {
  local seeds=(1 2)
  local configs=(
    "beta_0.0125_fmax_0.75_fmin_0.45 --beta 0.0125 --film_max_t 0.75 --film_min_t 0.45"
    "beta_0.0150_fmax_0.75_fmin_0.45 --beta 0.0150 --film_max_t 0.75 --film_min_t 0.45"
    "beta_0.0125_fmax_0.80_fmin_0.50 --beta 0.0125 --film_max_t 0.80 --film_min_t 0.50"
    "beta_0.0150_fmax_0.80_fmin_0.50 --beta 0.0150 --film_max_t 0.80 --film_min_t 0.50"
  )
  for cfg in "${configs[@]}"; do
    local label="${cfg%% *}"
    local extra="${cfg#* }"
    for seed in "${seeds[@]}"; do
      run_exp \
        "stage_a_${label}_seed_${seed}" \
        "run-exp --dataset cifar10 --partition_type class --algorithm SSFLv6 --model_type resnetv2 --channel_type rayleigh --n_clients 9 --n_client_data 3000 --batch_size 100 --n_epochs 1 --n_rounds 200 --compressed_dim 4096 --pruning_threshold 1.0 --semantic_spreading_enable 1 --snr_adaptive_beta_enable 1 --semantic_power_enable 0 --semantic_power_alpha 2.0 --result_path ${FOLLOWUP_ROOT} --seed ${seed} ${extra}"
    done
  done
}

run_stage_b() {
  local seeds=(1 2)
  local configs=(
    "power_alpha_2.0 --beta 0.0125 --film_max_t 0.75 --film_min_t 0.45 --semantic_power_enable 1 --semantic_power_alpha 2.0"
    "power_alpha_3.0 --beta 0.0125 --film_max_t 0.75 --film_min_t 0.45 --semantic_power_enable 1 --semantic_power_alpha 3.0"
  )
  for cfg in "${configs[@]}"; do
    local label="${cfg%% *}"
    local extra="${cfg#* }"
    for seed in "${seeds[@]}"; do
      run_exp \
        "stage_b_${label}_seed_${seed}" \
        "run-exp --dataset cifar10 --partition_type class --algorithm SSFLv6 --model_type resnetv2 --channel_type rayleigh --n_clients 9 --n_client_data 3000 --batch_size 100 --n_epochs 1 --n_rounds 200 --compressed_dim 4096 --pruning_threshold 1.0 --semantic_spreading_enable 1 --snr_adaptive_beta_enable 1 --result_path ${FOLLOWUP_ROOT} --seed ${seed} ${extra}"
    done
  done
}

main() {
  log "autonomous follow-up supervisor 시작"
  wait_for_cross_benchmark

  local summary_json
  summary_json="$(aggregate_rayleigh_summary)"
  log "rayleigh summary: ${summary_json}"

  local decision
  decision="$(SUMMARY_JSON="${summary_json}" python3 - <<'PY'
import json
import os
s = json.loads(os.environ["SUMMARY_JSON"])
c = s["candidate"]
sc = s["sc_usfl"]
dominates = (
    c["final_acc_mean"] > sc["final_acc_mean"]
    and c["snr_m6_mean"] > sc["snr_m6_mean"]
    and c["comm_mean"] <= sc["comm_mean"]
)
print("dominate" if dominates else "followup")
PY
)"

  log "decision: ${decision}"
  if [[ "${decision}" == "dominate" ]]; then
    log "candidate가 SC-USFL를 종합적으로 이겨 후속 탐색 생략"
    exit 0
  fi

  log "Stage A 통신량 절감 sweep 시작"
  run_stage_a
  log "Stage A 완료"

  log "Stage B semantic power allocation exploratory 시작"
  run_stage_b
  log "Stage B 완료"
}

main "$@"
