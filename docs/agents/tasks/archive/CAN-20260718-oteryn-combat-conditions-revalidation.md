---
task_id: CAN-20260718-oteryn-combat-conditions-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-014
status: completed
agent: "GPT-5.5 Thinking"
branch: docs/oam-014-combat-conditions-revalidation
base_branch: main
created: 2026-07-18
updated: 2026-07-18T12:03:57Z
last_verified_commit: "c9ba742731ebea2ccaf73b8b7ae78ee855ad9109"
risk: high
related_issue: "blakinio/Otheryn#34"
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
completed: 2026-07-18T12:03:57Z
---

# Goal

Revalidate exactly one canonical Oteryn migration unit, `combat-conditions`, against immutable task-start baselines and current target architecture. Accept only the smallest coherent evidence-backed adaptation required for condition lifecycle correctness.

# Immutable task-start baselines

- governance/legacy Canary: `blakinio/canary@0253b712cd4275e8ad72d5bca7020d1f4a2246b7`
- Oteryn target: `blakinio/Otheryn@3628effc5f22e7edbdc66dc5f514e4df5c9f0cda`
- upstream evidence: `opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f`
- maintained OTClient: `blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

# Final disposition

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
- [x] Verify exact donor test blob `ee2f185042cdb359aac1a752dce971ec76c38f8d` and CMake blob `b224d4eb1eb15eb92ca4a26f214c0764b82b03c3`.
- [x] Audit reviewed legacy history for additional coupled `condition.cpp` runtime fixes; none identified.
- [x] Determine final disposition `ADAPT`.
- [x] Materialize exact 3-path target runtime/test boundary with fail-closed donor verification.
- [x] Pass exact-head Otheryn CI #117, Required #108 and autofix #101.
- [x] Pass Linux debug build, Canary runtime smoke, DB schema import and actual CTest.
- [x] Pass 3/3 `ConditionLightTest` and 351/351 full target suite.
- [x] Record primary artifact `8429300008` and digest.
- [x] Audit target comments/reviews/threads and race-safe target-main drift before merge.
- [x] Squash-merge target PR #35 with expected-head protection as `9d797b547c3f85f6d210c6123202c7cae32d5133`.
- [x] Close target issue #34 completed.
- [x] Finalize Canary evidence report/task with exact target proof.
- [ ] Pass exact-head Canary Ownership and CI/Required.
- [ ] Audit/merge Canary governance PR #539.
- [ ] Archive task in separate lifecycle-only PR.
- [ ] Reconcile durable migration program in separate program-only PR.
- [ ] Mark OAM-014 COMPLETE and keep OAM-015 NOT STARTED until durable reconciliation merges.

# Exact target proof

```text
Otheryn PR #35 final head: f4044811f2b930318ec6541a51e73a9a1b6fdce0
CI #117: 29642976283 SUCCESS
Required #108: 29642976213 SUCCESS
autofix.ci #101: 29642976219 SUCCESS
Linux debug build: PASS
Canary runtime smoke: PASS
database schema import: PASS
full CTest: 351/351 PASS
ConditionLightTest: 3/3 PASS
primary test artifact: 8429300008
artifact digest: sha256:328f60045be1d42e4fba0c6b80aa64a3b8e767553808d7c47119750922cc2e36
target squash merge: 9d797b547c3f85f6d210c6123202c7cae32d5133
issue #34: CLOSED / completed
```

# Explicit exclusions

- no generic combat formula or target-selection change;
- no spell registration/cooldown migration;
- no vocation-specific state migration;
- no protocol/client/map/asset changes;
- no broad persistence redesign;
- no SQL/KV atomicity claim;
- no automatic persisted-data rewrite;
- no exhaustive condition timing/stacking/persistence correctness claim;
- no full Real Tibia condition formula/value parity claim.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T13:59:30+02:00
head: 861e93e1aca66491c3c2489a0e61394db97e4267
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
  - final disposition is combat-conditions ADAPT
  - immutable task-start baselines are Canary 0253b712cd4275e8ad72d5bca7020d1f4a2246b7 Otheryn 3628effc5f22e7edbdc66dc5f514e4df5c9f0cda upstream e0ac98e399d0f7e483f3668f57b78fcc45b6e53f OTClient 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
  - target and pinned upstream condition cpp share task-start blob 5b15ed00c7e92eef6d8c719aec423443efae8b7a
  - reviewed PR 297 runtime donor blob is 26a1cf0c9e01f4ab162438e8284f5cc73d129d11
  - exact donor test blob is ee2f185042cdb359aac1a752dce971ec76c38f8d
  - exact donor CMake blob is b224d4eb1eb15eb92ca4a26f214c0764b82b03c3
  - reviewed history found no second coupled delivered condition cpp runtime fix
  - target PR 35 final scope is exactly three accepted paths and contains no materializer helpers
  - exact-head CI Required and autofix gates passed
  - Linux debug build Canary runtime smoke DB import and actual CTest passed
  - full target suite passed 351 of 351
  - ConditionLightTest focused surface passed 3 of 3
  - target PR audit was clean and target main had no task-start drift immediately before merge
  - target PR 35 squash-merged with expected-head protection as 9d797b547c3f85f6d210c6123202c7cae32d5133
  - target issue 34 is closed completed
derived:
  - exact reviewed zero-level ConditionLight correctness boundary is dependency-valid after completed combat
  - persisted zero light values are normalized in memory without claiming broad persistence completeness
  - no physical-client E2E is required because no protocol or client boundary changed
unknown:
  - Canary governance feature merge SHA remains pending
  - lifecycle archive merge SHA remains pending
  - durable program reconciliation merge SHA remains pending
conflicts: []
first_failure:
  marker: none
  evidence: target adaptation completed successfully; only Canary governance lifecycle and durable program closeout remain
rejected_hypotheses:
  - file identity alone proves whole-module condition correctness
  - condition lifecycle belongs to generic combat OAM-013
  - individual spells belong inside combat-conditions ownership
  - zero-level normalization proves exhaustive condition timing stacking or persistence parity
changed_paths:
  - docs/agents/OTERYN_OAM_014_COMBAT_CONDITIONS_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260718-oteryn-combat-conditions-revalidation.md
validation:
  - command: exact target upstream condition core comparison
    result: PASS
    evidence: task-start target and upstream condition cpp blob 5b15ed00c7e92eef6d8c719aec423443efae8b7a
  - command: exact reviewed donor provenance verification
    result: PASS
    evidence: runtime test and CMake donor blobs matched PR 297 exactly
  - command: exact-head Otheryn adaptation CI and runtime proof
    result: PASS
    evidence: CI 29642976283 Required 29642976213 full CTest 351 of 351 ConditionLightTest 3 of 3
  - command: target merge race-safe audit
    result: PASS
    evidence: zero comments reviews and review threads; target main identical to immutable baseline before expected-head squash merge
blockers: []
next_action: Run exact-head Canary governance gates for PR 539, audit comments reviews and review threads, then squash-merge; do not start OAM-015.
```

## Automated lifecycle completion

- Feature PR: #539.
- Feature head: `9c806ec8524d59430395173d8187ef90d8b2e64d`.
- Merge commit: `c9ba742731ebea2ccaf73b8b7ae78ee855ad9109`.
- Merged at: `2026-07-18T12:03:57Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
