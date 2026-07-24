#!/usr/bin/env bash
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ARTIFACT_DIR="${AGENT_E2E_ARTIFACT_DIR:-${REPO_ROOT}/artifacts/agent-e2e}"
OTCLIENT_ROOT="${AGENT_E2E_OTCLIENT_ROOT:-${REPO_ROOT}/otclient}"
LIFECYCLE="${REPO_ROOT}/tools/e2e/run_physical_e2e_lifecycle.sh"
ENVELOPE="${REPO_ROOT}/tools/e2e/result_envelope.py"
ENVELOPE_IMPL="${REPO_ROOT}/tools/e2e/result_envelope_impl.py"
CLEANUP="${REPO_ROOT}/tools/e2e/cleanup_certification.py"
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"
DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-root}"
DB_NAME="${DB_NAME:-agent_e2e}"

mkdir -p "${ARTIFACT_DIR}"
ARTIFACT_DIR="$(cd "${ARTIFACT_DIR}" && pwd)"
RUN_STARTED_AT="$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)"
printf '%s\n' "${RUN_STARTED_AT}" > "${ARTIFACT_DIR}/run-started-at.txt"

execution_tier="${AGENT_E2E_EXECUTION_TIER:-}"
if [[ -z "${execution_tier}" ]]; then
  if [[ "${GITHUB_EVENT_NAME:-}" == "pull_request" ]]; then
    execution_tier="pr-required"
  elif [[ "${GITHUB_EVENT_NAME:-}" == "schedule" ]]; then
    execution_tier="scheduled"
  elif [[ "${GITHUB_EVENT_NAME:-}" == "workflow_dispatch" ]]; then
    execution_tier="on-demand"
  else
    execution_tier="unknown"
  fi
fi

(
  cd "${REPO_ROOT}"
  python3 -m unittest -v tests.e2e.test_result_envelope tests.e2e.test_cleanup_certification
) > "${ARTIFACT_DIR}/e2e-contract-tests.log" 2>&1
contract_status=$?
if [[ "${contract_status}" -ne 0 ]]; then
  cat "${ARTIFACT_DIR}/e2e-contract-tests.log" >&2 || true
  python3 - "${ARTIFACT_DIR}/result.json" "${contract_status}" <<'PY'
import json
import sys
from pathlib import Path

Path(sys.argv[1]).write_text(
    json.dumps(
        {
            "schema_version": 1,
            "status": "failure",
            "scenario": "static/e2e-contract",
            "phase": "runtime-contract",
            "shell_exit_code": int(sys.argv[2]),
            "checks": {"e2e_contract_tests": False},
        },
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)
PY
  python3 "${ENVELOPE}" finalize \
    --artifact-dir "${ARTIFACT_DIR}" \
    --phase runtime-contract \
    --shell-exit-code "${contract_status}" \
    --execution-tier "${execution_tier}" \
    --started-at "${RUN_STARTED_AT}" \
    > "${ARTIFACT_DIR}/result-envelope.stdout.log" \
    2> "${ARTIFACT_DIR}/result-envelope.stderr.log" || true
  exit "${contract_status}"
fi

python3 "${CLEANUP}" baseline \
  --artifact-dir "${ARTIFACT_DIR}" \
  --repo-root "${REPO_ROOT}" \
  --otclient-root "${OTCLIENT_ROOT}" \
  > "${ARTIFACT_DIR}/cleanup-baseline.stdout.log" \
  2> "${ARTIFACT_DIR}/cleanup-baseline.stderr.log"
baseline_status=$?
if [[ "${baseline_status}" -ne 0 ]]; then
  cat "${ARTIFACT_DIR}/cleanup-baseline.stderr.log" >&2 || true
  exit "${baseline_status}"
fi

setsid bash "${LIFECYCLE}" &
lifecycle_pid=$!
lifecycle_pgid="$(ps -o pgid= -p "${lifecycle_pid}" | tr -d '[:space:]')"
if [[ -z "${lifecycle_pgid}" ]]; then
  lifecycle_pgid="${lifecycle_pid}"
fi
wait "${lifecycle_pid}"
lifecycle_status=$?

MARIADB_PWD="${DB_PASSWORD}" python3 "${CLEANUP}" certify \
  --artifact-dir "${ARTIFACT_DIR}" \
  --repo-root "${REPO_ROOT}" \
  --otclient-root "${OTCLIENT_ROOT}" \
  --lifecycle-pid "${lifecycle_pid}" \
  --lifecycle-pgid "${lifecycle_pgid}" \
  --lifecycle-exit-code "${lifecycle_status}" \
  --db-host "${DB_HOST}" \
  --db-port "${DB_PORT}" \
  --db-user "${DB_USER}" \
  --db-name "${DB_NAME}" \
  > "${ARTIFACT_DIR}/cleanup-certification.stdout.log" \
  2> "${ARTIFACT_DIR}/cleanup-certification.stderr.log"
cleanup_status=$?

phase="$(python3 - "${ARTIFACT_DIR}/result.json" "${lifecycle_status}" <<'PY'
import json
import sys
from pathlib import Path

try:
    payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    payload = {}
status = int(sys.argv[2])
restart_phase = payload.get("restart_failure_phase")
if isinstance(restart_phase, str) and restart_phase:
    print(f"restart-{restart_phase}")
elif isinstance(payload.get("phase"), str) and payload["phase"]:
    print(payload["phase"])
elif status == 0:
    print("complete")
elif isinstance(payload.get("checks"), dict):
    print("evidence-evaluation")
else:
    print("bootstrap")
PY
)"

if [[ -f "${ARTIFACT_DIR}/runtime-hashes.txt" ]]; then
  sha256sum \
    "${ENVELOPE}" \
    "${ENVELOPE_IMPL}" \
    "${CLEANUP}" \
    "${BASH_SOURCE[0]}" \
    "${LIFECYCLE}" \
    >> "${ARTIFACT_DIR}/runtime-hashes.txt"
fi

python3 "${ENVELOPE}" finalize \
  --artifact-dir "${ARTIFACT_DIR}" \
  --phase "${phase}" \
  --shell-exit-code "${lifecycle_status}" \
  --execution-tier "${execution_tier}" \
  --started-at "${RUN_STARTED_AT}" \
  > "${ARTIFACT_DIR}/result-envelope.stdout.log" \
  2> "${ARTIFACT_DIR}/result-envelope.stderr.log"
envelope_status=$?

final_status="${lifecycle_status}"
if [[ "${final_status}" -eq 0 && "${cleanup_status}" -ne 0 ]]; then
  final_status="${cleanup_status}"
fi
if [[ "${final_status}" -eq 0 && "${envelope_status}" -ne 0 ]]; then
  final_status="${envelope_status}"
fi
if [[ "${cleanup_status}" -ne 0 ]]; then
  cat "${ARTIFACT_DIR}/cleanup-certification.stderr.log" >&2 || true
fi
if [[ "${envelope_status}" -ne 0 ]]; then
  cat "${ARTIFACT_DIR}/result-envelope.stderr.log" >&2 || true
fi
exit "${final_status}"
