# OAM-018 — Item Decay Revalidation

Status: **fresh preflight complete; target proof not started**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-018`

## Immutable task-start baselines

```text
legacy/governance Canary: blakinio/canary@3c4d2789ffa3d0c1e9453d20a8c5faeba35eb366
target Otheryn: blakinio/Otheryn@952e7550182df739824bddea687ef89bd8997674
upstream evidence: opentibiabr/canary@691614c1a302aee776002ca3851eca399be1a82c
maintained OTClient: blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

## Canonical module and provisional disposition

```text
item-decay → REUSE (candidate; target proof required)
```

Canonical registry record: `docs/agents/real-tibia/registry/modules/item-decay.yaml`.

Registry boundary:
- server: `src/items/decay/**`;
- dependencies: `engine-scheduler`, `item-instances`;
- interactions: `containers`, `item-definitions`, `world-persistence`.

The package owns scheduler-backed item duration start/stop/check and decay-transform/removal lifecycle. Static decay metadata, generic scheduler ownership, item movement/container transactions, restart recovery and proof of timing correctness remain outside this package.

## Dependency gate

- OAM-003 completed `engine-scheduler → REUSE`, retaining the pinned upstream lane/WDRR/barrier-parallel scheduler and rejecting the older legacy/Crystal scheduler model.
- OAM-007 completed the target item foundation containing canonical `item-instances` ownership.
- OAM-017 completed `containers → REUSE`; `containers` is an interaction, not a fundamental `item-decay` dependency.

Therefore the registry dependency gate for OAM-018 is satisfied.

## Fresh live-state and ownership preflight

At task start:
- Canary `main` is `3c4d2789ffa3d0c1e9453d20a8c5faeba35eb366`;
- Otheryn `main` is `952e7550182df739824bddea687ef89bd8997674`;
- Otheryn has no open pull requests;
- live Canary PRs #573, #572, #559, #526 and #514 do not change `src/items/decay/**`;
- no OAM branch matching `oam` is live in Canary or Otheryn before this task branch was created.

No overlapping live ownership was found for the canonical `item-decay` runtime boundary.

## Whole-boundary provenance

Target history from verified OAM bootstrap `3cc7c1dfea747bb380f3761ee7ff7ac30141a115` through task-start Otheryn `952e7550182df739824bddea687ef89bd8997674` contains no change under `src/items/decay/**`.

Pinned-upstream history from `a879c9312e34381e8eedf397b8ed44510698b689` through task-start upstream `691614c1a302aee776002ca3851eca399be1a82c` changes only Windows CI, network-message and server-definition paths and contains no change under `src/items/decay/**`.

Representative exact task-start blobs:

```text
Otheryn/upstream src/items/decay/decay.cpp
a337b872755217d87ac2261de6c3c1a593d805a6

Canary src/items/decay/decay.cpp
458cda4ac92f21289ca1072447e79c71de645ae8

Otheryn/upstream/Canary src/items/decay/decay.hpp
0d540e10dc73b65f2ce1aa00bfb9dd72994dcc5f
```

The `decay.cpp` legacy difference is narrow: the three decay scheduling calls omit `DispatcherLane::Maintenance`, while the target/upstream implementation schedules those callbacks explicitly on the maintenance lane. OAM-003 already established that the target/upstream lane/WDRR scheduler is the stronger canonical scheduler foundation and that the legacy scheduler model is older and must not replace it.

Therefore the legacy `decay.cpp` delta is currently rejected as a donor candidate: it is compatibility with a weaker scheduler boundary, not evidence of stronger canonical decay behavior.

## Proof requirement

The provisional `REUSE` decision is not final until an exact-head target proof passes. The target proof must:
- remain proof-only unless concrete evidence proves a production `item-decay` defect;
- avoid importing the legacy scheduler-call regression;
- add bounded focused tests for the existing target decay lifecycle;
- run the full applicable exact-head target gate and focused decay tests;
- preserve OAM-003 scheduler ownership and OAM-007 item-instance ownership;
- record exact changed files, final head, CI/Required/autofix results, focused/full test counts and review state.

## Explicit exclusions

OAM-018 does not claim:
- scheduler fairness, ordering or starvation freedom;
- exact wall-clock decay timing;
- restart/crash decay recovery;
- persistence completeness;
- item move/container transaction atomicity;
- duplication or loss freedom;
- static decay metadata parity;
- exhaustive transform correctness;
- protocol/client UI parity;
- full Real Tibia decay semantics.

## Current blocker

Repository policy permits writes only to `blakinio/canary` unless the user explicitly authorizes mutation of another named repository. This fresh preflight uses Otheryn read-only. A proof-only Otheryn branch/issue/PR must not be created until explicit authorization to mutate `blakinio/Otheryn` for OAM-018 is available.

OAM-019 is not started.
