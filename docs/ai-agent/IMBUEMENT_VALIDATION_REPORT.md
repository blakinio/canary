# Canary Imbuement Validation Report

> **Status:** evidence collected; static audit implemented; runtime scenarios not yet executed  
> **Observed:** 2026-07-12  
> **Writable repository:** `blakinio/canary`  
> **Reference:** <https://tibia.fandom.com/wiki/Imbuing>  
> **Task:** `CAN-20260712-imbuement-validation`  
> **Pull request:** #166

## 1. Purpose

This report validates Canary's active Imbuing definitions and their runtime wiring against the current TibiaWiki/Fandom Imbuing reference.

It follows `OTS_AI_WORLD_VALIDATION_PROJECT.md` and keeps the validation layers separate:

1. XML structure;
2. static references and registrations;
3. semantic agreement between XML, C++, Lua and the reference;
4. a machine-readable runtime scenario plan;
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
- `data-otservbr-global/scripts/actions/object/etcher.lua`.

### External reference

The referenced TibiaWiki/Fandom page was observed on 2026-07-12. The audit records only mechanics, numeric values, item IDs/counts and source links. It does not copy spoiler prose into the repository.

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

The registry has one Basic, Intricate and Powerful entry for every family. No duplicate base IDs, category IDs, family/tier pairs, source item IDs within one entry, or XML scroll IDs were found in the reviewed baseline.

## 4. Overall result

The active Imbuing system is structurally complete and its major runtime paths are connected. Most effects, creature-product requirements, durations, clearing behavior and scroll mappings agree with the current reference.

The audit found six distinct discrepancy groups:

1. the application fee/success model differs from the current reference;
2. all three Strike tiers use outdated critical values;
3. Basic Punch uses a different source item and count;
4. Intricate and Powerful Vibrancy scrolls are registered in Lua but cannot resolve through XML;
5. Powerful Featherweight has no unlock storage;
6. Powerful Vibrancy has no unlock storage.

The Vibrancy scroll gap is a directly demonstrated cross-file runtime defect. The remaining discrepancies are high-confidence reference mismatches, but their fixes must be split by concern and must not be mixed into this audit PR.

## 5. Findings

### IMB-001 — application fee and success model differs

**Disposition:** `reference-mismatch; target-version decision required`  
**Confidence:** high

Current XML:

| Tier | Attempt price | Success | Protection | Guaranteed total |
|---|---:|---:|---:|---:|
| Basic | 5,000 | 90% | 10,000 | 15,000 |
| Intricate | 30,000 | 70% | 30,000 | 60,000 |
| Powerful | 200,000 | 50% | 50,000 | 250,000 |

Current referenced values:

| Tier | Fixed fee |
|---|---:|
| Basic | 7,500 |
| Intricate | 60,000 |
| Powerful | 250,000 |

The current reference describes one fixed price rather than a chance plus optional protection. Intricate and Powerful guaranteed totals happen to equal the reference fees; Basic does not.

Do not patch this automatically. First decide whether the server intentionally targets the historical chance/protection economy or the current fixed-price economy. That decision affects protocol presentation, charging logic, tests and balance.

### IMB-002 — Strike critical values differ in every tier

**Disposition:** `confirmed-data-mismatch`  
**Confidence:** high

| Tier | Active XML | Current reference |
|---|---|---|
| Basic | 10% chance, +15% damage | 5% chance, +5% damage |
| Intricate | 10% chance, +25% damage | 5% chance, +15% damage |
| Powerful | 10% chance, +50% damage | 5% chance, +40% damage |

The XML loader stores these values directly in critical chance/damage skill fields. No reviewed runtime correction layer replaces them.

A separate data-fix PR should update the effect values and descriptions together, then add focused combat tests.

### IMB-003 — Basic Punch uses a different creature product

**Disposition:** `confirmed-data-mismatch`  
**Confidence:** high

| Tier | Active XML | Current reference chain |
|---|---|---|
| Basic | item `9690` ×20 | item `10281` ×25 |
| Intricate | item `10281` ×25 + item `11489` ×20 | same |
| Powerful | previous sources + item `40529` ×15 | same |

Only Basic Punch differs. Intricate and Powerful already start with the current Basic source, which reinforces that the Basic row is stale rather than a deliberate alternate chain.

A separate data-fix PR should change the Basic source and add an inventory-consumption regression test.

### IMB-004 — Vibrancy scrolls are registered but unmapped

**Disposition:** `confirmed-runtime-defect`  
**Confidence:** high

