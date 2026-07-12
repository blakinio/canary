---
task_id: CAN-20260712-analytics-data-correctness
coordination_id: ""
status: in-progress
agent: "GPT-5.6 Thinking"
branch: fix/analytics-data-correctness
base_branch: main
created: 2026-07-12T10:34:45Z
updated: 2026-07-12T10:34:45Z
last_verified_commit: "f0b1f38ca84743a4c79851d306ae8d1fdd33176d"
risk: medium
related_issue: ""
related_pr: ""
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

- [ ] Mana/supply/spell-only sessions expire and are not persisted as hunt sessions without combat or death.
- [ ] Death sessions persist even when shorter than `minimumSessionSeconds`.
- [ ] Sessions roll over at a UTC day boundary before recording the first event of the new day.
- [ ] Rune supply cost is recorded only when rune charges are actually removed.
- [ ] Maintenance uses validated configurable level-bracket boundaries rather than ignoring the Lua list.
- [ ] Grafana series include every grouping dimension and use consistent hunt/server filters.
- [ ] Persisted dead-letter rows are labelled as terminal records, not an active retry queue.
- [ ] Focused Lua, Python, shell and MariaDB regression coverage is added and passes in CI.
- [ ] Module catalogue and changelog are updated.
- [ ] Cross-repository impact is none.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- Current verified `main`: `f0b1f38ca84743a4c79851d306ae8d1fdd33176d`.
- No open PR matching Gameplay Analytics was found before branch creation.
- `docs/agents/ACTIVE_WORK.md` contains no overlapping Analytics task.
- Existing Analytics implementation is disabled by default and already has schema, batching, reliability, retention, dashboard and MariaDB tests.
- Local Git worktree/remote commands are unavailable because this session has GitHub connector access but no DNS-capable repository checkout; GitHub branch/ref state is authoritative.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Gameplay Analytics wrapper layers | Extend with a final correctness wrapper | `data-otservbr-global/scripts/lib/gameplay_analytics_*.lua` | Preserves existing core/context/schema/batching/reliability separation. |
| PR #114 aggregation fixes | Extend existing retention and dashboard semantics | maintenance script, views, MariaDB tests | Already owns rolling rebuild, party separation and shared-EXP caps. |
| Existing focused validators | Add explicit contracts instead of weakening checks | `tools/analytics/validate_*` | Matches repository test conventions. |

# Ownership and overlap check

- Open PRs inspected: repository-wide list and Analytics search; no Analytics overlap.
- Active tasks inspected: `docs/agents/ACTIVE_WORK.md`.
- Overlaps: none in claimed Analytics paths; PR #132 only affects `.github/workflows/ci.yml`.
- Resolution: use a dedicated branch and avoid `.github/workflows/ci.yml`.

# Current state

Verified defects affect session lifecycle, short-death retention, rune supply accounting, level-bracket configuration, daily rollover, Grafana series identity/filtering and dead-letter naming.

# Plan

1. Add focused regression tests and a final runtime correctness wrapper.
2. Move level-bracket ownership to validated maintenance configuration and test generated SQL behavior.
3. Correct rune supply guards, reporting views and dashboard queries.
4. Update validators, workflows, docs, catalogue and changelog.
5. Review the full diff, inspect CI, repair failures, then merge only if all gates pass.

# Work log

## 2026-07-12T10:34:45Z

- Changed: created task branch and claimed exact Analytics paths.
- Learned: no current Analytics PR or active-task overlap exists.
- Failed/blocked: local git status/build commands unavailable because the sandbox cannot resolve GitHub; repository writes and CI remain available through the GitHub connector.
- Result: implementation may proceed on `fix/analytics-data-correctness`.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Add a final runtime correctness wrapper instead of rewriting the core | Existing layer composition is stable and wrapper overrides can preserve all current public functions while minimizing regression surface. | Not required; task-local implementation choice. |
| Configure level brackets in maintenance, not Lua runtime | Brackets are assigned only during external daily aggregation; keeping a runtime-only list is misleading. | Not required; documented environment contract. |
| Rename dead-letter reporting semantics instead of inventing automatic replay | Persisted rows are terminal failure records today; adding replay needs a separate product/data lifecycle design. | Not required. |

# Files and interfaces

| Path/interface/config/schema | Purpose | Status |
|---|---|---|
| `gameplay_analytics_correctness.lua` | Lifecycle, rollover and persistence eligibility | planned |
| `LEVEL_BRACKETS` | Strict ascending maintenance aggregation boundaries | planned |
| rune scripts | Respect `REMOVE_RUNE_CHARGES` | planned |
| reporting view/dashboard | Unique series and truthful dead-letter labels | planned |
| focused tests/validators/workflows | Regression coverage | planned |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| | Focused local checks | not-run | No repository checkout in sandbox. |
| | GitHub Gameplay Analytics workflows | not-run | Will inspect on PR head. |

Never write `passed` without verification.

# Failed approaches and dead ends

- Direct `git clone`/`git ls-remote` is unavailable because the container cannot resolve `github.com`; use GitHub connector writes and GitHub Actions.

# Risks and compatibility

- Runtime: wrapper order must preserve context, schema, batching and reliability behavior.
- Data/migration: level-bracket defaults change from implicit 100-level buckets to the previously advertised explicit boundaries; deployment should use a new `CANARY_SERVER_VERSION` for before/after comparison.
- Security: no secrets or new identity dimensions.
- Backward compatibility: no protocol/client change; reporting view keeps compatibility aliases where practical.
- Cross-repo rollout: none.
- Rollback: disable Analytics, revert the PR, restore previous maintenance environment and rebuild recent aggregates while raw rows remain.

# Remaining work

1. Publish the early task index update and open a draft PR.
2. Implement focused fixes and tests.

# Handoff

## Start here

Read this task, current PR diff and all Analytics focused docs before changing wrapper order or aggregation semantics.

## Do not repeat

Do not create a second Analytics core or bypass existing batching/reliability/schema layers.

## Required reads

- `AGENTS.md`
- `docs/agents/ACTIVE_WORK.md`
- `docs/agents/MODULE_CATALOG.md`
- `docs/systems/gameplay-analytics-agent-handoff.md`
- current Analytics source/tests/docs

## Open questions

- None blocking implementation.

# Completion

- Final status: in progress
- PR:
- Merge commit:
- Catalogue updated: pending
- Changelog updated: pending
- Archived at:
