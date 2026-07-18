# OAM-010 — Character Progression Revalidation

Status: **target proof delivery complete; Canary governance pending final gate**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-010`

## Exact task-start baselines

```text
legacy/governance Canary: blakinio/canary@cb149d427e6a954ee3ab163758465627bc1e643c
target Otheryn: blakinio/Otheryn@f59a58426b4d3910ba0cdc0d2332c24f31a1db4f
upstream evidence: opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f
maintained OTClient: blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

Final target proof delivery:

```text
blakinio/Otheryn@a4d095e3880787233bd194616dc6d19e6b94faaf
```

The maintained client is pinned for reproducibility. The canonical `character-progression` record has no client implementation path, and OAM-010 makes no protocol/UI mutation.

## Selected canonical module and final disposition

Exactly one canonical migration unit is selected:

```text
character-progression ADAPT
```

`ADAPT` is deliberate and bounded. The target/upstream progression core is retained and proven without production mutation. Whole-module legacy `REUSE` is rejected because legacy Canary contains a session-coupled disconnect-death-protection policy inside the broad Player/death-loss surface that the clean target and pinned upstream do not contain. OAM-010 does not import that policy.

The module depends on completed `character-lifecycle` and `player-persistence` foundations. `weapon-proficiency` remains downstream and is not included.

## Task-start provenance

| Path | Legacy Canary | Otheryn target | Upstream evidence | Result |
|---|---|---|---|---|
| `src/creatures/players/player.hpp` | `43adfadfd1ef5dd3edad43cda9c42dc357490bb4` | `3140cd386ae36fac6bb19a4d84cff97ec0efdec2` | `3140cd386ae36fac6bb19a4d84cff97ec0efdec2` | broad legacy file differs; target equals upstream |
| `src/creatures/players/player.cpp` | `68f28716d655b58e3df6a73033e5a7454eeae781` | `01962877ba48ecccbabc0fbf94b1dc5197f0ae04` | `01962877ba48ecccbabc0fbf94b1dc5197f0ae04` | broad legacy file differs; target equals upstream |
| `src/io/functions/iologindata_load_player.cpp` | `19169deecdf67b47691e9e4521f3519c1bfbdc40` | `4f5023c39a74addb98e19d5c546f67a6f71a5e50` | `4f5023c39a74addb98e19d5c546f67a6f71a5e50` | broad legacy file differs; target equals upstream |
| `src/io/functions/iologindata_save_player.cpp` | `5bb44a2f2e15c33b39a5b24206440057ded4ab5b` | `5bb44a2f2e15c33b39a5b24206440057ded4ab5b` | `5bb44a2f2e15c33b39a5b24206440057ded4ab5b` | exact identity across all three |

Whole-file inequality was not treated as progression evidence. Legacy Player includes unrelated integrations such as Forge, imbuement-access and multichannel work that are outside this canonical module.

## Progression-specific semantic revalidation

### Level and experience

The pinned target and legacy revisions preserve the same selected level/experience threshold and advancement substrate. Target `Player::getExpForLevel` is directly covered by focused target proof.

The zero-stamina early return in the target experience-gain path was source-reviewed as compatibility evidence. A direct unit invocation of `gainExperience` crossed broader runtime callback/global-service boundaries in the minimal Player test harness and caused a harness-level crash. OAM-010 therefore does not claim an executable isolated test for that path and does not create a second runtime harness merely to force one.

### Skills and magic level

Selected regular-skill and magic-level advancement semantics are compatible across the pinned target/legacy surfaces. The target proof executes real vocation requirement thresholds through the existing `addOfflineTrainingTries` path for both a regular skill and magic level.

### Offline training

The selected offline-training time clamp/floor and advancement paths are compatible across the pinned target and legacy revisions. Focused target tests execute the time upper/lower bounds and both advancement categories.

### Persistence

Selected progression load fields for level/experience, magic level/mana spent, stamina, offline-training time/skill and related shared progression state were compared at the pinned revisions without finding a progression-specific target incompatibility requiring a whole-file load replacement.

The player save implementation blob is exact-identical across legacy, target and upstream at task start. OAM-004D remains authoritative: OAM-010 does not restore legacy IOLoginData wholesale and does not claim player SQL commit plus later durable KV flush is atomic.

### Death/loss and blessings

This is the confirmed progression-scope divergence.

Legacy Canary contains disconnect-death protection introduced by Canary PR #40 / merge `5dd90d1335fd4bf0a28cf9e0470366042739cae8`. The policy is configuration-driven and can suppress death loss and preserve blessings after a protected disconnect. The pinned Otheryn target and pinned upstream do not contain that behavior.

The policy is not imported by OAM-010 because it couples death/loss consequences to session/disconnect state and lacks sufficient bounded target/session/runtime proof here. This deliberate exclusion is the reason the legacy module is not approved for unconditional `REUSE`.

## Target proof delivery

Target issue/PR:

```text
blakinio/Otheryn#26
blakinio/Otheryn#27
```

Final target PR head:

```text
4152ee997e4ab6e1b8ca8c4b18ab86853ebeea58
```

Target PR #27 changed only:

```text
docs/oam-010-proof-scope.md
tests/unit/players/CMakeLists.txt
tests/unit/players/character_progression_test.cpp
```

No production `Player`, IOLoginData, persistence, protocol, client, database, map or gameplay source changed.

Final exact-head gates:

```text
autofix.ci #83 / run 29619165369: PASS
Required #90 / run 29619165343: PASS
CI #95 / run 29619165487: PASS
Linux debug Run Tests: PASS
comments: 0
submitted reviews: 0
review threads: 0
```

Final Linux debug test artifact:

```text
artifact id: 8421885698
name: linux-debug-test-logs
digest: sha256:b40a497f337a050312fa01632fefbfff7bb94e59f32449bb52131f197f759954
```

The artifact records all four focused tests executed and passed:

```text
CharacterProgressionTest.ExperienceThresholdsAreMonotonic
CharacterProgressionTest.OfflineTrainingTimeClampsAndFloors
CharacterProgressionTest.OfflineTrainingAdvancesRegularSkillAtRequirementBoundary
CharacterProgressionTest.OfflineTrainingAdvancesMagicLevelAtRequirementBoundary
```

The same final test run completed the full suite with 329/329 tests passing.

Two earlier proof attempts were rejected rather than promoted as evidence:

1. stack-allocated Player instances caused `bad_weak_ptr` in real advancement paths that correctly expect shared ownership;
2. after switching to `shared_ptr<Player>`, skill and magic tests passed, while direct `gainExperience` remained unsuitable for the minimal unit harness because it crosses broader runtime callbacks/globals.

The final proof keeps only isolated deterministic unit boundaries and uses source review for the zero-stamina gate.

PR #27 squash-merged as:

```text
a4d095e3880787233bd194616dc6d19e6b94faaf
```

Otheryn issue #26 was closed as completed.

## Final boundary classification

| Boundary | Final state | Evidence / decision |
|---|---|---|
| ownership/lifecycle | applicable, proven | shared state remains owned by runtime `Player`; OAM-005 character lifecycle remains authoritative |
| build/toolchain | applicable, proven | target focused tests registered in existing `canary_ut`; full target CI/Required/autofix passed |
| configuration | applicable, bounded | existing target configuration/vocation inputs retained; legacy disconnect-death policy configuration deliberately excluded |
| service/API | applicable, proven for selected scope | existing Player progression APIs retained; no new public runtime API introduced |
| scheduling/concurrency | no new boundary introduced | selected target proof adds no scheduler, timer or concurrency behavior |
| persistence | applicable, proven for bounded compatibility | selected load semantics reviewed; save blob exact-identical; OAM-004D preserved |
| protocol/session | not applicable to accepted core proof; divergence deferred | no protocol/client mutation; legacy disconnect-death session coupling is explicitly not migrated |
| identifiers/assets | not applicable | no independent IDs/assets migrated |
| world/map | not applicable | no OTBM/world ownership |
| runtime | applicable, bounded | target runtime smoke passed; focused deterministic target tests passed |
| tests | applicable, proven | four focused tests plus full 329/329 suite pass on exact target head |
| physical-client E2E | not applicable to this bounded compatibility disposition | no client/protocol/UI mutation; OAM-009 remains separate login/vocation physical proof |
| operations | bounded rollback | target delivery is proof-only; rollback is reverting the test/docs merge, with no production-state migration |
| security/privacy | no new boundary | no credential, secret or sensitive-data behavior changed |

## Final disposition rationale

`character-progression → ADAPT` means:

- retain the clean target/upstream progression core;
- preserve already-proven OAM-004/OAM-005 persistence and character-lifecycle adaptations;
- add target-side deterministic acceptance proof without production mutation;
- do not copy broad legacy Player/IOLoginData files;
- do not import the unproven session-coupled disconnect-death protection policy as part of this package.

This is not a Real Tibia parity claim. It is a bounded target-compatibility and migration-disposition decision.

## Known gaps

- Real Tibia XP, skill, magic, stamina, offline-training, death-loss and blessing formula/value parity remains unproven.
- The zero-stamina XP gate is source-reviewed in this package but not isolated as an executable unit test.
- Disconnect-death protection remains legacy-only and unadopted; any future target decision requires separate session/protocol/runtime evidence.
- No exhaustive death/loss/blessing runtime or physical-client E2E is claimed.
- No protocol/UI presentation compatibility claim is made.
- OAM-004 residual persistence gaps remain, including non-atomic player SQL commit versus later durable KV flush.

## Governance completion boundary

Target proof delivery is complete at `blakinio/Otheryn@a4d095e3880787233bd194616dc6d19e6b94faaf`.

Remaining sequence:

1. update the active OAM-010 task with this evidence and final `ADAPT` disposition;
2. synchronize Canary PR #509 cleanly to current `main` if needed;
3. require exact-head Ownership/CI and ready-state gates;
4. audit comments, reviews and unresolved threads;
5. squash-merge PR #509 with exact-head guard;
6. archive the OAM-010 task in a separate lifecycle-only PR;
7. reconcile OAM-010 completion in the durable Oteryn program record;
8. keep OAM-011 inactive until all three Canary boundaries are complete.
