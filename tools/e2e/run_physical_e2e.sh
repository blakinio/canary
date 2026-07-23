#!/usr/bin/env bash
set -Eeuo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SUITE="${AGENT_E2E_SUITE:-login}"
SCENARIO="${AGENT_E2E_SCENARIO_ID:-relog}"
RECOVERY_KEY="recovery/canary-restart-recovery"
CORE_RUNNER="${REPO_ROOT}/tools/e2e/run_physical_e2e_core.sh"
ARTIFACT_DIR="${AGENT_E2E_ARTIFACT_DIR:-${REPO_ROOT}/artifacts/agent-e2e}"
CANARY_BIN="${CANARY_BIN:-}"
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"
DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-root}"
DB_NAME="${DB_NAME:-agent_e2e}"
EXPECTED_CHARACTER="Paladin 15"
CANARY_PID_FILE="${ARTIFACT_DIR}/canary.pid"
OLD_PID_FILE="${ARTIFACT_DIR}/canary-old.pid"
RESTARTED_PID_FILE="${ARTIFACT_DIR}/canary-restarted.pid"
RESTART_READY_FILE="${ARTIFACT_DIR}/canary-restart-ready"
RESTART_PHASE_FILE="${ARTIFACT_DIR}/canary-restart-current-phase.txt"
RESTART_PHASES_TSV="${ARTIFACT_DIR}/canary-restart-phases.tsv"
RESTART_EVIDENCE="${ARTIFACT_DIR}/canary-restart-evidence.json"
CLIENT_EVENTS="${ARTIFACT_DIR}/client-events.tsv"
CORE_PID=""
WATCHER_PID=""

if [[ "${SUITE}/${SCENARIO}" != "${RECOVERY_KEY}" ]]; then
  exec bash "${CORE_RUNNER}"
fi

mkdir -p "${ARTIFACT_DIR}"
: > "${RESTART_PHASES_TSV}"
rm -f "${RESTART_READY_FILE}" "${OLD_PID_FILE}" "${RESTARTED_PID_FILE}" "${RESTART_EVIDENCE}"

record_restart_phase() {
  local phase="$1"
  local status="$2"
  local detail="$3"
  printf '%s\n' "${phase}" > "${RESTART_PHASE_FILE}"
  printf '%s\t%s\t%s\n' "${phase}" "${status}" "${detail//$'\t'/ }" >> "${RESTART_PHASES_TSV}"
}

fail_restart() {
  local phase="$1"
  local detail="$2"
  record_restart_phase "${phase}" "failure" "${detail}"
  printf '[agent-e2e-restart] %s failed: %s\n' "${phase}" "${detail}" >&2
  return 1
}

wait_for_client_marker() {
  local marker="$1"
  local key="${marker%%=*}"
  local value="${marker#*=}"
  for _ in $(seq 1 1800); do
    if [[ -f "${CLIENT_EVENTS}" ]] && awk -F '\t' -v key="${key}" -v value="${value}" '$2 == key && $3 == value { found = 1 } END { exit(found ? 0 : 1) }' "${CLIENT_EVENTS}"; then
      return 0
    fi
    sleep 0.1
  done
  return 1
}

pid_is_expected_canary() {
  local pid="$1"
  [[ "${pid}" =~ ^[0-9]+$ ]] || return 1
  kill -0 "${pid}" 2>/dev/null || return 1
  local actual_exe
  local expected_exe
  actual_exe="$(readlink -f "/proc/${pid}/exe" 2>/dev/null || true)"
  expected_exe="$(readlink -f "${CANARY_BIN}" 2>/dev/null || true)"
  [[ -n "${actual_exe}" && "${actual_exe}" == "${expected_exe}" ]]
}

wait_for_expected_canary_exe() {
  local pid="$1"
  for _ in $(seq 1 80); do
    if pid_is_expected_canary "${pid}"; then
      return 0
    fi
    kill -0 "${pid}" 2>/dev/null || return 1
    sleep 0.05
  done
  return 1
}

terminate_fixed_canary_pid() {
  local pid="$1"
  local phase="$2"
  if ! pid_is_expected_canary "${pid}"; then
    fail_restart "${phase}" "runner-owned PID is not the exact CANARY_BIN process"
    return 1
  fi
  kill -TERM "${pid}"
  for _ in $(seq 1 240); do
    if ! kill -0 "${pid}" 2>/dev/null; then
      return 0
    fi
    sleep 0.25
  done
  fail_restart "${phase}" "exact disposable Canary process did not terminate after SIGTERM"
}

cleanup_restarted_canary() {
  [[ -f "${RESTARTED_PID_FILE}" ]] || return 0
  local pid
  pid="$(cat "${RESTARTED_PID_FILE}" 2>/dev/null || true)"
  if pid_is_expected_canary "${pid}"; then
    kill -TERM "${pid}" 2>/dev/null || true
    for _ in $(seq 1 120); do
      if ! kill -0 "${pid}" 2>/dev/null; then
        return 0
      fi
      sleep 0.25
    done
  fi
}

