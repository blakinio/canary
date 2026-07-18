---
task_id: CAN-20260718-oteryn-combat-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-013
status: completed
agent: "GPT-5.5 Thinking"
branch: docs/oam-013-combat-revalidation
base_branch: main
created: 2026-07-18
updated: 2026-07-18T10:20:16Z
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
    - docs/agents/tasks/active/CAN-20260718-oteryn-combat-revalidation.md
    - docs/agents/OTERYN_OAM_013_COMBAT_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/combat.yaml
    - docs/agents/real-tibia/registry/modules/combat-conditions.yaml
    - docs/agents/real-tibia/registry/modules/spells.yaml
    - src/creatures/combat/combat.cpp
    - src/creatures/combat/combat.hpp
    - src/creatures/combat/condition.cpp
modules_touched:
  - combat
reuses:
  - OAM-004 player-persistence durability boundary
  - exact task-start Otheryn and pinned-upstream generic combat core
  - existing Otheryn combat unit-test and runtime smoke infrastructure
public_interfaces:
  - damage and healing pipeline
  - critical and leech modifiers
  - generic combat ordering
  - public ConditionType and CombatType mapping behavior
cross_repo_tasks: []
completed: 2026-07-18T10:20:16Z
---

# Goal

Revalidate canonical `combat` against immutable task-start baselines and retain the generic target combat core only when semantic review plus exact-target proof supports `REUSE`, without importing downstream condition lifecycle, spells, Wheel behavior or unrelated gameplay policy.

# Final disposition

```text
combat → REUSE
```

# Acceptance criteria

- [x] Re-fetch exact Canary, Otheryn, upstream and maintained-client heads before task creation.
- [x] Verify no pre-existing open OAM-013 PR in Canary or Otheryn.
- [x] Audit task-start open Canary PR changed paths for canonical combat overlap.
- [x] Select exactly one canonical module: `combat`.
- [x] Confirm hard dependency `player-persistence` is completed.
- [x] Publish governance PR #533.
- [x] Revalidate exact target versus pinned upstream central combat core.
- [x] Audit reviewed legacy combat history.
- [x] Separate downstream `combat-conditions` ownership.
- [x] Defer PR #297 zero-level light-condition safety to `combat-conditions`.
- [x] Reject PR #92 as runtime donor because intended `combat.cpp` wiring did not land.
- [x] Reject unrelated spell, Wheel, quest, client, protocol, map and asset scope.
- [x] Determine final disposition `REUSE`.
- [x] Create proof-only Otheryn issue #32 and PR #33 without combat implementation changes.
- [x] Keep target proof diff to exactly two test-only paths.
- [x] Pass exact-head CI #114, Required #106 and autofix #99.
- [x] Pass Linux debug build, Canary runtime smoke, DB schema import and actual CTest.
- [x] Pass 2/2 `CombatReuseTest` and 348/348 full target suite.
- [x] Audit target PR comments/reviews/threads and perform race-safe main drift check.
- [x] Squash-merge Otheryn PR #33 with `expected_head_sha` as `3628effc5f22e7edbdc66dc5f514e4df5c9f0cda`.
- [x] Close Otheryn issue #32 completed.
- [x] Detect non-overlapping Canary main drift from OTBM roadmap reconciliation.
- [x] Clean-sync governance branch directly onto current `main@abbeb51433d33af7398a82f0cd2ab776d01e710f`, preserving only two OAM-013 governance paths.
- [ ] Pass exact-head Canary Ownership and ready-state CI after clean-sync.
- [ ] Audit Canary PR #533 comments, reviews and review threads immediately before merge.
- [ ] Squash-merge Canary governance PR #533 and record merge SHA.
- [ ] Archive this task in a separate lifecycle-only PR.
- [ ] Reconcile the durable migration program in a separate program-only PR.
- [ ] Mark OAM-013 COMPLETE and keep OAM-014 NOT STARTED until durable reconciliation merges.

# Exact target proof

```text
Otheryn PR #33 final head: 6d5dfe623fef1a6db9b8447d1978a2a6bb1272eb
CI #114: 29639923928 SUCCESS
Required #106: 29639923874 SUCCESS
autofix.ci #99: 29639923867 SUCCESS
Linux debug build: PASS
Canary runtime smoke: PASS
database schema import: PASS
full CTest: 348/348 PASS
CombatReuseTest: 2/2 PASS
primary test artifact: 8428406618
artifact digest: sha256:9165209e09bdef873563b6fef90516d80032e280244af702843cc55f22774635
target squash merge: 3628effc5f22e7edbdc66dc5f514e4df5c9f0cda
issue #32: CLOSED / completed
```

