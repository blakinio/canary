# OTS AI Wheel of Destiny Validation — stan i handoff

> **Aktualizacja:** 2026-07-12  
> **Repo:** `blakinio/canary`  
> **Branch:** `feat/wheel-of-destiny-validation-audit`  
> **Draft PR:** [#169](https://github.com/blakinio/canary/pull/169)  
> **Projekt nadrzędny:** `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`  
> **Safety boundary:** ten PR zawiera wyłącznie dokumentację, read-only scannery, focused tests i CI. Nie zmienia gameplay, balansu, protokołu, schema, datapacka, mapy ani assetów.

## Metodologia

Każdą cechę sprawdzamy osobno:

```text
definition -> reference -> activation -> effect -> persistence -> protocol -> runtime -> regression
```

Statyczny match nie oznacza runtime verification.

Reference snapshot:

```text
https://tibia.fandom.com/wiki/Wheel_of_Destiny
checked: 2026-07-12
baseline: docs/ai-agent/WHEEL_OF_DESTINY_REFERENCE_BASELINE.json
```

Najważniejsze wartości: 36 slice'ów, Revelation 250/500/1000, 50 scroll points, 10 Monk quest points, do 50 Hunting Task Shop points, do 69 Grade IV points, limit 225 gems, reveal 125k/1m/6m, rotate 125k/250k/500k, Supreme Grade III 12.5m, Grade IV = 150% Grade I.

## Artefakty

| Path | Stan |
|---|---|
| `tools/ai-agent/wheel_of_destiny_validation.py` + test | 7 lokalnych testów passed |
| `tools/ai-agent/wheel_protocol_validation.py` + test | 2 lokalne testy passed |
| `tools/ai-agent/wheel_task_shop_validation.py` + test | 2 lokalne testy passed |
| `docs/ai-agent/WHEEL_OF_DESTINY_REFERENCE_BASELINE.json` | aktywny |
| `docs/ai-agent/WHEEL_OF_DESTINY_VALIDATION_REPORT.md` | aktywny |
| `docs/ai-agent/WHEEL_OF_DESTINY_RUNTIME_TEST_PLAN.json` | 20 scenariuszy |
| `.github/workflows/wheel-of-destiny-validation.yml` | trzy audyty, 11 testów, sześć artifact files; najnowszy run pending |
| `docs/agents/MODULE_CATALOG.md` | audit skatalogowany jako aktywne narzędzie PR #169 |

## Potwierdzony CI

```text
run 29203018790: success
7 focused tests passed
30 Wheel-related paths
4 errors / 6 warnings w pierwszym main artifact
16 Revelation Mastery double-pattern variants
```

Najnowsza wersja workflow dodatkowo generuje protocol i Task Shop audits. Nie oznaczać jej jako passed bez odczytu Actions.

## Statyczne zgodności

`static-consistent`, nie `verified`:

- 36 slice'ów;
- Revelation 250/500/1000;
- promoted Premium level 51+ access;
- 1 point per level after 50;
- 5 scrolls = 50;
- Monk bonus = 10;
- temple-only decrease/reset;
- reveal/rotate costs;
- Basic Grade II–IV;
- Supreme Grade II i IV;
- Grade IV multiplier 1.5.

## Potwierdzone problemy

### WOD-F001 — Supreme Grade III 12m zamiast 12.5m

High confidence. Osobny cost PR.

### WOD-F002 — Grade IV points są błędnie księgowane

`getExtraPoints()` pomija `m_modsMaxGrade`; globalny licznik jest dodawany do każdej domeny. Osobny points/persistence PR.

### WOD-F003 — Revelation Mastery double application

16 wariantów dodaje bonus bezpośrednio i przez queued strategy. Runtime measurement pending. Osobny exactly-once PR.

### WOD-F004 — brak limitu 225 revealed gems

Current handler, legacy handler i `revealGem()` nie sprawdzają cap. Osobny invariant 225/226 PR.

### WOD-F005 — unchecked Grade position

Current i legacy przekazują client byte do `improveGemGrade()`, które indeksuje tablice 49/95 przed walidacją. Osobny input-hardening PR.

### WOD-F006 — brak Hunting Task Shop Wheel points

Official Taskboard jest minimalnym shimem:

- shop offer count = 0;
- ShopBuy nie kupuje nagrody, tylko odsyła puste okno;
- `getExtraPoints()` nie ma Hunting Task source;
- `task_points` są osobną walutą Task Hunting, nie kupionymi Wheel points.

Osobny feature PR musi dodać oferty, zakup, bounded counter max 50, idempotency, persistence i klient–serwer contract. Nie dodawać całego salda `task_points` do Wheel.

Nie łączyć F001–F006 w jednym PR-ze.

## Otwarte ryzyka

- **WOD-R003:** kolejność money -> item/fragments wymaga fault-injection/concurrency testu.
- **WOD-R005:** duplicate neighbour dla `SLOT_GREEN_TOP_100` wymaga pełnego graph comparison.

## Persistence — stan

Potwierdzone statycznie:

- save używa `DBTransaction`;
- zapis obejmuje slot points, revealed/active gems, grades i scrolls;
- load order: DB slot points, revealed gems, active gems, grades, scrolls, potem `initializePlayerData()`;
- active gem UUID musi istnieć w revealed gems;
- destroyed gems są usuwane przed zapisem;
- `task_points` są ładowane jako Task Hunting currency.

Pending:

- DB transaction vs KV atomicity;
- corrupted/partial KV recovery;
- repeated-save cleanup;
- Grade IV counter rebuild/idempotency;
- migrations 32/33;
- logout/login/server-restart round trip.

## Pozostały zakres

- pełna mapa Dedication/Conviction/Revelation i spell augments;
- resonance, fragment yields, effective Grade gating, Momentum;
- complete persistence/migrations;
- current + legacy Canary ↔ `opentibiabr/otclient` contract;
- runtime i malformed-packet scenarios;
- osobne follow-up PR-y.

## Work log — 2026-07-12

- utworzono branch, task record, ACTIVE_WORK i draft PR #169;
- dodano baseline, report, 20-scenario plan, main scanner i 7 testów;
- pierwszy repository CI passed;
- dodano current+legacy protocol scanner i 2 testy;
- dodano Hunting Task Shop scanner i 2 testy;
- workflow rozszerzono do 11 testów i trzech audit pairs;
- potwierdzono WOD-F001..F006;
- dodano audit do `MODULE_CATALOG.md`;
- po każdej zmianie zaktualizowano ten handoff, task record, report lub PR evidence;
- nie zmieniono runtime.

## Aktualny stan

```text
confirmed findings: WOD-F001..WOD-F006
local focused tests: 11 passed
first repository CI: passed
latest three-audit CI: pending
module catalogue: updated
runtime claims: none
gameplay changes: none
```

## Handoff

Następny agent:

1. Odczytuje najnowszy `Wheel of Destiny Validation` run i trzy audit pairs.
2. Aktualizuje ten plik, report, task record i PR body exact wynikiem.
3. Kończy persistence/KV/migrations.
4. Mapuje perki i spelle.
5. Porównuje oba payload profiles z `opentibiabr/otclient`.
6. Nie naprawia gameplay w PR #169.

Nie zgadywać. Nie uznawać statycznego matchu za runtime proof. Nie traktować `task_points` jako Wheel points. Nie łączyć F001–F006.
