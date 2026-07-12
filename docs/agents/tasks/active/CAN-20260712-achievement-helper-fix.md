---
task_id: CAN-20260712-achievement-helper-fix
coordination_id: ""
status: active
agent: "GPT-5.6 Thinking"
branch: fix/achievement-helper-enumeration
base_branch: main
created: 2026-07-12T18:15:00Z
updated: 2026-07-12T18:15:00Z
last_verified_commit: "55543011493b490e418f002f217140b5d2b12bb1"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - "PR #175 post-merge task archival"
  - "merged audit PR #165"
blocks: []
owned_paths:
  - data/scripts/lib/register_achievements.lua
  - tests/lua/test_achievement_helpers.lua
  - docs/ai-agent/OTS_AI_ACHIEVEMENT_VALIDATION_PROJECT.md
  - docs/agents/tasks/active/CAN-20260712-achievement-helper-fix.md
  - docs/agents/ACTIVE_WORK.md
  - docs/agents/CHANGELOG.md
modules_touched:
  - achievement Lua helper layer
reuses:
  - merged achievement validation audit (#165)
  - existing Lua test harness conventions
public_interfaces:
  - ACHIEVEMENT_FIRST
  - ACHIEVEMENT_LAST
  - Game.isAchievementSecret
  - Player.getAchievements
  - Player.addAllAchievements
  - Player.removeAllAchievements
  - Player.getSecretAchievements
  - Player.getPublicAchievements
cross_repo_tasks: []
---

# Goal

Make achievement enumeration safe for the sparse registry and repair secret-metadata lookup without changing any achievement definition, ID, name, points, trigger or player KV format.

# Acceptance criteria

- [ ] Build a deterministic sorted list of valid registered numeric achievement IDs.
- [ ] Derive `ACHIEVEMENT_FIRST` and `ACHIEVEMENT_LAST` from explicit IDs instead of Lua's sparse-table length operator.
- [ ] Use the explicit ID list for all bulk/enumeration helpers.
- [ ] Return resolved metadata from `Game.isAchievementSecret`.
- [ ] Invalid ID/name returns false and logs the supplied identifier without a secondary Lua error.
- [ ] Preserve existing registry definitions and player KV compatibility.
- [ ] Add focused Lua tests covering gaps, highest ID, deterministic enumeration, bulk add/remove, public/secret filtering and invalid lookup.
- [ ] Merged audit reports no achievement-helper defect findings.
- [ ] Datapack smoke and required CI pass on the reviewed head.
- [ ] No unrelated gameplay, C++, map, asset or database change.
- [ ] Update durable achievement project documentation and agent changelog.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- The registry has 541 definitions in ID range `1..570` with 29 gaps.
- `#ACHIEVEMENTS` is not a valid boundary for a sparse Lua table.
- Registration currently uses `pairs`, while `Player.getAchievements` uses `1..#ACHIEVEMENTS`, so helper enumeration can diverge from registered runtime data.
- `Game.isAchievementSecret` resolves `foundAchievement` but returns `achievement.secret` from the input argument.
- Its invalid path formats the error with undefined variable `ach`.
- `Spdlog` exists only as a deprecated compatibility API; modern `logger.error` is available.
- No registry rename is permitted because unlocked KV is keyed by achievement name.

# Existing work to reuse

| Module/task | Reuse | Evidence/path |
|---|---|---|
| Achievement validation audit #165 | Confirmed findings and CI scanner | `tools/ai-agent/achievement_validation.py`, evidence report |
| Lua test harness | Minimal pcall/assert runner | `tests/lua/test_npc_messaging.lua` |
| Current registry helper | Preserve public API and defaults | `data/scripts/lib/register_achievements.lua` |

# Ownership and overlap check

- Open PRs inspected before branch creation.
- PR #175 owns only post-merge task archival/index cleanup and is an explicit stack dependency.
- No open PR changes `register_achievements.lua` or achievement helper tests.
- Resolution: dedicated stacked branch; do not merge before #175.

# Current state

The merged audit identifies three helper defects. No runtime behavior has been changed yet on this branch.

# Plan

1. Replace sparse length/range logic with a sorted explicit numeric-ID list.
2. Repair secret lookup/error handling.
3. Add a focused real-source Lua helper test.
4. Run audit, Lua tests, datapack smoke and full required CI.
5. Update handoff/changelog and merge only after #175 and all gates pass.

# Work log

## 2026-07-12T18:15:00Z

- Changed: created dedicated helper-fix branch and task record stacked on post-audit cleanup.
- Learned: all affected helper APIs can share one local sorted registered-ID list without changing public signatures or persistence.
- Failed/blocked: merge is held until PR #175 lands.
- Result: exact scope and ownership recorded before implementation.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Use a sorted local ID list captured by helper closures | Handles gaps, provides deterministic output and avoids a second global registry. | none |
| Include only successfully validated/registered definitions | Helper enumeration must match runtime registration rather than invalid source entries. | none |
| Keep canonical definitions and KV names unchanged | Prevents persistence compatibility risk. | none |
| Use modern `logger.error` and explicit `return false` | Avoids deprecated API and ambiguous return-value chaining. | none |

# Files and interfaces

| Path/interface/config/schema | Purpose | Status |
|---|---|---|
| `data/scripts/lib/register_achievements.lua` | sparse-safe registration/enumeration and secret helper | planned |
| `tests/lua/test_achievement_helpers.lua` | real-source helper behavior contract | planned |
| achievement project/changelog/task docs | remediation status and handoff | planned |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| | `luajit tests/lua/test_achievement_helpers.lua` | not-run | implementation pending |
| | Achievement Validation | not-run | implementation pending |
| | CI / Lua Tests / datapack smoke | not-run | implementation pending |

Never write `passed` without verification.

# Failed approaches and dead ends

# Risks and compatibility

- Runtime: helper enumeration and secret lookup behavior changes from broken/undefined to deterministic.
- Data/migration: none; IDs, names and KV keys remain unchanged.
- Security: none.
- Backward compatibility: public helper signatures remain unchanged; output order becomes deterministic ascending ID.
- Cross-repo rollout: none.
- Rollback: revert the focused PR.

# Remaining work

1. Implement helper changes and tests.
2. Publish draft PR after Active Work update.
3. Validate after PR #175 merges and rebase/merge current `main` if needed.

# Handoff

## Start here

Read merged audit report and this task, then inspect only the owned helper/test paths.

## Do not repeat

- Do not use `#ACHIEVEMENTS`.
- Do not rename definitions.
- Do not combine the two broken trigger-name fixes with this helper PR.
- Do not infer gameplay reachability from helper enumeration.

## Required reads

- `AGENTS.md`
- `docs/agents/ACTIVE_WORK.md`
- `docs/ai-agent/ACHIEVEMENT_VALIDATION_REPORT.md`
- `docs/ai-agent/OTS_AI_ACHIEVEMENT_VALIDATION_PROJECT.md`
- `data/scripts/lib/register_achievements.lua`

## Open questions

- None for the bounded helper repair.

# Completion

- Final status: active
- PR:
- Merge commit:
- Catalogue updated: not required; no new reusable module
- Changelog updated: pending
- Archived at:
