# OAM-051 Wheel of Destiny revalidation

## Current disposition

```text
wheel-of-destiny → ADAPT (phase A complete; phase B contract-blocked)
```

OAM-051 is intentionally decomposed. OAM-051A delivered and lifecycle-closed the server-side Wheel safety and state-integrity boundary. OAM-051B is limited to the Hunting Task Shop Bonus Promotion contract and remains blocked before target implementation.

## OAM-051A durable evidence

- Canary preflight PR #951 merged as `a4a35495d4a8dc047bd3315b95c9fb577ac597af`.
- Otheryn feature head `1f4ce3c11f6acf292775daac886e9dace7e8280f` passed CI `30193154684` and Required `30193154608`.
- Feature PR #115 merged as `47863ce250bce73c1b9af3077f82e9bf6e99e3d1`.
- Lifecycle PR #118 passed Required `30193946125` and merged as `bd0b58a362d89e449a6863ba299d1c50ad4e6685`.
- Canary phase-A governance PR #956 merged as `d8416553be77d4999d81afcce2399a37a25337a6`.

Phase A preserved every Task Shop, current-balance, combat-effect, spell-area, stance, replacement-spell, geometry and client exclusion.

## OAM-051B candidate

The bounded candidate from Canary PR #230 consists of:

- one Task Shop Bonus Promotion offer;
- points 1–50 and their deterministic cost progression;
- Hunting Task Point mutation;
- bounded Wheel KV/cache/load/relog state;
- one Player Lua binding;
- current-client payload and status fields;
- deterministic malformed-request, insufficient-balance, cap and failure tests.

PR #230 is donor evidence, not permission for whole-patch transfer.

## Transaction blocker

The donor purchase sequence removes Hunting Task Points before persisting the purchased Wheel point. This creates an unproven failure window. OAM-051B requires one explicit tested target model:

- rollback on persistence failure;
- recoverable staged intent with replay or compensation; or
- a proven existing transaction that covers both resource and Wheel-state mutation.

Required evidence must include persistence failure, interruption/relog, duplicate replay, cap and insufficient-balance cells. In-memory success is not durable proof.

## Maintained-client blocker

Fresh maintained-client baseline is `ce4329ee13b39576915240605c2fe6657096c517`. Repository search did not isolate authoritative parser/UI semantics for the Task Shop Wheel field. Target implementation remains blocked until evidence proves:

- field order and integer widths;
- purchased-count derivation;
- available/insufficient/bought status meanings;
- cap and relog display behavior;
- server-only compatibility or the need for a separately governed client change.

Static donor comments alone are insufficient; exact source or physical-client evidence is required.

## Preserved exclusions

OAM-051B does not authorize Wheel balance constants, formulas, areas, effect ordering, Vessel Resonance bonuses, critical healing, vocation stances, replacement spells, Strong Ice Wave geometry, legacy game parser transfer, map, schema or deployment changes.

Generated Lua API documents remain generated outputs. Canary Python validators remain external evidence tooling.

## Governance checkpoint

Canary PR #959 owns only this report and the active OAM-051 task. The `ci:final-gate` label was applied before this final checkpoint commit. Exact-head Ownership and full CI must pass before merge. The merge records a blocked preflight only; it does not authorize an Otheryn source branch.

## Nonclaims

OAM-051 does not yet prove Task Shop interoperability, atomic purchase durability, DB/KV failure recovery, physical-client behavior, complete Wheel parity or current authoritative gameplay balance.
