# OTS AI Achievement Validation — cel, metodologia, stan i handoff

> **Stan dokumentu:** 2026-07-12  
> **Projekt nadrzędny:** `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`  
> **Repozytorium zapisywalne:** `blakinio/canary`  
> **Gałąź robocza:** `feat/achievement-validation-audit`  
> **PR roboczy:** `#165`  
> **Aktualny etap:** narzędzie read-only zaimplementowane; pełny artefakt skanu repozytorium oczekuje na GitHub Actions  
> **Najważniejsza zasada:** brak prostego tekstowego wywołania `addAchievement` nie jest dowodem, że achievement jest nieosiągalny.

---

## 1. Cel projektu

Achievement może być poprawnie zdefiniowany w rejestrze, ale nadal nie działać w grze. Możliwe rozbieżności:

- definicja istnieje, lecz normalna ścieżka gameplay jej nie przyznaje;
- aktywny skrypt odwołuje się do nieistniejącej nazwy lub ID;
- trigger działa wyłącznie przez dynamiczną tabelę albo wrapper;
- wymagany quest, NPC, item, boss, storage lub event jest uszkodzony;
- licznik progressu nie osiąga progu albo nalicza się wielokrotnie;
- metadane rejestru różnią się od źródła referencyjnego;
- helper Lua błędnie iteruje po rzadkiej tabeli;
- komenda administracyjna działa, mimo że normalny trigger nie istnieje;
- zapis KV przestaje się ładować po zmianie nazwy achievementu.

Celem jest powtarzalny proces odróżniający:

```text
definicję
  od statycznej referencji
  od semantycznie poprawnego triggera
  od faktycznej osiągalności w runtime
```

Projekt jest rozszerzeniem OTS AI World Validation i używa tych samych warstw dowodowych. Nie zastępuje walidacji questów, mapy, NPC ani runtime.

---

## 2. Źródła prawdy

### Aktywny rejestr

```text
data/scripts/lib/register_achievements.lua
```

### Aktywne datapacki skanowane domyślnie

```text
data/
data-otservbr-global/
```

### Runtime API

```text
src/creatures/players/components/player_achievement.{hpp,cpp}
src/lua/functions/core/game/game_functions.cpp
data-otservbr-global/lib/functions/players.lua
```

### Źródło referencyjne wskazane przez użytkownika

```text
https://tibia.fandom.com/wiki/Achievements
```

Stan zapisany 2026-07-12 w:

```text
docs/ai-agent/ACHIEVEMENT_REFERENCE_BASELINE.json
```

Baseline:

- 562 achievementy wymienione na stronie;
- 563 łącznie, z jednym nieodkrytym secret achievementem;
- 362 common;
- 200 odkrytych secret z 201 łącznie;
- teoretyczna suma punktów 1470;
- 1425 po wykluczeniu wzajemnie wykluczających się osiągnięć.

TibiaWiki/Fandom jest źródłem referencyjnym, nie bezwarunkowym źródłem prawdy. Różnice trzeba potwierdzić wobec aktualnej gry, aktywnego datapacka i runtime. Do repozytorium nie wolno kopiować pełnych spoilerów.

GitHub, aktualny `main`, otwarte PR-y i aktywny kod są ważniejsze niż pamięć rozmowy oraz stare raporty.

---

## 3. Zaimplementowane narzędzie

Pliki:

```text
tools/ai-agent/achievement_validation.py
tools/ai-agent/test_achievement_validation.py
```

CLI:

```bash
python tools/ai-agent/achievement_validation.py \
  --repository-root . \
  --registry data/scripts/lib/register_achievements.lua \
  --script-root data \
  --script-root data-otservbr-global \
  --reference-baseline docs/ai-agent/ACHIEVEMENT_REFERENCE_BASELINE.json \
  --output artifacts/ACHIEVEMENT_AUDIT.json \
  --markdown artifacts/ACHIEVEMENT_AUDIT.md \
  --allow-findings
```

Bez podania `--script-root` używane są oba aktywne katalogi powyżej.

Format raportu:

```text
canary-achievement-audit-v1
```

Narzędzie:

