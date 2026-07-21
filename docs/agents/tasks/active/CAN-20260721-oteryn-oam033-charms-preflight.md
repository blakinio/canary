---
task_id: CAN-20260721-oteryn-oam033-charms-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-033
status: implementing
branch: docs/oam-033-charms-preflight
base_branch: main
created: 2026-07-21
updated: 2026-07-21
related_pr: "696"
modules_touched:
  - charms
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-oteryn-oam033-charms-preflight.md
  - docs/agents/OTERYN_OAM_033_CHARMS_REVALIDATION.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/REPOSITORY_MAP.md
  - docs/agents/CONTEXT_ROUTING.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  - docs/agents/real-tibia/registry/modules/charms.yaml
search_first:
  - merged legacy PR #188 Charm-owned hunk
  - src/creatures/players charm state and effect paths
  - src/server/network/protocol charm packet paths
  - data/scripts/lib/register_bestiary_charm.lua
  - open PR ownership overlapping charms
optional_reads:
  - docs/agents/real-tibia/TSD_004_CYCLOPEDIA_FAMILY_REPORT.md
  - docs/ai-agent/CYCLOPEDIA_FIX_LOG.md
---

# OAM-033 Charms preflight

## Goal

Perform a fresh bounded OAM-033 revalidation of canonical `charms` after complete OAM-032 closure. Determine the smallest evidence-backed `REUSE` or `ADAPT` boundary without importing separately owned Bestiary, Bosstiary, Titles, generic combat, protocol, maintained-client, monster-data, map, asset, schema, deployment, or unrelated runtime work.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T23:35:00+02:00
head: 6e8ff0e2ddad845ba7d685ab1bc1608af1054d57
branch: docs/oam-033-charms-preflight
pr: 696
status: validating
context_routes:
  - agent-governance
  - cpp-runtime
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-oteryn-oam033-charms-preflight.md
  - docs/agents/OTERYN_OAM_033_CHARMS_REVALIDATION.md
proven:
  - OAM-032 titles is fully complete with durable Canary reconciliation merge f05ea5e916af00ab1469a2332aaec2d3c9df7478.
  - OAM-032 target-task archive is complete in Otheryn at 1a4bbceda2c805bc69c68c1592e04e63d7e9a269.
  - Canonical charms depends on combat cyclopedia player-persistence and protocol; all four dependencies are completed OAM foundations.
  - TSD-004 preserves independent Charm ownership for definitions costs unlock state assignment and combat effects even where IOBestiary hosts Charm helpers.
  - Task-start Canary main is f05ea5e916af00ab1469a2332aaec2d3c9df7478.
  - Task-start Otheryn main is 1a4bbceda2c805bc69c68c1592e04e63d7e9a269.
  - Fresh upstream Canary main is 71a0f92b4da3f550b292fa7536a0e35c2769f1ae.
  - Maintained OTClient main is a6868920443dc285656bd016acdb2c1ea566e511.
  - Open Canary PRs do not overlap either selected Charm production path or OAM-033 governance paths and Otheryn had no competing open writer at preflight.
  - Merged legacy PR 188 supplies exactly two selected Charm-owned corrections: the mask.category registration guard and reset-all surcharge only for levels above 100.
  - PR 188 Bestiary Bosstiary and Cyclopedia Character hunks are separately completed OAM packages; PR 192 is monster data and PR 243 is validator control.
  - Otheryn PR 67 final head e1fca0b372173db335118735f501f315d442888f changed exactly seven intended paths and no temporary helper/workflow path.
  - Initial target CI 230 isolated one superseded OAM-031 old-Charm-formula boundary assertion; both OAM-033 focused tests passed and no production repair was required.
  - Final target autofix 192 Repository Audit 27 CI 233 Required 218 and Linux-debug full Run Tests succeeded.
  - Final target test-log artifact 8510218346 digest is sha256:1bc7425f036bb5f39c19539590da0704f026718e4bbd54ad2ede79c023300cbc.
  - Target comments reviews threads were empty and Otheryn main had no task-start drift.
  - Otheryn PR 67 merged as c887318a676998da5ef3224a3aa8d1e0df75e607.
derived:
  - OAM-033 final disposition is charms ADAPT with exactly two production corrections and one prior-package proof-boundary maintenance change.
unknown:
  - Exact final Canary governance gate evidence until PR 696 validation completes.
conflicts: []
first_failure:
  marker: superseded OAM-031 ownership-boundary assertion
  evidence: Initial target Linux-debug full suite passed 421 of 422 tests; the sole failure required the intentionally superseded old Charm reset-price formula and was retired without production change.
rejected_hypotheses:
  - Whole-module reuse based on broad path overlap; the reviewed donor contains two concrete Charm-owned corrections absent from target and upstream.
  - Treat the initial target test failure as a production regression; the failing assertion belonged to the pre-OAM-033 exclusion boundary and both new Charm proofs passed.
  - Import Bestiary Bosstiary or Cyclopedia Character donor hunks under Charm ownership; those are separately completed packages.
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-oteryn-oam033-charms-preflight.md
  - docs/agents/OTERYN_OAM_033_CHARMS_REVALIDATION.md
validation:
  - command: live dependency donor ownership and open-PR preflight
    result: PASS
    evidence: two bounded Charm-owned PR 188 corrections selected with no current writer overlap
  - command: Otheryn PR 67 exact-head target gates
    result: PASS
    evidence: final head e1fca0b372173db335118735f501f315d442888f passed autofix 192 Repository Audit 27 CI 233 Required 218 and Linux-debug full Run Tests before merge c887318a676998da5ef3224a3aa8d1e0df75e607
blockers: []
next_action: Mark PR 696 ready, apply final-gate, require exact-head Agent Task Ownership and CI success, audit exactly two governance paths plus comments reviews threads and Canary main drift, then expected-head squash merge before separate lifecycle and durable reconciliation.
```
