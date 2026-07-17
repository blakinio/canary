# OAM-008 — Vocations First Low-Risk Canonical Module Migration

Status: implementing

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

No vocation implementation or XML transfer is required because the exact task-start target already contains the same canonical module content.

## Working disposition

`vocations` → `REUSE` candidate.

This means OAM-008 accepts the already-present target implementation only after target compatibility and focused proof; it does not infer parity from file presence alone.

## Target proof package

Otheryn issue #24 tracks OAM-008.

Otheryn draft PR #25, branch `test/oam-008-vocations-reuse-proof`, is proof-only:

- adds focused unit coverage for case-insensitive vocation lookup;
- adds focused unit coverage for promotion lookup semantics;
- registers the test in the existing `canary_ut` target;
- changes no `vocation.cpp`, `vocation.hpp` or `vocations.xml` content.

The existing full target runtime path loads the same vocation XML during server startup, but OAM-008 does not substitute generic startup evidence for focused tests. OAM-009 remains the separate package for bounded target physical-client E2E proof.

## Validation plan

1. exact canonical registry/dependency/path refresh;
2. exact target/legacy/upstream blob matrix;
3. live open-PR ownership/overlap audit;
4. target PR #25 focused unit tests and full exact-head CI;
5. clean target comments/reviews/unresolved-thread gate;
6. exact-head target merge if all gates pass;
7. final Canary governance ownership/CI/review gates;
8. separate lifecycle-only archive;
9. only then OAM-009 may start.

## Known limits

- No Real Tibia vocation value parity is claimed.
- No combat damage, spell/weapon eligibility or Wheel behavior is proven by this package.
- No maintained-client source mutation is authorized or required.
- No physical-client E2E is claimed by OAM-008; that proof is deliberately reserved for OAM-009.
- Exact blob identity is provenance evidence, not sufficient by itself for `REUSE`; target tests and gates remain required.
