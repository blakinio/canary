---
program_id: CAN-PROGRAM-E2E-PLATFORM
name: Universal OTS E2E automation
status: active
owner: e2e-platform-agent
created: 2026-07-13T00:00:00+02:00
updated: 2026-07-23T00:00:00+02:00
last_verified_commit: f8f8d0fd830a8e01aa1cbc93d9e41907cc8ea077
primary_paths:
  - tools/e2e/**
  - tests/e2e/runtime/**
  - tests/e2e/client/**
shared_integration_paths:
  - .github/workflows/*e2e*.yml
  - tests/e2e/scenario_registry.*
related_programs:
  - CAN-PROGRAM-CYCLOPEDIA
  - CAN-PROGRAM-QUEST-AUDIT
  - CAN-PROGRAM-WHEEL-OF-DESTINY
  - CAN-PROGRAM-OTBM
  - CAN-PROGRAM-OTBM-E2E-ROUTING
cross_repo_contracts:
  - OTS-E2E-CANARY-OTCLIENT
---

# Mission

Maintain one reusable, disposable environment in which autonomous agents run real Canary and a real controlled OTClient, execute feature-specific scenarios, verify runtime/protocol/database effects, collect deterministic evidence, and clean up without touching production systems.

The current programme phase is no longer platform bootstrap. The reusable physical platform is merged and has proven login/relog, movement, floor change, teleport, typed persistence, bounded two-client orchestration, controlled client-disconnect recovery, and one representative cross-system gameplay journey. Further expansion must remain feature-driven and reuse these proven contracts rather than creating parallel orchestration.

Durable architecture: `docs/architecture/universal-e2e-gameplay-validation.md`.

# Authoritative responsibility boundary

## Universal E2E platform owns

- disposable MariaDB/MySQL bootstrap, schema import, fixtures and teardown;
- exact Canary artifact resolution or local build, isolated configuration, startup, readiness and shutdown;
- controlled pinned `blakinio/otclient` artifact resolution/build;
- transient map/client assets with integrity evidence and no committed binaries;
- virtual display and physical client automation;
- deterministic account, character, world, host, port and version configuration;
- login, safe logout, relog, timeout, crash handling and cleanup;
- stable scenario validation and generic physical action execution;
- shared SQL/protocol/evidence assertion surfaces;
- screenshots, logs, traces and machine-readable results;
- generic multi-client or fault/recovery capabilities when implemented through separate platform tasks.

The platform must remain feature-neutral. It must not encode feature-specific quest storages, rewards, NPCs, monsters, map landmarks or expected gameplay values.

## OTBM/static programmes own

- canonical static map evidence through the Unified OTBM World Index;
- walkability and route graph evidence through Reachability;
- AID/UID/item/position runtime-handler correlation through Script Resolution;
- reviewed floor-transition and other static mechanic evidence;
- static route/landmark/interaction planning through `CAN-PROGRAM-OTBM-E2E-ROUTING`.

Static evidence is preflight evidence, not physical gameplay success.

## Feature programmes own

- feature-specific scenario definitions;
- deterministic fixtures;
- feature actions and expected values;
- feature SQL/server/client/UI assertions;
- persistence expectations;
- feature cleanup requirements.

A feature task consumes platform implementation paths read-only unless a separate platform task explicitly owns a required generic interface change.

# Confirmed merged foundation

| Capability | State | Evidence | Reuse rule |
|---|---|---|---|
| Universal disposable physical E2E platform | merged | PR #245 | canonical lifecycle; never create a second orchestrator |
| Declarative bounded physical gameplay actions | merged | PR #446 | extend generic action interfaces only through platform tasks |
| Changed-scenario selection on same-repository PRs | merged | PR #477 | feature scenarios use the existing workflow/resolver |
| Physical movement | merged and runtime-proven | PR #481 | baseline for position-aware execution |
| Physical non-teleport floor change | merged and runtime-proven | PR #512 | baseline for cross-floor execution |
| Physical teleport | merged and runtime-proven | PR #525 | baseline for mechanic + persistence/relog execution |
| Typed persistence assertion surfaces | implementation merged; closure matrix delivered | PRs #565, #583, #586, #591, #595, #603, #608, #615 and closure PR #666 | use `docs/e2e/PERSISTENCE_ASSERTION_MATRIX.md`; add a new generic type only for a concrete evidence-backed reusable gap |
| Bounded two-client orchestration | merged and runtime-proven | PR #747; lifecycle archive #753 | reuse `canary-universal-e2e-two-client-orchestration-v1` for exactly one secondary controlled OTClient; do not generalize actor count or create a second server lifecycle without a separate platform task |
| Controlled client-disconnect recovery | merged and runtime-proven | PR #751; lifecycle archive #764 | reuse `canary-universal-e2e-client-disconnect-recovery-v1` for the fixed maintained-client `g_game.forceLogout()` fault and real second-login recovery; it is not arbitrary fault injection |
| Representative cross-system gameplay journey | merged and runtime-proven M4 sentinel | PR #765; lifecycle archive #791 | `journeys/promotion-combat-persistence` composes proven deterministic combat, arena return, Canary NPC promotion and typed relog/persistence; keep focused lower-level scenarios as the source of feature-specific proof |
| Cyclopedia-specific prototype | closed and superseded | PR #224 | historical evidence only; do not revive or copy its infrastructure |

# Current active integration work

## OTBM-aware physical routing

Draft PR #562 introduces `CAN-PROGRAM-OTBM-E2E-ROUTING` and owns the detailed bridge between static OTBM evidence and physical E2E.

Its programme boundary covers:

- executable route export from existing Reachability data;
- semantic landmark resolution;
- route interaction semantics;
- route preflight against exact provenance;
- Universal route-following integration;
- first landmark-to-landmark physical reference scenario.

This E2E programme must consume that bridge when stable and must not duplicate its parser, World Index, pathfinder or route-planning contracts.

# Stable scenario contract

Each scenario must define or resolve:

- unique scenario ID and owning programme;
- required server/client versions and capabilities;
- database and character fixture requirements;
- setup steps safe to repeat;
- client actions or protocol requests;
- static preflight requirements when relevant;
- observable server, client, UI and SQL assertions;
- persistence/relog checks when relevant;
- timeout and failure markers;
- artifacts to retain;
- cleanup requirements;
- paths the feature task may and may not edit.

Use `docs/agents/templates/E2E_SCENARIO.md` when adding a suite.

# Evidence maturity

Scenarios and programme claims must state the strongest level actually proven:

- `M0 static`: map/source/handler evidence only;
- `M1 physical-action`: real controlled OTClient performs the bounded action;
- `M2 feature-outcome`: feature-specific runtime assertions pass;
- `M3 persistence`: M2 plus safe logout, persisted state and relog verification;
- `M4 cross-actor/system`: multiple clients/processes or major systems interact successfully;
- `M5 recovery`: controlled failure plus expected recovery/rollback/idempotency/cleanup proof.

Never promote a lower evidence level to a higher one without the corresponding physical/runtime proof.

# Interface-change rule

When a feature needs a new generic capability:

1. the feature task records the missing capability and proposed interface;
2. a separate Universal E2E platform task claims and implements the generic capability;
3. the platform PR adds focused tests and preserves existing registered scenarios;
4. the feature PR consumes the stable interface without copying orchestration;
5. `depends_on` and `blocks` record merge order;
6. Canary/OTClient changes use a shared coordination ID and the cross-repository contract rules.

The same rule applies to generic route following, map-item interaction, persistence assertions, multi-client orchestration and fault injection.

# Ordered next-phase queue

The detailed implementation plan and acceptance gates live in `docs/architecture/universal-e2e-gameplay-validation.md`.

## E2E-GAMEPLAY-001 — programme reconciliation and architecture

Purpose: replace stale pre-bootstrap programme state with the current architecture and ordered queue.

Owner: documentation/agent-governance task.

Status: active through task `CAN-20260718-universal-e2e-gameplay-roadmap` / PR #563.

## E2E-GAMEPLAY-002 — OTBM-aware route consumption

Purpose: execute evidence-backed route plans through the existing physical OTClient runner with exact-position synchronization and fail-closed divergence evidence.

Depends on: stable required outputs from `CAN-PROGRAM-OTBM-E2E-ROUTING`.

Hard boundary: E2E consumes route plans; it does not implement an independent pathfinder.

## E2E-GAMEPLAY-003 — quest and NPC vertical slices

Purpose: add one deterministic real-client quest/NPC flow, including navigation when required and M3 persistence proof for durable quest state.

Start narrow. Do not attempt broad quest coverage in one PR.

## E2E-GAMEPLAY-004 — combat vertical slice

Purpose: prove one deterministic bounded combat lifecycle with a real client and retained first-failure evidence.

Use a controlled fixture; never depend on random public-world occupancy.

## E2E-GAMEPLAY-005 — persistence assertion matrix

Purpose: provide reusable assertion surfaces for storages/quest state, inventory/depot/inbox, bank/economy, vocation/progression and other durable feature rows.

Status: implementation complete through typed persistence slices PRs #565, #583, #586, #591, #595, #603, #608 and #615; canonical closure inventory delivered by PR #666 in `docs/e2e/PERSISTENCE_ASSERTION_MATRIX.md`.

Current reusable types are:

- `player_field`;
- `player_storage`;
- `player_item_presence`;
- `player_balance`;
- `player_magic_level`;
- `player_soul`;
- `player_skill_level`;
- `player_vocation`.

`player_field`, `player_balance`, `player_magic_level`, `player_soul`, `player_skill_level` and normalized `player_vocation` use controlled-client post-relog verification plus final fixed-shape SQL verification. `player_storage` and `player_item_presence` are intentionally database-only after the full canonical two-session lifecycle because the shared platform has no trustworthy universal client read surface for arbitrary storages or cross-location item persistence.

The closure audit also aligned the pre-existing client-verified `player_field` expected-value range with the exact Lua integer boundary already used by `player_balance`. No new assertion type was required.

This package proceeds independently of route planning because it reuses the already-proven two-session login/logout/relog lifecycle.

## E2E-GAMEPLAY-006 — multi-client orchestration

Purpose: extend the single canonical orchestrator to multiple controlled OTClients only when a concrete feature requires it.

Status: delivered through feature PR #747 and lifecycle archive PR #753. The merged `canary-universal-e2e-two-client-orchestration-v1` contract supports exactly one secondary controlled OTClient and physically proved simultaneous two-client presence, mutual visibility, bounded secondary shutdown and preservation of the primary canonical relog/persistence lifecycle.

Candidate consumers remain trade, party, PvP or direct player-to-player interaction; each must consume the bounded interface instead of copying orchestration.

## E2E-GAMEPLAY-007 — runtime fault and recovery validation

Purpose: introduce bounded explicit fault-injection seams only after a stable baseline scenario exists, then prove expected recovery, rollback, idempotency or cleanup.

Status: delivered through feature PR #751 and lifecycle archive PR #764. The merged `canary-universal-e2e-client-disconnect-recovery-v1` contract physically proved one explicit maintained-client `g_game.forceLogout()` disconnect, expected-failure classification, real second-session recovery and clean safe logout.

Never target production or third-party systems. The delivered seam is fixed-purpose client-disconnect recovery, not a generic arbitrary fault-command interface.

## E2E-GAMEPLAY-008 — cross-system gameplay journeys

Purpose: compose already-proven capabilities into representative player journeys such as temple -> depot -> NPC -> quest/combat -> reward -> relog/persistence.

Status: first representative journey delivered through PR #765 and lifecycle archive PR #791. `journeys/promotion-combat-persistence` physically composes deterministic combat, explicit arena close and return, Canary NPC promotion and durable Royal Paladin/zero-balance relog verification on the existing platform. No active 008 implementation task remains after lifecycle closure; future journeys require a fresh bounded task justified by concrete feature demand.

Journey tests are integration sentinels and never replace focused feature tests.

# Dependency guidance

```text
E2E-GAMEPLAY-001 architecture
        |
        +------------------------------+
        |                              |
        v                              v
OTBM-E2E routing programme        E2E-GAMEPLAY-005 persistence
        |
        v
E2E-GAMEPLAY-002 route consumption
        |
        +----------------------+
        |                      |
        v                      v
E2E-GAMEPLAY-003 quests/NPC    E2E-GAMEPLAY-004 combat
        |                      |
        +-----------+----------+
                    |
                    v
           E2E-GAMEPLAY-008 journeys

E2E-GAMEPLAY-006 multi-client: delivered as a bounded reusable platform contract; extend only from concrete feature demand.
E2E-GAMEPLAY-007 recovery: delivered as a bounded fixed client-disconnect recovery contract; add other fault seams only through separate evidence-backed platform tasks.
```

# Suite roots

Feature-owned suites may live under roots including:

- `tests/e2e/scenarios/login/**`;
- `tests/e2e/scenarios/cyclopedia/**`;
- `tests/e2e/scenarios/quests/**`;
- `tests/e2e/scenarios/wheel/**`;
- `tests/e2e/scenarios/forge/**`;
- `tests/e2e/scenarios/market/**`;
- `tests/e2e/scenarios/npc/**`;
- `tests/e2e/scenarios/combat/**`;
- `tests/e2e/scenarios/instances/**`;
- `tests/e2e/scenarios/protocol/**`;
- `tests/e2e/scenarios/multiclient/**`;
- `tests/e2e/scenarios/recovery/**`;
- `tests/e2e/scenarios/journeys/**`.

Additional roots require normal programme/task ownership and registry integration; do not create complete parallel workflows per suite.

# Execution target

The user-facing interface should continue to converge on commands equivalent to:

```text
run-e2e --suite login
run-e2e --suite quests
run-e2e --suite combat
run-e2e --suite forge
run-e2e --all
```

The exact executable remains an implementation detail of the existing platform. Agents must extend verified repository conventions rather than inventing another runner.

# Safety invariants

- no production credentials, database, host or irreversible external action;
- no committed Tibia assets, downloaded OTBM files, database dumps or secrets;
- every run uses an isolated disposable environment and always attempts cleanup;
- external binaries and assets are pinned or hash-recorded;
- failures retain enough evidence to identify the exact first failed layer;
- feature PRs never silently modify shared platform lifecycle behavior;
- platform PRs treat registered feature suites as compatibility inputs;
- no E2E success claim without a verified real workflow result on the exact relevant commit;
- no static OTBM success claim may be presented as physical gameplay proof;
- no independent E2E pathfinder after the OTBM route integration boundary exists;
- no blind nontrivial navigation once evidence-backed route consumption is available.

# Handoff

## Start here

Future agents should read, in order:

1. root `AGENTS.md`;
2. `docs/agents/REPOSITORY_MAP.md`;
3. `docs/agents/CONTEXT_ROUTING.md`;
4. this programme record;
5. `docs/architecture/universal-e2e-gameplay-validation.md`;
6. the selected active task and live PR;
7. for route work, the current merged/draft `OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md` and its technical contract.

## Do not repeat

- do not reopen or copy superseded PR #224 infrastructure;
- do not create one complete workflow per feature;
- do not create a second physical E2E orchestrator;
- do not implement an independent OTBM parser, World Index or route pathfinder inside E2E;
- do not use `opentibiabr/otclient` as a writable target;
- do not commit client assets or map binaries;
- do not invent coordinates, item IDs, NPCs, monsters, storages or dynamic Lua behavior;
- do not weaken login/logout/relog or physical evidence requirements to make a scenario pass.

## Next action selection

Choose the first queue item whose dependencies are already satisfied on current `main`.

At the time of this reconciliation:

- E2E-GAMEPLAY-001 remains the architecture/documentation package;
- E2E-GAMEPLAY-002 remains governed by the current OTBM-aware routing programme state and must be verified live before further route-consumption work;
- E2E-GAMEPLAY-005 persistence assertion implementation and canonical matrix are complete through the merged typed slices and closure package PR #666;
- E2E-GAMEPLAY-006 bounded two-client orchestration is delivered through PR #747 and lifecycle archive #753;
- E2E-GAMEPLAY-007 controlled client-disconnect recovery is delivered through PR #751 and lifecycle archive #764;
- E2E-GAMEPLAY-008 has one representative M4 integration sentinel delivered through PR #765 and lifecycle archive #791; no active 008 implementation task remains.

Never infer dependency completion from this document alone. Verify current task/PR/merge state before claiming the next package.