1. parsuje jawne rekordy `[id] = { ... }`;
2. stosuje domyślne `secret=false`, `grade=0`, `points=0` zgodnie z helperem;
3. wykrywa duplikaty ID i nazw;
4. wykrywa brakujące pola, błędne typy, kolejność ID i luki;
5. sprawdza relację grade/points, zachowując zero-point jako jawną informacyjną wyjątkową wartość;
6. wykrywa niebezpieczne użycie `#ACHIEVEMENTS`;
7. wykrywa potwierdzone błędy `Game.isAchievementSecret`;
8. skanuje aktywne Lua pod kątem:
   - `addAchievement`;
   - `addAchievementProgress`;
   - `hasAchievement`;
   - `removeAchievement`;
   - `addAllAchievements`;
   - `removeAllAchievements`;
9. odróżnia statyczne ID/nazwy od argumentów dynamicznych;
10. oznacza ścieżki `talkactions/god` jako administracyjne;
11. rozwiązuje statyczne referencje wobec rejestru;
12. raportuje nieznane statyczne referencje jako błąd;
13. nadaje per-achievement dyspozycję;
14. porównuje cztery wymiary baseline: count, common, secret i suma punktów;
15. generuje pełny JSON i małe Markdown summary.

Duży raport per-achievement pozostaje artefaktem CI, a nie plikiem commitowanym do repozytorium.

---

## 4. Dyspozycje generowane przez skaner

- `direct-static-award` — aktywny, nieadministracyjny literalny award;
- `static-progress-path` — aktywna literalna ścieżka progressu;
- `referenced-without-static-award` — aktywny check/remove bez statycznego awardu;
- `admin-only-static-reference` — rozpoznana wyłącznie ścieżka administracyjna;
- `no-direct-static-reference` — brak literalnej referencji przypisanej do definicji.

`no-direct-static-reference` nie oznacza automatycznie błędu. Dynamiczne tabele, wrappery, quest state machines i ścieżki engine-side wymagają kolejnej warstwy analizy.

Raport dodatkowo zachowuje:

- wszystkie dynamiczne wywołania z plikiem, linią, metodą i surowym argumentem;
- wszystkie nieznane statyczne wywołania;
- wszystkie resolved references per achievement;
- findings z severity `info`, `warning` albo `error`.

---

## 5. Warstwy walidacji

### Warstwa A — struktura rejestru

Sprawdza parsowalność, typy, pola, unikalność, zakres ID, luki, grade, points i secret.

### Warstwa B — statyczne referencje

Sprawdza, czy literalne nazwy i ID z aktywnych skryptów istnieją oraz czy są awardem, progressem, checkiem, removalem lub ścieżką admin-only.

### Warstwa C — semantyka triggera

Dla każdego przypadku trzeba potwierdzić, że:

- boss kill dotyczy właściwego bossa;
- quest completion nie następuje przed finalnym krokiem;
- progress ma właściwy próg i inkrementuje się raz;
- mutually exclusive achievements nie są przyznawane razem;
- daily/repeatable task nie duplikuje awardu;
- prerequisite denial nie przyznaje achievementu wcześnie.

### Warstwa D — ładowanie runtime

Canary musi zarejestrować wszystkie jawne rekordy, udostępniać lookup po ID/nazwie i poprawnie zapisać/odtworzyć unlocked KV, timestamp i punkty.

### Warstwa E — gameplay E2E

Testowa postać wykonuje realny przepływ z jawnie zadeklarowanym stanem początkowym, akcjami, expected progress, awardem, punktami, idempotencją, relogiem i cleanupem.

### Warstwa F — regresja ciągła

Szybki skan działa przy zmianie rejestru, aktywnych Lua, narzędzia albo baseline. Cięższe testy runtime są uruchamiane według zakresu zmiany.

---

## 6. Potwierdzone ustalenia przed pełnym skanem

### 6.1. Rejestr jest rzadką tabelą Lua

Jawne luki powodują, że najwyższy ID nie jest liczbą achievementów. Operator długości `#` nie stanowi bezpiecznej granicy iteracji po wszystkich wpisach.

### 6.2. Użycie `#ACHIEVEMENTS` jest potwierdzonym defektem infrastrukturalnym

Aktualny helper używa między innymi:

```lua
ACHIEVEMENT_LAST = #ACHIEVEMENTS
```

oraz iteruje `Player.getAchievements` od `1` do `#ACHIEVEMENTS`.

Skutek wymagający testu runtime: wpisy po pierwszych lukach mogą nie być zwracane przez helpery, mimo że rejestracja przez `pairs` je dodała.

