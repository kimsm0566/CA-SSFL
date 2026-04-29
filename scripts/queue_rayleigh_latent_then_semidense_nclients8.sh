#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/home/sunmin/SFL_Semantic"
LATENT_DOC="${REPO_ROOT}/docs/experiments/2026-04-10_01-17_v01_rayleigh-latent-mixing-pilot"
SEMI_DOC="${REPO_ROOT}/docs/experiments/2026-04-10_01-28_v01_rayleigh-semidense-pilot"
LOG_FILE="${SEMI_DOC}/QUEUE_LOG.md"

mkdir -p "${SEMI_DOC}"

log() {
  local ts
  ts="$(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf -- "- [%s] %s\n" "${ts}" "$1" | tee -a "${LOG_FILE}"
}

wait_for_latent() {
  local latent_result_root="${REPO_ROOT}/tmp/2026-04-10-rayleigh-latent-mixing-pilot"
  log "latent mixing pilot 완료 대기 시작"
  while true; do
    count="$(find "${latent_result_root}" -name 'seed_*.npz' 2>/dev/null | wc -l | tr -d ' ')"
    if [ "${count}" = "6" ]; then
      log "latent mixing pilot 결과 6개 확인"
      break
    fi
    sleep 60
  done
}

evaluate_latent() {
  (
    cd "${REPO_ROOT}" &&
    printf 'a\n' | sudo -S docker compose run --rm sfl-semantic bash -lc "python - <<'PY'
import json
from pathlib import Path
import numpy as np

base_root = Path('/workspace/tmp/2026-04-09-rayleigh-cross-benchmark-nclients8/cifar10/n_clients_8/n_client_data_3000/batch_size_100/data_partition_type_class/model_type_resnetv2/major_percent_0.8/n_epochs_1/beta_0.01/pruning_threshold_1.0/film_max_t_0.7/film_min_t_0.4/semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0')
latent_root = Path('/workspace/tmp/2026-04-10-rayleigh-latent-mixing-pilot/cifar10/n_clients_8/n_client_data_3000/batch_size_100/data_partition_type_class/model_type_resnetv2/major_percent_0.8/n_epochs_1/beta_0.01/pruning_threshold_1.0/film_max_t_0.7/film_min_t_0.4/semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0')
out_path = Path('/workspace/docs/experiments/2026-04-10_01-17_v01_rayleigh-latent-mixing-pilot/summary.json')

def summarize(paths):
    finals = []
    comms = []
    snr_accs = []
    for path in paths:
        d = np.load(path, allow_pickle=True)
        finals.append(float(d['train_acc'][-1]))
        comms.append(float(d['comm'][-1]))
        snr_accs.append(d['snr_accs'].astype(float))
    arr = np.stack(snr_accs)
    return {
        'count': len(paths),
        'final_acc_mean': float(np.mean(finals)),
        'comm_mean': float(np.mean(comms)),
        'm6_mean': float(np.mean(arr[:, 0])),
    }

base_new = base_root / 'latent_mixing_0/latent_mixing_strength_0.0/latent_mixing_groups_8/semidense_0/semidense_group_size_16/semidense_group_topk_4/SSFLv6/snr_10/compress_4096/channel_type_rayleigh'
base_old = base_root / 'SSFLv6/snr_10/compress_4096/channel_type_rayleigh'
base_paths = sorted(base_new.glob('seed_[12].npz'))
if len(base_paths) < 2:
    base_paths = sorted(base_old.glob('seed_[12].npz'))
baseline = summarize(base_paths)
candidates = {}
for strength in ['0.1', '0.25', '0.5']:
    p_new = latent_root / f'latent_mixing_1/latent_mixing_strength_{strength}/latent_mixing_groups_8/semidense_0/semidense_group_size_16/semidense_group_topk_4/SSFLv6/snr_10/compress_4096/channel_type_rayleigh'
    p_old = latent_root / f'latent_mixing_1/latent_mixing_strength_{strength}/latent_mixing_groups_8/SSFLv6/snr_10/compress_4096/channel_type_rayleigh'
    paths = sorted(p_new.glob('seed_[12].npz'))
    if len(paths) < 2:
        paths = sorted(p_old.glob('seed_[12].npz'))
    if len(paths) == 2:
        candidates[strength] = summarize(paths)

decision = {'baseline': baseline, 'candidates': candidates, 'promote_latent': False}
for strength, metrics in candidates.items():
    if metrics['final_acc_mean'] >= baseline['final_acc_mean'] - 0.5 and metrics['m6_mean'] >= baseline['m6_mean']:
        decision['promote_latent'] = True
        decision['winner'] = strength
        break

out_path.write_text(json.dumps(decision, indent=2), encoding='utf-8')
print(json.dumps(decision))
PY"
  )
}

main() {
  touch "${LOG_FILE}"
  log "latent -> semidense 자동 큐 시작"
  wait_for_latent
  decision_json="$(evaluate_latent)"
  log "latent 평가 완료: ${decision_json}"

  if printf '%s' "${decision_json}" | grep -q '"promote_latent": true'; then
    log "latent mixing pilot에서 기준 충족. semidense는 실행하지 않음"
    exit 0
  fi

  log "latent mixing 이득 부족. semidense pilot 시작"
  printf 'a\n' | sudo -S bash "${REPO_ROOT}/scripts/run_rayleigh_semidense_pilot_nclients8.sh"
}

main "$@"
