---
task_id: CAN-20260721-oteryn-oam033-charms-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-033
status: investigating
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
updated_at: 2026-07-21T23:10:00+02:00
head: 27a69c21126613a268786d28aa0669a0b5732fb5
branch: docs/oam-033-charms-preflight
pr: 696
status: investigating
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
  - Canonical charms depends on combat, cyclopedia, player-persistence and protocol; all four dependencies are completed OAM foundations.
  - Canonical charms scope includes charm registry, unlock and cost state, combat effect hooks and Cyclopedia presentation.
  - Canonical charms excludes Bestiary kill-tracking internals except their charm contract.
  - Task-start Canary main is f05ea5e916af00ab1469a2332aaec2d3c9df7478.
  - Task-start Otheryn main is 1a4bbceda2c805bc69c68c1592e04e63d7e9a269.
  - Fresh upstream Canary main is 71a0f92b4da3f550b292fa7536a0e35c2769f1ae.
  - Maintained OTClient main is a6868920443dc285656bd016acdb2c1ea566e511.
  - OAM-031 evidence isolated a merged legacy PR #188 all-Charm reset-price correction and deliberately excluded it from Bestiary ownership.
  - Narrow open-PR search for charm returned no current Canary PR; exact path-level ownership still requires verification before implementation.
derived:
  - Charms is the next dependency-valid canonical candidate after completed Titles.
  - PR #188 supplies a concrete Charm-owned donor candidate that must be semantically revalidated rather than copied wholesale.
unknown:
  - Exact current legacy versus task-start target/upstream Charm-owned semantic differences.
  - Exact production paths belonging to the accepted OAM-033 boundary after ownership refinement.
  - Whether the PR #188 reset-price correction is the only accepted Charm-owned adaptation.
  - Whether maintained OTClient evidence changes the server disposition or remains read-only compatibility evidence.
  - Final OAM-033 disposition and proof boundary.
conflicts: []
first_failure:
  marker: none
  evidence: No OAM-033 task-specific validation failure observed.
rejected_hypotheses:
  - Reopen titles: OAM-032 titles is durably complete and archived.
  - Infer whole-module reuse from broad path overlap: canonical Charm ownership spans multiple interacting surfaces and requires function-level decomposition.
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-oteryn-oam033-charms-preflight.md
validation:
  - command: live GitHub task-start preflight
    result: PASS
    evidence: OAM-032 durable/target cleanup plus Canary/Otheryn/upstream/OTClient heads and narrow open-PR charm search verified.
blockers: []
next_action: Inspect the merged legacy PR #188 Charm-owned reset-price hunk and current Charm-related legacy/target/upstream/client paths, refine exact ownership, then decide the smallest REUSE or ADAPT boundary before any target implementation.
```
