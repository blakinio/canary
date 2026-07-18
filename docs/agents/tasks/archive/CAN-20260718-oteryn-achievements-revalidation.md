---
task_id: CAN-20260718-oteryn-achievements-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-012
status: completed
agent: "GPT-5.5 Thinking"
branch: docs/oam-012-achievements-revalidation
base_branch: main
created: 2026-07-18T09:20:00+02:00
updated: 2026-07-18T11:31:00+02:00
completed: 2026-07-18T11:31:00+02:00
last_verified_commit: "92b704415ffb53165647c0623d1ab273fc7b723f"
risk: medium
related_issue: "blakinio/Otheryn#30"
related_pr: "524"
depends_on:
  - OAM-004
  - OAM-011
blocks:
  - OAM-013
owned_paths:
  exclusive:
    - docs/agents/OTERYN_OAM_012_ACHIEVEMENTS_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/real-tibia/registry/modules/achievements.yaml
    - src/creatures/players/components/player_achievement.cpp
    - src/creatures/players/components/player_achievement.hpp
    - data/scripts/lib/register_achievements.lua
    - src/creatures/players/components/weapon_proficiency.cpp
    - src/creatures/players/components/weapon_proficiency.hpp
    - tests/unit/players/components/player_achievement_test.cpp
    - tests/unit/players/components/weapon_proficiency_test.cpp
modules_touched:
  - achievements
cross_repo_tasks: []
---

# OAM-012 — Achievements Revalidation

## Completed result

Final disposition:

```text
achievements ADAPT
```

The accepted target adaptation preserves one authoritative central achievement catalogue, couples corrected point metadata with deterministic persisted aggregate-point reconciliation, and includes achievement `567` / `The Forbidden Build` with the exact reviewed twelve-weapon Weapon Proficiency attainability condition.

## Immutable task-start baselines

```text
Canary: d9c967d6e9b778da11a206d134d559f38ec1b8c8
Otheryn: 72f7bdc1a5afa9e9982c20bdcf3098c83dca543e
upstream: e0ac98e399d0f7e483f3668f57b78fcc45b6e53f
maintained OTClient: 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

## Selected adaptation provenance

```text
Canary PR #256
Canary PR #264 donor commit: d14d5c992d4095c79672a8469050aa9e103e34bb
Canary PR #288 donor commit: 67ac28ee314ccc31671344515633c9411c3fe9df
```

Verified donor blobs:

```text
player_achievement.cpp: 998a077b6302233ba81969e904f72ad19d4b4840
player_achievement.hpp: c44334cc9993c5a497ea2023d52cdd6d26501914
player_achievement_test.cpp: c10d90aa649322520739696507ba8a0ff2d05a06
register_achievements.lua: 25e5b794a41adb84f7c0f7d309283d4fdb971511
weapon_proficiency.cpp: 780d39f0c2cd0002ebd12f11a611212592217976
weapon_proficiency.hpp: 1ce80f1789aec6649df9943b24081f0df8f10fb2
weapon_proficiency_test.cpp: 756088ca70188226b2bbe96dd44f038fd6afe417
```

The earlier handover value for `player_achievement_test.cpp` was rejected by fail-closed exact Git blob verification and corrected to `c10d90aa649322520739696507ba8a0ff2d05a06`.

## Target adaptation and proof

Otheryn PR #31 changed exactly eight bounded runtime/test paths and removed all temporary donor-materialization plumbing before final proof.

```text
final target head: 8ee4bfe3c6b867834447a5b9e206e1dbd44f66d2
target squash merge: 4a16ca17ebd098cf9763bb3c07755bfd31ac1c43
CI run 29638502030: PASS
Required run 29638501951: PASS
Repository Audit run 29638501958: PASS
autofix run 29638501946: PASS
Linux debug build: PASS
Canary runtime smoke: PASS
database schema import: PASS
full CTest suite: 346/346 PASS
PlayerAchievementTest: 7/7 PASS
WeaponProficiencyTest: 10/10 PASS
comments: 0
reviews: 0
review threads: 0
```

Primary test artifact:

```text
artifact: 8427980477
digest: sha256:170df7911fd928bb6af90c7f703e00554eccb4625a56d9fd54cc20e0854e0d3e
```

Otheryn issue #30 is closed as completed.

## Canary governance completion

Canary governance PR #524 was clean-synchronized directly onto `main@417571a0a3990ed406d894211f8f0d78b190eb33` and contained exactly the OAM-012 evidence report plus the active task.

```text
final Canary governance head: 46e3d4c07146ac8c0eb034ea4b40259d042d6cbe
Agent Task Ownership run 29639189342: PASS
CI run 29639189415: PASS
Required: PASS
final comments: 0
final reviews: 0
final review threads: 0
feature squash merge: 92b704415ffb53165647c0623d1ab273fc7b723f
```

## Boundaries preserved

- Player SQL and player KV remain non-atomic; no SQL/KV atomicity claim was introduced.
- No generic KV schema redesign, automatic MySQL reconnect, arbitrary SQL replay, or cross-domain transaction was introduced.
- One authoritative catalogue remains at `data/scripts/lib/register_achievements.lua`; no duplicate registry or permanent overlay was added.
- No unrelated quest, combat, or spell achievement hooks were migrated.
- No governance validator was copied into Otheryn runtime.
- No client, protocol, map, or asset mutation was made.
- No full Real Tibia achievement attainability parity is claimed.
- The canonical module registry data-path metadata remains a non-blocking governance cleanup gap.

## Lifecycle

Target delivery and Canary governance feature completion are complete. This record is moved from `tasks/active` to `tasks/archive` by this separate OAM-012 lifecycle change after feature PR #524 merged.

OAM-013 remains inactive until this lifecycle archive and the separate durable Oteryn program reconciliation are both merged.
