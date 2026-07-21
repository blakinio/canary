---
task_id: CAN-20260721-oteryn-oam030-bosstiary-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-030
status: ready
agent: "GPT-5.6 Thinking"
branch: docs/oam-030-bosstiary-preflight
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "af27845b130a87d92f2794c2817d77cfe6d84825"
risk: medium
related_pr: "659"
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-oteryn-oam030-bosstiary-preflight.md
  - docs/agents/OTERYN_OAM_030_BOSSTIARY_REVALIDATION.md
depends_on:
  - completed OAM-028 cyclopedia
  - completed OAM player-persistence
blocks:
  - OAM-031
modules_touched:
  - bosstiary
---

# Goal

Revalidate canonical OAM-030 `bosstiary`, adapt only the independently reviewed missing boosted-boss-row initialization defect, close target/governance/lifecycle, then reconcile the durable Oteryn migration program before OAM-031 starts.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T10:20:00+02:00
head: 504c3f71477fb1d42bdfe746a23c9a1edfc730e7
branch: docs/oam-030-bosstiary-preflight
pr: 659
status: ready
context_routes:
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  - docs/agents/OTERYN_OAM_030_BOSSTIARY_REVALIDATION.md
  - docs/agents/real-tibia/registry/modules/bosstiary.yaml
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-oteryn-oam030-bosstiary-preflight.md
  - docs/agents/OTERYN_OAM_030_BOSSTIARY_REVALIDATION.md
proven:
  - OAM-001 through OAM-029 are durably complete and OAM-029 target checkpoint is archived.
  - Task-start baselines are Canary 419d0848448c641561e7bc06392a4b17b95213b2 and Otheryn 68d48deea999990b1eab30858f3a85fc9fef7067.
  - Fresh upstream is 71a0f92b4da3f550b292fa7536a0e35c2769f1ae and maintained OTClient is a6868920443dc285656bd016acdb2c1ea566e511.
  - Canonical bosstiary depends on completed cyclopedia and player-persistence and owns src/io/io_bosstiary.*.
  - PR 188 has one isolated Bosstiary donor that makes the missing boosted_boss row recovery reachable and initializes the singleton row.
  - Later legacy multichannel leadership logic and Bestiary Charms monster-data protocol client changes were excluded.
  - Otheryn PR 61 final head 4b6dd3fdca907d2f521cb366322dd5b007aca668 changed exactly five intended paths and no helper path.
  - Exact target autofix 185 CI 223 Required 208 and Linux-debug Run Tests succeeded; comments reviews threads were empty and target main had no drift.
  - PR 61 merged by expected-head squash as dc483d6e8d659d61482da2af7abda9b46b1766ff; Canary task-start drift was only independent OTBM lifecycle and governance was rebuilt on af27845b130a87d92f2794c2817d77cfe6d84825.
derived:
  - Final OAM-030 disposition is bosstiary ADAPT using only the reviewed PR 188 missing-row initialization correction.
unknown:
  - Final Canary governance exact-head gate outcome until PR 659 ready-state Ownership and CI complete.
conflicts: []
first_failure:
  marker: temporary target materializer anchor mismatch
  evidence: helper attempts failed without entering final diff; exact final target gates passed after helpers were removed
rejected_hypotheses:
  - Import current legacy io_bosstiary.cpp wholesale.
  - Select broad Charms before narrower Cyclopedia child packages.
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-oteryn-oam030-bosstiary-preflight.md
  - docs/agents/OTERYN_OAM_030_BOSSTIARY_REVALIDATION.md
validation:
  - command: fresh live-state open-PR ownership dependency and donor audit
    result: PASS
    evidence: no active writer overlapped src/io/io_bosstiary.* and donor scope was one isolated PR 188 hunk
  - command: Otheryn PR 61 exact-head target gate
    result: PASS
    evidence: autofix 185 CI 223 Required 208 Linux-debug Run Tests and merge dc483d6e8d659d61482da2af7abda9b46b1766ff
blockers: []
next_action: Mark Canary PR 659 ready, apply ci:final-gate, require Agent Task Ownership and final-gate CI success on the exact final head, audit exactly two governance files plus comments reviews threads and Canary-main drift, then expected-head squash merge if all gates remain clean.
```
