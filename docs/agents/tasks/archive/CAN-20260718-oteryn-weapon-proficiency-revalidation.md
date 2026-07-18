---
task_id: CAN-20260718-oteryn-weapon-proficiency-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-011
status: completed
agent: "GPT-5.5 Thinking"
branch: docs/oam-011-weapon-proficiency-revalidation
base_branch: main
created: 2026-07-18T08:17:00+02:00
updated: 2026-07-18T09:00:00+02:00
completed: 2026-07-18T09:00:00+02:00
last_verified_commit: "8df917cf34771e1388533915a6fa4e50aa91e1bb"
risk: medium
related_issue: ""
related_pr: "519"
depends_on:
  - OAM-010
  - OAM-004
blocks:
  - OAM-012
owned_paths:
  exclusive:
    - docs/agents/OTERYN_OAM_011_WEAPON_PROFICIENCY_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/weapon-proficiency.yaml
    - src/creatures/players/components/weapon_proficiency.cpp
    - src/creatures/players/components/weapon_proficiency.hpp
    - data/items/proficiencies.json
    - tests/unit/players/components/weapon_proficiency_test.cpp
modules_touched:
  - weapon-proficiency
cross_repo_tasks: []
---

# OAM-011 — Weapon Proficiency Revalidation

## Completed result

Final disposition:

```text
weapon-proficiency ADAPT
```

The clean target/upstream proficiency core is retained, but whole-module `REUSE` was rejected because task-start target/upstream contains a concrete first-gain mastery-state correctness defect and lacks accepted proficiency-side mastery achievement reconciliation.

The adapted production boundary is intentionally the exact proven Canary state after PR #272 and before PR #288. Achievement `567` / `The Forbidden Build` and its twelve-weapon condition remain excluded because the target achievement catalogue still treats `567` as unknown/non-existent and achievement-catalogue ownership is outside OAM-011.

## Exact baselines

```text
Canary task-start: 9586530202eb3e40569bf4f97d21c63c9d99b6cb
Otheryn task-start: a4d095e3880787233bd194616dc6d19e6b94faaf
upstream evidence: e0ac98e399d0f7e483f3668f57b78fcc45b6e53f
maintained OTClient: 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

## Selected adaptation provenance

```text
Canary PR #212: first-gain mastery correctness + getMasteredWeaponCount
Canary PR #272: idempotent mastery achievement reconciliation for 564/565/566
Canary PR #288: excluded later achievement 567 behaviour
selected donor head: 76ef99391f255653ddfb4cb16ab8a5fae239591c
weapon_proficiency.cpp donor blob: bd3ecad2b34fa5bc731e253718ef9185d372727b
weapon_proficiency.hpp donor blob: 451177df8ff3ef569f69c27dc2cd79d7d64918c8
focused test donor blob: 3b7310737c27b9b8865606baa4a6adfa0d324431
```

`data/items/proficiencies.json` remained exact-identical across task-start legacy, target and upstream and was not changed.

## Target adaptation and proof

Otheryn PR #29 changed exactly:

- `src/creatures/players/components/weapon_proficiency.cpp`;
- `src/creatures/players/components/weapon_proficiency.hpp`;
- `tests/unit/players/components/weapon_proficiency_test.cpp`;
- existing `tests/unit/players/components/CMakeLists.txt` registration.

Final target proof:

```text
final head: c9f060a2020c3612f65f8e31c6e745a03aa3fe5f
autofix 29634273531: PASS
CI 29634273615: PASS
Required 29634273523: PASS
Linux debug compile: PASS
runtime smoke: PASS
database schema import: PASS
Run Tests: PASS
focused WeaponProficiencyTest: 7/7 PASS
full suite: 336/336 PASS
artifact: 8426692510
artifact digest: sha256:f7602a97b67686e25f53e06974b08ee0c7646c4cba873999397437830f95c5cf
comments: 0
reviews: 0
review threads: 0
target squash merge: 72f7bdc1a5afa9e9982c20bdcf3098c83dca543e
```

## Canary governance completion

PR #519 was reconstructed directly onto `main@470a5e6deaaed67c17a2ddb2ab7b5bc1ed9609f6` with exactly the OAM-011 evidence report and active task.

```text
final Canary head: 35a0320c63fefe06789a928edef5bdcd4cc0fe33
pre-ready Ownership 29634880703: PASS
pre-ready CI 29634880757: PASS
ready-state CI 29634906649: PASS
Required: PASS
final comments: 0
final reviews: 0
final review threads: 0
feature squash merge: 8df917cf34771e1388533915a6fa4e50aa91e1bb
```

## Boundaries preserved

- OAM-004 player SQL versus later KV durability remains non-atomic; no KV schema or SQL persistence change was made.
- OAM-010 shared character progression ownership remains unchanged.
- Achievement catalogue ownership remains separate; only existing IDs 564/565/566 are reconciled by the proficiency component.
- Achievement 567 is explicitly excluded.
- Generic combat/perk architecture was not rewritten.
- No protocol, client, map or asset mutation was made.
- No physical-client E2E is claimed or required for the selected server-side mastery correctness boundary.
- No Real Tibia proficiency formula/perk parity is claimed.

## Lifecycle

Target delivery and Canary feature governance are complete. This record is moved from `tasks/active` to `tasks/archive` by the separate OAM-011 lifecycle change after feature PR #519 merged.

OAM-012 remains inactive until this lifecycle archive and the separate durable Oteryn program reconciliation are both merged.
