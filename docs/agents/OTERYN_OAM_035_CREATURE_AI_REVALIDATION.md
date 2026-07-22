# OAM-035 Creature AI revalidation

## Final disposition

`creature-ai → REUSE`

## Immutable baselines

- Canary preflight task-start: `6a87373e84073a84ccdbdb64f7d61b2747f40764`
- Otheryn target task-start: `4771350b44665c5a37b0c058b3d413c0c0de542d`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`
- Canary preflight merge: `0f288fe2722d66753c74d859196688a7f9f60e60`

Canonical `creature-ai` owns Monster runtime think, target/friend maintenance, target search and selection, follow/flee/movement decisions, attack/defense execution, callbacks, spawn/despawn and summon-ownership interactions. It depends only on completed `creature-definitions`; creature definition loading, static spawn placement, raids, boss reward orchestration, generic combat and protocol/client behavior remain separate boundaries.

## Reuse decision

Task-start Otheryn and fresh upstream Canary shared exact canonical owned core blobs: `src/creatures/monsters/monster.cpp` at `30cdadf4076d29116eb96fb8bb5f7f46bebddcd5` and `monster.hpp` at `a5426fdd22533179a9d54834dbe7b340a5d45012`. Legacy Canary diverged on both core blobs and was not selected as a stronger whole-module donor.

Target proof PR #72 preserved production code unchanged and added only a bounded source-contract proof, task record, proof document and unit-test registration. The proof guards the independent Monster runtime lifecycle surface and the modular `monster_targeting`, `monster_pathfinding`, `monster_combat_intention` and `MonsterComputeService` wiring, while existing focused tests remain behavioral evidence for those components.

PR #72 final head `c623dc3b60f359bd821cab112e7204aac1696494` passed exact-head autofix run `29902975001`, CI run `29902975132`, Required run `29902974955`, Linux-debug runtime smoke/schema/full `Run Tests`, Linux release, both Windows build paths and macOS. Changed-path audit was exactly four intended proof/task paths with no production path. Comments, reviews and review threads were empty, and Otheryn `main` remained at immutable target base before merge.

Otheryn PR #72 squash-merged as `d9359bed541b06c4457d23a352b877caf5e88df7`.

## Nonclaims

OAM-035 does not claim Real Tibia AI parity, exact target-choice weights, pathfinding parity, thread-safety proof, scheduler fairness, combat formula parity, spawn timing parity, summon ownership completeness, boss AI/reward correctness, raid behavior, protocol/client compatibility, physical-client gameplay E2E closure or full Oteryn readiness.
