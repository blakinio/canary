# OAM-012 — Achievements Revalidation

Status: **target adaptation merged; Canary governance closeout in review**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-012`

## Immutable task-start baselines

```text
legacy/governance Canary: blakinio/canary@d9c967d6e9b778da11a206d134d559f38ec1b8c8
target Otheryn: blakinio/Otheryn@72f7bdc1a5afa9e9982c20bdcf3098c83dca543e
upstream evidence: opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f
maintained OTClient: blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

These remain immutable task-start references. The maintained OTClient was read-only evidence only; OAM-012 required no client or protocol change.

## Canonical module and final disposition

```text
module: achievements
final disposition: ADAPT
```

`REUSE` was rejected because the task-start target/upstream lacked the selected persisted achievement-point reconciliation, carried stale point metadata, and marked achievement ID 567 as unknown.

`ADAPT` is proven by a bounded donor chain that preserves one authoritative achievement catalogue, couples point metadata correction with persisted aggregate reconciliation, and reopens Weapon Proficiency only for the exact achievement-567 attainability integration already separated by OAM-011.

## Selected coherent donor boundary

The accepted semantic chain is:

1. Canary PR #256 — reviewed safe non-point achievement metadata corrections.
2. Canary PR #264 — one logical adaptation containing five achievement point metadata corrections, deterministic persisted aggregate-points reconciliation, fail-closed unresolved-name handling, and seven `PlayerAchievementTest` cases.
3. Canary PR #288 — achievement 567 `The Forbidden Build`, its exact twelve-weapon mastery attainability condition, and three additional Weapon Proficiency focused tests.

The final catalogue was transferred from the exact PR #288 donor state, which contains the selected catalogue lineage. No bulk legacy copy and no unrelated achievement hooks were imported.

## Exact donor provenance

PR #264 donor commit:

```text
d14d5c992d4095c79672a8469050aa9e103e34bb
```

Verified Git blobs:

```text
src/creatures/players/components/player_achievement.cpp
998a077b6302233ba81969e904f72ad19d4b4840

src/creatures/players/components/player_achievement.hpp
c44334cc9993c5a497ea2023d52cdd6d26501914

tests/unit/players/components/player_achievement_test.cpp
c10d90aa649322520739696507ba8a0ff2d05a06
```

The task-start handover value `c10d90aa37e587aa1738512e4907a4399e97f511` for the test file was revalidated and rejected: the exact file at donor commit `d14d5c9...` hashes to `c10d90aa649322520739696507ba8a0ff2d05a06`. The materializer failed closed on the mismatch before the corrected exact provenance was accepted.

PR #288 donor commit:

```text
67ac28ee314ccc31671344515633c9411c3fe9df
```

Verified Git blobs:

```text
data/scripts/lib/register_achievements.lua
25e5b794a41adb84f7c0f7d309283d4fdb971511

src/creatures/players/components/weapon_proficiency.cpp
780d39f0c2cd0002ebd12f11a611212592217976

src/creatures/players/components/weapon_proficiency.hpp
1ce80f1789aec6649df9943b24081f0df8f10fb2

tests/unit/players/components/weapon_proficiency_test.cpp
756088ca70188226b2bbe96dd44f038fd6afe417
```

All seven donor-controlled files on the final target head were reverified against these exact Git blob SHAs after CI autofix. The autofix changed only CMake formatting.

## Target delivery

Otheryn issue:

```text
#30 — OAM-012: adapt achievement catalogue and point reconciliation
state: CLOSED / completed
```

Otheryn target PR:

```text
#31 — fix(achievements): adapt OAM-012 catalogue and reconciliation
final head: 8ee4bfe3c6b867834447a5b9e206e1dbd44f66d2
merge method: squash
target merge: 4a16ca17ebd098cf9763bb3c07755bfd31ac1c43
```

The final target diff contained exactly eight bounded runtime/test paths:

```text
data/scripts/lib/register_achievements.lua
src/creatures/players/components/player_achievement.cpp
src/creatures/players/components/player_achievement.hpp
src/creatures/players/components/weapon_proficiency.cpp
src/creatures/players/components/weapon_proficiency.hpp
tests/unit/players/components/CMakeLists.txt
tests/unit/players/components/player_achievement_test.cpp
tests/unit/players/components/weapon_proficiency_test.cpp
```

Temporary donor-materialization files were removed before final proof and merge. No governance validator, duplicate registry, overlay catalogue, or second unit-test harness remained in the target diff.

## Exact-head target proof

Final target head:

```text
8ee4bfe3c6b867834447a5b9e206e1dbd44f66d2
```

GitHub Actions proof:

```text
CI #111                     run 29638502030  SUCCESS
Required #104               run 29638501951  SUCCESS
Repository Audit #7         run 29638501958  SUCCESS
autofix.ci #97              run 29638501946  SUCCESS
```

Linux debug proof on the final head:

```text
configure/build: PASS
Canary datapack runtime smoke: PASS
database schema import: PASS
actual CTest Run Tests: 346/346 PASS
PlayerAchievementTest: 7/7 PASS
WeaponProficiencyTest: 10/10 PASS
```

The 10 Weapon Proficiency cases consist of the seven accepted OAM-011 cases plus the three OAM-012 `The Forbidden Build` cases:

```text
ForbiddenBuildReviewedWeaponSetIsExact
ForbiddenBuildRequiresEveryReviewedWeaponMastered
ForbiddenBuildIgnoresNonTargetAndDuplicateEntries
```

Additional exact-head matrix proof:

```text
Linux release build: PASS
Linux release Canary runtime smoke: PASS
Linux release Global datapack runtime smoke: PASS
Windows build: PASS
macOS build: PASS
macOS Canary runtime smoke: PASS
Docker CI job: PASS
```

Evidence artifacts from CI run `29638502030`:

```text
linux-debug-test-logs
artifact: 8427980477
digest: sha256:170df7911fd928bb6af90c7f703e00554eccb4625a56d9fd54cc20e0854e0d3e

linux-linux-debug-runtime-smoke-logs
artifact: 8427980648
digest: sha256:ef03229e25ce6d4e7290627161d0043f8680f4d52f7757d5c7ef5bfe7ae8b0d5

canary-linux-debug
artifact: 8427981926
digest: sha256:f50ab03ace6982253968f47e34e8d64ee86ce5fc9f3e6c9b9bbe1a4e00b042a9
```

The downloaded `linux-debug-test-logs` artifact independently confirmed `100% tests passed, 0 tests failed out of 346`, exactly seven `PlayerAchievementTest` cases, and exactly ten `WeaponProficiencyTest` cases.

## Final boundary classification

| Boundary | Final classification | Evidence-backed result |
|---|---|---|
| ownership/lifecycle | applicable | OAM-012 owns catalogue metadata, achievement point reconciliation, and the bounded 567 attainability integration; lifecycle remains separate after this governance feature merge |
| build/toolchain | compatible | existing Otheryn component `canary_ut` harness reused; only existing CMake registration changed |
| configuration | not applicable | no runtime configuration mutation |
| service/API | adapted | `PlayerAchievement` reconciliation API added from exact donor provenance without unrelated API redesign |
| scheduling/concurrency | no change | no scheduler or concurrency model mutation |
| persistence | adapted | persisted aggregate achievement points are reconciled from resolved current definitions; unresolved stored names fail closed; no SQL/KV atomicity claim |
| protocol/session | not applicable | no protocol, session, or maintained-client change |
| identifiers/assets | adapted | selected catalogue metadata corrections and ID 567 added through one central catalogue |
| world/map | not applicable | no map or world ownership change |
| runtime | applicable and proven | load reconciliation and achievement-567 award behavior covered by focused tests plus runtime smoke |
| tests | applicable and proven | 7/7 PlayerAchievement, 10/10 WeaponProficiency, full 346/346 target suite |
| physical-client E2E | not required | no client/protocol mutation and selected claims are proven below the client boundary |
| operations | bounded | exact-head CI, fail-closed donor verification, eight-path final diff, race-safe main-drift check, squash merge |
| security/privacy | no new boundary | no credential, privacy, or security-sensitive data-flow change |

## Catalogue ownership/path conclusion

`data/scripts/lib/register_achievements.lua` is the active central runtime achievement catalogue and registers definitions directly through `Game.registerAchievement(...)`.

The previously recorded canonical glob `data-otservbr-global/scripts/achievements/**` does not describe a second authoritative catalogue for this delivery. The mismatch is classified as canonical registry metadata drift/incompleteness, not a runtime ownership split. OAM-012 therefore preserved one authoritative central catalogue and did not introduce an overlay or duplicate registry.

Any future canonical registry metadata cleanup must preserve this conclusion and is not permission to create another runtime source of truth.

## Persistence conclusion

The five corrected point values and persisted aggregate-point reconciliation are one compatibility boundary. Metadata-only migration was rejected because existing stored aggregate values could remain stale.

OAM-012 does not change the inherited OAM-004 durability boundary:

- player SQL and player KV are not claimed to be atomic;
- no cross-domain transaction was introduced;
- no generic KV redesign was performed;
- no automatic MySQL reconnect or arbitrary SQL replay was introduced.

## Achievement 567 conclusion

Achievement 567 `The Forbidden Build` belongs in OAM-012 because this package owns the achievement catalogue boundary that OAM-011 deliberately excluded.

Its attainability integration is also accepted in this bounded package because PR #288 supplies an exact reviewed twelve-weapon condition and three deterministic focused tests, and the integration reuses the already-accepted OAM-011 Weapon Proficiency component rather than importing unrelated gameplay hooks.

A catalogue definition alone was not treated as attainability proof.

## Explicit exclusions and residual gaps

OAM-012 deliberately does **not** add or claim:

- unrelated quest achievement hooks;
- unrelated combat achievement hooks;
- unrelated spell achievement hooks;
- governance validator code in Otheryn runtime;
- duplicate achievement catalogue;
- permanent achievement override/overlay;
- generic KV schema redesign;
- SQL/KV transaction atomicity;
- client changes;
- protocol changes;
- map changes;
- asset changes;
- full Real Tibia achievement attainability parity.

Residual gap: the canonical module registry metadata should eventually be normalized so its declared data paths explicitly include the proven central catalogue path. This is documentation/governance cleanup only and is not a blocker to the bounded OAM-012 runtime adaptation.

## Final conclusion

```text
achievements → ADAPT
```

Target delivery is merged at:

```text
blakinio/Otheryn@4a16ca17ebd098cf9763bb3c07755bfd31ac1c43
```

OAM-012 is **not yet program-complete** at this point. The required remaining sequence is:

1. merge this Canary governance feature PR;
2. archive the active OAM-012 task in a separate lifecycle-only PR;
3. reconcile the durable migration program in a separate program-only PR;
4. keep OAM-013 `NOT STARTED` until the program reconciliation merge completes.
