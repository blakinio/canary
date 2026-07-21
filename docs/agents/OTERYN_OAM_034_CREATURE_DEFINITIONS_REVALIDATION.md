# OAM-034 Creature definitions revalidation

## Disposition

`creature-definitions → ADAPT`

## Immutable task-start baselines

- Canary/governance and legacy evidence: `ab2fb5548260544f42f786d11d4dd1b600c39a06`
- Otheryn target: `2fe646dfff3d4fc0672c3fbeca85708dabc4ce87`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `465b7a2192b176cf8cb9d58e000c38863e4a6e4c`

Canonical `creature-definitions` is dependency-valid with `depends_on: []` and owns monster definition data. Creature AI, spawns, raids and boss encounter orchestration are separate canonical packages.

## Selected adaptation boundary

Merged legacy PR #192 is the accepted bounded donor. Six production monster definitions contain reviewed data corrections still absent from task-start Otheryn and fresh upstream:

1. Agrestic Chicken: add `BESTY_RACE_BIRD`.
2. Terrified Elephant: add `BESTY_RACE_MAMMAL`.
3. Alternate Eradicator: change `bossRaceId` from `1225` to `1226`.
4. Monk's Apparition: change Bestiary `raceId` from `1946` to `2636`.
5. Haunted Dragon: add `BESTY_RACE_DRAGON`.
6. Crypt Warrior: add Bestiary `raceId = 1995` and `BESTY_RACE_UNDEAD`.

Fresh file-by-file comparison confirmed that every selected task-start target file is exact-identical to fresh upstream pre-fix content and current legacy preserves the exact PR #192 correction. PR #192 validator, validator tests, Cyclopedia logs and governance files are excluded. The target package adds only one local focused source-contract proof plus its test registration, evidence and task checkpoint.

## Target delivery state

Otheryn PR #69 is open from base `2fe646dfff3d4fc0672c3fbeca85708dabc4ce87` with initial exact head `dabc868c5ff9ca8009f20f1eb90645937ff18e22`. Its initial diff contains exactly ten intended paths: six production definitions, focused proof, test registration, target evidence and active task checkpoint. Exact-head autofix, Repository Audit, CI and Required validation are in progress.

## Governance drift audit

OAM-034 task-start Canary baseline is `ab2fb5548260544f42f786d11d4dd1b600c39a06`. Before governance branch creation, unrelated OTBM lifecycle PR #698 advanced Canary `main` to `7f32462c0e55f1efa397438652bb41f7e200f3d9`; its archive-only OTBM paths do not overlap OAM-034 governance or selected monster definitions. No open Otheryn PR and no open Canary PR matching `monster` or `creature-definitions` overlapped the selected production boundary during fresh preflight.

## Nonclaims

OAM-034 does not claim full monster catalogue parity, exhaustive stats, loot, spells, resistances or immunities, creature AI, spawn placement, raid behavior, boss encounter mechanics, Bestiary/Bosstiary runtime correctness, protocol/client compatibility, persistence correctness, maps/assets/schema/deployment parity, physical-client creature E2E closure, or full Real Tibia parity.