Dyspozycja: osobny focused fix po zamknięciu audytu.

### 6.3. `Game.isAchievementSecret` zawiera dwa potwierdzone błędy

Helper wyszukuje `foundAchievement`, ale zwraca:

```lua
return achievement.secret
```

Argument jest ID albo nazwą, nie tabelą metadata. Ponadto ścieżka błędu używa niezdefiniowanej zmiennej `ach`.

Dyspozycja: osobny focused fix z testami ID, name, public, secret i invalid input.

### 6.4. Unlocked KV jest kluczowane nazwą

C++ zapisuje timestamp pod nazwą achievementu i podczas ładowania ponownie mapuje nazwę na aktualne ID.

Konsekwencje:

- zmiana nazwy może osierocić zapis gracza;
- zmiana ID przy zachowaniu nazwy może zostać zmapowana na nowe ID;
- duplikaty nazw są krytyczne;
- rename wymaga migracji kompatybilności.

### 6.5. Zero-point nie może być automatycznie uznane za uszkodzenie

Aktualny rejestr i źródło referencyjne zawierają grade-1 achievement z zerową liczbą punktów. Skaner zapisuje to jako `registry-zero-point-exception` z severity `info`, zamiast tworzyć fałszywy błąd strukturalny.

---

## 7. Testy i workflow

Focused tests obejmują:

- sparsowany rejestr i domyślne pola;
- luki ID;
- błędną relację grade/points;
- statyczne nazwy i ID;
- wywołania dynamiczne;
- ścieżki administracyjne;
- trzy helper findings;
- per-achievement dispositions;
- nieznaną statyczną referencję;
- porównanie baseline.

Lokalnie na izolowanej kopii narzędzia wykonano:

```text
python -m unittest -v
7 tests passed
```

Dodatkowo przeszły `py_compile` oraz `json.tool` dla baseline i runtime planu. Nie jest to dowód pełnego skanu repozytorium.

Dedykowany workflow:

```text
.github/workflows/achievement-validation.yml
```

Wykonuje:

1. focused unittest discovery;
2. pełny skan obu aktywnych datapacków;
3. generowanie JSON i Markdown;
4. walidację JSON;
5. publikację summary;
6. upload artefaktu `achievement-validation-audit` na 14 dni.

`--allow-findings` pozwala opublikować dowody znanych defektów, ale pole `ok` w JSON pozostaje `false`. Workflow nie może udawać, że potwierdzone błędy nie istnieją.

---

## 8. Runtime test plan

Plik:

```text
docs/ai-agent/ACHIEVEMENT_RUNTIME_TEST_PLAN.json
```

Format:

```text
canary-achievement-runtime-test-plan-v1
```

Scenariusze blocking/high obejmują:

- pełną rejestrację wszystkich jawnych rekordów;
- enumerację najwyższego ID pomimo wcześniejszych luk;
- poprawny public/secret lookup po ID i nazwie;
- bezpieczny invalid lookup;
- idempotencję awardu i removalu;
- spójność punktów;
- persistence/reload;
- próg progressu;
- bulk admin award/remove z wysokimi ID;
- reprezentatywne E2E dla NPC, questa, bossa, movement, item use, progress, secret i najnowszego obsługiwanego contentu.

---

## 9. Bezpieczeństwo i granice

W audytowym PR-ze nie wolno:

- modyfikować `register_achievements.lua`;
- zmieniać aktywnych questów, NPC, actions, movements ani creature events;
- modyfikować C++ runtime;
- dodawać achievementów na podstawie zgadywania;
- uznawać braku statycznego matcha za `missing-runtime-path`;
- kopiować pełnej tabeli wiki ani spoilerów;
- commitować pełnego wygenerowanego raportu;
- modyfikować `.otbm`, `items.otb`, assetów ani konfiguracji produkcyjnej.

Każdy potwierdzony fix gameplay lub infrastruktury wymaga oddzielnego branch/task/PR i focused testów.

---

## 10. Stan pierwszego etapu

