# Achievement helper repair — sparse enumeration and secret lookup

## Status

```text
PR: #176
branch: fix/achievement-helper-enumeration
scope: Lua helper layer only
registry definitions changed: no
player KV format changed: no
```

This repair implements the first remediation stage from the merged achievement audit in PR #165.

## Confirmed problems

### Sparse-table length

`ACHIEVEMENTS` contains explicit numeric gaps, but the previous helper layer used:

```lua
ACHIEVEMENT_LAST = #ACHIEVEMENTS
```

and enumerated unlocked achievements through `1..#ACHIEVEMENTS`. Lua does not define a useful length boundary for a sparse table, so registered high IDs and helper enumeration could diverge.

### Secret metadata lookup

`Game.isAchievementSecret` resolved `foundAchievement` but returned `achievement.secret` from the input argument. Its invalid path also referenced undefined variable `ach`.

## Implemented behavior

The helper now:

1. collects every numeric registry key;
2. sorts the keys in ascending order;
3. validates and registers definitions in that order;
4. records only successfully registered IDs;
5. derives `ACHIEVEMENT_FIRST` and `ACHIEVEMENT_LAST` from that explicit list;
6. reuses the same list for unlocked, public, secret, bulk-add and bulk-remove enumeration;
7. resolves public/secret metadata by ID or exact name;
8. logs the supplied invalid identifier with `logger.error` and returns `false`.

Registration validation uses structured `if/elseif/else` flow rather than Lua labels. This preserves the skip-invalid behavior while remaining compatible with the repository's default StyLua parser configuration.

Output ordering becomes deterministic ascending ID. Public function signatures remain unchanged.

## Compatibility boundary

Unchanged:

- every achievement ID, name, description, grade, points and secret flag;
- active award/progress triggers;
- C++ registry and protocol code;
- player achievement KV keys and timestamps;
- map, assets, database and production configuration.

The repair deliberately does not address the two broken literal trigger names identified by the audit; those remain a separate focused PR.

## Focused test

```text
tests/lua/test_achievement_helpers.lua
```

The real registry source is loaded with minimal runtime stubs. The test verifies:

- every numeric definition is registered;
- first/last constants match actual sorted IDs;
- unlocked enumeration crosses sparse gaps and includes the highest ID;
- bulk add/remove visits every registered ID exactly once in ascending order;
- public and secret filters preserve deterministic ordering;
- secret lookup works by ID and name;
- invalid ID and invalid name log the supplied value and return false.

## Static audit result

The post-change `Achievement Validation` artifact contains no:

- `sparse-table-length-operator`;
- `secret-helper-returns-input`;
- `secret-helper-undefined-error-variable`.

The two unrelated invalid static trigger names and external baseline mismatch remain intentionally visible.

## Rollback

Revert PR #176. No data migration or cleanup is required because persistence formats and registry definitions are unchanged.
