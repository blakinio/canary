---
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
name: Tibia System Decomposition
status: active
owner: repository-wide
created: 2026-07-14T15:43:00+02:00
updated: 2026-07-14T23:55:00+02:00
last_verified_commit: "ff38dc9ff4092a8a1c631f62cea6df1c41c4f6a6"
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

# Bounded package queue

| ID | Scope | Status | Evidence baseline | Exact next action |
|---|---|---|---|---|
| `TSD-001` | taxonomy/hierarchy foundation and pilot | completed | PR #335; registry 19 → 22 | preserve archive |
| `TSD-002A` | engine foundation | completed | PR #340; registry 22 → 26 | preserve archive |
| `TSD-002B` | persistence and transactions | completed | PR #342; registry 26 → 29 | preserve archive |
| `TSD-003` | account, character and progression | completed | PR #355; registry 29 → 35 | preserve archive |
| `TSD-004` | Cyclopedia family | completed | PR #359; registry 35 → 39 | preserve archive |
| `TSD-005` | combat, weapons and vocations | completed | PR #362; registry 39 → 41 | preserve archive |
| `TSD-006` | creatures, hunting, raids and bosses | completed | PR #364; registry 41 → 45 | preserve archive |
| `TSD-007` | items and economy | active | PR #366; implementation head `ff38dc9ff4092a8a1c631f62cea6df1c41c4f6a6`; registry 45 → 49 | finish exact-head/ready CI, squash merge and lifecycle archive |
| `TSD-008` | world content | next | quests/NPCs/houses/OTBM/raids and TSD-007 item boundaries | classify map, movement, quests, houses, travel and instances |
| `TSD-009` | social, communication and trust | planned | social/account boundaries | separate communication, party/guild and sanctions/audit |
| `TSD-010` | protocol and client | planned | protocol umbrella and maintained client | classify wire/session/client-feature domains |
| `TSD-011` | analytics, security and AI | planned | analytics/safety boundaries | register durable read-only/analysis domains only |
| `TSD-012` | validation and live operations | planned | OTBM/E2E/UI modules | register only non-duplicative tooling |
| `TSD-013` | Oteryn migration classification | planned | completed inventories/proof packages | classify modules; do not copy code or create another registry |

# Completed delivery evidence

| Package | Feature merge | Lifecycle merge | Registry result |
|---|---|---|---|
| TSD-001 | `44fe3af9f29b3ae0164ac5d60fc1f14137b5cea5` | `cc8b3bdc9b34fb8e6802bd1a0fc0d535de2dd9ba` | 19 → 22 |
| UI-001A prerequisite | `09f7049401253dd38c8f34506946c2fbe287d220` | `6d368766cc47794ec0145b4b32613edaf7588adb` | source registry v1 → v2 |
| TSD-002A | `82f35c0147fdd33c8d4e70d98d003385daf61de6` | `709693b4cca42214c52e63ea15a1a22b93f9a113` | 22 → 26 |
| TSD-002B | `1410a8622aaca5e4afe1bd15aa2695e2dbb7bb94` | `d3dbca52ced28e747f1764167e1d479bd2568a6d` | 26 → 29 |
| TSD-003 | `1098363a708a1f5f875850670a5aad411031e188` | `9f82f93977e82784370961a72104efacd497c8e0` | 29 → 35 |
| TSD-004 | `6d6df89b02fca525ef76011369d8c6243de231d8` | `f163ed8e3b3d51e65c7fef1bc03830b12b2e6bfa` | 35 → 39 |
| TSD-005 | `68b9836cc8e6f55add9a6f3f8d7919e031defc50` | `f68f826915882b0b20081b8fca5ed975ce303f45` | 39 → 41 |
| TSD-006 | `8dfec274b0f460c1f0d6bee6c8a4b95a3ecf8c12` | `821f213038770d68cd95b1b22afa78937b974210` | 41 → 45 |

# Current active package — TSD-007

Task: `CAN-20260714-tibia-system-decomposition-items-economy`; draft PR #366.

Registry 45 → 49. Added only:

```text
containers
item-decay
item-definitions
item-instances
```

Existing records modified: 0. `market`, `imbuements`, `exaltation-forge`, `weapons`, `boss-encounters`, player/world persistence and protocol remain stable.

Classification:

- ItemType/Items registry and XML/appearance loading → `item-definitions`;
- runtime factory, attributes, transforms and serialization → `item-instances`;
- nested cylinder/container/depot/inbox/mailbox/reward-container lifecycle → `containers`;
- scheduler-backed duration/transform lifecycle → `item-decay`;
- movement, stacking, transfer, stash and managed-container behavior remain capabilities because orchestration spans Game/Cylinder/Container;
- market, Forge, Imbuements, weapons and boss rewards remain already covered;
- account coins and NPC trade remain deferred for a later bounded economy/source inventory.

Implementation/focused-test head `ff38dc9ff4092a8a1c631f62cea6df1c41c4f6a6` passed:

- Real Tibia Module Registry #300;
- Upstream Intelligence #331;
- Agent Task Ownership #1147;
- repository CI #2263;
- focused registry/source-role tests;
- schema/dependency validation;
- deterministic `generate --check`;
- discovery and `affected` commands.

Older TSD-005/TSD-006 tests now assert their package minimum rather than freezing the global total; TSD-007 owns the exact total 49 assertion.

Detailed evidence: `docs/agents/real-tibia/TSD_007_ITEMS_ECONOMY_REPORT.md`.

No completed package evidence establishes item metadata parity, movement/transfer atomicity, duplication/loss safety, container correctness, serializer completeness, decay timing/restart behavior, economy correctness, runtime behavior, protocol compatibility, physical-client E2E, Real Tibia parity or Oteryn readiness.

# Oteryn migration policy

The legacy repository remains the evidence laboratory. No code is copied to Oteryn by this program. Classification defaults to undecided or `REVALIDATE` until inventory, evidence, runtime proof and E2E proof exist.

# Exact next operational task

After PR #366 passes final exact-head review, ready-state Linux/Required, squash merge and a separate lifecycle archive, re-read then-current `main` and create only:

```text
task: CAN-20260714-tibia-system-decomposition-world-content
package: TSD-008
branch: docs/tibia-system-decomposition-world-content
```

Preserve quests, NPCs, houses, OTBM tooling, raids, spawns, item/container and persistence boundaries. Add only durable world/map/movement/travel/instance boundaries with independent current implementation roots.

# Handoff

Continue one task, branch and PR at a time. Re-read current main, open PRs, active tasks and ownership before every package. Preserve all proof limits and never infer behavioral correctness from inventory paths or passing CI.
