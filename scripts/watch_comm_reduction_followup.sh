#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/home/sunmin/SFL_Semantic"
RUNNER="${REPO_ROOT}/scripts/run_comm_reduction_followup.sh"
DOC_ROOT="${REPO_ROOT}/docs/experiments/2026-04-09_13-03_v01_comm-reduction-followup-rayleigh-awgn"
WATCHDOG_LOG="${DOC_ROOT}/WATCHDOG_LOG.md"
HOST_RESULT_ROOT="${REPO_ROOT}/tmp/2026-04-09-comm-reduction-followup-nclients8"
SUDO_PASS="${SUDO_PASS:-}"
INTERVAL_SEC="${INTERVAL_SEC:-1800}"
STALE_SEC="${STALE_SEC:-1200}"

mkdir -p "${DOC_ROOT}"

log() {
  local ts
  ts="$(date '+%Y-%m-%d %H:%M:%S %Z')"
  printf -- "- [%s] %s\n" "${ts}" "$1" | tee -a "${WATCHDOG_LOG}"
}

sudo_cmd() {
  if [ -z "${SUDO_PASS}" ]; then
    echo "SUDO_PASS is required" >&2
    exit 1
  fi
  printf '%s\n' "${SUDO_PASS}" | sudo -S "$@"
}

runner_pids() {
  pgrep -f "scripts/run_comm_reduction_followup.sh" || true
}

container_ids() {
  sudo_cmd docker ps --format '{{.ID}} {{.Names}}' | awk '/sfl_semantic-sfl-semantic-run/ {print $1}'
}

latest_server_log() {
  find "${HOST_RESULT_ROOT}" -name 'seed_*server.log' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -n 1 | cut -d' ' -f2-
}

gpu_util() {
  nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -n 1 | tr -d ' '
}

restart_runner() {
  log "restarting follow-up runner"
  while read -r cid; do
    [ -n "${cid}" ] && sudo_cmd docker rm -f "${cid}" >/dev/null 2>&1 || true
  done < <(container_ids)

  while read -r pid; do
    [ -n "${pid}" ] && sudo_cmd kill -9 "${pid}" >/dev/null 2>&1 || true
  done < <(runner_pids)

  nohup bash -lc "cd '${REPO_ROOT}' && printf '%s\n' '${SUDO_PASS}' | sudo -S bash -lc './scripts/run_comm_reduction_followup.sh'" \
    >> "${DOC_ROOT}/WATCHDOG_RESTART_STDOUT.log" 2>&1 &
  sleep 5
}

inspect_stall() {
  local cid="$1"
  local slog="$2"
  log "stall suspected: container=${cid:-none}, latest_server_log=${slog:-none}"
  if [ -n "${cid}" ]; then
    sudo_cmd docker top "${cid}" >> "${DOC_ROOT}/WATCHDOG_TOP.log" 2>&1 || true
  fi
  if [ -n "${slog}" ] && [ -f "${slog}" ]; then
    tail -n 80 "${slog}" >> "${DOC_ROOT}/WATCHDOG_SERVER_TAIL.log" 2>&1 || true
  fi
  nvidia-smi >> "${DOC_ROOT}/WATCHDOG_NVIDIA_SMI.log" 2>&1 || true
}

main() {
  touch "${WATCHDOG_LOG}"
  log "watchdog started: interval=${INTERVAL_SEC}s stale=${STALE_SEC}s"
  while true; do
    local util
    local cid
    local slog
    local now
    local stale_age
    util="$(gpu_util)"
    cid="$(container_ids | head -n 1)"
    slog="$(latest_server_log)"
    now="$(date +%s)"
    stale_age=0

    if [ -n "${slog}" ] && [ -f "${slog}" ]; then
      stale_age=$(( now - $(stat -c %Y "${slog}") ))
    fi

    log "status gpu_util=${util}% container=${cid:-none} latest_server_log_age=${stale_age}s runner_pids=$(runner_pids | tr '\n' ',' | sed 's/,$//')"

    if [ -n "${cid}" ] && [ "${util}" -eq 0 ] && [ "${stale_age}" -ge "${STALE_SEC}" ]; then
      inspect_stall "${cid}" "${slog}"
      restart_runner
      log "watchdog recovery executed"
    fi

    if [ -z "$(runner_pids)" ] && [ -z "${cid}" ]; then
      log "runner and container both absent, attempting restart"
      restart_runner
    fi

    sleep "${INTERVAL_SEC}"
  done
}

main "$@"
