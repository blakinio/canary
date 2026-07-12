#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNNER="${ROOT_DIR}/tools/analytics/maintain_gameplay_analytics.sh"
TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TEMP_DIR}"' EXIT

cat >"${TEMP_DIR}/mariadb" <<EOF
#!/usr/bin/env bash
touch "${TEMP_DIR}/mariadb-called"
echo "mariadb must not be called by VALIDATE_CONFIG_ONLY" >&2
exit 97
EOF
chmod +x "${TEMP_DIR}/mariadb"

run_validation() {
	env PATH="${TEMP_DIR}:${PATH}" VALIDATE_CONFIG_ONLY=true "$@" bash "${RUNNER}"
}

assert_contains() {
	local description="$1"
	local haystack="$2"
	local needle="$3"
	if [[ "${haystack}" != *"${needle}"* ]]; then
		echo "${description}: expected output to contain: ${needle}" >&2
		echo "actual output:" >&2
		echo "${haystack}" >&2
		exit 1
	fi
}

assert_invalid() {
	local description="$1"
	local expected="$2"
	shift 2
	local output
	if output="$(run_validation "$@" 2>&1)"; then
		echo "${description}: expected validation failure" >&2
		exit 1
	fi
	assert_contains "${description}" "${output}" "${expected}"
}

output="$(run_validation)"
assert_contains "default validation" "${output}" "Gameplay Analytics maintenance configuration valid"
assert_contains "default brackets" "${output}" "LEVEL_BRACKETS=50,100,200,300,400,600,800,1000"
assert_contains "default SQL case" "${output}" "LEVEL_BRACKET_SQL=CASE WHEN level_start < 50 THEN 0 WHEN level_start < 100 THEN 50 WHEN level_start < 200 THEN 100 WHEN level_start < 300 THEN 200 WHEN level_start < 400 THEN 300 WHEN level_start < 600 THEN 400 WHEN level_start < 800 THEN 600 WHEN level_start < 1000 THEN 800 ELSE 1000 END"
assert_contains "default deletion" "${output}" "DELETE_RAW_SESSIONS=false"

custom="$(run_validation LEVEL_BRACKETS=1,10,100 DELETE_RAW_SESSIONS=true RAW_RETENTION_DAYS=10 REAGGREGATE_DAYS=7 AGGREGATION_LAG_DAYS=1)"
assert_contains "custom brackets" "${custom}" "LEVEL_BRACKET_SQL=CASE WHEN level_start < 1 THEN 0 WHEN level_start < 10 THEN 1 WHEN level_start < 100 THEN 10 ELSE 100 END"
assert_contains "custom deletion" "${custom}" "DELETE_RAW_SESSIONS=true"

assert_invalid "duplicate bracket" "strictly ascending" LEVEL_BRACKETS=50,50
assert_invalid "descending bracket" "strictly ascending" LEVEL_BRACKETS=100,50
assert_invalid "zero bracket" "strictly ascending" LEVEL_BRACKETS=0,50
assert_invalid "non-numeric bracket" "strictly ascending" LEVEL_BRACKETS=50,abc
assert_invalid "32-bit overflow bracket" "must not exceed 2147483647" LEVEL_BRACKETS=2147483648
assert_invalid "arithmetic overflow bracket" "must not exceed 2147483647" LEVEL_BRACKETS=999999999999999999999999
assert_invalid "invalid validation switch" "VALIDATE_CONFIG_ONLY must be true or false" VALIDATE_CONFIG_ONLY=maybe
assert_invalid "unsafe retention window" "RAW_RETENTION_DAYS must be greater" DELETE_RAW_SESSIONS=true RAW_RETENTION_DAYS=8 REAGGREGATE_DAYS=7 AGGREGATION_LAG_DAYS=1
assert_invalid "invalid deletion switch" "DELETE_RAW_SESSIONS must be true or false" DELETE_RAW_SESSIONS=yes
assert_invalid "invalid numeric setting" "MAX_DAYS_PER_RUN must be a non-negative integer" MAX_DAYS_PER_RUN=abc
assert_invalid "zero work bound" "must be positive" MAX_DAYS_PER_RUN=0

if [[ -e "${TEMP_DIR}/mariadb-called" ]]; then
	echo "VALIDATE_CONFIG_ONLY unexpectedly invoked mariadb" >&2
	exit 1
fi

bash -n "${RUNNER}"
bash -n "$0"

echo "gameplay analytics maintenance configuration dry-run test passed"
