# Universal E2E Gameplay Validation Architecture

## Purpose

This document is the durable target architecture for extending the existing Universal OTS E2E platform from isolated physical proofs into broad, evidence-backed gameplay validation.

The core rule is simple:

> Static tools explain what should be possible. Universal Physical E2E proves what a real controlled OTClient can actually do against the exact Canary runtime.

The project must continue to use one reusable physical E2E lifecycle. Feature teams add scenarios and assertions; they do not create parallel runners, workflows, map parsers, pathfinders or client harnesses.

## Current proven baseline

The following foundations are already merged and must be reused:

- PR #245: Universal disposable MariaDB + exact Canary + controlled OTClient physical E2E platform;
- PR #446: declarative bounded physical gameplay action plans;
- PR #477: automatic selection of exactly one changed same-repository scenario;
- PR #481: deterministic physical movement proof;
- PR #512: deterministic non-teleport floor-change proof;
- PR #525: deterministic physical teleport proof with persistence/relog sentinel.

The OTBM-aware route bridge is separately owned by the programme introduced in draft PR #562. That programme is responsible for converting static map evidence into an executable route-plan contract. This architecture consumes that boundary; it does not duplicate it.

## Target outcome

A future feature scenario should be able to express an intent such as:

```text
login Knight 1
navigate to thais.depot
interact with depot locker
assert expected state
safe logout
relog
assert persisted state
safe logout
```

without embedding a long hand-authored directional sequence or inventing map mechanics.

For a more complex flow:

```text
login
navigate to quest NPC
perform dialogue
navigate through route mechanics
complete quest action
assert storage/inventory/database/UI state
logout
relog
assert persistence
```

The scenario owns the feature intent and expected gameplay result. Static map tooling owns map truth. The Universal E2E platform owns physical execution and evidence.

## Architectural layers

### Layer 1: deterministic runtime environment

Owner: Universal E2E platform.

Responsibilities:

- disposable database bootstrap and teardown;
- exact Canary revision/build selection;
- pinned controlled OTClient revision/build selection;
- transient map/client asset acquisition with integrity evidence;
- isolated host/port/account/player configuration;
- server/client startup, readiness, shutdown and cleanup;
- canonical login, safe logout, relog and timeout handling.

This layer must remain feature-neutral.

### Layer 2: static world and mechanic evidence

Owner: OTBM and related static-analysis programmes.

Responsibilities include reuse of:

- Unified OTBM World Index for exact tile/item/mechanic positions;
- Reachability for walkability and graph/path evidence;
- Script Resolution for AID/UID/item/position handler correlation;
- reviewed floor-transition evidence;
- teleport destinations;
- spawn/NPC evidence where relevant;
- storage dependency evidence where relevant.

This layer answers questions such as:

- where is an object or mechanic?
- is a tile statically walkable?
- is a route confirmed, conditional or unreachable?
- what static handler evidence exists for a mechanic?

It does not claim that a physical client completed the route or that runtime state satisfied a condition.

### Layer 3: OTBM-to-E2E navigation bridge

Owner: `CAN-PROGRAM-OTBM-E2E-ROUTING` / PR #562 programme.

Responsibilities:

- executable route export from existing Reachability data;
- semantic landmark resolution;
- route interaction semantics;
- route preflight against exact map/index/provenance;
- eventual `follow_route`/route-plan consumption contract with Universal E2E;
- first evidence-backed landmark-to-landmark reference scenario.

This layer must not introduce a second OTBM parser, World Index or independent pathfinder.

Until PR #562 is merged, consumers must treat field-level route schemas as unstable and depend only on the programme boundary.

### Layer 4: physical action execution

Owner: Universal E2E platform.

Responsibilities:

- execute bounded declared client actions;
- synchronize expected and observed player position;
- execute route-plan segments through the controlled real OTClient;
- expose deterministic action/result markers;
- stop fail-closed when physical state diverges from the executable plan;
- preserve canonical login/logout/relog lifecycle.

Feature suites may request capabilities from this layer but must not duplicate them.

### Layer 5: feature scenario suites

Owner: the corresponding feature programme.

Examples:

- `tests/e2e/scenarios/quests/**`;
- `tests/e2e/scenarios/npc/**`;
- `tests/e2e/scenarios/combat/**`;
- `tests/e2e/scenarios/forge/**`;
- `tests/e2e/scenarios/market/**`;
- `tests/e2e/scenarios/wheel/**`;
- `tests/e2e/scenarios/instances/**`;
- `tests/e2e/scenarios/protocol/**`.

