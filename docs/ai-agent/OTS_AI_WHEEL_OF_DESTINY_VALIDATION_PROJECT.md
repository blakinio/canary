# OTS AI Wheel of Destiny Validation — stan, metodologia i handoff

> **Aktualizacja:** 2026-07-12  
> **Projekt nadrzędny:** `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`  
> **Repozytorium zapisywalne:** `blakinio/canary`  
> **Gałąź:** `feat/wheel-of-destiny-validation-audit`  
> **Draft PR:** [#169](https://github.com/blakinio/canary/pull/169)  
> **Zakres PR:** wyłącznie dokumentacja, deterministyczne narzędzia walidacyjne, testy i CI; bez zmian gameplay, balansu, protokołu, schema, datapacka, mapy ani assetów.

---

## 1. Cel i metodologia

Zweryfikować Wheel of Destiny i Gem Atelier w pełnym łańcuchu:

```text
definition -> reference -> activation -> effect -> persistence -> protocol -> runtime -> regression
```

Sama obecność enumu, getter'a, handlera, skryptu lub danych nie jest dowodem poprawności efektu.

Źródła:

```text
writable: blakinio/canary
upstream reference: opentibiabr/canary
client contract: opentibiabr/otclient — pending
reference snapshot: https://tibia.fandom.com/wiki/Wheel_of_Destiny, 2026-07-12
baseline: docs/ai-agent/WHEEL_OF_DESTINY_REFERENCE_BASELINE.json
```

Najważniejsze wartości baseline:

- 36 slice'ów;
- Revelation 250 / 500 / 1000;
- 1 punkt za poziom po 50;
- 50 punktów z Promotion Scrolls;
- 10 punktów z The Way of the Monk;
- maksymalnie 50 punktów z Hunting Task Shop;
- maksymalnie 69 punktów z Grade IV mods;
- limit 225 revealed gems;
- reveal 125k / 1m / 6m;
- rotate 125k / 250k / 500k;
- Basic Grade II–IV: 2m / 5m / 30m;
- Supreme Grade II–IV: 5m / 12.5m / 75m;
- Grade IV = 150% Grade I;
- każdy Grade IV mod daje jeden stały Promotion Point.

---

## 2. Artefakty

| Path | Cel | Stan |
|---|---|---|
| `wheel_of_destiny_validation.py` | główny scanner definicji, kosztów, punktów i efektów | 7 testów passed lokalnie |
| `wheel_protocol_validation.py` | current + legacy Gem Atelier boundary audit | 2 testy passed lokalnie |
| `wheel_task_shop_validation.py` | Hunting Task Shop Wheel point-path audit | 2 testy passed lokalnie |
| odpowiednie `test_*.py` | focused defect/guard fixtures | 11 testów łącznie lokalnie |
| `WHEEL_OF_DESTINY_REFERENCE_BASELINE.json` | wersjonowany baseline | aktywny |
| `WHEEL_OF_DESTINY_VALIDATION_REPORT.md` | raport dowodowy | aktywny |
| `WHEEL_OF_DESTINY_RUNTIME_TEST_PLAN.json` | 20 scenariuszy runtime/protocol/persistence | aktywny |
| `.github/workflows/wheel-of-destiny-validation.yml` | trzy audyty, 11 testów, JSON validation i sześć artifact files | najnowszy run pending |

Pełne ścieżki narzędzi: `tools/ai-agent/**`.

---

## 3. CI

Potwierdzony pierwszy run:

```text
run: 29203018790
result: success
focused tests: 7 passed
source inventory: 30 files
main findings: 4 errors / 6 warnings
Revelation Mastery double-pattern variants: 16
```

Aktualny workflow dodatkowo generuje:

```text
WHEEL_PROTOCOL_AUDIT.json/.md
WHEEL_TASK_SHOP_AUDIT.json/.md
```

Najnowszego runu nie wolno oznaczyć jako passed przed odczytem GitHub Actions.

---

## 4. Statyczne zgodności

Status `static-consistent`, nie `verified`:

- 36 slice'ów;
- Revelation thresholds 250 / 500 / 1000;
- level 51+, promoted i Premium access;
- 1 point per level;
- pięć scrolli = 50;
- Monk bonus = 10;
- temple-only decrease/reset;
- reveal i rotate costs;
- Basic Grade II–IV costs;
- Supreme Grade II i IV costs;
- Grade IV multiplier 1.5.

---

## 5. Potwierdzone problemy

### WOD-F001 — Supreme Grade III 12m zamiast 12.5m

High confidence. Follow-up: osobny cost PR.

### WOD-F002 — Grade IV points nie są spendable i trafiają do każdej domeny

`getExtraPoints()` pomija `m_modsMaxGrade`, a `getPlayerSliceStage()` dodaje globalny licznik do każdej domeny. Follow-up: osobny points-accounting PR.

### WOD-F003 — Revelation Mastery jest naliczane podwójnie

16 wariantów dodaje bonus natychmiast i przez queued strategy. Runtime measurement pending. Follow-up: exactly-once PR.

### WOD-F004 — limit 225 revealed gems nie jest egzekwowany

Current i legacy handler nie sprawdzają cap; `revealGem()` również nie. Follow-up: centralny invariant 225/226.

### WOD-F005 — unchecked Grade position w current i legacy

Oba profile przekazują client byte do `improveGemGrade()`, które indeksuje tablice 49/95 przed walidacją. Follow-up: bounds + allowed-position validation przed pierwszym odczytem.

### WOD-F006 — Hunting Task Shop Wheel points nie są zaimplementowane

High confidence dla aktualnego official Taskboard profile:

- moduł deklaruje się jako minimalny packet shim;
- `sendShopWindow()` wysyła `offer count = 0`;
- `ShopBuy` tylko konsumuje payload i odsyła puste okno;
- `getExtraPoints()` nie ma Hunting Task source;
- zwykłe `task_points` są osobną walutą Task Hunting i nie stanowią Wheel Promotion Points.

Follow-up wymaga osobnego feature PR obejmującego shop offers, zakup, trwały licznik maksymalnie 50, idempotency, persistence i klient–serwer contract. Nie implementować tego jako prostego dodania całego salda `task_points` do Wheel.

Nie łączyć F001–F006 w jednym PR-ze.

---

## 6. Otwarte ryzyka

### WOD-R003 — kolejność usuwania zasobów

Reveal/upgrade wykonują count precheck, potem money removal przed item/fragments, bez lokalnego refund branch. Wymagany fault-injection/concurrency test.

### WOD-R005 — duplicate adjacency

`SLOT_GREEN_TOP_100` sprawdza `SLOT_GREEN_MIDDLE_100` dwa razy. Pełny graph comparison pending.

---

## 7. Persistence — stan

Potwierdzone statycznie:

- player save używa `DBTransaction`;
- online save wywołuje slot points, revealed/active gems, grades i scrolls persistence;
- active gems zapisują UUID i loadują się tylko, gdy UUID istnieje w revealed gems;
- destroyed gems są usuwane przed zapisem current revealed gems;
- `task_points` są ładowane jako Task Hunting currency.

Niepotwierdzone:

- pełna kolejność load calls;
- DB transaction względem KV writes;
- corrupted/partial KV recovery;
- repeated save behavior;
- Grade IV count rebuild/idempotency;
- migrations 32/33 i old-data compatibility;
- logout/login/server-restart round trip.

---

## 8. Pozostały zakres

- pełna mapa Dedication/Conviction/Revelation i spell augments dla wszystkich aktywnych vocations;
- resonance, fragment yields, effective Grade gating i Momentum;
- complete persistence/KV/migration review;
- current + legacy Canary ↔ OTClient payload contract;
- execution scenariuszy runtime;
- separate follow-up PRs dla potwierdzonych problemów.

---

## 9. Work log

### 2026-07-12 — Hunting Task Shop audit

- potwierdzono, że official Taskboard jest pustym shimem i nie sprzedaje Wheel points;
- WOD-R001 podniesiono do WOD-F006;
- dodano `wheel_task_shop_validation.py` i 2 focused tests;
- lokalny wynik: `Ran 2 tests ... OK`;
- workflow rozszerzono do 11 testów i trzech JSON/Markdown audit pairs;
- nie zmieniono runtime ani Taskboard behavior.

### 2026-07-12 — oba profile Gem Atelier

- odnaleziono legacy `Game::playerWheelGemAction()`;
- potwierdzono F004/F005 dla current i legacy;
- dodano protocol scanner i 2 focused tests;
- lokalny wynik: `Ran 2 tests ... OK`.

### 2026-07-12 — główny audit

- utworzono baseline, raport, runtime plan, scanner i 7 testów;
- pierwszy repository CI passed;
- potwierdzono F001–F005;
- zinwentaryzowano 30 paths.

---

## 10. Aktualny stan

```text
PR: #169 draft
confirmed findings: WOD-F001..WOD-F006
local tests: 7 + 2 + 2 = 11 passed
first repository CI: passed
latest three-audit workflow: pending
runtime claims: none
gameplay changes: none
```

### Acceptance

- [x] durable specialist document;
- [x] versioned baseline;
- [x] main, protocol i Task Shop scanners;
- [x] 11 focused tests lokalnie;
- [x] report i 20-scenario runtime plan;
- [x] pierwszy successful repository CI;
- [ ] latest 11-test workflow and artifacts reviewed;
- [ ] complete persistence/migrations;
- [ ] complete perks/spells;
- [ ] OTClient contract;
- [ ] runtime scenarios;
- [ ] focused defect PRs.

---

## 11. Handoff

### Następny krok

1. Odczytaj najnowszy workflow po commitach:
   - `1ec4c2e8a0c67c675f9bd3f137ddbbec5592c18d`;
   - `e3f1e4ab97ae4547852959e30901e43495e03389`;
   - `a9ab587c8f21811a0a3b0311eed1b211522c9bb9`.
2. Zapisz exact wynik i trzy artifacts w tym dokumencie, raporcie i task record.
3. Dokończ persistence load order, KV i migrations.
4. Zmapuj perks/spells.
5. Porównaj payloads z `opentibiabr/otclient`.
6. Nie naprawiaj gameplay w PR #169.

### Nie powtarzaj

- nie uznawaj static match za runtime verified;
- nie traktuj całego `task_points` balance jako Wheel points;
- nie uznawaj prechecku za transakcyjność bez failure testu;
- nie łącz F001–F006;
- nie modyfikuj upstream.

### Obowiązek aktualizacji

Po każdej zmianie kodu, testu, raportu, baseline, workflow lub klasyfikacji aktualizuj ten dokument, task record i PR evidence. Nie wpisuj `passed` ani `verified` bez wykonanego checku.
