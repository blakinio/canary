# OTS AI Achievement Validation — cel, metodologia, stan i handoff

> **Stan dokumentu:** 2026-07-12  
> **Projekt nadrzędny:** `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`  
> **Repozytorium zapisywalne:** `blakinio/canary`  
> **Gałąź robocza:** `feat/achievement-validation-audit`  
> **PR roboczy:** `#165`  
> **Aktualny etap:** read-only audyt rejestru achievementów i aktywnych ścieżek ich przyznawania  
> **Najważniejsza zasada:** brak prostego tekstowego wywołania `addAchievement` nie jest dowodem, że achievement jest nieosiągalny.

---

## 1. Po co istnieje ten projekt

Achievement może być poprawnie zdefiniowany w rejestrze, ale nadal nie działać w grze. Możliwe są między innymi następujące rozbieżności:

- achievement istnieje w `ACHIEVEMENTS`, lecz nie ma aktywnej ścieżki przyznania;
- skrypt przyznaje nazwę lub ID, których rejestr nie zawiera;
- trigger istnieje wyłącznie w nieaktywnym datapacku;
- osiągnięcie jest przyznawane przez dynamiczną tabelę albo wrapper, którego prosty grep nie klasyfikuje;
- wymagany quest, NPC, item, boss, storage lub event jest uszkodzony;
- progress counter istnieje, ale nigdy nie osiąga progu;
- metadata rejestru różni się od aktualnego źródła referencyjnego;
- silnik poprawnie zapisuje achievement, ale helper Lua błędnie iteruje po rzadkiej tabeli;
- administrator może przyznać achievement komendą, mimo że normalna ścieżka gameplay nie istnieje.

Celem projektu jest zbudowanie powtarzalnego procesu, który odróżnia definicję od rzeczywistej osiągalności i zapisuje dowody potrzebne do bezpiecznych, małych poprawek.

Projekt jest rozszerzeniem ogólnego OTS AI World Validation. Nie zastępuje walidacji questów, NPC, mapy ani runtime; łączy achievement z tymi warstwami.

---

## 2. Zakres walidacji

### 2.1. Rejestr achievementów

Źródło aktywne:

```text
data/scripts/lib/register_achievements.lua
```

Sprawdzane elementy:

- unikalność ID;
- unikalność nazw;
- obecność nazwy i opisu;
- poprawność `grade`, `points` i `secret`;
- zgodność punktów z zakresem wynikającym z grade;
- jawne luki ID;
- rzadkość tabeli i miejsca używające operatora długości `#`;
- zgodność wywołania `Game.registerAchievement` z API silnika.

### 2.2. Aktywne ścieżki runtime

Skan obejmuje aktywne katalogi:

```text
data/
data-otservbr-global/
```

Klasyfikowane operacje:

- `Player:addAchievement(...)`;
- `Player:addAchievementProgress(...)`;
- `Player:hasAchievement(...)`;
- `Player:removeAchievement(...)`;
- `Player:addAllAchievements(...)` i komendy administratorskie;
- wrappery i helpery wywołujące powyższe API;
- statyczne tabele zawierające nazwy lub ID;
- dynamiczne argumenty, których nie można bezpiecznie rozwinąć statycznie.

### 2.3. Zależności gameplay

Dla każdego achievementu docelowo należy ustalić:

```text
achievement
  -> trigger
  -> quest / task / world change
  -> NPC / monster / boss
  -> item / action / movement / event
  -> storage / KV / progress counter
  -> warunek początkowy
  -> efekt końcowy
```

### 2.4. Źródło referencyjne

Źródło porównawcze wskazane przez użytkownika:

```text
https://tibia.fandom.com/wiki/Achievements
```

Stan odczytany 2026-07-12:

- strona deklaruje 362 common i 200 z 201 secret achievements;
- deklaruje 562 z 563 odkrytych achievementów;
- tabela ma nagłówek `List of Achievements (562)`;
- strona podaje teoretyczną sumę 1470 punktów i 1425 po wykluczeniu wzajemnie wykluczających się osiągnięć.

Fandom/TibiaWiki jest źródłem referencyjnym, nie bezwarunkowym źródłem prawdy. Każdą różnicę należy potwierdzić także wobec aktualnej wersji gry, aktywnego datapacka i zachowania runtime. Nie wolno kopiować całych spoilerów ani dużej części tabeli do repozytorium.

---

## 3. Warstwy walidacji

### Warstwa A — struktura rejestru

