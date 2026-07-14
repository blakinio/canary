---
task_id: CAN-20260714-tibia-system-decomposition-world-content
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-008
status: active
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition-world-content
base_branch: main
created: 2026-07-15T00:50:00+02:00
updated: 2026-07-15T01:12:00+02:00
last_verified_commit: "360e478cbebc756f60933e547801307e7db805e7"
risk: low
related_issue: ""
related_pr: "368"
depends_on:
  - completed and archived TSD-007
blocks:
  - TSD-009 social communication and trust decomposition
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260714-tibia-system-decomposition-world-content.md
    - docs/agents/real-tibia/TSD_008_WORLD_CONTENT_REPORT.md
    - docs/agents/real-tibia/registry/modules/world-map-runtime.yaml
    - docs/agents/real-tibia/registry/modules/world-zones.yaml
    - docs/agents/real-tibia/registry/modules/instances.yaml
    - tools/agents/test_world_registry.py
    - tools/agents/test_upstream_intelligence_world.py
  shared:
    - docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
    - docs/agents/real-tibia/generated/**
    - tools/agents/test_items_registry.py
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/real-tibia/registry/modules/quests.yaml
    - docs/agents/real-tibia/registry/modules/npcs.yaml
    - docs/agents/real-tibia/registry/modules/houses.yaml
    - docs/agents/real-tibia/registry/modules/otbm-tooling.yaml
    - docs/agents/real-tibia/registry/modules/raids.yaml
    - docs/agents/real-tibia/registry/modules/spawns.yaml
    - docs/agents/real-tibia/registry/modules/containers.yaml
    - docs/agents/real-tibia/registry/modules/item-instances.yaml
    - docs/agents/real-tibia/registry/modules/world-persistence.yaml
    - tools/agents/real_tibia_registry*.py
    - tools/agents/upstream_intelligence*.py
    - .github/workflows/**
    - src/map/**
    - src/items/tile.*
    - src/io/iomap.*
    - src/game/zones/**
    - src/game/instance/**
    - tests/unit/game/instance/**
modules_touched:
  - Real Tibia module registry
  - runtime world map
  - world zones
  - instances
reuses:
  - existing registry/generator/mapper
  - existing OTBM tooling
  - existing InstanceManager foundation
public_interfaces:
  - bounded runtime world discovery records
cross_repo_tasks: []
---

# Goal

Complete bounded TSD-008 world-content inventory. Preserve quests, NPCs, houses, OTBM tooling, raids, spawns, item/container and persistence records. Add only durable runtime map, world-zone and instance lifecycles supported by verified current paths.

# Exact base and preflight

- Task-start main: `350739e5df12db5f3c749540a36bb7c3922cc5ee`.
- TSD-007 feature/lifecycle were merged first.
- Open PRs #360 protocol/session, #316 donor-map/content audit and #245 physical-client E2E remained read-only and non-overlapping.
- `ACTIVE_WORK.md` remained read-only.

# Delivered result

Registry records: 49 → 52. Added only:

- `instances`;
- `world-map-runtime`;
- `world-zones`.

Existing records modified: 0. Quests, NPCs, houses, OTBM tooling, raids, spawns, item/container, persistence and physical-client E2E boundaries remain stable.

# Classification

- Map/MapCache/Tile/IOMap, spatial lookup, movement, visibility and pathfinding → `world-map-runtime`.
- Static/dynamic zone registry, area indexing, membership caches and remove destination → `world-zones`.
- Configured region pool, instance state, creature ownership isolation, cleanup and expiration → `instances`.
- Map loading, tiles, movement, pathfinding, towns and waypoints remain capabilities inside runtime map.
- Teleports and floor transitions remain deferred findings because they lack one independent current root.
- NPC/boat/carpet travel remains inside NPC/quest boundaries.
- Houses, spawns, raids, OTBM analysis and world persistence remain already covered.

Detailed evidence: `docs/agents/real-tibia/TSD_008_WORLD_CONTENT_REPORT.md`.

# Validation and repair history

Implementation/focused-test head `360e478cbebc756f60933e547801307e7db805e7`:

- Real Tibia Module Registry #330: success;
- Upstream Intelligence #362: success;
- Agent Task Ownership #1186: success;
- repository CI #2304: success;
- focused registry/source-role tests: success;
- schema and dependency graph validation: success;
- deterministic `generate --check`: success;
- discovery and exact PR-range `affected`: success.

Repair history:

1. New records initially used wall-clock inventory date `2026-07-15`, while generated freshness is pinned to the registry baseline date `2026-07-14`. The three records were aligned to the existing baseline without modifying versions/baselines.
2. The first manual path-index materialization accidentally removed the pre-existing `src/io/iobestiary.* → cyclopedia` row. Focused tests/schema passed but `generate --check` failed. The row was restored; no TSD-008 path, module scope or runtime behavior changed.

Later program and task-record commits are documentation-only. This record cannot embed its own final SHA; live PR #368 metadata and exact-head workflows remain authoritative before merge.

# Acceptance criteria

- [x] Added only three confirmed records.
- [x] Preserved all existing module records unchanged.
- [x] Classified all TSD-008 candidates explicitly.
- [x] Used verified narrow paths and conservative maturity.
- [x] Regenerated deterministic indexes through the existing generator.
- [x] Added focused registry and source-role mapping tests.
- [x] Passed registry/UI/ownership/repository CI at the implementation head.
- [ ] Exact final-head and ready-state Linux/Required must pass before merge.
- [x] Made no runtime, gameplay, protocol, client, DB, map, OTBM, datapack, asset, workflow or E2E implementation change.

# Safety limits

Inventory does not prove OTBM runtime loading, map completeness, movement/pathfinding, visibility, zone membership, teleport/travel behavior, instance isolation/cleanup/expiration, persistence, runtime behavior, physical-client E2E or parity.

# Handoff

After PR #368 passes exact final-head review and ready-state CI, squash merge it and archive this task in a lifecycle-only PR. Only after that archive merges may TSD-009 start from then-current `main`:

```text
task: CAN-20260714-tibia-system-decomposition-social-communication-trust
package: TSD-009
branch: docs/tibia-system-decomposition-social-communication-trust
```
