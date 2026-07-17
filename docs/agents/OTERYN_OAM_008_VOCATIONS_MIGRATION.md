# OAM-008 — Vocations First Low-Risk Canonical Module Migration

Status: ready

## Bounded scope

Exactly one canonical module: `vocations`.

Out of scope: character progression state, combat formulas, spells, weapons, weapon proficiency, Wheel of Destiny, client presentation, protocol changes, persistence changes, Real Tibia value parity and every other canonical module.

## Exact task-start baselines

- governance/legacy: `blakinio/canary@317c1c4235377c388883aa2fd425d324f8ce4d2e`
- target: `blakinio/Otheryn@68c4f39f7b1b45f880543c258627b4ccf73dbc86`
- upstream: `opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f`
- maintained client: not applicable to OAM-008 module acceptance; OAM-009 owns separate physical-client proof

## Why `vocations` is the first low-risk module

The target architecture contract requires an evidence-selected low-risk module after the completed item/world runtime foundation.

`vocations` has:

- no canonical `depends_on` dependencies;
- a narrow static registry/configuration boundary;
- no direct persistence or protocol surface in its canonical scope;
- no open Canary PR overlap on its canonical paths;
- no open Otheryn PR at task-start;
- exact source/data identity across target, legacy and upstream.

Rejected alternatives for this first package:

- `world-zones`: target/upstream already carry a cleaner cache implementation than the divergent legacy fork, so legacy transfer would be baggage rather than a low-risk migration.
- `instances`: absent from target/upstream and therefore a real transfer candidate, but its merged legacy scope spans region allocation, creature ownership isolation, cleanup, expiration, scheduler ownership and an arena consumer; it is not the safest first slice.
- `containers`: nested state and serialization boundaries interact with player/world persistence and duplication/loss risks; broader than the selected static registry boundary.

## Canonical path matrix

| Path | Target blob | Legacy blob | Upstream blob | Result |
|---|---|---|---|---|
| `src/creatures/players/vocations/vocation.cpp` | `70411c647329194528b11985e9be5674804cc5bc` | same | same | identical |
| `src/creatures/players/vocations/vocation.hpp` | `537fc0c5b61f1e0026a96288d7da355d7c7c06e9` | same | same | identical |
| `data/XML/vocations.xml` | `57c014e720bbe8d7f83501970c2b89976598cc3d` | same | same | identical |

No vocation implementation or XML transfer was required because the exact task-start target already contained the same canonical module content.

## Final disposition

`vocations` → `REUSE`.

The decision is based on exact canonical content identity plus target compatibility proof; it is not inferred from file presence alone.

## Target proof and delivery

Otheryn issue #24 tracks OAM-008.

Otheryn PR #25 was proof-only and changed exactly:

- `tests/unit/players/vocation_test.cpp`;
- `tests/unit/players/CMakeLists.txt`.

It changed no `vocation.cpp`, `vocation.hpp` or `vocations.xml` content.

Final target PR head: `9453a1754501ce183e20d294df1064a5ccbad54c`.

Exact-head target gates:

- autofix.ci #77: PASS;
- CI #88: PASS;
- Required #84: PASS;
- Linux debug `Run Tests`: PASS;
- macOS build/runtime smoke: PASS;
- Windows CMake build/runtime smoke: PASS;
- Linux release build/runtime smokes: PASS;
- clean final review state: zero comments, zero submitted reviews and zero unresolved review threads.

The Linux debug test artifact `linux-debug-test-logs` recorded both focused tests as executed and passed among 325 CTest cases:

1. `VocationsTest.LookupIsCaseInsensitiveAndUnknownFallsBackToNone` — PASS;
2. `VocationsTest.PromotionLookupReturnsDistinctVocationWithMatchingBase` — PASS.

Otheryn PR #25 squash-merged with exact-head guard as `f59a58426b4d3910ba0cdc0d2332c24f31a1db4f`.

The target merge adds only durable focused acceptance coverage for an unchanged reused module.

## Validation boundary

OAM-008 acceptance proves:

- exact target/legacy/upstream identity for the three canonical paths;
- case-insensitive registry lookup and unknown-name fallback behavior;
- promoted-vocation lookup behavior for a distinct vocation sharing the base relation;
- clean full target CI/build/runtime smoke compatibility after adding the focused tests.

The existing full target runtime path loads vocation configuration during server startup, but OAM-008 does not claim physical-client proof. OAM-009 remains the separate package for bounded target physical-client E2E.

## Known limits

- No Real Tibia vocation value parity is claimed.
- No combat damage, spell/weapon eligibility or Wheel behavior is proven by this package.
- No maintained-client source mutation is authorized or required.
- No physical-client E2E is claimed by OAM-008; that proof is deliberately reserved for OAM-009.
- This package does not broaden persistence or protocol claims.
- The target test-only merge does not imply migration authorization for any other canonical module.

## Next gate

Finalize Canary governance PR #469 with the exact target merge evidence, shared program update, ownership/CI/review gates and separate lifecycle-only archival. Only after OAM-008 feature and lifecycle completion may OAM-009 begin.
