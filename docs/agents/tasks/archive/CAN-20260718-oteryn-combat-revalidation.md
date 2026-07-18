---
task_id: CAN-20260718-oteryn-combat-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-013
status: completed
agent: "GPT-5.5 Thinking"
branch: docs/oam-013-combat-revalidation
base_branch: main
created: 2026-07-18
updated: 2026-07-18
completed: 2026-07-18
last_verified_commit: "e4596861d8e8497645815d8eefb6cee3166b91d0"
risk: high
related_issue: "blakinio/Otheryn#32"
related_pr: "533"
depends_on:
  - OAM-004
  - OAM-012
blocks:
  - OAM-014
owned_paths:
  exclusive:
    - docs/agents/OTERYN_OAM_013_COMBAT_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/real-tibia/registry/modules/combat.yaml
    - docs/agents/real-tibia/registry/modules/combat-conditions.yaml
modules_touched:
  - combat
cross_repo_tasks: []
---

# OAM-013 — Combat Revalidation

## Completed result

```text
combat → REUSE
```

OAM-013 retained the task-start Otheryn generic combat core after exact target/upstream identity was combined with reviewed semantic history. File identity alone was not treated as sufficient evidence.

## Durable evidence before lifecycle archive

```text
Otheryn task-start: 4a16ca17ebd098cf9763bb3c07755bfd31ac1c43
upstream evidence: e0ac98e399d0f7e483f3668f57b78fcc45b6e53f
Canary task-start: e3563b447228830a4728790b52766dad56fe86f1
OTClient: 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f

target proof PR: blakinio/Otheryn#33
final target head: 6d5dfe623fef1a6db9b8447d1978a2a6bb1272eb
target squash merge: 3628effc5f22e7edbdc66dc5f514e4df5c9f0cda
Canary governance PR: #533
Canary governance squash merge: e4596861d8e8497645815d8eefb6cee3166b91d0
```

Exact-head target proof:

```text
CI 29639923928: PASS
Required 29639923874: PASS
autofix 29639923867: PASS
Linux debug build: PASS
Canary runtime smoke: PASS
database schema import: PASS
full CTest: 348/348 PASS
CombatReuseTest: 2/2 PASS
artifact: 8428406618
artifact digest: sha256:9165209e09bdef873563b6fef90516d80032e280244af702843cc55f22774635
```

## Reviewed exclusions

- PR #297 zero-level `ConditionLight` safety belongs to downstream `combat-conditions` and was not migrated in OAM-013.
- PR #92 was rejected as a runtime donor because its described `combat.cpp` wiring did not land on the final PR head/current task-start legacy main.
- No spell, Wheel, client, protocol, map, asset, quest, achievement or persistence redesign was migrated.
- No exhaustive combat correctness or full Real Tibia formula/value parity is claimed.

## Lifecycle

Target proof and Canary governance feature are complete. This record is moved from `tasks/active` to `tasks/archive` by the separate OAM-013 lifecycle change.

OAM-014 remains NOT STARTED until this lifecycle archive and the separate durable Oteryn program reconciliation are both merged.
