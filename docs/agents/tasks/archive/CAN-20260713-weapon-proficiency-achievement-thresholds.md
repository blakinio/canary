---
task_id: CAN-20260713-weapon-proficiency-achievement-thresholds
status: merged
agent: "GPT-5.6 Thinking"
branch: fix/weapon-proficiency-achievement-thresholds
base_branch: main
created: 2026-07-13T18:00:00+02:00
updated: 2026-07-13T23:45:00+02:00
last_verified_commit: "76ef99391f255653ddfb4cb16ab8a5fae239591c"
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
modules_touched:
  - WeaponProficiency runtime
  - achievement award path
  - achievement validation evidence
reuses:
  - WeaponProficiency::getMasteredWeaponCount()
  - PlayerAchievement::add(uint16_t, ...)
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Implement evidence-backed runtime awards for Weapon Proficiency achievement IDs 564, 565 and 566 at mastered-weapon thresholds 1, 10 and 50.

Achievement ID 567 `The Forbidden Build` was explicitly excluded because its definition, twelve-item condition and historical backfill require a separate focused change.

# Final result

PR [#272](https://github.com/blakinio/canary/pull/272) was squash-merged into `main` as:

```text
ef258a535349052bcd1ad4188664a006ede36660
```

The merged implementation:

- awards ID 564 at one mastered weapon;
- awards ID 565 at ten mastered weapons;
- awards ID 566 at fifty mastered weapons;
- uses `PlayerAchievement::add` for canonical idempotency;
- reconciles already-mastered weapons silently during login after achievement and proficiency state loading;
- awards live mastery transitions with the normal player message;
- returns every satisfied threshold so large jumps and backfills cannot skip lower achievements;
- preserves existing Weapon Proficiency serialization and mastery semantics;
- leaves ID 567 absent and untouched.

# Validation evidence

Final reviewed PR head:

```text
76ef99391f255653ddfb4cb16ab8a5fae239591c
```

| Check | Result |
|---|---|
| CI run `29266822352` | success |
| Fast Checks | success |
| Lua Tests | success |
| Linux debug compile | success |
| Linux debug `Run Tests` / `canary_ut` | success |
| Linux release compile and datapack smoke | success |
| Windows CMake build and Canary smoke | success |
| macOS build and Canary smoke | success |
| Docker matrix | success |
| autofix.ci run `29266822198` | success |
| Achievement Validation run `166` on final head | success |
| Weapon Proficiency Achievement Audit run `34` on final head | success |
| Agent Task Ownership | success |
| unresolved review threads | none |
| mergeability before merge | true |

Focused materialization and evidence synchronization runs also passed:

- runtime patch run `29266235224`;
- validator/evidence synchronization run `29266432307`.

# Regression protection

The merged tests and validators cover:

- counts below, at and above 1, 10 and 50;
- no award below each threshold;
- all eligible IDs returned for a large count;
- first-entry mastery state;
- existing-entry false-to-true mastery transitions;
- login-time reconciliation for existing players;
- ID-based runtime award-path detection in the dedicated audit;
- reviewed-evidence status for 564-566 as `partially-confirmed` rather than `handler-missing`.

# Evidence boundary

The implementation is intentionally recorded as `partially-confirmed`, not fully confirmed, because a real-client gameplay E2E was not executed. Compile, unit, smoke and static validation are complete.

# Explicitly unresolved follow-up

Achievement ID 567 `The Forbidden Build` remains a separate task. Before implementation it still requires proof and tests for:

- the canonical registry definition and metadata;
- the exact twelve qualifying items;
- item/proficiency resolution for each item;
- live award timing;
- historical existing-player backfill semantics.

# Failed approaches and recovery

- Direct local clone was unavailable because the execution shell could not resolve GitHub; repository writes were performed through the GitHub connector and validated by repository CI.
- Action-generated heads initially produced `action_required`; a user-authored head was created and the authoritative full matrix was run.
- During final header documentation, an accidental unrelated signature change and then duplicated declarations were detected and reverted before authoritative CI. The final header patch contains only the intended helper declarations and documentation.

# Safety boundary

- No `.otbm`, item data, client assets, DB schema, protocol or production configuration changed.
- No ID 567 definition or guessed condition was introduced.
- No unresolved achievement was promoted to `confirmed` without runtime E2E proof.

# Post-merge catalogue synchronization

A follow-up documentation PR corrected `MODULE_CATALOG.md` to include merged PR #272, the live/login award path for IDs 564–566, and the explicit remaining boundary for ID 567. This prevents future agents from duplicating the already merged threshold implementation.

# Completion

- Final status: merged
- PR: #272
- Merge commit: `ef258a535349052bcd1ad4188664a006ede36660`
- Final reviewed head: `76ef99391f255653ddfb4cb16ab8a5fae239591c`
- Catalogue synchronized: yes
- Archived at: `docs/agents/tasks/archive/CAN-20260713-weapon-proficiency-achievement-thresholds.md`
