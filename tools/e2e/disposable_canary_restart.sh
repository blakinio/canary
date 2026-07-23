#!/usr/bin/env bash

DISPOSABLE_CANARY_RESTART_SCENARIO_KEY="recovery/canary-restart-recovery"
DISPOSABLE_CANARY_RESTART_CHARACTER="Paladin 15"
DISPOSABLE_CANARY_RESTART_EXPECTED_BALANCE="12345"
DISPOSABLE_CANARY_RESTART_READY_FILE="${ARTIFACT_DIR}/canary-restart-ready"
DISPOSABLE_CANARY_RESTART_OLD_PID_FILE="${ARTIFACT_DIR}/canary-old.pid"
DISPOSABLE_CANARY_RESTART_NEW_PID_FILE="${ARTIFACT_DIR}/canary-restarted.pid"
DISPOSABLE_CANARY_RESTART_PHASE_FILE="${ARTIFACT_DIR}/canary-restart-current-phase.txt"
DISPOSABLE_CANARY_RESTART_PHASES_TSV="${ARTIFACT_DIR}/canary-restart-phases.tsv"
DISPOSABLE_CANARY_RESTART_EVIDENCE="${ARTIFACT_DIR}/canary-restart-evidence.json"
DISPOSABLE_CANARY_RESTART_EVENTS="${ARTIFACT_DIR}/client-events.tsv"
DISPOSABLE_CANARY_RESTART_PRE_BALANCE_FILE="${ARTIFACT_DIR}/database-restart-pre-balance.txt"

is_disposable_canary_restart_scenario() {
  [[ "${AGENT_E2E_SCENARIO_KEY:-${SUITE}/${SCENARIO}}" == "${DISPOSABLE_CANARY_RESTART_SCENARIO_KEY}" ]]
}

record_restart_phase() {
  local phase="$1"
  local status="$2"
  local detail="$3"
  CURRENT_PHASE="restart-${phase}"
  printf '%s\n' "${phase}" > "${DISPOSABLE_CANARY_RESTART_PHASE_FILE}"
  printf '%s\t%s\t%s\n' "${phase}" "${status}" "${detail//$'\t'/ }" >> "${DISPOSABLE_CANARY_RESTART_PHASES_TSV}"
}

fail_restart_phase() {
  local phase="$1"
  local detail="$2"
  record_restart_phase "${phase}" "failure" "${detail}"
  printf '[agent-e2e-restart] %s failed: %s\n' "${phase}" "${detail}" >&2
  return 1
}

initialize_disposable_canary_restart() {
  if ! is_disposable_canary_restart_scenario; then
    return 0
  fi
  : > "${DISPOSABLE_CANARY_RESTART_PHASES_TSV}"
  rm -f \
    "${DISPOSABLE_CANARY_RESTART_READY_FILE}" \
    "${DISPOSABLE_CANARY_RESTART_OLD_PID_FILE}" \
    "${DISPOSABLE_CANARY_RESTART_NEW_PID_FILE}" \
    "${DISPOSABLE_CANARY_RESTART_PRE_BALANCE_FILE}" \
    "${DISPOSABLE_CANARY_RESTART_EVIDENCE}"
}

validate_disposable_canary_restart_contract() {
  if ! is_disposable_canary_restart_scenario; then
    return 0
  fi
  (
    cd "${REPO_ROOT}"
    python3 -m unittest tests.e2e.test_canary_restart_recovery
  )
}

wait_for_restart_client_marker() {
  local key="$1"
  local value="$2"
  for _ in $(seq 1 1800); do
    if [[ -f "${DISPOSABLE_CANARY_RESTART_EVENTS}" ]] && \
       awk -F '\t' -v key="${key}" -v value="${value}" \
         '$2 == key && $3 == value { found = 1 } END { exit(found ? 0 : 1) }' \
         "${DISPOSABLE_CANARY_RESTART_EVENTS}"; then
      return 0
    fi
    sleep 0.1
  done
  return 1
}

