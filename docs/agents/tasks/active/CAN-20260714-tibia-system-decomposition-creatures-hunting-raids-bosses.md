---
task_id: CAN-20260714-tibia-system-decomposition-creatures-hunting-raids-bosses
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-006
status: active
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition-creatures-hunting-raids-bosses
base_branch: main
created: 2026-07-14T22:50:00+02:00
updated: 2026-07-14T22:50:00+02:00
last_verified_commit: "f68f826915882b0b20081b8fca5ed975ce303f45"
risk: low
related_issue: ""
related_pr: ""
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

# Boundary decision

Current source inventory supports four independent records:

- `creature-definitions` — MonsterType/Monsters registry, spells, loot, summons, immunities and metadata definitions;
- `creature-ai` — Monster runtime think/target/follow/movement/attack/flee lifecycle;
- `boss-encounters` — reward-boss participation, scoring, reward-container and reward-chest lifecycle;
- `raids` — raid registry/load/start/check/event/reset/reload state machine and raid data.

Static spawn placement and generic dynamic creation remain in `spawns`; Bestiary/Bosstiary kill progression remains in their records; Prey/Hunting Tasks remains in `prey`. Individual monster/boss/raid definitions are data entries, not standalone modules.

# Acceptance criteria

- [ ] Add only the four confirmed records.
- [ ] Preserve all existing records unchanged.
- [ ] Classify all TSD-006 candidates explicitly.
- [ ] Use verified narrow paths and conservative maturity.
- [ ] Regenerate deterministic indexes through the existing generator.
- [ ] Add focused registry and source-role mapping tests.
- [ ] Pass exact-head registry/UI/ownership/repository CI and ready-state Linux/Required.
- [ ] Make no runtime, gameplay, protocol, client, DB, map, OTBM, datapack, asset, workflow or E2E implementation change.

# Safety limits

Inventory does not prove creature AI correctness, pathfinding, target choice, spawn timing, boss participation/scoring/reward formulas, raid probability/order, Bestiary/Bosstiary/Prey credit, runtime behavior or parity.

# Handoff

After feature merge, archive this task in a separate lifecycle-only PR. Only after that archive merges may TSD-007 start from then-current `main`.