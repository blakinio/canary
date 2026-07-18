# OAM-011 — Weapon Proficiency Revalidation

Status: **target adaptation merged; Canary governance finalization pending**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-011`

## Exact task-start baselines

```text
legacy/governance Canary: blakinio/canary@9586530202eb3e40569bf4f97d21c63c9d99b6cb
target Otheryn: blakinio/Otheryn@a4d095e3880787233bd194616dc6d19e6b94faaf
upstream evidence: opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f
maintained OTClient: blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

The maintained client is pinned for reproducibility. The canonical `weapon-proficiency` registry declares no client path.

## Selected canonical module and final disposition

Exactly one canonical migration unit is selected:

```text
weapon-proficiency → ADAPT
```

Canonical scope includes proficiency JSON definitions, per-weapon experience/mastery lifecycle, selected-perk normalization/application, scoped player KV serialization, proficiency-side mastery achievement reconciliation and bounded combat/skill integration points.

The disposition is `ADAPT`, not `REUSE`, because the task-start target/upstream implementation contains a concrete first-gain mastery correctness defect and lacks the accepted proficiency-side mastery achievement reconciliation present in bounded legacy provenance.

The adaptation is deliberately narrower than the current legacy component. It includes the exact proven state after Canary PR #272 and before PR #288. Achievement `567` / `The Forbidden Build` and its twelve-weapon condition are not migrated because the target achievement catalogue still treats `567` as unknown/non-existent and achievement catalogue ownership is outside this package.

## Open-work overlap audit

At task start there was no open OAM-011 PR in Canary or Otheryn.

Open Canary PRs inspected before task creation were unrelated to canonical proficiency paths:

- PR #514: security runtime/workflow/tests/docs;
- PR #511: physical teleport scenario and task;
- PR #487: channel-registry portability test;
- PR #485: Windows CMake/vcpkg build configuration;
- PR #453: MyAAC/login-stack security documentation.

No ownership overlap was found with:

```text
src/creatures/players/components/weapon_proficiency.cpp
src/creatures/players/components/weapon_proficiency.hpp
data/items/proficiencies.json
tests/unit/players/components/weapon_proficiency_test.cpp
```

## Task-start provenance

| Path | Legacy Canary | Otheryn target | Upstream evidence | Reading |
|---|---|---|---|---|
| `src/creatures/players/components/weapon_proficiency.cpp` | `780d39f0c2cd0002ebd12f11a611212592217976` | `ffc01ba782093bdc4a0d9b78a29579a98fd2826a` | `ffc01ba782093bdc4a0d9b78a29579a98fd2826a` | target equals upstream; legacy differs |
| `src/creatures/players/components/weapon_proficiency.hpp` | `1ce80f1789aec6649df9943b24081f0df8f10fb2` | `9d5efd484625835ec25086b4a12e33d8e0c0efda` | `9d5efd484625835ec25086b4a12e33d8e0c0efda` | target equals upstream; legacy differs |
| `data/items/proficiencies.json` | `49ec7edc6dacdee4a055fc0f3a9544f15eafabdd` | `49ec7edc6dacdee4a055fc0f3a9544f15eafabdd` | `49ec7edc6dacdee4a055fc0f3a9544f15eafabdd` | exact identity across all three |
| `tests/unit/players/components/weapon_proficiency_test.cpp` | `756088ca70188226b2bbe96dd44f038fd6afe417` | absent | absent | legacy contains focused proof absent from target/upstream |

Blob identity was not treated as authorization and broad divergence was not treated as proof of `ADAPT` until function-level semantics were isolated.

## Function-level semantic revalidation

### First-gain mastery correctness

Task-start target/upstream `addExperience` creates the first stored entry with capped experience and returns immediately, but does not set `mastered=true` when the first gain reaches or exceeds maximum proficiency experience.

Canary PR #212 isolated and fixed that defect by introducing `createInitialState(experience, maxExperience)`, which:

- caps experience to maximum;
- sets `mastered=true` exactly when capped experience reaches maximum and maximum is non-zero;
- keeps zero-maximum state unmastered;
- exposes `getMasteredWeaponCount()` for bounded mastery accounting.

This is a real target correctness adaptation and independently rules out whole-module `REUSE`.

### Mastery achievement reconciliation

Canary PR #272 added proficiency-side, idempotent reconciliation for existing achievement IDs:

```text
1 mastered weapon  → 564
10 mastered weapons → 565
50 mastered weapons → 566
```

The component reconciles all satisfied thresholds:

- live when mastery changes `false → true`, with normal messaging;
- silently after normalized KV load, providing login-time backfill for existing mastered state.

The target already exposes `PlayerAchievement::add(id, message, ...)`, so no new achievement infrastructure or catalogue ownership is required.

### Explicitly excluded legacy delta

Canary PR #288 later added achievement `567` / `The Forbidden Build` and an exact twelve-weapon condition. OAM-011 excludes that delta because:

- target achievement registry still marks `567` as unknown/non-existent;
- adding the definition would cross into achievement catalogue ownership;
- the twelve-weapon condition is not required to repair mastery state correctness or reconcile existing 564/565/566 thresholds.

Therefore the final donor boundary is the exact Canary state after PR #272 and before PR #288.

## Exact target adaptation provenance

Otheryn target delivery: PR #29, final head `c9f060a2020c3612f65f8e31c6e745a03aa3fe5f`.

The production/test donor state is content-addressed to Canary PR #272 head `76ef99391f255653ddfb4cb16ab8a5fae239591c`:

```text
weapon_proficiency.cpp  bd3ecad2b34fa5bc731e253718ef9185d372727b
weapon_proficiency.hpp  451177df8ff3ef569f69c27dc2cd79d7d64918c8
weapon_proficiency_test.cpp  3b7310737c27b9b8865606baa4a6adfa0d324431
```

The final target diff contains exactly four paths:

```text
src/creatures/players/components/weapon_proficiency.cpp
src/creatures/players/components/weapon_proficiency.hpp
tests/unit/players/components/CMakeLists.txt
tests/unit/players/components/weapon_proficiency_test.cpp
```

`proficiencies.json`, achievement registry/catalogue, KV schema, SQL persistence, protocol, client, map and assets are unchanged.

Autofix changed only canonical CMake formatting; the final production cpp/hpp and focused test content remained the selected donor state.

## Target validation

Final exact head:

```text
c9f060a2020c3612f65f8e31c6e745a03aa3fe5f
```

Required target gates:

- autofix.ci `29634273531` — PASS;
- CI `29634273615` — PASS;
- Required `29634273523` — PASS;
- Linux debug compile — PASS;
- runtime smoke — PASS;
- database schema import — PASS;
- Linux debug `Run Tests` — PASS.

Focused proof from artifact `8426692510`:

- `WeaponProficiencyTest.InitialStateBelowMaximumIsNotMastered` — PASS;
- `WeaponProficiencyTest.InitialStateAtMaximumIsMastered` — PASS;
- `WeaponProficiencyTest.InitialStateAboveMaximumIsCappedAndMastered` — PASS;
- `WeaponProficiencyTest.ZeroMaximumNeverProducesMastery` — PASS;
- `WeaponProficiencyTest.MasteredWeaponCountIncludesOnlyMasteredEntries` — PASS;
- `WeaponProficiencyTest.EmptyStateHasNoMasteredWeapons` — PASS;
- `WeaponProficiencyTest.MasteryAchievementThresholdsAreExact` — PASS.

Full Linux debug suite: `336/336` tests PASS, `0` failures.

Artifact digest:

```text
sha256:f7602a97b67686e25f53e06974b08ee0c7646c4cba873999397437830f95c5cf
```

Final PR #29 audit: zero comments, zero reviews and zero review threads. Otheryn `main` remained at the exact task-start baseline before merge.

PR #29 squash-merged as:

```text
72f7bdc1a5afa9e9982c20bdcf3098c83dca543e
```

Target issue #28 was closed as completed after merge.

## Final architecture-boundary classification

| Boundary | Final state | Evidence |
|---|---|---|
| ownership/lifecycle | applicable, preserved | component remains owned by runtime `Player`; no ownership relocation |
| build/toolchain | applicable, adapted only for tests | one existing `canary_ut` component registration added; full target matrix passed |
| configuration | applicable, unchanged | proficiency limits and gain multiplier remain existing configuration inputs |
| service/API | applicable, minimally adapted | `getMasteredWeaponCount()` added; existing combat/perk APIs otherwise retained |
| scheduling/concurrency | no new boundary introduced | no scheduler/threading change selected; existing synchronous component/KV call paths preserved |
| persistence | applicable, preserved | existing scoped KV load/save retained; no KV schema change; OAM-004 SQL/KV non-atomicity remains authoritative |
| protocol/session | not selected for mutation | no protocol/session/client path changed; canonical module declares no client path |
| identifiers/assets | applicable, preserved | proficiency JSON exact identity retained; 564/565/566 already exist; 567 explicitly excluded |
| world/map | not applicable | no world/map ownership or mutation |
| runtime | applicable, adapted | first-gain mastery correctness and mastery reconciliation changed in target |
| tests | applicable, expanded | seven focused tests plus 336/336 full Linux debug suite passed |
| physical-client E2E | not required for selected claim | no client/protocol/UI mutation; selected mastery state and threshold claims are bounded by deterministic target unit/runtime proof |
| operations | bounded rollback available | target PR changes four paths; squash merge is independently revertible |
| security/privacy | no new boundary | no credentials, secrets or sensitive-data changes |

## Authoritative inherited boundaries preserved

1. OAM-004 `player-persistence → ADAPT`: proficiency KV remains outside any claim of SQL + KV atomicity.
2. OAM-008 `vocations → REUSE`: vocation registry remains outside OAM-011.
3. OAM-010 `character-progression → ADAPT`: shared character XP/skill/offline/death-loss ownership is not duplicated.
4. Achievement catalogue ownership remains outside OAM-011; only proficiency-side reconciliation of existing IDs 564–566 is adapted.
5. Generic combat/perk implementation remains outside scope.

## Explicit non-goals and residual gaps

- no wholesale current legacy component copy;
- no `The Forbidden Build` / achievement 567 migration;
- no achievement catalogue migration;
- no generic combat migration;
- no vocation migration;
- no Real Tibia formula/perk parity claim;
- no SQL + KV atomicity claim;
- no client fork or client mutation;
- no claim that every future proficiency achievement is automatically reconciled;
- no OAM-012 work before OAM-011 Canary feature, lifecycle and durable program reconciliation complete.

## Final disposition

```text
weapon-proficiency ADAPT
```

The clean target/upstream proficiency core is retained, with only the proven mastery correctness and existing-threshold reconciliation delta adapted. Later legacy achievement-567 behavior remains deliberately excluded.
