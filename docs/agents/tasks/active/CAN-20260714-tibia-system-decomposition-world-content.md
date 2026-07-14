---
task_id: CAN-20260714-tibia-system-decomposition-world-content
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-008
status: active
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition-world-content
base_branch: main
created: 2026-07-15T00:50:00+02:00
updated: 2026-07-15T00:50:00+02:00
last_verified_commit: "350739e5df12db5f3c749540a36bb7c3922cc5ee"
risk: low
related_issue: ""
related_pr: ""
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
- Open PRs #360 protocol/session, #316 donor-map/content audit and #245 physical-client E2E remain read-only and non-overlapping.
- `ACTIVE_WORK.md` remains read-only.

# Boundary decision

- `world-map-runtime`: runtime Map/Tile/IOMap loading, tile materialization, placement, movement, visibility, pathfinding and spatial lookup.
- `world-zones`: static/dynamic zone registry, area indexing, membership caches and remove-destination lifecycle.
- `instances`: configured map-region pool, Creating/Active/Closing/Destroyed lifecycle, creature ownership isolation, cleanup and expiration.

Map loading, tiles, movement and pathfinding stay one runtime-map boundary. Towns, waypoints, teleports, floor transitions and NPC travel remain capabilities/findings because they lack an independent current implementation root. Quests, NPCs, houses, spawns, raids, OTBM tooling and persistence remain existing records.

# Acceptance criteria

- [ ] Add only three confirmed records.
- [ ] Preserve all existing module records unchanged.
- [ ] Classify all TSD-008 candidates explicitly.
- [ ] Use verified narrow paths and conservative maturity.
- [ ] Regenerate deterministic indexes through the existing generator.
- [ ] Add focused registry and source-role mapping tests.
- [ ] Pass exact-head registry/UI/ownership/repository CI and ready-state Linux/Required.
- [ ] Make no runtime, gameplay, protocol, client, DB, map, OTBM, datapack, asset, workflow or E2E implementation change.

# Safety limits

Inventory does not prove OTBM load correctness, map completeness, movement/pathfinding, zone membership, teleport/travel behavior, instance isolation/cleanup/expiration, persistence, runtime behavior or parity.

# Handoff

After feature merge, archive this task in a separate lifecycle-only PR. Only after that archive merges may TSD-009 start from then-current `main`.