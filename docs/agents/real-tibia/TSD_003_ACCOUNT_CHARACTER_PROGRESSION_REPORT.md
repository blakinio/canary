# TSD-003 — Account, Character and Progression Decomposition

> Status: bounded inventory for `blakinio/canary`.
> Task-start main: `661d55085b6a2ad5e930ae3186aa63ba052b665e`.
> Integration refresh main: `84fefca166af37c6995edccc50d2fc522aa219c6`.
> This report is decision evidence for the canonical registry. It does not prove Real Tibia parity, runtime behavior, persistence safety, authentication security or client compatibility.

## Result

TSD-003 inventories account, authentication, character and progression boundaries without changing runtime code or replacing the existing broad `player-persistence`, `protocol`, `achievements` and `wheel-of-destiny` records.

- Registry records before: **29**.
- New records: **6**.
- Registry records after: **35**.
- Existing module records modified: **0**.
- Category/schema/generator/mapper/workflow changes: **none**.
- Runtime/gameplay/database/protocol/client/map/asset changes: **none**.

Records added:

1. `account-lifecycle`;
2. `account-authentication`;
3. `character-lifecycle`;
4. `character-progression`;
5. `vocations`;
6. `weapon-proficiency`.

## Preflight and concurrent work

The task started from `main@661d55085b6a2ad5e930ae3186aa63ba052b665e`. Before final shared-document integration, `main` advanced through unrelated or read-only-reviewed work to `84fefca166af37c6995edccc50d2fc522aa219c6`.

| PR / merge | Area | TSD-003 treatment |
|---|---|---|
| #350 / `f97c9fe0422718028c7ca50224e350ad846fd393` | Equipment Upgrade lifecycle archive | no overlapping source or registry path |
| #352 / `b0d7583fcfb443359feba3f0639e2c52e112ecf9` | multichannel documentation and `MODULE_CATALOG.md` | preserve the merged handoff/DB-row-handoff catalogue content during final integration |
| #339 / `06286302ae429e6ba05a152e3b171b7a43046a0c` | exact game-session disconnect cleanup | implementation is current-main inventory evidence only; no runtime/session correctness claim and no source edit |
| #351 / `2b9729a1bcfac4551456431cfc4f4ac9f2a63cfa` | The Beginning lifecycle archive | no overlapping Real Tibia registry path |
| #357 / `84fefca166af37c6995edccc50d2fc522aa219c6` | cross-process DB-row-handoff lifecycle archive | no module/runtime edit; current catalogue contract preserved |
| #316 | Targuna map/content evidence | read-only; no map, OTBM or content edit |
| #245 | shared physical-client E2E platform | read-only; no scenario or orchestrator change |

The six registry records, generated indexes and focused tests do not depend on the intervening lifecycle-document changes. The merged #339 implementation changed session/protocol runtime paths but did not alter the account repository, IOLoginData, Player progression, vocation or Weapon Proficiency discovery roots selected by this package. `ACTIVE_WORK.md` remains read-only.

## Current-main evidence inventory

### Account lifecycle

`src/account/CMakeLists.txt` compiles `account.cpp`, `account_repository.cpp` and `account_repository_db.cpp` as one account repository boundary.

`AccountInfo` stores account identity, premium state, account type, character roster, protocol compatibility, session expiry, creation time and house-bid state. `Account` owns load/reload/save, roster lookup, premium/account-type state, credential verification and coin operations.

The directory is therefore a durable account lifecycle boundary, but its coin methods do not authorize this package to absorb economy ownership. Coin balances and transaction policy remain for TSD-007.

### Account authentication

Authentication has an independent security lifecycle spanning:

- password verification through Argon/SHA compatibility;
- account session-expiry validation;
- `LoginSessionManager` issuance and single-use consumption of short-lived tokens bound to account, allowed character names and protocol profile;
- `IOLoginData::gameWorldAuthentication` ownership/deletion checks and authenticated account handoff.

The record excludes wire framing and protocol-version negotiation. PR #339 is now merged and its code is current-main inventory evidence for gameplay-session cleanup, but neither its PR claims nor passing tests prove the broader authentication/session safety dimensions excluded by TSD-003. Existing token tests are evidence pointers only and do not prove complete production authentication security.

### Character lifecycle

`IOLoginData` separates:

- account/character world authentication;
- player load by ID or name;
- always-loaded state;
- online-only component initialization;
- player save and online-only component save;
- save guards and character-name/GUID lookup.

`Player` is the runtime character object, but TSD-003 does not treat every method or component as a module. `character-lifecycle` uses the narrow Player and IOLoginData paths to discover authenticated ownership, load/save, online/offline initialization and logout/reload boundaries.

The record overlaps `player-persistence` intentionally. It does not replace that stable broad persistence identity and does not claim save atomicity, completeness or crash recovery.

### Character progression

Player contains shared level/experience, skill/magic-level, stamina/experience boost, offline-training and death/loss-related state and advancement hooks. The load/save split serializes that shared progression state.

Those capabilities share one character lifecycle and one large Player persistence surface. Separate records for each numeric field or formula would create false ownership granularity. TSD-003 therefore adds one `character-progression` compatibility/discovery umbrella and keeps formulas and states as findings inside it.

### Vocations

`Vocation` and `Vocations` provide a stable independent registry with:

- XML load/reload;
- base/promoted vocation relationships;
- skill and mana requirement caches;
- health, mana, capacity, speed, soul and regeneration growth parameters;
- mitigation and PvP multiplier configuration;
- one shared lifecycle for all vocation entries.

Per-vocation records remain rejected or merged because Knight, Paladin, Sorcerer, Druid and Monk variants are data entries inside the same registry and configuration contract.

### Weapon Proficiency

Weapon Proficiency has a durable independent component:

- JSON definition loading from `data/items/proficiencies.json`;
- per-weapon experience, levels, selected perks and mastery;
- normalized player-KV load/save;
- combat and skill integration;
- mastery achievement reconciliation;
- focused unit/audit evidence.

It therefore receives its own record. Existing tests and audits remain linked, but the new decomposition record starts at inventory/not-assessed and does not promote formula, persistence, runtime or E2E maturity.

## Candidate decisions

| Candidate | Decision | Result / reason |
|---|---|---|
| `account-lifecycle` | `ADD_NOW` | durable account identity, roster, repository and account-status lifecycle |
| `account-authentication` | `ADD_NOW` | independent credential/session/token issue-consume lifecycle |
| `account-entitlements` | `MERGE_WITH_ANOTHER_MODULE` | premium/account-type state remains an account-lifecycle capability; no separate stable implementation root |
| `premium-status` | `MERGE_WITH_ANOTHER_MODULE` | account-lifecycle capability |
| `account-sanctions` | `DEFER_TO_NEXT_PACKAGE` | moderation/ban/audit belongs to TSD-009 trust and safety inventory |
| `account-wide-storage` | `DEFER_TO_NEXT_PACKAGE` | no generic account-wide storage subsystem; existing account-wide quest access remains quest-specific |
| `character-lifecycle` | `ADD_NOW` | authenticated ownership plus load/save and online/offline initialization lifecycle |
| `character-creation` | `MERGE_WITH_ANOTHER_MODULE` | lifecycle step; current server inventory does not prove a separate creation subsystem |
| `character-login-load` | `MERGE_WITH_ANOTHER_MODULE` | character-lifecycle capability |
| `character-save` | `MERGE_WITH_ANOTHER_MODULE` | character-lifecycle and player-persistence capability |
| `character-logout` | `MERGE_WITH_ANOTHER_MODULE` | character-lifecycle capability; merged #339 remains protocol/session implementation evidence, not a standalone module |
| `character-reconnect` | `MERGE_WITH_ANOTHER_MODULE` | character/protocol lifecycle capability, not a standalone module |
| `character-deletion` | `MERGE_WITH_ANOTHER_MODULE` | ownership/deletion-state check inside character lifecycle; no separate implementation root |
| `character-progression` | `ADD_NOW` | compatibility umbrella for shared Player progression state |
| `levels-experience` | `MERGE_WITH_ANOTHER_MODULE` | character-progression finding |
| `skills-training` | `MERGE_WITH_ANOTHER_MODULE` | character-progression finding |
| `magic-level` | `MERGE_WITH_ANOTHER_MODULE` | character-progression finding |
| `stamina` | `MERGE_WITH_ANOTHER_MODULE` | character-progression finding |
| `offline-training` | `MERGE_WITH_ANOTHER_MODULE` | character-progression finding |
| `death-loss` | `MERGE_WITH_ANOTHER_MODULE` | progression consequence spanning Player, persistence and combat; no narrow standalone root |
| `blessings` | `MERGE_WITH_ANOTHER_MODULE` | death/loss progression capability pending a future evidence package |
| `vocations` | `ADD_NOW` | independent registry, promotion relation and XML configuration lifecycle |
| `promotion` | `MERGE_WITH_ANOTHER_MODULE` | relation inside the vocation registry |
| `vocation-knight` | `REJECT_AS_TOO_GRANULAR` | one entry in the shared vocation lifecycle |
| `vocation-paladin` | `REJECT_AS_TOO_GRANULAR` | one entry in the shared vocation lifecycle |
| `vocation-sorcerer` | `REJECT_AS_TOO_GRANULAR` | one entry in the shared vocation lifecycle |
| `vocation-druid` | `REJECT_AS_TOO_GRANULAR` | one entry in the shared vocation lifecycle |
| `vocation-monk` | `MERGE_WITH_ANOTHER_MODULE` | entry/capabilities inside `vocations`; combat-specific monk systems remain TSD-005 |
| `monk-harmony` | `MERGE_WITH_ANOTHER_MODULE` | vocation/combat finding, not separate registry ownership |
| `monk-virtues` | `MERGE_WITH_ANOTHER_MODULE` | vocation/combat finding, not separate registry ownership |
| `weapon-proficiency` | `ADD_NOW` | independent definition, progression, perk, persistence and validation lifecycle |
| `wheel-of-destiny` | `ALREADY_COVERED` | preserve existing record and program |
| `gem-atelier` | `MERGE_WITH_ANOTHER_MODULE` | Wheel of Destiny capability |
| `achievements` | `ALREADY_COVERED` | preserve existing record and evidence model |
| `titles` | `DEFER_TO_NEXT_PACKAGE` | component exists, but its Cyclopedia/client/unlock boundary is better classified with TSD-004/TSD-010 |
| `loyalty` | `MERGE_WITH_ANOTHER_MODULE` | progression/account capability in Player without an independent implementation root |
| `outfits` | `DEFER_TO_NEXT_PACKAGE` | appearance definition/unlock/client boundary requires a dedicated later inventory |
| `mounts` | `DEFER_TO_NEXT_PACKAGE` | appearance definition/unlock/client boundary requires a dedicated later inventory |
| `familiars` | `DEFER_TO_NEXT_PACKAGE` | appearance/vocation/client boundary requires a dedicated later inventory |
| `podiums-displays` | `MERGE_WITH_ANOTHER_MODULE` | appearance presentation capability, not a standalone lifecycle |

