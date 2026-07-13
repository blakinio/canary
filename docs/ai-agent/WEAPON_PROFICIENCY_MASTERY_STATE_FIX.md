# Weapon Proficiency initial mastery-state repair

PR #212 fixes one bounded runtime defect confirmed by audit #195.

## Behavior

- a first XP gain is capped at the weapon's maximum experience;
- the new state is immediately marked mastered when the capped XP reaches that maximum;
- `WeaponProficiency::getMasteredWeaponCount() const` returns the number of normalized stored states with `mastered=true`;
- existing-entry mastery, serialization and load normalization remain unchanged.

## Regression coverage

Focused C++ tests cover below, exact and above-maximum initial state, zero maximum, empty state and mixed mastered/unmastered counts. The read-only audit detector is synchronized so it no longer reports the repaired initial-state/count findings.

## Exclusions

No achievement award, IDs 564–567 registry definition, historical backfill, secret-set condition, KV schema, item/proficiency data, map, asset, database or production configuration change is included.
