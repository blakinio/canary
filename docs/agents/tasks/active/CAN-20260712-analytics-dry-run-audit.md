---
task_id: CAN-20260712-analytics-dry-run-audit
status: in-progress
agent: "GPT-5.6 Thinking"
branch: test/analytics-dry-run-audit
base_branch: main
created: 2026-07-12T13:15:00+02:00
updated: 2026-07-12T13:15:00+02:00
last_verified_commit: "e7007c0dd67d0b801b09a09000c288916c15a05e"
risk: low
related_pr: ""
owned_paths:
  - data-otservbr-global/scripts/lib/gameplay_analytics_correctness.lua
  - tools/analytics/maintain_gameplay_analytics.sh
  - tools/analytics/test_gameplay_analytics_correctness_edge_cases.lua
  - tools/analytics/test_gameplay_analytics_maintenance_config_dry_run.sh
  - .github/workflows/gameplay-analytics-dry-run.yml
  - docs/agents/ACTIVE_WORK.md
  - docs/agents/tasks/active/CAN-20260712-analytics-dry-run-audit.md
---

# Goal

Run adversarial Gameplay Analytics tests without a game server or database and add repeatable dry-run coverage for lifecycle boundaries and maintenance configuration.

# Acceptance criteria

- [ ] Lua edge tests cover exact UTC rollover, timeout boundaries, offline players, wrapper idempotence and error restoration.
- [ ] Maintenance configuration can be validated without invoking MariaDB.
- [ ] Invalid and extreme `LEVEL_BRACKETS` values fail deterministically.
- [ ] A dedicated GitHub Actions workflow runs without game-server or database services.
- [ ] Any defect exposed by the tests is fixed and documented.

# Constraints

- No physical Canary server.
- No MariaDB service or database connection in the dry-run workflow.
- No protocol or cross-repository changes.