wait_for_persisted_restart_balance() {
  local balance=""
  for _ in $(seq 1 100); do
    balance="$(mariadb -N -s -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" "${DB_NAME}" \
      -e "SELECT balance FROM players WHERE name='${DISPOSABLE_CANARY_RESTART_CHARACTER}' LIMIT 1;" 2>/dev/null || true)"
    printf '%s\n' "${balance}" > "${DISPOSABLE_CANARY_RESTART_PRE_BALANCE_FILE}"
    if [[ "${balance}" == "${DISPOSABLE_CANARY_RESTART_EXPECTED_BALANCE}" ]]; then
      return 0
    fi
    sleep 0.1
  done
  return 1
}

restart_pid_is_exact_canary() {
  local pid="$1"
  [[ "${pid}" =~ ^[0-9]+$ ]] || return 1
  kill -0 "${pid}" 2>/dev/null || return 1
  local actual_exe
  local expected_exe
  actual_exe="$(readlink -f "/proc/${pid}/exe" 2>/dev/null || true)"
  expected_exe="$(readlink -f "${CANARY_BIN}" 2>/dev/null || true)"
  [[ -n "${actual_exe}" && "${actual_exe}" == "${expected_exe}" ]]
}

resolve_exact_runner_owned_canary_pid() {
  local lifecycle_pid="$1"
  if restart_pid_is_exact_canary "${lifecycle_pid}"; then
    printf '%s\n' "${lifecycle_pid}"
    return 0
  fi
  [[ "${lifecycle_pid}" =~ ^[0-9]+$ ]] || return 1
  kill -0 "${lifecycle_pid}" 2>/dev/null || return 1
  local children_file="/proc/${lifecycle_pid}/task/${lifecycle_pid}/children"
  [[ -r "${children_file}" ]] || return 1
  local matches=()
  local child_pid
  for child_pid in $(cat "${children_file}"); do
    if restart_pid_is_exact_canary "${child_pid}"; then
      matches+=("${child_pid}")
    fi
  done
  [[ "${#matches[@]}" -eq 1 ]] || return 1
  printf '%s\n' "${matches[0]}"
}

wait_for_exact_canary_process() {
  local pid="$1"
  for _ in $(seq 1 80); do
    if restart_pid_is_exact_canary "${pid}"; then
      return 0
    fi
    kill -0 "${pid}" 2>/dev/null || return 1
    sleep 0.05
  done
  return 1
}

terminate_exact_disposable_canary() {
  local pid="$1"
  local phase="$2"
  if ! restart_pid_is_exact_canary "${pid}"; then
    fail_restart_phase "${phase}" "runner-owned process tree does not contain the exact CANARY_BIN process"
    return 1
  fi
  kill -TERM "${pid}"
  for _ in $(seq 1 240); do
    if ! kill -0 "${pid}" 2>/dev/null; then
      return 0
    fi
    sleep 0.25
  done
  fail_restart_phase "${phase}" "exact disposable Canary process did not terminate after SIGTERM"
}

