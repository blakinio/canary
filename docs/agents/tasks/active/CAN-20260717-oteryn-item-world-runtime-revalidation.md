---
task_id: CAN-20260717-oteryn-item-world-runtime-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: "OAM-007"
status: investigating
agent: oteryn-architecture-migration-agent
branch: docs/oam-007-item-world-runtime-revalidation
base_branch: main
created: 2026-07-17T06:45:00+02:00
updated: 2026-07-17T07:32:00+02:00
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
---

# Goal

Revalidate exactly three dependency-ordered canonical foundation modules — `item-definitions`, `item-instances`, and `world-map-runtime` — against fresh exact target, legacy and upstream baselines. Select one evidence-backed disposition per module, change Otheryn only when target adaptation is proven necessary, and stop before `world-zones`, `instances`, OAM-008 or any broad world-content migration.

# Pinned task-start baselines

- Canary/governance: `c2e181f892ce2f094e887f1da5c6c7df207629c9`
- Otheryn target: `c547d8ad70ef1252624c255476e6cb83fa125e14`
- upstream evidence: `opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f`
- maintained client evidence when runtime proof requires it: `blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

# Canonical dependency order

1. `item-definitions`
2. `item-instances` depends on `item-definitions`
3. `world-map-runtime` depends on both item modules

`world-zones` and `instances` are downstream and explicitly out of scope.

# Preflight evidence

- OAM-006 feature and lifecycle are complete; lifecycle merge is `b0ea0ba9508cc78d5580f44181115e9b304eb7da`.
- Fresh OAM-007 Canary task-start is `c2e181f892ce2f094e887f1da5c6c7df207629c9`.
- Otheryn has no open PR at task start.
- Open Canary PRs #451 and #453 are security-scoped and do not claim item/map runtime implementation ownership.
- Core exact-blob checks already show Otheryn equals upstream for `src/items/items.cpp`, `src/items/item.cpp`, `src/io/iomap.cpp`, `src/map/map.cpp`, `src/map/map.hpp`, `src/items/tile.cpp`, `src/items/tile.hpp`, `src/map/mapcache.cpp`, `src/map/mapcache.hpp` and `src/map/spectators.cpp`.
- Legacy Canary contains local deltas in at least `src/items/functions/item/item_parse.cpp`, `src/map/map.cpp`, `src/map/map.hpp`, `src/items/tile.cpp`, `src/items/tile.hpp` and `src/map/mapcache.cpp`; these are evidence candidates only and are not migration authorization.
- Otheryn issue #22 is the bounded target-side tracking issue; Canary draft PR #455 is the governance boundary.

# Investigation rules

- Do not infer `REUSE` from file presence alone.
- Do not port legacy map/item deltas without a concrete requirement, focused test or runtime proof that the upstream-aligned target lacks required behavior.
- Do not bulk-copy item/map directories or datapacks.
- Preserve OAM-004 persistence boundaries; item serialization evidence does not imply SQL/KV atomicity.
- Preserve OAM-006 protocol/client contract; no protocol or maintained-client mutation belongs here without separate exact evidence.
- Reuse existing Universal Agent E2E capabilities if physical runtime proof is applicable; do not create another orchestrator.
- Do not claim map completeness, Real Tibia parity, exhaustive movement/pathfinding correctness or item-value parity from foundation validation.

# Working hypotheses

| Module | Working disposition | Current reason |
|---|---|---|
| `item-definitions` | `REUSE` candidate | target core registry matches upstream; legacy parser delta still requires provenance/necessity review |
| `item-instances` | `REUSE` candidate | target runtime item core matches both legacy and upstream on the checked principal implementation; remaining attribute/serialization paths still require exact matrix completion |
| `world-map-runtime` | `REUSE` candidate | target matches upstream across checked principal runtime files; legacy Map/Tile/MapCache deltas require explicit proof before any port |

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T07:32:00+02:00
head: 205f0e8dd95cf19a52ea2e9250584b696db18868
branch: docs/oam-007-item-world-runtime-revalidation
pr: 455
status: investigating
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
  - canonical dependency order is item-definitions -> item-instances -> world-map-runtime
  - Otheryn principal checked item/map runtime blobs are upstream-aligned
  - legacy contains bounded local item/map deltas that are not automatically authorized for target
  - Otheryn issue 22 and Canary PR 455 bind the bounded cross-repository work
unknown:
  - final disposition for each of the three modules
  - whether any legacy delta has proven target value
  - whether a target code PR is required
  - exact focused/runtime/physical validation package
conflicts: []
first_failure:
  marker: none active
  evidence: preflight and ownership scope are clean
rejected_hypotheses:
  - legacy Canary is the target image
  - any Map/Tile/MapCache difference must be ported
  - item serializer presence proves persistence atomicity
  - world-zones or instances belong in OAM-007
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-oteryn-item-world-runtime-revalidation.md
  - docs/agents/OTERYN_OAM_007_ITEM_WORLD_RUNTIME_REVALIDATION.md
validation:
  - command: exact principal blob matrix
    result: IN_PROGRESS
    evidence: target/upstream alignment established for principal checked item/map files; remaining module paths and legacy-delta necessity review pending
blockers: []
next_action: Complete the exact module-path matrix and legacy-delta necessity review; create a target PR only if adaptation is proven necessary.
```
