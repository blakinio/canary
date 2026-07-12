# OTS AI Wheel of Destiny Validation — cel, metodologia, stan i handoff

> **Stan dokumentu:** 2026-07-12  
> **Projekt nadrzędny:** `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`  
> **Repozytorium zapisywalne:** `blakinio/canary`  
> **Gałąź robocza:** `feat/wheel-of-destiny-validation-audit`  
> **PR roboczy:** pending  
> **Aktualny etap:** read-only inwentaryzacja implementacji Wheel of Destiny i Gem Atelier  
> **Najważniejsza zasada:** obecność handlera lub danych nie dowodzi poprawności efektu gameplay; każda cecha musi mieć oddzielne dowody definicji, aktywacji, naliczania, zapisu i protokołu.

---

## 1. Po co istnieje ten projekt

Wheel of Destiny jest systemem rozproszonym pomiędzy:

- definicje koła i perków;
- stan postaci i zapis do bazy;
- przydzielanie promotion points;
- aktywację slice'ów, conviction i revelation perks;
- modyfikatory czarów, walki, leczenia, statystyk i odporności;
- Gem Atelier, affinity, sockety, resonance i fragmenty;
- protokół klient–serwer;
- Lua, itemy, bossy i źródła dodatkowych punktów;
- migracje danych i zgodność z klientem.

Każda warstwa może wyglądać poprawnie osobno, a pełna mechanika nadal może być błędna. Przykładowe klasy problemów:

- klient pokazuje perk jako aktywny, ale serwer nie stosuje bonusu;
- serwer liczy bonus, lecz nie zapisuje poprawnie presetów lub gemów;
- dwa źródła bonusu sumują się niezgodnie z regułą oficjalną;
- spell augment ma poprawną nazwę, ale modyfikuje zły etap obliczeń;
- affinity, resonance albo kolejność mod slotów jest walidowana niepoprawnie;
- koszt reveal/rotate/upgrade różni się od źródła referencyjnego;
- dodatkowe promotion points są przyznawane albo limitowane błędnie;
- opcodes lub kolejność pól protokołu różnią się między serwerem i klientem;
- system działa dla jednej profesji, ale nie dla pozostałych;
- funkcja istnieje, lecz nie ma testu potwierdzającego realny efekt.

Celem projektu jest stworzenie powtarzalnej, evidence-based walidacji całego systemu oraz trwałego handoffu dla kolejnych agentów. Pierwszy etap pozostaje read-only: nie zmienia balansu, danych koła, protokołu ani gameplay.

---

## 2. Źródła prawdy

### 2.1. Repozytorium runtime

Zapisywalne źródło:

```text
blakinio/canary
```

Upstream referencyjny, tylko do odczytu:

```text
opentibiabr/canary
```

### 2.2. Źródło gameplay wskazane przez użytkownika

```text
https://tibia.fandom.com/wiki/Wheel_of_Destiny
```

Stan odczytany 2026-07-12 obejmuje między innymi:

- 1 promotion point za każdy poziom po 50 dla promowanej postaci premium;
- cztery domeny i 36 slice'ów;
- Revelation Perks przy progach 250 / 500 / 1000 punktów w domenie;
- darmowy reset punktów wyłącznie w temple;
- Gem Atelier, maksymalnie 225 ujawnionych gemów;
- affinity domeny, Vessel Resonance i aktywację kolejnych mod slotów;
- bonus resonance: lesser +1, regular +1, greater +2 do damage/healing;
- koszty reveal i rotate zależne od rozmiaru gema;
- Fragment Workshop, Grade I–IV i zależność aktywnego grade od poprzedniego slotu;
- dodatkowe promotion points za pełne ulepszenie modów do Grade IV;
- dodatkowe źródła punktów opisane na stronie referencyjnej.

TibiaWiki/Fandom jest źródłem porównawczym, nie automatycznym dowodem implementacyjnym. Dla spornych lub zmiennych wartości należy szukać oficjalnych changelogów CipSoft i zachować datę wersji.

### 2.3. Źródła kontraktu klient–serwer

Jeżeli audyt dotknie payloadu lub opcode, wymagane jest równoległe porównanie z kompatybilnym OTClientem i zapis kontraktu w `docs/agents/CROSS_REPO_CONTRACTS.md`. Ten PR nie zmienia protokołu.

---

## 3. Wstępna inwentaryzacja kodu

Potwierdzone główne ścieżki w Canary:

```text
src/io/io_wheel.hpp
src/io/io_wheel.cpp
src/creatures/players/components/wheel/player_wheel.hpp
src/creatures/players/components/wheel/player_wheel.cpp
src/creatures/players/components/wheel/wheel_definitions.hpp
src/creatures/players/components/wheel/wheel_gems.hpp
src/creatures/players/components/wheel/wheel_gems.cpp
src/creatures/players/components/wheel/wheel_spells.hpp
src/enums/player_wheel.hpp
src/server/network/protocol/protocolgame.hpp
src/io/iologindata.cpp
src/io/functions/iologindata_load_player.cpp
data/scripts/actions/items/wheel_scrolls.lua
data-otservbr-global/migrations/32.lua
data-otservbr-global/migrations/33.lua
```

Powiązane ścieżki wymagające skanowania:

```text
src/creatures/combat/**
src/creatures/players/vocations/**
src/lua/functions/creatures/player/**
data/scripts/spells/**
data/scripts/actions/**
data-otservbr-global/**
schema.sql
```

Lista jest wstępna. Nie wolno uznać jej za pełną bez deterministycznego skanu wszystkich symboli Wheel, perków, gemów i promotion points.

---

## 4. Zakres walidacji

### 4.1. Dostęp i promotion points

Sprawdzić:

- wymagania level, promotion i premium;
- wzór bazowych punktów;
- limity i źródła dodatkowych punktów;
- scrolls, questy, task shop i punkty z gem modów;
- maksymalną pulę i zachowanie po zmianie level/premium/promotion;
- walidację wydawania, zwrotu i resetu punktów;
- ograniczenie resetu do temple;
- brak duplikacji punktów przy ponownym użyciu źródła.

### 4.2. Topologia koła

Sprawdzić:

- cztery domeny;
- 36 slice'ów;
- połączenia i odblokowywanie sąsiednich slice'ów;
- koszt i limit każdego slice'a;
- odblokowanie Conviction Perk po pełnym slice;
- sumowanie wielokrotnych Conviction Perks;
- progi Revelation 250 / 500 / 1000 na domenę;
- poprawność wszystkich profesji, w tym Monk jeżeli aktywna wersja protokołu/danych go obsługuje;
- zachowanie presetów i przełączania konfiguracji.

### 4.3. Dedication Perks

Dla każdego bonusu potwierdzić:

```text
definicja
  -> koszt / progres
  -> aktywacja
  -> miejsce obliczenia
  -> stacking
  -> widoczność klienta
  -> zapis / reload
  -> test runtime
```

Kategorie obejmują między innymi HP, mana, capacity, skills, magic level, obrażenia, leczenie i odporności. Dokładna lista musi wynikać z kodu i danych, nie z pamięci.

### 4.4. Conviction Perks i spell augments

Dla każdego perka:

- profesja i slice;
- nazwa/ID;
- warunek aktywacji;
- efekt i jednostka;
- stacking;
- modyfikowany spell lub mechanika;
- etap obliczenia damage/healing/cooldown/mana/range/area;
- interakcja z innymi perkami, charmami, imbue, equipment i gem mods;
- test pozytywny, negatywny i graniczny.

### 4.5. Revelation Perks

Dla każdego z czterech perków profesji:

- progi stage 1/2/3;
- efekt każdego stage;
- aktywacja/dezaktywacja po zmianie presetów;
- cooldown, duration, charges i eventy okresowe;
- cleanup po logout/death/reload;
- brak przecieku efektu pomiędzy presetami lub profesjami.

### 4.6. Gem Atelier

Sprawdzić:

- typy lesser / regular / greater;
- liczbę Basic/Supreme mod slotów;
- maksymalnie 225 ujawnionych gemów;
- reveal, bind, destroy/remove i persistence;
- domain affinity i rotację clockwise;
- socket matching;
- Vessel Resonance i kolejność aktywacji slotów;
- bonus damage/healing przy pełnej liczbie resonance;
- koszty reveal i rotate;
- rozbijanie gemów i fragment rewards;
- upgrade Grade I–IV;
- koszt fragmentów i gold dla Basic/Supreme;
- zasadę, że aktywny grade slotu nie może przekroczyć grade poprzedniego slotu;
- +50% wartości Grade IV względem Grade I tam, gdzie reguła ma zastosowanie;
- Momentum dla cooldown augments;
- dodatkowy promotion point za pełne Grade IV;
- limity, idempotencję i rollback transakcji.

