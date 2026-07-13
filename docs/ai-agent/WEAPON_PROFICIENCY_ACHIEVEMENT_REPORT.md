# Weapon Proficiency achievements 564–567 — evidence report

> **Runtime remediation update:** PR #212 corrects the first-entry mastery state and adds the const `WeaponProficiency::getMasteredWeaponCount()` query. Achievement awards 564–566, historical backfill and ID 567 remain intentionally outside that PR.

## Final static decision

```text
scope: read-only audit
PR: #195
runtimeModified: false
registryModified: false
assetBinaryCommitted: false
thresholdDefinitionsPresent: 3/3
thresholdAwardPathsPresent: 0/3
secretDefinitionPresent: false
secretItemProficiencyContract: 12/12 verified
```

This report separates four independent questions:

1. Is the achievement definition present?
2. Can Weapon Proficiency detect the qualifying mastery state correctly?
3. Is there an active award path and an existing-player backfill policy?
4. For secret ID 567, are every item ID and resolved proficiency assignment proven?

No runtime or registry change is authorized merely because a reference achievement exists.

## Target definitions

| ID | Canonical name | Reference condition | Active Canary definition |
|---:|---|---:|---|
| 564 | The First of Many | master 1 weapon | present |
| 565 | A Well-Honed Arsenal | master 10 weapons | present |
| 566 | Arsenal of War | master 50 weapons | present |
| 567 | The Forbidden Build | master the reviewed secret weapon set | absent |

The first three definitions exist but have no award hook. ID 567 is absent, although its complete item/proficiency data contract is now proven.

## Confirmed runtime findings

### Existing-entry mastery transition exists

For a weapon already present in the proficiency map, `WeaponProficiency::addExperience` sets `mastered=true` when the new XP reaches the computed maximum.

### Initial one-gain mastery path is incomplete

When a weapon has no existing proficiency entry, the method stores:

```cpp
proficiency.try_emplace(weaponId, std::min(experience, maxExperience));
```

and returns. A first gain equal to or greater than maximum XP can therefore store capped XP without setting `mastered=true` during that runtime transition.

Disposition: `confirmed-runtime-defect`.

### Load normalization can recover the flag

`WeaponProficiency::load()` calls `normalizeStoredState(weaponId)`, and normalization derives the mastered flag from stored XP versus maximum XP. A relog can repair the flag state, but that does not repair the missing immediate transition or award achievements automatically.

Disposition: `confirmed-backfill-input`, not yet a backfill policy.

### No mastery achievement hook

The component contains no call to the Player achievement API for IDs 564–566. No active textual award path was found elsewhere.

Disposition: `confirmed-missing-award-path` for IDs 564, 565 and 566.

### No public mastered-count API

The component exposes sorted tracked weapon IDs, but no public query returning the normalized mastered count. A future implementation needs one canonical count rather than reimplementing map iteration in multiple call sites.

Disposition: `required-runtime-contract`.

### PlayerAchievement API is available

`PlayerAchievement::add(uint16_t id, ...)` exists and is the appropriate idempotent award surface once Weapon Proficiency can evaluate normalized mastery counts.

## Secret ID 567 — verified asset/server contract

The user-provided `assets(1).zip` was read without committing or distributing binary assets. The repository stores only hashes and extracted metadata in:

```text
docs/ai-agent/WEAPON_PROFICIENCY_FORBIDDEN_BUILD_BASELINE.json
```

Source integrity:

```text
archive sha256:
01c45146e2fcec3f4087844e0cbc1817fb1d60b310a35ac5d88c07aab6f73d1a

appearances.dat sha256:
aa44a154f30c7ed59acc25f246286396e4043851ef0b54ef3cf3951e46d1ce50

asset proficiencies.json sha256:
1a915dffd9265cd1c18d39e55da7ede691b2e58add534bc186238ae028a73f22

asset/server proficiencies.json Git blob sha1:
49ec7edc6dacdee4a055fc0f3a9544f15eafabdd
```

The asset proficiency JSON is byte-identical to active `data/items/proficiencies.json`. The independent CI validator also checked every item identity and referenced proficiency ID.

| Reference name | Item ID | Proficiency ID | Active contract |
|---|---:|---:|---|
| Club of the Fury | 9385 | 245 | verified |
| Glooth Blade | 21179 | 413 | verified |
| Glutton's Mace | 9373 | 244 | verified |
| Glooth Club | 21178 | 411 | verified |
| Ice Rapier | 3284 | 161 | verified |
| Incredible Mumpiz Slayer | 9396 | 242 | verified |
| Musician's Bow | 9378 | 331 | verified |
| Ornate Carving Rod | 26073 | 162 | verified |
| Ornate Mayhem Wand | 26009 | 177 | verified |
| Pointed Rabbitslayer | 9375 | 259 | verified |
| Small Stone | 1781 | 125 | verified |
| Snowball | 2992 | 126 | verified |

All twelve names and item IDs exist in active `items.xml`. None uses an XML proficiency override; protobuf appearance metadata supplies the IDs, and all twelve definitions exist in the active 420-entry proficiency JSON.

## Machine-readable evidence

Dedicated workflow run:

```text
run: 29208968551
artifact: 8264580164
artifact sha256: 27055d467bee7da8a9e32f3bbd5a4d78c8cb09f03e995717803740112ee71696
```

Runtime audit result:

```text
definitions: 3/4
award paths: 0/3
existing transition sets mastered: true
initial creation sets mastered: false
load normalization derives mastery: true
mastered-count API present: false
PlayerAchievement add API present: true
findings: 5 errors, 2 warnings, 1 info
```

Asset/server validator result:

```text
ok: true
baseline entries: 12
verified entries: 12
active proficiency definitions: 420
findings: 0
```

The runtime audit's `forbiddenBuildEligibilityProven=0` field is intentionally XML-only. Since these items have no XML overrides, the separate protobuf/active-server validator is authoritative for ID 567 and reports 12/12.

## Required implementation order after the audit

### PR A — mastery-state correctness and query surface

- set `mastered` correctly on the first-entry XP path;
- expose a deterministic normalized mastered count;
- add focused C++ tests for first entry, existing entry, invalid item and stale stored flags;
- do not award achievements until the shared count contract is stable.

### PR B — threshold awards and historical backfill

- evaluate thresholds 1, 10 and 50 through one shared function;
- award IDs 564–566 through `PlayerAchievement::add`;
- evaluate on a false→true mastery transition;
- define and test one explicit post-load backfill point for existing players;
- prove repeated evaluation is idempotent.

### PR C — secret ID 567

- add the canonical registry definition with verified metadata;
- keep the twelve reviewed item IDs in one constant set;
- count only normalized mastered entries for those exact item IDs;
- test partial sets, all twelve, invalid/duplicate entries and existing-player backfill;
- preserve player KV compatibility.

## Runtime scenarios

Machine-readable scenarios are stored in:

```text
docs/ai-agent/WEAPON_PROFICIENCY_ACHIEVEMENT_RUNTIME_PLAN.json
```

Blocking cases include existing and initial-entry mastery, thresholds 1/10/50, repeated evaluation, historical backfill, stale flag normalization, combat/catalyst parity, the exact twelve-item secret condition and invalid proficiency data.

## Safety boundary

This audit does not modify:

- `register_achievements.lua`;
- Weapon Proficiency or PlayerAchievement C++;
- active Lua gameplay;
- player KV data;
- `items.xml`, `proficiencies.json` or protobuf assets;
- `.otbm`, client assets, database or production configuration.

## Conclusion

IDs 564–566 are defined but unobtainable through the currently inspected runtime because no award path exists. The initial-entry mastery transition has a confirmed flag defect. Existing stored XP is normalizable and can support a deliberate historical backfill, but no policy exists yet. ID 567's twelve-item asset/server eligibility contract is fully verified; implementation must still be performed in separate focused runtime and registry PRs with the supplied test plan.
