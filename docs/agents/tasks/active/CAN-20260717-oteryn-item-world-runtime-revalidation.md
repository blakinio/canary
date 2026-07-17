---
task_id: CAN-20260717-oteryn-item-world-runtime-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: "OAM-007"
status: implementing
agent: oteryn-architecture-migration-agent
branch: docs/oam-007-item-world-runtime-revalidation
base_branch: main
created: 2026-07-17T06:45:00+02:00
updated: 2026-07-17T08:15:00+02:00
last_verified_commit: "c2e181f892ce2f094e887f1da5c6c7df207629c9"
risk: high
related_issue: "22"
related_pr: "455"
depends_on:
  - OAM-003
  - OAM-004
  - OAM-006
blocks:
  - OAM-008
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260717-oteryn-item-world-runtime-revalidation.md
    - docs/agents/OTERYN_OAM_007_ITEM_WORLD_RUNTIME_REVALIDATION.md
  shared:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  read_only:
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/item-definitions.yaml
    - docs/agents/real-tibia/registry/modules/item-instances.yaml
    - docs/agents/real-tibia/registry/modules/world-map-runtime.yaml
    - docs/agents/real-tibia/TSD_007_ITEMS_ECONOMY_REPORT.md
    - docs/agents/real-tibia/TSD_008_WORLD_CONTENT_REPORT.md
    - blakinio/canary@c2e181f892ce2f094e887f1da5c6c7df207629c9
    - blakinio/Otheryn@c547d8ad70ef1252624c255476e6cb83fa125e14
    - opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f
    - blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
modules_touched:
  - item-definitions
  - item-instances
  - world-map-runtime
reuses:
  - docs/agents/OTERYN_OAM_003_ENGINE_FOUNDATION_REVALIDATION.md
  - docs/agents/OTERYN_OAM_004_PERSISTENCE_FOUNDATION_REVALIDATION.md
  - docs/agents/OTERYN_OAM_006_NETWORK_LOGIN_PROTOCOL_REVALIDATION.md
  - Universal Agent E2E
public_interfaces:
  - static item definition loading and lookup
  - runtime item construction and serialization boundary
  - map and tile runtime loading, spatial lookup, movement, visibility and pathfinding
cross_repo_tasks:
  - blakinio/Otheryn#22
  - blakinio/Otheryn#23
---

# Goal

Revalidate exactly `item-definitions`, `item-instances`, and `world-map-runtime`, adapt Otheryn only where evidence proves necessity, and stop before downstream world modules or OAM-008.

# Current dispositions

| Module | Disposition candidate | Evidence |
|---|---|---|
| `item-definitions` | `ADAPT` | Canary PR #81 proves the missing magic-field add-item handler; Otheryn PR #23 is the bounded adaptation |
| `item-instances` | `REUSE` | checked principal runtime paths are identical across task-start target, legacy, and upstream |
| `world-map-runtime` | `REUSE` | target/upstream align on checked runtime paths; legacy map fork has no proven target necessity |

# Safety

- Do not bulk-copy legacy item/map code or datapacks.
- Preserve OAM-004 persistence boundaries and OAM-006 protocol/client boundaries.
- Do not start `world-zones`, `instances`, or OAM-008 here.
- Reuse the existing Universal Agent E2E for exact final-target runtime proof.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T08:15:00+02:00
head: de826aa4b448b2f2e3ba6062a412adb5cb14ccd0
branch: docs/oam-007-item-world-runtime-revalidation
pr: 455
status: implementing
context_routes:
  - agent-governance
  - item-definitions
  - item-instances
  - world-map-runtime
owned_paths:
  - docs/agents/tasks/active/CAN-20260717-oteryn-item-world-runtime-revalidation.md
  - docs/agents/OTERYN_OAM_007_ITEM_WORLD_RUNTIME_REVALIDATION.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
proven:
  - OAM-006 feature and lifecycle are complete
  - Canary task-start is c2e181f892ce2f094e887f1da5c6c7df207629c9
  - Otheryn task-start is c547d8ad70ef1252624c255476e6cb83fa125e14
  - upstream evidence head is e0ac98e399d0f7e483f3668f57b78fcc45b6e53f
  - maintained client evidence head is 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
  - item-definitions requires bounded ADAPT for verified Canary PR 81 behavior
  - item-instances is a REUSE candidate
  - world-map-runtime is a REUSE candidate
derived:
  - only item-definitions currently requires target code adaptation
  - legacy-only map runtime divergence is insufficient migration authorization
  - final runtime proof must pin the exact post-merge Otheryn revision
unknown:
  - final Otheryn PR 23 merge SHA
  - exact final-target runtime and physical evidence
  - final Canary feature-governance merge SHA
  - final Canary lifecycle merge SHA
conflicts: []
first_failure:
  marker: none active
  evidence: Otheryn PR 23 ready-triggered exact-head CI is running
rejected_hypotheses:
  - legacy Canary is the target image
  - every Map Tile or MapCache difference must be ported
  - the unrelated manual healing-rune part of PR 81 belongs in OAM-007
  - item serializer presence proves persistence atomicity
  - downstream world modules belong in OAM-007
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-oteryn-item-world-runtime-revalidation.md
  - docs/agents/OTERYN_OAM_007_ITEM_WORLD_RUNTIME_REVALIDATION.md
validation:
  - command: exact canonical blob matrix and legacy-delta provenance review
    result: PASS
    evidence: one required item-definition adaptation was isolated; item-instance and world-map runtime legacy-only deltas do not meet the adaptation gate
blockers: []
next_action: Require Otheryn PR 23 exact-head ready gates, merge with exact-head guard, then run exact controlled-server runtime proof before finalizing Canary PR 455.
```