Each scenario owns:

- deterministic fixture requirements;
- feature-specific actions;
- feature-specific expected gameplay values;
- server/client/UI/SQL assertions;
- required persistence/relog assertions;
- cleanup expectations.

A feature scenario consumes shared platform code read-only unless a separate platform task owns a generic interface change.

### Layer 6: assertion and persistence evidence

Owner: shared Universal E2E assertion interfaces plus feature-owned expectations.

Assertion classes should include, when relevant:

- observed player position and floor;
- server-side login/session markers;
- protocol event markers;
- SQL scalar/table assertions;
- storage values;
- inventory/depot/inbox state;
- bank or economy state;
- quest progression;
- vocation/progression values;
- online/offline ownership state;
- screenshots or UI state where server-side evidence is insufficient.

Persistence-sensitive scenarios should prove state across a canonical safe logout and relog rather than only within one live session.

### Layer 7: evidence and diagnostics

Owner: Universal E2E platform.

Every physical scenario must retain enough evidence to diagnose the first failed invariant.

For navigation-aware scenarios this should eventually include:

- exact map/index/provenance identifiers used for planning;
- requested origin/destination or landmark identifiers;
- executable route plan;
- actual observed position trace or bounded checkpoints;
- route interactions attempted;
- first divergence marker;
- client/server logs;
- screenshots when useful;
- SQL/protocol assertions;
- machine-readable final result;
- cleanup result.

The result must distinguish:

- static preflight failure;
- route execution failure;
- feature action failure;
- assertion failure;
- persistence/relog failure;
- infrastructure failure.

### Layer 8: advanced orchestration

Owner: future bounded Universal E2E platform tasks.

This layer includes capabilities that should be added only when demanded by concrete feature scenarios:

- multiple simultaneous controlled OTClients;
- deterministic player-to-player interaction;
- runtime fault injection;
- controlled Canary restart/crash/recovery flows;
- database interruption/recovery seams where safely supported;
- cross-process or multichannel scenarios.

Do not add these capabilities speculatively in feature PRs.

## Evidence maturity model

Every scenario or claim should state the strongest evidence level it actually proves.

### M0 — static evidence only

Examples:

- item/teleport exists at exact OTBM position;
- static route is confirmed by Reachability;
- script handler is resolved.

This is not physical gameplay proof.

### M1 — physical action proof

A real controlled OTClient performs the bounded action and the expected immediate runtime effect is observed.

Examples:

- movement;
- door/use interaction;
- floor change;
- teleport;
- NPC dialogue step;
- attack action.

### M2 — feature outcome proof

The real client completes the feature action and feature-specific server/client/SQL assertions pass.

Examples:

- quest storage changes;
- reward item received;
- forge operation result;
- market operation recorded.

### M3 — persistence proof

M2 plus canonical safe logout, persisted state verification, relog and re-verification.

Use for any feature whose correctness is expected to survive session boundaries.

### M4 — cross-actor or cross-system proof

The scenario spans multiple clients, processes or major gameplay systems and verifies their combined result.

Examples:

- trade between two real clients;
- party/PvP interaction;
- NPC travel followed by quest completion;
- cross-channel persistent handoff.

### M5 — recovery/resilience proof

The scenario introduces a controlled failure and proves the expected safe recovery, rollback, idempotency or cleanup result.

A lower level must never be reported as a higher level without the additional runtime evidence.

## Ordered implementation programme

Each package below must be implemented through its own active task, branch and PR. Agents must verify current `main`, live dependencies and path ownership before starting.

### E2E-GAMEPLAY-001 — programme reconciliation and durable architecture

Status: this documentation task.

Deliverables:

- reconcile `E2E_AUTOMATION_PROGRAM.md` with merged work;
- publish this architecture;
- publish the architecture ADR;
- define the ordered queue and responsibility boundaries.

Acceptance gate:

- no runtime/workflow implementation paths changed;
- no overlap with PR #562 exclusive paths;
- repository ownership and docs CI green.

### E2E-GAMEPLAY-002 — OTBM-aware route consumption

Dependencies:

- the required route-plan/export portions of `CAN-PROGRAM-OTBM-E2E-ROUTING` must be merged or otherwise explicitly stable.

Goal:

- allow Universal Physical E2E to execute an evidence-backed route plan instead of a hand-authored directional sequence.

Expected deliverables:

- generic route-plan loader/validator in the existing E2E platform;
- exact-position synchronization between route steps or segments and the physical client;
- fail-closed divergence evidence;
- route-plan artifact retention;
- focused tests using synthetic route plans;
- no independent pathfinding in E2E.

Reference acceptance scenario:

- first landmark-to-landmark route defined by the OTBM routing programme, expected initially to target `thais.temple -> thais.depot` once exact anchors are evidence-backed.

Acceptance gate:

- static preflight identifies the exact route/map/index provenance;
- a real controlled OTClient reaches the accepted destination;
- no blind unbounded movement loop;
- divergence fails with exact last observed/expected position evidence;
- login/logout/relog sentinel remains intact when required.

### E2E-GAMEPLAY-003 — quest and NPC vertical slices

Dependencies:

- E2E-GAMEPLAY-002 for scenarios that require nontrivial map navigation;
- existing quest/NPC static validators where applicable.

Goal:

- prove complete small quest/NPC flows using real client actions rather than only static source evidence.

Start with one deterministic vertical slice, not a broad quest sweep.

Candidate shape:

```text
login
navigate to NPC
perform bounded dialogue
navigate/interact with quest mechanic
assert storage/reward
safe logout
relog
assert persisted storage/reward
```

Acceptance gate:

- exact fixture and expected values are evidence-backed;
- all navigation uses the route integration when nontrivial;
- M3 persistence proof for persistent quest state;
- no guessed NPC names, coordinates, storages or item IDs.

### E2E-GAMEPLAY-004 — combat vertical slice

Dependencies:

- existing physical visible-target attack capability;
- deterministic creature fixture or controlled scenario environment.

Goal:

- prove one bounded combat lifecycle with a real client.

Candidate coverage:

- target acquisition;
- attack start;
- observable damage/combat result;
- kill or deterministic termination where safe;
- reward/loot/state assertion where applicable.

Acceptance gate:

- deterministic target fixture;
- bounded timeout and cleanup;
- no reliance on random world occupancy;
- retain server/client evidence for the first failed combat invariant.

### E2E-GAMEPLAY-005 — persistence assertion matrix

Dependencies:

- existing canonical two-session login/logout/relog lifecycle.

Goal:

- define and implement reusable assertion surfaces for persisted gameplay state.

Priority domains:

1. storages/quest progression;
2. inventory and depot/inbox state;
3. bank/economy values;
4. vocation/progression values;
5. feature-specific durable rows.

Acceptance gate:

- each assertion type has a focused test;
- scenarios explicitly declare whether persistence is required;
- persistence is checked after safe logout and before/after relog as appropriate;
- transient runtime-only state is not mistaken for durable state.

### E2E-GAMEPLAY-006 — multi-client orchestration

Dependencies:

- stable single-client platform and evidence format;
- a concrete feature that requires more than one client.

Goal:

- extend the canonical platform to run multiple controlled OTClients in one disposable environment without creating a second orchestrator.

First scenario should be selected from a deterministic need such as:

- trade;
- party interaction;
- PvP interaction;
- player-to-player mail or other direct interaction.

Acceptance gate:

- clients have distinct deterministic identities and logs;
- scenario result identifies which client performed each action;
- cleanup leaves no connected test players;
- timeouts cannot leave orphan clients;
- evidence remains machine-readable.

### E2E-GAMEPLAY-007 — runtime fault and recovery validation

Dependencies:

- stable relevant baseline scenario;
- explicit safe fault-injection seam.

Goal:

- prove recovery and cleanup behavior under controlled failures.

Candidate faults:

- client disconnect;
- server restart during a defined safe phase;
- bounded connection timeout;
- controlled database availability interruption only when a safe isolated seam exists.

Acceptance gate:

- fault is explicit and reproducible;
- expected recovery/rollback behavior is defined before execution;
- production/external systems are never targeted;
- cleanup is attempted even on failure;
- results distinguish expected injected failure from platform defects.

### E2E-GAMEPLAY-008 — cross-system gameplay journeys

Dependencies:

- required lower-level feature suites and shared capabilities are already individually proven.

Goal:

