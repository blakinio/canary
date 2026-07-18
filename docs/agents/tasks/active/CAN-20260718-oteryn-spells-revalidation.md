---
task_id: CAN-20260718-oteryn-spells-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-016
status: implementing
agent: "GPT-5.5 Thinking"
branch: docs/oam-016-spells-revalidation
base_branch: main
created: 2026-07-18
updated: 2026-07-18T18:14:00+02:00
last_verified_commit: "1dd21117ce06cc4463e6185f4ff74546031b55e6"
risk: high
related_issue: "blakinio/Otheryn#38"
related_pr: "548"
depends_on:
  - OAM-013
blocks:
  - OAM-017
modules_touched:
  - spells
owned_paths:
  exclusive:
    - docs/agents/OTERYN_OAM_016_SPELLS_REVALIDATION.md
    - docs/agents/tasks/active/CAN-20260718-oteryn-spells-revalidation.md
---

# Goal

Revalidate canonical OAM-016 `spells` against immutable task-start baselines and accept only the strongest dependency-valid evidence-backed target implementation.

# Provisional disposition

```text
spells → REUSE
```

Final only after exact-target proof and full closeout.

# Immutable task-start baselines

- Canary: `93296bbf0c349a6589af51a311d12f7dfaf6c001`
- Otheryn: `1dd21117ce06cc4463e6185f4ff74546031b55e6`
- upstream: `691614c1a302aee776002ca3851eca399be1a82c`
- OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

# Evidence decision

The canonical registry record `spells.yaml` depends only on completed OAM-013 `combat`. OAM-002 whole-tree provenance plus later target/upstream history shows no canonical spell production mutation through task start. Task-start target/upstream/legacy share exact `spells.cpp` blob `4afc2bafdcd3d122097b973931845b0fec7f32fb`; target/legacy `spells.hpp` blob is `d419f509853b3eb45658c2e8f5d6fbaec1f8d611`.

Reviewed legacy differences are cross-module packages, not isolated spell-core donors:

- PR #76/#108: Gameplay Analytics instrumentation/runtime-reference hardening in representative spell/rune scripts;
- PR #216/#220: Wheel 15.25-conditioned additional areas in `flurry_of_blows.lua` and `front_sweep.lua`, coupled to Wheel ownership.

OAM-016 does not partially import either package.

# Target proof

```text
Otheryn issue #38: OPEN
Otheryn PR #39: OPEN
target proof head at task checkpoint: 62a61725c66a2c394327cb665f08d076c2b7d791
scope: tests/unit/game/CMakeLists.txt + tests/unit/game/spell_reuse_test.cpp
```

No production runtime/data mutation is authorized.

# Exclusions

- no exhaustive formula/value parity;
- no exhaustive cooldown/resource/rune-consumption parity;
- no individual spell-script parity;
- no Wheel augmentation parity or partial PR #216/#220 import;
- no Gameplay Analytics instrumentation parity;
- no protocol/client/map/assets/persistence mutation;
- preserve OAM-004 SQL/KV non-atomicity and completed OAM-006/OAM-007/OAM-013/OAM-014/OAM-015 ownership.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T18:14:00+02:00
head: 9c99d1bc2079c855428f7b3ef62189bbffe909e2
branch: docs/oam-016-spells-revalidation
pr: 548
status: implementing
next_action: Validate Otheryn PR #39 on its exact head, then record merged target evidence and move Canary PR #548 to ready state.
context_routes:
  - docs/agents/OTERYN_OAM_016_SPELLS_REVALIDATION.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
owned_paths:
  - docs/agents/OTERYN_OAM_016_SPELLS_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260718-oteryn-spells-revalidation.md
proven:
  - Fresh task-start heads were pinned for Canary, Otheryn, upstream and maintained OTClient.
  - Canonical spells depends only on completed combat.
  - Target and upstream production history through task start contains no canonical spells path mutation.
derived:
  - Current target/upstream spell core is the strongest dependency-valid candidate, pending exact-target proof.
unknown:
  - Exact target CI and full-test result for Otheryn PR #39.
  - Final OAM-016 disposition until target proof passes and merges.
conflicts: []
rejected_hypotheses:
  - Treating Gameplay Analytics instrumentation as an independent spell-core donor.
  - Partially importing only the spell-script fragment of the coordinated Wheel 15.25 package.
changed_paths:
  - docs/agents/OTERYN_OAM_016_SPELLS_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260718-oteryn-spells-revalidation.md
blockers:
  - Otheryn PR #39 exact-head CI and full tests must pass before final disposition.
first_failure:
  marker: none
  evidence: No validation failure has been observed at this checkpoint.
validation:
  - command: OAM-016 fresh preflight
    result: PASS
    evidence: Canonical registry dependency and open-PR ownership checks passed.
  - command: Otheryn PR #39 exact-head CI
    result: NOT_RUN
    evidence: Target validation is pending.
```
