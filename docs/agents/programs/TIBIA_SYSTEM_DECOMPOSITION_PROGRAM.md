---
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
name: Tibia System Decomposition
status: active
owner: repository-wide
created: 2026-07-14T15:43:00+02:00
updated: 2026-07-14T19:45:00+02:00
last_verified_commit: "3eb7ae24bb1b918a0b040270e58c49037a873ee8"
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
| `TSD-003` | account, character and progression | active | PR #355; implementation head `3eb7ae24bb1b918a0b040270e58c49037a873ee8`; registry 29 → 35 | finish current-main integration, exact-head/ready CI, squash merge and lifecycle archive |
| `TSD-004` | Cyclopedia family | next | `cyclopedia` and `charms` umbrellas plus completed TSD-003 boundaries | preserve umbrella; evaluate durable children |
| `TSD-005` | combat, weapons and vocations | planned | `combat`, `spells`, `vocations` and progression boundaries | split only durable formula/state/weapon domains |
| `TSD-006` | creatures, hunting, raids and bosses | planned | `spawns`, `prey`, `cyclopedia` | separate spawn, encounter, credit, reward and scheduling |
| `TSD-007` | items and economy | planned | `market`, `imbuements`, `exaltation-forge` | classify item lifecycle, movement, trade, market and rewards |
| `TSD-008` | world content | planned | quests/NPCs/houses/OTBM records | classify map, movement, quests, houses, travel and instances |
| `TSD-009` | social, communication and trust | planned | social/account category and TSD-003 account boundaries | separate communication, party/guild and sanctions/audit |
| `TSD-010` | protocol and client | planned | `protocol` umbrella, maintained client and TSD-003 authentication/lifecycle boundaries | classify wire/session/client-feature domains |
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
- `transaction-boundaries` and `save-restart-reload` were merged into existing boundaries; `database-reconciliation` was deferred.
- Final feature checks: Real Tibia Module Registry #156, Upstream Intelligence #184, Agent Task Ownership #1013, CI #2128 and ready-state CI #2129 — success.
- Archive: `docs/agents/tasks/archive/CAN-20260714-tibia-system-decomposition-persistence-transactions.md`.

No TSD-002B evidence establishes ACID semantics, rollback completeness, retry/reconnect safety, migration reversibility, idempotency, crash consistency, restart/reload safety or production MariaDB compatibility.

# Current active package — TSD-003

Task: `CAN-20260714-tibia-system-decomposition-account-character-progression`; draft PR #355.

Registry 29 → 35. Added only:

```text
account-authentication
account-lifecycle
character-lifecycle
character-progression
vocations
weapon-proficiency
```

Existing module records changed: 0. `player-persistence`, `protocol`, `achievements` and `wheel-of-destiny` remain stable existing boundaries.

Key classification:

- account entitlements and premium state remain account-lifecycle capabilities;
- account sanctions are deferred to TSD-009;
- generic account-wide storage is not claimed from quest-specific evidence;
- level, skill, magic-level, stamina, offline-training, death-loss and blessing state remain findings inside `character-progression`;
- individual vocation entries remain inside one `vocations` registry lifecycle;
- titles, outfits, mounts and familiars are deferred to later Cyclopedia/client inventory;
- Weapon Proficiency receives a durable independent record.

Implementation/focused-test head `3eb7ae24bb1b918a0b040270e58c49037a873ee8` passed:

- Real Tibia Module Registry #191;
- Upstream Intelligence #219;
- Agent Task Ownership #1058;
- repository CI #2170.

The package does not prove authentication security, token replay safety, save atomicity, progression formulas, vocation parity, Weapon Proficiency parity, runtime behavior, physical-client E2E or Oteryn readiness.

Detailed evidence: `docs/agents/real-tibia/TSD_003_ACCOUNT_CHARACTER_PROGRESSION_REPORT.md`.

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

After PR #355 passes final exact-head review, ready-state Linux/Required, squash merge and a separate lifecycle archive, re-read then-current `main` and create only:

```text
task: CAN-20260714-tibia-system-decomposition-cyclopedia-family
package: TSD-004
branch: docs/tibia-system-decomposition-cyclopedia-family
```

Preserve the `cyclopedia` umbrella and evaluate durable items, bestiary, bosstiary, map, character/title and house surfaces without duplicating `charms`, `achievements`, account/character lifecycle, protocol or existing validation tooling.

# Handoff

Continue one task, branch and PR at a time. Before every package re-read current main, open PRs, active tasks and ownership. Preserve all proof limits and never infer behavioral correctness from inventory paths or passing CI.
