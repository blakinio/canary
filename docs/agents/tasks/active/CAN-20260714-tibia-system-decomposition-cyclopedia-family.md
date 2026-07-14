---
task_id: CAN-20260714-tibia-system-decomposition-cyclopedia-family
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-004
status: active
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition-cyclopedia-family
base_branch: main
created: 2026-07-14T20:10:00+02:00
updated: 2026-07-14T20:32:00+02:00
last_verified_commit: "cc6a0352c3dfc88b2be5efd1164162c9e2870003"
risk: low
related_issue: ""
related_pr: "359"
depends_on:
  - completed and archived TSD-003
blocks:
  - TSD-005 combat, weapons and vocations decomposition
  - TSD-006 creatures, hunting, raids and bosses decomposition
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260714-tibia-system-decomposition-cyclopedia-family.md
    - docs/agents/real-tibia/TSD_004_CYCLOPEDIA_FAMILY_REPORT.md
    - docs/agents/real-tibia/registry/modules/bestiary.yaml
    - docs/agents/real-tibia/registry/modules/bosstiary.yaml
    - docs/agents/real-tibia/registry/modules/cyclopedia-character.yaml
    - docs/agents/real-tibia/registry/modules/titles.yaml
    - tools/agents/test_cyclopedia_registry.py
    - tools/agents/test_upstream_intelligence_cyclopedia.py
  shared:
    - docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
    - docs/agents/real-tibia/generated/**
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - AGENTS.md
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/real-tibia/TAXONOMY.md
    - docs/agents/real-tibia/MATURITY_MODEL.md
    - docs/agents/real-tibia/registry/categories.yaml
    - docs/agents/real-tibia/registry/schemas/**
    - docs/agents/real-tibia/registry/modules/cyclopedia.yaml
    - docs/agents/real-tibia/registry/modules/charms.yaml
    - docs/agents/real-tibia/registry/modules/houses.yaml
    - docs/agents/real-tibia/registry/modules/achievements.yaml
    - docs/agents/real-tibia/registry/modules/protocol.yaml
    - docs/agents/upstream/**
    - tools/agents/real_tibia_registry*.py
    - tools/agents/upstream_intelligence*.py
    - .github/workflows/**
    - tools/ai-agent/cyclopedia_validation.py
    - tools/ai-agent/test_cyclopedia_validation.py
    - docs/ai-agent/OTS_AI_CYCLOPEDIA_VALIDATION_PROJECT.md
    - docs/ai-agent/CYCLOPEDIA_VALIDATION_REPORT.md
    - docs/ai-agent/CYCLOPEDIA_RUNTIME_TEST_PLAN.json
    - src/io/iobestiary.*
    - src/io/io_bosstiary.*
    - src/creatures/players/components/player_cyclopedia.*
    - src/creatures/players/components/player_title.*
    - src/enums/player_cyclopedia.hpp
    - src/server/network/protocol/**
    - src/map/house/**
    - schema.sql
    - data/monster/**
    - data-otservbr-global/monster/**
    - data/scripts/systems/bestiary_charms.lua
    - data/scripts/lib/register_bestiary_charm.lua
    - tests/**
modules_touched:
  - Real Tibia module registry
  - cyclopedia umbrella
  - bestiary
  - bosstiary
  - cyclopedia character
  - titles
  - charms
  - houses
reuses:
  - existing Real Tibia registry-as-code
  - existing deterministic generator and discovery commands
  - source-role-aware Upstream Intelligence mapper
  - existing Cyclopedia validator and evidence reports
public_interfaces:
  - bounded Cyclopedia family discovery records
cross_repo_tasks: []
---

# Goal

Complete TSD-004 as a bounded Cyclopedia-family inventory over current `main`. Preserve `cyclopedia` as the compatibility/discovery umbrella and `charms`, `houses`, `achievements`, account/character boundaries and `protocol` as stable existing records. Classify items, Bestiary, Bosstiary, map, character/summary/history, titles, houses and client surfaces; add only durable independent records with verified current Canary and maintained-OTClient paths.

# Exact base and preflight

- Task-start main: `9f82f93977e82784370961a72104efacd497c8e0`.
- TSD-001 through TSD-003 feature and lifecycle cycles were merged first.
- Open PRs inspected: #316 and #245.
- PR #316 owns donor-map/content evidence and remains read-only; no map, OTBM or content edit occurred.
- PR #245 owns the single shared physical-client E2E platform and remains read-only; no scenario or orchestrator change occurred.
- OpenTibiaBR Canary and maintained OTClient were evidence sources only; no upstream write occurred.
- `ACTIVE_WORK.md` remained read-only.

# Delivered registry result

Registry records: 35 → 39. Added only:

- `bestiary`;
- `bosstiary`;
- `cyclopedia-character`;
- `titles`.

Existing module records modified: 0. Categories, schemas, generator, mapper and workflows remain unchanged.

Stable records preserved unchanged:

- `cyclopedia` as the broad compatibility/discovery umbrella;
- `charms`;
- `houses`;
- `achievements`;
- `protocol`;
- `character-lifecycle`;
- `character-progression`;
- `player-persistence`.

# Candidate conclusions

- Bestiary receives a narrow kill/unlock/race/completion record; Charm ownership remains separate.
- Bosstiary receives a narrow rarity/points/boosted-boss/slot/loot-bonus record; generic boss encounters remain later work.
- Cyclopedia Character receives an independent summary/death/recent-kill/KV component record.
- Titles receives an independent definition/unlock/current-selection/persistence record.
- Cyclopedia Items and Map remain umbrella/protocol/client surfaces.
- Cyclopedia Houses is already covered by `houses` plus presentation/protocol interaction.
- Outfits, mounts and familiars remain deferred.

Detailed evidence and exclusions are in `docs/agents/real-tibia/TSD_004_CYCLOPEDIA_FAMILY_REPORT.md`.

# Maturity and relationships

All four records start at lifecycle/implementation/evidence `inventory`; persistence, protocol, automated tests, runtime validation and gameplay E2E remain `not-assessed`.

Fundamental dependency edges only:

- `bestiary` → `cyclopedia`, `player-persistence`;
- `bosstiary` → `cyclopedia`, `player-persistence`;
- `cyclopedia-character` → `cyclopedia`, `player-persistence`;
- `titles` → `cyclopedia-character`, `player-persistence`.

The dependency graph remains acyclic.

# Validation history

Implementation/focused-test head `cc6a0352c3dfc88b2be5efd1164162c9e2870003`:

- Real Tibia Module Registry #222: success;
- Upstream Intelligence #250: success;
- Agent Task Ownership #1082: success;
- repository CI #2195: success;
- focused registry and server/client source-role tests: success;
- schema and dependency validation: success;
- deterministic `generate --check`: success;
- stale/module/lookup-path/exact PR-range `affected` commands: success.

Later program, catalogue, changelog, report and this task-record update are documentation-only. This task record cannot embed its own final SHA; live PR #359 metadata and exact-head workflows are authoritative for final readiness and merge.

# Acceptance criteria

- [x] Inventoried current Bestiary, Bosstiary, character summary/history, titles, item/map/house and maintained-client Cyclopedia paths.
- [x] Gave every TSD-004 candidate an explicit decision with exclusions and evidence limits.
- [x] Preserved `cyclopedia`, `charms`, `houses`, `achievements`, `protocol` and TSD-003 records unchanged.
- [x] Used narrow verified paths; no new narrow record uses broad `src/**`, `modules/game_cyclopedia/**` or all monster data.
- [x] Kept new maturity at inventory/not-assessed.
- [x] Kept generic item ownership in TSD-007, map/world mechanics in TSD-008 and wire/client contracts in TSD-010.
- [x] Reused the existing Cyclopedia validator; created no second scanner or E2E platform.
- [x] Updated deterministic generated indexes through the existing generator contract.
- [x] Added focused registry and source-aware mapping regressions.
- [x] Passed registry validate/generate/stale/module/lookup-path/affected and dependency graph checks at the implementation head.
- [ ] Exact final-head and ready-state registry/UI/ownership/repository CI must pass before merge.
- [x] Made no schema, SQL, migration, runtime, C++, Lua gameplay, protocol, client, map, OTBM, datapack, asset, workflow or E2E implementation change.

# Safety and limitations

This task is documentation, registry metadata, generated navigation and focused discovery tests only. It cannot prove Bestiary/Bosstiary IDs, formulas, progression, persistence, boosted-boss behavior, title unlock correctness, protocol compatibility, maintained-client rendering, runtime behavior, physical-client E2E or Oteryn readiness.

# Handoff

After PR #359 passes exact final-head checks, changed-file/review inspection and ready-state Linux/Required, squash merge it and archive this task in a separate lifecycle-only PR. Only after that lifecycle merge may TSD-005 start from then-current `main`:

```text
task: CAN-20260714-tibia-system-decomposition-combat-weapons-vocations
package: TSD-005
branch: docs/tibia-system-decomposition-combat-weapons-vocations
```
