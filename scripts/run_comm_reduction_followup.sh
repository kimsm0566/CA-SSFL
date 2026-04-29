#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/home/sunmin/SFL_Semantic"
RESULT_ROOT="/workspace/tmp/2026-04-09-comm-reduction-followup-nclients8"
HOST_RESULT_ROOT="${REPO_ROOT}/tmp/2026-04-09-comm-reduction-followup-nclients8"
DOC_ROOT="${REPO_ROOT}/docs/experiments/2026-04-09_13-03_v01_comm-reduction-followup-rayleigh-awgn"
LOG_FILE="${DOC_ROOT}/RUNLOG.md"

mkdir -p "${DOC_ROOT}"

is_blacklisted() {
  local channel="$1"
  local seed="$2"
  local beta="$3"
  local fmax="$4"
  local fmin="$5"

  if [ "${channel}" = "rayleigh" ] && [ "${beta}" = "0.001" ] && [ "${fmax}" = "0.7" ] && [ "${fmin}" = "0.4" ]; then
    return 0
  fi

  return 1
}

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
  local channel="$1"
  local seed="$2"
  local beta="$3"
  local fmax="$4"
  local fmin="$5"
  printf "%s/cifar10/n_clients_8/n_client_data_3000/batch_size_100/data_partition_type_class/model_type_resnetv2/major_percent_0.8/n_epochs_1/beta_%s/pruning_threshold_1.0/film_max_t_%s/film_min_t_%s/semantic_spreading_1/snr_adaptive_beta_1/semantic_power_0/semantic_power_alpha_2.0/SSFLv6/snr_10/compress_4096/channel_type_%s/seed_%s.npz" \
    "${HOST_RESULT_ROOT}" "${beta}" "${fmax}" "${fmin}" "${channel}" "${seed}"
}

run_candidate_exp() {
  local stage="$1"
  local channel="$2"
  local seed="$3"
  local beta="$4"
  local fmax="$5"
  local fmin="$6"
  local label="${stage}_beta_${beta}_fmax_${fmax}_fmin_${fmin}_${channel}_seed_${seed}"
  local expected_npz
  expected_npz="$(npz_path "${channel}" "${seed}" "${beta}" "${fmax}" "${fmin}")"

  if is_blacklisted "${channel}" "${seed}" "${beta}" "${fmax}" "${fmin}"; then
    log "SKIP ${label} (blacklisted unstable config)"
    return 0
  fi

  if [ -f "${expected_npz}" ]; then
    log "SKIP ${label} (existing artifact: ${expected_npz})"
    return 0
  fi

  run_exp \
    "${label}" \
    --dataset cifar10 --partition_type class --algorithm SSFLv6 --model_type resnetv2 \
    --channel_type "${channel}" --n_clients 8 --n_client_data 3000 --batch_size 100 \
    --n_epochs 1 --n_rounds 200 --compressed_dim 4096 --pruning_threshold 1.0 \
    --semantic_spreading_enable 1 --snr_adaptive_beta_enable 1 \
    --semantic_power_enable 0 --semantic_power_alpha 2.0 \
    --result_path "${RESULT_ROOT}" --seed "${seed}" \
    --beta "${beta}" --film_max_t "${fmax}" --film_min_t "${fmin}"
}

