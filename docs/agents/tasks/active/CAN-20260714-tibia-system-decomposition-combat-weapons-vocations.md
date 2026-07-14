---
task_id: CAN-20260714-tibia-system-decomposition-combat-weapons-vocations
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-005
status: active
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition-combat-weapons-vocations
base_branch: main
created: 2026-07-14T21:00:00+02:00
updated: 2026-07-14T21:00:00+02:00
last_verified_commit: "f163ed8e3b3d51e65c7fef1bc03830b12b2e6bfa"
risk: low
related_issue: ""
related_pr: ""
depends_on:
  - completed and archived TSD-004
blocks:
  - TSD-006 creatures hunting raids and bosses decomposition
  - TSD-007 items and economy decomposition
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260714-tibia-system-decomposition-combat-weapons-vocations.md
    - docs/agents/real-tibia/TSD_005_COMBAT_WEAPONS_VOCATIONS_REPORT.md
    - docs/agents/real-tibia/registry/modules/combat-conditions.yaml
    - docs/agents/real-tibia/registry/modules/weapons.yaml
    - tools/agents/test_combat_registry.py
    - tools/agents/test_upstream_intelligence_combat.py
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
    - docs/agents/real-tibia/registry/modules/combat.yaml
    - docs/agents/real-tibia/registry/modules/spells.yaml
    - docs/agents/real-tibia/registry/modules/vocations.yaml
    - docs/agents/real-tibia/registry/modules/weapon-proficiency.yaml
    - docs/agents/real-tibia/registry/modules/character-progression.yaml
    - docs/agents/real-tibia/registry/modules/player-persistence.yaml
    - docs/agents/upstream/**
    - tools/agents/real_tibia_registry*.py
    - tools/agents/upstream_intelligence*.py
    - .github/workflows/**
    - src/creatures/combat/**
    - src/items/weapons/**
    - src/creatures/players/vocations/**
    - src/creatures/players/components/weapon_proficiency.*
    - data/scripts/spells/**
    - data-otservbr-global/scripts/spells/**
    - data/XML/vocations.xml
    - data/items/proficiencies.json
    - tests/**
modules_touched:
  - Real Tibia module registry
  - combat umbrella
  - conditions
  - weapons
  - spells
  - vocations
  - weapon proficiency
reuses:
  - existing Real Tibia registry-as-code
  - existing deterministic generator and discovery commands
  - source-role-aware Upstream Intelligence mapper
public_interfaces:
  - bounded combat conditions and weapon discovery records
cross_repo_tasks: []
---

# Goal

Complete TSD-005 as a bounded combat, weapons and vocations inventory over current `main`. Preserve `combat`, `spells`, `vocations`, `weapon-proficiency`, `character-progression` and `player-persistence` as stable existing records. Evaluate target selection, combat permission checks, damage/healing formulas, mitigation/blocking, conditions, weapons and vocation interactions; add only durable independent boundaries with verified current paths.

# Exact base and preflight

- Task-start main: `f163ed8e3b3d51e65c7fef1bc03830b12b2e6bfa`.
- TSD-001 through TSD-004 feature/lifecycle cycles were merged first.
- Open PRs inspected: #360, #316 and #245.
- PR #360 currently claims only its protocol-session task record and remains read-only; any later runtime expansion stays outside this documentation package.
- PR #316 owns donor-map/content audit files and remains read-only.
- PR #245 owns the shared physical-client E2E platform and remains read-only.
- `ACTIVE_WORK.md` remains read-only.

# Initial boundary decision

Current source inventory supports two new independent records:

- `combat-conditions` — condition creation, lifecycle, stacking/refresh, timed execution, serialization and persistent-condition state;
- `weapons` — weapon registry, wield/use checks, melee/distance/wand formulas, vocation/level requirements, resource/charge consumption and combat handoff.

Target selection, PvP/protection/permission checks, area/chain targeting, damage/healing formulas, armor/shield mitigation and combat ordering remain capabilities of the existing `combat` umbrella because they share `combat.*` and do not have an independent stable subsystem root. Individual weapon classes and vocation entries remain data/types inside their parent records.

# Acceptance criteria

- [ ] Inventory current combat, condition, weapon, spell, vocation and proficiency paths.
- [ ] Give each TSD-005 candidate an explicit decision and evidence limit.
- [ ] Preserve existing module records unchanged.
- [ ] Add only `combat-conditions` and `weapons` unless a further independent lifecycle is proven.
- [ ] Use verified narrow paths and no broad `src/**`.
- [ ] Keep all new maturity conservative at inventory/not-assessed.
- [ ] Regenerate indexes through the existing deterministic generator contract.
- [ ] Add focused registry and source-role mapping regressions.
- [ ] Pass validate, generate --check, stale, module, lookup-path, affected and dependency graph checks.
- [ ] Pass exact final-head and ready-state registry/UI/ownership/repository CI.
- [ ] Make no runtime, C++, Lua gameplay, protocol, client, database, map, OTBM, datapack, asset, workflow or E2E implementation change.

# Safety and limitations

This task inventories boundaries only. Source and tests cannot prove target legality, PvP permissions, damage/healing values, mitigation order, condition semantics, weapon formulas, vocation compatibility, persistence, runtime correctness, physical-client E2E or Real Tibia parity.

# Handoff

After feature merge, archive this task in a separate lifecycle-only PR. Only after that archive merges may TSD-006 start from then-current `main`.