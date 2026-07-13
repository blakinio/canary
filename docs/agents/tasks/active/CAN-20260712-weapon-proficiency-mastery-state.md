---
task_id: CAN-20260712-weapon-proficiency-mastery-state
status: ready-for-review
agent: "GPT-5.6 Thinking"
branch: fix/weapon-proficiency-mastery-state
base_branch: main
created: 2026-07-12T21:20:00Z
updated: 2026-07-12T21:20:00Z
last_verified_commit: "5c0c9495bf1f93f15e95b1dd65e744d3c986d9d0"
risk: medium
related_issue: ""
related_pr: "#212"
depends_on:
  - "weapon proficiency achievement audit PR #195"
blocks:
  - "achievement thresholds 564-566 implementation"
  - "secret achievement 567 implementation"
owned_paths:
  - src/creatures/players/components/weapon_proficiency.hpp
  - src/creatures/players/components/weapon_proficiency.cpp
  - tests/unit/players/components/weapon_proficiency_test.cpp
  - tests/unit/players/components/CMakeLists.txt
  - docs/ai-agent/WEAPON_PROFICIENCY_MASTERY_STATE_FIX.md
  - docs/ai-agent/WEAPON_PROFICIENCY_ACHIEVEMENT_REPORT.md
  - tools/ai-agent/weapon_proficiency_achievement_audit.py
  - tools/ai-agent/test_weapon_proficiency_achievement_audit.py
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260712-weapon-proficiency-mastery-state.md
modules_touched:
  - WeaponProficiency runtime
reuses:
  - weapon proficiency audit #195
  - existing Player unit-test constructor and component accessor
public_interfaces:
  - WeaponProficiency::getMasteredWeaponCount
cross_repo_tasks: []
---

# Goal

Correct the first-entry mastery flag and expose one deterministic mastered-weapon count API without awarding achievements or changing persistence format.

# Acceptance criteria

- [x] A first XP gain reaching or exceeding maximum stores capped XP and `mastered=true` before return.
- [x] A first below-maximum gain remains unmastered.
- [x] Existing-entry mastery behavior remains unchanged.
- [x] `getMasteredWeaponCount()` counts only stored entries with normalized `mastered=true`.
- [x] Count is independent of unordered-map iteration order.
- [x] Public API is const, read-only and documented.
- [x] Focused C++ unit tests cover initial mastered/unmastered state and mixed mastered counts.
- [x] No achievement award, registry definition, backfill policy or ID 567 condition is added.
- [x] No player KV key/schema, items, proficiencies, map, assets, database or production configuration change.
- [ ] Linux build, unit tests, formatter and datapack smoke pass on the reviewed head.
- [ ] Branch is refreshed after #195 merges and exact changed-file list is reviewed.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- `addExperience` currently uses `try_emplace(weaponId, std::min(experience, maxExperience))` and returns without setting the new entry's mastered flag.
- Existing entries set `mastered=true` when their new XP reaches maximum.
- Load normalization derives mastery from stored XP, but requiring a relog is incorrect runtime behavior.
- The component exposes sorted tracked weapon IDs but no canonical mastered-count query.
- This task intentionally does not award IDs 564–567.

# Ownership and overlap

- Open PR state was inspected before branch creation.
- No open PR owns the WeaponProficiency C++ component or planned unit test.
- This branch is stacked on read-only audit #195 and must be refreshed after that PR merges.

# Plan

1. Add const `getMasteredWeaponCount()`.
2. Correct initial-entry state construction in `addExperience`.
3. Add focused component unit tests without loading production player data.
4. Run formatter, C++ tests, full build and both datapack smokes.
5. Merge only after #195 and all current-head gates pass.

# Work log

## 2026-07-13T07:00:00Z

- Changed: implemented the initial-state factory, const mastered count, focused C++ tests and synchronized the audit detector.
- Learned: the component CMake target uses `target_sources`; the stale temporary workflow marker was corrected before execution.
- Result: runtime scope is complete; current-head CI and exact diff review remain.

## 2026-07-12T21:20:00Z

- Changed: created a separate runtime-fix task and branch stacked on audit #195.
- Learned: the repair can remain independent of achievement award/backfill behavior.
- Result: exact ownership and compatibility boundary recorded before C++ changes.

# Decisions

| Decision | Reason |
|---|---|
| Expose one canonical count API | Follow-up threshold and secret conditions must not duplicate map iteration. |
| Keep count based on normalized stored flag | `normalizeStoredState` is already the canonical persisted-state repair path. |
| Do not award achievements here | Mastery correctness and award/backfill policy have different risks and test matrices. |
| Preserve KV serialization | The existing `mastered` field remains authoritative and compatible. |

# Validation

| Commit | Check | Result |
|---|---|---|
| | focused C++ tests | not-run |
| | formatter | not-run |
| | Linux build and datapack smoke | not-run |

Never write `passed` without verification.

# Risks and compatibility

- Runtime: fixes immediate mastery state on first capped gain.
- Persistence: no key or serialization change.
- Public API: additive read-only count query.
- Rollback: revert focused PR; no migration required.

# Handoff

Read audit #195, this task and the two WeaponProficiency source files. Do not add achievement awards or ID 567 in this PR.

# Completion

- Final status: ready-for-review
- PR: #212
- Merge commit:
- Changelog updated: pending
- Archived at:
