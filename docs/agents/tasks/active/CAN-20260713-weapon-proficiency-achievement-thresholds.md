---
task_id: CAN-20260713-weapon-proficiency-achievement-thresholds
status: active
agent: "GPT-5.6 Thinking"
branch: fix/weapon-proficiency-achievement-thresholds
base_branch: main
created: 2026-07-13T18:00:00+02:00
updated: 2026-07-13T18:30:00+02:00
last_verified_commit: "ab474562c47b3af87ea8d964f1f75f6d264a86f7"
risk: medium
related_issue: ""
related_pr: "#272"
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
  - tools/ai-agent/weapon_proficiency_achievement_audit.py
  - tools/ai-agent/test_weapon_proficiency_achievement_audit.py
  - docs/ai-agent/ACHIEVEMENT_REVIEWED_EVIDENCE.json
  - docs/ai-agent/WEAPON_PROFICIENCY_ACHIEVEMENT_REPORT.md
  - docs/agents/tasks/active/CAN-20260713-weapon-proficiency-achievement-thresholds.md
modules_touched:
  - WeaponProficiency runtime
  - achievement award path
  - achievement validation evidence
reuses:
  - WeaponProficiency::getMasteredWeaponCount()
  - PlayerAchievement::add(uint16_t, ...)
  - weapon proficiency audit and focused tests
public_interfaces: []
cross_repo_tasks: []
---

# Goal and exact scope

Implement evidence-backed runtime awards for Weapon Proficiency achievement IDs 564, 565 and 566 at mastered-weapon thresholds 1, 10 and 50.

ID 567 `The Forbidden Build` is explicitly excluded because its twelve-item condition, missing definition and historical backfill require a separate focused change.

# Acceptance criteria

- [x] Reconfirm current registry metadata for IDs 564–566.
- [x] Award 564 when mastered count reaches at least 1.
- [x] Award 565 when mastered count reaches at least 10.
- [x] Award 566 when mastered count reaches at least 50.
- [x] Award path is idempotent through `PlayerAchievement::add`.
- [x] No award is emitted below each threshold.
- [x] A single reconciliation can award every newly satisfied threshold.
- [x] Existing WeaponProficiency serialization and mastery semantics remain unchanged.
- [x] Existing players with already-mastered weapons receive login-time reconciliation after achievements are loaded.
- [x] Initial and existing-entry mastery transitions invoke reconciliation only when mastery is newly reached.
- [x] Focused threshold and audit tests pass in materializer runs.
- [x] Dedicated validator recognizes IDs 564–566 as active award paths.
- [x] Comprehensive reviewed evidence changes 564–566 from `handler-missing` to `partially-confirmed`.
- [x] No ID 567 definition or condition is added.
- [ ] Full current-head CI, C++ unit tests and both achievement workflows pass on a user-authored head.
- [ ] Exact changed-file list and review threads checked on final head.
- [ ] Ready/auto-merge gate satisfied.

# Sources and evidence

- `docs/ai-agent/WEAPON_PROFICIENCY_ACHIEVEMENT_REPORT.md`, read 2026-07-13.
- `docs/ai-agent/WEAPON_PROFICIENCY_ACHIEVEMENT_RUNTIME_PLAN.json`, read 2026-07-13.
- comprehensive achievement audit #238, merged 2026-07-13.
- Weapon Proficiency audit #195 and runtime fix #212.
- `src/io/functions/iologindata_load_player.cpp`: achievements load before WeaponProficiency, proving a safe login reconciliation point.
- `src/creatures/players/components/player_achievement.cpp`: `add()` is idempotent and persists canonical unlock name/timestamp and points.
- current open PR state, checked 2026-07-13; no overlapping PR owns this scope.

# Confirmed implementation

- `getMasteryAchievementIds()` maps mastered counts to IDs 564/565/566 at exact thresholds 1/10/50.
- `reconcileMasteryAchievements()` uses `m_player.achiev().add`, preserving canonical idempotency.
- `WeaponProficiency::load()` reconciles with `message=false` after stored states are normalized and after achievement state was loaded by login initialization.
- New entries reconcile when their initial state is already mastered.
- Existing entries reconcile only on a false-to-true mastery transition.
- The helper returns all satisfied IDs, so a large backfill or transition cannot skip lower thresholds.
- ID 567 remains absent and untouched.

# Remaining uncertainty

- Full runtime/E2E with a real client remains unproven; therefore reviewed status is `partially-confirmed`, not `confirmed`.
- The exact user-facing behavior of CipSoft historical backfill messages is not public; this implementation persists silently on login and messages only live mastery transitions.

# Changed files and purpose

| Path | Purpose |
|---|---|
| `src/creatures/players/components/weapon_proficiency.hpp` | private threshold/reconciliation helpers |
| `src/creatures/players/components/weapon_proficiency.cpp` | threshold mapping, live awards and login backfill |
| `tests/unit/players/components/weapon_proficiency_test.cpp` | exact threshold boundary coverage |
| `tools/ai-agent/weapon_proficiency_achievement_audit.py` | detect ID-based runtime award path |
| `tools/ai-agent/test_weapon_proficiency_achievement_audit.py` | regression for active 564–566 paths |
| `docs/ai-agent/ACHIEVEMENT_REVIEWED_EVIDENCE.json` | update 564–566 reviewed status/evidence |
| `docs/ai-agent/WEAPON_PROFICIENCY_ACHIEVEMENT_REPORT.md` | durable implementation boundary |
| this task | execution record and Handoff |

# Commands and tests

```text
python -m unittest discover -s tools/ai-agent -p "test_weapon_proficiency_achievement_audit.py" -v
python -m unittest discover -s tools/ai-agent -p "test_achievement_validation.py" -v
python -m py_compile tools/ai-agent/weapon_proficiency_achievement_audit.py
python -m json.tool docs/ai-agent/ACHIEVEMENT_REVIEWED_EVIDENCE.json
git diff --check
git diff --cached --check
```

## Verified automation

| Commit/run | Check | Result |
|---|---|---|
| `2ca478b519204178232303362a1e471ba3320c1c` / `29266235224` | runtime patch, clang-format, focused Weapon Proficiency and comprehensive achievement tests, commit/push | passed |
| `f03f49206b0ec9313dc4723ceca23ca0609469f4` / `29266432307` | validator synchronization, both focused test suites, JSON validation, generated audit assertions, commit/push | passed |
| `ab474562c47b3af87ea8d964f1f75f6d264a86f7` | action-generated head | workflows marked `action_required`; not counted as current-head validation |

# Failed approaches

1. Direct local `git clone` failed because the shell environment could not resolve `github.com`; no repository state changed.
2. Action-generated commits did not start authoritative repository workflows and returned `action_required`; a normal user-authored task update is used to trigger final CI.

# Design decisions

| Decision | Reason |
|---|---|
| One canonical threshold helper | avoids duplicated threshold logic across live and backfill paths |
| Award all satisfied thresholds | supports existing players and large count jumps without skipping lower achievements |
| Reconcile after `WeaponProficiency::load()` | achievements are already loaded and proficiency states already normalized |
| Silent login reconciliation | prevents login message spam while still persisting missing achievements |
| Message on live transition | preserves normal achievement feedback for newly earned mastery |
| Keep 567 separate | different definition, condition and evidence boundary |
| Keep status partially-confirmed | no real-client runtime/E2E proof yet |

# Exact remaining work

1. Run all workflows on the user-authored head produced by this task update.
2. Inspect C++ compile/unit results, dedicated Weapon Proficiency audit and comprehensive Achievement Validation.
3. Check exact final diff and review threads.
4. Update this task with final run IDs/SHA.
5. Mark PR Ready and enable auto-merge only when all gates pass.
6. Archive task after merge in a separate cleanup PR.

# Handoff

- branch: `fix/weapon-proficiency-achievement-thresholds`
- current implementation commit before final task update: `ab474562c47b3af87ea8d964f1f75f6d264a86f7`
- PR: `#272`
- completed: runtime thresholds, login reconciliation, unit threshold test, validator synchronization and reviewed evidence update
- not completed: authoritative current-head CI and merge
- last correct tests: runs `29266235224` and `29266432307`, both success
- blocker: none; final workflows must run on the user-authored head
- next step: inspect workflow runs for the commit created by this task update; repair any failure before Ready.

# Completion

- Final status: active
- PR: #272
- Merge commit:
- Archived at:
