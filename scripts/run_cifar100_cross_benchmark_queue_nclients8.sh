#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/home/sunmin/SFL_Semantic"
DOC_ROOT="${REPO_ROOT}/docs/experiments/2026-04-11/2026-04-11_22-20_v01_cifar100-cross-benchmark-plan"
LOG_FILE="${DOC_ROOT}/QUEUE_LOG.md"

mkdir -p "${DOC_ROOT}"

log() {
  local ts
  ts="$(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf -- "- [%s] %s\n" "${ts}" "$1" | tee -a "${LOG_FILE}"
}

main() {
  touch "${LOG_FILE}"
  log "cifar100 cross benchmark queue 시작"
  bash "${REPO_ROOT}/scripts/run_cifar100_awgn_threeway_benchmark_nclients8.sh"
  bash "${REPO_ROOT}/scripts/run_cifar100_rayleigh_threeway_benchmark_nclients8.sh"
  log "cifar100 cross benchmark queue 완료"
}

main "$@"
