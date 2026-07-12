---
task_id: CAN-20260712-achievement-helper-fix
coordination_id: ""
status: active
agent: "GPT-5.6 Thinking"
branch: fix/achievement-helper-enumeration
base_branch: main
created: 2026-07-12T18:15:00Z
updated: 2026-07-12T18:44:00Z
last_verified_commit: "576989a0a5f69844d843347ce7e2e3789dbaee71"
risk: medium
related_issue: ""
related_pr: "#176"
depends_on:
  - "merged audit PR #165"
  - "merged cleanup PR #175"
blocks: []
owned_paths:
  - data/scripts/lib/register_achievements.lua
  - tests/lua/test_achievement_helpers.lua
  - docs/ai-agent/ACHIEVEMENT_HELPER_FIX.md
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

- [x] Build a deterministic sorted list of valid registered numeric achievement IDs.
- [x] Derive `ACHIEVEMENT_FIRST` and `ACHIEVEMENT_LAST` from explicit IDs instead of Lua's sparse-table length operator.
- [x] Use the explicit ID list for all bulk/enumeration helpers.
- [x] Return resolved metadata from `Game.isAchievementSecret`.
- [x] Invalid ID/name returns false and logs the supplied identifier without a secondary Lua error.
- [x] Preserve existing registry definitions and player KV compatibility.
- [x] Add focused Lua tests covering gaps, highest ID, deterministic enumeration, bulk add/remove, public/secret filtering and invalid lookup.
- [x] Merged audit reports no achievement-helper defect findings.
- [ ] Lua test suite and datapack smoke pass on the final reviewed head.
- [ ] Full required CI passes on the final reviewed head.
- [x] No unrelated gameplay, C++, map, asset or database change.
- [x] Update durable achievement repair documentation and agent changelog.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- The registry has 541 definitions in ID range `1..570` with 29 gaps.
- `#ACHIEVEMENTS` is not a valid boundary for a sparse Lua table.
- Registration previously used `pairs`, while `Player.getAchievements` used `1..#ACHIEVEMENTS`, so helper enumeration could diverge from registered runtime data.
- `Game.isAchievementSecret` resolved `foundAchievement` but returned `achievement.secret` from the input argument.
- Its invalid path formatted an error with undefined variable `ach`.
- `Spdlog` is deprecated compatibility API; the repair uses modern `logger.error`.
- No registry rename is permitted because unlocked KV is keyed by achievement name.

# Existing work to reuse

| Module/task | Reuse | Evidence/path |
|---|---|---|
| Achievement validation audit #165 | Confirmed findings and CI scanner | `tools/ai-agent/achievement_validation.py`, evidence report |
| Lua test harness | Minimal pcall/assert runner | `tests/lua/test_npc_messaging.lua` |
| Current registry helper | Preserve public API and defaults | `data/scripts/lib/register_achievements.lua` |

# Ownership and overlap check

- Open PRs were inspected before branch creation.
- Cleanup PR #175 has merged and the branch was refreshed against merge commit `ab0ca005625ca4f80fc5931d86a3f8d0b0304299`.
- No open PR changes `register_achievements.lua` or the focused helper test.
- The two broken literal trigger names remain explicitly outside this PR.

# Current state

The helper implementation and focused real-source Lua test are committed. The post-change achievement audit contains no helper defect findings. Full Lua/runtime CI remains pending because the PR is still draft.

# Implemented behavior

1. Collect numeric registry keys and sort ascending.
2. Validate/register definitions in deterministic order.
3. Retain only successfully registered IDs for helper enumeration.
4. Derive first/last constants from the retained list.
5. Reuse the list for unlocked, bulk, public and secret helper methods.
6. Resolve secret metadata from the found achievement.
7. Log invalid ID/name with `logger.error` and return false.

# Work log

## 2026-07-12T18:44:00Z

- Changed: added focused repair documentation, changelog entry and refreshed Active Work after #175 merged.
- Learned: the post-change audit has only the two unrelated static trigger errors; all three helper findings are gone.
- Validation: Achievement Validation run `29204015123` succeeded on implementation head `b084331b8ae393e8159f7b0eaddfd6f2ed691408`; artifact `8263206451` was downloaded and inspected.
- Failed/blocked: CI Lua/build jobs were skipped while the PR remained draft.
- Result: implementation is ready for full runtime-facing CI after final documentation update.