Pytanie: czy rejestr da się deterministycznie sparsować i zarejestrować?

Wyniki:

- liczba definicji;
- zakres ID;
- luki;
- duplikaty;
- brakujące pola;
- błędne typy i zakresy metadata.

### Warstwa B — statyczne referencje

Pytanie: czy wszystkie statyczne nazwy i ID używane w aktywnych skryptach istnieją w rejestrze?

Wyniki:

- poprawne statyczne awardy;
- nieznane nazwy/ID;
- check-only;
- remove-only;
- progress-only;
- admin-only;
- dynamic-unresolved.

### Warstwa C — spójność semantyczna

Pytanie: czy trigger odpowiada warunkowi opisanemu przez achievement?

Przykłady:

- boss kill rzeczywiście dotyczy właściwego bossa;
- quest completion występuje dopiero po finalnym kroku;
- licznik postępu ma właściwy próg i inkrementuje się raz;
- wzajemnie wykluczające się achievementy nie są przyznawane razem;
- daily/repeatable task nie duplikuje awardu ani progressu.

### Warstwa D — ładowanie runtime

Pytanie: czy rejestr i wszystkie aktywne skrypty ładują się bez błędów?

Minimalne kontrole:

- `Game.registerAchievement` rejestruje wszystkie poprawne rekordy;
- nie występują błędy nieznanych achievementów podczas startu;
- API Lua zwraca poprawne dane po ID i nazwie;
- zapis i ponowne wczytanie unlocked achievements zachowują ID, nazwę, timestamp i punkty.

### Warstwa E — scenariusze gameplay

Pytanie: czy testowa postać może faktycznie zdobyć achievement zgodnie z oczekiwanym przepływem?

Każdy scenariusz powinien deklarować:

- początkowe storage/KV;
- wymagane itemy, NPC, potwory i pozycje;
- akcje gracza;
- oczekiwany progress;
- moment przyznania;
- oczekiwane punkty i komunikat;
- idempotencję przy powtórzeniu;
- zachowanie po relogu;
- cleanup.

### Warstwa F — regresja ciągła

Pytanie: czy zmiana questa, NPC, itemu lub eventu nie usuwa potwierdzonej ścieżki achievementu?

CI powinno uruchamiać szybki skan rejestru i statycznych referencji przy każdej zmianie odpowiednich ścieżek. Cięższe testy runtime i E2E powinny być uruchamiane według zakresu zmiany albo harmonogramu.

---

## 4. Dyspozycje audytu

Każdy achievement otrzymuje niezależne statusy dla definicji i osiągalności.

### Status definicji

- `definition-valid` — rekord jest strukturalnie poprawny;
- `definition-mismatch` — metadata różni się od potwierdzonego źródła;
- `definition-invalid` — rekord nie może być poprawnie zarejestrowany;
- `definition-needs-review` — dowody są niewystarczające.

### Status ścieżki przyznania

- `static-award-confirmed` — istnieje bezpośredni, aktywny i rozwiązywalny award;
- `progress-path-confirmed` — istnieje rozwiązywalny licznik i próg;
- `dynamic-path` — istnieje aktywna ścieżka dynamiczna wymagająca dodatkowej analizy;
- `admin-only` — znaleziono wyłącznie ścieżkę administratorską;
- `check-only` — achievement jest sprawdzany, ale skan nie znalazł awardu;
- `remove-only` — istnieje usuwanie bez znalezionego normalnego awardu;
- `no-static-path` — brak statycznie rozpoznanej ścieżki; nie jest to automatycznie błąd;
- `missing-runtime-path` — mocne dowody potwierdzają brak wymaganej implementacji;
- `runtime-proven` — scenariusz runtime/E2E faktycznie przeszedł;
- `needs-manual-review` — dowody są niewystarczające.

### Confidence

- `high` — bezpośredni aktywny kod, jednoznaczne zależności i/lub test runtime;
- `medium` — silna korelacja statyczna bez pełnego runtime;
- `low` — hipoteza wymagająca dalszych dowodów.

---

## 5. Potwierdzone wstępne ustalenia

### 5.1. Rejestr jest rzadką tabelą Lua

Rejestr zawiera jawne luki, między innymi ID oznaczone komentarzem jako `Unknown/non-existent`. Najwyższy zdefiniowany ID nie jest liczbą achievementów.

Konsekwencja: kod nie może używać `#ACHIEVEMENTS` jako pewnej liczby elementów ani górnej granicy iteracji po wszystkich definicjach.

