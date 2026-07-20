# Player soul persistence assertion

## Purpose

`player_soul` is a bounded Universal OTS E2E persistence assertion for exact durable player soul state.

It reuses the existing two-session controlled-OTClient lifecycle:

1. the scenario runs through the normal first client session;
2. the client performs the canonical safe logout;
3. Canary persists the player and the runner waits for the existing persistence sentinel;
4. the same controlled client logs in again;
5. phase two reads soul through maintained `LocalPlayer.getSoul()`;
6. the existing post-cycle SQL evaluator verifies the fixed `players.soul` column.

This is an M3 persistence assertion surface. It does not define how a feature earns, spends, regenerates or otherwise changes soul.

## Contract

A persistence check has this exact shape:

```json
{
  "id": "expected-soul",
  "type": "player_soul",
  "equals": 100
}
```

`equals` must be an integer in the inclusive range `0..255`. Booleans, floats, strings, negative values and values above `255` are rejected.

No table, column, predicate, SQL fragment or alternative client getter is caller-selectable.

## Client verification

The phase-two controlled-client plan keeps the typed check as `player_soul` and reads the value with maintained OTClient `LocalPlayer.getSoul()`.

The maintained getter returns an unsigned 8-bit soul value, so the manifest boundary is deliberately restricted to `0..255` rather than accepting the wider SQL column domain.

## Database verification

The compiler emits exactly one semicolon-free scalar query against the fixed Canary column:

```sql
SELECT IF((SELECT `soul` FROM `players` WHERE `name` = '<escaped character>') = <equals>, 1, 0)
```

The character fixture is SQL-escaped by the existing persistence compiler. Callers cannot replace `players`, `soul`, the predicate, or the query shape.

## Reuse and boundaries

Use `player_soul` when a feature already has a deterministic fixture/action that is expected to leave an exact soul value durable across logout and relog.

Do not use it to claim coverage for:

- soul regeneration timing or formulas;
- vocation-specific maximum soul rules;
- spell or item costs that consume soul;
- offline regeneration;
- temporary/protocol display effects not represented by persisted exact soul;
- arbitrary player columns or generic SQL assertions.

Those behaviors require feature-owned scenarios and evidence. This contract only provides the reusable exact client-plus-SQL persistence assertion.

## Reused infrastructure

- `tools/e2e/persistence_assertions.py` validates and compiles the bounded assertion.
- `tools/e2e/client/agent_e2e_scenario.lua` reads maintained `LocalPlayer.getSoul()` after relog.
- `tools/e2e/run_agent_e2e.py` continues to own the existing scenario-plan and two-session lifecycle.

No second E2E runner, workflow, client fork, OTBM parser, route executor or arbitrary SQL surface is introduced.