restart_disposable_canary() {
  if ! is_disposable_canary_restart_scenario; then
    fail_restart_phase "restart-request" "fixed restart seam invoked outside ${DISPOSABLE_CANARY_RESTART_SCENARIO_KEY}"
    return 1
  fi
  if [[ -z "${CANARY_BIN}" || ! -x "${CANARY_BIN}" ]]; then
    fail_restart_phase "restart-request" "CANARY_BIN is not the executable selected by the canonical lifecycle"
    return 1
  fi
  if [[ "${AGENT_E2E_CHARACTER}" != "${DISPOSABLE_CANARY_RESTART_CHARACTER}" ]]; then
    fail_restart_phase "restart-request" "fixed restart scenario character contract changed"
    return 1
  fi

  if ! wait_for_restart_client_marker "mutation_request" "bank_balance_12345"; then
    fail_restart_phase "pre-restart-gameplay" "client did not issue the fixed bank-balance mutation"
    return 1
  fi
  if ! wait_for_restart_client_marker "save_request" "fixed_server_save"; then
    fail_restart_phase "pre-restart-gameplay" "client did not request the fixed server save after mutation"
    return 1
  fi
  if ! wait_for_restart_client_marker "restart_request" "disposable_canary"; then
    fail_restart_phase "restart-request" "client did not request the fixed disposable Canary restart"
    return 1
  fi
  if ! wait_for_persisted_restart_balance; then
    fail_restart_phase "pre-restart-gameplay" "database did not persist exact balance 12345 before restart"
    return 1
  fi
  record_restart_phase "pre-restart-gameplay" "success" "mutation=bank_balance_12345;save=requested;database_balance_12345_confirmed"
  record_restart_phase "restart-request" "success" "fixed_disposable_canary"

  local lifecycle_pid="${CANARY_PID}"
  local old_pid=""
  old_pid="$(resolve_exact_runner_owned_canary_pid "${lifecycle_pid}" || true)"
  if [[ -z "${old_pid}" ]] || ! restart_pid_is_exact_canary "${old_pid}"; then
    fail_restart_phase "process-termination" "canonical lifecycle process tree does not identify exactly one CANARY_BIN process"
    return 1
  fi
  printf '%s\n' "${old_pid}" > "${DISPOSABLE_CANARY_RESTART_OLD_PID_FILE}"
  if ! terminate_exact_disposable_canary "${old_pid}" "process-termination"; then
    return 1
  fi
  CANARY_PID=""
  if kill -0 "${old_pid}" 2>/dev/null; then
    fail_restart_phase "process-termination" "old disposable Canary PID remains active"
    return 1
  fi
  record_restart_phase "process-termination" "success" "old_pid=${old_pid};lifecycle_pid=${lifecycle_pid};inactive=true"

  local initial_stdout_lines=0
  if [[ -f "${ARTIFACT_DIR}/canary.stdout.log" ]]; then
    initial_stdout_lines="$(wc -l < "${ARTIFACT_DIR}/canary.stdout.log")"
  fi

  (
    cd "${REPO_ROOT}"
    exec "${CANARY_BIN}" >> "${ARTIFACT_DIR}/canary.stdout.log" 2>> "${ARTIFACT_DIR}/canary.stderr.log"
  ) &
  CANARY_PID=$!
  local new_pid="${CANARY_PID}"
  printf '%s\n' "${new_pid}" > "${DISPOSABLE_CANARY_RESTART_NEW_PID_FILE}"
  printf '%s\n' "${new_pid}" > "${ARTIFACT_DIR}/canary.pid"

  if [[ "${new_pid}" == "${old_pid}" ]]; then
    fail_restart_phase "server-startup" "restarted Canary unexpectedly reused the old PID"
    return 1
  fi
  if ! wait_for_exact_canary_process "${new_pid}"; then
    fail_restart_phase "server-startup" "replacement PID is not the exact CANARY_BIN process"
    return 1
  fi
  record_restart_phase "server-startup" "success" "new_pid=${new_pid};same_binary=true"

  local ready=false
  for _ in $(seq 1 220); do
    if ! restart_pid_is_exact_canary "${new_pid}"; then
      fail_restart_phase "readiness" "restarted Canary exited before readiness"
      return 1
    fi
    if tail -n "+$((initial_stdout_lines + 1))" "${ARTIFACT_DIR}/canary.stdout.log" 2>/dev/null | grep -qi 'server online!'; then
      ready=true
      break
    fi
    sleep 0.5
  done
  if [[ "${ready}" != true ]]; then
    fail_restart_phase "readiness" "restarted Canary did not report a new server-online marker"
    return 1
  fi

  local ghost_count
  ghost_count="$(mariadb -N -s -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" "${DB_NAME}" \
    -e "SELECT COUNT(*) FROM players_online WHERE player_id=(SELECT id FROM players WHERE name='${DISPOSABLE_CANARY_RESTART_CHARACTER}');")"
  printf '%s\n' "${ghost_count}" > "${ARTIFACT_DIR}/database-restart-pre-relogin-online-count.txt"
  if [[ "${ghost_count}" != "0" ]]; then
    fail_restart_phase "readiness" "stale players_online row remained before recovery relog"
    return 1
  fi
  record_restart_phase "readiness" "success" "new_server_online=true;ghost_session_count=0"
  printf 'ready\n' > "${DISPOSABLE_CANARY_RESTART_READY_FILE}"
  CURRENT_PHASE="physical-client"
}

