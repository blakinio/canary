# Canary Imbuement Validation Report

> **Status:** static evidence collected; deterministic audits implemented; runtime scenarios not yet executed  
> **Observed:** 2026-07-12  
> **Writable repository:** `blakinio/canary`  
> **Reference:** <https://tibia.fandom.com/wiki/Imbuing>  
> **Task:** `CAN-20260712-imbuement-validation`  
> **Pull request:** #166

## 1. Purpose

This report validates Canary's active Imbuing definitions and runtime wiring against the TibiaWiki/Fandom Imbuing reference observed on 2026-07-12.

It follows `OTS_AI_WORLD_VALIDATION_PROJECT.md` and keeps the validation layers separate:

1. XML and registry structure;
2. static references and registrations;
3. semantic agreement between XML, C++, Lua, storage declarations and the reference;
4. machine-readable runtime scenarios;
5. later gameplay regression tests.

This PR is read-only. It does not modify `data/XML/imbuements.xml`, active scripts, item definitions, engine behavior, map files, client assets or production configuration. Confirmed gameplay changes must be delivered in separate focused PRs.

## 2. Sources inspected

### Active registry and runtime

- `data/XML/imbuements.xml`;
- `src/creatures/players/imbuements/imbuements.{hpp,cpp}`;
- `src/creatures/players/imbuements/imbuement_storage_policy.hpp`;
- `src/creatures/players/player.{hpp,cpp}`;
- `src/game/game.cpp`;
- `src/items/item.{hpp,cpp}`;
- `src/lua/functions/items/imbuement_functions.cpp`;
- `src/lua/functions/creatures/player/player_functions.cpp`;
- `data-otservbr-global/scripts/actions/object/imbuement_shrine.lua`;
- `data-otservbr-global/scripts/actions/object/imbuement_scrolls.lua`;
- `data-otservbr-global/scripts/actions/object/etcher.lua`;
- `data-otservbr-global/lib/core/storages.lua`;
- `data-otservbr-global/scripts/quests/forgotten_knowledge/creaturescripts_bosses_kill.lua`;
- `config.lua.dist`.

### External reference

The referenced TibiaWiki/Fandom page was observed on 2026-07-12. The audit records mechanics, numeric values, item IDs/counts and source links. It does not copy spoiler prose into the repository.

## 3. Deterministic baseline

| Dimension | Active Canary baseline |
|---|---:|
| Base tiers | 3 |
| Categories | 20 (`0..19`) |
| Imbuement families | 24 |
| Tier entries | 72 |
| XML-mapped Intricate/Powerful scrolls | 46 |
| Scroll item IDs registered by active Lua | 48 |
| Duration per tier | 72,000 seconds / 20 hours |
| Shrine clear cost | 15,000 gold |
| Distinct nonzero XML unlock storage IDs | 7 |
| Powerful families using nonzero XML storage | 22 |
| Powerful families using `storage=0` | 2 |
| Default storage filtering | disabled |

The registry contains one Basic, Intricate and Powerful entry for every family. No duplicate base IDs, category IDs, family/tier pairs, source item IDs within one entry or XML scroll IDs were found.

## 4. Overall result

The active Imbuing system is structurally complete and its major runtime paths are connected. Most effects, creature-product requirements, durations, clearing behavior and scroll mappings agree with the current reference.

The audit found six material discrepancy groups:

1. the application fee/success model differs from the current reference;
2. all three Strike tiers use different critical values;
3. Basic Punch uses a different source item and count;
4. Intricate and Powerful Vibrancy scrolls are registered in Lua but cannot resolve through XML;
5. all seven nonzero Powerful unlock storage IDs are absent from the active storage registry, affecting 22 families;
6. Powerful Featherweight and Vibrancy use `storage=0`, so they bypass family-specific filtering.

The storage defect is configuration-dependent but broad. The default configuration disables storage filtering, which hides the defect. When filtering is enabled, the policy hides an entry whenever its configured storage reads `-1`. Undeclared IDs therefore leave the 22 affected Powerful families hidden, while the two zero-storage families remain visible without their documented unlocks.

## 5. Findings

### IMB-001 — application fee and success model differs

**Disposition:** `reference-mismatch; target-version decision required`  
**Confidence:** high

| Tier | Active attempt price | Active success | Active protection | Active guaranteed total | Current reference fee |
|---|---:|---:|---:|---:|---:|
| Basic | 5,000 | 90% | 10,000 | 15,000 | 7,500 |
| Intricate | 30,000 | 70% | 30,000 | 60,000 | 60,000 |
| Powerful | 200,000 | 50% | 50,000 | 250,000 | 250,000 |

