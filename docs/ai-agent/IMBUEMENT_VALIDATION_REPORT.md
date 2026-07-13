# Canary Imbuement Validation Report

> **Status:** static evidence collected; IMB-005 repaired by PR #206; runtime scenarios not yet executed  
> **Observed:** 2026-07-12  
> **Writable repository:** `blakinio/canary`  
> **Reference:** <https://tibia.fandom.com/wiki/Imbuing>  
> **Audit PR:** #166  
> **Storage repair PR:** #206

## 1. Purpose and evidence boundary

This report validates Canary's active Imbuing definitions and runtime wiring and records the focused repair of the Forgotten Knowledge Powerful unlock storages.

Evidence layers remain separate:

1. XML and registry structure;
2. static registrations and references;
3. semantic agreement between XML, C++, Lua, storage declarations and the external reference;
4. machine-readable runtime scenarios;
5. later live gameplay and persistence regression tests.

PR #166 was a read-only audit. PR #206 changes only the seven nonzero Powerful storage groups in `data/XML/imbuements.xml`, the deterministic validator/tests, focused workflow and documentation. It does not change fees, effects, materials, scroll mappings, boss scripts, storage declarations, engine code, map files, item binaries, client assets, protocol or production configuration.

## 2. Sources inspected

- `data/XML/imbuements.xml`;
- `src/creatures/players/imbuements/imbuements.{hpp,cpp}`;
- `src/creatures/players/imbuements/imbuement_storage_policy.hpp`;
- `src/creatures/players/player.{hpp,cpp}`;
- `src/game/game.cpp`;
- `src/items/item.{hpp,cpp}`;
- `src/lua/functions/items/imbuement_functions.cpp`;
- `src/lua/functions/creatures/player/player_functions.cpp`;
- active shrine, scroll and Etcher actions;
- `data-otservbr-global/lib/core/storages.lua`;
- `data-otservbr-global/scripts/quests/forgotten_knowledge/creaturescripts_bosses_kill.lua`;
- `config.lua.dist`;
- the TibiaWiki/Fandom Imbuing page observed on 2026-07-12.

The report records mechanics and numeric evidence without copying spoiler prose.

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
| Distinct nonzero Powerful storage IDs | 7 |
| Powerful families using nonzero storage | 22 |
| Powerful families using `storage=0` | 2 |
| Default storage filtering | disabled |

The registry contains one Basic, Intricate and Powerful entry for every family. No duplicate base IDs, category IDs, family/tier pairs, source item IDs within one entry or XML scroll IDs were found.

## 4. Current result

The active system is structurally complete and its major runtime paths are connected. PR #206 repairs the broad Forgotten Knowledge storage-wiring defect found by the audit.

Remaining material discrepancy groups are:

1. the application fee/success model differs from the observed current reference;
2. all three Strike tiers use different critical values;
3. Basic Punch uses a different source item and count;
4. Intricate and Powerful Vibrancy scrolls are registered in Lua but cannot resolve through XML;
5. Powerful Featherweight and Vibrancy use `storage=0`, so they bypass family-specific filtering.

## 5. Findings

### IMB-001 — application fee and success model differs

**Disposition:** `reference-mismatch; target-version decision required`  
**Confidence:** high

| Tier | Active attempt price | Active success | Active protection | Active guaranteed total | Observed reference fee |
|---|---:|---:|---:|---:|---:|
| Basic | 5,000 | 90% | 10,000 | 15,000 | 7,500 |
| Intricate | 30,000 | 70% | 30,000 | 60,000 | 60,000 |
| Powerful | 200,000 | 50% | 50,000 | 250,000 | 250,000 |

Do not patch this automatically. The server must first choose whether it targets the historical chance/protection economy or the current fixed-fee economy.

### IMB-002 — Strike critical values differ

**Disposition:** `confirmed-data-mismatch`  
**Confidence:** high

| Tier | Active XML | Observed reference |
|---|---|---|
| Basic | 10% chance, +15% damage | 5% chance, +5% damage |
| Intricate | 10% chance, +25% damage | 5% chance, +15% damage |
| Powerful | 10% chance, +50% damage | 5% chance, +40% damage |

The loader stores these values directly. No reviewed runtime layer replaces them.

### IMB-003 — Basic Punch source differs

**Disposition:** `confirmed-data-mismatch`  
**Confidence:** high

| Tier | Active XML | Observed reference chain |
|---|---|---|
| Basic | item `9690` ×20 | item `10281` ×25 |
| Intricate | item `10281` ×25 + item `11489` ×20 | same |
| Powerful | previous sources + item `40529` ×15 | same |

Only Basic Punch differs.

### IMB-004 — Vibrancy scrolls are registered but unmapped

**Disposition:** `confirmed-runtime-defect`  
**Confidence:** high

The active Lua action registers Powerful range `51444..51467` and Intricate range `51724..51747`. Therefore IDs `51466` and `51746` are registered, but neither Vibrancy tier has a `scroll` attribute in XML. `getImbuementByScrollID()` cannot resolve either item.

A separate PR must add both mappings and test successful application, invalid targets, occupied categories and consumption atomicity.