### 4.7. Persistence i migracje

Sprawdzić:

- schema i migracje;
- serializację/deserializację presets, points, unlocked gems i grades;
- walidację danych uszkodzonych, starych i częściowych;
- brak utraty danych przy save/load;
- zachowanie po zmianie wersji klienta/serwera;
- transakcyjność operacji kosztowych.

### 4.8. Protokół

Sprawdzić bez zmiany kontraktu:

- opcodes inbound/outbound;
- kolejność, szerokość i signedness pól;
- count fields i limity;
- feature/version gates;
- payload koła, presetów, gem atelier, reveal, rotate, socket i upgrade;
- zachowanie na nieobsługiwanym kliencie;
- walidację wejścia po stronie serwera.

### 4.9. Runtime i regresja

Docelowo wymagane są scenariusze:

- bazowe punkty dla poziomów 50/51 i wysokiego levelu;
- reset poza temple i w temple;
- odblokowanie slice adjacency;
- każdy typ dedication bonusu;
- reprezentatywny spell augment każdej profesji;
- każdy Revelation stage;
- reveal/socket/unsocket/rotate/upgrade gema;
- persistence przez save/logout/login;
- błędne, powtórzone i graniczne pakiety klienta;
- brak bonusu po dezaktywacji presetu.

---

## 5. Warstwy dowodowe

Każdy element otrzymuje niezależny status w następujących warstwach:

1. **definition** — istnieje kompletna definicja;
2. **reference** — wszystkie symbole, itemy, spelle i pola mają cel;
3. **activation** — istnieje osiągalna ścieżka aktywacji;
4. **effect** — efekt jest naliczany w odpowiednim miejscu;
5. **persistence** — stan przeżywa save/load;
6. **protocol** — klient i serwer zgadzają się co do kontraktu;
7. **runtime** — scenariusz gameplay potwierdza zachowanie;
8. **regression** — test automatyczny chroni potwierdzone zachowanie.

Nie wolno podnosić statusu wyższej warstwy na podstawie samej obecności kodu w niższej.

---

## 6. Klasyfikacja wyników

Planowane disposition:

- `verified` — zgodność potwierdzona odpowiednimi dowodami i testem;
- `static-consistent` — definicje i referencje są spójne, runtime niepotwierdzony;
- `protocol-unverified` — logika wygląda spójnie, ale kontrakt klienta nie został zweryfikowany;
- `runtime-unverified` — brak testu rzeczywistego efektu;
- `partial` — część wariantów/profesji/stage działa lub jest zaimplementowana;
- `mismatch` — potwierdzona różnica względem wybranego źródła prawdy;
- `missing-path` — definicja istnieje, ale brak osiągalnej aktywacji;
- `missing-effect` — aktywacja istnieje, ale brak efektu;
- `persistence-risk` — zapis/load jest niepełny albo niebezpieczny;
- `needs-manual-review` — dowody są niewystarczające;
- `out-of-scope-version` — cecha pochodzi z innej wersji Tibii/protokołu.

Każdy `mismatch` musi podawać:

- wersję i datę źródła referencyjnego;
- dokładną ścieżkę i symbol w kodzie;
- aktualne zachowanie;
- oczekiwane zachowanie;
- confidence;
- najmniejszy bezpieczny follow-up PR.

---

## 7. Plan artefaktów

Pierwszy audyt powinien dostarczyć:

```text
tools/ai-agent/wheel_of_destiny_validation.py
tools/ai-agent/test_wheel_of_destiny_validation.py
docs/ai-agent/WHEEL_OF_DESTINY_VALIDATION_REPORT.md
docs/ai-agent/WHEEL_OF_DESTINY_RUNTIME_TEST_PLAN.json
```

Planowane narzędzie ma być deterministyczne i read-only. Powinno co najmniej:

- zinwentaryzować pliki i symbole Wheel;
- wyodrębnić definicje profesji, slice'ów, perków i gemów;
- zmapować miejsca użycia perków i augmentów;
- zmapować persistence, migracje i protocol handlers;
- wykrywać definicje bez efektu oraz efekt bez definicji;
- generować raport i plan scenariuszy bez modyfikacji datapacka.

---

## 8. Safety boundary

W tym pierwszym PR nie wolno zmieniać:

- wartości balansu;
- aktywnych definicji Wheel/Gem Atelier;
- spell/combat behavior;
- protokołu;
- schema/migracji;
- itemów i datapacka;
- `.otbm`, `items.otb` ani assetów klienta;
- produkcyjnej konfiguracji.

Potwierdzone defekty muszą być dzielone na osobne, małe PR-y z focused testami. Zmiana protokołu wymaga osobnego kontraktu Canary ↔ OTClient.

---

## 9. Changelog / work log

### 2026-07-12 — utworzenie projektu walidacji Wheel of Destiny

- utworzono dedykowany dokument obok głównego World Validation project;
- zapisano read-only scope i źródła prawdy;
- zapisano wstępną inwentaryzację głównych plików Wheel;
- rozdzielono warstwy definition/reference/activation/effect/persistence/protocol/runtime/regression;
- zapisano zakres Wheel, spell augments, Revelation Perks i Gem Atelier;
- zapisano plan deterministycznego narzędzia, raportu i runtime test planu;
- nie zmieniono gameplay, danych, protokołu ani mapy.

---

## 10. Aktualny stan

```text
branch: feat/wheel-of-destiny-validation-audit
base: main @ dbcc809bac57bb78425ca39c2523c723cef79bb0
PR: pending
phase: repository inventory
code changes: none
runtime claims: none
```

Potwierdzone na tym etapie:

- repozytorium zawiera rozbudowany komponent Wheel, IO i Gem Atelier;
- system ma zależności w combat/spells/vocations/protocol/persistence/Lua;
- brak istniejącego aktywnego PR-a walidującego Wheel of Destiny;
- wymagany jest osobny audyt, ponieważ sama walidacja questów nie obejmuje efektów koła.

Niepotwierdzone jeszcze:

- kompletność wszystkich perków i profesji;
- zgodność wartości balansu;
- poprawność kosztów Gem Atelier;
- poprawność protocol payload;
- save/load round-trip;
- rzeczywiste efekty runtime.

---

## 11. Handoff dla kolejnego agenta

### Zacznij od tego

1. Przeczytaj `AGENTS.md` i `docs/agents/**`.
2. Przeczytaj `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`.
3. Przeczytaj ten dokument w całości.
4. Sprawdź aktualny `main`, otwarte PR-y i task record.
5. Nie zakładaj, że lista plików z sekcji 3 jest kompletna.
6. Najpierw wykonaj deterministyczną inwentaryzację, potem klasyfikację.
7. Oddziel wartości aktualnej wersji od historycznych zmian balansu.
8. Nie naprawiaj gameplay w audytowym PR-ze.

### Minimalna kolejność analizy

1. `wheel_definitions.hpp` i enumy;
2. `player_wheel.*`;
3. `wheel_gems.*`;
4. `io_wheel.*` i save/load;
5. protocol handlers;
6. wszystkie call sites perków/spell augments;
7. Lua/itemowe źródła punktów;
8. schema i migracje;
9. kompatybilny OTClient;
10. focused runtime scenarios.

### Czego nie zgadywać

- znaczenia numeric enum bez potwierdzenia po obu stronach protokołu;
- oficjalnej wartości balansu bez wersjonowanego źródła;
- osiągalności dodatkowych punktów na podstawie samej obecności skryptu;
- poprawności efektu na podstawie samego getter'a;
- kompatybilności klienta bez porównania payloadu;
- obsługi Monk bez sprawdzenia wersji danych i protokołu.

### Obowiązek aktualizacji

Po każdej zmianie kodu, testu, raportu, klasyfikacji lub decyzji:

1. zaktualizuj ten dokument;
2. zaktualizuj task record;
3. zapisz dokładny test i wynik;
4. zaktualizuj PR body, jeżeli zmienia się zakres lub stan;
5. nie oznaczaj warstwy jako `verified` bez odpowiedniego dowodu.
