---
task_id: CAN-20260722-oteryn-oam035-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
status: ready
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-035-preflight
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "6a87373e84073a84ccdbdb64f7d61b2747f40764"
risk: medium
related_issue: ""
related_pr: "707"
depends_on:
  - OAM-034 formally complete
blocks:
  - OAM-035 target proof/delivery selection
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260722-oteryn-oam035-preflight.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/real-tibia/registry/modules/**
modules_touched:
  - oteryn-architecture-migration
  - creature-ai
cross_repo_tasks: []
---

# OAM-035 Fresh Preflight

## Goal

Perform a fresh dependency-valid canonical-module preflight after formal OAM-034 closure. Do not implement OAM-035 in this task.

## Selected package

`creature-ai` is the selected dependency-valid OAM-035 canonical package.

Preflight disposition: `REUSE candidate`.

The final OAM-035 disposition still requires bounded target-side proof. This preflight does not claim runtime correctness, Real Tibia AI parity, pathfinding correctness, target-choice correctness, thread safety, or physical-client E2E closure.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T09:22:00+02:00
head: 4756e075023ac1376dfb88afc8deeef7bd833db2
branch: dudantas/oam-035-preflight
pr: 707
status: ready
context_routes:
  - agent-governance
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260722-oteryn-oam035-preflight.md
proven:
  - OAM-034 is formally complete before OAM-035 selection.
  - Fresh Canary main baseline is 6a87373e84073a84ccdbdb64f7d61b2747f40764.
  - Fresh Otheryn main baseline is 4771350b44665c5a37b0c058b3d413c0c0de542d.
  - Fresh upstream Canary baseline is 71a0f92b4da3f550b292fa7536a0e35c2769f1ae.
  - Fresh maintained OTClient baseline is a6868920443dc285656bd016acdb2c1ea566e511.
  - PR 707 live preflight head before preflight-completion commits was bb0554c8fa94fe0908be2cfa2ce7e371743382ed and both CI and Agent Task Ownership succeeded on that head.
  - Canonical creature-ai depends only on creature-definitions, which OAM-034 completed, and owns Monster runtime think target friend follow flee movement attack defense and spawn/despawn interactions.
  - Fresh ownership search found no open Canary or Otheryn PR matching the selected monster creature targeting or pathfinding boundary.
  - Otheryn and fresh upstream Canary have identical creature-ai owned blobs: monster.cpp 30cdadf4076d29116eb96fb8bb5f7f46bebddcd5 and monster.hpp a5426fdd22533179a9d54834dbe7b340a5d45012.
  - Legacy Canary differs on both owned blobs: monster.cpp 07356b448a61808d912d94de6fa09e3689a43fef and monster.hpp 04073f7d73a3d6c3c1ac4a3fa7d5b1998cca07e7.
  - Reviewed target/upstream monster.cpp contains the modular monster_combat_intention monster_pathfinding monster_targeting and monster_compute_service architecture that is absent from the reviewed legacy blob prefix.
  - The canonical registry keeps creature-definitions creature-ai boss-encounters raids and static spawns as separate ownership boundaries.
derived:
  - creature-ai is the next selected dependency-valid OAM-035 canonical package.
  - Whole-module legacy REUSE is rejected because current clean target and fresh upstream are identical on the owned core while legacy diverges from their newer modular AI architecture.
  - The smallest evidence-backed preflight outcome is creature-ai as a target/upstream REUSE candidate pending bounded target-side proof.
  - OAM-036 through OAM-039 must not start before OAM-035 target proof governance lifecycle and durable reconciliation are complete.
unknown:
  - Exact focused target proof boundary and resulting final REUSE or ADAPT disposition until OAM-035 target-side validation is executed.
  - Whether bounded target proof will expose a target-specific creature-ai defect requiring ADAPT.
conflicts: []
first_failure:
  marker: none
  evidence: No OAM-035 implementation or target validation failure exists because this task is preflight-only.
rejected_hypotheses:
  - Select creature-ai before OAM-034 closure; its only hard dependency was creature-definitions and is now satisfied.
  - Treat legacy Canary as the stronger whole-module creature-ai donor; target and fresh upstream share the same newer modular owned core while legacy differs.
  - Start OAM-036 through OAM-039 in parallel; the program requires one bounded OAM package and full lifecycle reconciliation at a time.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-oteryn-oam035-preflight.md
validation:
  - command: PR 707 preflight CI and Agent Task Ownership on bb0554c8fa94fe0908be2cfa2ce7e371743382ed
    result: PASS
    evidence: CI run 29899266233 and Agent Task Ownership run 29899265812 succeeded.
  - command: fresh dependency ownership baseline and semantic donor preflight
    result: PASS
    evidence: creature-ai dependency is satisfied no overlapping open writer was found exact baselines were pinned and target/upstream owned blobs match while legacy diverges from the newer modular core.
blockers: []
next_action: Merge PR 707 after exact-current-head required checks pass, then obtain explicit authorization for writes to blakinio/Otheryn before creating the bounded OAM-035 creature-ai target proof at Otheryn baseline 4771350b44665c5a37b0c058b3d413c0c0de542d.
```