### 5.2. `ACHIEVEMENT_LAST = #ACHIEVEMENTS` wymaga naprawy w osobnym PR

Aktualny helper ustawia:

```lua
ACHIEVEMENT_LAST = #ACHIEVEMENTS
```

Dla rzadkiej tabeli wynik operatora `#` nie jest wiarygodnym kontraktem liczby rekordów. Ten sam problem dotyczy `Player.getAchievements`, który iteruje od `1` do `#ACHIEVEMENTS`.

Dyspozycja: `confirmed-infrastructure-defect`; nie naprawiać w audytowym PR-ze.

### 5.3. `Game.isAchievementSecret` zwraca niewłaściwą wartość

Helper poprawnie wyszukuje `foundAchievement`, lecz kończy się zwróceniem:

```lua
return achievement.secret
```

Argument `achievement` jest ID albo nazwą, a nie znalezioną tabelą metadata. Powinien zostać użyty wynik wyszukiwania. Dodatkowo ścieżka błędu formatuje niezdefiniowaną zmienną `ach`.

Dyspozycja: `confirmed-infrastructure-defect`; osobny focused fix z testem.

### 5.4. System silnika zapisuje unlocked achievements po nazwie

C++ zapisuje timestamp w scoped KV pod nazwą achievementu, a podczas ładowania ponownie mapuje nazwę na aktualne ID.

Konsekwencje do walidacji:

- zmiana nazwy może osierocić istniejący zapis gracza;
- zmiana ID przy zachowaniu nazwy może zostać zmapowana na nowy ID;
- duplikaty nazw są krytyczne;
- migracje nazw wymagają jawnego planu kompatybilności.

---

## 6. Narzędzie audytowe

Planowane pliki:

```text
tools/ai-agent/achievement_validation.py
tools/ai-agent/test_achievement_validation.py
```

Planowany CLI:

```bash
python tools/ai-agent/achievement_validation.py \
  --repository-root . \
  --registry data/scripts/lib/register_achievements.lua \
  --script-root data \
  --script-root data-otservbr-global \
  --output artifacts/ACHIEVEMENT_VALIDATION.json
```

Minimalny raport JSON powinien zawierać:

- hash i ścieżkę rejestru;
- wszystkie definicje;
- luki i błędy metadata;
- wszystkie znalezione referencje z plikiem i linią;
- klasyfikację typu operacji;
- statycznie rozwiązane nazwy/ID;
- nierozwiązane wyrażenia dynamiczne;
- per-achievement summary;
- globalne findingi infrastrukturalne;
- confidence i evidence paths;
- wersję formatu raportu.

Duży wygenerowany raport powinien być artefaktem CI, nie plikiem commitowanym do repozytorium.

---

## 7. Raport i test plan

Małe trwałe pliki w repozytorium:

```text
docs/ai-agent/ACHIEVEMENT_VALIDATION_REPORT.md
docs/ai-agent/ACHIEVEMENT_RUNTIME_TEST_PLAN.json
```

`ACHIEVEMENT_VALIDATION_REPORT.md` ma zawierać:

- baseline;
- podsumowanie liczebności;
- potwierdzone defekty;
- klasyfikację grup achievementów;
- reprezentatywne dowody;
- ograniczenia statycznej analizy;
- kolejność osobnych PR-ów naprawczych.

`ACHIEVEMENT_RUNTIME_TEST_PLAN.json` ma zawierać małe scenariusze pogrupowane według mechanizmu:

- direct quest completion;
- boss kill;
- item use;
- movement/discovery;
- NPC dialogue/trade;
- progress counter;
- mutually exclusive achievements;
- secret achievement visibility;
- persistence/reload;
- points and removal consistency.

---

## 8. Bezpieczeństwo i granice

W audytowym PR-ze nie wolno:

- modyfikować rejestru achievementów;
- zmieniać aktywnych questów, NPC, actions, movements ani creature events;
- modyfikować C++ runtime;
- dodawać achievementów na podstawie zgadywania;
- uznawać braku statycznego matcha za dowód `missing-runtime-path`;
- kopiować pełnej tabeli Fandom/TibiaWiki ani całych spoilerów;
- commitować surowych wielomegabajtowych raportów;
- modyfikować `.otbm`, `items.otb`, assetów klienta ani konfiguracji produkcyjnej.

Każdy potwierdzony defekt gameplay lub infrastruktury powinien otrzymać oddzielny branch, task record, focused test i PR.

---

## 9. Kryteria ukończenia pierwszego etapu

- [ ] rejestr jest deterministycznie parsowany;
- [ ] wszystkie definicje mają structural status;
- [ ] aktywne katalogi są przeskanowane;
- [ ] statyczne nazwy i ID są rozwiązane wobec rejestru;
- [ ] dynamiczne referencje są raportowane osobno;
- [ ] admin-only nie jest mylone z gameplay-obtainable;
- [ ] powstaje per-achievement klasyfikacja;
- [ ] powstaje mały evidence report;
- [ ] powstaje runtime test plan;
- [ ] focused unit tests przechodzą;
- [ ] AI Agent Tools CI przechodzi na aktualnym headzie;
- [ ] pełny diff nie zawiera zmian gameplay, mapy ani assetów.

Pierwszy etap nie dowodzi pełnej osiągalności wszystkich achievementów. Buduje wiarygodny indeks i kolejkę ręcznej/runtime walidacji.

---

## 10. Kolejne etapy

1. Naprawić potwierdzone helper defects w osobnym PR.
2. Zweryfikować metadata rejestru wobec aktualnego źródła referencyjnego.
3. Sklasyfikować wszystkie dynamiczne award tables i wrappery.
4. Połączyć achievementy z grafem zależności questów.
5. Wybrać reprezentatywne scenariusze runtime dla każdego typu triggera.
6. Naprawiać wyłącznie potwierdzone braki w małych PR-ach.
7. Dodać CI regression gate dla registry/reference audit.

---

## 11. Źródła prawdy

### Projekt nadrzędny

```text
docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md
```

### Projekt achievementów

```text
docs/ai-agent/OTS_AI_ACHIEVEMENT_VALIDATION_PROJECT.md
```

### Rejestr

```text
data/scripts/lib/register_achievements.lua
```

### Runtime API

```text
src/creatures/players/components/player_achievement.{hpp,cpp}
src/lua/functions/core/game/game_functions.cpp
data-otservbr-global/lib/functions/players.lua
```

### Koordynacja

```text
docs/agents/tasks/active/CAN-20260712-achievement-validation.md
docs/agents/ACTIVE_WORK.md
```

GitHub, aktualny `main`, otwarte PR-y i aktywny kod są ważniejsze niż pamięć rozmowy oraz stare raporty.

---

## 12. Handoff dla kolejnego agenta

### Zacznij od tego

1. Przeczytaj `AGENTS.md`.
2. Przeczytaj `docs/agents/README.md` i `ACTIVE_WORK.md`.
3. Sprawdź wszystkie otwarte PR-y.
4. Przeczytaj nadrzędny projekt World Validation.
5. Przeczytaj ten dokument.
6. Przeczytaj aktywny task record.
7. Sprawdź aktualny head PR `#165` i changed files.
8. Przeczytaj rejestr oraz Player achievement API.
9. Nie zakładaj, że liczby zapisane w tym dokumencie są nadal aktualne; ponownie uruchom skaner.

### Nie powtarzaj

- nie licz achievementów przez najwyższe ID;
- nie używaj `#ACHIEVEMENTS` jako pewnej liczby rekordów;
- nie uznawaj braku direct call za dowód nieosiągalności;
- nie mieszaj komend GOD z normalnym gameplay;
- nie traktuj check/remove jako awardu;
- nie analizuj nieaktywnych datapacków razem z aktywnymi bez jawnej etykiety;
- nie kopiuj całych spoilerów z wiki;
- nie naprawiaj wielu niepowiązanych achievementów w jednym PR-ze.

### Po każdym zakończonym etapie

1. zaktualizuj aktywny task record;
2. zaktualizuj changelog w tym dokumencie;
3. zaktualizuj mały evidence report;
4. uruchom focused tests i AI Agent Tools CI;
5. sprawdź pełny changed-file list i diff;
6. zapisz ograniczenia oraz dokładne niewykonane testy runtime;
7. wydziel gameplay fixes do osobnych PR-ów.

---

## 13. Changelog

### 2026-07-12 — utworzenie osobnego projektu achievementów

- oddzielono trwały opis walidacji achievementów od ogólnego projektu World Validation;
- zapisano zakres rejestru, triggerów, zależności gameplay i runtime;
- zdefiniowano statusy definicji i osiągalności;
- zapisano dwa potwierdzone defekty helperów Lua do osobnych focused PR-ów;
- zdefiniowano plan narzędzia, raportu i runtime test planu;
- utrwalono zasady bezpieczeństwa i handoff dla kolejnego agenta.