## Relationships

Only fundamental dependencies are encoded:

- `account-lifecycle` depends on `database-connection`;
- `account-authentication` depends on `account-lifecycle`;
- `character-lifecycle` depends on `account-authentication` and `player-persistence`;
- `character-progression` depends on `character-lifecycle` and `player-persistence`;
- `weapon-proficiency` depends on `character-progression` and `player-persistence`;
- `vocations` has no `depends_on` edge.

All other links are descriptive `interacts_with`. The graph remains acyclic.

## Maturity

All six records start with:

```text
lifecycle: inventory
implementation: inventory
evidence: inventory
persistence: not-assessed
protocol: not-assessed
automated_tests: not-assessed
runtime_validation: not-assessed
gameplay_e2e: not-assessed
```

This remains true even where existing unit tests, audits or merged feature work are referenced. The decomposition package inventories boundaries; it does not inherit proof automatically.

## Discovery boundaries

- All new server paths are verified and narrower than broad `src/**`.
- Overlap with `player-persistence` and `protocol` is expected and does not transfer ownership.
- Server source-role mapping includes the new records.
- Client-only source buckets do not receive server-only account/character/progression records.
- Unmapped paths remain explicit and reviewed decisions remain unchanged.
- `affected` and `lookup-path` output stays deterministic.

Representative verified lookups:

```text
src/account/account.cpp
  → account-lifecycle
  → account-authentication
  → no server-side protocol false-positive

src/security/login_session_manager.cpp
  → account-authentication

src/io/iologindata.cpp
  → account-authentication
  → character-lifecycle
  → player-persistence

src/creatures/players/player.cpp
  → character-lifecycle
  → character-progression
  → player-persistence
  → existing broad feature records where their path hints intentionally overlap

src/creatures/players/vocations/vocation.cpp
  → vocations
  → player-persistence through its existing broad umbrella

src/creatures/players/components/weapon_proficiency.cpp
  → weapon-proficiency
  → character-progression
  → player-persistence
```

## Validation history

Implementation/focused-test head `3eb7ae24bb1b918a0b040270e58c49037a873ee8`:

- Real Tibia Module Registry #191: success;
- Upstream Intelligence #219: success;
- Agent Task Ownership #1058: success;
- repository CI #2170: success;
- focused registry and source-role mapping tests: success;
- schema and dependency validation: success;
- deterministic `generate --check`: success;
- module, lookup-path, stale and exact PR-range affected commands: success.

Later program, catalogue, changelog, report and task-record commits are documentation-only. Final exact-head and ready-state checks remain authoritative before merge.

## Evidence limits

TSD-003 does **not** prove:

- credential confidentiality or resistance to all authentication attacks;
- token randomness, replay safety or concurrency correctness beyond existing source/tests;
- protocol or maintained-client compatibility;
- game-session cleanup or replacement-session safety, including behavior beyond the bounded merged #339 regression;
- player save atomicity, completeness, rollback or crash consistency;
- account entitlement, premium or coin correctness;
- experience, skill, stamina, offline-training, death-loss or blessing parity;
- vocation growth/formula parity;
- Weapon Proficiency definition/perk/formula parity;
- production runtime behavior;
- physical-client E2E;
- Oteryn migration readiness.

## Next package

After feature merge and a separate lifecycle archive, TSD-004 must start from then-current `main`:

```text
task: CAN-20260714-tibia-system-decomposition-cyclopedia-family
package: TSD-004
branch: docs/tibia-system-decomposition-cyclopedia-family
```

TSD-004 should preserve the `cyclopedia` umbrella and evaluate durable children such as items, bestiary, bosstiary, character, map and house surfaces without duplicating `charms`, `achievements`, titles/appearance or protocol ownership.
