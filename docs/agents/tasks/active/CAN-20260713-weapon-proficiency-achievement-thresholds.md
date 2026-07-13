---
task_id: CAN-20260713-weapon-proficiency-achievement-thresholds
status: active
agent: "GPT-5.6 Thinking"
branch: fix/weapon-proficiency-achievement-thresholds
base_branch: main
created: 2026-07-13T18:00:00+02:00
updated: 2026-07-13T18:00:00+02:00
last_verified_commit: ""
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - "merged comprehensive achievement audit #238"
  - "merged Weapon Proficiency audit #195"
  - "merged mastery-state/count API fix #212"
blocks:
  - "Weapon Proficiency secret achievement 567 implementation"
owned_paths:
  - src/creatures/players/components/weapon_proficiency.hpp
  - src/creatures/players/components/weapon_proficiency.cpp
  - tests/unit/players/components/weapon_proficiency_test.cpp
  - data/scripts/lib/register_achievements.lua
  - tools/ai-agent/weapon_proficiency_achievement_audit.py
  - tools/ai-agent/test_weapon_proficiency_achievement_audit.py
  - docs/ai-agent/WEAPON_PROFICIENCY_ACHIEVEMENT_REPORT.md
  - docs/ai-agent/WEAPON_PROFICIENCY_ACHIEVEMENT_RUNTIME_PLAN.json
  - docs/agents/tasks/active/CAN-20260713-weapon-proficiency-achievement-thresholds.md
modules_touched:
  - WeaponProficiency runtime
  - achievement award path
reuses:
  - WeaponProficiency::getMasteredWeaponCount()
  - PlayerAchievement::add(uint16_t, ...)
  - weapon proficiency audit and focused tests
public_interfaces: []
cross_repo_tasks: []
---

# Goal and exact scope

Implement evidence-backed runtime awards for Weapon Proficiency achievement IDs 564, 565 and 566 at mastered-weapon thresholds 1, 10 and 50.

ID 567 `The Forbidden Build` is explicitly excluded from this PR because its twelve-item condition, definition and backfill require a separate focused change.

# Acceptance criteria

- [ ] Reconfirm current registry metadata for IDs 564–566.
- [ ] Award 564 when mastered count first reaches at least 1.
- [ ] Award 565 when mastered count first reaches at least 10.
- [ ] Award 566 when mastered count first reaches at least 50.
- [ ] Award path is idempotent through `PlayerAchievement::add`.
- [ ] No award is emitted below each threshold.
- [ ] A single large transition can award all newly satisfied thresholds.
- [ ] Existing WeaponProficiency serialization and mastery semantics remain unchanged.
- [ ] Existing players with already-mastered weapons receive an explicit, tested backfill path or the PR remains blocked with a documented reason.
- [ ] Focused C++ and audit regression tests pass.
- [ ] Full current-head CI passes before merge.
- [ ] No ID 567 definition or condition is added.

# Sources and evidence

- `docs/ai-agent/WEAPON_PROFICIENCY_ACHIEVEMENT_REPORT.md`, read 2026-07-13.
- `docs/ai-agent/WEAPON_PROFICIENCY_ACHIEVEMENT_RUNTIME_PLAN.json`, read 2026-07-13.
- comprehensive achievement audit #238, merged 2026-07-13.
- Weapon Proficiency audit #195 and runtime fix #212.
- current `main` source and open PR state, checked 2026-07-13.

# Confirmed findings

- IDs 564–566 are defined in Canary.
- Reviewed thresholds are 1, 10 and 50 mastered weapons.
- No active award hook existed in the reviewed audit.
- `getMasteredWeaponCount()` and correct first-entry mastery state already exist.
- `PlayerAchievement::add` is the canonical idempotent award API.
- No open PR currently owns this exact scope.

# Uncertain findings requiring proof

- Best lifecycle point for existing-player backfill without repeated expensive scans.
- Whether load normalization should trigger achievement reconciliation directly or through login initialization.
- Exact negative-path behavior when proficiency metadata is missing or max experience is zero.

# Plan

1. Inspect current runtime and registry on latest `main`.
2. Design one canonical reconciliation helper for thresholds 564–566.
3. Call it on mastery transitions and one bounded existing-player lifecycle path.
4. Add focused tests for below/exact/crossed thresholds, repeated calls and backfill.
5. Synchronize validator/report/runtime plan.
6. Run full CI and merge only after all gates pass.

# Commands and tests

Pending implementation. Every command/run ID and result will be recorded here.

# Failed approaches

None yet.

# Handoff

- branch: `fix/weapon-proficiency-achievement-thresholds`
- PR: pending
- current status: pre-implementation
- completed: overlap check, scope selection, branch and durable task creation
- not completed: runtime implementation, backfill decision, tests and CI
- blocker: none; backfill lifecycle requires source inspection
- next step: inspect current `WeaponProficiency::addExperience`, load path and `PlayerAchievement::add`, then implement a single reconciliation helper.

# Completion

- Final status: active
- PR:
- Merge commit:
- Archived at:
