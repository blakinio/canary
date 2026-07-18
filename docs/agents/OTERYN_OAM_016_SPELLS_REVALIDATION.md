# OAM-016 — Spells Revalidation

Status: **target proof in progress**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-016`

## Immutable task-start baselines

```text
legacy/governance Canary: blakinio/canary@93296bbf0c349a6589af51a311d12f7dfaf6c001
target Otheryn: blakinio/Otheryn@1dd21117ce06cc4463e6185f4ff74546031b55e6
upstream evidence: opentibiabr/canary@691614c1a302aee776002ca3851eca399be1a82c
maintained OTClient: blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

All four live heads were refreshed at task start.

## Canonical module and provisional disposition

```text
spells → REUSE (pending exact-target proof)
```

Canonical registry record: `docs/agents/real-tibia/registry/modules/spells.yaml`.

Registry boundary:

- server: `src/creatures/combat/spells/**`
- data: `data/scripts/spells/**`, `data-otservbr-global/scripts/spells/**`
- hard dependency: `combat`
- dependency status: completed by OAM-013
- interaction: `wheel-of-destiny`

The module owns spell registration, runes and instant spells, cooldown/vocation restrictions and deterministic area/runtime execution discovery. Generic combat policy, Wheel ownership, client hotkey UI, Analytics collection, protocol/client/map/assets and Real Tibia formula/value parity remain outside this package.

## Fresh live-state/open-PR preflight

At task start:

- no open Otheryn PR existed;
- Canary PR #514 owns authenticated-session transport security validation;
- Canary PR #525 owns deterministic physical teleport E2E;
- Canary PR #526 owns shared-state/economy security-audit documentation;
- none owns the canonical OAM-016 spell production boundary.

No overlapping open PR was identified for `src/creatures/combat/spells/**`, `data/scripts/spells/**` or `data-otservbr-global/scripts/spells/**`.

## Whole-boundary target/upstream provenance

OAM-002 established the clean target from exact pinned upstream Canary content. Target history from verified bootstrap `3cc7c1dfea747bb380f3761ee7ff7ac30141a115` through OAM-016 task-start `1dd21117ce06cc4463e6185f4ff74546031b55e6` changes no canonical spell production path. Upstream history from bootstrap source `a879c9312e34381e8eedf397b8ed44510698b689` through task-start pin `691614c1a302aee776002ca3851eca399be1a82c` changes only Windows workflow, network-message and server-definition paths, not the spell boundary.

Representative exact spell-core blobs are identical at task start:

```text
src/creatures/combat/spells.cpp
4afc2bafdcd3d122097b973931845b0fec7f32fb

src/creatures/combat/spells.hpp
d419f509853b3eb45658c2e8f5d6fbaec1f8d611
```

The `spells.cpp` blob is exact across target, pinned upstream and task-start legacy Canary. `spells.hpp` is also exact between target and task-start legacy. This identity is not used alone; whole-history provenance and legacy-donor review are required before accepting `REUSE`.

## Reviewed legacy history

### Gameplay Analytics spell/rune instrumentation

Merged PR #76 adds Gameplay Analytics calls to representative spell/rune scripts and PR #108 later hardens those integrations so scripts resolve the live Analytics global instead of capturing/reloading the core incorrectly. These are Analytics ownership/instrumentation changes, not independent spell-runtime corrections. OAM-016 does not import or validate the Analytics subsystem.

### Wheel 15.25 coordinated spell-area changes

Merged PR #216/#220 changes `data/scripts/spells/attack/flurry_of_blows.lua` and `data/scripts/spells/attack/front_sweep.lua` as part of a coordinated Wheel of Destiny 15.25 package. The changes add Wheel-conditioned alternative combat areas and depend on Wheel-owned runtime semantics.

Concrete provenance:

```text
flurry_of_blows.lua target/upstream: 8d291175b5e6b85b4b247a3586394fe5dd6cca70
flurry_of_blows.lua legacy:          bd926f373c434561a8a56a66a0c25b8b6179b0b0

front_sweep.lua target: ea814e49a644bf4b43de57c87562b633b1d072f7
front_sweep.lua legacy: 84ab18af2fdd4073211ba05362029e4e52bbbabf
```

OAM-016 will not import only the spell-script fragments of that coherent Wheel package and will not reopen unresolved Wheel ownership. This is recorded as a separate cross-module Wheel/spells parity gap, not silently dismissed evidence.

## Target proof

Otheryn issue:

```text
#38 — OAM-016: prove reusable spells core
```

Otheryn target PR:

```text
#39 — test(spells): prove OAM-016 reused spells core
```

Accepted target proof scope is tests only:

```text
tests/unit/game/CMakeLists.txt
tests/unit/game/spell_reuse_test.cpp
```

Focused `SpellReuseTest` coverage is bounded to:

1. deterministic spell configuration state round-trip through the existing `InstantSpell` API;
2. vocation-map configuration state;
3. exact instant-spell registry lookup;
4. case-insensitive spell-name lookup through the current registry surface.

No production spell runtime/data mutation is authorized by this proof.

## Boundary classification

| Boundary | Classification | Evidence-backed result |
|---|---|---|
| ownership/lifecycle | applicable | canonical `spells` retained; generic combat remains OAM-013 |
| build/toolchain | compatible | existing Otheryn C++ unit-test harness reused |
| configuration | retained | existing spell configuration surface tested; no config mutation |
| service/API | retain target/upstream | current spell registry/configuration API retained pending proof |
| scheduling/concurrency | no change | no scheduler/concurrency mutation |
| persistence | no change | no new durable state |
| protocol/session | no OAM-016 change | no wire/session mutation |
| identifiers/assets | no change | no identifier/asset migration |
| world/map | no change | no world/map mutation |
| runtime | pending exact-target proof | full target build/runtime smoke required |
| tests | pending | focused `SpellReuseTest` plus full target CTest required |
| physical-client E2E | not claimed | no protocol/client mutation; Wheel parity gap remains separate |
| operations | bounded | exact-head CI/review/drift/merge gates required |
| security/privacy | no new boundary | no credential/privacy/security flow mutation |

## Explicit exclusions

OAM-016 does **not** claim or add:

- exhaustive spell formulas or hit/heal value parity;
- exhaustive cooldown enforcement parity;
- exhaustive mana/soul/resource/rune consumption parity;
- individual spell-script parity across either datapack;
- Wheel of Destiny spell augmentation parity;
- partial migration of PR #216/#220;
- Gameplay Analytics instrumentation or telemetry parity;
- protocol/client/map/asset changes;
- persistence redesign or SQL/KV atomicity;
- full Real Tibia spell-system parity.

OAM-004 SQL/KV non-atomicity and completed OAM-006/OAM-007/OAM-013/OAM-014/OAM-015 ownership remain authoritative.

## Completion gate

The provisional `spells → REUSE` disposition becomes final only after:

1. proof-only target PR exact-head CI/Required/autofix and full CTest pass;
2. focused `SpellReuseTest` passes;
3. target comments/reviews/threads are clean and target-main drift is checked;
4. target proof PR merges with expected-head protection;
5. Canary governance is updated with exact proof and passes exact-head gates;
6. separate lifecycle archive and durable program reconciliation merge;
7. any automatically opened self-owned `docs(agents): archive merged PR` duplicate is explicitly closed after the authoritative lifecycle archive is established.

OAM-017 must remain NOT STARTED until the full OAM-016 sequence completes.
