---
task_id: CAN-20260712-achievement-trigger-names
status: active
agent: "GPT-5.6 Thinking"
branch: fix/achievement-trigger-names
base_branch: main
created: 2026-07-12T19:47:00Z
updated: 2026-07-12T19:47:00Z
last_verified_commit: "6240b6670fab8a62b2d64eff522cec3de513072d"
risk: low
related_issue: ""
related_pr: ""
depends_on:
  - "merged achievement audit PR #165"
  - "merged achievement helper PR #176"
  - "post-merge cleanup PR #182"
blocks: []
owned_paths:
  - data/scripts/actions/items/usable_phantasmal_jade_items.lua
  - data-otservbr-global/scripts/quests/hero_of_rathleton/actions_reward.lua
  - tools/ai-agent/test_achievement_validation.py
  - docs/ai-agent/ACHIEVEMENT_TRIGGER_FIX.md
  - docs/agents/tasks/active/CAN-20260712-achievement-trigger-names.md
  - docs/agents/ACTIVE_WORK.md
  - docs/agents/CHANGELOG.md
modules_touched:
  - achievement gameplay triggers
reuses:
  - merged achievement validation audit (#165)
  - sparse-safe helper repair (#176)
  - achievement validation scanner and tests
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Correct two active literal achievement award names so exact case-sensitive runtime lookup resolves the canonical registry entries, without renaming definitions or changing quest/mount progression.

# Acceptance criteria

- [ ] Phantasmal jade completion awards canonical ID 514 name `You Got Horse Power`.
- [ ] Hero of Rathleton reward awards canonical ID 360 name `The Professor's Nut`.
- [ ] Existing companion rewards, mount, storage and item behavior remain unchanged.
- [ ] Focused real-source contract test proves all static achievement references in both files resolve.
- [ ] Full Achievement Validation reports zero unknown static achievement references.
- [ ] AI Agent Tools, Lua tests, formatter, datapack smoke and required CI pass on the reviewed head.
- [ ] No registry definition/name, player KV, C++, map, asset, database or production configuration change.
- [ ] Update durable fix documentation and agent changelog.
- [ ] Refresh branch after PR #182 merges and review exact changed-file list.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- C++ stores achievement names in `std::map<std::string, uint16_t>` and performs exact `find(name)`.
- `You got Horse Power` does not resolve canonical `You Got Horse Power` (ID 514).
- `The Professors Nut` does not resolve canonical `The Professor's Nut` (ID 360).
- Unlocked achievement KV is keyed by canonical name; definitions must not be renamed to accommodate broken call sites.
- The merged helper repair #176 removed all helper defect findings.
- The remaining static audit errors are exactly these two trigger names.

# Existing work to reuse

| Module/task | Reuse | Evidence/path |
|---|---|---|
| Achievement validation audit #165 | Exact findings, source paths and case-sensitive lookup evidence | `docs/ai-agent/ACHIEVEMENT_VALIDATION_REPORT.md` |
| Achievement scanner | Parse registry and resolve literal references | `tools/ai-agent/achievement_validation.py` |
| Existing focused tests | Fixture and real-source test conventions | `tools/ai-agent/test_achievement_validation.py` |

# Ownership and overlap check

- Open PR state was inspected before branch creation.
- No open PR owns either gameplay file or the achievement validation test.
- PR #182 owns only archival/index cleanup; this branch is stacked on it to avoid shared `ACTIVE_WORK.md` conflicts.
- Resolution: do not merge before #182; refresh against current `main` after it lands.

# Plan

1. Replace only the two literal strings with canonical names.
2. Add a real-source contract test resolving all static references in those files.
3. Run the complete achievement artifact and inspect `unknownStaticReferenceCount`.
4. Run formatter, Lua/datapack smoke and full required CI.
5. Update documentation/task and merge after dependency and all gates pass.

# Work log

## 2026-07-12T19:47:00Z

- Changed: created a dedicated stacked branch and task for the two confirmed trigger failures.
- Learned: both fixes are call-site corrections; registry renames would introduce unnecessary KV compatibility risk.
- Blocked: merge waits for documentation cleanup PR #182.
- Result: exact ownership and acceptance criteria recorded before gameplay edits.

# Decisions

| Decision | Reason/evidence |
|---|---|
| Correct call sites to canonical names | C++ lookup is exact and canonical definitions are persistence keys. |
| Keep both typo corrections in one PR | They are the complete bounded set of identical static-name resolution failures from one audit. |
| Add a real-source scanner contract | Prevents case/apostrophe regressions and verifies all static refs in both touched files. |
| Do not alter award timing/progression | Audit confirmed only name resolution, not quest/mount flow defects. |

# Validation and CI

| Commit | Check | Result | Notes |
|---|---|---|---|
| | focused Python contract | not-run | implementation pending |
| | Achievement Validation | not-run | implementation pending |
| | required CI | not-run | implementation pending |

Never write `passed` without verification.

# Risks and compatibility

- Runtime: two previously ineffective award calls begin resolving and awarding existing canonical achievements.
- Persistence: no format or canonical name change.
- Duplicate awards: existing C++/Player API idempotence remains authoritative.
- Rollback: revert the focused PR; no data migration required.

# Remaining work

1. Implement both exact-string corrections and test.
2. Publish draft PR and register it in Active Work.
3. Inspect artifact and complete all CI gates.
4. Merge and archive task separately.

# Handoff

## Start here

Read this task, merged audit report and the two owned Lua files.

## Do not repeat

- Do not rename registry definitions.
- Do not change storage `24850`, item rewards, mount ID `167` or required item counts.
- Do not mix missing achievement definitions/content into this PR.
- Do not weaken the scanner to hide unknown references.

# Completion

- Final status: active
- PR:
- Merge commit:
- Changelog updated: pending
- Archived at:
