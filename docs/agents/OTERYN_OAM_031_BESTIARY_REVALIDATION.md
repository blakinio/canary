# OAM-031 Bestiary revalidation

## Final disposition

`bestiary → ADAPT`

## Immutable task-start baselines

- Canary/governance: `9aa582eb6b8ab9444294e08798f628cd053d2428`
- Otheryn target: `6a7e54ee3c9597e3ab265a14c2b783631ef3776f`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`

Canonical `bestiary` owns the narrow server root `src/io/iobestiary.*` and depends on completed `cyclopedia` and `player-persistence`. Monster definitions are evidence inputs rather than the module ownership root; Charm definitions, unlocks, assignment, reset policy and combat effects remain under canonical `charms` ownership.

## Selected adaptation boundary

Task-start Otheryn and fresh upstream shared exact `src/io/iobestiary.cpp` blob `c0497c4d1814e7950ad8fc27b9a4ec1f86d4a5cd`. Merged legacy PR #188 supplied three hunks in that file; semantic ownership decomposition selected exactly two Bestiary-owned corrections:

1. `IOBestiary::addBestiaryKill` now validates `player` and `mtype` before dereferencing `mtype->info.raceid`, preserving the existing zero-race early return.
2. `IOBestiary::calculateDifficult` converts `chance` to `double` before division by `1000.0`, preserving fractional difficulty thresholds that integer division previously truncated.

The PR #188 all-Charm reset-price correction was deliberately excluded as `charms` ownership. Merged PR #192 monster-definition data was also excluded because those files are not the canonical Bestiary ownership root. Current legacy retains both selected corrections; whole-file legacy reuse was rejected because `iobestiary.cpp` also hosts separately owned Charm helpers and behavior.

## Target delivery

Otheryn PR #63 final head `c49796d696448aa168c34629dc9ebcd9fd7a9465` changed exactly five intended OAM-031 paths. The production-only diff was exactly `src/io/iobestiary.cpp`, +7/-3, matching the two selected hunks. Focused proof additionally guards that the target's pre-existing all-Charm reset-price formula remains unchanged by OAM-031.

Exact-head autofix.ci #187, CI #226 and Required #211 succeeded. Linux debug compilation, runtime smoke, database schema import and full `Run Tests` succeeded. Test-log artifact `8493329878` has digest `sha256:e99f341683bc432512ddd0dc235204f8b13510cd48eaf9f06c9cdf53d7dbc432`. Comments, reviews and review threads were empty; Otheryn `main` had no drift from immutable target base `6a7e54ee3c9597e3ab265a14c2b783631ef3776f`. PR #63 merged by expected-head squash as `86e4b08c28ede2f35c215a7c2327a579f4a61419`.

## Governance drift audit

Before governance finalization, Canary `main` advanced from task-start `9aa582eb6b8ab9444294e08798f628cd053d2428` to `87c4f71b0deb880da7ba4228bc29e769db2c5818`. The intervening changes are independently owned E2E persistence and OTS/OTBM roadmap/task work; no changed path overlaps the OAM-031 governance files or canonical `src/io/iobestiary.*`. The governance branch was therefore reconstructed on current `main` before final gating.

## Nonclaims

OAM-031 does not claim full Bestiary parity, exhaustive kill-stage/reward correctness, Charm correctness, monster-definition parity, exact protocol/client rendering compatibility, persistence completeness, tracker refresh correctness under every runtime state, database durability, physical-client Bestiary E2E closure, or full Real Tibia parity.
