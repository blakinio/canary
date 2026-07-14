---
task_id: CAN-20260714-tibia-system-decomposition-cyclopedia-family
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-004
status: active
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition-cyclopedia-family
base_branch: main
created: 2026-07-14T20:10:00+02:00
updated: 2026-07-14T20:24:00+02:00
last_verified_commit: "9f82f93977e82784370961a72104efacd497c8e0"
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
- PR #316 owns donor-map/content evidence and remains read-only; no map, OTBM or content edit is allowed.
- PR #245 owns the single shared physical-client E2E platform and remains read-only; no scenario or orchestrator change is allowed.
- OpenTibiaBR Canary and maintained OTClient are evidence sources only; no upstream write is authorized.
- `ACTIVE_WORK.md` remains read-only.

# Initial boundary conclusions

Current source and validator evidence supports evaluating four durable independent records:

- `bestiary` — kill tracking, unlock stages, race lookup and finished/stage-two progression, excluding Charm ownership;
- `bosstiary` — boss rarity stages, points, boosted boss, kill tracking and slot/loot bonus lifecycle;
- `cyclopedia-character` — summary, death history, recent kills and KV-backed character Cyclopedia state;
- `titles` — title definitions, unlock/current selection, KV persistence and cross-domain unlock checks.

Expected non-record conclusions:

- `cyclopedia` remains the unchanged broad umbrella;
- `charms` and `houses` remain existing independent records;
- `cyclopedia-items` and `cyclopedia-map` remain umbrella/protocol/client surfaces unless a separate stable server lifecycle is proven;
- `cyclopedia-houses` is already covered by `houses` plus Cyclopedia/protocol presentation;
- outfits, mounts and familiars remain outside this package.

These are bounded inventory hypotheses until registry validation, deterministic generation and focused source-role tests pass.

# Acceptance criteria

- [ ] Inventory current Bestiary, Bosstiary, character summary/history, titles, item/map/house and maintained-client Cyclopedia paths.
- [ ] Give every TSD-004 candidate an explicit decision with exclusions and evidence limits.
- [ ] Preserve `cyclopedia`, `charms`, `houses`, `achievements`, `protocol` and TSD-003 records unchanged.
- [ ] Use narrow verified paths; no new narrow record may use broad `src/**`, `modules/game_cyclopedia/**` or all monster data as its primary discovery root.
- [ ] Keep new maturity at inventory/not-assessed.
- [ ] Keep generic item ownership in TSD-007, map/world mechanics in TSD-008 and wire/client contracts in TSD-010.
- [ ] Reuse the existing Cyclopedia validator; create no second scanner or E2E platform.
- [ ] Update deterministic generated indexes through the existing generator contract.
- [ ] Add focused registry and source-aware mapping regressions.
- [ ] Pass registry validate/generate/stale/module/lookup-path/affected and dependency graph checks.
- [ ] Pass exact final-head and ready-state registry/UI/ownership/repository CI before merge.
- [ ] Make no schema, SQL, migration, runtime, C++, Lua gameplay, protocol, client, map, OTBM, datapack, asset, workflow or E2E implementation change.

# Safety and limitations

This task is documentation, registry metadata, generated navigation and focused discovery tests only. It cannot prove Bestiary/Bosstiary IDs, formulas, progression, persistence, boosted-boss behavior, title unlock correctness, protocol compatibility, maintained-client rendering, runtime behavior, physical-client E2E or Oteryn readiness.

# Handoff

After a feature PR passes exact final-head checks, changed-file/review inspection and ready-state Linux/Required, squash merge it and archive this task in a separate lifecycle-only PR. Only after that lifecycle merge may TSD-005 start from then-current `main`.