- compose previously proven capabilities into representative end-to-end player journeys.

Example shape:

```text
login at temple
navigate to depot
prepare inventory
navigate to NPC
travel or enter quest route
complete quest interaction
fight deterministic encounter
receive reward
return or logout
relog
assert persisted result
```

These journeys are integration sentinels. They must reuse existing feature suites/capabilities rather than reimplement them.

Acceptance gate:

- every major step maps to an already owned feature/platform capability;
- failure reports the first system boundary that failed;
- journey-level success never replaces focused feature tests.

## Dependency graph

```text
E2E-GAMEPLAY-001  architecture/programme reconciliation
        |
        +-----------------------------+
        |                             |
        v                             v
OTBM-E2E routing programme       E2E-GAMEPLAY-005 persistence matrix
        |
        v
E2E-GAMEPLAY-002 route consumption
        |
        +---------------------+
        |                     |
        v                     v
E2E-GAMEPLAY-003 quests/NPC   E2E-GAMEPLAY-004 combat
        |                     |
        +----------+----------+
                   |
                   v
          E2E-GAMEPLAY-008 journeys

E2E-GAMEPLAY-006 multi-client  <- start only from concrete feature demand
E2E-GAMEPLAY-007 fault/recovery <- start only after a stable baseline exists
```

`E2E-GAMEPLAY-005` may proceed in parallel with route work because it primarily extends assertion contracts around the already-proven two-session lifecycle.

## Scenario development rules

### Rule 1: one concrete vertical slice first

Do not start by attempting to cover an entire system. Add one deterministic scenario that proves the shared capability and feature contract, then expand through separate tasks.

### Rule 2: no blind movement for nontrivial navigation

Once the OTBM route integration is available, nontrivial navigation scenarios must consume evidence-backed route planning. Hand-authored directional sequences remain acceptable only for tiny bounded platform probes whose exact purpose is to test movement itself.

### Rule 3: static truth and runtime truth stay separate

A green OTBM/static report is preflight evidence, not E2E success. A physical E2E result does not authorize changing static map evidence or marking unresolved scripts as handled.

### Rule 4: feature values belong to feature suites

The shared platform must not encode quest storages, reward values, NPC names, monster IDs or map landmarks as generic defaults.

### Rule 5: generic capability changes are separate platform tasks

If a feature requires a new generic action or assertion interface:

1. record the missing capability in the feature task;
2. create a bounded Universal E2E platform task;
3. implement focused generic tests;
4. merge the platform capability;
5. consume it from the feature scenario.

### Rule 6: exact evidence before broad reuse

A new capability is not considered stable merely because unit tests pass. Physical behavior claims require a real workflow result on the exact relevant commit.

### Rule 7: do not create parallel infrastructure

Forbidden unless an explicit architecture decision supersedes this document:

- second E2E orchestrator;
- per-feature complete workflow copies;
- second OTBM parser or World Index;
- independent E2E pathfinder;
- feature-specific client fork used as shared infrastructure;
- committed downloaded OTBM/client assets;
- AI-generated map imagery as evidence.

## Agent startup instructions for future work

Before starting any package from this programme:

1. read root `AGENTS.md`;
2. read `docs/agents/REPOSITORY_MAP.md` and `docs/agents/CONTEXT_ROUTING.md`;
3. read `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`;
4. read this architecture;
5. read the active task/live PR for the selected package;
6. for navigation work, read the merged/current `OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md` and its technical contract;
7. inspect open PRs and active tasks for owned-path overlap;
8. create one bounded active task and draft PR before substantial implementation.

Do not choose a later package while an explicit dependency remains unmerged unless the task can proceed independently and records that boundary.

## Programme completion definition

The Universal E2E gameplay programme is not considered broadly mature merely because one scenario exists for every category.

A production-quality validation layer should eventually provide:

- stable login/relog baseline;
- OTBM-aware navigation for nontrivial routes;
- representative M3 quest/NPC and persistence scenarios;
- representative deterministic combat scenario;
- reusable persistence assertions;
- at least one justified multi-client scenario;
- at least one justified resilience scenario;
- one cross-system player journey composed from already-proven capabilities;
- deterministic artifacts that identify the first failed layer;
- all work executed through the single Universal E2E platform.

The queue is intentionally incremental. Each package should land independently with exact evidence and leave the repository in a usable state for the next agent.
