---
task_id: CAN-20260714-tibia-system-decomposition-combat-weapons-vocations
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-005
status: active
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition-combat-weapons-vocations
base_branch: main
created: 2026-07-14T21:00:00+02:00
updated: 2026-07-14T22:32:00+02:00
last_verified_commit: "775481e9fbec13871159fcff0c46ae4a014b3075"
risk: low
related_issue: ""
related_pr: "362"
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
    - tools/agents/test_real_tibia_registry.py
    - tools/agents/test_cyclopedia_registry.py
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
- PR #360 claims protocol-session task ownership and remains read-only to this package.
- PR #316 owns donor-map/content audit files and remains read-only.
- PR #245 owns the shared physical-client E2E platform and remains read-only.
- `ACTIVE_WORK.md` remains read-only.

# Delivered registry result

Registry records: 39 → 41. Added only:

- `combat-conditions`;
- `weapons`.

Existing records modified: 0. Categories, schemas, generator, mapper and workflows remain unchanged. Existing `combat`, `spells`, `vocations`, `weapon-proficiency`, `character-progression`, `player-persistence` and `protocol` records remain stable.

# Candidate conclusions

- Target selection, PvP/protection permission checks, area/chain targeting, formulas, damage/healing, mitigation, ordering and critical/leech remain capabilities of `combat`.
- Condition creation, timed lifecycle, stacking/refresh, execution, subclasses and serialization receive `combat-conditions`.
- Weapon registry, wield/use checks, melee/distance/wand implementations, formula/resource surfaces and combat handoff receive `weapons`.
- Individual conditions, weapon classes and vocation entries remain inside their parent records.
- Spells, vocations and Weapon Proficiency are already covered.

Detailed decisions and evidence limits are in `docs/agents/real-tibia/TSD_005_COMBAT_WEAPONS_VOCATIONS_REPORT.md`.

# Validation and repair history

Implementation/focused-test head `775481e9fbec13871159fcff0c46ae4a014b3075`:

- Real Tibia Module Registry #247: success;
- Upstream Intelligence #276: success;
- Agent Task Ownership #1104: success;
- focused registry and source-role tests: success;
- schema/dependency validation: success;
- deterministic `generate --check`: success;
- stale/module/lookup-path/exact PR-range `affected`: success.

Review-fix history:

1. The first client-source focused test incorrectly expected paths matching the configured client `src/**` pattern to remain unmapped. It was corrected to expect `protocol` through the allowed client bucket while explicitly excluding server-only `combat`, `combat-conditions` and `weapons`.
2. Older TSD-003/TSD-004 tests froze the global registry total at 39. They now assert only their minimum package baseline; the TSD-005 test alone verifies the exact current total of 41.

Later program, changelog and this task-record commit are documentation-only. This record cannot embed its own final SHA; live PR #362 metadata and exact-head workflows are authoritative before merge.

# Acceptance criteria

- [x] Inventoried current combat, condition, weapon, spell, vocation and proficiency paths.
- [x] Gave each TSD-005 candidate an explicit decision and evidence limit.
- [x] Preserved existing module records unchanged.
- [x] Added only `combat-conditions` and `weapons`.
- [x] Used verified narrow paths and no broad new `src/**`.
- [x] Kept all new maturity conservative at inventory/not-assessed.
- [x] Regenerated indexes through the existing deterministic generator contract.
- [x] Added focused registry and source-role mapping regressions.
- [x] Passed validate, generate --check, stale, module, lookup-path, affected and dependency graph checks at the implementation head.
- [ ] Exact final current-head and ready-state registry/UI/ownership/repository CI must pass before merge.
- [x] Made no runtime, C++, Lua gameplay, protocol, client, database, map, OTBM, datapack, asset, workflow or E2E implementation change.

# Safety and limitations

This task inventories boundaries only. Source and tests cannot prove target legality, PvP permissions, damage/healing values, mitigation order, condition timing/stacking/persistence, weapon formulas/resource use, vocation compatibility, runtime correctness, physical-client E2E or Real Tibia parity.

# Handoff

After PR #362 passes exact final-head checks, changed-file/review inspection and ready-state Linux/Required, squash merge it and archive this task in a separate lifecycle-only PR. Only after that archive merges may TSD-006 start from then-current `main`:

```text
task: CAN-20260714-tibia-system-decomposition-creatures-hunting-raids-bosses
package: TSD-006
branch: docs/tibia-system-decomposition-creatures-hunting-raids-bosses
```
