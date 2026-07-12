# Canary Wheel of Destiny validation report

> **Snapshot:** 2026-07-12  
> **Branch:** `feat/wheel-of-destiny-validation-audit`  
> **PR:** #169  
> **Reference:** current user-requested `https://tibia.fandom.com/wiki/Wheel_of_Destiny` snapshot  
> **Evidence level:** static source analysis confirmed by GitHub Actions run `29203018790`; runtime, persistence round-trip and OTClient protocol remain unverified

## Decision

The current implementation is **not yet verified as faithful**. GitHub Actions successfully ran the scanner and seven focused tests against the actual PR merge. The audit inventoried **30 Wheel-related source files** and emitted **4 errors / 6 warnings**. Three high-confidence mismatches/defects and multiple risks require focused runtime or protocol evidence.

No gameplay, balance, protocol, schema, datapack, map or asset files are changed by this audit.

## Static matches

| Area | Reference | Canary evidence | Status |
|---|---:|---|---|
| Wheel topology size | 36 slices | `WheelSlots_t` defines 36 slots | `static-consistent` |
| Revelation thresholds | 250 / 500 / 1000 | `WheelStagePointsEnum_t` | `static-consistent` |
| Base points | 1 per level after 50 | `wheelPointsPerLevel = 1`; access requires level > 50 | `static-consistent` |
| Access | promoted Premium character, level 51+ | `PlayerWheel::canOpenWheel()` | `static-consistent` |
| Promotion Scrolls | maximum 50 | five server entries total 3+5+9+13+20 | `static-consistent` |
| Monk quest | maximum 10 | `wheelMonkQuestBonus = 10` | `static-consistent` |
| Temple reset | decreases only in temple | `PlayerWheel::getOptions()` | `static-consistent` |
| Reveal costs | 125k / 1m / 6m | config defaults | `static-consistent` |
| Rotate costs | 125k / 250k / 500k | config defaults | `static-consistent` |
| Basic Grade II–IV | 2m/5m/30m and 5/15/30 fragments | `getLesserGradeCost()` | `static-consistent` |
| Supreme Grade II and IV | 5m and 75m | `getGreaterGradeCost()` | `static-consistent` |
| Grade IV scaling | +50% over Grade I | grade multiplier 1.5 | `static-consistent` |

A static match is not a runtime verification.

## Confirmed static mismatches and defects

### WOD-F001 — Supreme Grade III cost is 12,000,000 instead of 12,500,000

- **Disposition:** `mismatch`
- **Confidence:** high
- **Reference snapshot:** 2026-07-12; Supreme Grade III costs 12,500,000 gold and 15 Greater Fragments.
- **Current code:** `PlayerWheel::getGreaterGradeCost()` returns 12,000,000 and 15 for internal grade 2 / displayed Grade III.
- **Impact:** every Supreme Mod Grade III upgrade is 500,000 gold cheaper than the selected reference.
- **Runtime evidence:** not yet executed.
- **Safe follow-up:** separate gameplay PR changing only the cost plus focused cost test after audit review.

### WOD-F002 — Grade IV permanent points are not added to the spendable point pool and are injected into every domain

- **Disposition:** `mismatch`
- **Confidence:** high
- **Reference snapshot:** every fully enhanced Grade IV mod grants one permanent Promotion Point; up to 69 are available from this source.
- **Current code:** `PlayerWheel::getExtraPoints()` only sums Promotion Scrolls and the Monk quest bonus. `m_modsMaxGrade` is absent from the spendable point calculation.
- **Additional current behavior:** `PlayerWheel::getPlayerSliceStage()` adds the global `m_modsMaxGrade` count to each individual domain total.
- **Impact:** Grade IV rewards cannot be spent like normal points, while the same global count can advance Revelation thresholds independently in all four domains.
- **Runtime evidence:** not yet executed.
- **Safe follow-up:** separate points-accounting PR with save/load and four-domain boundary tests.

### WOD-F003 — Revelation Mastery Supreme Mods are applied twice

