# Universal E2E persistence assertion matrix

## Purpose

This document is the canonical feature-neutral inventory of the typed `scenario.assertions.persistence` contract implemented by the Universal Physical E2E platform.

It records what each merged assertion type proves, which evidence surface verifies it, and which stronger feature semantics remain outside the shared platform contract. Feature suites continue to own concrete storage keys, item IDs, expected balances, progression values, vocation expectations, and other gameplay-specific values.

The matrix does not introduce arbitrary SQL, a second E2E lifecycle, feature-specific defaults, or a new persistence assertion type.

## Canonical M3 lifecycle

A persistence-sensitive scenario uses the existing two-session lifecycle:

1. the controlled real OTClient completes the first-session scenario actions;
2. the client performs a safe logout;
3. the harness waits for the existing server-persistence sentinel;
4. the same controlled client logs in again;
5. assertion types with a trustworthy client read surface are re-read and compared in phase two;
6. the client performs the second safe logout;
7. all typed assertions are compiled to fixed-shape scalar SQL and evaluated through the existing post-cycle SQL assertion path.

A client-readable type therefore requires both post-relog client equality and final SQL equality. A database-only type still requires the full successful two-session lifecycle before its final SQL assertion; database-only does not mean a pre-logout database observation is sufficient for M3 evidence.

## Assertion matrix

| Assertion type | Feature-owned input | Controlled-client post-relog verification | Final persisted verification | Evidence boundary |
|---|---|---|---|---|
| `player_field` | `field` = `level` or `experience`; exact non-negative `equals` in `0..9007199254740991` | `LocalPlayer.getLevel()` or `LocalPlayer.getExperience()` | fixed `players.level` or `players.experience` equality for the fixture character | Client + SQL. The shared bound is the exact Lua integer range because the maintained client exposes 64-bit experience to Lua through a numeric conversion; values above `2^53-1` are not accepted for exact phase-two equality. |
| `player_storage` | exact unsigned-32 `key`; exact signed-32 `equals` | none | fixed `player_storage`/`players` joined row existence with exact key and value | Database-only after the full two-session cycle. Generic arbitrary Canary storages have no trustworthy universal controlled-client getter. Quest/UI visibility, when required, is a separate feature-owned assertion. |
| `player_item_presence` | `location` = `inventory`, `depot`, or `inbox`; `item_id` in `1..65535`; strict `present` boolean | none | fixed `EXISTS`/`NOT EXISTS` against `player_items`, `player_depotitems`, or `player_inboxitems` | Database-only after the full two-session cycle. Proves row presence/absence only; it does not prove serialized hierarchy, container placement, or universal quantity semantics. |
| `player_balance` | exact `equals` in `0..9007199254740991` | `LocalPlayer.getResourceBalance(RESOURCE_BANK_BALANCE)` | fixed `players.balance` equality | Client + SQL. The exact Lua integer bound is deliberate even though the database column can represent a wider domain. |
| `player_magic_level` | exact `equals` in `0..65535` | `LocalPlayer.getMagicLevel()` | fixed `players.maglevel` equality | Client + SQL. Does not cover `manaspent`, percentage, temporary modifiers, base/effective normalization, or skill-gain mechanics. |
| `player_soul` | exact `equals` in `0..255` | `LocalPlayer.getSoul()` | fixed `players.soul` equality | Client + SQL. Does not cover regeneration timing, vocation maximums, spell/item costs, or offline-regeneration rules. |
| `player_skill_level` | one classic `skill` name plus exact `equals` in `0..65535` | `LocalPlayer.getSkillBaseLevel(fixedClientSkillId)` | fixed matching `players.skill_*` column equality | Client + SQL. Supports only `fist`, `club`, `sword`, `axe`, `distance`, `shielding`, and `fishing`; excludes tries, percentages, loyalty, temporary bonuses, additional skills, and progression formulas. |
| `player_vocation` | one reviewed semantic `vocation` name | none | fixed mapped Canary server vocation ID in `players.vocation` | Database-only after the full two-session cycle. Physical promotion evidence showed an exact persisted Royal Paladin server vocation while `LocalPlayer.getVocation()` exposed the base-family client value after relog, so the getter is not used as an exact promoted-vocation equality surface. Callers cannot supply raw IDs or custom mappings. |

## Fixed semantic mappings

