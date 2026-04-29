#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/home/sunmin/SFL_Semantic"
LATENT_RUNNER="${REPO_ROOT}/scripts/run_rayleigh_latent_mixing_pilot_nclients8.sh"
QUEUE_RUNNER="${REPO_ROOT}/scripts/queue_rayleigh_latent_then_semidense_nclients8.sh"
LATENT_DOC="${REPO_ROOT}/docs/experiments/2026-04-10_01-17_v01_rayleigh-latent-mixing-pilot"
SEMI_DOC="${REPO_ROOT}/docs/experiments/2026-04-10_01-28_v01_rayleigh-semidense-pilot"
WATCHDOG_LOG="${SEMI_DOC}/WATCHDOG_LOG.md"
LATENT_RESULT_ROOT="${REPO_ROOT}/tmp/2026-04-10-rayleigh-latent-mixing-pilot"
SEMI_RESULT_ROOT="${REPO_ROOT}/tmp/2026-04-10-rayleigh-semidense-pilot"
SUDO_PASS="${SUDO_PASS:-}"
INTERVAL_SEC="${INTERVAL_SEC:-1800}"
STALE_SEC="${STALE_SEC:-1200}"

mkdir -p "${SEMI_DOC}"

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

latent_pids() {
  pgrep -f "scripts/run_rayleigh_latent_mixing_pilot_nclients8.sh" || true
}

queue_pids() {
  pgrep -f "scripts/queue_rayleigh_latent_then_semidense_nclients8.sh" || true
}

container_ids() {
  sudo_cmd docker ps --format '{{.ID}} {{.Names}}' | awk '/sfl_semantic-sfl-semantic-run/ {print $1}'
}

gpu_util() {
  nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -n 1 | tr -d ' '
}

latent_done() {
  local count
  count="$(find "${LATENT_RESULT_ROOT}" -name 'seed_*.npz' 2>/dev/null | wc -l | tr -d ' ')"
  [ "${count}" = "6" ]
}

latest_activity_log() {
  local roots=()
  [ -d "${LATENT_RESULT_ROOT}" ] && roots+=("${LATENT_RESULT_ROOT}")
  [ -d "${SEMI_RESULT_ROOT}" ] && roots+=("${SEMI_RESULT_ROOT}")
  if [ "${#roots[@]}" -eq 0 ]; then
    return 0
  fi
  find "${roots[@]}" -name 'seed_*server.log' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -n 1 | cut -d' ' -f2-
}

restart_latent() {
  log "restarting latent runner"
  while read -r cid; do
    [ -n "${cid}" ] && sudo_cmd docker rm -f "${cid}" >/dev/null 2>&1 || true
  done < <(container_ids)
  while read -r pid; do
    [ -n "${pid}" ] && sudo_cmd kill -9 "${pid}" >/dev/null 2>&1 || true
  done < <(latent_pids)

  nohup bash -lc "cd '${REPO_ROOT}' && printf '%s\n' '${SUDO_PASS}' | sudo -S bash '${LATENT_RUNNER}'" \
    >> "${LATENT_DOC}/WATCHDOG_RESTART_STDOUT.log" 2>&1 &
  sleep 5
}

restart_queue() {
  log "restarting queue runner"
  while read -r pid; do
    [ -n "${pid}" ] && sudo_cmd kill -9 "${pid}" >/dev/null 2>&1 || true
  done < <(queue_pids)

  nohup bash -lc "cd '${REPO_ROOT}' && printf '%s\n' '${SUDO_PASS}' | sudo -S bash '${QUEUE_RUNNER}'" \
    >> "${SEMI_DOC}/WATCHDOG_RESTART_STDOUT.log" 2>&1 &
  sleep 5
}

inspect_stall() {
  local cid="$1"
  local slog="$2"
  log "stall suspected: container=${cid:-none}, latest_server_log=${slog:-none}"
  if [ -n "${cid}" ]; then
    sudo_cmd docker top "${cid}" >> "${SEMI_DOC}/WATCHDOG_TOP.log" 2>&1 || true
  fi
  if [ -n "${slog}" ] && [ -f "${slog}" ]; then
    tail -n 120 "${slog}" >> "${SEMI_DOC}/WATCHDOG_SERVER_TAIL.log" 2>&1 || true
  fi
  nvidia-smi >> "${SEMI_DOC}/WATCHDOG_NVIDIA_SMI.log" 2>&1 || true
}

main() {
  touch "${WATCHDOG_LOG}"
  log "watchdog started: interval=${INTERVAL_SEC}s stale=${STALE_SEC}s"
  while true; do
    util="$(gpu_util)"
    cid="$(container_ids | head -n 1)"
    slog="$(latest_activity_log)"
    now="$(date +%s)"
    stale_age=0
    if [ -n "${slog}" ] && [ -f "${slog}" ]; then
      stale_age=$(( now - $(stat -c %Y "${slog}") ))
    fi

    if latent_done; then
      latent_state="yes"
    else
      latent_state="no"
    fi

    log "status gpu_util=${util}% container=${cid:-none} stale=${stale_age}s latent_done=${latent_state} latent_pids=$(latent_pids | tr '\n' ',' | sed 's/,$//') queue_pids=$(queue_pids | tr '\n' ',' | sed 's/,$//')"

    if [ -n "${cid}" ] && [ "${util}" -eq 0 ] && [ "${stale_age}" -ge "${STALE_SEC}" ]; then
      inspect_stall "${cid}" "${slog}"
      if latent_done; then
        restart_queue
      else
        restart_latent
      fi
      log "watchdog recovery executed"
    fi

    if ! latent_done && [ -z "$(latent_pids)" ] && [ -z "${cid}" ]; then
      log "latent runner absent before completion, restarting"
      restart_latent
    fi

    if [ -z "$(queue_pids)" ]; then
      log "queue runner absent, restarting"
      restart_queue
    fi

    sleep "${INTERVAL_SEC}"
  done
}

main "$@"
