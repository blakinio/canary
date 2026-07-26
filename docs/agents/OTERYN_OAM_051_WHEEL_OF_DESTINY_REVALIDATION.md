# OAM-051 Wheel of Destiny revalidation

## Final disposition

```text
wheel-of-destiny → ADAPT (phase A and phase B durably complete)
```

OAM-051 completed as two bounded Otheryn server-side packages. OAM-051A delivered Wheel safety and state-integrity hardening. OAM-051B delivered only the Hunting Task Shop Bonus Promotion points contract. The programme does not claim a complete maintained-client Taskboard UI or complete current Wheel parity.

## OAM-051A durable evidence

- Canary preflight PR #951 merged as `a4a35495d4a8dc047bd3315b95c9fb577ac597af`.
- Otheryn feature head `1f4ce3c11f6acf292775daac886e9dace7e8280f` passed CI `30193154684` and Required `30193154608`.
- Otheryn feature PR #115 merged as `47863ce250bce73c1b9af3077f82e9bf6e99e3d1`.
- Otheryn lifecycle PR #118 passed Required `30193946125` and merged as `bd0b58a362d89e449a6863ba299d1c50ad4e6685`.
- Canary phase-A governance PR #956 merged as `d8416553be77d4999d81afcce2399a37a25337a6`.

Phase A integrated atomic/fail-closed allocation validation, temple-only decrease enforcement, saturating point accounting, bounded gem/grade/state handling, permanent-point load ordering and malformed current-protocol Wheel action rejection. It preserved every Task Shop, current-balance, combat-effect, spell-area, stance, replacement-spell, geometry and client exclusion.

## OAM-051B resolved contract

The candidate from Canary PR #230 was reduced to one Bonus Promotion offer:

- offer id `0`, type `4`;
- purchased points `0..50`, displayed as current purchases plus one;
- cost for next point `n`: `100 * (1 + n * (n - 1) / 2)`;
- statuses `0x00` available, `0x02` insufficient points and `0x04` bought/capped;
- exact Taskboard request/response handling;
- Hunting Task Point mutation;
- Wheel extra-point accounting;
- deterministic malformed-request, cap, persistence and replay validation.

Generated Lua API documents and Canary-only Python validators remained evidence tooling. The donor patch was not copied wholesale.

## Maintained-client wire contract

Maintained-client baseline: `blakinio/otclient@ce4329ee13b39576915240605c2fe6657096c517`.

```text
server opcode 0x5B
  U8 subtype = 0x02
  U8 offers_count
  repeated offer:
    U8  offer_type = 0x04
    U16 purchased_display_value
    U32 next_cost
    U8  status

client opcode 0x5F
  U8 action = 0x0B
  U16 offer_id = 0
  no trailing bytes
```

The client derives purchased count as `max(display_value - 1, 0)`. Its parser consumes the payload and dispatches `g_game.onTaskHuntingShopData`. The baseline does not ship a complete controller-owned `modules/game_taskboard` UI consumer, so packet compatibility is proven but visible/operable maintained-client UI is not claimed.

## Durable transaction model

The donor Wheel-KV sequence was rejected. Otheryn persists Hunting Task Points and PlayerStorage inside the same `DBTransaction::executeWithinTransaction(savePlayerGuard)` SQL boundary, while Wheel KV is staged only after that transaction commits.

OAM-051B therefore uses SQL-backed PlayerStorage:

- reserve `wheel.hunting_task_shop_points` as key `6` in the existing Wheel range, yielding absolute key `1000006`;
- validate offer id, exact cost, balance and cap before mutation;
- update the storage-backed purchased count and Hunting Task balance together;
- restore the prior count if the in-process debit unexpectedly fails;
- rely on SQL rollback if player save fails;
- never mirror the purchased count into Wheel KV;
- load the storage-backed count before persisted Wheel allocation acceptance.

## OAM-051B target completion

- Canary preflight exact head `f7ba253dc078b9ed65801d1df36599e181ecdb81` passed Agent Task Ownership `30200151129` and CI `30200151201`.
- Canary preflight PR #959 merged as `9e865b68b9197b28450002412ca1720683cf1f64`.
- Otheryn exact final feature head `a507abc5d6b9aa3158f9b009a715d5aee0b4c43c` passed Repository Audit `30206237389`, autofix `30206237391`, CI `30206237518` and Required `30206237406`.
- Full Otheryn CI included Fast Checks, Lua Tests, Linux debug/release, all C++ tests, schema import, Canary and Global runtime smoke, macOS, both Windows variants and Docker validation.
- Otheryn feature PR #128 changed exactly seven declared paths, had no comments, reviews or review threads, was behind `main` by zero and squash-merged with expected-head protection as `546eac0a00ec620e7293d0548e30662024464084`.
- Otheryn lifecycle PR #134 changed only active/archive and two evidence reports, passed Required `30207104087` and merged as `db10096f0ebb484f05883dbde4dd895744fbe8c6`.

## Delivered target boundary

Otheryn now contains:

- named SQL-backed storage `wheel.hunting_task_shop_points` / `1000006`;
- one bounded Bonus Promotion offer;
- exact cost, display and status handling;
- fail-closed incomplete, trailing and wrong-offer request rejection;
- same-SQL-transaction persistence for balance and purchased count;
- no Wheel KV mirror;
- storage-derived Wheel extra-point accounting;
- official Wheel payload reporting;
- focused cost, cap, rollback, parser, load-order and persistence-boundary tests;
- unchanged empty Bounty and Weekly shims.

## Preserved exclusions

OAM-051 did not deliver or authorize:

- maintained-client Taskboard UI or assets;
- Bounty, Weekly, Soulpit or other Task Shop offers;
- current Wheel balance constants, formulas, areas or effect ordering;
- Vessel Resonance bonuses, critical healing, vocation stances, replacement spells or Strong Ice Wave geometry;
- legacy parser transfer;
- generated Lua API migration;
- schema migration, map, deployment or production changes.

## Governance closure

OAM-051A and OAM-051B are durably complete. The active Canary preflight task is archived after exact Otheryn feature and lifecycle evidence. OAM-052 may be selected only from a fresh current-state ownership, dependency and evidence review; deferred OAM-051 nonclaims must not be silently reopened as part of that selection.

## Remaining nonclaims

OAM-051 does not prove physical maintained-client Taskboard interaction, a complete Taskboard UI, complete Wheel parity or current authoritative gameplay balance. Those remain separate milestones and do not keep OAM-051 active.