- **Disposition:** `missing-correct-effect`
- **Confidence:** high
- **CI evidence:** all **16** detected Revelation Mastery cases (general plus Knight, Paladin, Druid, Sorcerer and Monk variants) are affected.
- **Current code:** each Revelation Mastery case in `WheelModifierContext::addStrategies(WheelGemSupremeModifier_t, ...)` both:
  1. queues `GemModifierRevelationStrategy`, and
  2. calls `m_wheel.addRevelationBonus(...)` immediately.
- **Execution path:** `PlayerWheel::processActiveGems()` later calls `m_modifierContext->executeStrategies()`, which executes the queued strategy and adds the same value again.
- **Impact:** affected active Supreme Mods appear to contribute twice their configured Revelation Mastery value.
- **Runtime evidence:** not yet executed.
- **Safe follow-up:** separate one-line behavioral correction plus a regression test proving one application per active gem and no accumulation across recalculation.

## Risks requiring further evidence

### WOD-R001 — Hunting Task Shop point path not found in `getExtraPoints()`

The selected reference allows up to 50 points from the Hunting Task Shop. The direct point calculator currently exposes no visible Hunting Task source. This is a `missing-path` candidate, but all Lua, KV and protocol award paths still need full semantic review.

### WOD-R002 — 225 revealed-gem cap is not enforced inside `revealGem()`

The direct reveal method has no visible size comparison against 225. A caller may enforce the cap elsewhere; protocol handlers and all call sites must be audited before classifying this as a confirmed defect.

### WOD-R003 — reveal and upgrade operations are not visibly atomic

`revealGem()` and `improveGemGrade()` remove money before removing the required item/fragments and contain no local refund branch. Prechecks may make normal failure unlikely, but race/failure behavior and persistence transactions require runtime fault-injection tests.

### WOD-R004 — client-supplied grade position may be indexed before bounds validation

`improveGemGrade()` accesses `m_basicGrades[pos]` or `m_supremeGrades[pos]` before a visible bounds/membership guard. The protocol parser must be checked to determine whether malformed input can reach this method.

### WOD-R005 — duplicate topology neighbour check

The `SLOT_GREEN_TOP_100` branch checks `SLOT_GREEN_MIDDLE_100` twice. This may be harmless duplication or may replace an intended second edge. The full 36-slice adjacency graph must be compared with the compatible client/reference.

## Evidence still missing

- complete Dedication/Conviction/Revelation matrix for all five vocations;
- every spell augment call site and calculation stage;
- Gem Atelier fragment yields and destroy/remove behavior;
- previous-slot effective-grade gating;
- all persistence fields, migration behavior and malformed-data recovery;
- complete inbound/outbound opcode and payload comparison with the compatible OTClient;
- focused gameplay/runtime tests;

## CI evidence

- workflow: `Wheel of Destiny Validation`
- run: `29203018790`
- head SHA: `13c14437b40db057a094f3625215b10b4061ed6b`
- job: `Audit Wheel of Destiny and Gem Atelier` — success
- focused tests: success
- generated audit: success
- JSON validation: success
- artifact upload: success
- artifact summary: 36 slices, thresholds 250/500/1000, 5 scrolls/50 points, 30 source files, 16 doubled Revelation modifiers, 4 errors, 6 warnings

## Audited source inventory

The generated artifact records 30 paths, including Wheel components, combat/spells, player/vocation, IO, protocol, Lua bindings and Gem Atelier/reward scripts. The full machine-readable list remains in the workflow artifact `WHEEL_OF_DESTINY_AUDIT.json`.

## Audit artifacts

- `tools/ai-agent/wheel_of_destiny_validation.py`
- `tools/ai-agent/test_wheel_of_destiny_validation.py`
- `docs/ai-agent/WHEEL_OF_DESTINY_REFERENCE_BASELINE.json`
- `docs/ai-agent/WHEEL_OF_DESTINY_RUNTIME_TEST_PLAN.json`
- `.github/workflows/wheel-of-destiny-validation.yml`

## Next safe actions

1. Retain and review the successful GitHub Actions JSON/Markdown artifact when the scanner changes.
2. Finish the protocol, persistence and call-site inventory.
3. Convert each confirmed defect into a separate focused PR only after evidence review.
4. Do not combine balance corrections, point accounting and Revelation Mastery behavior in one gameplay PR.
