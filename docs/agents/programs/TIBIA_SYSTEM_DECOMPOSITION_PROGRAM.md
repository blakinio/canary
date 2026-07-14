---
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
name: Tibia System Decomposition
status: active
owner: repository-wide
created: 2026-07-14T15:43:00+02:00
updated: 2026-07-14T20:42:00+02:00
last_verified_commit: "6d6df89b02fca525ef76011369d8c6243de231d8"
primary_paths:
  - docs/agents/real-tibia/**
  - docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
shared_integration_paths:
  - tools/agents/real_tibia_registry*.py
  - tools/agents/upstream_intelligence*.py
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
related_programs:
  - CAN-PROGRAM-REAL-TIBIA-PARITY
  - CAN-PROGRAM-UPSTREAM-INTELLIGENCE
  - CAN-PROGRAM-E2E-PLATFORM
cross_repo_contracts: []
---

# Mission

Maintain one durable logical decomposition of Tibia and Canary through the existing Real Tibia registry so agents can discover bounded domains, coordinate work, map upstream changes, assign proof layers and later classify migration work for Oteryn without changing gameplay or physically reorganizing the legacy source tree.

This program is architecture, registry metadata, documentation and coordination only. It never authorizes runtime changes.

# Source-of-truth and safety contract

The only canonical module inventory is `docs/agents/real-tibia/registry/**`. Generated indexes are derived artifacts; package reports explain decisions but are not a second registry.

The program reuses Real Tibia Parity governance, the source-role-aware Upstream Intelligence mapper, the shared physical-client E2E platform, the existing OTBM analysis pipeline and task ownership.

Permanent rules:

- path hints are discovery, not ownership or edit authorization;
- broad existing IDs remain stable umbrellas;
- narrow records use verified current paths and never broad server `src/**`;
- `depends_on` means a fundamental dependency and must remain acyclic;
- file/schema/helper/migration/test presence supports at most inventory;
- no TSD package claims gameplay/runtime, persistence, protocol, parity, E2E or Oteryn readiness;
- no second registry, generator, watcher, mapper, parser, renderer or E2E orchestrator;
- no physical source-tree refactor or normal-task edit to `ACTIVE_WORK.md`.

New decomposition records start at lifecycle/implementation/evidence `inventory`; persistence, protocol, automated tests, runtime validation and gameplay E2E stay `not-assessed` unless a later narrow proof task establishes otherwise.

# Program integrations

- **Real Tibia Parity:** owns evidence precedence and behavioral conclusions.
- **Upstream Intelligence:** uses only source-policy-allowed buckets; mapping remains deterministic, discovery-only and does not change triage or reviewed decisions.
- **Physical-client E2E:** remains one shared orchestrator; TSD packages do not duplicate it.
- **OTBM tooling:** existing parser/index/resolution/renderer pipelines remain canonical; TSD creates no competing tooling.

# Bounded package queue

| ID | Scope | Status | Evidence baseline | Exact next action |
|---|---|---|---|---|
| `TSD-001` | taxonomy/hierarchy foundation and three-record pilot | completed | PR #335; merge `44fe3af9f29b3ae0164ac5d60fc1f14137b5cea5`; registry 19 → 22 | preserve archive |
| `TSD-002A` | scheduler, DI, Lua bindings and build foundation | completed | PR #340; merge `82f35c0147fdd33c8d4e70d98d003385daf61de6`; registry 22 → 26 | preserve archive |
| `TSD-002B` | DB connection/migrations, transaction and world-persistence classification | completed | PR #342; merge `1410a8622aaca5e4afe1bd15aa2695e2dbb7bb94`; registry 26 → 29 | preserve archive |
| `TSD-003` | account, character and progression | completed | PR #355; merge `1098363a708a1f5f875850670a5aad411031e188`; registry 29 → 35 | preserve archive |
| `TSD-004` | Cyclopedia family | completed | PR #359; merge `6d6df89b02fca525ef76011369d8c6243de231d8`; registry 35 → 39 | preserve archive |
| `TSD-005` | combat, weapons and vocations | next | `combat`, `spells`, `vocations`, `weapon-proficiency` and completed TSD-004 boundaries | split only durable formula/state/weapon/combat domains |
| `TSD-006` | creatures, hunting, raids and bosses | planned | `spawns`, `prey`, `bestiary`, `bosstiary`, `cyclopedia` | separate spawn, encounter, credit, reward and scheduling |
| `TSD-007` | items and economy | planned | `market`, `imbuements`, `exaltation-forge` | classify item lifecycle, movement, trade, market and rewards |
| `TSD-008` | world content | planned | quests/NPCs/houses/OTBM records | classify map, movement, quests, houses, travel and instances |
| `TSD-009` | social, communication and trust | planned | social/account category and TSD-003 account boundaries | separate communication, party/guild and sanctions/audit |
| `TSD-010` | protocol and client | planned | `protocol` umbrella, maintained client and account/Cyclopedia boundaries | classify wire/session/client-feature domains |
| `TSD-011` | analytics, security and AI | planned | analytics/safety boundaries | register durable read-only/analysis domains only |
| `TSD-012` | validation and live-operations tooling | planned | OTBM/E2E/UI modules | register only non-duplicative long-lived tooling |
| `TSD-013` | Oteryn migration classification | planned | completed inventories and proof packages | classify modules; do not copy code or create another registry |

# Completed delivery evidence

## TSD-001

- Feature PR #335, head `f8524a7a51d6c5b84bcd847da9a2a7923af34dfb`.
- Merge `44fe3af9f29b3ae0164ac5d60fc1f14137b5cea5`; lifecycle merge `cc8b3bdc9b34fb8e6802bd1a0fc0d535de2dd9ba`.
- Registry 19 → 22; added only `engine-runtime-lifecycle`, `configuration`, `lua-runtime`.
- Archive: `docs/agents/tasks/archive/CAN-20260714-tibia-system-decomposition-bootstrap.md`.

## Source-role mapping prerequisite

- UI-001A feature PR #337, merge `09f7049401253dd38c8f34506946c2fbe287d220`.
- Lifecycle merge `6d368766cc47794ec0145b4b32613edaf7588adb`.
- Source registry v1 → v2; modules changed 0.
- Archive: `docs/agents/tasks/archive/CAN-20260714-upstream-intelligence-source-role-path-mapping.md`.

## TSD-002A

- Feature PR #340, head `4a044a0f93a23aa7c610c41d1003d5f83d7fc62c`.
- Merge `82f35c0147fdd33c8d4e70d98d003385daf61de6`; lifecycle merge `709693b4cca42214c52e63ea15a1a22b93f9a113`.
- Registry 22 → 26; added only `build-system`, `engine-scheduler`, `engine-service-container`, `lua-bindings`.
- Existing records modified 0; `data-registries` and `platform-compatibility` were merged into existing boundaries.
- Archive: `docs/agents/tasks/archive/CAN-20260714-tibia-system-decomposition-engine-foundation.md`.

## TSD-002B

- Feature PR #342, head `4ec6fa8df83f80cde17219251a3e50aa9788ab23`.
- Merge `1410a8622aaca5e4afe1bd15aa2695e2dbb7bb94`; lifecycle merge `d3dbca52ced28e747f1764167e1d479bd2568a6d`.
- Registry 26 → 29; added only `database-connection`, `database-migrations`, `world-persistence`.
- Existing records modified 0; `player-persistence` remained the compatibility umbrella.
- Archive: `docs/agents/tasks/archive/CAN-20260714-tibia-system-decomposition-persistence-transactions.md`.

## TSD-003

- Feature PR #355, head `d85f248a624fc01c0efa5f7970988fd6aa15e370`.
- Merge `1098363a708a1f5f875850670a5aad411031e188`; lifecycle merge `9f82f93977e82784370961a72104efacd497c8e0`.
- Registry 29 → 35; added only `account-authentication`, `account-lifecycle`, `character-lifecycle`, `character-progression`, `vocations`, `weapon-proficiency`.
- Existing records modified 0; `player-persistence`, `protocol`, `achievements` and `wheel-of-destiny` remained stable.
- Archive: `docs/agents/tasks/archive/CAN-20260714-tibia-system-decomposition-account-character-progression.md`.

## TSD-004

- Feature PR #359, head `e4ce70fdb18d604b001edf8d577481e1c2aea762`.
- Merge `6d6df89b02fca525ef76011369d8c6243de231d8`.
- Registry 35 → 39; added only `bestiary`, `bosstiary`, `cyclopedia-character`, `titles`.
- Existing records modified 0; `cyclopedia`, `charms`, `houses`, `achievements`, `protocol`, character lifecycle/progression and player persistence remained stable.
- Final feature checks: Real Tibia Module Registry #226, Upstream Intelligence #254, Agent Task Ownership #1086, CI #2199 and ready-state CI #2200 — success.
- Cyclopedia Items/Map remain umbrella/protocol/client surfaces; Cyclopedia Houses remains covered by `houses`; appearance unlocks remain deferred.
- Archive: `docs/agents/tasks/archive/CAN-20260714-tibia-system-decomposition-cyclopedia-family.md`.

No completed package evidence automatically establishes authentication security, persistence/transaction safety, progression or combat formulas, Cyclopedia/Bestiary/Bosstiary/title correctness, protocol compatibility, maintained-client behavior, runtime behavior, physical-client E2E, Real Tibia parity or Oteryn readiness.

# Oteryn migration policy

The legacy repository remains the evidence laboratory. No code is copied to Oteryn by this program.

Future classifications are `REUSE`, `ADAPT`, `REVALIDATE`, `REWRITE`, `DO_NOT_MIGRATE` and `EXPERIMENTAL_ONLY`. Code presence is insufficient; the default is undecided or `REVALIDATE`.

Required flow:

```text
legacy inventory
→ evidence
→ runtime proof
→ E2E proof
→ migration classification
→ bounded Oteryn package
```

# Exact next operational task

After the TSD-004 lifecycle archive merges, re-read then-current `main`, open PRs, active tasks and ownership, then create only:

```text
task: CAN-20260714-tibia-system-decomposition-combat-weapons-vocations
package: TSD-005
branch: docs/tibia-system-decomposition-combat-weapons-vocations
```

Preserve `combat`, `spells`, `vocations` and `weapon-proficiency`; split only durable targeting, permission, formula, mitigation, condition, weapon and vocation-combat boundaries supported by independent current implementation roots.

# Handoff

Continue one task, branch and PR at a time. Before every package re-read current main, open PRs, active tasks and ownership. Preserve all proof limits and never infer behavioral correctness from inventory paths or passing CI.
