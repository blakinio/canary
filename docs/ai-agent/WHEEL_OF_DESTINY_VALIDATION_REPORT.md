# Canary Wheel of Destiny validation report

> **Snapshot:** 2026-07-12  
> **Branch:** `feat/wheel-of-destiny-validation-audit`  
> **PR:** #169  
> **Reference:** current user-requested `https://tibia.fandom.com/wiki/Wheel_of_Destiny` snapshot  
> **Evidence level:** static source analysis plus current-payload caller review; runtime, persistence round-trip, legacy payload and OTClient contract remain unverified

## Decision

The current implementation is **not yet verified as faithful**. The first GitHub Actions run successfully executed the scanner and seven focused tests against the actual PR merge, inventoried **30 Wheel-related source files** and emitted **4 errors / 6 warnings**. Subsequent caller review confirmed two former warnings as current-payload defects: the unenforced 225-gem cap and unvalidated Grade position. The enhanced scanner/test version is published; its CI result is pending.

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

## Confirmed mismatches and defects

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
- **Safe follow-up:** separate behavioral correction plus a regression test proving one application per active gem and no accumulation across recalculation.

### WOD-F004 — maximum 225 revealed gems is not enforced

- **Disposition:** `mismatch`
- **Confidence:** high for current payload
- **Reference snapshot:** a character can have at most 225 revealed gems.
- **Protocol entry:** `ProtocolGame::parseWheelGemAction()` dispatches Reveal directly from the client-supplied quality byte.
- **Runtime entry:** `PlayerWheel::revealGem()` validates vocation gem ID, item ownership and money, but never checks `m_revealedGems.size()`.
- **Impact:** a current-payload client can continue revealing gems after 225 while resources remain available.
- **Safe follow-up:** separate invariant PR with a centralized 225/226 boundary test and no resource consumption on rejection.

### WOD-F005 — ImproveGrade indexes fixed arrays using an unchecked client byte

- **Disposition:** `protocol-input-safety`
- **Confidence:** high for current payload
- **Protocol entry:** `ProtocolGame::parseWheelGemAction()` reads `position` as one byte and directly calls `improveGemGrade(fragmentType, position)`.
- **Runtime entry:** `PlayerWheel::improveGemGrade()` reads `m_basicGrades[pos]` or `m_supremeGrades[pos]` before any bounds or modifier-membership validation.
- **Bounds:** the arrays have 49 and 95 elements, while the client byte can represent 0..255.
- **Impact:** malformed current-payload input can cause out-of-bounds access/undefined behavior before grade/cost validation.
- **Safe follow-up:** separate input-hardening PR validating both array bounds and allowed modifier positions before the first read, with malformed-packet regression coverage.

## Risks requiring further evidence

### WOD-R001 — Hunting Task Shop point path not found in `getExtraPoints()`

The selected reference allows up to 50 points from the Hunting Task Shop. The direct point calculator currently exposes no visible Hunting Task source. This is a `missing-path` candidate, but all Lua, KV and award paths still need full semantic review.

### WOD-R003 — reveal and upgrade operations are not visibly atomic

`revealGem()` and `improveGemGrade()` perform item-count prechecks, then remove money before removing the required item/fragments and contain no local refund branch. Normal dispatcher execution may make failure unlikely, but fault-injection/concurrency and persistence transaction behavior remain unverified.

### WOD-R005 — duplicate topology neighbour check

The `SLOT_GREEN_TOP_100` branch checks `SLOT_GREEN_MIDDLE_100` twice. This may be harmless duplication or may replace an intended second edge. The full 36-slice adjacency graph must be compared with the compatible client/reference.

### WOD-R006 — legacy Gem Atelier payload is not yet traced

Non-current protocol profiles delegate to `Game::playerWheelGemAction`. Action, quality, index and Grade-position validation in that path still require evidence and comparison with current payload behavior.

## Caller-review result

- invalid gem indexes for destroy/switch/lock are passed through `PlayerWheel::getGem()`, which logs and returns an empty sentinel; those three operations return without modifying state;
- Reveal has no caller or runtime cap check;
- ImproveGrade does not use `getGem()` and reaches fixed arrays directly;
- invalid Reveal quality resolves to vocation gem ID 0 and is rejected, so it is not classified with F004/F005.

## Evidence still missing

- complete Dedication/Conviction/Revelation matrix for all five vocations;
- every spell augment call site and calculation stage;
- Gem Atelier fragment yields and destroy/remove behavior versus reference;
- previous-slot effective-grade gating;
- all persistence fields, migration behavior and malformed-data recovery;
- legacy payload review;
- complete inbound/outbound payload comparison with the compatible OTClient;
- focused gameplay/runtime tests.

## CI evidence

### Confirmed first run

- workflow: `Wheel of Destiny Validation`
- run: `29203018790`
- head SHA: `13c14437b40db057a094f3625215b10b4061ed6b`
- job: `Audit Wheel of Destiny and Gem Atelier` — success
- focused tests: success
- generated audit: success
- JSON validation: success
- artifact upload: success
- artifact summary: 36 slices, thresholds 250/500/1000, 5 scrolls/50 points, 30 source files, 16 doubled Revelation modifiers, 4 errors, 6 warnings

### Enhanced protocol-boundary version

- scanner commit: `36dbd278cbe032486439d1a1a17c79b9ec81a885`
- test commit: `92dc0572b14cb221dc79a6f86ae29aa50a895b2c`
- local focused tests: 7 passed
- repository CI: pending
- expected but not yet authoritative result: 6 errors / 4 warnings

## Audited source inventory

The first generated artifact records 30 paths, including Wheel components, combat/spells, player/vocation, IO, protocol, Lua bindings and Gem Atelier/reward scripts. The full machine-readable list remains in the workflow artifact `WHEEL_OF_DESTINY_AUDIT.json`.

## Audit artifacts

- `tools/ai-agent/wheel_of_destiny_validation.py`
- `tools/ai-agent/test_wheel_of_destiny_validation.py`
- `docs/ai-agent/WHEEL_OF_DESTINY_REFERENCE_BASELINE.json`
- `docs/ai-agent/WHEEL_OF_DESTINY_RUNTIME_TEST_PLAN.json`
- `.github/workflows/wheel-of-destiny-validation.yml`

## Next safe actions

1. Review the enhanced scanner's GitHub Actions run and replace expected counts with artifact-backed counts.
2. Trace legacy `Game::playerWheelGemAction`, persistence and Hunting Task point paths.
3. Compare both protocol profiles with the compatible OTClient.
4. Convert each confirmed defect into a separate focused PR only after evidence review.
5. Do not combine cost, point accounting, Revelation Mastery, cap enforcement or input hardening in one gameplay PR.