run_stage_a() {
  local configs=(
    "beta_0.1_fmax_0.7_fmin_0.4 --beta 0.1 --film_max_t 0.7 --film_min_t 0.4"
    "beta_0.1_fmax_0.8_fmin_0.5 --beta 0.1 --film_max_t 0.8 --film_min_t 0.5"
    "beta_0.1_fmax_0.9_fmin_0.6 --beta 0.1 --film_max_t 0.9 --film_min_t 0.6"
    "beta_0.01_fmax_0.7_fmin_0.4 --beta 0.01 --film_max_t 0.7 --film_min_t 0.4"
    "beta_0.01_fmax_0.8_fmin_0.5 --beta 0.01 --film_max_t 0.8 --film_min_t 0.5"
    "beta_0.01_fmax_0.9_fmin_0.6 --beta 0.01 --film_max_t 0.9 --film_min_t 0.6"
    "beta_0.001_fmax_0.7_fmin_0.4 --beta 0.001 --film_max_t 0.7 --film_min_t 0.4"
    "beta_0.001_fmax_0.8_fmin_0.5 --beta 0.001 --film_max_t 0.8 --film_min_t 0.5"
    "beta_0.001_fmax_0.9_fmin_0.6 --beta 0.001 --film_max_t 0.9 --film_min_t 0.6"
    "beta_0.0001_fmax_0.7_fmin_0.4 --beta 0.0001 --film_max_t 0.7 --film_min_t 0.4"
    "beta_0.0001_fmax_0.8_fmin_0.5 --beta 0.0001 --film_max_t 0.8 --film_min_t 0.5"
    "beta_0.0001_fmax_0.9_fmin_0.6 --beta 0.0001 --film_max_t 0.9 --film_min_t 0.6"
  )

  for cfg in "${configs[@]}"; do
    local label="${cfg%% *}"
    local extra="${cfg#* }"
    local beta
    local fmax
    local fmin
    beta="$(awk '{for(i=1;i<=NF;i++) if($i=="--beta") print $(i+1)}' <<< "${extra}")"
    fmax="$(awk '{for(i=1;i<=NF;i++) if($i=="--film_max_t") print $(i+1)}' <<< "${extra}")"
    fmin="$(awk '{for(i=1;i<=NF;i++) if($i=="--film_min_t") print $(i+1)}' <<< "${extra}")"
    for seed in 1 2; do
      run_candidate_exp "stage_a" "rayleigh" "${seed}" "${beta}" "${fmax}" "${fmin}"
    done
  done
}

