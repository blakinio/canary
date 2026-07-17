#!/usr/bin/env bash
set -Eeuo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SUITE="${AGENT_E2E_SUITE:-login}"
SCENARIO="${AGENT_E2E_SCENARIO_ID:-relog}"
ARTIFACT_DIR="${AGENT_E2E_ARTIFACT_DIR:-${REPO_ROOT}/artifacts/agent-e2e}"
OTCLIENT_ROOT="${AGENT_E2E_OTCLIENT_ROOT:-${REPO_ROOT}/otclient}"
ASSET_SOURCE="${AGENT_E2E_ASSET_SOURCE:-${REPO_ROOT}/tibia-client-assets/assets}"
CANARY_BIN="${CANARY_BIN:-}"
OTCLIENT_BIN="${OTCLIENT_BIN:-}"
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"
DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-root}"
DB_NAME="${DB_NAME:-agent_e2e}"
DISPLAY_NUMBER="${AGENT_E2E_DISPLAY:-:99}"
CURRENT_PHASE="bootstrap"
BACKUP_DIR=""
CREATED_MAP=false
CREATED_MAP_PATH=""
CREATED_ASSET_TARGET=false
HAD_CONFIG=false
HAD_OTCLIENTRC=false
CLIENT_PID=""
CANARY_PID=""
XVFB_PID=""
TCPDUMP_PID=""

mkdir -p "${ARTIFACT_DIR}"
ARTIFACT_DIR="$(cd "${ARTIFACT_DIR}" && pwd)"
SCENARIO_ENV="${ARTIFACT_DIR}/scenario.env"
SCENARIO_MANIFEST="${ARTIFACT_DIR}/scenario-manifest.json"
RESULT_JSON="${ARTIFACT_DIR}/result.json"

log() {
  printf '[agent-e2e] %s\n' "$*"
}

record_bootstrap_failure() {
  local status="$1"
  if [[ -f "${RESULT_JSON}" ]]; then
    return
  fi
  python3 - "${RESULT_JSON}" "${SUITE}/${SCENARIO}" "${CURRENT_PHASE}" "${status}" <<'PY'
import json
import sys
from pathlib import Path

path, scenario, phase, status = sys.argv[1:]
payload = {
    "schema_version": 1,
    "status": "failure",
    "scenario": scenario,
    "phase": phase,
    "shell_exit_code": int(status),
    "checks": {},
}
Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
}

restore_workspace() {
  if [[ -z "${BACKUP_DIR}" || ! -d "${BACKUP_DIR}" ]]; then
    return
  fi

  if [[ "${HAD_CONFIG}" == true ]]; then
    cp "${BACKUP_DIR}/config.lua" "${REPO_ROOT}/config.lua"
  else
    rm -f "${REPO_ROOT}/config.lua"
  fi

  if [[ -d "${OTCLIENT_ROOT}" ]]; then
    if [[ "${HAD_OTCLIENTRC}" == true ]]; then
      cp "${BACKUP_DIR}/otclientrc.lua" "${OTCLIENT_ROOT}/otclientrc.lua"
    else
      rm -f "${OTCLIENT_ROOT}/otclientrc.lua"
    fi
    if [[ -f "${BACKUP_DIR}/otclient-init.lua" ]]; then
      cp "${BACKUP_DIR}/otclient-init.lua" "${OTCLIENT_ROOT}/init.lua"
    fi
  fi

  if [[ "${CREATED_MAP}" == true && -n "${CREATED_MAP_PATH}" ]]; then
    rm -f "${CREATED_MAP_PATH}"
  fi
  if [[ "${CREATED_ASSET_TARGET}" == true && -n "${AGENT_E2E_CLIENT_VERSION:-}" ]]; then
    rm -rf "${OTCLIENT_ROOT}/data/things/${AGENT_E2E_CLIENT_VERSION}"
  fi
  rm -rf "${BACKUP_DIR}"
}

stop_capture() {
  if [[ -n "${TCPDUMP_PID}" ]]; then
    sudo kill -INT "${TCPDUMP_PID}" 2>/dev/null || true
    wait "${TCPDUMP_PID}" 2>/dev/null || true
    TCPDUMP_PID=""
  fi
}

