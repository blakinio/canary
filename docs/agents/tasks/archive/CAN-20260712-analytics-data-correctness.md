---
task_id: CAN-20260712-analytics-data-correctness
status: merged
agent: "GPT-5.6 Thinking"
branch: fix/analytics-data-correctness
base_branch: main
created: 2026-07-12T10:34:45Z
completed: 2026-07-12T11:03:00Z
risk: medium
related_pr: "#135"
merge_commit: "c726b342a77327206682fc51cec18052098a67d5"
cross_repo_tasks: []
---

# Goal

Eliminate verified Gameplay Analytics data-correctness defects without weakening disabled-by-default behavior, bounded work, privacy, migration safety or failure isolation.

# Result

PR #135 was squash-merged as `c726b342a77327206682fc51cec18052098a67d5`.

Implemented:

- UTC day rollover before recording the first metric of a later day;
- persistence eligibility requiring combat or death;
- expiry and discard of non-combat-only sessions;
- retention of death and rollover fragments below `minimumSessionSeconds`;
- rune supply accounting conditional on `REMOVE_RUNE_CHARGES`;
- validated maintenance `LEVEL_BRACKETS` replacing the ignored runtime list;
- dimension-safe Grafana labels and consistent hunt/server filters;
- terminal dead-letter reporting with the old pending name retained only as a compatibility alias;
- focused Lua, Python, shell and real MariaDB regression coverage.

# Validation

All current-head workflows passed before merge:

- Gameplay Analytics;
- Gameplay Analytics Retention;
- Gameplay Analytics Dashboards;
- Gameplay Analytics Supply and Loot Telemetry;
- Gameplay Analytics Spell Telemetry;
- Gameplay Analytics Hunt Areas;
- general CI.

No unresolved reviews or review threads existed. GitHub reported the PR mergeable. Local checkout tests were unavailable because the execution sandbox could not resolve GitHub; no local result was claimed.

# Compatibility and rollout

- No protocol, OTClient or cross-repository change.
- Production enabling remains an operator action.
- Deploy with a new `CANARY_SERVER_VERSION` because collection and aggregation semantics changed.
- Keep `DELETE_RAW_SESSIONS=false` until recent aggregates have been rebuilt and reconciled.
- Rollback by disabling Analytics, reverting #135, restoring the prior maintenance environment and rebuilding while raw rows remain.

# Reuse guidance

Use the existing live `GameplayAnalytics` wrapper stack. Load `gameplay_analytics_correctness.lua` after reliability, never reload the core from shared scripts, configure brackets through maintenance `LEVEL_BRACKETS`, and do not treat persisted dead-letter rows as an active replay queue.
