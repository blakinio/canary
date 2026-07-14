---
task_id: CAN-20260714-analytics-dry-run-oteryn-handoff
status: validating
agent: "GPT-5.6 Thinking"
branch: docs/analytics-dry-run-oteryn-handoff
base_branch: main
created: 2026-07-14T12:00:00+02:00
updated: 2026-07-14T13:30:00+02:00
last_verified_commit: "34d16130d5e18653b69e1fa949b578436e92e046"
risk: low
related_pr: "#330"
modules_touched:
  - Gameplay Analytics
owned_paths:
  exclusive:
    - docs/systems/gameplay-analytics-dry-run.md
    - docs/agents/tasks/active/CAN-20260714-analytics-dry-run-oteryn-handoff.md
    - tools/analytics/test_gameplay_analytics_runtime_hooks.lua
    - .github/workflows/gameplay-analytics.yml
    - .github/workflows/gameplay-analytics-dry-run.yml
    - .github/workflows/gameplay-analytics-retention.yml
    - .github/workflows/gameplay-analytics-dashboards.yml
    - .github/workflows/gameplay-analytics-spells.yml
    - .github/workflows/gameplay-analytics-supply-loot.yml
    - .github/workflows/gameplay-analytics-hunt-areas.yml
  read_only:
    - data-otservbr-global/scripts/config/gameplay_analytics.lua
    - data-otservbr-global/scripts/lib/gameplay_analytics*.lua
    - data-otservbr-global/scripts/systems/gameplay_analytics.lua
    - data/scripts/lib/gameplay_analytics*.lua
    - data/scripts/runes/fireball.lua
    - data/scripts/runes/intense_healing_rune.lua
    - data/scripts/actions/items/potions.lua
    - data/scripts/eventcallbacks/monster/postdroploot_gameplay_analytics.lua
    - schema/gameplay_analytics*.sql
    - schema/gameplay_analytics_migrations/**
    - tools/analytics/**
    - grafana/gameplay-analytics-dashboard.json
reuses:
  - Existing GameplayAnalytics core/context/schema/batching/reliability/correctness wrapper stack
  - Existing dry-run, Lua, Python, shell and MariaDB test suites
  - Existing reporting views, dashboard, migration and maintenance tooling
depends_on: []
blocks: []
cross_repo_tasks: []
---

# Goal

Reconstruct the actual Gameplay Analytics state from current `main`, rerun available validation, replace the short dry-run note with an evidence-qualified runtime/dry-run reference, and add a non-implementing Oteryn migration and future analytics handoff.

# Scope

- Documentation-first audit of the current Analytics implementation and tests.
- No gameplay, protocol, OTClient, map, multichannel, instance, Redis, Security Analytics runtime or live AI-agent implementation.
- Runtime code changes were allowed only for a reproduced current defect; no runtime defect requiring a production-code change was reproduced.
- One new deterministic Lua test directly invokes the registered mock runtime hooks for summon attribution, PvP gating, mana arithmetic, healing, experience, kill/death, login and startup/shutdown delegation.
- Focused workflow path updates make the authoritative handoff document trigger all Analytics validation families.

# Acceptance criteria

- [x] Current runtime, configuration, event hooks, wrappers, persistence, retry/dead-letter, schema/migrations, maintenance, retention, reporting and administration are documented from source.
- [x] Dry-run-only behavior and no-server/no-database boundaries are explicit.
- [x] Tests requiring MariaDB are separated from tests that do not.
- [x] Historical PR/document claims are separated from current-head execution evidence.
- [x] Oteryn architecture, safety boundaries and migration classification table are complete.
- [ ] All available Analytics workflows pass on the final synchronized head.
- [ ] Full changed-file list and final merge gate are reviewed.

# Findings

- The former `docs/systems/gameplay-analytics-dry-run.md` was only a short invocation/limits note and did not describe the live runtime, persistence/failure semantics, MariaDB test boundary or Oteryn migration decisions.
- No open pull request claimed Gameplay Analytics paths when the task started.
- Comparing PR #140 merge commit with the audited current main found no later Gameplay Analytics runtime, schema, test or workflow changes; repository-wide governance and unrelated features advanced substantially.
- Summon attribution, PvP gating and mana-hook arithmetic previously had strong source validators but no direct mock execution of the registered runtime callbacks. The new test fills that deterministic dry-run gap without claiming real engine event order.
- No current gameplay, protocol or database-schema defect was reproduced.
- Direct runtime configuration can still yield an empty `serverVersion` if an operator bypasses the installer; the installer itself rejects an empty or placeholder `CANARY_SERVER_VERSION`. This is documented as an operational/staging gate, not changed in this PR.
- Local checkout execution is unavailable in the tool sandbox because GitHub DNS resolution fails. No local pass is claimed.

# Validation log

First complete test head: `34d16130d5e18653b69e1fa949b578436e92e046`.

| Workflow | Result |
| --- | --- |
| Agent Task Ownership | passed |
| Gameplay Analytics Dry Run — No server or database | passed |
| Gameplay Analytics — validators/Lua | passed |
| Gameplay Analytics — MariaDB integration | passed |
| Gameplay Analytics Retention | passed |
| Gameplay Analytics Dashboards | passed |
| Gameplay Analytics Spell Telemetry | passed |
| Gameplay Analytics Supply and Loot Telemetry | passed |
| Gameplay Analytics Hunt Areas | passed |
| General CI | passed |

The final documentation commit intentionally follows this test head. Because the authoritative handoff path is included in every Analytics workflow filter, all checks must pass again on the final head before merge.
