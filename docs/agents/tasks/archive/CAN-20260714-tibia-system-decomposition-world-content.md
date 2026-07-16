---
task_id: CAN-20260714-tibia-system-decomposition-world-content
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-008
status: merged
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition-world-content
base_branch: main
created: 2026-07-15T00:50:00+02:00
updated: 2026-07-15T01:21:33+02:00
last_verified_commit: "8692347930d86c5411dede46cb90251e5c677d96"
risk: low
related_issue: ""
related_pr: "#368"
depends_on:
  - completed and archived TSD-007
blocks:
  - TSD-009 social communication and trust decomposition
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260714-tibia-system-decomposition-world-content.md
    - docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
  shared: []
  read_only:
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/real-tibia/**
    - tools/agents/**
    - .github/workflows/**
    - src/**
    - data/**
    - tests/**
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

# Final result

PR #368 was squash-merged on `2026-07-14T23:21:33Z`.

- Task-start base: `350739e5df12db5f3c749540a36bb7c3922cc5ee`.
- Final feature head: `588bb075ae0ccf86093ae13a1f3880f7bb127f47`.
- Squash merge SHA: `8692347930d86c5411dede46cb90251e5c677d96`.
- Changed files: 13.
- Registry: 49 → 52.
- Added only `instances`, `world-map-runtime`, `world-zones`.
- Existing records modified: 0.
- Runtime/gameplay/protocol/client/DB/map/OTBM/datapack/assets/workflows/E2E changed: no.

# Classification

- Runtime map loading, tiles, spatial lookup, movement, visibility and pathfinding → `world-map-runtime`.
- Zone registry, indexing and membership lifecycle → `world-zones`.
- Region allocation, instance state, creature ownership, cleanup and expiration → `instances`.
- Towns, waypoints, teleports, floor transitions and NPC travel remained capabilities/findings or existing boundaries.

# Validation evidence

Final head `588bb075ae0ccf86093ae13a1f3880f7bb127f47`:

- Registry #332: success;
- Upstream Intelligence #364: success;
- Ownership #1188: success;
- current-head CI #2306 / Required: success;
- ready-state CI #2307: Lua Tests, Fast Checks, Linux release and Required — success;
- focused registry/source-role tests: success;
- schema/dependency validation and deterministic `generate --check`: success;
- changed files: 13 declared paths;
- comments, change-request reviews and unresolved threads: none;
- exact-head squash merge guard used.

# Repair history

1. Freshness dates were aligned from wall-clock `2026-07-15` to the registry baseline `2026-07-14`.
2. The accidentally omitted pre-existing `src/io/iobestiary.* → cyclopedia` generated row was restored after `generate --check` failed.

Neither repair changed TSD-008 scope, dependencies or runtime behavior.

# Safety boundary

Documentation, registry metadata, generated navigation and focused tests only. This task proves neither runtime map correctness, movement/pathfinding, zone membership, travel semantics, instance isolation/cleanup/expiration, persistence, physical-client E2E, Real Tibia parity nor Oteryn readiness.

# Next exact task

```text
task: CAN-20260714-tibia-system-decomposition-social-communication-trust
program: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
package: TSD-009
branch: docs/tibia-system-decomposition-social-communication-trust
```
