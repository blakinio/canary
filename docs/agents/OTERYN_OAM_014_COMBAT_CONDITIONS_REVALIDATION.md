# OAM-014 — Combat Conditions Revalidation

Status: **REVALIDATE — target adaptation candidate identified**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-014`

## Immutable task-start baselines

```text
legacy/governance Canary: blakinio/canary@0253b712cd4275e8ad72d5bca7020d1f4a2246b7
target Otheryn: blakinio/Otheryn@3628effc5f22e7edbdc66dc5f514e4df5c9f0cda
upstream evidence: opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f
maintained OTClient: blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

All four live heads were refreshed at task start.

## Canonical module

```text
combat-conditions
```

Registry boundary:

- server: `src/creatures/combat/condition.*`
- hard dependency: `combat`
- dependency status: completed by OAM-013
- scope: condition creation, timed lifecycle, stacking/execution, serialization and persistent-condition discovery

Explicit exclusions:

- generic combat formulas/targeting;
- spell definitions and cooldown ownership;
- vocation-specific modules;
- protocol/client/map/assets;
- broad persistence redesign or SQL/KV atomicity claims.

## Fresh live-state/open-PR preflight

At task start:

- no open Otheryn PR exists;
- open Canary PRs were audited for overlap with `src/creatures/combat/condition.*`;
- PR #514 touches security validation infrastructure only;
- PR #525 touches physical teleport E2E only;
- PR #526 touches security audit documentation only;
- automated lifecycle PRs do not own the OAM-014 condition runtime boundary.

No overlapping open PR was identified for the canonical OAM-014 runtime path.

## Initial semantic evidence

Task-start target and pinned upstream share the exact `condition.cpp` blob:

```text
5b15ed00c7e92eef6d8c719aec423443efae8b7a
```

Reviewed Canary PR #297 (`fix(combat): guard zero-level light conditions`) final head:

```text
b7f5de1f04cd3b521ee9621a0f001f0ced5e6c39
```

Its accepted runtime blob for `src/creatures/combat/condition.cpp` is:

```text
26a1cf0c9e01f4ab162438e8284f5cc73d129d11
```

Current task-start legacy Canary has the same corrected runtime blob.

PR #297 closes two independently reachable zero-level `ConditionLight` boundaries:

1. normalize level `0` in `ConditionLight::startCondition` before fade-interval division;
2. normalize deserialized persisted level `0` in `ConditionLight::unserializeProp`.

The reviewed PR also provides three focused regression cases covering deserialize normalization, direct zero-level start safety, and preservation of valid nonzero behavior.

## Working disposition

```text
combat-conditions → ADAPT
```

This remains subject to exact donor provenance verification, smallest coherent target materialization, exact-head target CI/runtime/CTest proof, governance gates, lifecycle archive and durable program reconciliation.

## Safety boundary

OAM-014 will not bulk-copy condition subsystems or infer whole-module parity from file identity. The candidate adaptation is limited to the reviewed zero-level `ConditionLight` correctness boundary and its focused tests unless further dependency-valid evidence is proven before target write.

OAM-015 remains **NOT STARTED**.
