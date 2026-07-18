# OAM-015 — Weapons Revalidation

Status: **target proof in progress**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-015`

## Immutable task-start baselines

```text
legacy/governance Canary: blakinio/canary@051f4101cac5250dd41d8aa0914fcc8761b08d64
target Otheryn: blakinio/Otheryn@9d797b547c3f85f6d210c6123202c7cae32d5133
upstream evidence: opentibiabr/canary@691614c1a302aee776002ca3851eca399be1a82c
maintained OTClient: blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

All four live heads were refreshed at task start.

## Canonical module and provisional disposition

```text
weapons → REUSE (pending exact-target proof)
```

Registry boundary:

- server: `src/items/weapons/**`
- data: `data/scripts/weapons/**`
- hard dependency: `combat`
- dependency status: completed by OAM-013
- interactions: character progression, combat conditions, spells, vocations and Weapon Proficiency

The canonical boundary owns weapon registry/script registration, wield/use checks, melee/distance/wand implementations, damage/element surfaces, resource/charge/break/item-count consumption and combat/proficiency handoff discovery. Generic combat policy, spell/rune registration, item economy/market, protocol serialization, client UI and Real Tibia formula parity remain outside this package.

## Fresh live-state/open-PR preflight

At task start:

- no open Otheryn PR existed;
- Canary PR #514 owns authenticated-session security validation infrastructure only;
- Canary PR #525 owns the physical teleport E2E scenario only;
- Canary PR #526 owns shared-state/economy security-audit documentation only;
- none of the open Canary PRs changes `src/items/weapons/**` or `data/scripts/weapons/**`.

No overlapping open PR was identified for the canonical OAM-015 weapons production boundary.

## Whole-boundary target/upstream provenance

OAM-002 bootstrap PR #1 established the target from exact pinned upstream Canary content rather than importing legacy runtime history. OAM-002 post-merge verification then proved final target `3cc7c1dfea747bb380f3761ee7ff7ac30141a115` differed from pinned upstream `a879c9312e34381e8eedf397b8ed44510698b689` only in the target CI workflow delta plus the temporary verifier. Therefore the canonical `src/items/weapons/**` and `data/scripts/weapons/**` production boundary started upstream-exact.

Subsequent target history from `3cc7c1dfea747bb380f3761ee7ff7ac30141a115` through task-start `9d797b547c3f85f6d210c6123202c7cae32d5133` changes no canonical weapons production path. Subsequent upstream history from `a879c9312e34381e8eedf397b8ed44510698b689` through pinned `691614c1a302aee776002ca3851eca399be1a82c` changes only Windows workflow/network/server-definition paths, not the weapons boundary.

Task-start target and pinned latest upstream therefore retain the same canonical weapons production boundary. Representative exact runtime blobs are:

```text
src/items/weapons/weapons.cpp
4094a124e42263047b81a459d93b187aeca25c7f

src/items/weapons/weapons.hpp
093c58aef02b4f2ea44b21796ba697ca0a2e7add
```

This provenance is stronger than file-presence identity alone: the initial whole-tree bootstrap delta and all later target/upstream production changes were bounded before selecting `REUSE`.

## Reviewed legacy history: PR #78 wand/Cyclopedia fix

Task-start legacy Canary has:

```text
src/items/weapons/weapons.cpp
ba3bc8f564601993780c15ac532b52b433f33944

src/items/weapons/weapons.hpp
093c58aef02b4f2ea44b21796ba697ca0a2e7add
```

The `weapons.cpp` difference has concrete provenance and must not be interpreted as an isolated legacy improvement. Merged Canary PR #78 (`8e6fa1a89dde40e9d832391c06a49bd30af31541`) addresses upstream issue #3645 with one coordinated wand/Cyclopedia display-stat fix spanning:

```text
src/items/functions/item/item_parse.cpp
src/items/weapons/weapons.cpp
src/server/network/protocol/protocolgame.cpp
```

The wand-specific PR #78 behavior:

1. publishes wand combat type and a nonzero display attack value while parsing the item/weapon definition;
2. removes the two `const_cast<ItemType &>` metadata writes from `WeaponWand::configureWeapon` only after that publication is moved to item parsing;
3. changes character/Cyclopedia packet attack fields to calculated wand attack totals and bonuses;
4. explicitly does **not** alter the actual wand damage roll.

Upstream issue #3645 remains open and describes zero/null wand attack display as a client-debug/crash risk, so this is a real unresolved cross-module compatibility gap rather than evidence to dismiss. However, importing only PR #78's `weapons.cpp` deletion would split a coherent fix. Importing its item-definition and protocol portions in OAM-015 would reopen already completed canonical ownership from OAM-007 and OAM-006 and would change a user-visible protocol/display contract without dedicated exact-target physical proof.

Therefore OAM-015 does **not** partially migrate PR #78. It retains the upstream-aligned canonical weapons runtime/data boundary and records the PR #78 wand-display issue as a separate unresolved cross-module `item-definitions`/`weapons`/`protocol` compatibility gap. This package makes no wand/Cyclopedia display-parity claim.

Searches for other visible delivered legacy history using `getMaxWeaponDamage`, `playerWeaponCheck`, `REMOVE_WEAPON_AMMO` and `WeaponDistance` identified no second weapons-runtime donor requiring coupling into OAM-015.

TSD-005 remains discovery evidence only and explicitly does not prove weapon formula, hit-chance, resource-consumption or Real Tibia parity.

## Target proof

Otheryn issue:

```text
#36 — OAM-015: prove reusable weapons core
```

Otheryn target PR:

```text
#37 — test(weapons): prove OAM-015 reused weapons core
```

The target package is proof-only. Its accepted scope is limited to:

```text
tests/unit/items/CMakeLists.txt
tests/unit/items/weapon_reuse_test.cpp
```

Focused `WeaponReuseTest` coverage is runtime-only:

1. stable maximum melee damage helper behavior;
2. stable melee/ranged `getMaxWeaponDamage` behavior, including zero melee attack value;
3. deterministic configured maximum wand damage;
4. zero separate wand element-damage value.

An earlier draft assertion that treated target/upstream wand ItemType metadata publication as correctness evidence was deliberately removed after PR #78 provenance review. OAM-015 does not freeze the unresolved display implementation as a parity invariant.

No production `src/items/weapons/**`, `data/scripts/weapons/**`, item-definition or protocol mutation is authorized by the final OAM-015 evidence boundary.

## Boundary classification

| Boundary | Current classification | Evidence-backed result |
|---|---|---|
| ownership/lifecycle | applicable | canonical `weapons` runtime/data retained; generic combat remains completed OAM-013 |
| build/toolchain | compatible | existing Otheryn C++ unit-test harness reused |
| configuration | no change | no configuration mutation |
| service/API | retain target/upstream | current weapons runtime substrate retained pending proof |
| scheduling/concurrency | no change | no scheduler/concurrency mutation |
| persistence | no change | no new persistence boundary |
| protocol/session | known external gap, no OAM-015 change | PR #78 wand display integration is recorded but not partially migrated |
| identifiers/assets | no change | no identifier/asset migration |
| world/map | no change | no world/map mutation |
| runtime | pending exact-target proof | full target build/runtime smoke required |
| tests | pending | focused `WeaponReuseTest` plus full target CTest required |
| physical-client E2E | not claimed | no OAM-015 protocol/client mutation; PR #78 gap remains unproven on exact target |
| operations | bounded | exact-head CI/review/drift/merge gates required |
| security/privacy | no new boundary | no credential/privacy/security flow mutation |

## Explicit exclusions

OAM-015 does **not** claim or add:

- exhaustive weapon damage or hit-chance parity;
- Real Tibia melee/distance/wand formula parity;
- exhaustive resource, charge, break or ammunition-consumption parity;
- individual weapon-script parity across the entire datapack;
- wand/Cyclopedia display-stat compatibility or client-crash closure for upstream issue #3645;
- partial migration of the cross-module PR #78 fix;
- generic combat policy changes;
- spell/rune migration;
- vocation or Weapon Proficiency redesign;
- protocol/client/map/asset changes;
- persistence redesign or SQL/KV atomicity.

OAM-004 SQL/KV non-atomicity and completed OAM-006/OAM-007/OAM-013/OAM-014 ownership remain authoritative.

## Completion gate

The provisional `weapons → REUSE` disposition becomes final only after:

1. proof-only target PR exact-head CI/Required/autofix and full CTest pass;
2. focused `WeaponReuseTest` passes;
3. target comments/reviews/threads are clean and target-main drift is checked;
4. target proof PR merges with exact-head protection;
5. this Canary governance task is updated with exact proof and passes its own exact-head gates;
6. separate lifecycle archive and durable program reconciliation merge;
7. any automatically opened `docs(agents): archive merged PR` owned by this workflow is explicitly closed after it has served its purpose, so no stale self-owned archive PR remains open.

OAM-016 must remain NOT STARTED until the full OAM-015 sequence completes.