cleanup() {
  local status=$?
  set +e
  stop_capture
  [[ -n "${CLIENT_PID}" ]] && kill "${CLIENT_PID}" 2>/dev/null
  [[ -n "${CANARY_PID}" ]] && kill "${CANARY_PID}" 2>/dev/null
  [[ -n "${XVFB_PID}" ]] && kill "${XVFB_PID}" 2>/dev/null
  record_bootstrap_failure "${status}"
  restore_workspace
  exit "${status}"
}
trap cleanup EXIT

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "required command not found: $1" >&2
    exit 1
  }
}

for command in python3 curl mariadb mariadb-admin sha256sum timeout Xvfb; do
  require_command "${command}"
done

CURRENT_PHASE="scenario-resolution"
: > "${SCENARIO_ENV}"
python3 "${REPO_ROOT}/tools/e2e/run_agent_e2e.py" resolve \
  --suite "${SUITE}" \
  --scenario "${SCENARIO}" \
  --manifest "${SCENARIO_MANIFEST}" \
  --github-env "${SCENARIO_ENV}"
python3 "${REPO_ROOT}/tools/e2e/server_selection.py" \
  --manifest "${SCENARIO_MANIFEST}" \
  --root "${REPO_ROOT}" \
  --github-env "${SCENARIO_ENV}"

while IFS='=' read -r key value; do
  [[ -z "${key}" ]] && continue
  if [[ ! "${key}" =~ ^[A-Z_][A-Z0-9_]*$ ]]; then
    echo "unsafe scenario environment key: ${key}" >&2
    exit 1
  fi
  printf -v "${key}" '%s' "${value}"
  export "${key}"
done < "${SCENARIO_ENV}"

PASSWORD_VARIABLE="${AGENT_E2E_PASSWORD_ENV}"
if [[ ! "${PASSWORD_VARIABLE}" =~ ^[A-Z_][A-Z0-9_]*$ ]]; then
  echo "unsafe password environment variable name: ${PASSWORD_VARIABLE}" >&2
  exit 1
fi
if [[ -z "${!PASSWORD_VARIABLE:-}" ]]; then
  echo "password environment variable is empty: ${PASSWORD_VARIABLE}" >&2
  exit 1
fi
export AGENT_E2E_PASSWORD="${!PASSWORD_VARIABLE}"
export AGENT_E2E_ARTIFACT_DIR="${ARTIFACT_DIR}"
export AGENT_E2E_PING_PROFILE="${AGENT_E2E_PING_PROFILE:-disabled}"

if [[ -z "${CANARY_BIN}" || ! -x "${CANARY_BIN}" ]]; then
  echo "CANARY_BIN must point to an executable exact-head Canary binary" >&2
  exit 1
fi
if [[ -z "${OTCLIENT_BIN}" || ! -x "${OTCLIENT_BIN}" ]]; then
  echo "OTCLIENT_BIN must point to an executable controlled OTClient binary" >&2
  exit 1
fi
if [[ ! -d "${OTCLIENT_ROOT}" ]]; then
  echo "OTClient source directory not found: ${OTCLIENT_ROOT}" >&2
  exit 1
fi
if [[ ! -s "${ASSET_SOURCE}/catalog-content.json" ]]; then
  echo "client asset source is incomplete: ${ASSET_SOURCE}" >&2
  exit 1
fi

BACKUP_DIR="$(mktemp -d)"
if [[ -f "${REPO_ROOT}/config.lua" ]]; then
  HAD_CONFIG=true
  cp "${REPO_ROOT}/config.lua" "${BACKUP_DIR}/config.lua"
fi
if [[ -f "${OTCLIENT_ROOT}/otclientrc.lua" ]]; then
  HAD_OTCLIENTRC=true
  cp "${OTCLIENT_ROOT}/otclientrc.lua" "${BACKUP_DIR}/otclientrc.lua"
fi
cp "${OTCLIENT_ROOT}/init.lua" "${BACKUP_DIR}/otclient-init.lua"

CURRENT_PHASE="runtime-contract"
AGENT_E2E_CLIENT_VERSION="$(grep -E 'static constexpr auto CLIENT_VERSION[[:space:]]*=' "${REPO_ROOT}/src/core.hpp" | grep -Eo '[0-9]+' | tail -n 1)"
ASSET_VERSION="$(tr -cd '0-9.' < "${REPO_ROOT}/tibia-client-assets/package.json.version" 2>/dev/null | cut -d. -f1,2 | tr -d '.' || true)"
if [[ -z "${ASSET_VERSION}" ]]; then
  ASSET_VERSION="${AGENT_E2E_CLIENT_VERSION}"
