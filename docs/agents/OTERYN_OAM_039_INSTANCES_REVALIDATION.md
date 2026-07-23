# OAM-039 Instances revalidation

## Final disposition

`instances → ADAPT`

## Baselines

- Canary OAM-039 preflight merge: `5c0613fd853e85421a89f661e9b3774c4dd730ff`
- Canary fresh governance base: `2b2eafcd0d7990f499f25acf74af6526ca72ceee`
- Otheryn target task-start base: `a275f1d788b50164ffc79b6f6143e13b9150c82e`
- Otheryn target delivery merge: `a2a52e239d8e8a770ff7376fcbb9b5bfdcc8cc13`
- fresh upstream Canary baseline used by preflight: `7323503b3dc61ed86bf1f04a611b2d0aec64b35a`
- maintained OTClient baseline used by preflight: `1e5305395159142634f182d9e888e5f9164228c6`

## Selection and ownership

Canonical `instances` owns configured non-overlapping map-region allocation, strong instance/slot identifiers, `InstanceState` lifecycle, stable runtime creature-id ownership, fail-closed relations, summon ownership inheritance, cleanup quarantine and expiration, lazy instance-scoped event liveness, and the bounded `InstanceArenaService` consumer.

`Game` ownership, ordinary spawn/NPC scoping, spectator/target/combat isolation, generic scheduler cancellation, Lua/admin/talkaction reachability, protocol/client paths, map content, assets, persistence, physical-client orchestration and full Real Tibia instance parity remain outside OAM-039.

Clean Otheryn and fresh upstream lacked the canonical `InstanceManager` roots, so `REUSE` was unavailable. Legacy Canary provided the staged behavioral donor, but target delivery intentionally adapted only the canonical subsystem and focused tests/build registration instead of copying cross-module runtime wiring wholesale.

## Target adaptation

Otheryn PR #81 introduced exactly 19 bounded paths: task/evidence documents, canonical `src/game/instance/**`, production CMake registration, focused `tests/unit/game/instance/**`, and test CMake registration. No `Game`, `Creature`, Lua, talkaction, protocol, client, map-content, asset, schema or persistence path was changed.

The clean target deliberately does not import legacy `data-canary` arena coordinates. `InstanceArenaService::configuredRegions()` remains empty by default and the bounded consumer operates against explicitly configured target regions, keeping the clean target fail-closed until separately owned map/runtime integration is proven.

## First failure and bounded repair

Initial exact head `58c4d2cf2cb5f26d67974b78e9d8e16885eae702` passed formatting, compile/platform paths, runtime smoke and schema import, but Linux-debug full tests exposed one owned lifecycle defect: `InstanceManagerTest.CleanupRunsExactlyOnceAndDirtyRegionIsQuarantined` observed that a quarantined `Closing` instance returned early on retry and therefore did not release its region after creature ownership was later drained.

The bounded repair changed `InstanceManager::close()` so a `Closing` retry skips the cleanup callback but retries finalization and region release when ownership is empty. Cleanup still executes exactly once; dirty regions remain quarantined until cleanup ownership is drained.

## Final target validation

Otheryn PR #81 final head `e216c3bb732bc6dc97374833bbfcb13a4f4ebc50` passed:

- autofix run `30002236999`;
- CI run `30002237279`;
- Required run `30002237057`;
- Fast Checks and Lua tests;
- Linux release and Linux debug compilation/runtime paths;
- Linux-debug database import and full `Run Tests`, including the repaired quarantine/finalization case;
- both Windows build paths;
- macOS build/runtime smoke;
- Docker build validation.

The final PR changed exactly the 19 intended bounded paths. Comments, submitted reviews and review threads were empty. Otheryn `main` remained at the immutable task-start base before merge. PR #81 squash-merged as `a2a52e239d8e8a770ff7376fcbb9b5bfdcc8cc13`.

## Final conclusion

OAM-039 is `ADAPT`: the clean target now contains the bounded canonical instance lifecycle/isolation foundation with one evidence-driven lifecycle repair, while cross-module production activation remains deliberately outside this package.

## Nonclaims

OAM-039 does not claim complete production instance activation through `Game`, ordinary spawn/NPC ownership, full spectator/target/combat isolation, logout/death/reconnect semantics, generic scheduler task cancellation, production arena coordinates, persistence semantics, admin Lua/talkaction reachability, two-parallel-instance physical E2E, multiworld support or full Real Tibia instance parity.
