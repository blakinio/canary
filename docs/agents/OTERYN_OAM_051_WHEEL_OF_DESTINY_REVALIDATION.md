# OAM-051 Wheel of Destiny revalidation

## Current disposition

```text
wheel-of-destiny → ADAPT (phase A complete; phase B contract resolved and target-bounded)
```

OAM-051 is intentionally decomposed. OAM-051A delivered and lifecycle-closed the server-side Wheel safety and state-integrity boundary. OAM-051B is limited to the Hunting Task Shop Bonus Promotion contract. The source and persistence evidence below resolves the preflight blockers and authorizes a bounded Otheryn server-and-tests package; it does not authorize a complete maintained-client Taskboard UI claim.

## OAM-051A durable evidence

- Canary preflight PR #951 merged as `a4a35495d4a8dc047bd3315b95c9fb577ac597af`.
- Otheryn feature head `1f4ce3c11f6acf292775daac886e9dace7e8280f` passed CI `30193154684` and Required `30193154608`.
- Feature PR #115 merged as `47863ce250bce73c1b9af3077f82e9bf6e99e3d1`.
- Lifecycle PR #118 passed Required `30193946125` and merged as `bd0b58a362d89e449a6863ba299d1c50ad4e6685`.
- Canary phase-A governance PR #956 merged as `d8416553be77d4999d81afcce2399a37a25337a6`.

Phase A preserved every Task Shop, current-balance, combat-effect, spell-area, stance, replacement-spell, geometry and client exclusion.

## OAM-051B bounded candidate

The candidate from Canary PR #230 is reduced to:

- one Task Shop Bonus Promotion offer;
- purchased points `0..50` and next-point display values `1..51`;
- cost for next point `n`: `100 * (1 + n * (n - 1) / 2)`;
- Hunting Task Point mutation;
- Wheel extra-point accounting;
- current Taskboard request/response handling;
- deterministic malformed-request, insufficient-balance, cap, persistence and relog tests.

Generated Lua API documents and Canary-only Python validators are evidence tooling, not target migration content. PR #230 remains a donor, not permission for whole-patch transfer.

## Resolved maintained-client wire contract

The maintained-client baseline is `blakinio/otclient@ce4329ee13b39576915240605c2fe6657096c517`.

The exact existing parser contract is:

```text
server opcode 0x5B
  U8 subtype = 0x02                 # Hunting Shop
  U8 offers_count
  repeated offer:
    U8  offer_type = 0x04           # Bonus Promotion
    U16 purchased_display_value     # current purchases + 1
    U32 next_cost
    U8  status
```

The maintained client derives `currentPurchases` as `max(display_value - 1, 0)`. Its exact statuses are `0x00` available, `0x02` not enough points and `0x04` bought. A zero `next_cost` is also treated as bought. The existing Otheryn request shim already constrains Shop Buy to action `0x0B` plus one `U16` offer identifier; the bounded Bonus Promotion offer identifier is `0`.

The C++ parser consumes this payload and dispatches `g_game.onTaskHuntingShopData`. The exact baseline does not ship a complete controller-owned `modules/game_taskboard` UI consumer. Therefore:

- the Otheryn server package is `server-first-safe` at the wire level;
- current maintained-client parsing must not desynchronize;
- the feature is not claimed visible or operable through that maintained client until a separate `OTS-*` client Taskboard module contract is delivered;
- no OTClient mutation belongs in the OAM-051B server package.

## Resolved durable transaction model

The donor KV sequence is rejected. Otheryn persists Hunting Task Points through the player SQL save transaction, while Wheel KV is deliberately staged after that transaction commits in a separate persistence domain. Those two domains cannot prove atomic purchase durability.

OAM-051B must instead persist the purchased-point count through the existing SQL-backed `PlayerStorage` domain:

- reserve `wheel.hunting_task_shop_points` as key `6` in the existing `1000000..2000000` Wheel storage range;
- keep the runtime Wheel count synchronized from that storage value;
- mutate Hunting Task Points and the storage-backed purchased count together in one bounded player operation;
- validate offer id, exact current cost, balance and cap before either mutation;
- rollback both in-memory values if the bounded operation cannot complete;
- rely on the existing `DBTransaction::executeWithinTransaction(savePlayerGuard)` boundary, which persists player storages and Task Hunting state in one SQL transaction;
- never mirror this purchased count into Wheel KV.

This model has deterministic failure semantics:

- crash before a successful player save loses both in-memory mutations;
- SQL save failure rolls back both durable mutations;
- successful SQL commit persists both;
- duplicate/replayed requests re-evaluate current state and cannot pass the cap or reuse a stale lower cost;
- relog loads the same storage-backed count before Wheel extra-point accounting is accepted.

## Required target validation

The Otheryn implementation must prove:

- exact packet bytes, widths, offer type, display-value offset and status values;
- malformed/truncated/trailing request rejection without mutation;
- wrong offer id rejection;
- exact costs at representative boundaries, including points 1, 2, 49 and 50;
- insufficient balance and already-at-cap behavior;
- atomic in-memory rollback;
- SQL transaction failure leaves both durable values unchanged;
- successful save/relog restores both the reduced Hunting Task Point balance and purchased Wheel points;
- duplicate/replayed purchase cannot double-apply;
- Wheel extra points load before persisted allocation validation;
- existing empty Bounty and Weekly shims remain unchanged.

Physical official-client interaction remains a final acceptance cell when the environment is available. Static packet fixtures and repository CI do not replace that evidence.

## Authorized target boundary

A fresh Otheryn task may now own only the bounded server-and-tests paths required for:

- storage reservation `wheel.hunting_task_shop_points`;
- one atomic purchase operation;
- Taskboard Shop response and Shop Buy handling;
- Wheel extra-point load/accounting;
- focused C++/Lua/source-contract and persistence failure tests;
- OAM task/report lifecycle records.

The target branch must start from current Otheryn `main`, search current ownership again and use a draft PR. It must not copy the donor wholesale.

## Preserved exclusions

OAM-051B does not authorize a maintained-client Taskboard UI, assets, other Taskboard offers, Bounty/Weekly implementation, Wheel balance constants, formulas, areas, effect ordering, Vessel Resonance bonuses, critical healing, vocation stances, replacement spells, Strong Ice Wave geometry, legacy parser transfer, schema migration, map or deployment changes.

## Governance checkpoint

Canary PR #959 owns only this report and the active OAM-051 task. Exact-head Agent Task Ownership and CI must pass before merge. Its merge authorizes only the bounded Otheryn OAM-051B server-and-tests task described above. A complete maintained-client Taskboard experience remains a separate cross-repository milestone and claim.

## Nonclaims

OAM-051 does not yet prove the target implementation, physical-client behavior, a maintained-client Taskboard UI, complete Wheel parity or current authoritative gameplay balance.
