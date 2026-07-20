---
task_id: CAN-20260720-oteryn-oam028-cyclopedia-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-028
status: implementing
agent: "GPT-5.5 Thinking"
branch: docs/oam-028-cyclopedia-preflight
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "85b26b41510101259f6138f2c864bf0c4a473f2a"
risk: medium
related_pr: ""
owned_paths:
  - docs/agents/tasks/active/CAN-20260720-oteryn-oam028-cyclopedia-preflight.md
  - docs/agents/OTERYN_OAM_028_CYCLOPEDIA_REVALIDATION.md
depends_on:
  - completed OAM protocol
  - completed OAM player-persistence
blocks:
  - OAM-029
modules_touched:
  - cyclopedia
---

# Goal

Revalidate canonical OAM-028 `cyclopedia` as the broad compatibility/discovery umbrella, preserve already separated child ownership, deliver the smallest evidence-backed target proof, close governance/lifecycle, then reconcile the durable Oteryn migration program before OAM-029 starts.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20T22:42:00Z
head: 85b26b41510101259f6138f2c864bf0c4a473f2a
branch: docs/oam-028-cyclopedia-preflight
pr: none
status: investigating
context_routes:
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
  - docs/agents/real-tibia/registry/modules/cyclopedia.yaml
  - docs/agents/real-tibia/TSD_004_CYCLOPEDIA_FAMILY_REPORT.md
owned_paths:
  - docs/agents/tasks/active/CAN-20260720-oteryn-oam028-cyclopedia-preflight.md
  - docs/agents/OTERYN_OAM_028_CYCLOPEDIA_REVALIDATION.md
proven:
  - OAM-001..OAM-027 are durably complete and OAM-027 target checkpoint is archived.
  - Task-start Canary main is 85b26b41510101259f6138f2c864bf0c4a473f2a.
  - Task-start Otheryn main is 2a008f1c8cfa679c9b70281e4c8c16120a7567fa.
  - Fresh upstream Canary is 71a0f92b4da3f550b292fa7536a0e35c2769f1ae.
  - Maintained OTClient is a6868920443dc285656bd016acdb2c1ea566e511.
  - Canonical cyclopedia depends only on completed protocol and player-persistence.
  - TSD-004 preserves cyclopedia as a broad compatibility/discovery umbrella and assigns independent durable child roots to bestiary, bosstiary, cyclopedia-character and titles; charms and houses retain their existing independent records.
  - Task-start Otheryn and fresh upstream share protocolgame.hpp blob 082d66596a424fc44143298c41fe01ff4007a439.
  - Task-start Otheryn, fresh upstream and legacy share player_cyclopedia.hpp enum blob 45fed9ad2f3b7e35bdc7afd9dbd52d5d1b736311.
  - Merged legacy PR 188 contains Bestiary, Bosstiary, Charms and Cyclopedia Character child-boundary runtime fixes and explicitly no protocol or maintained-OTClient change.
  - Merged legacy PR 192 contains Bestiary/Bosstiary monster-data corrections and explicitly no protocol or maintained-OTClient change.
  - Cyclopedia validation PR 243 is validator/workflow control only and does not provide an umbrella runtime donor.
  - Current open Canary PR 514 changes security runtime tooling/tests/docs only and does not touch production protocol paths; PRs 637/646 own NPC E2E and OTBM E2E work respectively.
derived:
  - The smallest evidence-backed OAM-028 disposition candidate is cyclopedia REUSE with proof-only target evidence, preserving completed OAM-006 protocol architecture and all TSD-004 child ownership boundaries.
unknown:
  - Exact final target CI evidence until the target proof PR is gated.
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - Import PR 188 wholesale as umbrella Cyclopedia work; rejected because its production fixes belong to bestiary, bosstiary, charms and cyclopedia-character child boundaries.
  - Import PR 192 as umbrella Cyclopedia work; rejected because it is Bestiary/Bosstiary data ownership.
  - Treat broad cyclopedia registry path hints as exclusive edit ownership; rejected by TSD-004 many-to-many discovery contract.
changed_paths: []
validation:
  - command: fresh live-state/open-PR/ownership audit
    result: PASS
    evidence: exact task-start SHAs pinned; no active production writer overlaps the proof-only target boundary
  - command: canonical dependency and TSD-004 child-boundary audit
    result: PASS
    evidence: protocol/player-persistence complete; child roots remain separately owned
blockers: []
next_action: Create dedicated Otheryn branch dudantas/oam-028-cyclopedia-reuse from target main 2a008f1c8cfa679c9b70281e4c8c16120a7567fa and add proof-only evidence/tests for the existing Cyclopedia umbrella protocol surface and TSD-004 child delegation; do not mutate production protocol, child runtime/data or maintained OTClient paths.
```
