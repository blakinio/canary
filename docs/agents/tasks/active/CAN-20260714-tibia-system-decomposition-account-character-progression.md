---
task_id: CAN-20260714-tibia-system-decomposition-account-character-progression
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-003
status: active
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition-account-character-progression
base_branch: main
created: 2026-07-14T19:10:00+02:00
updated: 2026-07-14T19:52:00+02:00
last_verified_commit: "3eb7ae24bb1b918a0b040270e58c49037a873ee8"
risk: low
related_issue: ""
related_pr: "355"
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

# Exact base and integration refresh

- Task-start main: `661d55085b6a2ad5e930ae3186aa63ba052b665e`.
- Integration refresh main: `84fefca166af37c6995edccc50d2fc522aa219c6`.
- TSD-001, UI-001A, TSD-002A and TSD-002B feature/lifecycle cycles were merged first.
- PRs #350, #351, #352 and #357 merged documentation/lifecycle work while this task was active; their shared catalogue content was preserved.
- PR #339 merged exact session cleanup as `06286302ae429e6ba05a152e3b171b7a43046a0c`; its runtime implementation is read-only inventory evidence and does not promote TSD-003 maturity or safety claims.
- PR #316 owns map/content evidence paths and PR #245 owns the shared physical-client E2E platform; neither scope is modified.
- `ACTIVE_WORK.md` remains read-only.

# Delivered registry result

Registry records: 29 → 35. Added only:

- `account-lifecycle`;
- `account-authentication`;
- `character-lifecycle`;
- `character-progression`;
- `vocations`;
- `weapon-proficiency`.

Existing module records modified: 0. Categories, schemas, generator, mapper and workflows remain unchanged. `player-persistence`, `protocol`, `achievements` and `wheel-of-destiny` remain stable existing boundaries.

# Candidate conclusions

- Account entitlements and premium state remain account-lifecycle capabilities.
- Account sanctions are deferred to TSD-009.
- No generic account-wide storage subsystem is claimed from quest-specific evidence.
- Character creation/load/save/logout/reconnect/deletion remain lifecycle capabilities, not helper-level modules.
- Level, experience, skill, magic-level, stamina, offline-training, death-loss and blessings remain findings inside `character-progression`.
- Individual vocation entries remain in one vocation registry lifecycle.
- Weapon Proficiency receives a durable independent record.
- Titles, outfits, mounts and familiars are deferred to later Cyclopedia/client inventory.

Detailed decisions and evidence limits are recorded in `docs/agents/real-tibia/TSD_003_ACCOUNT_CHARACTER_PROGRESSION_REPORT.md`.

# Maturity and relationships

All six records start at lifecycle/implementation/evidence `inventory`; persistence, protocol, automated tests, runtime validation and gameplay E2E remain `not-assessed`.

Fundamental dependency edges only:

- `account-lifecycle` → `database-connection`;
- `account-authentication` → `account-lifecycle`;
- `character-lifecycle` → `account-authentication`, `player-persistence`;
- `character-progression` → `character-lifecycle`, `player-persistence`;
- `weapon-proficiency` → `character-progression`, `player-persistence`;
- `vocations` has no dependency edge.

The dependency graph remains acyclic.

# Validation history

Implementation/focused-test head `3eb7ae24bb1b918a0b040270e58c49037a873ee8`:

- Real Tibia Module Registry #191: success;
- Upstream Intelligence #219: success;
- Agent Task Ownership #1058: success;
- repository CI #2170: success;
- focused registry and source-role mapping tests: success;
- schema/dependency validation: success;
- deterministic `generate --check`: success;
- stale/module/lookup-path/exact PR-range affected commands: success.

Later program, catalogue, changelog, report and this task-record update are documentation-only. This task record cannot embed its own final SHA; live PR #355 metadata and exact-head workflows are authoritative for final readiness and merge.

# Acceptance criteria

- [x] Inventoried current account/authentication, character load/save, progression, vocation and Weapon Proficiency paths.
- [x] Gave every TSD-003 candidate an explicit decision with evidence and exclusions.
- [x] Preserved existing broad records and avoided fake hierarchy dependencies.
- [x] Used narrow verified paths; no new narrow record uses broad `src/**`.
- [x] Kept all new maturity at conservative inventory/not-assessed.
- [x] Kept account coin economy in TSD-007, sanctions/audit in TSD-009 and protocol/session transport outside this package.
- [x] Deferred appearance/Cyclopedia/client surfaces lacking an independent TSD-003 boundary.
- [x] Updated deterministic generated indexes through the existing generator contract.
- [x] Added focused registry and source-aware mapping regressions.
- [x] Passed registry validate/generate/stale/module/lookup-path/affected and dependency graph checks at the implementation head.
- [ ] Exact final current-head and ready-state registry/UI/ownership/repository CI must pass before merge.
- [x] Made no schema, SQL, migration, runtime, C++, Lua gameplay, protocol, client, map, OTBM, datapack, asset, workflow or E2E implementation change.

# Safety and limitations

This task is documentation, registry metadata, generated navigation and focused discovery tests only. It cannot prove authentication security, token replay safety, persistence completeness, save atomicity, progression formula correctness, vocation parity, entitlement correctness, runtime behavior, physical-client E2E or Oteryn readiness.

# Handoff

After PR #355 passes exact final-head checks, changed-file/review inspection and ready-state Linux/Required, squash merge it and archive this task in a separate lifecycle-only PR. Only after that lifecycle merge may TSD-004 start from then-current `main`:

```text
task: CAN-20260714-tibia-system-decomposition-cyclopedia-family
package: TSD-004
branch: docs/tibia-system-decomposition-cyclopedia-family
```