fi
if [[ "${ASSET_VERSION}" != "${AGENT_E2E_CLIENT_VERSION}" ]]; then
  echo "client asset version ${ASSET_VERSION} does not match Canary client version ${AGENT_E2E_CLIENT_VERSION}" >&2
  exit 1
fi
export AGENT_E2E_CLIENT_VERSION

sha256sum \
  "${CANARY_BIN}" \
  "${OTCLIENT_BIN}" \
  "${REPO_ROOT}/tools/e2e/run_agent_e2e.py" \
  "${REPO_ROOT}/tools/e2e/server_selection.py" \
  "${REPO_ROOT}/tools/e2e/run_physical_e2e.sh" \
  "${REPO_ROOT}/tools/e2e/client/agent_e2e.lua" \
  > "${ARTIFACT_DIR}/runtime-hashes.txt"
printf 'scenario=%s\ncanary_head=%s\notclient_repository=%s\notclient_ref=%s\nclient_version=%s\nasset_version=%s\nping_profile=%s\nserver_datapack=%s\nserver_map=%s\n' \
  "${AGENT_E2E_SCENARIO_KEY}" \
  "${GITHUB_SHA:-local}" \
  "${AGENT_E2E_CLIENT_REPOSITORY}" \
  "${AGENT_E2E_CLIENT_REF}" \
  "${AGENT_E2E_CLIENT_VERSION}" \
  "${ASSET_VERSION}" \
  "${AGENT_E2E_PING_PROFILE}" \
  "${AGENT_E2E_SERVER_DATAPACK}" \
  "${AGENT_E2E_SERVER_MAP}" \
  > "${ARTIFACT_DIR}/runtime-contract.txt"
ldd "${CANARY_BIN}" > "${ARTIFACT_DIR}/canary-ldd.txt" 2>&1 || true
ldd "${OTCLIENT_BIN}" > "${ARTIFACT_DIR}/otclient-ldd.txt" 2>&1 || true

CURRENT_PHASE="database-initialization"
export MARIADB_PWD="${DB_PASSWORD}"
for attempt in $(seq 1 90); do
  if mariadb-admin -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" ping >/dev/null 2>&1; then
    break
  fi
  if [[ "${attempt}" -eq 90 ]]; then
    echo "database did not become ready" >&2
    exit 1
  fi
  sleep 2
done
mariadb -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" "${DB_NAME}" < "${REPO_ROOT}/schema.sql"
mariadb -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" "${DB_NAME}" < "${REPO_ROOT}/docker/data/01-test_account.sql"
mariadb -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" "${DB_NAME}" < "${REPO_ROOT}/docker/data/02-test_account_players.sql"
mariadb -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" "${DB_NAME}" \
  -e 'DELETE FROM players_online; DELETE FROM boosted_boss;'
mariadb -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" "${DB_NAME}" \
  -e "SELECT id,name,email FROM accounts WHERE id=101; SELECT id,name,account_id,level FROM players WHERE name='${AGENT_E2E_CHARACTER}';" \
  > "${ARTIFACT_DIR}/database-fixture.tsv"