finalize_disposable_canary_restart() {
  if ! is_disposable_canary_restart_scenario; then
    return 0
  fi

  if ! wait_for_restart_client_marker "login_2" "success"; then
    fail_restart_phase "reconnect" "controlled OTClient did not reconnect after server readiness"
    return 1
  fi
  record_restart_phase "reconnect" "success" "login_2=success"

  if ! wait_for_restart_client_marker "recovery_online" "confirmed"; then
    fail_restart_phase "relog" "controlled OTClient did not re-enter the world"
    return 1
  fi
  record_restart_phase "relog" "success" "world_reentry_confirmed"

  if ! wait_for_restart_client_marker "persistence_check_balance" "success"; then
    fail_restart_phase "persistence-assertion" "post-relog client balance assertion did not pass"
    return 1
  fi
  record_restart_phase "persistence-assertion" "success" "client_balance_12345_confirmed_after_relog"

  if ! wait_for_restart_client_marker "cleanup" "safe_logout_complete"; then
    fail_restart_phase "cleanup" "controlled OTClient did not complete safe logout"
    return 1
  fi
  local final_online_count
  final_online_count="$(cat "${ARTIFACT_DIR}/database-after-online-count.txt" 2>/dev/null || true)"
  if [[ "${final_online_count}" != "0" ]]; then
    fail_restart_phase "cleanup" "players_online was not empty after recovery safe logout"
    return 1
  fi

  local cleanup_pid="${CANARY_PID}"
  if ! terminate_exact_disposable_canary "${cleanup_pid}" "cleanup"; then
    return 1
  fi
  CANARY_PID=""
  record_restart_phase "cleanup" "success" "safe_logout=true;players_online=0;restarted_canary_stopped=true"
  CURRENT_PHASE="database-final-state"
}

write_disposable_canary_restart_evidence() {
  if ! is_disposable_canary_restart_scenario; then
    return 0
  fi
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
pre_restart_balance = read_int("database-restart-pre-balance.txt")
ghost_count = read_int("database-restart-pre-relogin-online-count.txt")
final_online_count = read_int("database-after-online-count.txt")
checks = {
    "all_restart_phases_success": all(phases.get(name, {}).get("status") == "success" for name in required),
    "pre_restart_balance_persisted": pre_restart_balance == 12345,
    "old_process_terminated": phases.get("process-termination", {}).get("status") == "success",
    "replacement_process_started": phases.get("server-startup", {}).get("status") == "success",
    "restart_pid_changed": old_pid > 0 and new_pid > 0 and old_pid != new_pid,
    "server_ready_after_restart": phases.get("readiness", {}).get("status") == "success",
    "ghost_session_absent_before_relogin": ghost_count == 0,
    "physical_relog_succeeded": phases.get("relog", {}).get("status") == "success",
    "persistence_assertion_succeeded": phases.get("persistence-assertion", {}).get("status") == "success",
    "cleanup_succeeded": phases.get("cleanup", {}).get("status") == "success" and final_online_count == 0,
}
failure_phase = next((name for name in required if phases.get(name, {}).get("status") != "success"), None)
payload = {
    "schema_version": 1,
    "contract": "canary-universal-e2e-disposable-canary-restart-recovery-v1",
    "old_pid": old_pid,
    "new_pid": new_pid,
    "pre_restart_persisted_balance": pre_restart_balance,
    "ghost_session_count_before_relogin": ghost_count,
    "final_players_online_count": final_online_count,
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

augment_disposable_canary_restart_result() {
  if ! is_disposable_canary_restart_scenario; then
    return 0
  fi
  python3 - "${ARTIFACT_DIR}" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

artifacts = Path(sys.argv[1])
result_path = artifacts / "result.json"
evidence_path = artifacts / "canary-restart-evidence.json"
result = json.loads(result_path.read_text(encoding="utf-8"))
evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
checks = result.setdefault("checks", {})
for name, passed in evidence.get("checks", {}).items():
    checks[f"restart_{name}"] = bool(passed)
result["restart_evidence"] = evidence
result["restart_failure_phase"] = evidence.get("failure_phase")
result["status"] = "success" if all(bool(value) for value in checks.values()) else "failure"
result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
if result["status"] != "success":
    raise SystemExit(1)
PY
}
