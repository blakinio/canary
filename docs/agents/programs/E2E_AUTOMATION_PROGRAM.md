---
program_id: CAN-PROGRAM-E2E-PLATFORM
name: Universal OTS E2E automation
status: active
owner: e2e-platform-agent
created: 2026-07-13T00:00:00+02:00
updated: 2026-07-23T00:00:00+02:00
last_verified_commit: 115f3ac2fffc36bb4e415c2a6fb45908d9538ba3
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

The programme is no longer in platform bootstrap. The reusable physical platform has proven login/relog, movement, floor change, teleport, OTBM-aware route execution, typed persistence, bounded two-client orchestration, controlled client-disconnect recovery and one representative cross-system gameplay journey.

The next phase focuses on broader gameplay coverage, resilience, deterministic reproduction, diagnostics/test intelligence, operational stability and release confidence while preserving one canonical physical lifecycle.

Durable architecture:

- `docs/architecture/universal-e2e-gameplay-validation.md` — foundational gameplay-validation layers and M0-M5 evidence maturity;
- `docs/architecture/universal-e2e-quality-resilience-roadmap.md` — post-008 quality, resilience, test-intelligence and release roadmap.

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
- generic multi-client, recovery, replay, diagnostics, stability or selection capabilities only when implemented through separate bounded platform tasks.

The platform must remain feature-neutral. It must not encode feature-specific quest storages, rewards, NPCs, monsters, map landmarks or expected gameplay values.

## OTBM/static programmes own

- canonical static map evidence through the Unified OTBM World Index;
- walkability and route graph evidence through Reachability;
- AID/UID/item/position runtime-handler correlation through Script Resolution;
- reviewed floor-transition and other static mechanic evidence;
- static route/landmark/interaction planning through `CAN-PROGRAM-OTBM-E2E-ROUTING`;
- OTBM Semantic Diff and other static impact evidence used by scenario selection where applicable.

Static evidence is preflight/selection evidence, not physical gameplay success.

## Feature programmes own

- feature-specific scenario definitions;
- deterministic fixtures;
- feature actions and expected values;
- feature SQL/server/client/UI assertions;
- persistence expectations;
- feature invariants and exactly-once expectations;
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
| OTBM-aware route execution | merged and runtime-proven | route-plan/follow_route/preflight/reference-route packages including PRs #573, #589, #594 and #600 | consume canonical route evidence; never add an E2E pathfinder |
| Typed persistence assertion surfaces | implementation merged; closure matrix delivered | PRs #565, #583, #586, #591, #595, #603, #608, #615 and closure PR #666 | use `docs/e2e/PERSISTENCE_ASSERTION_MATRIX.md`; add a generic type only for a concrete reusable gap |
| Bounded two-client orchestration | merged and runtime-proven | PR #747; lifecycle archive #753 | reuse `canary-universal-e2e-two-client-orchestration-v1` for exactly one secondary controlled OTClient |
| Controlled client-disconnect recovery | merged and runtime-proven | PR #751; lifecycle archive #764 | reuse `canary-universal-e2e-client-disconnect-recovery-v1`; it is not arbitrary fault injection |
| Representative cross-system gameplay journey | merged and runtime-proven M4 sentinel | PR #765; lifecycle archive #791 | `journeys/promotion-combat-persistence` is an integration sentinel; focused lower-level scenarios remain authoritative |
| Cyclopedia-specific prototype | closed and superseded | PR #224 | historical evidence only; do not revive or copy its infrastructure |

# Current integration boundary

## OTBM-aware physical routing

Merged planning PR #562 introduced `CAN-PROGRAM-OTBM-E2E-ROUTING` as the detailed bridge between static OTBM evidence and physical E2E. Follow-up packages delivered executable route plans, semantic landmarks/interactions, exact movement edges, `follow_route`, exact-map preflight and a reference Thais temple-to-depot physical route.

