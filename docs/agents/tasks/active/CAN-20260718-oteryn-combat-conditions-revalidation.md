---
task_id: CAN-20260718-oteryn-combat-conditions-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-014
status: ready
agent: "GPT-5.5 Thinking"
branch: docs/oam-014-combat-conditions-revalidation
base_branch: main
created: 2026-07-18
updated: 2026-07-18T13:36:54+02:00
last_verified_commit: "7ed093cd71e75221b7c256a07b8f37704a6d06fc"
risk: high
related_pr: "539"
depends_on:
  - OAM-013
blocks:
  - OAM-015
owned_paths:
  exclusive:
    - docs/agents/OTERYN_OAM_014_COMBAT_CONDITIONS_REVALIDATION.md
    - docs/agents/tasks/active/CAN-20260718-oteryn-combat-conditions-revalidation.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/combat-conditions.yaml
    - src/creatures/combat/condition.cpp
    - src/creatures/combat/condition.hpp
    - tests/unit/players/condition/CMakeLists.txt
    - tests/unit/players/condition/condition_light_test.cpp
modules_touched:
  - combat-conditions
reuses:
  - completed OAM-013 combat boundary
  - existing Otheryn condition runtime and unit-test harness
public_interfaces:
  - condition creation and timed lifecycle
  - condition serialization and deserialization
  - ConditionLight start and restore safety
cross_repo_tasks: []
---

# Goal

Revalidate exactly one canonical Oteryn migration unit, `combat-conditions`, against immutable task-start baselines and current target architecture. Accept only the smallest coherent evidence-backed adaptation required for condition lifecycle correctness.

# Immutable task-start baselines

- governance/legacy Canary: `blakinio/canary@0253b712cd4275e8ad72d5bca7020d1f4a2246b7`
- Oteryn target: `blakinio/Otheryn@3628effc5f22e7edbdc66dc5f514e4df5c9f0cda`
- upstream evidence: `opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f`
- maintained OTClient: `blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

# Initial disposition

```text
combat-conditions → REVALIDATE
```

Working candidate after initial semantic evidence:

```text
combat-conditions → ADAPT
```

# Acceptance criteria

- [x] Refresh Canary, Otheryn, upstream and maintained-client live heads.
- [x] Verify OAM-014 is eligible only after durable OAM-013 reconciliation.
- [x] Select exactly one canonical module from registry: `combat-conditions`.
- [x] Confirm hard dependency `combat` is completed.
- [x] Audit open Canary/Otheryn PRs for overlap with `src/creatures/combat/condition.*`.
- [x] Record immutable task-start baselines.
- [x] Publish draft governance PR #539 and bind this task to it.
- [x] Confirm task-start Otheryn and pinned upstream `condition.cpp` share blob `5b15ed00c7e92eef6d8c719aec423443efae8b7a`.
- [x] Confirm reviewed PR #297/current legacy corrected runtime blob is `26a1cf0c9e01f4ab162438e8284f5cc73d129d11`.
- [ ] Verify exact donor test/CMake provenance from PR #297.
- [ ] Audit reviewed legacy history for any additional coupled `combat-conditions` runtime fixes.
- [ ] Determine final disposition.
- [ ] Materialize smallest coherent target runtime/test boundary if `ADAPT`.
- [ ] Pass exact-head Otheryn CI/Required/autofix and actual CTest.
- [ ] Audit target comments/reviews/threads and race-safe target-main drift before merge.
- [ ] Merge target PR and close target issue.
- [ ] Finalize Canary evidence report/task with exact target proof.
- [ ] Pass exact-head Canary Ownership and CI/Required.
- [ ] Audit/merge Canary governance PR #539.
- [ ] Archive task in separate lifecycle-only PR.
- [ ] Reconcile durable migration program in separate program-only PR.
- [ ] Mark OAM-014 COMPLETE and keep OAM-015 NOT STARTED until durable reconciliation merges.

# Explicit exclusions

- no generic combat formula or target-selection change;
- no spell registration/cooldown migration;
- no vocation-specific state migration;
- no protocol/client/map/asset changes;
- no broad persistence redesign;
- no SQL/KV atomicity claim;
- no exhaustive condition timing/stacking/persistence parity claim unless separately proven.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T13:36:54+02:00
head: 7ed093cd71e75221b7c256a07b8f37704a6d06fc
branch: docs/oam-014-combat-conditions-revalidation
pr: 539
status: ready
context_routes:
  - agent-governance
  - oteryn-migration
  - combat-conditions
owned_paths:
  - docs/agents/OTERYN_OAM_014_COMBAT_CONDITIONS_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260718-oteryn-combat-conditions-revalidation.md
proven:
  - immutable task-start baselines are Canary 0253b712cd4275e8ad72d5bca7020d1f4a2246b7 Otheryn 3628effc5f22e7edbdc66dc5f514e4df5c9f0cda upstream e0ac98e399d0f7e483f3668f57b78fcc45b6e53f OTClient 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
  - canonical module combat-conditions depends on completed combat
  - open PR audit found no overlap with src/creatures/combat/condition.*
  - target and pinned upstream condition cpp share blob 5b15ed00c7e92eef6d8c719aec423443efae8b7a
  - reviewed PR 297 and task-start legacy condition cpp share corrected blob 26a1cf0c9e01f4ab162438e8284f5cc73d129d11
derived:
  - PR 297 is a dependency-valid bounded adaptation candidate for OAM-014
  - no physical-client E2E is expected unless protocol/client ownership changes
unknown:
  - exact donor test and CMake blobs remain to be verified
  - additional coupled reviewed condition-lifecycle fixes remain to be audited
  - final disposition and target merge SHA remain pending
  - Canary governance lifecycle and durable reconciliation merge SHAs remain pending
conflicts: []
first_failure:
  marker: none
  evidence: preflight complete; donor provenance and bounded semantic audit remain
rejected_hypotheses:
  - condition lifecycle belongs to generic combat OAM-013
  - file identity alone proves whole-module correctness
  - spells belong inside combat-conditions ownership
changed_paths:
  - docs/agents/OTERYN_OAM_014_COMBAT_CONDITIONS_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260718-oteryn-combat-conditions-revalidation.md
validation:
  - command: fresh live-state and open-PR overlap preflight
    result: PASS
    evidence: no Otheryn open PR and no Canary open PR owns condition runtime paths
  - command: exact task-start target upstream condition core comparison
    result: PASS
    evidence: target and upstream condition cpp blob 5b15ed00c7e92eef6d8c719aec423443efae8b7a
  - command: reviewed PR 297 runtime provenance check
    result: PASS
    evidence: donor and task-start legacy condition cpp blob 26a1cf0c9e01f4ab162438e8284f5cc73d129d11
blockers: []
next_action: Verify exact PR 297 donor test/CMake provenance and audit additional reviewed combat-conditions history before any target write; do not start OAM-015.
```
