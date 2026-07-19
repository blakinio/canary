# OAM-017 — Containers Revalidation

Status: **target proof merged; governance closeout in progress**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-017`

## Immutable task-start baselines

```text
legacy/governance Canary: blakinio/canary@6c2ed7fd5d7e0f51bf7bfc75ebcc30b840315e41
target Otheryn: blakinio/Otheryn@46cc7458d644da356371aabf3ff18c0e51d228a8
upstream evidence: opentibiabr/canary@691614c1a302aee776002ca3851eca399be1a82c
maintained OTClient: blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

## Canonical module and final disposition

```text
containers → REUSE
```

Canonical registry record: `docs/agents/real-tibia/registry/modules/containers.yaml`.

Registry boundary:
- server: `src/items/containers/**`, `src/items/cylinder.*`
- hard dependency: `item-instances`
- dependency status: completed by OAM-007
- interactions: boss encounters, item decay, market, player persistence and world persistence

The package owns nested container/cylinder add-remove-query lifecycle, capacity, nested traversal/depth handling, depot/inbox/mailbox/reward container discovery, batch/pagination/managed-container surfaces and container serialization-boundary discovery. Generic Game move orchestration, item definitions, boss reward scoring, market pricing and proof of transactional move safety remain outside this package.

## Fresh preflight

At task start:
- Otheryn had no open PR;
- Canary #514 owned authenticated-session security validation;
- Canary #525 owned physical teleport E2E;
- Canary #526 owned shared-state/economy security-audit documentation;
- none touched `src/items/containers/**` or `src/items/cylinder.*`.

## Whole-boundary provenance

OAM-002 established the target from exact pinned upstream Canary content. Target history from verified bootstrap `3cc7c1dfea747bb380f3761ee7ff7ac30141a115` through task-start `46cc7458d644da356371aabf3ff18c0e51d228a8` contains no canonical container production path change. Upstream history from bootstrap source `a879c9312e34381e8eedf397b8ed44510698b689` through task-start pin `691614c1a302aee776002ca3851eca399be1a82c` changes only Windows workflow, network-message and server-definition paths.

Representative exact task-start blobs:

```text
src/items/containers/container.cpp
2688a2d59bebac33b801cfdd11d0aa5c26a07016

src/items/cylinder.cpp
82c6cf3fd6dff9d579d35cfbaf1f4b52ec4c46b8
```

Both are identical across target, pinned upstream and task-start legacy. Identity alone is not accepted; whole-history provenance and delivered legacy history were reviewed.

## Reviewed legacy history

Legacy-vs-upstream comparison through task start contains no changed file under `src/items/containers/**` or `src/items/cylinder.*`.

Two delivered PRs surfaced by container-related discovery but are outside the canonical runtime boundary:
- PR #60 fixes house transfer orchestration and changes only `src/map/house/house.cpp`;
- PR #108 hardens Gameplay Analytics spell/supply/loot scripts and changes no canonical container/cylinder source path.

Neither is a container-runtime donor. OAM-017 does not import house-transfer orchestration or Analytics instrumentation.

## Initial proof-harness failure and resolution

The first target proof head `7dcdcff1dde59a702b00d77f5049bd99a126a6eb` failed only the two new focused tests in Linux debug CI #125 / run `29653898425`:

```text
357 total
355 passed
2 failed

ContainerReuseTest.PreservesDirectCapacityAndItemLifecycle — SEGFAULT
ContainerReuseTest.PreservesBoundedNestedTraversal — SEGFAULT
```

The failure was isolated to the proof harness. Unit test startup does not load item definitions; `Items::Items()` leaves the item-type vector empty, while an out-of-range `Items::getItemType()` falls back to `items.front()`. The new tests constructed synthetic id/type `0` objects before seeding any item type, so object construction entered undefined behavior before the container behavior under test.

The correction is tests-only: `ScopedItemTypeRegistry` provides the minimum synthetic item-type registry state when the unit process starts empty and restores the original registry size after each focused test. No file under `src/items/containers/**`, `src/items/cylinder.*` or any other production runtime/data path changed.

## Accepted exact target proof

```text
Otheryn issue #40: CLOSED / completed
Otheryn PR #41: MERGED
final target head: ee111cb6ef6299a0de7fb19de76934b6369b7cf0
target squash merge: 952e7550182df739824bddea687ef89bd8997674
autofix.ci #108 / 29679028025: SUCCESS
CI #127 / 29679028059: SUCCESS
Required #115 / 29679028000: SUCCESS
full CTest: 357/357 PASS
focused ContainerReuseTest: 2/2 PASS
artifact: 8440064893
name: linux-debug-test-logs
digest: sha256:28d82a5a1d36d89a8892280e73bb671a846743962786922093a907e8b80b79c1
```

Both focused tests passed individually in the full CTest execution. The final target diff contains exactly `tests/unit/items/containers/container_test.cpp`. Target comments, reviews and review threads were all empty. Otheryn `main` remained at task-start head `46cc7458d644da356371aabf3ff18c0e51d228a8` before merge, so target-main drift was none. PR #41 merged with expected-head protection on `ee111cb6ef6299a0de7fb19de76934b6369b7cf0`.

## Explicit exclusions

OAM-017 does not claim:
- transactional move atomicity;
- absence of duplication or item loss across generic move orchestration;
- exhaustive cycle safety;
- full serialization or persistence completeness;
- restart/crash recovery;
- depot/inbox/mailbox/reward parity;
- protocol/client UI parity;
- market, boss-reward or item-decay parity;
- Real Tibia container formula/value semantics beyond the bounded proof.

OAM-004 SQL/KV non-atomicity and completed OAM-007 item-instance ownership remain authoritative.

## Remaining closeout

The target proof is complete and `containers → REUSE` is final. OAM-017 is not durably complete until:
1. Canary governance PR #555 passes fresh final exact-head Agent Task Ownership and CI plus clean review/main-drift audit, then merges with expected-head protection;
2. a separate authoritative lifecycle-only archive merges;
3. any self-owned automatic `docs(agents): archive merged PR #555 task` duplicate is explicitly closed after the authoritative lifecycle archive is established;
4. a separate one-file durable program reconciliation merges.

OAM-018 remains NOT STARTED until the complete OAM-017 sequence finishes.