## 2026-07-12T18:28:00Z

- Changed: applied the bounded helper patch and created `tests/lua/test_achievement_helpers.lua`; removed the temporary source-export workflow from the branch.
- Learned: generated test indentation required a follow-up correction before CI.
- Result: production helper and corrected test are now on a clean current-main branch.

## 2026-07-12T18:15:00Z

- Changed: created dedicated helper-fix branch, task record and draft PR #176.
- Result: exact scope and ownership recorded before implementation.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Use a sorted local ID list captured by helper closures | Handles gaps, provides deterministic output and avoids a second global registry. | none |
| Include only successfully validated/registered definitions | Helper enumeration must match runtime registration rather than invalid source entries. | none |
| Keep canonical definitions and KV names unchanged | Prevents persistence compatibility risk. | none |
| Use modern `logger.error` and explicit `return false` | Avoids deprecated API and ambiguous return-value chaining. | none |
| Keep trigger typo fixes separate | Audit/fix boundaries require one logical behavior change per PR. | none |

# Files and interfaces

| Path/interface/config/schema | Purpose | Status |
|---|---|---|
| `data/scripts/lib/register_achievements.lua` | sparse-safe registration/enumeration and secret helper | implemented |
| `tests/lua/test_achievement_helpers.lua` | real-source helper behavior contract | implemented |
| `docs/ai-agent/ACHIEVEMENT_HELPER_FIX.md` | durable remediation behavior and rollback | implemented |
| task/changelog/Active Work | coordination and discovery | current |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `b084331b8ae393e8159f7b0eaddfd6f2ed691408` | Achievement Validation run `29204015123` | passed | no helper finding codes in artifact |
| same | artifact `8263206451` | inspected | two unrelated static trigger errors remain |
| final head | Lua Tests | not-run | PR still draft |
| final head | Linux datapack smoke | not-run | PR still draft |
| final head | required CI | not-run | PR still draft |

Never write `passed` without verification.

# Failed approaches and dead ends

- The repository file is too large for a safe full replacement through the truncated text connector.
- A temporary one-run workflow exported and then applied a bounded marker-checked patch; it removed itself before final review.
- The generated test initially contained literal `\\t` sequences; the file was corrected before full CI.

# Risks and compatibility

- Runtime: helper enumeration changes from undefined sparse behavior to deterministic ascending registered IDs.
- Data/migration: none; IDs, names, points and KV keys remain unchanged.
- Security: none.
- Backward compatibility: public helper signatures remain unchanged; ordering becomes deterministic ascending ID.
- Cross-repo rollout: none.
- Rollback: revert PR #176; no data cleanup required.

# Remaining work

1. Mark PR ready to run Lua tests, datapack smoke and full required CI.
2. Inspect formatter output, full diff and exact changed-file list.
3. Update PR/task with final head and checks.
4. Merge only after all gates pass, then archive the task in a follow-up docs cleanup.

# Handoff

## Start here

Read `docs/ai-agent/ACHIEVEMENT_HELPER_FIX.md`, this task and PR #176.

## Do not repeat

- Do not use `#ACHIEVEMENTS`.
- Do not rename definitions.
- Do not combine the two broken trigger-name fixes with this helper PR.
- Do not infer gameplay reachability from helper enumeration.

## Required reads

- `AGENTS.md`
- `docs/agents/ACTIVE_WORK.md`
- `docs/ai-agent/ACHIEVEMENT_VALIDATION_REPORT.md`
- `docs/ai-agent/ACHIEVEMENT_HELPER_FIX.md`
- `data/scripts/lib/register_achievements.lua`
- `tests/lua/test_achievement_helpers.lua`

## Open questions

- None for the bounded helper repair.

# Completion

- Final status: active
- PR: #176
- Merge commit:
- Catalogue updated: not required; no new reusable module
- Changelog updated: yes
- Archived at:
