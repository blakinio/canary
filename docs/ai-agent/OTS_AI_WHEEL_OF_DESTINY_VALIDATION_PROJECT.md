# OTS AI Wheel of Destiny Validation — stan, metodologia i handoff

> **Aktualizacja:** 2026-07-12  
> **Projekt nadrzędny:** `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`  
> **Repozytorium zapisywalne:** `blakinio/canary`  
> **Gałąź:** `feat/wheel-of-destiny-validation-audit`  
> **Draft PR:** [#169](https://github.com/blakinio/canary/pull/169)  
> **Zakres PR:** wyłącznie dokumentacja, deterministyczne narzędzia walidacyjne, testy i CI; bez zmian gameplay, balansu, protokołu, schema, datapacka, mapy ani assetów.

---

## 1. Cel

Zweryfikować kompletny Wheel of Destiny i Gem Atelier w Canary względem wersjonowanego źródła referencyjnego oraz faktycznych ścieżek runtime:

```text
definition
  -> reference
  -> activation
  -> effect
  -> persistence
  -> protocol
  -> runtime
  -> regression
```

Sama obecność enumu, getter'a, handlera lub danych nie jest dowodem poprawności efektu.

---

## 2. Źródła prawdy

### Kod

```text
writable:       blakinio/canary
reference-only: opentibiabr/canary
client contract: opentibiabr/otclient — do porównania
```

### Gameplay reference

```text
https://tibia.fandom.com/wiki/Wheel_of_Destiny
snapshot: 2026-07-12
baseline: docs/ai-agent/WHEEL_OF_DESTINY_REFERENCE_BASELINE.json
```

Baseline obejmuje między innymi:

- 36 slice'ów;
- Revelation thresholds 250 / 500 / 1000;
- 1 punkt za każdy poziom po 50;
- maksymalnie 50 punktów z Promotion Scrolls;
- 10 punktów z The Way of the Monk;
- maksymalnie 50 punktów z Hunting Task Shop;
- maksymalnie 69 punktów z Grade IV mods;
- limit 225 revealed gems;
- reveal costs 125k / 1m / 6m;
- rotate costs 125k / 250k / 500k;
- Basic Grade II–IV: 2m / 5m / 30m;
- Supreme Grade II–IV: 5m / 12.5m / 75m;
- Grade IV = 150% wartości Grade I;
- każdy mod w Grade IV daje jeden stały Promotion Point.

Wartości wiki są wersjonowanym źródłem porównawczym, nie niewersjonowanym oficjalnym kontraktem.

---

## 3. Artefakty

| Path | Cel | Stan |
|---|---|---|
| `tools/ai-agent/wheel_of_destiny_validation.py` | główny statyczny scanner definicji, kosztów, punktów i efektów | aktywny |
| `tools/ai-agent/test_wheel_of_destiny_validation.py` | focused tests głównego scannera | 7 lokalnych testów passed |
| `tools/ai-agent/wheel_protocol_validation.py` | osobny audit current + legacy Gem Atelier boundaries | utworzony |
| `tools/ai-agent/test_wheel_protocol_validation.py` | focused tests obu profili protokołu | 2 lokalne testy passed |
| `docs/ai-agent/WHEEL_OF_DESTINY_REFERENCE_BASELINE.json` | wersjonowany baseline | aktywny |
| `docs/ai-agent/WHEEL_OF_DESTINY_VALIDATION_REPORT.md` | raport dowodowy | aktywny |
| `docs/ai-agent/WHEEL_OF_DESTINY_RUNTIME_TEST_PLAN.json` | 20 scenariuszy runtime/protocol/persistence | aktywny |
| `.github/workflows/wheel-of-destiny-validation.yml` | oba scannery, 9 testów, JSON validation i artifacts | zaktualizowany; nowy run pending |

---

## 4. Potwierdzony CI

Pierwszy workflow przed dodaniem osobnego legacy audit:

```text
run: 29203018790
head: 13c14437b40db057a094f3625215b10b4061ed6b
result: success
focused tests: 7 passed
source inventory: 30 files
findings: 4 errors / 6 warnings
Revelation Mastery double-pattern variants: 16
```

Nowa wersja workflow uruchamia również:

```text
wheel_protocol_validation.py
2 dodatkowe focused tests
WHEEL_PROTOCOL_AUDIT.json
WHEEL_PROTOCOL_AUDIT.md
```

Wynik tego runu nie może być oznaczony jako passed przed odczytem GitHub Actions.

---

## 5. Statyczne zgodności

Status: `static-consistent`, nie `verified`.

- 36 slice'ów;
- Revelation thresholds 250 / 500 / 1000;
- level 51+, promoted i Premium access gate;
- 1 point per level;
- pięć Promotion Scrolls dających łącznie 50;
- Monk quest bonus 10;
- temple-only point decrease/reset;
- reveal costs 125k / 1m / 6m;
- rotate costs 125k / 250k / 500k;
- Basic Grade II–IV costs;
- Supreme Grade II i Grade IV costs;
- Grade IV multiplier 1.5.

---

## 6. Potwierdzone problemy

### WOD-F001 — Supreme Grade III kosztuje 12m zamiast 12.5m

- **Confidence:** high.
- `PlayerWheel::getGreaterGradeCost()` zwraca 12,000,000 + 15 fragmentów.
- Baseline wymaga 12,500,000 + 15.
- Follow-up: osobny minimalny cost PR z focused testem.

### WOD-F002 — Grade IV points nie są spendable i są dodawane do każdej domeny

- **Confidence:** high.
- `getExtraPoints()` nie uwzględnia `m_modsMaxGrade`.
- `getPlayerSliceStage()` dodaje globalny `m_modsMaxGrade` osobno do każdej domeny.
- Follow-up: osobny points-accounting PR z save/load i threshold boundary tests.

### WOD-F003 — Revelation Mastery jest naliczane podwójnie

- **Confidence:** high static; runtime test pending.
- 16 wykrytych wariantów jednocześnie:
  - dodaje bonus natychmiast przez `addRevelationBonus()`;
  - tworzy `GemModifierRevelationStrategy`, wykonywaną później przez `executeStrategies()`.
- Follow-up: osobny effect PR z testem exactly-once i no accumulation.

### WOD-F004 — limit 225 revealed gems nie jest egzekwowany

- **Confidence:** high dla current i legacy profile.
- Current: `ProtocolGame::parseWheelGemAction()` przekazuje Reveal bez cap check.
- Legacy: `Game::playerWheelGemAction()` przekazuje Reveal bez cap check.
- Runtime: `PlayerWheel::revealGem()` nie sprawdza `m_revealedGems.size()`.
- Follow-up: centralny invariant 225/226 z testem braku utraty zasobów.

### WOD-F005 — unchecked Grade position w obu profilach

- **Confidence:** high dla current i legacy profile.
- Current przekazuje client byte `position`.
- Legacy przekazuje client byte `pos`.
- `improveGemGrade()` indeksuje przed walidacją:
  - `m_basicGrades[49]`;
  - `m_supremeGrades[95]`.
- Byte dopuszcza 0..255.
- Follow-up: osobny input-hardening PR z bounds + allowed-mod membership checks przed pierwszym odczytem i malformed-packet testem.

Nie łączyć F001–F005 w jednym PR-ze.

---

## 7. Otwarte ryzyka

### WOD-R001 — Hunting Task Shop Wheel points

- `getExtraPoints()` nie zawiera ścieżki Hunting Task Shop.
- Pole DB `task_points` jest ładowane jako zwykła waluta Task Hunting; nie jest to dowód konwersji do Wheel Promotion Points.
- Repo search nie znalazł jeszcze award/storage path dodającego maksymalnie 50 Wheel points.
- Przed klasyfikacją `missing-path` trzeba przejrzeć Task Hunting Shop handlers, reward IDs, Lua i KV.

### WOD-R003 — kolejność usuwania zasobów

- reveal/upgrade wykonują item-count precheck;
- następnie usuwają money przed item/fragments;
- brak lokalnego refund branch.
- Wymagany fault-injection/concurrency test; nie klasyfikować jako exploit bez dowodu runtime.

### WOD-R005 — duplicate adjacency

`SLOT_GREEN_TOP_100` sprawdza `SLOT_GREEN_MIDDLE_100` dwa razy. Trzeba porównać pełny 36-slice graph z klientem/reference.

---

## 8. Persistence — stan analizy

Potwierdzone statycznie:

- zapis gracza jest otoczony `DBTransaction`;
- online save wywołuje:
  - `saveDBPlayerSlotPointsOnLogout()`;
  - `saveRevealedGems()`;
  - `saveActiveGems()`;
  - `saveKVModGrades()`;
  - `saveKVScrolls()`;
- active gems są zapisywane przez UUID;
- load active gem akceptuje UUID tylko wtedy, gdy istnieje w loaded revealed gems;
- destroyed gems są usuwane, a revealed gems zapisywane przez KV.

Niepotwierdzone:

- dokładna kolejność wszystkich load calls;
- round-trip corrupted/partial KV;
- atomiczność DB transaction względem KV writes;
- zachowanie `m_destroyedGems` po wielokrotnym save;
- Grade IV count rebuild i idempotency;
- migration 32/33 oraz legacy data compatibility.

---

## 9. Pozostały zakres

- pełna mapa Dedication/Conviction/Revelation dla wszystkich aktywnych vocations;
- każdy spell augment i miejsce naliczania damage/healing/cooldown/mana/area;
- fragment yields i gem destroy behavior;
- Vessel Resonance, kolejność mod slots i +1/+1/+2 damage/healing;
- previous-slot effective-grade gating;
- Momentum;
- pełny persistence/KV/migration round-trip;
- Hunting Task Shop point path;
- Canary ↔ kompatybilny OTClient payload contract;
- execution wszystkich scenariuszy z `WHEEL_OF_DESTINY_RUNTIME_TEST_PLAN.json`.

---

## 10. Work log

### 2026-07-12 — audit obu profili protokołu

- odnaleziono legacy `Game::playerWheelGemAction()`;
- potwierdzono, że F004 i F005 dotyczą current i legacy profile;
- dodano `wheel_protocol_validation.py`;
- dodano 2 focused tests: defect fixture oraz guarded fixture;
- lokalny wynik: `Ran 2 tests ... OK`;
- zaktualizowano workflow, aby wykonywał łącznie 9 focused tests i publikował osobny protocol artifact;
- nie zmieniono runtime ani protokołu.

### 2026-07-12 — current profile i główny scanner

- dodano baseline, raport, 20-scenario runtime plan, główny scanner i 7 testów;
- pierwszy CI run `29203018790` passed;
- potwierdzono F001–F005;
- zinwentaryzowano 30 Wheel-related paths.

### 2026-07-12 — uruchomienie projektu

- utworzono branch i draft PR #169;
- utworzono task record i wpis ACTIVE_WORK;
- utworzono ten dokument obok głównego projektu.

---

## 11. Aktualny stan

```text
PR: #169 draft
phase: current + legacy boundary automated; persistence/Hunting Task/OTClient/runtime pending
confirmed findings: WOD-F001..WOD-F005
local focused tests: 7 + 2 passed
first repository CI: passed
latest workflow CI: pending
runtime claims: none
gameplay changes: none
```

### Acceptance

- [x] specialist durable document;
- [x] versioned baseline;
- [x] main static scanner i 7 tests;
- [x] current + legacy protocol scanner i 2 tests;
- [x] initial evidence report;
- [x] 20-scenario runtime plan;
- [x] dedicated CI workflow i pierwszy successful run;
- [ ] review latest 9-test workflow artifact;
- [ ] Hunting Task points path;
- [ ] complete persistence/migration review;
- [ ] complete perk/spell matrix;
- [ ] compatible OTClient contract;
- [ ] runtime scenarios;
- [ ] separate defect PRs.

---

## 12. Handoff

### Następny krok

1. Odczytaj najnowszy `Wheel of Destiny Validation` run po commitach:
   - `5e93d3be342e5a954ee282e2faf19af8ead0b964`;
   - `3028ea1756d3a9058a2d33c55fb15d11d7a21d4f`;
   - `3d9018f5651ceeffc94dda20bae2656bdbdad54c`.
2. Zapisz exact result i protocol artifact w tym dokumencie, raporcie i task record.
3. Prześledź Task Hunting Shop reward/purchase handlers.
4. Dokończ load order, KV i migrations.
5. Porównaj oba payload profiles z `opentibiabr/otclient`.
6. Nie naprawiaj gameplay w PR #169.

### Nie powtarzaj

- nie uznawaj static match za runtime verified;
- nie uznawaj `task_points` za Wheel points bez award/use path;
- nie uznawaj prechecku za transakcyjność bez failure testu;
- nie naprawiaj F001–F005 razem;
- nie modyfikuj `opentibiabr/canary`.

### Obowiązek aktualizacji

Po każdej zmianie kodu, testu, raportu, baseline, workflow lub klasyfikacji:

1. zaktualizuj ten dokument;
2. zaktualizuj task record;
3. zapisz exact test i wynik;
4. zaktualizuj PR body, jeżeli evidence lub scope się zmieniły;
5. nie wpisuj `passed` ani `verified` bez wykonanego checku.
