# OAM-013 — Combat Revalidation

Status: **target reuse proof merged; Canary governance closeout in review**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-013`

## Immutable task-start baselines

```text
legacy/governance Canary: blakinio/canary@e3563b447228830a4728790b52766dad56fe86f1
target Otheryn: blakinio/Otheryn@4a16ca17ebd098cf9763bb3c07755bfd31ac1c43
upstream evidence: opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f
maintained OTClient: blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

All four refs matched their live `main` branches at task start.

## Final disposition

```text
combat → REUSE
```

This conclusion is based on exact target/upstream core identity plus reviewed semantic history and exact-target proof. It is not inferred from file presence alone.

## Canonical boundary

OAM-013 owns the generic `combat` engine. `player-persistence` is its completed hard dependency.

Explicitly separate/downstream:

- `combat-conditions` owns condition lifecycle and the reviewed zero-level `ConditionLight` safety fix;
- `spells` depends on `combat` and owns individual spell definitions;
- Wheel-only allocation/augmentation remains separate;
- protocol, client, map, asset, quest and achievement boundaries are unchanged.

## Task-start overlap audit

No open OAM-013 PR existed in Canary or Otheryn. Open Canary PRs #526, #525 and #514 had no changed-path overlap with the selected generic combat boundary. Otheryn had no open PRs.

## Exact target/upstream core evidence

```text
src/creatures/combat/combat.cpp
Otheryn: 8c3a2c87ead3e55c0ae219a0f8b075a44c3dec0a
upstream: 8c3a2c87ead3e55c0ae219a0f8b075a44c3dec0a

src/creatures/combat/combat.hpp
Otheryn: 125390ed1a35cf804f5b31dbec61bcca346275c2
upstream: 125390ed1a35cf804f5b31dbec61bcca346275c2
legacy Canary: 125390ed1a35cf804f5b31dbec61bcca346275c2
```

## Reviewed legacy findings

### PR #297 — deferred to `combat-conditions`

PR #297 is a real bounded correctness fix for zero-level `ConditionLight` state, with three focused regressions. Final donor head: `b7f5de1f04cd3b521ee9621a0f001f0ced5e6c39`; production blob `26a1cf0c9e01f4ab162438e8284f5cc73d129d11`; test blob `ee2f185042cdb359aac1a752dce971ec76c38f8d`.

TSD-005 and the canonical registry place `condition.*` lifecycle behavior in downstream `combat-conditions`, so OAM-013 did not copy this fix.

### PR #92 — rejected as runtime donor

PR #92 describes chain-target hardening plus Wheel policy, but exact revalidation found that its final head `a3e62948a1c14e423ba29df17b76cdcdcea01a44` and current task-start legacy `combat.cpp` do not contain the described runtime wiring. Helper/test intent is not accepted as delivered donor provenance. The Wheel portion is cross-boundary.

No other reviewed, delivered, dependency-valid generic-combat runtime adaptation was identified for migration.

## Proof-only Otheryn delivery

```text
issue: #32 CLOSED / completed
PR: #33 test(combat): prove OAM-013 reused combat core
final head: 6d5dfe623fef1a6db9b8447d1978a2a6bb1272eb
target squash merge: 3628effc5f22e7edbdc66dc5f514e4df5c9f0cda
```

Final target diff was exactly test-only:

```text
tests/unit/game/CMakeLists.txt
tests/unit/game/combat_reuse_test.cpp
```

No combat implementation file changed.

## Exact-head target proof

```text
CI #114        run 29639923928  SUCCESS
Required #106  run 29639923874  SUCCESS
autofix.ci #99 run 29639923867  SUCCESS
Linux debug build: PASS
Canary runtime smoke: PASS
database schema import: PASS
actual CTest: 348/348 PASS
CombatReuseTest: 2/2 PASS
```

Focused cases:

```text
CombatReuseTest.MapsKnownConditionAndDamageTypesBidirectionally
CombatReuseTest.MapsUnsupportedTypesToNone
```

Primary evidence artifact:

```text
linux-debug-test-logs
artifact: 8428406618
digest: sha256:9165209e09bdef873563b6fef90516d80032e280244af702843cc55f22774635
```

The downloaded artifact independently confirmed `100% tests passed, 0 tests failed out of 348` and both focused cases passing.

## Target merge audit

Immediately before merge:

```text
comments: 0
reviews: 0
review threads: 0
Otheryn main drift from task-start baseline: none
PR scope: exactly 2 test-only paths
```

The merge used `expected_head_sha` protection.

## Boundary conclusion

- generic combat runtime/API: `REUSE`;
- build/toolchain: existing `canary_ut` reused;
- persistence: no change; OAM-004 SQL/KV non-atomicity preserved;
- scheduling/concurrency: no change;
- protocol/session/client: no change;
- world/map/assets: no change;
- runtime proof: build + Canary smoke PASS;
- tests: 2/2 focused and 348/348 full suite PASS;
- physical-client E2E: not required because no protocol/client boundary changed.

## Explicit exclusions

OAM-013 does not claim or migrate:

- condition lifecycle or the zero-level `ConditionLight` fix;
- individual spells;
- Wheel-only behavior;
- unrelated quest/achievement hooks;
- protocol/client/map/asset changes;
- persistence redesign or SQL/KV atomicity;
- exhaustive combat correctness;
- full Real Tibia combat formula/value parity.

## Final conclusion

```text
combat → REUSE
```

Target proof is merged at `blakinio/Otheryn@3628effc5f22e7edbdc66dc5f514e4df5c9f0cda`.

The Canary governance branch was clean-synchronized onto current non-overlapping `main@abbeb51433d33af7398a82f0cd2ab776d01e710f` after OTBM roadmap drift. Only this evidence report and the active OAM-013 task are preserved on the branch.

Remaining mandatory sequence:

1. merge Canary governance PR #533;
2. archive the active task in a lifecycle-only PR;
3. reconcile the durable migration program in a program-only PR;
4. keep OAM-014 `NOT STARTED` until durable reconciliation merges.
