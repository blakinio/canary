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

The canonical boundary owns weapon registry/script registration, wield/use checks, melee/distance/wand implementations, damage/element surfaces, resource/charge/break/item-count consumption and combat/proficiency handoff discovery. Generic combat policy, spell/rune registration, item economy/market, client UI and Real Tibia formula parity remain outside this package.

## Fresh live-state/open-PR preflight

At task start:

- no open Otheryn PR existed;
- Canary PR #514 owns authenticated-session security validation infrastructure only;
- Canary PR #525 owns the physical teleport E2E scenario only;
- Canary PR #526 owns shared-state/economy security-audit documentation only;
- none of the open Canary PRs changes `src/items/weapons/**` or `data/scripts/weapons/**`.

No overlapping open PR was identified for the canonical OAM-015 weapons boundary.

## Exact target/upstream/legacy evidence

Task-start target and latest upstream share exact runtime blobs:

```text
src/items/weapons/weapons.cpp
4094a124e42263047b81a459d93b187aeca25c7f

src/items/weapons/weapons.hpp
093c58aef02b4f2ea44b21796ba697ca0a2e7add
```

Task-start legacy Canary has:

```text
src/items/weapons/weapons.cpp
ba3bc8f564601993780c15ac532b52b433f33944

src/items/weapons/weapons.hpp
093c58aef02b4f2ea44b21796ba697ca0a2e7add
```

The reviewed runtime difference is not a target defect. Legacy omits two current upstream/target statements in `WeaponWand::configureWeapon` that publish wand metadata into `ItemType`:

```cpp
const_cast<ItemType &>(it).combatType = params.combatType;
const_cast<ItemType &>(it).maxHitChance = (minChange + maxChange) / 2;
```

Therefore legacy is not accepted as a stronger whole-module runtime donor. File identity alone is not treated as sufficient for `REUSE`; the proof package must exercise stable weapon formula helpers and the wand metadata behavior that distinguishes the retained target/upstream implementation from legacy.

Reviewed visible legacy PR history found no delivered `src/items/weapons/**` runtime repair requiring migration. TSD-005 remains discovery evidence only and explicitly does not prove weapon formula, hit-chance, resource-consumption or Real Tibia parity.

## Target proof plan

Otheryn issue:

```text
#36 — OAM-015: prove reusable weapons core
```

The target package is proof-only unless new evidence isolates a defect. Planned focused assertions:

1. stable melee maximum-damage helper behavior;
2. stable melee/ranged `getMaxWeaponDamage` behavior, including zero melee attack value;
3. `WeaponWand::configureWeapon` publishes average wand hit metadata into `ItemType`, preserving the current target/upstream behavior absent from legacy.

No production `src/items/weapons/**` or `data/scripts/weapons/**` mutation is authorized by the current evidence.

## Boundary classification

| Boundary | Current classification | Evidence-backed result |
|---|---|---|
| ownership/lifecycle | applicable | canonical `weapons` only; generic combat remains completed OAM-013 |
| build/toolchain | compatible | existing Otheryn C++ unit-test harness will be reused |
| configuration | no change | no configuration mutation planned |
| service/API | retain target/upstream | current weapon API/runtime substrate retained pending proof |
| scheduling/concurrency | no change | no scheduler/concurrency mutation |
| persistence | no change | no new persistence boundary |
| protocol/session | no change | no protocol/session mutation |
| identifiers/assets | no change | no identifier/asset migration |
| world/map | no change | no world/map mutation |
| runtime | pending exact-target proof | full target build/runtime smoke required |
| tests | pending | focused `WeaponReuseTest` plus full target CTest required |
| physical-client E2E | not required | no protocol/client/user-visible contract mutation |
| operations | bounded | exact-head CI/review/drift/merge gates required |
| security/privacy | no new boundary | no credential/privacy/security flow mutation |

## Explicit exclusions

OAM-015 does **not** claim or add:

- exhaustive weapon damage or hit-chance parity;
- Real Tibia melee/distance/wand formula parity;
- exhaustive resource, charge, break or ammunition-consumption parity;
- individual weapon-script parity across the entire datapack;
- generic combat policy changes;
- spell/rune migration;
- vocation or Weapon Proficiency redesign;
- protocol/client/map/asset changes;
- persistence redesign or SQL/KV atomicity.

OAM-004 SQL/KV non-atomicity and completed OAM-013/OAM-014 combat ownership remain authoritative.

## Completion gate

The provisional `weapons → REUSE` disposition becomes final only after:

1. proof-only target PR exact-head CI/Required/autofix and full CTest pass;
2. focused `WeaponReuseTest` passes;
3. target comments/reviews/threads are clean and target-main drift is checked;
4. target proof PR merges with exact-head protection;
5. this Canary governance task is updated with exact proof and passes its own exact-head gates;
6. separate lifecycle archive and durable program reconciliation merge.

OAM-016 must remain NOT STARTED until the full OAM-015 sequence completes.
