#!/usr/bin/env bash
set -uo pipefail

REPO_ROOT="/home/sunmin/SFL_Semantic"
DOC_ROOT="${REPO_ROOT}/docs/experiments/2026-04-14/2026-04-14_00-40_v01_cifar100-cross-benchmark-updated-ca-ssfl"
LOG_FILE="${DOC_ROOT}/QUEUE_LOG.md"

mkdir -p "${DOC_ROOT}"

log() {
  local ts
  ts="$(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf -- "- [%s] %s\n" "${ts}" "$1" | tee -a "${LOG_FILE}"
}

main() {
  touch "${LOG_FILE}"
  log "cifar100 cross benchmark queue (updated CA-SSFL) 시작"
  bash "${REPO_ROOT}/scripts/run_cifar100_awgn_threeway_benchmark_updated_ca_ssfl_nclients8.sh" || log "awgn runner exited non-zero"
  bash "${REPO_ROOT}/scripts/run_cifar100_rayleigh_threeway_benchmark_updated_ca_ssfl_nclients8.sh" || log "rayleigh runner exited non-zero"
  log "cifar100 cross benchmark queue (updated CA-SSFL) 완료"
}

main "$@"
