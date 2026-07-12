# Achievement trigger name repair

## Scope

PR #184 corrects the two literal achievement names that failed exact runtime lookup in the merged achievement audit.

| Active path | Previous literal | Canonical registry entry |
|---|---|---|
| `data/scripts/actions/items/usable_phantasmal_jade_items.lua` | `You got Horse Power` | ID 514 — `You Got Horse Power` |
| `data-otservbr-global/scripts/quests/hero_of_rathleton/actions_reward.lua` | `The Professors Nut` | ID 360 — `The Professor's Nut` |

## Why this is a runtime defect

Achievement names are registered in a `std::map<std::string, uint16_t>` and looked up using exact `find(name)`. Case and punctuation differences therefore do not resolve to the canonical definitions.

The correction belongs in the call sites. Renaming registry entries would be unsafe because unlocked achievement persistence is keyed by canonical name.

## Behavior after the fix

- Completing the phantasmal jade item sequence continues to grant mount `167`, `Natural Born Cowboy`, and now also resolves `You Got Horse Power`.
- Opening the eligible Hero of Rathleton reward chest continues to grant the same items and storage `24850`, and now resolves `The Professor's Nut`.
- Existing duplicate-award/idempotence behavior remains in the Player achievement API.

## Compatibility boundary

Unchanged:

- achievement registry IDs and names;
- descriptions, grades, points and secrecy;
- required phantasmal item IDs/counts and KV keys;
- mount ID `167`;
- Hero of Rathleton reward items and storage `24850`;
- C++ runtime and player KV format;
- map, assets, database and production configuration.

## Regression contract

`tools/ai-agent/test_achievement_validation.py` loads the real registry and both active source files, verifies the canonical award names are present, and asserts every static achievement reference in those files resolves.

The complete `Achievement Validation` artifact must report:

```text
unknownStaticReferenceCount: 0
```

Baseline metadata differences and unresolved dynamic references remain separate audit work.

## Rollback

Revert PR #184. No data migration or cleanup is required.
