# OAM-033 Charms revalidation

## Final disposition

`charms → ADAPT`

## Immutable task-start baselines

- Canary/governance: `f05ea5e916af00ab1469a2332aaec2d3c9df7478`
- Otheryn target: `1a4bbceda2c805bc69c68c1592e04e63d7e9a269`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`

Canonical `charms` owns Charm definitions, costs, unlock state, assignment and combat effects and depends on completed `combat`, `cyclopedia`, `player-persistence` and `protocol`. TSD-004 preserves this independent ownership even where `IOBestiary` hosts Charm helper methods.

## Accepted adaptation boundary

Merged legacy PR #188 supplies exactly two accepted Charm-owned corrections:

1. `data/scripts/lib/register_bestiary_charm.lua`: `registerCharm.category` checks `mask.category` before applying `charm:category(mask.category)` instead of gating the category on unrelated `mask.type`.
2. `src/io/iobestiary.cpp`: the all-Charm reset price charges the `11,000` surcharge only for levels above 100 with `(playerLevel - 100) * 11000`, rather than charging `playerLevel * 11000` after level 100.

Task-start target and fresh upstream retained both pre-fix behaviors while current legacy retained both PR #188 corrections. PR #188 Bestiary, Bosstiary and Cyclopedia Character hunks are already owned by OAM-031, OAM-030 and OAM-029; PR #192 is monster-data remediation and PR #243 is validator/workflow control. No maintained OTClient change is selected.

Current open Canary PRs at preflight did not touch either selected production path or OAM-033 governance paths, and Otheryn had no competing open writer. The smallest valid disposition is therefore `ADAPT`, limited to the two production corrections plus focused proof and necessary prior-proof boundary maintenance.

## Target delivery

Otheryn PR #67 final head `e1fca0b372173db335118735f501f315d442888f` changed exactly seven intended paths: the two production fixes, OAM-033 task/evidence/test registration, and one OAM-031 proof-boundary maintenance file. No temporary helper/workflow path remained.

The first target CI run #230 on superseded head `88804b02857e76039fe694dfffc99fcc4fa49c51` compiled successfully and passed runtime smoke/schema, Fast Checks, Lua, autofix and Repository Audit, but Linux-debug full tests finished 421/422. The sole failure was `Oam031BestiaryAdaptTest.CharmResetPricingRemainsOutsideBestiaryPackage`, an older assertion that explicitly required the pre-OAM-033 reset-price formula. Both new OAM-033 focused tests passed. The obsolete Charm-specific OAM-031 assertion was retired without changing either production correction; OAM-031 Bestiary null-safety and difficulty proofs remain intact.

On final head `e1fca0b372173db335118735f501f315d442888f`, autofix.ci #192 run `29867543037`, Repository Audit #27 run `29867542987`, CI #233 run `29867543182`, and Required #218 run `29867542998` all succeeded. Linux-debug full `Run Tests` succeeded. Test-log artifact `8510218346` has digest `sha256:1bc7425f036bb5f39c19539590da0704f026718e4bbd54ad2ede79c023300cbc`. Comments, reviews and review threads were empty, Otheryn `main` had no drift from immutable target base, and PR #67 merged as `c887318a676998da5ef3224a3aa8d1e0df75e607`.

## Governance drift audit

Canary `main` remains at immutable OAM-033 task-start baseline `f05ea5e916af00ab1469a2332aaec2d3c9df7478` when this governance record is finalized. The active OAM-033 preflight branch/PR #696 is the existing single bounded governance owner for this package; no second OAM-033 governance task is created.

## Nonclaims

OAM-033 does not claim exhaustive Charm definition/value parity, all unlock costs, assignment-slot rules, combat proc formulas, element/resistance behavior, Bestiary progress correctness, protocol/client compatibility, maintained-client rendering, persistence atomicity, economy transaction atomicity, physical-client Charm E2E closure, or full Real Tibia parity.
