# Canary Wheel of Destiny validation report

> **Snapshot:** 2026-07-12  
> **Branch:** `feat/wheel-of-destiny-validation-audit`  
> **Draft PR:** #169  
> **Reference:** `https://tibia.fandom.com/wiki/Wheel_of_Destiny`, checked 2026-07-12  
> **Evidence:** static source analysis, current + legacy caller-boundary analysis and focused parser tests; runtime and compatible-client contract remain unverified.

## Decision

Canary's Wheel of Destiny is **not yet verified as faithful**. The audit currently has six confirmed static/caller-path findings and two unresolved risks. This PR changes only documentation, tools, tests and CI.

## Static matches

Status `static-consistent`, not runtime verified:

- 36 slices;
- Revelation thresholds 250 / 500 / 1000;
- level 51+, promoted Premium access;
- 1 point per level after 50;
- five Promotion Scrolls totaling 50;
- Monk quest bonus 10;
- temple-only decrease/reset;
- reveal 125k / 1m / 6m;
- rotate 125k / 250k / 500k;
- Basic Grade II–IV;
- Supreme Grade II and IV;
- Grade IV multiplier 1.5.

## Confirmed findings

### WOD-F001 — Supreme Grade III cost

Expected 12,500,000 + 15 Greater Fragments; current code returns 12,000,000 + 15. High confidence. Isolated cost PR required.

### WOD-F002 — Grade IV point accounting

`m_modsMaxGrade` is absent from spendable points and added globally to every domain Revelation total. Reference behavior is one permanent spendable point per Grade IV mod, maximum 69. Isolated points/persistence PR required.

### WOD-F003 — Revelation Mastery double application

Sixteen detected variants add immediately and queue a strategy applied later by `executeStrategies()`. High-confidence static pattern; runtime measurement pending. Exactly-once regression required.

### WOD-F004 — 225 revealed-gem cap missing

Current handler, legacy handler and `revealGem()` contain no cap check. Central 225/226 invariant and no-resource-loss test required.

### WOD-F005 — unchecked Grade position

Current and legacy handlers pass an arbitrary byte to `improveGemGrade()`, which reads 49/95-element arrays before validation. Bounds and allowed-position guards must precede the first read; malformed-packet runtime test required.

### WOD-F006 — Hunting Task Shop Wheel points missing

The selected reference permits up to 50 purchased Wheel points. Current official Taskboard implementation:

- declares itself a minimal packet shim;
- sends shop offer count `0`;
- treats `ShopBuy` only as a payload shape and returns an empty shop window;
- has no Wheel-point purchase or persistence path;
- `PlayerWheel::getExtraPoints()` has no Hunting Task source.

`task_points` is Task Hunting currency earned by task claims; it must not be interpreted as already purchased Wheel points. Implementing F006 requires a bounded purchase record, price/offer contract, maximum 50, idempotency, save/load and OTClient compatibility.

## Open risks

### WOD-R003 — resource removal ordering

Count prechecks exist, but reveal/upgrade remove money before item/fragments and have no local refund branch. Fault-injection/concurrency evidence is required.

### WOD-R005 — duplicate adjacency

`SLOT_GREEN_TOP_100` checks `SLOT_GREEN_MIDDLE_100` twice. Full graph comparison pending.

## Persistence evidence

Confirmed statically:

- save uses `DBTransaction`;
- slot points, revealed/active gems, grades and scrolls are persisted;
- active gem UUID must resolve to a revealed gem on load;
- destroyed gems are removed before saving current revealed gems;
- `task_points` is loaded as Task Hunting currency.

Pending:

- complete load order;
- DB transaction vs KV atomicity;
- corrupted/partial KV recovery;
- repeated saves and destroyed-gem cleanup;
- Grade IV count rebuild/idempotency;
- migrations 32/33;
- logout/login/server-restart round trip.

## Tests and CI

Local focused suites:

- main scanner: 7 passed;
- current + legacy protocol: 2 passed;
- Hunting Task Shop: 2 passed;
- total: 11 passed.

Confirmed repository run before companion audits:

```text
run 29203018790: success
30 source files
4 errors / 6 warnings
16 Revelation double-pattern variants
```

Latest workflow now creates:

- `WHEEL_OF_DESTINY_AUDIT.json/.md`;
- `WHEEL_PROTOCOL_AUDIT.json/.md`;
- `WHEEL_TASK_SHOP_AUDIT.json/.md`.

Latest result is pending and must not be marked passed before GitHub Actions evidence.

## Remaining evidence

- all Dedication/Conviction/Revelation effects and spell augments;
- Gem resonance, fragments, Grade gating and Momentum;
- complete persistence/migrations;
- current + legacy payload comparison with compatible OTClient;
- runtime and malformed-packet scenarios.

## Safe follow-up order

1. Review latest eleven-test CI and all three artifacts.
2. Complete persistence and OTClient analysis.
3. Execute runtime scenarios.
4. Open separate PRs for F001–F006.