CURRENT_PHASE="server-configuration"
MAP_PATH="${AGENT_E2E_SERVER_MAP_PATH}"
if [[ ! -s "${MAP_PATH}" ]]; then
  if [[ "${AGENT_E2E_SERVER_ALLOW_MAP_DOWNLOAD}" != "true" ]]; then
    echo "selected non-default map is missing or empty: ${MAP_PATH}" >&2
    exit 1
  fi
  mkdir -p "$(dirname "${MAP_PATH}")"
  MAP_URL="$(grep -E '^mapDownloadUrl[[:space:]]*=' "${REPO_ROOT}/config.lua.dist" | sed -E 's/.*"([^"]+)".*/\1/')"
  test -n "${MAP_URL}"
  curl --fail --location --retry 5 --retry-delay 5 "${MAP_URL}" --output "${MAP_PATH}"
  CREATED_MAP=true
  CREATED_MAP_PATH="${MAP_PATH}"
fi
sha256sum "${MAP_PATH}" > "${ARTIFACT_DIR}/map.sha256"

python3 - "${REPO_ROOT}/config.lua.dist" "${REPO_ROOT}/config.lua" "${DB_HOST}" "${DB_USER}" "${DB_PASSWORD}" "${DB_NAME}" "${DB_PORT}" "${AGENT_E2E_SERVER_DATAPACK}" "${AGENT_E2E_SERVER_MAP}" <<'PY'
import re
import sys
from pathlib import Path

source, target, db_host, db_user, db_password, db_name, db_port, server_datapack, server_map = sys.argv[1:]
config = Path(source).read_text(encoding="utf-8")
values = {
    "dataPackDirectory": repr(server_datapack).replace("'", '"'),
    "mapName": repr(server_map).replace("'", '"'),
    "mapDownloadUrl": '""',
    "toggleDownloadMap": "false",
    "toggleMapCustom": "false",
    "startupDatabaseOptimization": "false",
    "mysqlDatabaseBackup": "false",
    "toggleSaveInterval": "false",
    "forgeInfluencedLimit": "0",
    "forgeFiendishLimit": "0",
    "ip": '"127.0.0.1"',
    "loginProtocolPort": "7171",
    "gameProtocolPort": "7172",
    "statusProtocolPort": "7173",
    "serverName": '"Canary E2E"',
    "houseRentPeriod": '"never"',
    "mysqlHost": repr(db_host).replace("'", '"'),
    "mysqlUser": repr(db_user).replace("'", '"'),
    "mysqlPass": repr(db_password).replace("'", '"'),
    "mysqlDatabase": repr(db_name).replace("'", '"'),
    "mysqlPort": db_port,
    "mysqlSock": '""',
    "metricsEnablePrometheus": "false",
    "metricsEnableOstream": "false",
}
for key, value in values.items():
    pattern = re.compile(rf"^{re.escape(key)}\s*=.*$", re.MULTILINE)
    matches = pattern.findall(config)
    if len(matches) != 1:
        raise SystemExit(f"expected exactly one config key {key}, got {len(matches)}")
    config = pattern.sub(f"{key} = {value}", config, count=1)
auth_pattern = re.compile(r"^authType\s*=.*$", re.MULTILINE)
if auth_pattern.search(config):
    config = auth_pattern.sub('authType = "password"', config, count=1)
else:
    config += '\nauthType = "password"\n'
Path(target).write_text(config, encoding="utf-8")
PY
sha256sum "${REPO_ROOT}/config.lua" > "${ARTIFACT_DIR}/config.sha256"

CURRENT_PHASE="client-configuration"
ASSET_TARGET="${OTCLIENT_ROOT}/data/things/${AGENT_E2E_CLIENT_VERSION}"
if [[ ! -s "${ASSET_TARGET}/catalog-content.json" ]]; then
  mkdir -p "${ASSET_TARGET}"
  cp -a "${ASSET_SOURCE}/." "${ASSET_TARGET}/"
  CREATED_ASSET_TARGET=true
fi
sha256sum "${ASSET_TARGET}/catalog-content.json" > "${ARTIFACT_DIR}/catalog-content.sha256"
du -sh "${ASSET_TARGET}" > "${ARTIFACT_DIR}/assets-size.txt"
cp "${REPO_ROOT}/${AGENT_E2E_CLIENT_AUTOMATION}" "${OTCLIENT_ROOT}/otclientrc.lua"
python3 - "${OTCLIENT_ROOT}/init.lua" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
text = text.replace("enabled = true,", "enabled = false,", 1)
text = text.replace("installSounds = true,", "installSounds = false,", 1)
path.write_text(text, encoding="utf-8")
PY

CURRENT_PHASE="server-startup"
(
  cd "${REPO_ROOT}"
  "${CANARY_BIN}" > "${ARTIFACT_DIR}/canary.stdout.log" 2> "${ARTIFACT_DIR}/canary.stderr.log"
) &
CANARY_PID=$!
echo "${CANARY_PID}" > "${ARTIFACT_DIR}/canary.pid"
for attempt in $(seq 1 450); do
  if ! kill -0 "${CANARY_PID}" 2>/dev/null; then
    cat "${ARTIFACT_DIR}/canary.stdout.log" "${ARTIFACT_DIR}/canary.stderr.log" >&2 || true
    exit 1
  fi
  if grep -qi 'server online!' "${ARTIFACT_DIR}/canary.stdout.log" "${ARTIFACT_DIR}/canary.stderr.log"; then
    break
  fi
  if [[ "${attempt}" -eq 450 ]]; then
    echo "Canary did not report server online" >&2
    exit 1
  fi
  sleep 2
done

CURRENT_PHASE="physical-client"
export DISPLAY="${DISPLAY_NUMBER}"
Xvfb "${DISPLAY_NUMBER}" -screen 0 1280x800x24 > "${ARTIFACT_DIR}/xvfb.log" 2>&1 &
XVFB_PID=$!
echo "${XVFB_PID}" > "${ARTIFACT_DIR}/xvfb.pid"
sleep 2

if command -v tcpdump >/dev/null 2>&1; then
  sudo tcpdump -i lo -nn -s 0 -U -w "${ARTIFACT_DIR}/game-port-7172.pcap" 'tcp port 7172' \
    > "${ARTIFACT_DIR}/tcpdump.stdout.log" 2> "${ARTIFACT_DIR}/tcpdump.stderr.log" &
  TCPDUMP_PID=$!
  echo "${TCPDUMP_PID}" > "${ARTIFACT_DIR}/tcpdump.pid"
  sleep 1
else
  printf 'tcpdump unavailable\n' > "${ARTIFACT_DIR}/tcpdump-unavailable.txt"
fi

set +e
(
  cd "${OTCLIENT_ROOT}"
  if command -v strace >/dev/null 2>&1; then
    timeout --signal=TERM "$((AGENT_E2E_GLOBAL_TIMEOUT_SECONDS + 30))" \
      strace -ff -tt -e trace=network,close,shutdown,poll,ppoll,select,pselect6,epoll_wait,epoll_pwait \
      -o "${ARTIFACT_DIR}/otclient.strace" \
      "${OTCLIENT_BIN}" \
      > "${ARTIFACT_DIR}/otclient.stdout.log" \
      2> "${ARTIFACT_DIR}/otclient.stderr.log"
  else
    printf 'strace unavailable\n' > "${ARTIFACT_DIR}/strace-unavailable.txt"
    timeout --signal=TERM "$((AGENT_E2E_GLOBAL_TIMEOUT_SECONDS + 30))" \
      "${OTCLIENT_BIN}" \
      > "${ARTIFACT_DIR}/otclient.stdout.log" \
      2> "${ARTIFACT_DIR}/otclient.stderr.log"
  fi
) &
CLIENT_PID=$!
set -e
echo "${CLIENT_PID}" > "${ARTIFACT_DIR}/otclient.pid"

ONLINE_CAPTURED=false
for _ in $(seq 1 120); do
  if [[ -f "${ARTIFACT_DIR}/client-events.tsv" ]] && \
     grep -q $'\tonline_stable_1\tconfirmed$' "${ARTIFACT_DIR}/client-events.tsv"; then
    mariadb -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" "${DB_NAME}" \
      -e "SELECT * FROM players_online; SELECT id,name,lastlogin,lastlogout FROM players WHERE name='${AGENT_E2E_CHARACTER}';" \
      > "${ARTIFACT_DIR}/database-online.tsv"
    mariadb -N -s -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" "${DB_NAME}" \
      -e "SELECT COUNT(*) FROM players_online WHERE player_id=(SELECT id FROM players WHERE name='${AGENT_E2E_CHARACTER}');" \
      > "${ARTIFACT_DIR}/database-online-count.txt"
    ONLINE_CAPTURED=true
    break
  fi
  if ! kill -0 "${CLIENT_PID}" 2>/dev/null; then
    break
  fi
  sleep 1
done
printf '%s\n' "${ONLINE_CAPTURED}" > "${ARTIFACT_DIR}/online-captured.txt"
if command -v import >/dev/null 2>&1; then
  import -display "${DISPLAY_NUMBER}" -window root "${ARTIFACT_DIR}/client.png" || true
fi

set +e
wait "${CLIENT_PID}"
CLIENT_EXIT_CODE=$?
set -e
CLIENT_PID=""
printf '%s\n' "${CLIENT_EXIT_CODE}" > "${ARTIFACT_DIR}/otclient-exit-code.txt"
stop_capture

CURRENT_PHASE="database-final-state"
mariadb -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" "${DB_NAME}" \
  -e "SELECT * FROM players_online; SELECT id,name,lastlogin,lastlogout FROM players WHERE name='${AGENT_E2E_CHARACTER}';" \
  > "${ARTIFACT_DIR}/database-after.tsv"
mariadb -N -s -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" "${DB_NAME}" \
  -e 'SELECT COUNT(*) FROM players_online;' > "${ARTIFACT_DIR}/database-after-online-count.txt"
mariadb -N -s -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" "${DB_NAME}" \
  -e "SELECT lastlogin > 0 FROM players WHERE name='${AGENT_E2E_CHARACTER}';" > "${ARTIFACT_DIR}/database-lastlogin-set.txt"
mariadb -N -s -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" "${DB_NAME}" \
  -e "SELECT lastlogout > 0 FROM players WHERE name='${AGENT_E2E_CHARACTER}';" > "${ARTIFACT_DIR}/database-lastlogout-set.txt"

grep -F "${AGENT_E2E_CHARACTER} has logged in." "${ARTIFACT_DIR}/canary.stdout.log" \
  > "${ARTIFACT_DIR}/server-login-matches.txt" || true
grep -Ei 'disconnect|write error|read error|connection|session end|logged out' \
  "${ARTIFACT_DIR}/canary.stdout.log" "${ARTIFACT_DIR}/canary.stderr.log" \
  > "${ARTIFACT_DIR}/server-connection-matches.txt" || true

CURRENT_PHASE="evidence-evaluation"
python3 - "${ARTIFACT_DIR}" "${GITHUB_SHA:-local}" <<'PY'
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

artifacts = Path(sys.argv[1])
canary_head = sys.argv[2]
manifest = json.loads((artifacts / "scenario-manifest.json").read_text(encoding="utf-8"))
scenario = manifest["scenario"]
required = scenario["assertions"]["required_markers"]

events = []
event_pairs = set()
event_path = artifacts / "client-events.tsv"
if event_path.exists():
    for line in event_path.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        timestamp, key, value = parts
        events.append({"timestamp": timestamp, "key": key, "value": value})
        event_pairs.add(f"{key}={value}")
missing = [marker for marker in required if marker not in event_pairs]


def integer(name: str, default: int = -1) -> int:
    try:
        return int((artifacts / name).read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return default


def line_count(name: str) -> int:
    path = artifacts / name
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip())


client_exit = integer("otclient-exit-code.txt")
players_online_snapshot = integer("database-online-count.txt")
after_online_count = integer("database-after-online-count.txt")
lastlogin_set = integer("database-lastlogin-set.txt")
lastlogout_set = integer("database-lastlogout-set.txt")
server_login_count = line_count("server-login-matches.txt")
session_record_count = sum(
    1 for phase in (1, 2)
    if (artifacts / f"session-{phase}.record").exists()
    and (artifacts / f"session-{phase}.record").stat().st_size > 0
)

fatal_patterns = re.compile(
    r"segmentation fault|stack smashing|corrupted double-linked list|double free|assertion failed|fatal error|terminate called|std::bad_alloc",
    re.IGNORECASE,
)
fatal_log_hits = []
for name in (
    "otclient.stdout.log",
    "otclient.stderr.log",
    "otclient.internal.log",
    "canary.stdout.log",
    "canary.stderr.log",
):
    path = artifacts / name
    if not path.exists():
        continue
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if fatal_patterns.search(line):
            fatal_log_hits.append(f"{name}: {line}")

checks = {
    "required_markers": not missing,
    "client_exit_zero": client_exit == 0,
    "two_server_logins_observed": server_login_count == 2,
    "two_packet_records_present": session_record_count == 2,
    "lastlogin_persisted": lastlogin_set == 1,
    "lastlogout_persisted": lastlogout_set == 1,
    "no_fatal_runtime_log": not fatal_log_hits,
}
success = all(checks.values())
result = {
    "schema_version": 2,
    "status": "success" if success else "failure",
    "scenario": manifest["key"],
    "canary_head": canary_head,
    "client_repository": scenario["client"]["repository"],
    "client_ref": scenario["client"]["ref"],
    "checks": checks,
    "missing_markers": missing,
    "client_exit_code": client_exit,
    "server_login_count": server_login_count,
    "session_record_count": session_record_count,
    "lastlogin_set": lastlogin_set,
    "lastlogout_set": lastlogout_set,
    "players_online_snapshot": players_online_snapshot,
    "players_online_snapshot_is_diagnostic_only": True,
    "after_online_count": after_online_count,
    "fatal_log_hits": fatal_log_hits,
    "events": events,
}
(artifacts / "result.json").write_text(
    json.dumps(result, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(json.dumps(result, indent=2, sort_keys=True))
if not success:
    raise SystemExit(1)
PY

CURRENT_PHASE="complete"
log "scenario ${AGENT_E2E_SCENARIO_KEY} passed"