The current reference describes one fixed price rather than a chance plus optional protection. Intricate and Powerful guaranteed totals happen to equal the current fees; Basic does not.

Do not patch this automatically. First decide whether the server intentionally targets the historical chance/protection economy or the current fixed-price economy. That decision affects protocol presentation, charging logic, tests and balance.

### IMB-002 — Strike critical values differ in every tier

**Disposition:** `confirmed-data-mismatch`  
**Confidence:** high

| Tier | Active XML | Current reference |
|---|---|---|
| Basic | 10% chance, +15% damage | 5% chance, +5% damage |
| Intricate | 10% chance, +25% damage | 5% chance, +15% damage |
| Powerful | 10% chance, +50% damage | 5% chance, +40% damage |

The XML loader stores these values directly in the critical chance/damage skill fields. No reviewed runtime correction layer replaces them.

A separate data-fix PR should update the effect values and descriptions together, then add focused combat tests.

### IMB-003 — Basic Punch uses a different creature product

**Disposition:** `confirmed-data-mismatch`  
**Confidence:** high

| Tier | Active XML | Current reference chain |
|---|---|---|
| Basic | item `9690` ×20 | item `10281` ×25 |
| Intricate | item `10281` ×25 + item `11489` ×20 | same |
| Powerful | previous sources + item `40529` ×15 | same |

Only Basic Punch differs. Intricate and Powerful already start with the current Basic source, reinforcing that the Basic row is stale rather than a deliberate alternate chain.

### IMB-004 — Vibrancy scrolls are registered but unmapped

**Disposition:** `confirmed-runtime-defect`  
**Confidence:** high

The active scroll action registers both complete ranges:

- Powerful: `51444..51467`;
- Intricate: `51724..51747`.

Therefore it registers Powerful Vibrancy scroll `51466` and Intricate Vibrancy scroll `51746`. `data/XML/imbuements.xml` contains no `scroll` attribute for either Vibrancy tier. `Imbuements::getImbuementByScrollID()` can only resolve IDs inserted into the XML-derived scroll map, so these two registered actions have no target imbuement.

This is a narrow follow-up fix: add the two mappings in a dedicated PR and cover successful application, invalid target, occupied category and consumption atomicity.

### IMB-005 — nonzero Powerful unlock storages are stale

**Disposition:** `confirmed-configuration-dependent-runtime-defect`  
**Confidence:** high

The XML uses these seven nonzero storage IDs:

```text
50488, 50490, 50492, 50494, 50496, 50498, 50501
```

None is declared in the active `storages.lua`. They affect 22 Powerful families:

| XML storage | Affected families |
|---:|---|
| 50488 | Reap, Vampirism, Lich Shroud |
| 50490 | Electrify, Cloud Fabric, Swiftness |
| 50492 | Venom, Snake Skin, Chop, Slash, Bash, Punch |
| 50494 | Scorch, Void, Dragon Hide |
| 50496 | Frost, Quara Scale, Blockade |
| 50498 | Demon Presence, Precision |
| 50501 | Strike, Epiphany |

The active Forgotten Knowledge boss path instead uses named storages with current IDs:

| Active storage | Boss/unlock group |
|---:|---|
| 45489 | Lady Tenebris |
| 45490 | Lloyd |
| 45491 | Thorn Knight |
| 45492 | Dragonking |
| 45493 | Frozen Horror |
| 45494 | Time Guardian |
| 45495 | Last Lore Keeper |

The family grouping creates a strong one-to-one semantic correspondence between each stale XML group and these current boss storages. A data-fix PR should still verify the mapping explicitly and add before/after unlock tests rather than replacing IDs blindly.

`toggleImbuementShrineStorage` is disabled by default. With filtering disabled, the stale IDs are dormant. With filtering enabled, `ImbuementStoragePolicy::shouldHide()` reads each stale ID and hides the entry while it remains `-1`; active boss kills write different storage IDs, so the documented unlock cannot reveal those 22 entries.

### IMB-006 — Powerful Featherweight and Vibrancy bypass unlock filtering

**Disposition:** `confirmed-reference-mismatch; exact completion condition unresolved`  
**Confidence:** high for bypass, medium for the final replacement storage/value

Powerful Featherweight and Powerful Vibrancy use `storage="0"`. The storage policy explicitly does not hide zero-storage entries. They therefore remain visible when family-specific filtering is enabled, despite the current reference requiring:

- Dangerous Depths for Powerful Featherweight;
- Dream Courts for Powerful Vibrancy.

Dangerous Depths has active storage declarations beginning at questline `45851`, but the exact completion condition that should unlock Featherweight has not yet been proven. The same evidence step remains for Dream Courts/Vibrancy. Do not invent either replacement ID or value.

## 6. Confirmed conforming behavior

The static audit confirms:

- 20-hour duration for all three tiers;
- 15,000-gold clearing cost for every tier;
- Basic, Intricate and Powerful definitions for all 24 families;
- all non-Strike effect values match the current reference baseline used by the scanner;
- all material chains except Basic Punch match that baseline;
- all scroll mappings except Vibrancy match the active contiguous Lua ranges;
- the shrine has a common access gate when storage filtering is enabled;
- PR #86 corrected the policy to read the configured storage ID rather than a boolean expression;
- item filtering uses item-declared categories/tiers and rejects a second imbuement from an occupied category;
- Etcher item `51443` calls `clearAllImbuements`, is consumed only after a successful clear and reports failure otherwise;
- combat and non-combat duration policies are implemented separately;
- the decay scheduler persists remaining seconds on the item and removes expired stats.

The policy implementation is correct for valid storage IDs; the current defect is the XML-to-storage wiring.

## 7. Deterministic tools

### Registry and runtime audit

```text
tools/ai-agent/imbuement_validation.py
```

Checks XML structure, effects, materials, costs, duration, scroll registration and required runtime paths.

### Storage wiring audit

```text
tools/ai-agent/imbuement_storage_validation.py
```

Checks:

- every nonzero XML storage against active Lua declarations;
- affected Powerful families;
- zero-storage bypasses;
- default filtering configuration;
- current Forgotten Knowledge named-storage wiring.

The focused workflow publishes both JSON reports as artifacts.

## 8. Runtime test plan

`docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json` defines bounded scenarios for:

- shrine and common access;
- Powerful unlock storage mapping;
- account/tier rules;
- charging and resource atomicity;
- Strike effects;
- Punch materials;
- Vibrancy scrolls;
- duplicate category rejection;
- shrine and Etcher clearing;
- combat and non-combat duration consumption;
- save/logout/login persistence;
- item eligibility.

The most important invariant is atomicity: a rejected or failed application must not consume gold, source items or scrolls, and a successful application must consume each required resource exactly once.

## 9. Limitations

This audit does **not** yet prove:

- real Canary startup without imbuement warnings in the user's deployment configuration;
- complete current-reference parity for every individual imbuable equipment item;
- exact protocol/UI presentation for every supported client profile;
- the exact Dangerous Depths and Dream Courts completion storage/value for Featherweight and Vibrancy;
- end-to-end combat math under live gameplay;
- save/load persistence through a real database.

No server, database or game client was available in the connector environment. These gaps are represented in the runtime plan rather than marked as passed.

## 10. Recommended delivery order

1. **Repair Powerful unlock storage wiring** in a focused data + regression-test PR after confirming the seven current Forgotten Knowledge mappings and the two external quest completion conditions.
2. **Fix Vibrancy scroll mappings** in a narrow XML + focused-test PR.
3. **Confirm the target Tibia economy/version** before changing the fee/success model.
4. **Fix Strike and Basic Punch** in a separate data-fidelity PR with combat/inventory tests.
5. **Execute the runtime plan** in controlled Canary staging and retain the report as a CI artifact.
6. **Add equipment eligibility parity** as a separate audit using `items.xml` and item metadata.

## 11. Reproduction

```bash
python -m py_compile \
  tools/ai-agent/imbuement_validation.py \
  tools/ai-agent/imbuement_storage_validation.py \
  tools/ai-agent/test_imbuement_validation.py \
  tools/ai-agent/test_imbuement_storage_validation.py

python -m unittest discover \
  -s tools/ai-agent \
  -p 'test_imbuement*_validation.py' \
  -v

python tools/ai-agent/imbuement_validation.py \
  --repository-root . \
  --output artifacts/IMBUEMENT_VALIDATION.json \
  --runtime-plan artifacts/IMBUEMENT_RUNTIME_TEST_PLAN.json

python tools/ai-agent/imbuement_storage_validation.py \
  --repository-root . \
  --output artifacts/IMBUEMENT_STORAGE_VALIDATION.json
```

Known reference and storage discrepancies are audit evidence, so default report generation returns success. Strict modes are available for targeted CI or follow-up validation after the defects are repaired.