This E2E programme consumes that bridge and must not duplicate its parser, World Index, pathfinder or route-planning contracts. Future route work must verify the live routing-programme state rather than relying on this summary alone.

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
- feature/domain invariants where relevant;
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

## Orthogonal quality dimensions

Post-008 work reports these separately from M0-M5:

- determinism;
- stability;
- resilience;
- exactly-once;
- concurrency;
- cleanup;
- performance;
- compatibility;
- diagnostics.

Recommended states are `not-evaluated`, `pass`, `fail`, `unstable` and `blocked`. A quality dimension must not be inferred from an unrelated maturity proof.

# Execution tiers

The detailed policy is in `docs/architecture/universal-e2e-quality-resilience-roadmap.md`.

- **PR-required:** deterministic impacted scenarios and focused regression gates.
- **Scheduled/nightly:** repeated stability, soak, fuzzing, wider matrices and selected concurrency workloads.
- **Release certification:** reviewed gold scenarios, migration validation, supported compatibility/datapack cells and resilience sentinels.
- **On-demand investigation:** deterministic replay, failure minimization, expanded differential runs, crash analysis and controlled infrastructure faults.

Retries may collect stability evidence but must never erase or hide the original failing attempt.

# Interface-change rule

When a feature needs a new generic capability:

1. the feature task records the missing capability and proposed interface;
2. a separate Universal E2E platform task claims and implements the generic capability;
3. the platform PR adds focused tests and preserves existing registered scenarios;
4. the feature PR consumes the stable interface without copying orchestration;
5. `depends_on` and `blocks` record merge order;
6. Canary/OTClient changes use a shared coordination ID and the cross-repository contract rules.

The same rule applies to route following, map-item interaction, persistence assertions, multi-client orchestration, fault injection, replay, result envelopes, cleanup certification and test selection.

# Delivered gameplay roadmap foundation

`E2E-GAMEPLAY-001` through `E2E-GAMEPLAY-008` are the delivered foundation, not the active future queue.

- `E2E-GAMEPLAY-001` established programme reconciliation and durable layered architecture through PR #563.
- `E2E-GAMEPLAY-002` route consumption is represented by the merged OTBM-to-E2E route/follow_route/preflight/reference-route chain; detailed ownership stays with the route programme.
- `E2E-GAMEPLAY-003` and `004` established focused NPC/quest and deterministic combat vertical-slice patterns.
- `E2E-GAMEPLAY-005` delivered the typed persistence matrix and closure inventory through PR #666.
- `E2E-GAMEPLAY-006` delivered bounded two-client orchestration through PR #747 and lifecycle archive #753.
- `E2E-GAMEPLAY-007` delivered fixed-purpose client-disconnect recovery through PR #751 and lifecycle archive #764.
- `E2E-GAMEPLAY-008` delivered the first representative M4 integration sentinel through PR #765 and lifecycle archive #791.

Do not reopen these package IDs merely to add new work. New work uses a fresh bounded task under the successor roadmap.

# Post-008 successor roadmap

The authoritative detailed queue is `docs/architecture/universal-e2e-quality-resilience-roadmap.md` with packages `E2E-QRI-001` through `E2E-QRI-028`.

The roadmap is organized into four workstreams:

1. **Gameplay coverage** — real two-player trade/persistence, broader representative Journey 002 and deterministic OTClient UI assertions.
2. **Reliability/resilience** — Canary restart recovery, fixture snapshot/restore, exactly-once, concurrency, controlled DB interruption, save/restart consistency, controlled test time and cleanup certification.
3. **Test intelligence/diagnostics** — standard result envelope, factual coverage dashboard, differential runtime comparison, deterministic replay, failure minimization, invariants, seeded reproducible fuzzing, state-machine misuse, dependency-driven selection, crash bundles and stability certification.
4. **Operational/release confidence** — soak, performance regression, Canary/OTClient compatibility, datapack compatibility, migration E2E and a reviewed release gold suite.