wrapper_cleanup() {
  local status=$?
  set +e
  [[ -n "${WATCHER_PID}" ]] && kill "${WATCHER_PID}" 2>/dev/null || true
  [[ -n "${CORE_PID}" ]] && kill "${CORE_PID}" 2>/dev/null || true
  cleanup_restarted_canary
  exit "${status}"
}
trap wrapper_cleanup EXIT

restart_disposable_canary() {
  if [[ "${SUITE}/${SCENARIO}" != "${RECOVERY_KEY}" ]]; then
    fail_restart "restart-request" "fixed restart seam invoked outside ${RECOVERY_KEY}"
    return 1
  fi
  if [[ -z "${CANARY_BIN}" || ! -x "${CANARY_BIN}" ]]; then
    fail_restart "restart-request" "CANARY_BIN is not the executable selected by the canonical lifecycle"
    return 1
  fi
  if ! wait_for_client_marker "pre_restart_persistence_check=success"; then
    fail_restart "pre-restart-gameplay" "client did not prove the persistent state before restart"
    return 1
  fi
  record_restart_phase "pre-restart-gameplay" "success" "client_balance_12345_confirmed"
  if ! wait_for_client_marker "restart_request=disposable_canary"; then
    fail_restart "restart-request" "client did not request the fixed disposable Canary restart"
    return 1
  fi
  record_restart_phase "restart-request" "success" "fixed_disposable_canary"

  if [[ ! -f "${CANARY_PID_FILE}" ]]; then
    fail_restart "process-termination" "canonical runner PID file is missing"
    return 1
  fi
  local old_pid
  old_pid="$(cat "${CANARY_PID_FILE}")"
  if ! pid_is_expected_canary "${old_pid}"; then
    fail_restart "process-termination" "canonical runner PID does not identify the exact CANARY_BIN process"
    return 1
  fi
  printf '%s\n' "${old_pid}" > "${OLD_PID_FILE}"
  if ! terminate_fixed_canary_pid "${old_pid}" "process-termination"; then
    return 1
  fi
  if kill -0 "${old_pid}" 2>/dev/null; then
    fail_restart "process-termination" "old disposable Canary PID remains active"
    return 1
  fi
  record_restart_phase "process-termination" "success" "old_pid=${old_pid};inactive=true"

  local initial_stdout_lines=0
  if [[ -f "${ARTIFACT_DIR}/canary.stdout.log" ]]; then
    initial_stdout_lines="$(wc -l < "${ARTIFACT_DIR}/canary.stdout.log")"
  fi
  (
    cd "${REPO_ROOT}"
    "${CANARY_BIN}" >> "${ARTIFACT_DIR}/canary.stdout.log" 2>> "${ARTIFACT_DIR}/canary.stderr.log"
  ) &
  local new_pid=$!
  printf '%s\n' "${new_pid}" > "${RESTARTED_PID_FILE}"
  printf '%s\n' "${new_pid}" > "${CANARY_PID_FILE}"
  if [[ "${new_pid}" == "${old_pid}" ]]; then
    fail_restart "server-startup" "restarted Canary unexpectedly reused the old PID"
    return 1
  fi
  if ! wait_for_expected_canary_exe "${new_pid}"; then
    fail_restart "server-startup" "replacement PID is not the exact CANARY_BIN process"
    return 1
  fi
  record_restart_phase "server-startup" "success" "new_pid=${new_pid};same_binary=true"

  local ready=false
  for _ in $(seq 1 220); do
    if ! pid_is_expected_canary "${new_pid}"; then
      fail_restart "readiness" "restarted Canary exited before readiness"
      return 1
    fi
    if tail -n "+$((initial_stdout_lines + 1))" "${ARTIFACT_DIR}/canary.stdout.log" 2>/dev/null | grep -qi 'server online!'; then
      ready=true
      break
    fi
    sleep 0.5
  done
  if [[ "${ready}" != true ]]; then
    fail_restart "readiness" "restarted Canary did not report a new server-online marker"
    return 1
  fi

  local ghost_count
  ghost_count="$(MARIADB_PWD="${DB_PASSWORD}" mariadb -N -s -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" "${DB_NAME}" -e "SELECT COUNT(*) FROM players_online WHERE player_id=(SELECT id FROM players WHERE name='${EXPECTED_CHARACTER}');")"
  printf '%s\n' "${ghost_count}" > "${ARTIFACT_DIR}/database-restart-pre-relogin-online-count.txt"
  if [[ "${ghost_count}" != "0" ]]; then
    fail_restart "readiness" "stale players_online row remained before recovery relog"
    return 1
  fi
  record_restart_phase "readiness" "success" "new_server_online=true;ghost_session_count=0"
  printf 'ready\n' > "${RESTART_READY_FILE}"

  if ! wait_for_client_marker "login_request_2="; then
    :
  fi
  if ! wait_for_client_marker "login_2=success"; then
    fail_restart "reconnect" "controlled OTClient did not reconnect after server readiness"
    return 1
  fi
  record_restart_phase "reconnect" "success" "login_2=success"
  if ! wait_for_client_marker "recovery_online=confirmed"; then
    fail_restart "relog" "controlled OTClient did not re-enter the world"
    return 1
  fi
  record_restart_phase "relog" "success" "world_reentry_confirmed"
  if ! wait_for_client_marker "persistence_check_balance=success"; then
    fail_restart "persistence-assertion" "post-relog typed balance assertion did not pass"
    return 1
  fi
  record_restart_phase "persistence-assertion" "success" "client_balance_12345_confirmed_after_relog"
  if ! wait_for_client_marker "cleanup=safe_logout_complete"; then
    fail_restart "cleanup" "controlled OTClient did not complete safe logout"
    return 1
  fi
  if ! terminate_fixed_canary_pid "${new_pid}" "cleanup"; then
    return 1
  fi
  record_restart_phase "cleanup" "success" "safe_logout=true;restarted_canary_stopped=true"
}

