---
task_id: CAN-20260714-tibia-system-decomposition-account-character-progression
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-003
status: active
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition-account-character-progression
base_branch: main
created: 2026-07-14T19:10:00+02:00
updated: 2026-07-14T19:10:00+02:00
last_verified_commit: "661d55085b6a2ad5e930ae3186aa63ba052b665e"
risk: low
related_issue: ""
related_pr: ""
depends_on:
  - completed and archived TSD-002B
blocks:
  - TSD-004 Cyclopedia family decomposition
  - TSD-005 combat, weapons and vocations decomposition
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260714-tibia-system-decomposition-account-character-progression.md
    - docs/agents/real-tibia/TSD_003_ACCOUNT_CHARACTER_PROGRESSION_REPORT.md
    - docs/agents/real-tibia/registry/modules/account-lifecycle.yaml
    - docs/agents/real-tibia/registry/modules/account-authentication.yaml
    - docs/agents/real-tibia/registry/modules/character-lifecycle.yaml
    - docs/agents/real-tibia/registry/modules/character-progression.yaml
    - docs/agents/real-tibia/registry/modules/vocations.yaml
    - docs/agents/real-tibia/registry/modules/weapon-proficiency.yaml
  shared:
    - docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
    - docs/agents/real-tibia/generated/**
    - tools/agents/test_real_tibia_registry.py
    - tools/agents/test_upstream_intelligence_decomposition.py
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - AGENTS.md
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/real-tibia/TAXONOMY.md
    - docs/agents/real-tibia/MATURITY_MODEL.md
    - docs/agents/real-tibia/registry/categories.yaml
    - docs/agents/real-tibia/registry/schemas/**
    - docs/agents/real-tibia/registry/modules/player-persistence.yaml
    - docs/agents/real-tibia/registry/modules/protocol.yaml
    - docs/agents/real-tibia/registry/modules/achievements.yaml
    - docs/agents/real-tibia/registry/modules/wheel-of-destiny.yaml
    - docs/agents/upstream/**
    - tools/agents/real_tibia_registry*.py
    - tools/agents/upstream_intelligence*.py
    - .github/workflows/**
    - schema.sql
    - src/account/**
    - src/security/**
    - src/io/**
    - src/creatures/players/**
    - src/server/network/**
    - data/XML/vocations.xml
    - data/items/proficiencies.json
    - data-otservbr-global/account_quests.lua
    - data-otservbr-global/scripts/custom/account_quest_system.lua
    - tests/**
modules_touched:
  - Real Tibia module registry
  - account lifecycle and authentication
  - character lifecycle and progression
  - vocations
  - weapon proficiency
reuses:
  - existing Real Tibia registry-as-code
  - existing deterministic generator and discovery commands
  - source-role-aware Upstream Intelligence mapper
public_interfaces:
  - bounded account, character and progression discovery records
cross_repo_tasks: []
---

# Goal

Complete TSD-003 as a bounded account, character and progression inventory over current `main`. Classify account authentication and entitlements, account-wide state, character lifecycle, levels/skills/stamina/offline training/death-loss/blessings, vocations, Weapon Proficiency, titles and appearance unlocks. Add only durable independent records with verified current paths and preserve `player-persistence`, `protocol`, `achievements` and `wheel-of-destiny` as stable existing boundaries.

# Exact base and preflight

- Task-start main: `661d55085b6a2ad5e930ae3186aa63ba052b665e`.
- TSD-001, UI-001A, TSD-002A and TSD-002B feature/lifecycle cycles were merged first.
- Open PRs inspected: #352, #351, #350, #339, #316 and #245.
- PR #352 modifies shared `docs/agents/MODULE_CATALOG.md`; this task will refresh that file from then-current `main` only at final integration.
- PR #339 owns session/protocol runtime paths; this task reads them only and makes no runtime or protocol edit.
- PR #316 owns map/content evidence paths and PR #245 owns the shared physical-client E2E platform; neither scope is modified.
- `ACTIVE_WORK.md` remains read-only.

# Initial boundary hypotheses

Inventory currently supports evaluating these durable records:

- `account-lifecycle` — account identity, roster, premium/account-type state and repository lifecycle, excluding coin economy and wire protocol;
- `account-authentication` — credential/session verification and single-use login-token lifecycle, excluding transport packets and gameplay-session cleanup;
- `character-lifecycle` — authenticated character ownership, load/save/online-only component lifecycle and logout/reload persistence boundaries;
- `character-progression` — shared level, experience, skill, magic-level, stamina, offline-training and death/loss progression state hosted by Player and serializers;
- `vocations` — vocation registry, promotion relation, growth multipliers and XML configuration;
- `weapon-proficiency` — proficiency definitions, experience/perks/mastery, KV persistence and achievement interaction.

These are hypotheses until the report, registry validation and focused tests are complete. A class, field, XML row, helper, test or existing PR is not sufficient by itself.

# Acceptance criteria

- [ ] Inventory current account/authentication, character load/save, progression, vocation and Weapon Proficiency paths.
- [ ] Give every TSD-003 candidate an explicit decision with evidence and exclusions.
- [ ] Preserve existing broad records and do not encode hierarchy through fake `depends_on` edges.
- [ ] Use narrow verified paths; no new narrow record may use broad `src/**`.
- [ ] Keep all new maturity at conservative inventory/not-assessed unless an existing record is merely referenced.
- [ ] Keep account coin economy in TSD-007, sanctions/audit in TSD-009 and protocol/session transport in TSD-010 or active runtime ownership.
- [ ] Keep appearance/Cyclopedia/client surfaces deferred when current evidence does not justify an independent TSD-003 boundary.
- [ ] Update deterministic generated indexes through the existing generator contract.
- [ ] Add focused registry and source-aware mapping regressions.
- [ ] Pass registry validate/generate/stale/module/lookup-path/affected and dependency graph checks.
- [ ] Pass exact final-head and ready-state registry/UI/ownership/repository CI before merge.
- [ ] Make no schema, SQL, migration, runtime, C++, Lua gameplay, protocol, client, map, OTBM, datapack, asset, workflow or E2E implementation change.

# Safety and limitations

This task is documentation, registry metadata, generated navigation and focused discovery tests only. It cannot prove authentication security, session replay resistance beyond existing tests, persistence completeness, save atomicity, progression formula correctness, vocation parity, entitlement correctness, runtime behavior, physical-client E2E or Oteryn readiness.

# Handoff

After a feature PR passes exact final-head checks, changed-file/review inspection and ready-state Linux/Required, squash merge it and archive this task in a separate lifecycle-only PR. Only after that lifecycle merge may TSD-004 start from then-current `main`.