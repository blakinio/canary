#!/usr/bin/env bash
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ARTIFACT_DIR="${AGENT_E2E_ARTIFACT_DIR:-${REPO_ROOT}/artifacts/agent-e2e}"
LIFECYCLE="${REPO_ROOT}/tools/e2e/run_physical_e2e_lifecycle.sh"
ENVELOPE="${REPO_ROOT}/tools/e2e/result_envelope.py"

mkdir -p "${ARTIFACT_DIR}"
ARTIFACT_DIR="$(cd "${ARTIFACT_DIR}" && pwd)"
RUN_STARTED_AT="$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)"
printf '%s\n' "${RUN_STARTED_AT}" > "${ARTIFACT_DIR}/run-started-at.txt"

(
  cd "${REPO_ROOT}"
  python3 -m unittest -v tests.e2e.test_result_envelope
) > "${ARTIFACT_DIR}/result-envelope-contract-tests.log" 2>&1
contract_status=$?
if [[ "${contract_status}" -ne 0 ]]; then
  cat "${ARTIFACT_DIR}/result-envelope-contract-tests.log" >&2 || true
  python3 - "${ARTIFACT_DIR}/result.json" "${contract_status}" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
status = int(sys.argv[2])
path.write_text(
    json.dumps(
        {
            "schema_version": 1,
            "status": "failure",
            "scenario": "static/result-envelope-contract",
            "phase": "runtime-contract",
            "shell_exit_code": status,
            "checks": {"result_envelope_contract_tests": False},
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
    --phase "runtime-contract" \
    --shell-exit-code "${contract_status}" \
    --execution-tier "${AGENT_E2E_EXECUTION_TIER:-unknown}" \
    --started-at "${RUN_STARTED_AT}" \
    > "${ARTIFACT_DIR}/result-envelope.stdout.log" \
    2> "${ARTIFACT_DIR}/result-envelope.stderr.log" || true
  exit "${contract_status}"
fi

bash "${LIFECYCLE}"
lifecycle_status=$?

phase="$(python3 - "${ARTIFACT_DIR}/result.json" "${lifecycle_status}" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
status = int(sys.argv[2])
try:
    payload = json.loads(path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    payload = {}
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
  sha256sum "${ENVELOPE}" >> "${ARTIFACT_DIR}/runtime-hashes.txt"
fi

python3 "${ENVELOPE}" finalize \
  --artifact-dir "${ARTIFACT_DIR}" \
  --phase "${phase}" \
  --shell-exit-code "${lifecycle_status}" \
  --execution-tier "${AGENT_E2E_EXECUTION_TIER:-unknown}" \
  --started-at "${RUN_STARTED_AT}" \
  > "${ARTIFACT_DIR}/result-envelope.stdout.log" \
  2> "${ARTIFACT_DIR}/result-envelope.stderr.log"
envelope_status=$?

if [[ "${envelope_status}" -ne 0 ]]; then
  cat "${ARTIFACT_DIR}/result-envelope.stderr.log" >&2 || true
  if [[ "${lifecycle_status}" -eq 0 ]]; then
    lifecycle_status=1
  fi
fi

exit "${lifecycle_status}"
