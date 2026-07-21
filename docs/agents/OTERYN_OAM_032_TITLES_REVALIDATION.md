# OAM-032 Titles revalidation

## Final disposition

`titles → REUSE`

## Immutable task-start baselines

- Canary/governance: `db7cf6af480285ad4a87c3be2981a873f175eab6`
- Otheryn target: `ad2bd2f187df057c47d05c121351159ce30cc457`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`

Canonical `titles` owns the narrow server root `src/creatures/players/components/player_title.*` and depends only on completed `cyclopedia-character` and `player-persistence`. Bestiary, Bosstiary, character progression, houses and protocol remain interactions; appearance lifecycles and maintained-client rendering remain separate boundaries.

## Reuse boundary

Task-start Otheryn, current legacy and fresh upstream share exact `src/creatures/players/components/player_title.cpp` blob `c885d5ee55970d8ce93a80bb477bc317fb9faa98` and `player_title.hpp` blob `118806fee9ca6d939d73067af14c63c59d291f25`. Blob identity is supporting evidence only.

TSD-004 establishes an independent Titles definition, unlock, removal, current-selection and KV-persistence lifecycle rooted in `player_title.*`. Merged Cyclopedia runtime remediation PR #188 contains no Titles-root path; PR #192 is Bestiary/Bosstiary monster-data remediation; PR #243 changes validator workflow control only. The Cyclopedia audit's zero-finding result is not promoted into a claim about title definitions, thresholds, permanence, persistence, protocol, runtime behavior or maintained-client correctness.

No accepted legacy donor delta was found inside the canonical Titles root, and the task-start open-PR ownership audit found no overlapping writer. The smallest valid disposition is therefore `REUSE`, preserving the clean target implementation without production, protocol, data, schema, map, asset, deployment or maintained-OTClient mutation.

## Target delivery

Otheryn PR #65 final head `3244c8b0993047d9fe72ed56125a6f9e218defbb` changed exactly four intended OAM-032 proof/task paths and no production path. Focused proof guards the independent `PlayerTitle` lifecycle surface, scoped `titles/current-title` and `titles/unlocked` KV contracts, and the unlock gate on current-title selection.

Exact-head autofix.ci #188 run `29863062941`, CI #228 run `29863063433` and Required #213 run `29863063406` succeeded. Linux-debug compilation, runtime smoke, database schema import and full `Run Tests` succeeded. Test-log artifact `8508497986` has digest `sha256:2c2b98f96fe73bd8b2e9123f662779534a70ec7b0a5b7ebe895f1769b05ae9b3`. Comments, reviews and review threads were empty; Otheryn `main` had no drift from immutable target base `ad2bd2f187df057c47d05c121351159ce30cc457`. PR #65 merged by expected-head squash as `f5f21347c578a382cf0c52dbb4c69673ab3b05a9`.

## Governance drift audit

Canary `main` remains at immutable OAM-032 task-start baseline `db7cf6af480285ad4a87c3be2981a873f175eab6` when this governance package is created. Current open Canary PRs own E2E/security/documentation surfaces and do not overlap `player_title.*` or the two OAM-032 governance paths; Otheryn had no open PR at preflight.

## Nonclaims

OAM-032 does not claim title-definition or unlock-threshold parity, completeness of every cross-domain eligibility check, map/Drome/Goshnar or other TODO-backed title conditions, persistence atomicity or crash recovery, exact protocol compatibility, maintained-client parsing/rendering correctness, physical-client Titles E2E closure, or full Real Tibia parity.
