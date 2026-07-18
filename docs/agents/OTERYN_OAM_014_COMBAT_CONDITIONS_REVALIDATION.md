# OAM-014 — Combat Conditions Revalidation

Status: **target adaptation merged; Canary governance closeout in review**

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

## Canonical module and final disposition

```text
combat-conditions → ADAPT
```

Registry boundary:

- server: `src/creatures/combat/condition.*`
- hard dependency: `combat`
- dependency status: completed by OAM-013
- scope: condition creation, timed lifecycle, stacking/execution, serialization and persistent-condition discovery

The accepted adaptation is deliberately narrower than the whole module: it imports the reviewed zero-level `ConditionLight` correctness boundary from Canary PR #297 and its focused tests.

## Fresh live-state/open-PR preflight

At task start:

- no open Otheryn PR existed;
- open Canary PRs were audited for overlap with `src/creatures/combat/condition.*`;
- PR #514 touched security validation infrastructure only;
- PR #525 touched physical teleport E2E only;
- PR #526 touched security audit documentation only;
- automated lifecycle PRs did not own the OAM-014 runtime boundary.

No overlapping open PR was identified for the canonical OAM-014 runtime path.

## Exact target/upstream and donor evidence

Task-start target and pinned upstream shared exact `condition.cpp` blob:

```text
5b15ed00c7e92eef6d8c719aec423443efae8b7a
```

Reviewed Canary PR #297 final head:

```text
b7f5de1f04cd3b521ee9621a0f001f0ced5e6c39
```

Accepted exact donor boundary:

```text
src/creatures/combat/condition.cpp
26a1cf0c9e01f4ab162438e8284f5cc73d129d11

tests/unit/players/condition/condition_light_test.cpp
ee2f185042cdb359aac1a752dce971ec76c38f8d

tests/unit/players/condition/CMakeLists.txt
b224d4eb1eb15eb92ca4a26f214c0764b82b03c3
```

Task-start legacy Canary already contained the corrected `condition.cpp` blob. Reviewed-history search found no second delivered PR that changed `condition.cpp` and needed to be coupled into this package.

## Accepted runtime behavior

PR #297 closes two independently reachable zero-level `ConditionLight` boundaries:

1. `ConditionLight::startCondition` normalizes level `0` to minimum valid level `1` before fade-interval division;
2. `ConditionLight::unserializeProp` normalizes deserialized persisted level `0` to `1`.

Existing valid nonzero behavior remains unchanged.

Focused regression coverage proves:

1. serialized/deserialized zero level becomes `1`;
2. directly constructed zero-level light starts safely with level `1` and interval `5000 / 1`;
3. valid level `5` remains `5` with interval `5000 / 5`.

## Target materialization

Otheryn issue:

```text
#34 — OAM-014: adapt zero-level ConditionLight safety
state: CLOSED / completed
```

Otheryn PR:

```text
#35 — fix(combat): adapt OAM-014 ConditionLight safety
final head: f4044811f2b930318ec6541a51e73a9a1b6fdce0
merge method: squash
target merge: 9d797b547c3f85f6d210c6123202c7cae32d5133
```

The final target diff contained exactly three accepted paths:

```text
src/creatures/combat/condition.cpp
tests/unit/players/condition/CMakeLists.txt
tests/unit/players/condition/condition_light_test.cpp
```

A temporary fail-closed materializer verified all three exact donor blob SHAs and removed itself before final review. No helper workflow or script remained in the accepted target diff.

## Exact-head target proof

Final target head:

```text
f4044811f2b930318ec6541a51e73a9a1b6fdce0
```

GitHub Actions:

```text
CI #117        run 29642976283  SUCCESS
Required #108  run 29642976213  SUCCESS
autofix.ci #101 run 29642976219 SUCCESS
```

Linux debug proof:

```text
configure/build: PASS
Canary datapack runtime smoke: PASS
database schema import: PASS
actual CTest Run Tests: 351/351 PASS
ConditionLightTest: 3/3 PASS
```

Primary evidence artifact:

```text
linux-debug-test-logs
artifact: 8429300008
digest: sha256:328f60045be1d42e4fba0c6b80aa64a3b8e767553808d7c47119750922cc2e36
```

The downloaded test artifact independently confirmed `100% tests passed, 0 tests failed out of 351` and all three focused `ConditionLightTest` cases passing.

The full ready-state platform matrix completed successfully, including Linux release, Windows, macOS and Docker jobs.

## Final target merge audit

Immediately before squash merge:

```text
comments: 0
reviews: 0
review threads: 0
Otheryn main drift from task-start baseline: none
PR scope: exactly 3 accepted paths
```

The merge used `expected_head_sha` protection and produced:

```text
9d797b547c3f85f6d210c6123202c7cae32d5133
```

## Boundary classification

| Boundary | Final classification | Evidence-backed result |
|---|---|---|
| ownership/lifecycle | applicable | `combat-conditions` only; generic combat remains completed OAM-013 |
| build/toolchain | compatible | existing Otheryn C++ unit-test harness reused |
| configuration | no change | no runtime configuration mutation |
| service/API | ADAPT | `ConditionLight` start/deserialization safety corrected |
| scheduling/concurrency | no change | no scheduler/concurrency mutation |
| persistence | bounded compatibility fix | invalid persisted zero light value is normalized in memory on load; no data rewrite or transaction redesign |
| protocol/session | no change | no protocol/session mutation |
| identifiers/assets | no change | no asset/identifier migration |
| world/map | no change | no map/world mutation |
| runtime | compatible and proven | exact-target build and Canary runtime smoke passed |
| tests | applicable and proven | 3/3 focused cases and 351/351 full target suite passed |
| physical-client E2E | not required | no protocol/client boundary changed |
| operations | bounded | exact donor blobs, exact-head gates, 3-path diff, race-safe drift check, expected-head merge |
| security/privacy | no new boundary | no credential/privacy/security-sensitive flow changed |

## Explicit exclusions

OAM-014 deliberately does **not** add or claim:

- generic combat formula or target-selection changes;
- spell registration, cooldown or individual spell migration;
- vocation-specific state migration;
- protocol/client/map/asset changes;
- broad persistence redesign;
- SQL/KV transaction atomicity;
- automatic persisted-data rewrite;
- exhaustive condition timing, stacking or persistence correctness;
- full Real Tibia condition formula/value parity.

OAM-004 SQL/KV non-atomicity remains authoritative.

## Final conclusion

```text
combat-conditions → ADAPT
```

Target adaptation is merged at:

```text
blakinio/Otheryn@9d797b547c3f85f6d210c6123202c7cae32d5133
```

OAM-014 is **not yet program-complete** at this point. The mandatory remaining sequence is:

1. merge this Canary governance feature PR;
2. archive the active OAM-014 task in a separate lifecycle-only PR;
3. reconcile the durable migration program in a separate program-only PR;
4. keep OAM-015 `NOT STARTED` until durable reconciliation merges.