- [x] rejestr jest deterministycznie parsowany;
- [x] structural findings są generowane;
- [x] oba aktywne katalogi są obsługiwane;
- [x] statyczne nazwy i ID są rozwiązywane;
- [x] dynamiczne referencje są raportowane osobno;
- [x] admin-only jest oddzielone od gameplay;
- [x] powstaje per-achievement klasyfikacja;
- [x] powstał versioned reference baseline;
- [x] powstał runtime test plan;
- [x] focused unit tests przeszły lokalnie;
- [x] dodano dedykowany workflow i artefakt;
- [ ] pierwszy pełny artefakt repozytorium został pobrany i zweryfikowany;
- [ ] powstał finalny mały `ACHIEVEMENT_VALIDATION_REPORT.md`;
- [ ] GitHub checks przeszły na aktualnym headzie;
- [ ] pełny diff i changed-file list przeszły końcowy review.

Pierwszy etap nie dowodzi pełnej osiągalności wszystkich achievementów. Buduje wiarygodny indeks i kolejkę semantycznej/runtime walidacji.

---

## 11. Kolejność dalszych prac

1. Uruchomić pełny workflow i pobrać artefakt.
2. Sprawdzić, czy parser ma false positives albo pominięte formy wywołań.
3. Naprawić sam skaner, aż raport będzie deterministyczny i wiarygodny.
4. Utworzyć mały `ACHIEVEMENT_VALIDATION_REPORT.md` z liczbami i reprezentatywnymi dowodami.
5. Wydzielić helper defects do osobnego PR.
6. Rozwijać bezpieczne resolvery dynamicznych tabel/wrapperów bez zgadywania.
7. Powiązać achievementy z grafem zależności questów.
8. Dodawać małe scenariusze runtime/E2E według mechanizmu.
9. Naprawiać tylko potwierdzone braki, każdy osobno.

---

## 12. Koordynacja

```text
docs/agents/tasks/active/CAN-20260712-achievement-validation.md
docs/agents/ACTIVE_WORK.md
docs/agents/MODULE_CATALOG.md
```

PR #166 dotyczący Imbuing czyta nadrzędny projekt World Validation, ale nie edytuje go i nie pokrywa się z narzędziem achievementów.

---

## 13. Handoff dla kolejnego agenta

### Zacznij od tego

1. Przeczytaj `AGENTS.md`.
2. Przeczytaj `docs/agents/README.md`, `ACTIVE_WORK.md` i `MODULE_CATALOG.md`.
3. Sprawdź wszystkie otwarte PR-y.
4. Przeczytaj `OTS_AI_WORLD_VALIDATION_PROJECT.md`.
5. Przeczytaj ten dokument i aktywny task record.
6. Sprawdź aktualny head i changed files PR #165.
7. Uruchom skaner na prawdziwym checkoutcie.
8. Pobierz artefakt `achievement-validation-audit`.
9. Nie klasyfikuj żadnego achievementu jako missing bez semantycznych albo runtime dowodów.

### Nie powtarzaj

- nie licz definicji przez najwyższe ID;
- nie używaj `#ACHIEVEMENTS` jako liczby rekordów;
- nie mieszaj GOD commands z normalnym gameplay;
- nie traktuj check/remove jako awardu;
- nie analizuj nieaktywnych datapacków jako aktywnych;
- nie kopiuj spoilerów;
- nie commituj pełnego wygenerowanego raportu;
- nie naprawiaj helperów w tym audytowym PR-ze;
- nie odrzucaj automatycznie zero-point exception.

### Ograniczenie środowiska bieżącej sesji

Kontener nie rozwiązuje DNS dla `github.com`, więc nie można wykonać lokalnego clone ani pełnego skanu. GitHub code search nie indeksuje wystarczająco forka. Pełne liczby muszą pochodzić z Actions lub prawdziwego checkoutu.

---

## 14. Changelog

### 2026-07-12 — implementacja pierwszej warstwy walidacji

- dodano deterministyczny parser i skaner aktywnych referencji;
- dodano 7 focused tests;
- dodano wersjonowany baseline TibiaWiki/Fandom;
- dodano machine-readable runtime test plan;
- dodano dedykowany workflow i artefakt;
- skatalogowano moduł dla innych agentów;
- zapisano trzy potwierdzone helper findings;
- utrzymano pełny read-only boundary.

### 2026-07-12 — utworzenie osobnego projektu achievementów

- oddzielono trwały opis od ogólnego projektu World Validation;
- zdefiniowano zakres rejestru, triggerów, zależności gameplay i runtime;
- zdefiniowano statusy, bezpieczeństwo i handoff.