write_restart_evidence() {
  python3 - "${ARTIFACT_DIR}" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

artifacts = Path(sys.argv[1])
phase_path = artifacts / "canary-restart-phases.tsv"
phases: dict[str, dict[str, str]] = {}
if phase_path.exists():
    for raw in phase_path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = raw.split("\t", 2)
        if len(parts) == 3:
            phase, status, detail = parts
            phases[phase] = {"status": status, "detail": detail}
required = [
    "pre-restart-gameplay",
    "restart-request",
    "process-termination",
    "server-startup",
    "readiness",
    "reconnect",
    "relog",
    "persistence-assertion",
    "cleanup",
]

def read_int(name: str) -> int:
    try:
        return int((artifacts / name).read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return -1

old_pid = read_int("canary-old.pid")
new_pid = read_int("canary-restarted.pid")
ghost_count = read_int("database-restart-pre-relogin-online-count.txt")
checks = {
    "all_restart_phases_success": all(phases.get(name, {}).get("status") == "success" for name in required),
    "old_process_terminated": phases.get("process-termination", {}).get("status") == "success",
    "replacement_process_started": phases.get("server-startup", {}).get("status") == "success",
    "restart_pid_changed": old_pid > 0 and new_pid > 0 and old_pid != new_pid,
    "server_ready_after_restart": phases.get("readiness", {}).get("status") == "success",
    "ghost_session_absent_before_relogin": ghost_count == 0,
    "physical_relog_succeeded": phases.get("relog", {}).get("status") == "success",
    "persistence_assertion_succeeded": phases.get("persistence-assertion", {}).get("status") == "success",
    "cleanup_succeeded": phases.get("cleanup", {}).get("status") == "success",
}
failure_phase = next((name for name in required if phases.get(name, {}).get("status") != "success"), None)
payload = {
    "schema_version": 1,
    "contract": "canary-universal-e2e-disposable-canary-restart-recovery-v1",
    "old_pid": old_pid,
    "new_pid": new_pid,
    "ghost_session_count_before_relogin": ghost_count,
    "phases": {name: phases.get(name, {"status": "missing", "detail": ""}) for name in required},
    "checks": checks,
    "failure_phase": failure_phase,
    "status": "success" if all(checks.values()) else "failure",
}
(artifacts / "canary-restart-evidence.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY
}

augment_result() {
  python3 - "${ARTIFACT_DIR}" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

artifacts = Path(sys.argv[1])
result_path = artifacts / "result.json"
evidence_path = artifacts / "canary-restart-evidence.json"
if not result_path.exists() or not evidence_path.exists():
    raise SystemExit(0)
result = json.loads(result_path.read_text(encoding="utf-8"))
evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
checks = result.setdefault("checks", {})
for name, passed in evidence.get("checks", {}).items():
    checks[f"restart_{name}"] = bool(passed)
result["restart_evidence"] = evidence
result["restart_failure_phase"] = evidence.get("failure_phase")
result["status"] = "success" if all(bool(value) for value in checks.values()) else "failure"
result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
}

bash "${CORE_RUNNER}" &
CORE_PID=$!
restart_disposable_canary &
WATCHER_PID=$!

set +e
wait "${CORE_PID}"
CORE_STATUS=$?
CORE_PID=""
wait "${WATCHER_PID}"
WATCHER_STATUS=$?
WATCHER_PID=""
set -e

write_restart_evidence
augment_result
trap - EXIT
cleanup_restarted_canary

if [[ "${CORE_STATUS}" -ne 0 || "${WATCHER_STATUS}" -ne 0 ]]; then
  exit 1
fi

python3 - "${RESTART_EVIDENCE}" <<'PY'
import json
import sys
from pathlib import Path
payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if payload.get("status") != "success":
    raise SystemExit(1)
PY