### IMB-005 — Forgotten Knowledge Powerful storages repaired

**Disposition:** `repaired-by-pr-206`  
**Confidence:** high

The original audit found seven undeclared XML storage IDs:

```text
50488, 50490, 50492, 50494, 50496, 50498, 50501
```

They affected 22 Powerful families. PR #206 maps every group to the active storage written by the corresponding Forgotten Knowledge boss path:

| Active storage | Boss/unlock group | Powerful families |
|---:|---|---|
| 45489 | Lady Tenebris | Reap, Vampirism, Lich Shroud |
| 45490 | Lloyd | Electrify, Cloud Fabric, Swiftness |
| 45491 | Thorn Knight | Venom, Snake Skin, Chop, Slash, Bash, Punch |
| 45492 | Dragonking | Scorch, Void, Dragon Hide |
| 45493 | Frozen Horror | Frost, Quara Scale, Blockade |
| 45494 | Time Guardian | Demon Presence, Precision |
| 45495 | Last Lore Keeper | Strike, Epiphany |

The replacement counts are exactly `3/3/6/3/3/2/2`, totaling 22 entries. Every unrelated XML attribute is preserved.

The focused validator now:

- rejects every legacy ID;
- rejects undeclared nonzero Imbuement storages;
- verifies the exact family-to-storage grouping;
- verifies the active boss storage tokens;
- runs in `--strict` mode in CI.

With storage filtering enabled, a boss kill now writes the same storage ID read by the corresponding Powerful entry.

### IMB-006 — Featherweight and Vibrancy bypass filtering

**Disposition:** `confirmed-reference-mismatch; exact completion condition unresolved`  
**Confidence:** high for the bypass, medium for any future replacement storage/value

Powerful Featherweight and Powerful Vibrancy still use `storage="0"`. The policy intentionally does not hide zero-storage entries, so they remain visible when family-specific filtering is enabled.

The observed reference requires Dangerous Depths for Powerful Featherweight and Dream Courts for Powerful Vibrancy. The exact active completion storage and value for each quest have not yet been proven. Do not invent either mapping.

## 6. Confirmed conforming behavior

Static evidence confirms:

- 20-hour duration for all tiers;
- 15,000-gold clearing cost;
- Basic, Intricate and Powerful definitions for all 24 families;
- all non-Strike effect values match the scanner baseline;
- all material chains except Basic Punch match that baseline;
- all scroll mappings except Vibrancy match the active Lua ranges;
- the shrine has a common access gate when storage filtering is enabled;
- PR #86 corrected the storage policy to read the configured storage ID;
- item filtering uses item-declared categories/tiers and rejects an occupied category;
- Etcher item `51443` clears all Imbuements and is consumed only after success;
- combat and non-combat duration policies are separate;
- the decay scheduler persists remaining seconds and removes expired stats;
- the Forgotten Knowledge Powerful family groups now use declared, actively written storages.

## 7. Deterministic tools and CI

### Registry/runtime audit

```text
tools/ai-agent/imbuement_validation.py
```

Checks XML structure, effects, materials, costs, duration, scroll registration and required runtime markers.

### Storage-wiring audit

```text
tools/ai-agent/imbuement_storage_validation.py
```

Checks declared storage IDs, legacy IDs, exact Forgotten Knowledge family groups, zero-storage bypasses, filtering defaults and boss-write wiring.

### Focused workflow

```text
.github/workflows/imbuement-validation.yml
```

The workflow compiles both validators/tests, runs all focused tests, generates registry/storage/runtime-plan JSON, validates JSON syntax and executes the storage audit in strict mode.

## 8. Runtime test plan

`docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json` retains bounded scenarios for:

- shrine/common access;
- Powerful unlock visibility before and after each boss storage;
- account/tier rules;
- charging and resource atomicity;
- Strike effects;
- Punch materials;
- Vibrancy scrolls;
- duplicate-category rejection;
- shrine and Etcher clearing;
- combat/non-combat duration consumption;
- save/logout/login persistence;
- item eligibility.

A rejected or failed application must not consume gold, source items or scrolls; a successful application must consume each required resource exactly once.

## 9. Limitations

This work does not yet prove:

- real Canary startup in the user's deployment configuration;
- live before/after shrine visibility for all seven boss groups;
- full equipment eligibility parity;
- exact protocol/UI presentation for every supported client profile;
- the Dangerous Depths and Dream Courts completion conditions;
- end-to-end combat math;
- real database save/load persistence.

These remain runtime scenarios, not passed claims.

## 10. Recommended delivery order

1. Prove the exact Dangerous Depths and Dream Courts completion conditions before assigning Featherweight/Vibrancy storages.
2. Fix Vibrancy scroll mappings in a narrow XML/test PR.
3. Decide the target Imbuing economy/version before changing fees or success logic.
4. Fix Strike and Basic Punch in a separate data-fidelity PR.
5. Execute the runtime plan in controlled Canary staging.
6. Audit full equipment eligibility against item metadata.

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
  --output artifacts/IMBUEMENT_STORAGE_VALIDATION.json \
  --strict
```
