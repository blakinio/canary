# Player vocation persistence assertion

## Purpose

`player_vocation` is a bounded Universal OTS E2E persistence assertion for durable player vocation state.

The contract deliberately separates the two identifier domains used by the maintained stack:

- Canary persists the server vocation ID in `players.vocation`;
- the maintained OTClient exposes the client-facing vocation ID through `LocalPlayer.getVocation()`.

A scenario supplies only one reviewed semantic vocation name. The persistence compiler owns both fixed numeric mappings. The caller cannot provide SQL columns or numeric server/client vocation IDs.

## Scenario contract

```json
{
  "assertions": {
    "persistence": {
      "required": true,
      "checks": [
        {
          "id": "vocation",
          "type": "player_vocation",
          "vocation": "knight"
        }
      ]
    }
  }
}
```

Allowed fields are exactly:

- `id`;
- `type` = `player_vocation`;
- `vocation` = one supported semantic name.

## Fixed mapping

| Semantic vocation | Canary `players.vocation` | Maintained OTClient vocation ID |
|---|---:|---:|
| `none` | 0 | 0 |
| `sorcerer` | 1 | 3 |
| `druid` | 2 | 4 |
| `paladin` | 3 | 2 |
| `knight` | 4 | 1 |
| `master_sorcerer` | 5 | 13 |
| `elder_druid` | 6 | 14 |
| `royal_paladin` | 7 | 12 |
| `elite_knight` | 8 | 11 |
| `monk` | 9 | 5 |
| `exalted_monk` | 10 | 15 |

These values are fixed inside `tools/e2e/persistence_assertions.py`. They mirror the maintained Canary vocation `id`/`clientid` contract and the maintained OTClient server/client vocation constants.

## Verification lifecycle

The assertion reuses the canonical Universal Agent E2E two-session lifecycle:

1. the first controlled-client session runs the declared scenario;
2. the client performs a safe logout;
3. the harness waits for server persistence;
4. the controlled client logs in again;
5. the `player_vocation` assertion is normalized into the existing runtime `player_field` check for `vocation` with the fixed client vocation ID;
6. the existing controlled-client driver reads `LocalPlayer.getVocation()` and requires exact equality;
7. after the full cycle, the normal scalar SQL evaluator checks the fixed `players.vocation` column against the fixed server vocation ID.

The runtime plan therefore never compares a Canary server vocation ID directly with the client-facing vocation ID.

## Safety boundary

The contract does not expose:

- arbitrary numeric server vocation IDs;
- arbitrary numeric client vocation IDs;
- caller-selected SQL columns or tables;
- raw `player_field` access to `vocation`;
- custom or dynamically registered vocations.

Unsupported semantic names fail validation instead of being interpreted or guessed.

## Out of scope

This assertion proves only the durable normalized vocation identity across logout and relog. It does not prove:

- vocation selection, promotion or demotion mechanics;
- NPC dialogue or payment requirements for vocation changes;
- custom vocation definitions outside the fixed maintained mapping;
- vocation-dependent formulas, skills, spells, regeneration, capacity or combat behavior;
- historical migration correctness for previously persisted values.

Those require separate feature-owned scenarios or contracts.
