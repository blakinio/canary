# OAM-017 — Containers Revalidation

Status: **target proof in progress**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-017`

## Immutable task-start baselines

```text
legacy/governance Canary: blakinio/canary@6c2ed7fd5d7e0f51bf7bfc75ebcc30b840315e41
target Otheryn: blakinio/Otheryn@46cc7458d644da356371aabf3ff18c0e51d228a8
upstream evidence: opentibiabr/canary@691614c1a302aee776002ca3851eca399be1a82c
maintained OTClient: blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

## Canonical module and provisional disposition

```text
containers → REUSE (pending exact-target proof)
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

## Target proof

Otheryn issue:

```text
#40 — OAM-017: prove reusable containers core
```

Otheryn PR:

```text
#41 — test(containers): prove OAM-017 reused containers core
```

The target proof changes one already registered test path only:

```text
tests/unit/items/containers/container_test.cpp
```

Focused `ContainerReuseTest` coverage:
1. direct capacity/free-slot behavior;
2. direct add/find/remove lifecycle;
3. parent-backed holding discovery;
4. nested depth-first traversal;
5. maximum traversal-depth signaling.

No production container/cylinder mutation is authorized.

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

## Completion gate

`containers → REUSE` becomes final only after:
1. exact target CI/Required/autofix and full CTest pass;
2. focused `ContainerReuseTest` passes;
3. target comments/reviews/threads are clean and target-main drift is checked;
4. target proof merges with expected-head protection;
5. final Canary governance exact-head gates and audit pass;
6. separate authoritative lifecycle archive and durable program reconciliation merge;
7. any self-owned automatic `docs(agents): archive merged PR` duplicate is explicitly closed after authoritative lifecycle is established.

OAM-018 remains NOT STARTED until the complete OAM-017 sequence finishes.
