# OAM-018 — Item Decay Revalidation

Status: **target proof complete; Canary governance validation pending**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-018`

## Immutable task-start baselines

```text
legacy/governance Canary: blakinio/canary@3c4d2789ffa3d0c1e9453d20a8c5faeba35eb366
target Otheryn: blakinio/Otheryn@952e7550182df739824bddea687ef89bd8997674
upstream evidence: opentibiabr/canary@691614c1a302aee776002ca3851eca399be1a82c
maintained OTClient: blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

## Canonical module and final disposition

```text
item-decay → REUSE
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
- Canary `main` was `3c4d2789ffa3d0c1e9453d20a8c5faeba35eb366`;
- Otheryn `main` was `952e7550182df739824bddea687ef89bd8997674`;
- Otheryn had no open pull requests;
- live Canary PRs #573, #572, #559, #526 and #514 did not change `src/items/decay/**`;
- no OAM branch matching `oam` was live in Canary or Otheryn before this task branch was created.

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

Therefore the legacy `decay.cpp` delta is rejected as a donor candidate: it is compatibility with a weaker scheduler boundary, not evidence of stronger canonical decay behavior.

## Exact target proof

Target PR: `blakinio/Otheryn#42` — `test(item-decay): prove OAM-018 reused decay core`.

```text
task-start target: 952e7550182df739824bddea687ef89bd8997674
final target proof head: 13e245f3c49477fa75c20171f0c845dec91d0824
target squash merge: 7ba76d2754a060a9a9eec0a23c686aefac725af2
autofix.ci #110 / 29682419114: SUCCESS
CI #130 / 29682419178: SUCCESS after one failed-job rerun
Required #117 / 29682419125: SUCCESS after rerun against green CI #130
full Linux debug CTest: 359/359 PASS
focused ItemDecayReuseTest: 2/2 PASS
linux-debug-test-logs artifact: 8441163603
digest: sha256:de3f541b41aa9d4f39a4d8d629de52a51e09b8eaff461c8706bb7a296cfd9631
comments: 0
reviews: 0
review threads: 0
```

The proof-only target diff contains exactly:
- `tests/unit/items/CMakeLists.txt`;
- `tests/unit/items/decay/decay_test.cpp`.

No production `src/items/decay/**`, scheduler, item runtime, persistence, protocol, data, map or client path changed.

The focused proof establishes:
- a decayable item starts decay through the real `Decay::startDecay` path;
- stopping preserves a positive remaining duration and clears active decay state;
- the same item can restart decay;
- a non-decayable item remains unscheduled;
- `DECAYING_STOPPING` is cleared fail-closed.

## CI transient classification

The first ready-cycle macOS job compiled successfully but reported failure in `Smoke test Canary datapack runtime`. Its uploaded runtime artifact showed the server reached `Canary CI Smoke server online!`, received SIGTERM and shut down cleanly with empty stderr. No focused decay test failed and no production code was changed.

A single failed-job rerun on the same exact head passed the macOS runtime smoke. This is classified as a transient smoke-harness/timing false negative, not a production `item-decay` defect. The rerun did not mutate the target head.

## Decision rationale

`item-decay → REUSE` is final because:
- the target/upstream decay implementation is provenance-stable across the bounded history examined;
- its scheduler calls preserve the stronger OAM-003 lane-based scheduler contract;
- the only reviewed legacy delta weakens that scheduling boundary and provides no stronger decay behavior;
- exact-head focused proof and the full target build/test matrix pass without modifying production decay runtime.

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

## Current state

Target proof is merged. Canary governance PR #578 remains the current bounded coordination surface and must pass exact-final-head ownership, CI and review gates before merge. After governance merge, OAM-018 still requires a separate authoritative lifecycle archive and one-file durable program reconciliation.

OAM-019 is not started.