## Recommended first implementation wave

Select one package at a time after live dependency and ownership preflight. Current recommendation:

1. `E2E-QRI-005` — standard machine-readable result envelope and richer first-failure evidence;
2. `E2E-QRI-006` — resource cleanup certification;
3. `E2E-QRI-001` — real two-player trade and persistence;
4. `E2E-QRI-002` — Canary restart/reconnect recovery;
5. `E2E-QRI-003` — broader representative Journey 002;
6. `E2E-QRI-004` — factual M0-M5 plus quality-dimension coverage dashboard;
7. `E2E-QRI-022` — flake/stability certification after the selected scenarios are stable enough to measure.

Later waves cover transactional/resilience correctness (`QRI-008` through `014`), test intelligence (`QRI-015` through `021`) and operational/release confidence (`QRI-023` through `028`).

This ordering is guidance, not permission to start all packages concurrently. Concrete feature demand and current ownership remain authoritative.

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

Future tier-aware execution may add repository-approved equivalents for impacted, nightly or release selections, but the exact executable remains an implementation detail of the existing platform. Agents must extend verified repository conventions rather than inventing another runner.

# Safety invariants

- no production credentials, database, host or irreversible external action;
- no committed Tibia assets, downloaded OTBM files, database dumps or secrets;
- every run uses an isolated disposable environment and always attempts cleanup;
- external binaries and assets are pinned or hash-recorded;
- failures retain enough evidence to identify the exact first failed layer;
- retries never erase original instability/failure evidence;
- feature PRs never silently modify shared platform lifecycle behavior;
- platform PRs treat registered feature suites as compatibility inputs;
- no E2E success claim without a verified real workflow result on the exact relevant commit;
- no static OTBM success claim may be presented as physical gameplay proof;
- no independent E2E pathfinder after the OTBM route integration boundary exists;
- no blind nontrivial navigation once evidence-backed route consumption is available;
- restart/DB/time/fuzz/stress seams must be fixed-purpose, isolated and bounded;
- no arbitrary host, shell, SQL, packet-payload or external-target surface is authorized by the post-008 roadmap;
- soak/fuzz/matrix workloads must not become unconditional every-PR gates without separate evidence-backed policy.

# Handoff

## Start here

Future agents should read, in order:

1. root `AGENTS.md`;
2. `docs/agents/REPOSITORY_MAP.md`;
3. `docs/agents/CONTEXT_ROUTING.md`;
4. this programme record;
5. `docs/architecture/universal-e2e-gameplay-validation.md`;
6. `docs/architecture/universal-e2e-quality-resilience-roadmap.md`;
7. the selected active task and live PR;
8. for route work, the current `OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md` and technical contract.

## Do not repeat

- do not reopen or copy superseded PR #224 infrastructure;
- do not create one complete workflow per feature;
- do not create a second physical E2E orchestrator;
- do not implement an independent OTBM parser, World Index or route pathfinder inside E2E;
- do not use `opentibiabr/otclient` as a writable target;
- do not commit client assets, map binaries, live DB snapshots/dumps or crash dumps;
- do not invent coordinates, item IDs, NPCs, monsters, storages or dynamic Lua behavior;
- do not weaken login/logout/relog or physical evidence requirements to make a scenario pass;
- do not hide flaky failures behind retry-until-green behavior;
- do not start destructive/fault work without an explicit isolated seam and declared expected recovery result.

## Next action selection

The E2E-GAMEPLAY-001..008 foundation is delivered and lifecycle-closed. Future implementation work should select exactly one bounded `E2E-QRI-*` package whose dependencies and concrete consumer demand are satisfied on current `main`.

Prefer the first implementation wave from the successor roadmap, beginning with result/diagnostic and cleanup foundations before expensive repetition or broad fault matrices. Verify live task/PR/ownership state before claiming any package and never infer completion from this programme record alone.
