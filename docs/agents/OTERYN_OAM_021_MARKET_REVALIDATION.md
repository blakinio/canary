# Oteryn OAM-021 Market Revalidation

Date: 2026-07-19

Task: `CAN-20260719-oteryn-market-revalidation`

Coordination: `OAM-021`

Canonical module: `market`

Final disposition: `ADAPT`

## Immutable task-start baselines

- Canary legacy/governance: `183d7224cb5de57585294d72631f37783b93dc89`
- clean Otheryn target: `d59207d05ab6dd9450b05d0a6b4d9122fda60489`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

## Dependency and ownership result

Canonical `market` depends on completed `player-persistence` and `protocol` and interacts with completed `exaltation-forge`, so it is dependency-valid after OAM-020.

Fresh preflight found no open Otheryn or maintained-OTClient PR and no pre-existing OAM-021 branch/PR. Canary had advanced one commit after the OAM-020 durable reconciliation, but the delta was limited to unrelated player-skill persistence E2E documentation/tests/tooling and did not overlap OAM-021 governance ownership.

Open Canary PR #526 is an evidence-only security audit. Its changed paths are limited to its own task/security documents, so it is not a runtime writer and does not conflict with this package. Its qualified market findings were nevertheless treated as required evidence before classification.

## Source comparison and classification

The task-start Otheryn and fresh upstream market core are content-identical for the reviewed `src/io/iomarket.cpp` and `src/game/game.cpp` market implementation. This rejects any claim that ordinary upstream drift itself requires a legacy copy.

Current legacy Canary differs through selected multichannel additions:

- PR #152 / market expiry: `EconomicLedgerStore` audit/idempotency around expiry;
- PR #191 / market expiry: cluster leader gating for the global expiry job;
- PR #234 / market cancel: `EconomicLedgerStore` audit/idempotency around cancellation.

Those changes are deliberately not imported wholesale. They depend on the separately owned multichannel runtime and do not form a complete generic exactly-once market contract: create and accept remain explicitly unwired, and the underlying offer/history/value-effect crash boundary remains only partially covered.

Open security audit evidence further records:

- `OTS-ECO-MKT-001` — `PROVEN`, HIGH: a cross-process/multiwriter partial-fill race because acceptance reads an offer without a row claim and applies value effects before the final offer decrement/delete;
- `OTS-ECO-MKT-002` — `PROVEN`, HIGH: a multichannel remote-owner hazard where `getPlayerByGUID(..., true)` can load and full-save a stale counterparty snapshot owned by another live process.

These findings block unconditional whole-module `REUSE`. They do not justify importing the legacy multichannel stack into the clean target: Otheryn does not currently adopt that cross-process ownership model, and `DatabaseTasks` returns asynchronous DB callbacks to the single dispatcher before gameplay callbacks execute. Future multiwriter market support must therefore define its own atomic claim/recovery and remote-owner routing contract.

Generic crash/restart atomicity between durable market-offer/history mutation and item/balance/account effects remains a known clean-target gap. OAM-021 does not claim to solve it with an incomplete ledger import.

Therefore the accepted disposition is:

```text
market → ADAPT
```

## Maintained-client contract

At maintained OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`, the existing market request wire contract is compatible with the clean target:

- create: type, item id, optional tier for classified items, amount, 64-bit price, anonymous flag;
- cancel: timestamp plus 16-bit counter;
- accept: timestamp plus 16-bit counter plus amount;
- existing MarketEnter/MarketDetail/MarketBrowse responses are already dispatched by the client parser.

The bounded target adaptation does not change those packet shapes, so no maintained-OTClient write is required.

## Accepted target adaptation

Target PR: `blakinio/Otheryn#45`

Target branch: `dudantas/oam-021-market-adapt`

Exact final target head: `f13d4d2d0626c99dd2318ef088ce155f67b0b5ae`

Target squash merge: `b90e287a40413102c87e8c7fa3d5c01ad401cb6d`

The bounded target change contains exactly five intended paths:

- `docs/oam-021-market-adapt.md`
- `src/io/iomarket.cpp`
- `src/io/market_validation.hpp`
- `tests/unit/game/CMakeLists.txt`
- `tests/unit/game/oam_021_market_adapt_test.cpp`

It:

- centralizes deterministic 16-bit market offer counter derivation;
- rejects client timestamp/duration combinations that would underflow the offer creation lookup;
- replaces parse-then-`uint8_t`-truncate tier handling with strict `std::from_chars` parsing and configured/range validation;
- adds focused deterministic tests for those accepted boundaries.

A temporary target materializer applied the exact `iomarket.cpp` hunk and removed itself before the target PR was opened. No materializer path remained in the target diff.

## Exact target proof

```text
Otheryn PR #45 final head: f13d4d2d0626c99dd2318ef088ce155f67b0b5ae
target squash merge: b90e287a40413102c87e8c7fa3d5c01ad401cb6d
autofix.ci #144 / 29704971999: SUCCESS
CI #167 / 29704972077: SUCCESS
Required #151 / 29704972006: SUCCESS
full Linux debug CTest: 396/396 PASS
focused Oam021MarketAdaptTest: 3/3 PASS
test-log artifact: 8447725005
test-log digest: sha256:f6f6b67fda044f1d8b88600a87234f4cb6559ae3e3d9270ddd2a98041948debb
linux-debug binary artifact: 8447726445
linux-debug binary digest: sha256:7075ee646302f99d111d0838a6f5943fa791545c0e1a8dee112c61ce4a857084
```

The ready-state full matrix passed Fast Checks and Lua Tests; Linux debug compiled, imported schema and passed all 396 CTest cases; Linux release compiled and passed Canary and Global runtime smoke tests; macOS release produced its release/runtime-smoke artifacts; Windows CMake compiled and passed runtime smoke; Windows Solution produced its debug artifact; and Docker image build/validation succeeded.

Pre-merge target audits were clean on the exact final head: exactly five intended paths, zero comments, zero reviews, zero review threads, and Otheryn `main` had no drift from the task-start target base. The merge used expected-head squash protection against `f13d4d2d0626c99dd2318ef088ce155f67b0b5ae`.

## Explicit exclusions and known gaps

OAM-021 does not import or claim:

- generic multichannel Redis/session ownership or leader-election architecture;
- legacy `economic_ledger` as a generic market recovery solution;
- crash-safe exactly-once create/cancel/accept/expiry;
- cross-process/multiwriter market safety;
- remote-player mutation routing;
- generic bank/account/guild economy redesign;
- exhaustive current Real Tibia market parity;
- NPC shops, store products or direct player trade;
- maps, OTBM, `items.otb`, world assets, schema or deployment changes;
- maintained-OTClient changes;
- physical-client Market E2E closure.

These exclusions are deliberate boundaries, not hidden completion claims.

## Lifecycle gate

The target stage is merged and proven. OAM-021 remains incomplete until the remaining governance lifecycle is performed in order:

1. exact-head Canary governance gates and expected-head governance merge;
2. separate authoritative lifecycle archive;
3. separate one-file durable program reconciliation;
4. only then may OAM-022 start.
