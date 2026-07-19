# Player magic-level persistence assertion

`player_magic_level` extends the existing `scenario.assertions.persistence` contract with one exact durable progression assertion.

## Contract

```json
{
  "id": "magic-level",
  "type": "player_magic_level",
  "equals": 42
}
```

`equals` must be an integer in `0..65535`. The bound intentionally matches the maintained OTClient `LocalPlayer::getMagicLevel()` `uint16_t` read surface used by the controlled physical client after relog.

The assertion uses two independent checks in the canonical two-session lifecycle:

1. after the first safe logout, persistence sentinel and relog, `agent_e2e_scenario.lua` reads `LocalPlayer:getMagicLevel()` and requires exact equality;
2. after the second safe logout, the existing SQL assertion evaluator requires exact equality against `players.maglevel` for the fixture character.

The SQL compiler is fixed-shape and semicolon-free. Callers cannot choose a table, column, predicate or SQL fragment.

## Evidence boundary

Canary persists `player->magLevel` to `players.maglevel` and restores it during player load. This contract proves that exact durable value only.

It deliberately does **not** claim persistence or equality for:

- `manaspent`;
- magic-level percentage;
- temporary magic-level modifiers;
- `getBaseMagicLevel()` versus effective-value normalization;
- vocation normalization;
- individual combat skills or skill tries.

Those require separately reviewed contracts because their persistence and client-visible semantics differ.

Feature-specific progression actions and expected magic levels remain in feature-owned scenarios. Shared platform fixtures do not invent progression values.
