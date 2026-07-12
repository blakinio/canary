# Canary Wheel of Destiny validation report

> **Snapshot:** 2026-07-12  
> **Branch:** `feat/wheel-of-destiny-validation-audit`  
> **Draft PR:** #169  
> **Reference:** `https://tibia.fandom.com/wiki/Wheel_of_Destiny`, checked 2026-07-12  
> **Evidence:** static source analysis, current + legacy caller-boundary analysis, focused parser tests; runtime and compatible-client contract remain unverified.

## Decision

Canary's Wheel of Destiny is **not yet verified as faithful**. The audit has five confirmed static/caller-boundary findings and three unresolved risks. This PR changes only documentation, tools, tests and CI.

## Confirmed static matches

- 36 slices;
- Revelation thresholds 250 / 500 / 1000;
- level 51+, promoted Premium access;
- 1 point per level after 50;
- five Promotion Scrolls totaling 50;
- Monk quest bonus 10;
- temple-only point decrease/reset;
- reveal costs 125k / 1m / 6m;
- rotate costs 125k / 250k / 500k;
- Basic Grade II–IV costs;
- Supreme Grade II and IV costs;
- Grade IV multiplier 1.5.

These are `static-consistent`, not runtime verified.

## Confirmed findings

### WOD-F001 — Supreme Grade III cost mismatch

- expected: 12,500,000 gold + 15 Greater Fragments;
- actual: 12,000,000 + 15;
- confidence: high;
- follow-up: isolated cost PR and focused test.

### WOD-F002 — Grade IV point accounting

- `m_modsMaxGrade` is absent from spendable `getExtraPoints()`;
- the global count is added separately to every domain Revelation total;
- reference behavior: each Grade IV mod grants one permanent spendable Promotion Point, maximum 69;
- confidence: high;
- follow-up: isolated points-accounting PR with persistence and four-domain boundary tests.

### WOD-F003 — Revelation Mastery double application

- 16 detected general/vocation variants both add immediately and queue a strategy;
- `executeStrategies()` later applies the queued value;
- confidence: high static, runtime effect measurement pending;
- follow-up: isolated exactly-once correction and no-accumulation test.

### WOD-F004 — 225 revealed-gem maximum unenforced in both profiles

- current profile: `ProtocolGame::parseWheelGemAction()` has no cap guard;
- legacy profile: `Game::playerWheelGemAction()` has no cap guard;
- runtime: `PlayerWheel::revealGem()` has no `m_revealedGems.size()` guard;
- confidence: high for caller boundary;
- follow-up: central invariant and 225/226 resource-preservation test.

### WOD-F005 — unchecked Grade position in both profiles

- current and legacy profiles pass a client byte to `improveGemGrade()`;
- runtime reads `m_basicGrades[pos]` or `m_supremeGrades[pos]` before validation;
- array sizes: 49 and 95; byte range: 0..255;
- confidence: high for out-of-bounds possibility; controlled runtime impact test pending;
- follow-up: bounds and allowed-position validation before first read plus malformed-packet test.

## Open risks

### WOD-R001 — Hunting Task Shop Wheel points

The reference permits up to 50 Wheel points from the Hunting Task Shop. `getExtraPoints()` has no visible source. DB `task_points` is ordinary Task Hunting currency and is not proof of a Wheel reward path. Task Shop handlers, rewards, Lua and KV remain to be traced.

### WOD-R003 — resource removal ordering

Reveal and Grade upgrade perform count prechecks, then remove money before item/fragments, without a local refund branch. Fault-injection/concurrency evidence is required before stronger classification.

### WOD-R005 — duplicate adjacency check

`SLOT_GREEN_TOP_100` checks `SLOT_GREEN_MIDDLE_100` twice. Full graph comparison is pending.

## Persistence evidence

Confirmed statically:

- player save is wrapped in `DBTransaction`;
- online save calls slot-point, revealed-gem, active-gem, Grade and scroll persistence;
- active gems persist by UUID and load only when the UUID exists in revealed gems;
- destroyed gems are removed before current revealed gems are saved.

Still unverified:

- complete load order;
- DB transaction versus KV atomicity;
- corrupted/partial KV recovery;
- repeated save behavior;
- Grade IV count rebuild/idempotency;
- migrations 32/33 and old-data compatibility;
- real logout/login/server-restart round trip.

## Test and CI evidence

### Local focused tests

- main scanner: 7 passed;
- current + legacy protocol scanner: 2 passed.

### Confirmed repository run

```text
run: 29203018790
result: success
source inventory: 30 files
main artifact: 4 errors / 6 warnings
Revelation double-pattern count: 16
```

### Latest workflow version

The workflow now executes nine tests and generates:

- `WHEEL_OF_DESTINY_AUDIT.json/.md`;
- `WHEEL_PROTOCOL_AUDIT.json/.md`.

Its result is pending and must not be marked passed until read from GitHub Actions.

## Audit artifacts

- `tools/ai-agent/wheel_of_destiny_validation.py`
- `tools/ai-agent/test_wheel_of_destiny_validation.py`
- `tools/ai-agent/wheel_protocol_validation.py`
- `tools/ai-agent/test_wheel_protocol_validation.py`
- `docs/ai-agent/WHEEL_OF_DESTINY_REFERENCE_BASELINE.json`
- `docs/ai-agent/WHEEL_OF_DESTINY_RUNTIME_TEST_PLAN.json`
- `.github/workflows/wheel-of-destiny-validation.yml`

## Remaining evidence

- every Dedication/Conviction/Revelation and spell augment for all active vocations;
- Gem Atelier resonance, fragment yields, effective Grade gating and Momentum;
- Hunting Task Shop point award/storage path;
- complete persistence and migrations;
- current and legacy payload comparison with compatible OTClient;
- malformed-packet and gameplay runtime scenarios.

## Safe follow-up order

1. Review latest nine-test CI and both artifacts.
2. Finish Hunting Task and persistence analysis.
3. Compare both profiles with OTClient.
4. Execute runtime scenarios.
5. Open separate PRs for F001, F002, F003, F004 and F005.
