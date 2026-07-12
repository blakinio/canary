# Gameplay Analytics dry-run validation

This validation path checks Gameplay Analytics without starting Canary and without connecting to MariaDB.

## Maintenance configuration only

Run:

```bash
VALIDATE_CONFIG_ONLY=true \
LEVEL_BRACKETS=50,100,200,300,400,600,800,1000 \
DELETE_RAW_SESSIONS=false \
bash tools/analytics/maintain_gameplay_analytics.sh
```

The command validates numeric bounds, booleans, the raw-retention safety margin and the complete `LEVEL_BRACKETS` contract. It prints the generated SQL `CASE` expression and exits before constructing or invoking a database query. Values above `2147483647` are rejected before Bash arithmetic can overflow.

Do not set `VALIDATE_CONFIG_ONLY=true` in the production systemd service. It is a one-shot diagnostic switch.

## Mocked runtime tests

`tools/analytics/test_gameplay_analytics_correctness_edge_cases.lua` uses a deterministic clock and mocked players to cover:

- exact UTC midnight and multi-day rollover;
- same-day activity that must not roll over;
- online and offline non-combat expiry;
- timeout clamping and exact boundary behavior;
- short death retention;
- wrapper idempotence;
- restoration of `minimumSessionSeconds` after a simulated finish exception;
- direct combat, death-only and non-combat enqueue eligibility.

No engine process, map, network service or database is used.

## Automated workflow

`.github/workflows/gameplay-analytics-dry-run.yml` runs static Python validators, mutation tests, shell configuration tests, mocked LuaJIT tests and reporting-asset parsing. Its job is named `No server or database` and defines no service containers.

## Limits

Dry-run validation cannot prove that real Canary event hooks fire in the correct order, that production MariaDB permissions and latency are correct, or that a long-running server has no performance or concurrency issue. Those require staging or production-like integration tests. The dry-run suite is intended to find deterministic logic, boundary, configuration and wrapper-composition defects before deployment.
