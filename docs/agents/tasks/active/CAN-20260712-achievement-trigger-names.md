---
task_id: CAN-20260712-achievement-trigger-names
status: ready-for-review
agent: "GPT-5.6 Thinking"
branch: fix/achievement-trigger-names
base_branch: main
created: 2026-07-12T19:47:00Z
updated: 2026-07-12T19:55:00Z
last_verified_commit: "fbb5a3360f8502c645d3fb520ccecad6895c707a"
risk: low
related_issue: ""
related_pr: "#184"
depends_on:
  - "merged achievement audit PR #165"
  - "merged achievement helper PR #176"
  - "merged post-helper cleanup PR #182"
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

- [x] Phantasmal jade completion uses canonical ID 514 name `You Got Horse Power`.
- [x] Hero of Rathleton reward uses canonical ID 360 name `The Professor's Nut`.
- [x] Existing companion rewards, mount, storage and item behavior remain unchanged.
- [x] Focused real-source contract proves all static achievement references in both files resolve.
- [x] Full Achievement Validation reports zero unknown static achievement references.
- [x] No registry definition/name, player KV, C++, map, asset, database or production configuration change.
- [x] Durable fix documentation and agent changelog updated.
- [x] Branch refreshed after PR #182 merged; cleanup-only paths removed from the diff.
- [ ] Formatter, Lua tests, datapack smoke and required CI pass on the final ready head.
- [ ] Exact final changed-file list and review threads checked.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- C++ stores achievement names in `std::map<std::string, uint16_t>` and performs exact `find(name)`.
- `You got Horse Power` did not resolve canonical `You Got Horse Power` (ID 514).
- `The Professors Nut` did not resolve canonical `The Professor's Nut` (ID 360).
- Unlocked achievement KV is keyed by canonical name; call sites were corrected instead of renaming definitions.
- Merged helper repair #176 removed all helper defect findings.

# Ownership and overlap

- Open PR state was inspected before implementation.
- No open PR owns either gameplay file or the achievement validation test.
- Cleanup PR #182 merged as `26792fb9c6f680e3d2c6dd2821bf2e9770f5c3b5`.
- Branch was refreshed on current `main` commit `9441d984ecd127b16542622d6fdb72d4878b583b` without overwriting unrelated instance work.

# Implemented behavior

1. Corrected phantasmal jade award literal to `You Got Horse Power`.
2. Corrected Hero of Rathleton award literal to `The Professor's Nut`.
3. Added a real-source test that loads the active registry, scans both files and asserts all their static references resolve.
4. Added durable behavior, compatibility and rollback documentation.

# Validation and CI

Draft evidence head:

```text
2985e2ad3c9d09210cc6c4ab892126e7506b4dc2
```

Verified:

- Achievement Validation run `29206575804`: success;
- AI Agent Tools run `29206575806`: success;
- Account Quests run `29206575838`: success;
- audit artifact `8263916548`, SHA-256 `770483ddc3863818206d214e980144a9a56dfefc62c06b2fbafdd98dfe40ce7c`;
- artifact parsed: `ok=true`, `unknownStaticReferenceCount=0`, 160 resolved static references, no error findings;
- remaining warning is only the known external reference-baseline mismatch.

Final ready-head CI is pending after this task update.

# Work log

## 2026-07-12T19:55:00Z

- Changed: refreshed the branch after #182 and current instance commits; only seven intended paths remain relative to that reviewed base.
- Learned: fixing the two names raises direct static awards from 87 to 89 and removes every unknown static achievement reference.
- Validation: downloaded and parsed the full achievement artifact; zero errors remain.
- Result: implementation is ready for full non-draft CI and final diff review.

## 2026-07-12T19:50:00Z

- Changed: corrected both literal names, added the real-source scanner contract, fix documentation, changelog and Active Work entry.
- Result: draft focused workflows passed.

## 2026-07-12T19:47:00Z

- Changed: created dedicated stacked branch and task.
- Decision: repair call sites, not canonical registry/persistence names.

# Decisions

| Decision | Reason/evidence |
|---|---|
| Correct call sites to canonical names | Exact C++ lookup and name-keyed persistence make registry renames unsafe and unnecessary. |
| Keep both corrections in one PR | They are the complete bounded set of the same confirmed static-name failure. |
| Add a real-source scanner contract | Prevents case/punctuation regressions without duplicating runtime implementation. |
| Preserve progression and rewards | Audit established name-resolution defects only. |

# Risks and compatibility

- Runtime: two previously ineffective award calls now resolve existing achievements.
- Persistence: no format or canonical key change.
- Duplicate awards: existing Player API idempotence remains authoritative.
- Rollback: revert PR #184; no migration required.

# Remaining work

1. Mark PR #184 ready and run full CI/datapack gates.
2. Review final seven-file diff and review threads.
3. Merge after all checks pass.
4. Archive this task in a documentation-only follow-up.

# Handoff

Read `docs/ai-agent/ACHIEVEMENT_TRIGGER_FIX.md`, this task and PR #184.

Do not rename registry definitions, change storage `24850`, reward items, mount `167`, item requirements, or mix missing definitions/content into this PR.

# Completion

- Final status: ready-for-review
- PR: #184
- Merge commit:
- Changelog updated: yes
- Archived at:
