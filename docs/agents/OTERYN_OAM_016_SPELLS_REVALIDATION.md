# OAM-016 — Spells Revalidation

Status: **target proof complete**

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

## Canonical module and final disposition

```text
spells → REUSE
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

At task start no open Otheryn PR existed. Canary PR #514 owned authenticated-session transport security validation, #525 physical teleport E2E and #526 shared-state/economy security-audit documentation. None owned the canonical OAM-016 spell production boundary.

No overlapping open PR was identified for `src/creatures/combat/spells/**`, `data/scripts/spells/**` or `data-otservbr-global/scripts/spells/**`.

## Whole-boundary target/upstream provenance

OAM-002 established the clean target from exact pinned upstream Canary content. Target history from verified bootstrap `3cc7c1dfea747bb380f3761ee7ff7ac30141a115` through OAM-016 task-start `1dd21117ce06cc4463e6185f4ff74546031b55e6` changes no canonical spell production path. Upstream history from bootstrap source `a879c9312e34381e8eedf397b8ed44510698b689` through task-start pin `691614c1a302aee776002ca3851eca399be1a82c` changes only Windows workflow, network-message and server-definition paths, not the spell boundary.

Representative exact spell-core blobs:

```text
src/creatures/combat/spells.cpp
4afc2bafdcd3d122097b973931845b0fec7f32fb

src/creatures/combat/spells.hpp
d419f509853b3eb45658c2e8f5d6fbaec1f8d611
```

The `spells.cpp` blob is exact across target, pinned upstream and task-start legacy Canary. `spells.hpp` is exact between target and task-start legacy. Identity alone was not accepted; whole-history provenance and legacy-donor review were completed before selecting `REUSE`.

## Reviewed legacy history

Merged PR #76 adds Gameplay Analytics calls to representative spell/rune scripts and PR #108 later hardens those integrations so scripts resolve the live Analytics global instead of capturing/reloading the core incorrectly. These are Analytics ownership/instrumentation changes, not independent spell-runtime corrections. OAM-016 does not import or validate the Analytics subsystem.

Merged PR #216/#220 changes `data/scripts/spells/attack/flurry_of_blows.lua` and `data/scripts/spells/attack/front_sweep.lua` as part of a coordinated Wheel of Destiny 15.25 package. The changes add Wheel-conditioned alternative combat areas and depend on Wheel-owned runtime semantics.

Concrete provenance:

```text
flurry_of_blows.lua target/upstream: 8d291175b5e6b85b4b247a3586394fe5dd6cca70
flurry_of_blows.lua legacy:          bd926f373c434561a8a56a66a0c25b8b6179b0b0
front_sweep.lua target:              ea814e49a644bf4b43de57c87562b633b1d072f7
front_sweep.lua legacy:              84ab18af2fdd4073211ba05362029e4e52bbbabf
```

OAM-016 does not import only the spell-script fragments of that coherent Wheel package and does not reopen unresolved Wheel ownership. This remains a separate cross-module Wheel/spells parity gap.

## Exact target proof

```text
Otheryn issue #38: CLOSED / completed
Otheryn PR #39 final head: 62a61725c66a2c394327cb665f08d076c2b7d791
target squash merge: 46cc7458d644da356371aabf3ff18c0e51d228a8
CI #123: 29651516932 SUCCESS
Required #112: 29651516827 SUCCESS
autofix.ci #105: 29651516800 SUCCESS
Linux debug runtime smoke: PASS
database schema import: PASS
full CTest: 355/355 PASS
focused SpellReuseTest: 2/2 PASS
primary artifact: 8431734928
digest: sha256:e98fc12c4e8c4f661d96ebb39a7b7fe44d58c2e7c7dc53beb27c14773f0db5f8
```

The exact target PR changed only:

```text
tests/unit/game/CMakeLists.txt
tests/unit/game/spell_reuse_test.cpp
```

No production spell runtime/data mutation occurred. Immediately before expected-head squash merge, comments, reviews and review threads were all empty, and target `main` remained exactly task-start `1dd21117ce06cc4463e6185f4ff74546031b55e6`.

Focused `SpellReuseTest` passed:

1. `SpellReuseTest.PreservesDeterministicConfigurationSurface`;
2. `SpellReuseTest.PreservesInstantSpellRegistryLookup`.

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

## Remaining closeout

Target proof is complete and `spells → REUSE` is final. Canary governance PR #548 must pass final exact-head gates and merge, followed by a separate authoritative lifecycle archive and separate durable program reconciliation. Any automatically opened self-owned `docs(agents): archive merged PR` duplicate must be explicitly closed after the authoritative lifecycle archive is established.

OAM-017 remains NOT STARTED until the full OAM-016 sequence completes.