### Classic skills

| `skill` | Canary column | Controlled-client skill id |
|---|---|---:|
| `fist` | `players.skill_fist` | 0 |
| `club` | `players.skill_club` | 1 |
| `sword` | `players.skill_sword` | 2 |
| `axe` | `players.skill_axe` | 3 |
| `distance` | `players.skill_dist` | 4 |
| `shielding` | `players.skill_shielding` | 5 |
| `fishing` | `players.skill_fishing` | 6 |

### Vocations

| Semantic vocation | Canary server vocation ID | Configured client vocation ID (reference only) |
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

The fixed mappings are owned by `tools/e2e/persistence_assertions.py`. Feature scenarios select semantic values; they do not provide database columns, client IDs, server IDs, predicates, or SQL fragments. The configured client vocation IDs remain a reviewed reference mapping but are not used for exact M3 phase-two vocation equality unless a future independently proven client surface supports that distinction.

## Focused verification inventory

| Surface | Focused test |
|---|---|
| base typed persistence contract and phase-two lifecycle integration | `tests/e2e/test_persistence_assertions.py` |
| exact Lua-safe `player_field` client equality boundary | `tests/e2e/test_player_field_persistence_precision.py` |
| `player_storage` | `tests/e2e/test_player_storage_persistence.py` |
| `player_item_presence` across inventory/depot/inbox | `tests/e2e/test_player_item_persistence.py` |
| `player_balance` | `tests/e2e/test_player_balance_persistence.py` |
| `player_magic_level` | `tests/e2e/test_player_magic_level_persistence.py` |
| `player_soul` | `tests/e2e/test_player_soul_persistence.py` |
| `player_skill_level` | `tests/e2e/test_player_skill_level_persistence.py` |
| `player_vocation` | `tests/e2e/test_player_vocation_persistence.py` |

The implementation contract is centralized in `tools/e2e/persistence_assertions.py`; `tools/e2e/run_agent_e2e.py` materializes only assertion types with trustworthy client-readable checks into the phase-two plan and compiles every typed assertion to final SQL; `tools/e2e/client/agent_e2e_scenario.lua` executes client-readable checks only after the second physical login.

## Safety and ownership boundaries

- `scenario.assertions.persistence.required` is explicit; checks are not accepted when persistence is declared false, and a required persistence declaration cannot be empty.
- A scenario may declare at most 32 typed persistence checks.
- Unknown assertion types and unknown type-specific fields fail validation.
- The typed contract never accepts caller-selected table names, columns, predicates, or SQL fragments.
- `player_storage`, `player_item_presence`, and `player_vocation` must not be presented as directly client-verified exact generic state under the current evidence boundary.
- A successful SQL assertion before the canonical logout/relog cycle is not M3 persistence proof.
- Feature suites own the action that changes state and the exact expected gameplay values. Shared platform documentation and fixtures must not invent quest storages, item IDs, balances, progression values, or feature outcomes.
- A typed persistence assertion proves only its bounded durable value or row predicate. It does not prove the gameplay mechanic that produced that state unless the feature scenario separately performs and verifies that mechanic.

## E2E-GAMEPLAY-005 closure

The merged typed persistence surface covers the programme priority domains with eight bounded assertion types:

- storages and quest progression through `player_storage`, with feature-owned client/UI assertions when a quest requires visible proof;
- inventory, depot, and inbox row presence through `player_item_presence`;
- bank/economy state through `player_balance`;
- durable player progression through `player_field`, `player_magic_level`, `player_soul`, `player_skill_level`, and normalized `player_vocation`.

The closure audit found one reusable correctness gap in the pre-existing `player_field` contract: client-verified 64-bit experience expectations were accepted beyond the range where the maintained Lua numeric bridge guarantees exact integer equality. The contract now reuses the existing `MAX_SAFE_LUA_INTEGER` boundary already used by `player_balance`, and a focused regression test covers that boundary. Later physical promotion evidence also corrected the `player_vocation` evidence boundary: semantic server-vocation equality remains exact after the full M3 cycle, while promoted-vocation equality is no longer inferred from `LocalPlayer.getVocation()`.

No additional persistence assertion type is required to close the declared `E2E-GAMEPLAY-005` matrix. New durable domains should be added only when a concrete feature requires a reusable assertion surface and the client/database semantics are independently evidence-backed.