select_best_config() {
  (
    cd "${REPO_ROOT}" &&
    docker compose run --rm sfl-semantic python - <<'PY'
import glob, json, numpy as np

result_root = "/workspace/tmp/2026-04-09-comm-reduction-followup-nclients8/cifar10/n_clients_8/n_client_data_3000/batch_size_100/data_partition_type_class/model_type_resnetv2/major_percent_0.8/n_epochs_1"
legacy = "/workspace/tmp/2026-04-09-rayleigh-seq-full/cifar10/n_clients_9/n_client_data_3000/batch_size_100/data_partition_type_class/model_type_resnetv2/major_percent_0.8/n_epochs_1/beta_0.01/pruning_threshold_1.0/film_max_t_0.7/film_min_t_0.4/semantic_spreading_1/snr_adaptive_beta_1/SSFLv6/snr_10/compress_4096/channel_type_rayleigh"

def summarize(paths):
    finals, comms, m6, p12 = [], [], [], []
    for path in sorted(paths):
        d = np.load(path, allow_pickle=True)
        finals.append(float(d["train_acc"][-1]))
        comms.append(float(d["comm"][-1]))
        smap = {int(s): float(a) for s, a in zip(d["test_snrs"], d["snr_accs"])}
        m6.append(smap[-6])
        p12.append(smap[12])
    return {
        "count": len(paths),
        "final_acc_mean": float(np.mean(finals)),
        "comm_mean": float(np.mean(comms)),
        "m6_mean": float(np.mean(m6)),
        "p12_mean": float(np.mean(p12)),
    }

reference = summarize(glob.glob(f"{legacy}/seed_[12].npz"))

configs = [
    ("beta_0.1_fmax_0.7_fmin_0.4", 0.1, 0.7, 0.4),
    ("beta_0.1_fmax_0.8_fmin_0.5", 0.1, 0.8, 0.5),
    ("beta_0.1_fmax_0.9_fmin_0.6", 0.1, 0.9, 0.6),
    ("beta_0.01_fmax_0.7_fmin_0.4", 0.01, 0.7, 0.4),
    ("beta_0.01_fmax_0.8_fmin_0.5", 0.01, 0.8, 0.5),
    ("beta_0.01_fmax_0.9_fmin_0.6", 0.01, 0.9, 0.6),
    ("beta_0.001_fmax_0.7_fmin_0.4", 0.001, 0.7, 0.4),
    ("beta_0.001_fmax_0.8_fmin_0.5", 0.001, 0.8, 0.5),
    ("beta_0.001_fmax_0.9_fmin_0.6", 0.001, 0.9, 0.6),
    ("beta_0.0001_fmax_0.7_fmin_0.4", 0.0001, 0.7, 0.4),
    ("beta_0.0001_fmax_0.8_fmin_0.5", 0.0001, 0.8, 0.5),
    ("beta_0.0001_fmax_0.9_fmin_0.6", 0.0001, 0.9, 0.6),
]

summaries = []
for label, beta, fmax, fmin in configs:
    pattern = (
        f"{result_root}/beta_{beta}/pruning_threshold_1.0/film_max_t_{fmax}/film_min_t_{fmin}/"
        "semantic_spreading_1/snr_adaptive_beta_1/semantic_power_0/semantic_power_alpha_2.0/"
        "SSFLv6/snr_10/compress_4096/channel_type_rayleigh/seed_*.npz"
    )
    paths = glob.glob(pattern)
    summary = summarize(paths)
    summary.update({
        "label": label,
        "beta": beta,
        "film_max_t": fmax,
        "film_min_t": fmin,
        "complete": summary["count"] == 2,
        "meets_retention": (
            summary["count"] == 2 and
            summary["final_acc_mean"] >= reference["final_acc_mean"] - 1.0 and
            summary["m6_mean"] >= reference["m6_mean"] - 1.0
        ),
        "score": summary["final_acc_mean"] + summary["m6_mean"] - 0.0002 * summary["comm_mean"],
    })
    summaries.append(summary)

complete = [s for s in summaries if s["complete"]]
eligible = [s for s in complete if s["meets_retention"]]
if eligible:
    best = min(eligible, key=lambda s: s["comm_mean"])
    selection_mode = "retention_constrained_min_comm"
else:
    best = max(complete, key=lambda s: s["score"])
    selection_mode = "fallback_score"

print(json.dumps({
    "reference": reference,
    "summaries": summaries,
    "best": best,
    "selection_mode": selection_mode,
}))
PY
  )
}

run_stage_b_awgn() {
  local beta="$1"
  local film_max_t="$2"
  local film_min_t="$3"
  for seed in 1 2; do
    run_candidate_exp "stage_b" "awgn" "${seed}" "${beta}" "${film_max_t}" "${film_min_t}"
  done
}

main() {
  touch "${LOG_FILE}"
  log "comm-reduction follow-up 시작"
  run_stage_a

  local selection_json
  selection_json="$(select_best_config | tail -n 1)"
  log "selection ${selection_json}"

  local beta
  local film_max_t
  local film_min_t
  beta="$(SELECTION_JSON="${selection_json}" python3 - <<'PY'
import json, os
s = json.loads(os.environ["SELECTION_JSON"])
print(s["best"]["beta"])
PY
)"
  film_max_t="$(SELECTION_JSON="${selection_json}" python3 - <<'PY'
import json, os
s = json.loads(os.environ["SELECTION_JSON"])
print(s["best"]["film_max_t"])
PY
)"
  film_min_t="$(SELECTION_JSON="${selection_json}" python3 - <<'PY'
import json, os
s = json.loads(os.environ["SELECTION_JSON"])
print(s["best"]["film_min_t"])
PY
)"

  run_stage_b_awgn "${beta}" "${film_max_t}" "${film_min_t}"
  log "comm-reduction follow-up 완료"
}

main "$@"
