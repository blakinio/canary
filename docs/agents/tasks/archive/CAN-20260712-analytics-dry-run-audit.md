---
task_id: CAN-20260712-analytics-dry-run-audit
status: completed
agent: "GPT-5.6 Thinking"
branch: test/analytics-dry-run-audit
base_branch: main
created: 2026-07-12T13:15:00+02:00
updated: 2026-07-12T13:25:00+02:00
last_verified_commit: "880a508e3f4ca71f17cbff78cb2cf11bd3b7ef88"
risk: low
related_pr: "#140"
merge_commit: "86f553c15cbabf2234243f11584cdc6ed8008029"
---

# Goal

Run adversarial Gameplay Analytics tests without a game server or database and add repeatable dry-run coverage for lifecycle boundaries and maintenance configuration.

# Acceptance criteria

- [x] Lua edge tests cover exact UTC rollover, timeout boundaries, offline players, wrapper idempotence and error restoration.
- [x] Maintenance configuration can be validated without invoking MariaDB.
- [x] Invalid and extreme `LEVEL_BRACKETS` values fail deterministically.
- [x] A dedicated GitHub Actions workflow runs without game-server or database services.
- [x] Defects exposed by the tests are fixed and documented.

# Defects found

1. `shortDeathSessionsPersisted` and `shortRolloverSessionsPersisted` were incremented before the wrapped finish returned. A thrown finish error could therefore report persistence that never happened. Counters now advance only after finish returns successfully.
2. Online non-combat sessions expiring before `minimumSessionSeconds` were removed by the core before reaching the explicit enqueue eligibility filter. Data was not persisted, but `discardedNonCombatSessions` undercounted these cases. Expiry now temporarily uses minimum `0`, allowing the explicit non-combat filter to reject and count every expired utility-only session.
3. `LEVEL_BRACKETS` accepted arbitrarily large decimal strings before Bash arithmetic. Values above `2147483647` are now rejected before evaluation.

# Dry-run coverage

- Exact UTC midnight and multi-day rollover.
- Same-day activity without rollover.
- Online and offline non-combat expiry.
- Timeout clamping at the exact boundary.
- Short-death retention.
- Wrapper idempotence.
- Global minimum restoration after a simulated finish exception.
- Direct combat/death/non-combat enqueue eligibility.
- Valid, duplicate, descending, zero, malformed and overflow maintenance brackets.
- Proof that `VALIDATE_CONFIG_ONLY=true` does not invoke a stubbed `mariadb` executable.

# Validation

| Commit | Workflow | Result |
|---|---|---|
| `880a508e3f4ca71f17cbff78cb2cf11bd3b7ef88` | Gameplay Analytics Dry Run — `No server or database` | passed |
| same | Gameplay Analytics | passed |
| same | Gameplay Analytics Retention | passed |
| same | General CI | passed |

The dry-run job defines no service containers and uses no game server, map process, network service or database connection.

# Limits

These tests do not prove real event-hook ordering, production database permissions/latency, long-running performance or concurrency behavior. Those remain staging/integration concerns.

# Completion

- Final status: merged
- PR: #140
- Merge commit: `86f553c15cbabf2234243f11584cdc6ed8008029`
- Cross-repository impact: none
- Archived at: `docs/agents/tasks/archive/CAN-20260712-analytics-dry-run-audit.md`
