# OTS AI Wheel of Destiny Validation — cel, metodologia, stan i handoff

> **Stan dokumentu:** 2026-07-12  
> **Projekt nadrzędny:** `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`  
> **Repozytorium zapisywalne:** `blakinio/canary`  
> **Gałąź robocza:** `feat/wheel-of-destiny-validation-audit`  
> **Draft PR:** [#169](https://github.com/blakinio/canary/pull/169)  
> **Aktualny etap:** audyt statyczny i current-payload protocol boundary; persistence, OTClient contract i runtime pozostają otwarte  
> **Najważniejsza zasada:** obecność definicji, getter'a lub handlera nie dowodzi poprawności gameplay. Każda cecha wymaga osobnych dowodów definicji, aktywacji, efektu, zapisu, protokołu i runtime.

---

## 1. Cel projektu

Wheel of Destiny jest systemem rozproszonym pomiędzy:

- definicje Wheel, slice'ów i perków;
- stan postaci, presety i przydział Promotion Points;
- Dedication, Conviction i Revelation Perks;
- spell augments, combat, healing, statystyki i odporności;
- Gem Atelier, domain affinity, sockety, Vessel Resonance i fragmenty;
- zapis/load, migracje i KV;
- protokół klient–serwer;
- Lua, itemy, bossy, questy i dodatkowe źródła punktów.

Celem jest powtarzalna, evidence-based walidacja całego systemu względem wskazanego źródła referencyjnego i aktywnej wersji Canary. Pierwszy PR jest **read-only**: nie zmienia balansu, gameplay, protokołu, schema, datapacka, mapy ani assetów.

---

## 2. Źródła prawdy i wersjonowanie

### 2.1. Kod runtime

```text
writable: blakinio/canary
reference-only: opentibiabr/canary
```

### 2.2. Gameplay reference wskazany przez użytkownika

```text
https://tibia.fandom.com/wiki/Wheel_of_Destiny
snapshot checked: 2026-07-12
```

Zapisany baseline:

```text
docs/ai-agent/WHEEL_OF_DESTINY_REFERENCE_BASELINE.json
```

Snapshot obejmuje między innymi:

- 1 punkt za każdy poziom po 50;
- promoted Premium character od level 51;
- 4 domeny i 36 slice'ów;
- Revelation thresholds 250 / 500 / 1000;
- darmowy reset punktów tylko w temple;
- maksymalnie 50 punktów z Promotion Scrolls;
- maksymalnie 10 punktów z The Way of the Monk;
- maksymalnie 50 punktów z Hunting Task Shop;
- maksymalnie 69 punktów z modów ulepszonych do Grade IV;
- maksymalnie 225 revealed gems;
- resonance bonus +1 / +1 / +2 damage and healing;
- reveal costs 125k / 1m / 6m;
- rotate costs 125k / 250k / 500k;
- Basic upgrade costs 2m / 5m / 30m;
- Supreme upgrade costs 5m / 12.5m / 75m;
- 5 / 15 / 30 fragments;
- Grade IV = +50% względem Grade I;
- każdy Grade IV mod daje jeden stały Promotion Point.

TibiaWiki/Fandom jest wersjonowanym źródłem porównawczym, nie automatycznym oficjalnym kontraktem. Każdy mismatch musi zawierać datę snapshotu, dokładny symbol i confidence.

### 2.3. Protokół

Jeżeli audyt potwierdzi różnicę payloadu lub opcode, wymagane jest porównanie z kompatybilnym OTClientem i osobny kontrakt Canary ↔ OTClient w `docs/agents/CROSS_REPO_CONTRACTS.md`. PR #169 nie zmienia protokołu.

Current-payload entry point został potwierdzony:

```text
opcode 0xE7
  -> ProtocolGame::parseWheelGemAction
  -> direct PlayerWheel methods
```

Dla `Reveal` i `ImproveGrade` parser przekazuje wartości klienta bez walidacji limitu/indeksu. Legacy payload nadal wymaga osobnego prześledzenia przez `Game::playerWheelGemAction`.

---

## 3. Główne ścieżki kodu

```text
src/creatures/players/components/wheel/player_wheel.hpp
src/creatures/players/components/wheel/player_wheel.cpp
src/creatures/players/components/wheel/wheel_definitions.hpp
src/creatures/players/components/wheel/wheel_gems.hpp
src/creatures/players/components/wheel/wheel_gems.cpp
src/creatures/players/components/wheel/wheel_spells.hpp
src/enums/player_wheel.hpp
src/io/io_wheel.hpp
src/io/io_wheel.cpp
src/io/iologindata.cpp
src/io/functions/iologindata_load_player.cpp
src/server/network/protocol/**
src/creatures/combat/**
src/creatures/players/vocations/**
src/lua/functions/creatures/player/**
data/scripts/actions/items/wheel_scrolls.lua
data/libs/functions/gematelier.lua
data/scripts/eventcallbacks/monster/ondroploot_gem_atelier.lua
data-otservbr-global/migrations/32.lua
data-otservbr-global/migrations/33.lua
schema.sql
```

Pierwszy CI artifact zinwentaryzował 30 Wheel-related paths. Lista nadal nie jest uznana za kompletną semantycznie bez pełnego call-site review.

---

## 4. Artefakty audytu

| Path | Cel | Stan |
|---|---|---|
| `tools/ai-agent/wheel_of_destiny_validation.py` | deterministyczny read-only scanner i klasyfikator | utworzony; rozszerzony o protocol boundary |
| `tools/ai-agent/test_wheel_of_destiny_validation.py` | focused parser/finding tests | utworzony; 7 lokalnych testów passed po rozszerzeniu |
| `docs/ai-agent/WHEEL_OF_DESTINY_REFERENCE_BASELINE.json` | wersjonowane wartości ze wskazanego snapshotu | utworzony |
| `docs/ai-agent/WHEEL_OF_DESTINY_VALIDATION_REPORT.md` | human-readable evidence report | utworzony i aktualizowany |
| `docs/ai-agent/WHEEL_OF_DESTINY_RUNTIME_TEST_PLAN.json` | 20 scenariuszy runtime/protocol/persistence | utworzony |
| `.github/workflows/wheel-of-destiny-validation.yml` | CI: tests, audit, JSON validation, artifacts | pierwszy run `29203018790` passed; run po protocol enhancement pending |

Pierwszy potwierdzony CI artifact:

```text
run: 29203018790
head: 13c14437b40db057a094f3625215b10b4061ed6b
result: success
source files: 30
findings: 4 errors / 6 warnings
doubled Revelation Mastery variants: 16
```

Po caller/protocol review skaner został rozszerzony tak, aby:

- analizował `ProtocolGame::parseWheelGemAction()`;
- traktował brak cap 225 w parserze i `revealGem()` jako błąd;
- odczytywał rozmiary `m_basicGrades[49]` i `m_supremeGrades[95]`;
- traktował dowolny client byte przekazany do bezpośredniego indeksowania jako błąd bounds safety;
- zachowywał resource-ordering jako ostrzeżenie do fault-injection review.

Oczekiwany wynik nowej wersji na niezmienionym runtime to 6 errors / 4 warnings; wiążący wynik zostanie zapisany dopiero po CI.

---

## 5. Warstwy dowodowe

Każdy element otrzymuje niezależny status:

1. **definition** — kompletna definicja;
2. **reference** — symbole/itemy/spelle/pola mają cel;
3. **activation** — osiągalna ścieżka aktywacji;
4. **effect** — efekt jest naliczany w poprawnym miejscu i raz;
5. **persistence** — save/load round-trip;
6. **protocol** — klient i serwer zgadzają się co do kontraktu;
7. **runtime** — rzeczywisty scenariusz gameplay;
8. **regression** — test automatyczny chroni zachowanie.

Status wyższej warstwy nie może wynikać wyłącznie z obecności kodu w niższej.

Disposition:

- `verified`
- `static-consistent`
- `protocol-unverified`
- `runtime-unverified`
- `partial`
- `mismatch`
- `missing-path`
- `missing-effect`
- `persistence-risk`
- `needs-manual-review`
- `out-of-scope-version`

---

## 6. Potwierdzone statyczne zgodności

Na snapshot 2026-07-12 kod jest statycznie spójny dla:

- 36 slice'ów;
- Revelation thresholds 250 / 500 / 1000;
- level > 50, promoted, Premium gate;
- 1 point per level;
- pięciu Promotion Scrolls dających łącznie 50;
- Monk quest bonus 10;
- temple-only decrease/reset option;
- reveal costs 125k / 1m / 6m;
- rotate costs 125k / 250k / 500k;
- Basic Grade II–IV costs;
- Supreme Grade II i Grade IV costs;
- Grade IV multiplier 1.5.

Wszystkie te pozycje pozostają `static-consistent`, nie `verified`.

---

## 7. Potwierdzone problemy

### WOD-F001 — Supreme Grade III: 12m zamiast 12.5m

- **Disposition:** `mismatch`
- **Confidence:** high
- **Reference:** snapshot 2026-07-12 — 12,500,000 gold + 15 Greater Fragments.
- **Code:** `PlayerWheel::getGreaterGradeCost()` zwraca 12,000,000 + 15.
- **Impact:** upgrade jest tańszy o 500,000.
- **Runtime:** unverified.
- **Follow-up:** osobny minimalny gameplay PR z focused cost testem.

### WOD-F002 — Grade IV points nie są spendable i są dodawane do każdej domeny

- **Disposition:** `mismatch`
- **Confidence:** high
- **Reference:** każdy Grade IV mod daje jeden stały spendable Promotion Point; maksymalnie 69.
- **Code:** `PlayerWheel::getExtraPoints()` sumuje scrolls i Monk bonus, ale nie `m_modsMaxGrade`.
- **Code:** `PlayerWheel::getPlayerSliceStage()` dodaje globalne `m_modsMaxGrade` do totalu każdej domeny.
- **Impact:** punktów nie można wydawać jak normalnych, natomiast ten sam globalny licznik może przesuwać Revelation thresholds w czterech domenach.
- **Runtime:** unverified.
- **Follow-up:** osobny points-accounting PR z save/load i threshold boundary tests.

### WOD-F003 — Revelation Mastery Supreme Mods są naliczane podwójnie

- **Disposition:** `missing-correct-effect`
- **Confidence:** high
- **Code:** przypadki Revelation Mastery jednocześnie tworzą `GemModifierRevelationStrategy` i wywołują `m_wheel.addRevelationBonus(...)` natychmiast.
- **Execution:** `PlayerWheel::processActiveGems()` następnie uruchamia `executeStrategies()`, które stosuje queued strategy drugi raz.
- **Coverage:** pierwszy CI artifact wykrył 16 wariantów general/vocation.
- **Runtime:** unverified.
- **Follow-up:** osobny correction PR i regression test: exactly once per active gem, no accumulation on recalculation.

### WOD-F004 — limit 225 revealed gems nie jest egzekwowany

- **Disposition:** `mismatch`
- **Confidence:** high dla current payload.
- **Reference:** maksymalnie 225 revealed gems.
- **Protocol:** `ProtocolGame::parseWheelGemAction()` przekazuje Reveal bez sprawdzenia liczby gemów.
- **Runtime:** `PlayerWheel::revealGem()` sprawdza item i money, ale nie rozmiar `m_revealedGems`.
- **Impact:** current-payload client może ujawniać kolejne gemy po przekroczeniu 225, jeżeli ma wymagane zasoby.
- **Follow-up:** osobny invariant PR z checkiem centralnym i boundary testem 225/226.

### WOD-F005 — ImproveGrade przyjmuje dowolny indeks klienta przed bounds check

- **Disposition:** `protocol-input-safety`
- **Confidence:** high dla current payload.
- **Protocol:** pozycja jest pojedynczym client byte i jest bezpośrednio przekazywana do `improveGemGrade()`.
- **Runtime:** metoda najpierw odczytuje `m_basicGrades[pos]` lub `m_supremeGrades[pos]`.
- **Bounds:** tablice mają odpowiednio 49 i 95 elementów, a byte dopuszcza 0..255.
- **Impact:** malformed current-payload packet może wywołać out-of-bounds access/undefined behavior przed jakąkolwiek walidacją grade/cost.
- **Follow-up:** osobny input-hardening PR z membership/bounds validation przed odczytem oraz malformed-packet testem.

Pełny opis: `docs/ai-agent/WHEEL_OF_DESTINY_VALIDATION_REPORT.md`.

---

## 8. Ryzyka wymagające dalszych dowodów

- **WOD-R001:** bezpośrednia ścieżka Hunting Task Shop points nie występuje w `getExtraPoints()`; pełny Lua/KV review pending.
- **WOD-R003:** reveal/upgrade usuwają money przed item/fragments bez lokalnego refund branch; oba wykonują precheck item count, dlatego klasyfikacja wymaga fault-injection/concurrency evidence.
- **WOD-R005:** `SLOT_GREEN_TOP_100` sprawdza `SLOT_GREEN_MIDDLE_100` dwa razy; pełny graph comparison pending.
- **WOD-R006:** legacy payload przechodzi przez `Game::playerWheelGemAction`; jego walidacja i zgodność z current payload są pending.

Nie wolno zmieniać tych ryzyk na confirmed defects bez brakujących dowodów.

---

## 9. Zakres pozostałej walidacji

### Promotion Points i topologia

- Hunting Task Shop award path i idempotency;
- Grade IV point lifecycle, cap i persistence;
- wszystkie 36 adjacency edges;
- max pool i zachowanie po level/premium/promotion changes;
- forged packets i point refund rules.

### Perki i spelle

Dla każdego Dedication/Conviction/Revelation:

```text
definition -> activation -> effect -> stacking -> protocol visibility -> persistence -> runtime -> regression
```

Wymagane wszystkie aktywne profesje, w tym Monk tylko zgodnie z aktywną wersją danych/protokołu.

### Gem Atelier

- reveal/bind/remove/destroy;
- fragment yields;
- affinity clockwise rotation;
- socket matching i 4 active vessels;
- Vessel Resonance i kolejność mod slotów;
- +1/+1/+2 damage/healing;
- effective grade gating przez poprzedni slot;
- Momentum;
- transactional failure paths;
- save/load UUID consistency.

### Persistence i protocol

- schema, migrations, KV i corrupted/legacy data;
- complete round-trip;
- legacy payload path;
- opcodes, field order, widths, counts i feature gates;
- compatible OTClient comparison;
- malformed indexes/counts rejected server-side.

Machine-readable plan: `docs/ai-agent/WHEEL_OF_DESTINY_RUNTIME_TEST_PLAN.json`.

---

## 10. Safety boundary

W PR #169 nie wolno zmieniać:

- balansu i wartości aktywnego Wheel;
- spell/combat behavior;
- protocol payload/opcodes;
- schema/migrations;
- itemów, datapacka, `.otbm`, `items.otb` ani client assets;
- produkcyjnej konfiguracji.

Każdy potwierdzony defect ma trafić do osobnego, małego PR-a z focused testem. Nie łączyć cost fix, points accounting, Revelation Mastery, cap enforcement ani input hardening w jednym PR-ze.

---

## 11. Changelog / work log

### 2026-07-12 — current-payload caller review i scanner protocol boundary

- potwierdzono `0xE7 -> parseWheelGemAction()` dla current payload;
- potwierdzono brak cap 225 w parserze i `revealGem()`; WOD-R002 podniesiono do WOD-F004;
- potwierdzono przekazanie dowolnego byte `position` do bezpośredniego indeksowania tablic 49/95; WOD-R004 podniesiono do WOD-F005;
- potwierdzono, że invalid index dla destroy/switch/lock przechodzi przez bezpieczny `getGem()` guard;
- rozszerzono scanner o `protocolgame.cpp`, cap invariant i bounds safety;
- zaktualizowano focused fixtures/test assertions;
- lokalnie ponownie wykonano 7 testów: `OK`;
- najnowszy CI po rozszerzeniu jest pending;
- nie zmieniono gameplay, protokołu, schema, datapacka ani mapy.

### 2026-07-12 — pierwszy CI artifact

- workflow run `29203018790` zakończył się sukcesem;
- wszystkie kroki: tests, audit, JSON validation, summary i artifact upload — success;
- artifact: 30 source files, 4 errors, 6 warnings, 16 doubled Revelation modifiers;
- zaktualizowano evidence report dokładnymi wynikami.

### 2026-07-12 — scanner, baseline, report, runtime plan i CI

- dodano `WHEEL_OF_DESTINY_REFERENCE_BASELINE.json`;
- dodano 20 machine-readable runtime/protocol/persistence scenarios;
- dodano początkowy evidence report;
- dodano deterministic read-only scanner;
- dodano 7 focused unit tests;
- wynik lokalny: `Ran 7 tests ... OK`;
- dodano dedykowany GitHub Actions workflow;
- potwierdzono WOD-F001, WOD-F002 i WOD-F003 na poziomie statycznym;
- zapisano początkowe ryzyka bez przedwczesnych runtime claims;
- nie zmieniono gameplay, protokołu, schema, datapacka ani mapy.

### 2026-07-12 — publikacja pracy

- utworzono branch `feat/wheel-of-destiny-validation-audit`;
- utworzono draft PR #169;
- utworzono persistent task record;
- dodano wpis do `docs/agents/ACTIVE_WORK.md`;
- merge-base gałęzi: `dbcc809bac57bb78425ca39c2523c723cef79bb0`;
- `main` przesunął się po utworzeniu gałęzi niezależnym commitem dokumentacyjnym; brak overlap z owned paths.

### 2026-07-12 — utworzenie projektu

- utworzono ten dokument obok głównego World Validation project;
- zapisano scope, evidence layers, safety boundary i handoff;
- nie zmieniono runtime.

---

## 12. Aktualny stan

```text
branch: feat/wheel-of-destiny-validation-audit
merge-base: dbcc809bac57bb78425ca39c2523c723cef79bb0
PR: #169 draft
phase: current-payload boundary classified; latest enhanced scanner CI pending
first CI: run 29203018790 passed
local tests after enhancement: 7 passed
confirmed findings: WOD-F001..WOD-F005
runtime claims: none
gameplay changes: none
```

### Acceptance state

- [x] dedykowany durable project document;
- [x] versioned reference baseline;
- [x] deterministic static scanner;
- [x] focused unit tests;
- [x] initial evidence report;
- [x] machine-readable runtime test plan;
- [x] dedicated CI workflow;
- [x] pierwszy CI run na actual repository branch reviewed;
- [x] current-payload Reveal/ImproveGrade caller boundary reviewed;
- [ ] CI run rozszerzonego protocol scanner reviewed;
- [ ] complete Wheel/Gem source and call-site inventory;
- [ ] every perk mapped to effect path;
- [ ] persistence round-trip reviewed;
- [ ] OTClient protocol contract reviewed;
- [ ] runtime scenarios executed;
- [ ] confirmed defects split into focused follow-up PRs.

---

## 13. Handoff dla kolejnego agenta

### Start here

1. Przeczytaj `AGENTS.md` i `docs/agents/**`.
2. Przeczytaj `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`.
3. Przeczytaj ten dokument i `WHEEL_OF_DESTINY_VALIDATION_REPORT.md`.
4. Otwórz PR #169, aktualny task record i workflow runs dla head.
5. Pobierz najnowszy artifact `WHEEL_OF_DESTINY_AUDIT.json/.md`.
6. Nie naprawiaj gameplay w PR #169.

### Następny krok techniczny

1. Sprawdź CI dla head po commitach protocol scanner/test.
2. Potwierdź exact finding counts: oczekiwane 6 errors / 4 warnings, ale nie zapisuj tego jako wynik bez artifactu.
3. Zaktualizuj report, ten dokument, task record i PR body wynikiem CI.
4. Prześledź legacy `Game::playerWheelGemAction`.
5. Zmapuj save/load, migrations/KV oraz wszystkie Hunting Task point paths.
6. Porównaj current i legacy payload z kompatybilnym `opentibiabr/otclient`.
7. Dopiero potem przygotuj osobne defect PR-y.

### Nie powtarzaj

- nie licz samego highest enum ID jako liczby slice'ów bez parsera;
- nie uznawaj wiki za niewersjonowany official truth;
- nie uznawaj getter'a za dowód efektu;
- nie uznawaj resource-order warning za exploit bez fault-injection evidence;
- nie uznawaj static match za runtime verified;
- nie łącz WOD-F001..F005 w jeden gameplay PR;
- nie zmieniaj upstream `opentibiabr/canary`.

### Otwarte pytania

- Gdzie i jak Hunting Task Shop zapisuje dodatkowe punkty?
- Jak legacy payload waliduje action, quality, index i grade position?
- Czy resource prechecks eliminują partial-consumption failure, czy potrzebna jest transakcja/refund?
- Jaki jest zamierzony drugi neighbour dla `SLOT_GREEN_TOP_100`?
- Czy wszystkie Revelation Mastery variants są rzeczywiście podwajane w runtime?
- Czy wszystkie pięć vocations ma kompletny Wheel i spell augment coverage?
- Czy kompatybilny OTClient ogranicza UI, ale serwer nadal musi bronić invariantów niezależnie od klienta?

### Obowiązek aktualizacji

Po każdej zmianie kodu, testu, baseline, raportu, klasyfikacji lub decyzji:

1. zaktualizuj ten dokument;
2. zaktualizuj `docs/agents/tasks/active/CAN-20260712-wheel-of-destiny-validation.md`;
3. zapisz exact command/check i wynik;
4. zaktualizuj PR body, jeżeli zmienił się zakres lub evidence;
5. nie wpisuj `passed` ani `verified` bez wykonania odpowiedniego checku.
