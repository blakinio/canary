---
task_id: CAN-20260717-oteryn-item-world-runtime-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: "OAM-007"
status: implementing
agent: oteryn-architecture-migration-agent
branch: docs/oam-007-item-world-runtime-revalidation
base_branch: main
created: 2026-07-17T06:45:00+02:00
updated: 2026-07-17T08:05:00+02:00
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

Revalidate exactly three dependency-ordered canonical foundation modules — `item-definitions`, `item-instances`, and `world-map-runtime` — against fresh exact target, legacy and upstream baselines. Select one evidence-backed disposition per module, change Otheryn only where target adaptation is proven necessary, and stop before `world-zones`, `instances`, OAM-008 or any broad world-content migration.

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

# Evidence and current dispositions

| Module | Working disposition | Evidence |
|---|---|---|
| `item-definitions` | `ADAPT` | target/upstream parser lacks the PR #81 magic-field add-item handler; merged PR #81 fixed verified upstream issue #3584 with focused policy coverage; Otheryn PR #23 is the bounded adaptation |
| `item-instances` | `REUSE` | checked `item.cpp/.hpp`, `attribute.cpp` and `custom_attribute.cpp` are identical across target, legacy and upstream; no required legacy-only behavior identified |
| `world-map-runtime` | `REUSE` | target/upstream align across checked IOMap/Spectators/Map/Tile/MapCache/MapSector/A* paths and include `navigation_snapshot`; legacy is a distinct Map/Tile/MapCache fork without proven target necessity |

# Target adaptation boundary

Otheryn draft PR #23 is based on exact task-start target `c547d8ad70ef1252624c255476e6cb83fa125e14`.

It only:

- adds the PR #81 pure magic-field registration policy and three-case unit test;
- routes the parser's existing three-argument event registration through a bounded overload;
- preserves the four-argument weapon registration path;
- adds the existing add-item-on-tile handler only for `MOVE_EVENT_STEP_IN + magic field`;
- registers the new translation unit in CMake and the existing Windows MSBuild bridge.

It does not import the unrelated manual healing-rune portion of PR #81 and does not modify legacy Map/Tile/MapCache code, datapacks, protocol or client code.

# Safety rules

- Do not bulk-copy item/map directories or datapacks.
- Preserve OAM-004 persistence boundaries; item serialization evidence does not imply SQL/KV atomicity.
- Preserve OAM-006 protocol/client contract; no protocol or maintained-client mutation belongs here without separate exact evidence.
- Reuse existing Universal Agent E2E for exact final-target runtime proof; do not create another orchestrator.
- Do not claim map completeness, Real Tibia parity, exhaustive movement/pathfinding correctness or item-value parity.
- Do not start `world-zones`, `instances` or OAM-008 inside this package.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T08:05:00+02:00
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
  - canonical dependency order is item-definitions -> item-instances -> world-map-runtime
  - item-definitions requires bounded ADAPT for verified magic-field add-item behavior from Canary PR 81
  - item-instances remains a REUSE candidate with principal checked paths identical across baselines
  - world-map-runtime remains a REUSE candidate; legacy map fork lacks proven target necessity
  - Otheryn issue 22 Canary PR 455 and Otheryn PR 23 bind the bounded cross-repository work
unknown:
  - final Otheryn PR 23 merge SHA
  - exact final-target runtime and physical evidence
  - final Canary feature-governance merge SHA
  - final Canary lifecycle merge SHA
conflicts: []
first_failure:
  marker: none active
  evidence: target PR 23 exact-head CI is running
rejected_hypotheses:
  - legacy Canary is the target image
  - every Map Tile or MapCache difference must be ported
  - the unrelated manual healing-rune part of PR 81 belongs in OAM-007
  - item serializer presence proves persistence atomicity
  - world-zones or instances belong in OAM-007
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-oteryn-item-world-runtime-revalidation.md
  - docs/agents/OTERYN_OAM_007_ITEM_WORLD_RUNTIME_REVALIDATION.md
validation:
  - command: exact canonical blob matrix and legacy-delta provenance review
    result: PASS
    evidence: one required item-definition adaptation isolated to PR 81 behavior; item-instance and world-map runtime legacy-only deltas do not meet the target-adaptation gate
  - command: Otheryn PR 23 exact-head CI
    result: IN_PROGRESS
    evidence: head cd6fae153ebe495ec9030c9c729f2ceef06872ef
blockers: []
next_action: Require Otheryn PR 23 exact-head draft and ready gates, merge with exact-head guard, then run exact controlled-server runtime/physical proof against the final target before finalizing Canary PR 455.
```
