#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
INSTALLER="${ROOT}/tools/analytics/install_gameplay_analytics.sh"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

mkdir -p "${TMP_DIR}/bin"
touch "${TMP_DIR}/baseline.sql"

cat >"${TMP_DIR}/bin/mariadb" <<STUB
#!/usr/bin/env bash
touch "${TMP_DIR}/mariadb-called"
exit 99
STUB
chmod +x "${TMP_DIR}/bin/mariadb"

run_rejected() {
	local label="$1"
	local password="$2"
	local version="$3"
	local expected="$4"
	local log="${TMP_DIR}/${label}.log"

	rm -f "${TMP_DIR}/mariadb-called"
	set +e
	PATH="${TMP_DIR}/bin:${PATH}" \
		DB_PASSWORD="${password}" \
		CANARY_SERVER_VERSION="${version}" \
		BASELINE_SCHEMA="${TMP_DIR}/baseline.sql" \
		bash "${INSTALLER}" >"${log}" 2>&1
	local status=$?
	set -e

	if [[ ${status} -eq 0 ]]; then
		echo "${label}: installer unexpectedly accepted an invalid environment" >&2
		exit 1
	fi
	grep -F "${expected}" "${log}" >/dev/null
	if [[ -e "${TMP_DIR}/mariadb-called" ]]; then
		echo "${label}: installer attempted SQL before rejecting the environment" >&2
		exit 1
	fi
}

run_rejected "empty-password" "" "build-1" "DB_PASSWORD is empty or still has the placeholder value"
run_rejected "whitespace-password" "   " "build-1" "DB_PASSWORD is empty or still has the placeholder value"
run_rejected "placeholder-password" "CHANGE_ME" "build-1" "DB_PASSWORD is empty or still has the placeholder value"
run_rejected "empty-version" "secret" "" "CANARY_SERVER_VERSION is empty or still has the placeholder value"
run_rejected "whitespace-version" "secret" "   " "CANARY_SERVER_VERSION is empty or still has the placeholder value"
run_rejected "placeholder-version" "secret" "CHANGE_ME" "CANARY_SERVER_VERSION is empty or still has the placeholder value"

rm -f "${TMP_DIR}/mariadb-called"
set +e
PATH="${TMP_DIR}/bin:${PATH}" \
	DB_PASSWORD="secret" \
	CANARY_SERVER_VERSION="build-1" \
	BASELINE_SCHEMA="${TMP_DIR}/baseline.sql" \
	bash "${INSTALLER}" >"${TMP_DIR}/valid-values.log" 2>&1
status=$?
set -e

if [[ ${status} -ne 99 || ! -e "${TMP_DIR}/mariadb-called" ]]; then
	echo "valid-values: installer did not proceed to MariaDB after valid environment checks" >&2
	cat "${TMP_DIR}/valid-values.log" >&2
	exit 1
fi

echo "gameplay analytics installer environment guards passed"
