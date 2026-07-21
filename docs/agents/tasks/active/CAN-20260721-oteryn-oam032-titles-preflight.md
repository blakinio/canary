---
task_id: CAN-20260721-oteryn-oam032-titles-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-032
status: investigating
branch: docs/oam-032-titles-preflight
base_branch: main
created: 2026-07-21
updated: 2026-07-21
related_pr: ""
modules_touched:
  - titles
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-oteryn-oam032-titles-preflight.md
  - docs/agents/OTERYN_OAM_032_TITLES_REVALIDATION.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/REPOSITORY_MAP.md
  - docs/agents/CONTEXT_ROUTING.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  - docs/agents/real-tibia/registry/modules/titles.yaml
search_first:
  - src/creatures/players/components/player_title.cpp
  - src/creatures/players/components/player_title.hpp
  - open PR ownership overlapping titles/player_title
optional_reads:
  - docs/agents/real-tibia/TSD_004_CYCLOPEDIA_FAMILY_REPORT.md
---

# OAM-032 Titles preflight

## Goal

Perform a fresh bounded OAM-032 revalidation of canonical `titles` after OAM-031 completion. Determine `REUSE`, `ADAPT`, or another evidence-backed disposition without importing separately owned Cyclopedia, Bestiary, Bosstiary, Charms, protocol, client, outfit, mount, familiar, map, or unrelated runtime work.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T22:00:00+02:00
head: db7cf6af480285ad4a87c3be2981a873f175eab6
branch: docs/oam-032-titles-preflight
pr: none
status: investigating
context_routes:
  - architecture
  - testing
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-oteryn-oam032-titles-preflight.md
  - docs/agents/OTERYN_OAM_032_TITLES_REVALIDATION.md
proven:
  - OAM-031 bestiary target, governance, lifecycle, durable reconciliation and target-task cleanup are complete.
  - OAM-031 durable reconciliation merged in Canary as 819e4f9d19f71a06dacb4d395734f47ebc03422d.
  - OAM-031 target-task archive merged in Otheryn as ad2bd2f187df057c47d05c121351159ce30cc457.
  - Fresh preflight selected titles as the smallest dependency-valid candidate ahead of broader charms.
  - Canonical titles depends only on completed cyclopedia-character and player-persistence.
  - Canonical titles server root is src/creatures/players/components/player_title.*.
  - Task-start Canary main is db7cf6af480285ad4a87c3be2981a873f175eab6.
  - Task-start Otheryn main is ad2bd2f187df057c47d05c121351159ce30cc457.
  - Fresh upstream Canary main is 71a0f92b4da3f550b292fa7536a0e35c2769f1ae.
  - Maintained OTClient main is a6868920443dc285656bd016acdb2c1ea566e511.
  - Task-start Otheryn and fresh upstream player_title.cpp share blob c885d5ee55970d8ce93a80bb477bc317fb9faa98.
  - Task-start Otheryn, fresh upstream and legacy player_title.hpp share blob 118806fee9ca6d939d73067af14c63c59d291f25.
  - Current open Canary PRs reviewed so far do not overlap canonical player_title.* ownership.
derived:
  - OAM-032 should continue as a narrow titles preflight before charms.
  - Blob identity is supporting evidence only and does not yet prove REUSE.
unknown:
  - Whether current legacy player_title.cpp differs semantically from task-start target/upstream in a Titles-owned way.
  - Whether merged legacy PR history contains bounded Titles-owned corrections that should be adapted.
  - Final OAM-032 disposition and exact proof boundary.
conflicts: []
first_failure:
  marker: none
  evidence: No task-specific validation failure observed.
rejected_hypotheses:
  - Start charms before titles: titles has the narrower canonical root and fewer dependencies.
  - Infer REUSE from shared target/upstream blobs alone: repository rules require semantic evidence.
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-oteryn-oam032-titles-preflight.md
validation:
  - command: live GitHub preflight
    result: PASS
    evidence: Canary/Otheryn/upstream/OTClient task-start SHAs and title root blobs verified; open PR ownership checked narrowly.
blockers: []
next_action: Compare current legacy player_title.cpp and relevant merged legacy PR history against task-start Otheryn/upstream, isolate only Titles-owned semantic differences, then decide REUSE or ADAPT before any target implementation.
```
