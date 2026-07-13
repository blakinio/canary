# Achievement metadata parity — non-point repair

> **Repository:** `blakinio/canary`  
> **PR:** #256  
> **Source observed:** 2026-07-13  
> **Reference revision:** TibiaWiki/Fandom MediaWiki `1188274`  
> **Scope:** metadata only; no award conditions, handlers, storages, maps, quests, items or backfill

## Decision

The comprehensive audit in merged PR #238 identified seven metadata conflicts. They cannot safely be repaired as one registry-only patch.

Two fields do not alter persisted achievement point totals and are repaired in PR #256:

| ID | Achievement | Canary before | Real Tibia reference | Repair |
|---:|---|---|---|---|
| 406 | The More the Merrier | grade 1, 0 points, secret | grade 0, 0 points, secret | grade 1 → 0 |
| 513 | Soul Mender | grade 4, 10 points, public | grade 4, 10 points, secret | secret false → true |

Five point corrections are deliberately excluded:

| ID | Achievement | Canary | Reference |
|---:|---|---:|---:|
| 526 | King's Council | 0 | 2 |
| 555 | Inner Peace | 2 | 3 |
| 556 | Fiend Rider | 2 | 3 |
| 559 | Hope of the Merudri | 3 | 2 |
| 562 | Alpha Rider | 2 | 3 |

## Evidence

### Registry before repair

```text
data/scripts/lib/register_achievements.lua
ID 406: grade 1, points 0, secret true
ID 513: grade 4, points 10, secret omitted/default false
ID 526: points 0
ID 555: points 2
ID 556: points 2
ID 559: points 3
ID 562: points 2
```

### Pinned factual catalogue

```text
docs/ai-agent/ACHIEVEMENT_REFERENCE_CATALOG.json
source page: https://tibia.fandom.com/wiki/Achievements
revision: 1188274
observed: 2026-07-13
SHA-256: 8a429425ab7b088758646b07f036afdd1d579188d056491aed8e77650306ae8b
```

The catalogue confirms grade 0 for ID 406 and the five point values. The live `Soul Mender` page confirms ID 513 is secret, grade 4 and worth 10 points.

### Current live-page verification

- `The More the Merrier`: grade 0, 0 points, secret, active historical entry; it is no longer obtainable for new players.
- `Soul Mender`: grade 4, 10 points, secret and active.
- `King's Council`: grade 1, 2 points, common and active; its page records that it became obtainable after Winter Update 2025.
- `Hope of the Merudri`: grade 1, 2 points, common and active.

The remaining point values are retained from the pinned complete table revision and must be rechecked again in the point-reconciliation PR.

## Persistence boundary

`PlayerAchievement` does not derive points from unlocked achievements when loading. It increments and decrements a persisted KV total when achievements are added or removed:

```text
src/creatures/players/components/player_achievement.cpp:35  add current definition points
src/creatures/players/components/player_achievement.cpp:82  read persisted points KV
src/creatures/players/components/player_achievement.cpp:87  increment persisted points KV
src/creatures/players/components/player_achievement.cpp:92  decrement persisted points KV
src/creatures/players/components/player_achievement.cpp:101 load unlocked names without recomputing points
```

Therefore, changing a definition's points alone would correct new unlocks but leave existing characters with stale totals. The five point corrections require a separate design that deterministically recomputes or migrates the point total from canonical unlocked entries, with existing-player and idempotency tests.

## Implemented changes

```text
ID 406: grade 1 -> 0
ID 513: secret false/default -> true
```

No names, IDs, points, conditions, handlers, persistence keys or gameplay paths are changed.

## Regression coverage

`test_confirmed_live_non_point_metadata_matches_reference` parses the real registry and asserts:

```text
406: grade 0, points 0, secret true
513: grade 4, points 10, secret true
```

Materializer validation run `29257442036` passed 14/14 focused tests, Python compilation, the full achievement audit, JSON validation and `git diff --check`. The resulting audit reduced `conflicting` from 31 to 29 while keeping the five point conflicts explicit.

Atomic publication run `29257672213` created commit `b0015325c6bfd4d5db48f7fbeee28da08fd84473` and removed the temporary workflow.

## Follow-up requirement

Create a separate task and PR for achievement point reconciliation. It must:

1. prove all five live point values again;
2. define the authoritative total as the sum of canonical unlocked definitions;
3. reconcile existing player KV totals idempotently;
4. preserve unlock timestamps and canonical-name keys;
5. cover upgrades, downgrades, repeated login, missing definitions and removed achievements;
6. change the five registry point values only together with the reconciliation path and tests.
