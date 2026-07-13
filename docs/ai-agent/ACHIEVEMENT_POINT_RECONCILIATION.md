# Achievement point reconciliation

PR #264 corrects five revision-backed Real Tibia point values and repairs the persisted aggregate for existing characters.

## Corrected definitions

| ID | Achievement | Before | After |
|---:|---|---:|---:|
| 526 | King's Council | 0 | 2 |
| 555 | Inner Peace | 2 | 3 |
| 556 | Fiend Rider | 2 | 3 |
| 559 | Hope of the Merudri | 3 | 2 |
| 562 | Alpha Rider | 2 | 3 |

Source: committed achievement reference catalogue from MediaWiki revision `1188274`, observed 2026-07-13.

## Persistence behavior

`PlayerAchievement::loadUnlockedAchievements()` rebuilds the in-memory unlock list from canonical-name KV entries and then reconciles `achievements/points` against current registry definitions.

The repair:

- changes only the aggregate point key;
- preserves unlock names and timestamps;
- supports upward and downward corrections;
- is idempotent across repeated load/login;
- reconciles an empty unlock set to zero;
- keeps existing `add()` and `remove()` arithmetic valid after reconciliation.

## Unknown historical names

If any stored canonical name cannot be resolved, reconciliation is aborted and the old aggregate is preserved. The unknown key is not removed or renamed. This avoids silently subtracting points whose historical definition is unavailable.

## Safety boundary

No achievement is awarded, removed or backfilled. Names, IDs, grades, secret flags, handlers, quests, maps, items, database schema and client protocol are unchanged.

## Rollback

Reverting the PR restores the previous metadata and load behavior. No schema migration or destructive key rewrite is involved.
