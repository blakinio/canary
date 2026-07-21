---
task_id: CAN-20260721-oteryn-oam031-bestiary-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-031
status: ready
agent: "GPT-5.6 Thinking"
branch: docs/oam-031-bestiary-preflight
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "87c4f71b0deb880da7ba4228bc29e769db2c5818"
risk: medium
related_pr: ""
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-oteryn-oam031-bestiary-preflight.md
  - docs/agents/OTERYN_OAM_031_BESTIARY_REVALIDATION.md
depends_on:
  - completed OAM-028 cyclopedia
  - completed player-persistence
blocks:
  - OAM-032
modules_touched:
  - bestiary
---

# Goal

Revalidate canonical OAM-031 `bestiary`, adapt only independently reviewed Bestiary-owned correctness defects, close target/governance/lifecycle, reconcile the durable Oteryn migration program, and archive the target checkpoint before any OAM-032 starts.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T13:35:00+02:00
head: 87c4f71b0deb880da7ba4228bc29e769db2c5818
branch: docs/oam-031-bestiary-preflight
pr: none
status: ready
context_routes:
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  - docs/agents/OTERYN_OAM_031_BESTIARY_REVALIDATION.md
  - docs/agents/real-tibia/registry/modules/bestiary.yaml
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-oteryn-oam031-bestiary-preflight.md
  - docs/agents/OTERYN_OAM_031_BESTIARY_REVALIDATION.md
proven:
  - OAM-001 through OAM-030 are durably complete and the OAM-030 target checkpoint is archived.
  - Task-start baselines are Canary 9aa582eb6b8ab9444294e08798f628cd053d2428 and Otheryn 6a7e54ee3c9597e3ab265a14c2b783631ef3776f.
  - Fresh upstream is 71a0f92b4da3f550b292fa7536a0e35c2769f1ae and maintained OTClient is a6868920443dc285656bd016acdb2c1ea566e511.
  - Canonical bestiary depends on completed cyclopedia and player-persistence and owns src/io/iobestiary.*.
  - PR 188 supplied two selected Bestiary corrections; Charm reset pricing and PR 192 monster data were excluded.
  - Otheryn PR 63 final head c49796d696448aa168c34629dc9ebcd9fd7a9465 changed exactly five intended paths.
  - Production-only target diff was exactly iobestiary.cpp plus 7 minus 3 and preserved Charm reset pricing.
  - Exact target autofix 187 CI 226 Required 211 and Linux-debug Run Tests succeeded.
  - Target artifact 8493329878 digest is sha256:e99f341683bc432512ddd0dc235204f8b13510cd48eaf9f06c9cdf53d7dbc432.
  - Target comments reviews threads were empty and target main had no drift.
  - PR 63 merged by expected-head squash as 86e4b08c28ede2f35c215a7c2327a579f4a61419.
  - Canary task-start drift to 87c4f71b0deb880da7ba4228bc29e769db2c5818 is independent E2E and OTS/OTBM work with no overlap.
derived:
  - Final OAM-031 disposition is bestiary ADAPT with exactly two reviewed production corrections plus focused proof.
unknown:
  - Final Canary governance exact-head gate outcome until Ownership and final-gate CI complete.
conflicts: []
first_failure:
  marker: none
  evidence: No task-specific validation failure observed.
rejected_hypotheses:
  - Copy current legacy iobestiary.cpp wholesale.
  - Import Charm reset pricing under Bestiary ownership.
  - Import monster-definition changes from PR 192.
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-oteryn-oam031-bestiary-preflight.md
  - docs/agents/OTERYN_OAM_031_BESTIARY_REVALIDATION.md
validation:
  - command: Otheryn PR 63 exact-head target gate
    result: PASS
    evidence: autofix 187 CI 226 Required 211 Linux-debug Run Tests and merge 86e4b08c28ede2f35c215a7c2327a579f4a61419
blockers: []
next_action: Open the two-file Canary governance PR, require exact-head Agent Task Ownership and ci:final-gate CI success, audit comments reviews threads and Canary-main drift, then expected-head squash merge before separate lifecycle closure.
```
