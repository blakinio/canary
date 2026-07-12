---
task_id: CAN-20260712-analytics-data-correctness
coordination_id: ""
status: ready-to-merge
agent: "GPT-5.6 Thinking"
branch: fix/analytics-data-correctness
base_branch: main
created: 2026-07-12T10:34:45Z
updated: 2026-07-12T11:01:00Z
last_verified_commit: "4837508d5d25b37f99be859e780f6e1ec47947e5"
risk: medium
related_issue: ""
related_pr: "#135"
depends_on: []
blocks: []
owned_paths:
  - data-otservbr-global/scripts/config/gameplay_analytics.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics_correctness.lua
  - data-otservbr-global/scripts/systems/gameplay_analytics.lua
  - data/scripts/runes/fireball.lua
  - data/scripts/runes/intense_healing_rune.lua
  - tools/analytics/**
  - schema/gameplay_analytics_views.sql
  - grafana/gameplay-analytics-dashboard.json
  - docs/systems/gameplay-analytics*.md
  - .github/workflows/gameplay-analytics*.yml
  - docs/agents/ACTIVE_WORK.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
  - docs/agents/tasks/active/CAN-20260712-analytics-data-correctness.md
modules_touched:
  - Gameplay Analytics runtime lifecycle
  - Gameplay Analytics maintenance aggregation
  - Gameplay Analytics reporting and Grafana
  - Gameplay Analytics supply tracking
reuses:
  - GameplayAnalytics wrapper architecture
  - existing bounded retry/batching/context/schema layers
  - existing Analytics MariaDB and dashboard integration tests
public_interfaces:
  - GameplayAnalytics status fields
  - maintenance LEVEL_BRACKETS environment variable
  - analytics_dead_letter_health reporting view
cross_repo_tasks: []
---

# Goal

Eliminate the verified data-correctness defects in Gameplay Analytics without weakening disabled-by-default, bounded-work, privacy, migration, or failure-isolation guarantees.

# Acceptance criteria

- [x] Mana/supply/spell-only sessions expire and are not persisted as hunt sessions without combat or death.
- [x] Death sessions persist even when shorter than `minimumSessionSeconds`.
- [x] Sessions roll over at a UTC day boundary before recording the first event of the new day.
- [x] Rune supply cost is recorded only when rune charges are actually removed.
- [x] Maintenance uses validated configurable level-bracket boundaries rather than ignoring the Lua list.
- [x] Grafana series include every grouping dimension and use consistent hunt/server filters.
- [x] Persisted dead-letter rows are labelled as terminal records, not an active retry queue.
- [x] Focused Lua, Python, shell and MariaDB regression coverage is added and passes in CI.
- [x] Module catalogue and changelog are updated.
- [x] Cross-repository impact is none.
- [x] Autonomous merge gate satisfied at verified head `4837508d5d25b37f99be859e780f6e1ec47947e5`.

# Confirmed context

- Work started from `main` commit `f0b1f38ca84743a4c79851d306ae8d1fdd33176d`.
- No open Analytics PR or active Analytics task overlapped the claimed paths.
- Later `main` changes did not modify the Analytics paths and GitHub reports PR #135 mergeable.
- Local Git commands remain unavailable because the sandbox cannot resolve GitHub; GitHub connector state and Actions are authoritative.

# Existing work reused

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Gameplay Analytics wrapper layers | Added one final correctness wrapper | `data-otservbr-global/scripts/lib/gameplay_analytics_*.lua` | Preserves core/context/schema/batching/reliability separation. |
| PR #114 aggregation fixes | Extended retention and dashboard semantics | maintenance script, views, MariaDB tests | Reuses rolling rebuild, party separation and shared-EXP caps. |
| Existing focused validators | Added explicit contracts and regression tests | `tools/analytics/validate_*` | Matches repository test conventions. |

# Implementation summary

- Added `gameplay_analytics_correctness.lua` after reliability to enforce UTC rollover, combat/death persistence eligibility, non-combat expiry and short death/rollover retention.
- Added lifecycle health counters to `/analytics status`.
- Removed the unused runtime `levelBrackets` option and added validated maintenance `LEVEL_BRACKETS` with explicit bucket semantics.
- Guarded integrated rune supply events with `REMOVE_RUNE_CHARGES`.
- Made Grafana series identities include vocation, bracket, hunt and server version; aligned party filters.
- Relabelled persisted dead letters as terminal failure history while preserving a compatibility SQL alias.
- Added Lua, Python, shell and real MariaDB regression coverage plus documentation and agent catalogue updates.

# Work log

## 2026-07-12T10:34:45Z

- Created the task branch and claimed exact Analytics paths.
- Verified no current Analytics PR/task overlap.
- Recorded the local Git/DNS limitation.

## 2026-07-12T10:36:06Z

- Opened draft PR #135.
- Implemented lifecycle, rune, maintenance, reporting and dashboard fixes with focused tests.

## 2026-07-12T10:54:00Z

- First CI pass exposed two documentation-validator mismatches: the reliability document omitted the exact `lastFlushDurationMs` field name, and a dead-letter semantic phrase was split across SQL comment lines.
- Corrected the documentation/contracts without weakening runtime tests.

## 2026-07-12T11:01:00Z

- Verified all workflows at head `4837508d5d25b37f99be859e780f6e1ec47947e5` are complete and successful.
- Verified no unresolved review threads and GitHub reports the PR mergeable.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Add a final runtime correctness wrapper | Minimizes regression surface while preserving existing wrappers and dynamic enqueue behavior. | Not required. |
| Configure level brackets in maintenance | Daily aggregation, not runtime collection, assigns the bracket. | Not required. |
| Report dead letters truthfully instead of inventing replay | Persisted rows have no automatic replay lifecycle. | Not required. |
| Split active sessions at the first event on a later UTC day | Keeps post-midnight metrics out of the previous daily group without storing movement/segment history. | Not required. |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `4837508d5d25b37f99be859e780f6e1ec47947e5` | Gameplay Analytics | passed | validators, Python unit tests, Lua context/batching/reliability/correctness/schema tests, MariaDB schema/persistence/migrations |
| `4837508d5d25b37f99be859e780f6e1ec47947e5` | Gameplay Analytics Retention | passed | validator, shell syntax, systemd validation, MariaDB aggregation/retention lifecycle |
| `4837508d5d25b37f99be859e780f6e1ec47947e5` | Gameplay Analytics Dashboards | passed | JSON/YAML/static validation and MariaDB reporting-view integration |
| `4837508d5d25b37f99be859e780f6e1ec47947e5` | Gameplay Analytics Supply and Loot Telemetry | passed | static/unit/Lua/MariaDB coverage including rune charge guard |
| `4837508d5d25b37f99be859e780f6e1ec47947e5` | Gameplay Analytics Spell Telemetry | passed | static and Lua integration coverage |
| `4837508d5d25b37f99be859e780f6e1ec47947e5` | Gameplay Analytics Hunt Areas | passed | no regression in shared Analytics tooling/docs |
| `4837508d5d25b37f99be859e780f6e1ec47947e5` | General CI | passed | build-scope workflow completed successfully; non-applicable matrix jobs skipped by path scope |
| current task | Local checks | unavailable | No DNS-capable checkout in sandbox; no result claimed. |

# Risks and compatibility

- Runtime wrapper order is enforced by static and Lua regression tests.
- No protocol, client or cross-repository change.
- `LEVEL_BRACKETS` changes daily dimensions; deployment must record a new `CANARY_SERVER_VERSION` and rebuild while raw rows remain.
- `pending_dead_letters` remains a compatibility alias, while the shipped dashboard uses `dead_letter_records`.
- Rollback: disable Analytics, revert #135, restore the prior maintenance environment and rebuild recent aggregates before enabling raw deletion.

# Remaining work

1. Mark PR #135 ready.
2. Squash-merge after rechecking the current head and merge gate.
3. Archive this task record after merge.

# Handoff

Read PR #135, this task and the focused Analytics docs before changing lifecycle or aggregation semantics. Do not bypass the wrapper stack, duplicate `LEVEL_BRACKETS` in runtime config, or interpret persisted dead-letter rows as an active retry queue.

# Completion

- Final status: ready to merge
- PR: #135
- Merge commit: pending
- Catalogue updated: yes
- Changelog updated: yes
- Archived at: pending after merge
