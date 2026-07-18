---
task_id: CAN-20260718-oteryn-spells-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-016
status: review
agent: "GPT-5.5 Thinking"
branch: docs/oam-016-spells-revalidation
base_branch: main
created: 2026-07-18
updated: 2026-07-18T18:30:00+02:00
last_verified_commit: "46cc7458d644da356371aabf3ff18c0e51d228a8"
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

# Final disposition

```text
spells → REUSE
```

# Immutable task-start baselines

- Canary: `93296bbf0c349a6589af51a311d12f7dfaf6c001`
- Otheryn: `1dd21117ce06cc4463e6185f4ff74546031b55e6`
- upstream: `691614c1a302aee776002ca3851eca399be1a82c`
- OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

# Evidence decision

The canonical registry record `spells.yaml` depends only on completed OAM-013 `combat`. OAM-002 whole-tree provenance plus later target/upstream history shows no canonical spell production mutation through task start. Task-start target/upstream/legacy share exact `spells.cpp` blob `4afc2bafdcd3d122097b973931845b0fec7f32fb`; target/legacy `spells.hpp` blob is `d419f509853b3eb45658c2e8f5d6fbaec1f8d611`.

Reviewed legacy differences remain cross-module packages, not isolated spell-core donors:

- PR #76/#108: Gameplay Analytics instrumentation/runtime-reference hardening in representative spell/rune scripts;
- PR #216/#220: Wheel 15.25-conditioned additional areas in `flurry_of_blows.lua` and `front_sweep.lua`, coupled to Wheel ownership.

OAM-016 does not partially import either package.

# Exact target proof

```text
Otheryn issue #38: CLOSED / completed
Otheryn PR #39 final head: 62a61725c66a2c394327cb665f08d076c2b7d791
target squash merge: 46cc7458d644da356371aabf3ff18c0e51d228a8
CI #123 / 29651516932: SUCCESS
Required #112 / 29651516827: SUCCESS
autofix.ci #105 / 29651516800: SUCCESS
full CTest: 355/355 PASS
focused SpellReuseTest: 2/2 PASS
artifact: 8431734928
digest: sha256:e98fc12c4e8c4f661d96ebb39a7b7fe44d58c2e7c7dc53beb27c14773f0db5f8
```

Final target diff contained exactly two test paths and no production runtime/data change. Target comments, reviews and review threads were all empty, target `main` had no task-start drift, and the target merge used expected-head protection.

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
updated_at: 2026-07-18T18:30:00+02:00
head: ab1d4cb99fe388459c2fb384d5e03bc41b6dc7c5
branch: docs/oam-016-spells-revalidation
pr: 548
status: validating
next_action: Pass final exact-head Agent Task Ownership and CI for Canary PR #548, then perform clean review and main-drift audit before expected-head merge.
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
  - Otheryn PR #39 merged exact head 62a61725c66a2c394327cb665f08d076c2b7d791 as 46cc7458d644da356371aabf3ff18c0e51d228a8.
  - Exact target proof passed 355 of 355 full tests and 2 of 2 focused SpellReuseTest cases.
derived:
  - Canonical OAM-016 disposition is REUSE while Analytics instrumentation and coordinated Wheel spell-area changes remain excluded cross-module gaps.
unknown:
  - Canary governance merge SHA is unavailable until PR #548 merges.
conflicts: []
rejected_hypotheses:
  - Treating Gameplay Analytics instrumentation as an independent spell-core donor.
  - Partially importing only the spell-script fragment of the coordinated Wheel 15.25 package.
changed_paths:
  - docs/agents/OTERYN_OAM_016_SPELLS_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260718-oteryn-spells-revalidation.md
blockers:
  - Final exact-head Canary governance gates and pre-merge audit must pass.
first_failure:
  marker: none
  evidence: No validation failure has occurred in the accepted OAM-016 target proof.
validation:
  - command: OAM-016 fresh preflight
    result: PASS
    evidence: Canonical registry dependency and open-PR ownership checks passed.
  - command: Otheryn PR #39 exact-head CI run 29651516932
    result: PASS
    evidence: Exact target head passed platform builds, runtime smoke, database import and 355 of 355 CTest cases.
  - command: SpellReuseTest exact-target proof
    result: PASS
    evidence: Both focused SpellReuseTest cases passed on exact head 62a61725c66a2c394327cb665f08d076c2b7d791.
```
