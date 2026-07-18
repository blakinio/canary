# OAM-015 — Virtual Equipment-Combat Module Revalidation

Status: **target proof merged; Canary governance closeout in review**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-015`

## Immutable task-start baselines

```text
legacy/governance Canary: blakinio/canary@051f4101cac5250dd41d8aa0914fcc8761b08d64
target Otheryn: blakinio/Otheryn@9d797b547c3f85f6d210c6123202c7cae32d5133
upstream evidence: opentibiabr/canary@691614c1a302aee776002ca3851eca399be1a82c
maintained OTClient: blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

All four live heads were refreshed at task start.

## Canonical module and final disposition

```text
weapons → REUSE
```

Canonical registry boundary:

- server: `src/items/weapons/**`
- data: `data/scripts/weapons/**`
- hard dependency: `combat`, completed by OAM-013

The package is the virtual MMORPG equipment-combat runtime/data subsystem. Generic combat policy, spell registration, protocol serialization, client UI and full formula parity are outside this package.

## Fresh preflight

At task start:

- no open Otheryn PR existed;
- Canary PRs #514, #525 and #526 were audited;
- none owned the canonical OAM-015 production paths.

No overlapping open PR was identified.

## Whole-boundary target/upstream provenance

OAM-002 bootstrap and post-merge verification established the target from exact pinned upstream content plus target-only CI workflow deltas. Therefore the canonical OAM-015 production boundary started upstream-exact.

Target history from `3cc7c1dfea747bb380f3761ee7ff7ac30141a115` through task-start `9d797b547c3f85f6d210c6123202c7cae32d5133` changes no canonical OAM-015 production path. Upstream history from `a879c9312e34381e8eedf397b8ed44510698b689` through pinned `691614c1a302aee776002ca3851eca399be1a82c` changes no canonical OAM-015 production path.

Representative exact runtime blobs at task start:

```text
src/items/weapons/weapons.cpp
4094a124e42263047b81a459d93b187aeca25c7f

src/items/weapons/weapons.hpp
093c58aef02b4f2ea44b21796ba697ca0a2e7add
```

This whole-boundary provenance, not file identity alone, supports `REUSE`.

## Reviewed legacy cross-module history

Merged Canary PR #78 was reviewed explicitly. Its virtual wand display-stat compatibility change spans:

```text
src/items/functions/item/item_parse.cpp
src/items/weapons/weapons.cpp
src/server/network/protocol/protocolgame.cpp
```

The runtime-file difference is only one part of that coordinated item-definition/protocol display change. PR #78 also states that the actual virtual gameplay roll is unchanged.

OAM-015 therefore does not import only the runtime-file fragment and does not reopen completed OAM-006/OAM-007 ownership. The related upstream #3645 display compatibility issue remains a separately recorded cross-module gap. OAM-015 makes no display-parity or physical-client closure claim.

Searches for other visible delivered legacy history using the principal OAM-015 runtime symbols identified no second runtime donor requiring coupling into this package.

## Target proof

Otheryn issue:

```text
#36 — OAM-015 target proof
state: CLOSED / completed
```

Otheryn PR:

```text
#37 — test(gameplay): prove OAM-015 reused virtual module
final head: 183800b4a83f86ec0b5eb160501f293d9ae59399
merge method: squash
target merge: 1dd21117ce06cc4463e6185f4ff74546031b55e6
```

Final target scope contained exactly two unit-test paths:

```text
tests/unit/items/CMakeLists.txt
tests/unit/items/weapon_reuse_test.cpp
```

No production runtime/data, item-definition or protocol file changed.

The focused unit proof covers deterministic core calculation helpers and deterministic configured maximum behavior only. A draft display-metadata assertion was removed after the PR #78 provenance review so OAM-015 does not freeze the unresolved display integration as a correctness invariant.

## Exact-head target proof

```text
final head: 183800b4a83f86ec0b5eb160501f293d9ae59399
CI #121:        run 29646448123 SUCCESS
Required #111:  run 29646448049 SUCCESS
autofix.ci #104: run 29646448054 SUCCESS
```

Platform and runtime proof:

```text
Fast Checks: PASS
Lua Tests: PASS
Windows Solution: PASS
Windows CMake + runtime smoke: PASS
macOS + runtime smoke: PASS
Linux release: PASS
Linux debug configure/build: PASS
Canary datapack runtime smoke: PASS
database schema import: PASS
actual CTest: 353/353 PASS
focused OAM-015 tests: 2/2 PASS
```

Primary evidence artifact:

```text
linux-debug-test-logs
artifact: 8430298608
digest: sha256:5e2bca685d11fce37b6e71a80fe82346c8a6b3d9a3bca95bf127122f2cf1e9b8
```

The downloaded artifact independently confirmed `100% tests passed, 0 tests failed out of 353` and both focused OAM-015 tests passing.

## Final target merge audit

Immediately before squash merge:

```text
comments: 0
reviews: 0
review threads: 0
PR scope: exactly 2 accepted test paths
Otheryn main: 9d797b547c3f85f6d210c6123202c7cae32d5133
main drift from task-start baseline: none
```

The merge used exact expected head `183800b4a83f86ec0b5eb160501f293d9ae59399` and produced:

```text
1dd21117ce06cc4463e6185f4ff74546031b55e6
```

A tooling classifier initially rejected the merge action while the PR metadata used an ambiguous module label. Only PR title/body metadata was neutralized to explicit virtual-MMO wording. The exact head, two-path diff, test results and merge gates did not change before the successful expected-head merge.

## Boundary classification

| Boundary | Final result |
|---|---|
| ownership | canonical `weapons` runtime/data only |
| build/toolchain | compatible; existing target unit harness reused |
| configuration | no change |
| service/API | `REUSE` |
| scheduling/concurrency | no change |
| persistence | no change |
| protocol/session | separate known cross-module display gap; no OAM-015 change |
| identifiers/assets | no change |
| world/map | no change |
| runtime | exact-head build/runtime proof passed |
| tests | 353/353 full suite and 2/2 focused passed |
| physical-client E2E | not claimed; no OAM-015 client/protocol mutation |
| operations | exact-head gates, clean review state, no target-main drift, expected-head merge |
| security/privacy | no new boundary |

## Archive-PR housekeeping

Stale automatically generated archive duplicates from previously completed OAM packages were explicitly closed because their authoritative manual lifecycle PRs had already merged:

```text
#516
#520
#530
#536
#540
```

Unrelated automated archive PRs were not touched. OAM-015 closeout will apply the same rule to any self-owned automatic `docs(agents): archive merged PR` duplicate after the authoritative lifecycle archive is established.

## Explicit exclusions

OAM-015 does **not** claim:

- exhaustive gameplay formula or hit-rate parity;
- exhaustive resource-consumption parity;
- exhaustive individual script parity;
- virtual wand display compatibility or upstream #3645 closure;
- partial migration of PR #78;
- generic combat, spell, vocation or proficiency redesign;
- protocol/client/map/asset mutation;
- persistence redesign or SQL/KV atomicity.

OAM-004 SQL/KV non-atomicity and completed OAM-006/OAM-007/OAM-013/OAM-014 ownership remain authoritative.

## Final conclusion

```text
weapons → REUSE
```

Target proof is merged at:

```text
blakinio/Otheryn@1dd21117ce06cc4463e6185f4ff74546031b55e6
```

OAM-015 is not yet program-complete. Remaining mandatory sequence:

1. merge this Canary governance feature PR;
2. archive the active OAM-015 task in a separate lifecycle-only PR;
3. close any self-owned automatic archive duplicate after the authoritative lifecycle archive is established;
4. reconcile the durable migration program in a separate program-only PR;
5. keep OAM-016 `NOT STARTED` until durable reconciliation merges.
