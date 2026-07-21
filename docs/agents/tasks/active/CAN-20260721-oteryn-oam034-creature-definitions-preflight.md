---
task_id: CAN-20260721-oteryn-oam034-creature-definitions-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-034
status: implementing
branch: docs/oam-034-creature-definitions-preflight
base_branch: main
created: 2026-07-21
updated: 2026-07-21
modules_touched:
  - creature-definitions
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-oteryn-oam034-creature-definitions-preflight.md
  - docs/agents/OTERYN_OAM_034_CREATURE_DEFINITIONS_REVALIDATION.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  - docs/agents/real-tibia/registry/modules/creature-definitions.yaml
search_first:
  - merged legacy PR #192 monster-definition data
  - selected six monster definition files across target upstream and legacy
  - open PR ownership overlapping creature-definitions
---

# OAM-034 Creature definitions preflight

## Goal

Govern the bounded OAM-034 `creature-definitions → ADAPT` package selected from reviewed legacy PR #192 without importing Creature AI, spawn, raid, boss-encounter, Cyclopedia validator or unrelated runtime/data work.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T23:58:00+02:00
head: 9a5709bee7083b4fd43c7ae0a91765874349c019
branch: docs/oam-034-creature-definitions-preflight
status: implementing
context_routes:
  - agent-governance
  - cross-repo
  - testing
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-oteryn-oam034-creature-definitions-preflight.md
  - docs/agents/OTERYN_OAM_034_CREATURE_DEFINITIONS_REVALIDATION.md
proven:
  - OAM-033 is fully complete through Canary reconciliation ab2fb5548260544f42f786d11d4dd1b600c39a06 and Otheryn target archive 2fe646dfff3d4fc0672c3fbeca85708dabc4ce87.
  - Canonical creature-definitions has no fundamental dependencies and owns monster definition data.
  - OAM-034 task-start baselines are Canary ab2fb5548260544f42f786d11d4dd1b600c39a06, Otheryn 2fe646dfff3d4fc0672c3fbeca85708dabc4ce87, upstream 71a0f92b4da3f550b292fa7536a0e35c2769f1ae and maintained OTClient 465b7a2192b176cf8cb9d58e000c38863e4a6e4c.
  - Final selected disposition is creature-definitions ADAPT with exactly six production corrections from merged legacy PR 192.
  - Every selected task-start target file equals fresh upstream pre-fix content and current legacy preserves the exact reviewed correction.
  - PR 192 validator tests logs and governance files are excluded from the target package.
  - Otheryn PR 69 initial head dabc868c5ff9ca8009f20f1eb90645937ff18e22 contains exactly ten intended target paths.
  - No open target PR and no open Canary monster or creature-definitions PR overlapped the selected production boundary during fresh preflight.
  - Canary main advanced after task start only by unrelated OTBM lifecycle archive work before this governance branch was created.
derived:
  - The smallest valid OAM-034 package is six production definition files plus focused target proof task and evidence.
unknown:
  - Exact final target CI merge and artifact evidence until Otheryn PR 69 validation completes.
conflicts: []
first_failure:
  marker: none
  evidence: No OAM-034 implementation or validation failure has been observed at governance checkpoint creation.
rejected_hypotheses:
  - Expand creature-definitions to Creature AI spawns raids or boss encounters; canonical registry keeps those packages separate.
  - Import all PR 192 validator infrastructure into Otheryn; it is not required by the selected production correction boundary.
changed_paths:
  - docs/agents/OTERYN_OAM_034_CREATURE_DEFINITIONS_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260721-oteryn-oam034-creature-definitions-preflight.md
validation:
  - command: fresh dependency donor ownership and six-file comparison preflight
    result: PASS
    evidence: dependency-valid package exact target/upstream pre-fix equality exact legacy corrections and no overlapping live writer
blockers: []
next_action: Wait for exact-head Otheryn PR 69 validation; if clean audit scope comments reviews threads and target main drift then expected-head squash merge. Update this governance package with final target evidence before exact-head Ownership and final-gate CI.
```
