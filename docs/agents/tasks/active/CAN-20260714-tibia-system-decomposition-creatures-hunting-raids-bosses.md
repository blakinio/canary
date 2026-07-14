---
task_id: CAN-20260714-tibia-system-decomposition-creatures-hunting-raids-bosses
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-006
status: active
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition-creatures-hunting-raids-bosses
base_branch: main
created: 2026-07-14T22:50:00+02:00
updated: 2026-07-14T23:18:00+02:00
last_verified_commit: "e4362168807c74eb66b17405cba06aa0d874c19f"
risk: low
related_issue: ""
related_pr: "364"
depends_on:
  - completed and archived TSD-005
blocks:
  - TSD-007 items and economy decomposition
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260714-tibia-system-decomposition-creatures-hunting-raids-bosses.md
    - docs/agents/real-tibia/TSD_006_CREATURES_HUNTING_RAIDS_BOSSES_REPORT.md
    - docs/agents/real-tibia/registry/modules/creature-definitions.yaml
    - docs/agents/real-tibia/registry/modules/creature-ai.yaml
    - docs/agents/real-tibia/registry/modules/boss-encounters.yaml
    - docs/agents/real-tibia/registry/modules/raids.yaml
    - tools/agents/test_creature_registry.py
    - tools/agents/test_upstream_intelligence_creatures.py
  shared:
    - docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
    - docs/agents/real-tibia/generated/**
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - AGENTS.md
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/real-tibia/registry/modules/spawns.yaml
    - docs/agents/real-tibia/registry/modules/prey.yaml
    - docs/agents/real-tibia/registry/modules/bestiary.yaml
    - docs/agents/real-tibia/registry/modules/bosstiary.yaml
    - docs/agents/real-tibia/registry/modules/cyclopedia.yaml
    - docs/agents/real-tibia/registry/modules/combat.yaml
    - docs/agents/real-tibia/registry/modules/combat-conditions.yaml
    - docs/agents/real-tibia/registry/modules/weapons.yaml
    - docs/agents/upstream/**
    - tools/agents/real_tibia_registry*.py
    - tools/agents/upstream_intelligence*.py
    - .github/workflows/**
    - src/creatures/monsters/**
    - src/lua/creature/raids.*
    - data/libs/systems/reward_boss.lua
    - data/scripts/systems/reward_chest.lua
    - data/raids/**
    - data-otservbr-global/monster/**
    - data-otservbr-global/scripts/raids/**
    - tests/**
modules_touched:
  - Real Tibia module registry
  - creature definitions
  - creature AI
  - boss encounters
  - raids
reuses:
  - existing Real Tibia registry-as-code
  - existing deterministic generator
  - source-role-aware Upstream Intelligence mapper
  - existing spawn/NPC validation tooling
public_interfaces:
  - bounded creature, encounter and raid discovery records
cross_repo_tasks: []
---

# Goal

Complete TSD-006 as a bounded creatures, hunting, raids and bosses inventory. Preserve `spawns`, `prey`, `bestiary`, `bosstiary`, `cyclopedia`, `combat`, `combat-conditions` and `weapons`; add only durable independent creature-definition, AI, boss-encounter and raid lifecycles supported by verified current paths.

# Exact base and preflight

- Task-start main: `f68f826915882b0b20081b8fca5ed975ce303f45`.
- Open PRs inspected: #360, #316 and #245.
- #360 protocol/session runtime, #316 donor map/content audit and #245 physical-client E2E remain read-only and non-overlapping.
- `ACTIVE_WORK.md` remains read-only.

# Delivered result

Registry records: 41 → 45. Added only:

- `boss-encounters`;
- `creature-ai`;
- `creature-definitions`;
- `raids`.

Existing records modified: 0. `spawns`, `prey`, `bestiary`, `bosstiary`, `cyclopedia`, `combat`, `combat-conditions`, `weapons` and player persistence remain stable.

# Classification summary

- MonsterType/Monsters registry and active monster data receive `creature-definitions`.
- Runtime Monster think/target/follow/flee/movement/attack lifecycle receives `creature-ai`.
- Reward-boss participation, contribution scoring, reward generation and reward-container handoff receive `boss-encounters`.
- Raid registry, probabilistic scheduling, ordered events, reset and reload receive `raids`.
- Static placement and generic dynamic creation remain in `spawns`.
- Prey/Hunting Tasks, Bestiary and Bosstiary credit remain already covered.
- Individual monster, boss and raid definitions remain data entries rather than modules.

Detailed evidence: `docs/agents/real-tibia/TSD_006_CREATURES_HUNTING_RAIDS_BOSSES_REPORT.md`.

# Validation and repair history

Implementation/focused-test head `e4362168807c74eb66b17405cba06aa0d874c19f`:

- Real Tibia Module Registry #275: success;
- Upstream Intelligence #305: success;
- Agent Task Ownership #1126: success;
- repository CI #2241: success;
- focused registry/source-role tests: success;
- schema and dependency validation: success;
- deterministic `generate --check`: success;
- discovery and exact PR-range `affected`: success.

The initial generated dependency mismatch was caused solely by unsorted `interacts_with` arrays in `creature-ai` and `raids`. Their relation order was normalized without changing scope, paths, dependencies, mapper behavior or runtime code.

Later program and task-record commits are documentation-only. This record cannot embed its own final SHA; live PR #364 metadata and exact-head workflows remain authoritative before merge.

# Acceptance criteria

- [x] Added only the four confirmed records.
- [x] Preserved all existing records unchanged.
- [x] Classified all TSD-006 candidates explicitly.
- [x] Used verified narrow paths and conservative maturity.
- [x] Regenerated deterministic indexes through the existing generator.
- [x] Added focused registry and source-role mapping tests.
- [x] Passed registry/UI/ownership/repository CI at the implementation head.
- [ ] Exact final-head and ready-state Linux/Required must pass before merge.
- [x] Made no runtime, gameplay, protocol, client, DB, map, OTBM, datapack, asset, workflow or E2E implementation change.

# Safety limits

Inventory does not prove creature AI correctness, pathfinding, target choice, spawn timing, boss participation/scoring/reward formulas, raid probability/order, Bestiary/Bosstiary/Prey credit, persistence safety, runtime behavior or parity.

# Handoff

After PR #364 passes exact final-head review and ready-state CI, squash merge it and archive this task in a separate lifecycle-only PR. Only after that archive merges may TSD-007 start from then-current `main`:

```text
task: CAN-20260714-tibia-system-decomposition-items-economy
package: TSD-007
branch: docs/tibia-system-decomposition-items-economy
```