The active scroll action registers both complete ranges:

- Powerful: `51444..51467`;
- Intricate: `51724..51747`.

Therefore it registers:

- Powerful Vibrancy scroll `51466`;
- Intricate Vibrancy scroll `51746`.

`data/XML/imbuements.xml` contains no `scroll` attribute for Intricate or Powerful Vibrancy. `Imbuements::getImbuementByScrollID()` can only resolve IDs inserted into the XML-derived scroll map, so these two registered item actions have no target imbuement.

This is the smallest and least ambiguous follow-up fix: add the two mappings in a dedicated PR and cover successful application, invalid target, occupied category and consumption atomicity.

### IMB-005 — Powerful Featherweight has no unlock storage

**Disposition:** `reference-mismatch; configuration-dependent gameplay defect`  
**Confidence:** high

The current reference requires the Dangerous Depths unlock for Powerful Featherweight. The active XML stores `storage="0"`, which the storage policy treats as not having a family-specific gate.

When shrine storage filtering is enabled, the common shrine gate still applies, but this entry cannot enforce the documented Powerful Featherweight unlock independently.

The follow-up must first identify and verify the exact existing quest storage and completion value. Do not invent a storage ID.

### IMB-006 — Powerful Vibrancy has no unlock storage

**Disposition:** `reference-mismatch; configuration-dependent gameplay defect`  
**Confidence:** high

The current reference requires the Dream Courts unlock for Powerful Vibrancy. The active XML stores `storage="0"`.

As with Featherweight, the common shrine gate is not equivalent to the documented family-specific Powerful unlock. The exact active quest storage must be traced and verified before changing XML.

## 6. Confirmed conforming behavior

The static audit confirms the following current behavior:

- 20-hour duration is configured for all three tiers;
- clearing one slot costs 15,000 gold for all tiers;
- every family has Basic, Intricate and Powerful definitions;
- all non-Strike effect values match the current reference baseline used by the scanner;
- all material chains except Basic Punch match that baseline;
- all scroll mappings except Vibrancy match the active contiguous Lua ranges;
- the shrine action has a common Forgotten Knowledge gate when storage filtering is enabled;
- the merged storage-policy correction from PR #86 reads the configured storage ID rather than a boolean expression;
- item filtering uses item-declared categories/tiers and rejects a second imbuement from an already occupied category;
- Etcher item `51443` calls `clearAllImbuements`, is consumed only after a successful clear, and reports failure otherwise;
- combat and non-combat duration policies are implemented separately;
- the decay scheduler persists remaining seconds on the item and removes expired stats.

These are static and semantic confirmations. They do not replace a real server/client gameplay run.

## 7. Runtime test plan

`docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json` defines bounded scenarios for:

- shrine and storage access;
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

## 8. Limitations

This audit does **not** yet prove:

- that a real Canary process loads the registry without runtime warnings in the user's deployment configuration;
- complete current-reference parity for every individual imbuable equipment item;
- exact protocol/UI presentation for every supported client profile;
- exact quest completion storage values for Featherweight and Vibrancy;
- end-to-end combat math under live gameplay;
- save/load persistence through a real database.

No server, database or game client was available in the GitHub connector environment. These gaps are explicitly represented in the runtime plan rather than marked as passed.

## 9. Recommended delivery order

1. **Fix Vibrancy scroll mappings** in a narrow XML + focused-test PR.
2. **Confirm target Tibia economy/version** before changing the fee/success model.
3. **Fix Strike and Basic Punch** in a separate data-fidelity PR with combat/inventory tests.
4. **Trace exact existing storages** for Dangerous Depths and Dream Courts, then gate Powerful Featherweight/Vibrancy in a focused PR.
5. **Execute the runtime plan** in controlled Canary staging and retain the report as a CI artifact.
6. **Add equipment eligibility parity** as a separate audit using `items.xml` and item metadata.

## 10. Reproduction

```bash
python -m py_compile \
  tools/ai-agent/imbuement_validation.py \
  tools/ai-agent/test_imbuement_validation.py

python -m unittest tools/ai-agent/test_imbuement_validation.py -v

python tools/ai-agent/imbuement_validation.py \
  --repository-root . \
  --output artifacts/IMBUEMENT_VALIDATION.json \
  --runtime-plan artifacts/IMBUEMENT_RUNTIME_TEST_PLAN.json
```

Known reference discrepancies are report data, so the default invocation returns success after a valid audit. CI can use `--fail-on error` to fail on broken structure or runtime wiring while preserving reviewed reference mismatches as evidence.
