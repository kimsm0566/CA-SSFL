#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/home/sunmin/SFL_Semantic"
DOC_ROOT="${REPO_ROOT}/docs/experiments/2026-04-09_21-58_v01_rayleigh-pivot-after-spreading-failure"
QUEUE_LOG="${DOC_ROOT}/QUEUE_LOG.md"

mkdir -p "${DOC_ROOT}"

log() {
  local ts
  ts="$(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf -- "- [%s] %s\n" "${ts}" "$1" | tee -a "${QUEUE_LOG}"
}

touch "${QUEUE_LOG}"
log "waiting for awgn ca-ssfl orig backfill to finish"

while pgrep -f 'run_awgn_ca_ssfl_orig_nclients8.sh' >/dev/null 2>&1; do
  sleep 60
done

log "awgn ca-ssfl orig finished, starting rayleigh semantic power sweep"
printf '%s\n' 'a' | sudo -S bash -lc "${REPO_ROOT}/scripts/run_rayleigh_semantic_power_sweep_nclients8.sh"
