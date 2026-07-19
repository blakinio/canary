# Player skill level persistence

The Universal Physical E2E platform supports a bounded typed persistence assertion for the seven classic durable player skill levels:

```json
{
  "id": "sword-level",
  "type": "player_skill_level",
  "skill": "sword",
  "equals": 90
}
```

Supported `skill` values are exactly:

- `fist`;
- `club`;
- `sword`;
- `axe`;
- `distance`;
- `shielding`;
- `fishing`.

## Contract

Each public skill name maps to one fixed Canary database column and one fixed maintained-OTClient classic skill enum value:

| `skill` | Canary column | OTClient skill id |
|---|---|---:|
| `fist` | `players.skill_fist` | 0 |
| `club` | `players.skill_club` | 1 |
| `sword` | `players.skill_sword` | 2 |
| `axe` | `players.skill_axe` | 3 |
| `distance` | `players.skill_dist` | 4 |
| `shielding` | `players.skill_shielding` | 5 |
| `fishing` | `players.skill_fishing` | 6 |

`equals` must be an exact integer in `0..65535`, matching Canary's uint16 load boundary for classic skill levels.

The assertion participates in the existing two-session persistence lifecycle:

1. the controlled real OTClient completes phase one and logs out safely;
2. the runner waits for server persistence and performs the canonical relog;
3. phase two reads the exact **base** skill level through maintained `LocalPlayer.getSkillBaseLevel(skillId)` and requires equality with `equals`;
4. after the second safe logout, the existing scalar SQL verifier requires the corresponding fixed `players.skill_*` column to equal the same value.

The client check intentionally uses `getSkillBaseLevel`, not `getSkillLevel`. Maintained OTClient keeps received current/effective `level` and `baseLevel` separately for classic skills, so the base value is the stable client-side representation that corresponds to durable database state rather than temporary or equipment-derived bonuses.

## Safety boundary

The typed contract does not accept:

- arbitrary SQL, table names, column names or predicates;
- arbitrary numeric skill IDs;
- `_tries` values or training progress;
- skill percentages;
- loyalty adjustments;
- temporary, equipment or condition bonuses;
- additional skills such as critical hit, life leech, mana leech or elemental modifiers;
- Forge-specific progression;
- skill-gain mechanics or expected progression formulas.

Those surfaces require separate evidence-backed contracts if they become necessary. `player_skill_level` proves only that one exact classic base skill level survives the canonical save/logout/relog cycle and matches final persisted SQL state.

## Ownership boundary

Feature scenarios own the exact skill name and expected level. The shared E2E platform owns validation, the fixed skill-to-column/client-ID mapping, post-relog base-level verification and final SQL compilation. This contract adds no runner, workflow, pathfinder, OTBM parser or feature-specific gameplay logic.