# Explicit exclusions

- no generic combat implementation mutation;
- no `combat-conditions` lifecycle migration;
- no zero-level `ConditionLight` fix in OAM-013;
- no individual spell definitions;
- no Wheel-only behavior;
- no unrelated quest/achievement hooks;
- no protocol/client/map/asset changes;
- no persistence redesign or SQL/KV atomicity claim;
- no exhaustive combat correctness or Real Tibia formula/value parity claim.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T12:11:58+02:00
head: 443f8852821ee825ad7571a36317e13d8a25c60c
branch: docs/oam-013-combat-revalidation
pr: 533
status: ready
context_routes:
  - agent-governance
  - oteryn-migration
  - combat
owned_paths:
  - docs/agents/OTERYN_OAM_013_COMBAT_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260718-oteryn-combat-revalidation.md
proven:
  - final disposition is combat REUSE
  - immutable task-start baselines are Canary e3563b447228830a4728790b52766dad56fe86f1 Otheryn 4a16ca17ebd098cf9763bb3c07755bfd31ac1c43 upstream e0ac98e399d0f7e483f3668f57b78fcc45b6e53f OTClient 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
  - target and upstream central combat cpp share blob 8c3a2c87ead3e55c0ae219a0f8b075a44c3dec0a
  - target upstream and legacy combat hpp share blob 125390ed1a35cf804f5b31dbec61bcca346275c2
  - PR 297 belongs to downstream combat-conditions and was not copied
  - PR 92 is not accepted as delivered runtime donor
  - no delivered dependency-valid generic combat runtime adaptation was identified
  - proof-only target PR 33 changed exactly two test-only paths
  - full target suite passed 348 of 348 and CombatReuseTest passed 2 of 2
  - target PR 33 merged with expected head protection as 3628effc5f22e7edbdc66dc5f514e4df5c9f0cda
  - target issue 32 is closed completed
  - Canary main drift was limited to OTBM roadmap paths and did not overlap OAM-013
  - governance branch was clean-synced directly to Canary main abbeb51433d33af7398a82f0cd2ab776d01e710f
  - governance branch contains only the OAM-013 evidence report and active task
derived:
  - reviewed semantic history plus exact target upstream identity supports generic combat REUSE
  - combat-conditions retains PR 297 as downstream evidence after combat completion
  - no physical-client E2E is required because no protocol/client boundary changed
unknown:
  - Canary governance feature merge SHA remains pending
  - lifecycle archive merge SHA remains pending
  - durable program reconciliation merge SHA remains pending
conflicts: []
first_failure:
  marker: none
  evidence: target proof completed; only Canary governance lifecycle and durable program closeout remain
rejected_hypotheses:
  - file identity alone proves whole-module REUSE
  - condition lifecycle belongs to generic combat ownership
  - PR 92 prose proves delivered runtime chain-target hardening
  - individual spells belong to generic combat
  - Wheel-only behavior belongs to OAM-013
changed_paths:
  - docs/agents/OTERYN_OAM_013_COMBAT_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260718-oteryn-combat-revalidation.md
validation:
  - command: exact target upstream generic combat core revalidation
    result: PASS
    evidence: central combat cpp and hpp match pinned upstream while reviewed legacy deltas were classified separately
  - command: reviewed legacy semantic and ownership audit
    result: PASS
    evidence: PR 297 deferred to combat-conditions and PR 92 rejected as undelivered runtime donor
  - command: exact-head Otheryn proof-only CI and runtime proof
    result: PASS
    evidence: CI 29639923928 Required 29639923874 full CTest 348 of 348 CombatReuseTest 2 of 2
  - command: target merge race-safe audit
    result: PASS
    evidence: zero comments reviews and review threads; target main identical to immutable baseline before expected-head merge
  - command: Canary governance clean synchronization
    result: PASS
    evidence: branch reset to current main abbeb51433d33af7398a82f0cd2ab776d01e710f after non-overlapping OTBM roadmap drift
blockers: []
next_action: Run exact-head Canary governance gates for PR 533 after clean-sync, audit comments reviews and review threads, then squash-merge; do not start OAM-014.
```

## Automated lifecycle completion

- Feature PR: #533.
- Feature head: `f9ebe10abe28f03326ffab938f472c7c72d991cb`.
- Merge commit: `e4596861d8e8497645815d8eefb6cee3166b91d0`.
- Merged at: `2026-07-18T10:20:16Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
