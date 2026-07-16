# OTS — końcowe archiwum pracy agenta

**Data archiwizacji:** 2026-07-14  
**Repozytorium robocze:** `blakinio/canary`  
**Aktualny `main` podczas archiwizacji:** `1410a8622aaca5e4afe1bd15aa2695e2dbb7bb94`  
**Merge produkcyjnego hardeningu account-wide quests:** `e1086633ea36f94495198b6195db2097ed7c3797` — PR #124

---

## 1. Cel zakończonego zakresu

Zaimplementować bezpieczny system współdzielenia trwałego dostępu do lokacji questowych między postaciami na jednym koncie, bez kopiowania storage ukończenia questa.

Zasady:

- progres questa, quest log, stany walk i cooldowny pozostają per postać;
- trwałe przejścia, drzwi i wybrane teleporty mogą być per konto;
- nagrody są kontrolowane przez `rewardMode`;
- reward roomy i finałowe walki nie są automatycznie współdzielone;
- reset postaci nie usuwa trwałego dostępu konta ani historii nagród.

---

## 2. Status końcowy

**Zakres repozytoryjny jest zakończony i znajduje się na `main`.**

Zaimplementowane questy:

1. The Ape City
2. The Secret Service
3. In Service of Yalahar
4. The New Frontier
5. Wrath of the Emperor

Zaimplementowane elementy techniczne:

- persistence account-wide access;
- tryby nagród `oncePerAccount` i `oncePerCharacter`;
- reset postępu per postać;
- completion-only unlock gates;
- główny przełącznik `accountWideQuestSystemEnabled`;
- atomowy reward claim przez `db.queryAffectedRows`;
- administracyjna komenda `/questaccess [Player Name]`;
- migracja DB 62;
- tabela audytowa `account_quest_migrations`;
- narzędzie dry-run-first do migracji quest ID i storage;
- testy integracyjne na tymczasowej MariaDB 11.4;
- walidator kontraktu;
- dokumentacja Lua API;
- handoff w `docs/systems/account-wide-quests-handoff.md`.

Brak otwartych PR-ów dotyczących account-wide quests podczas archiwizacji.

---

## 3. Najważniejsze PR-y

| PR | Zakres | Status |
|---:|---|---|
| #31 | framework, persistence, nagrody i reset postaci | merged |
| #37 | The Ape City | merged |
| #39 | The Secret Service | merged |
| #42 | formatowanie konfiguracji | merged |
| #53 | walidacja ID, poprawne liczenie, completion-only unlock | merged |
| #113 | Yalahar, New Frontier, Wrath, testy i handoff | merged |
| #120 | aktualizacja listy pozostałych prac | merged |
| #124 | pełny production hardening | merged |

PR #124:  
`https://github.com/blakinio/canary/pull/124`

---

## 4. Wynik testów PR #124

Wszystkie końcowe testy zakończyły się sukcesem:

- Account Quests validator;
- integracja z tymczasową MariaDB;
- równoległy reward claim — dokładnie jeden zwycięzca;
- migracja quest ID;
- migracja storage i polityki konfliktów;
- izolacja między kontami;
- reset jednej postaci bez usuwania accessu konta;
- import schematu MySQL;
- Lua tests;
- clang-format;
- Stylua;
- cmake-format;
- statyczna analiza;
- yamllint;
- Linux debug;
- Linux release;
- Windows CMake;
- Windows Solution;
- macOS;
- Docker build i walidacja obrazu;
- runtime smoke tests dostępne w CI.

---

## 5. Obsługa operacyjna

### Przełącznik główny

```lua
accountWideQuestSystemEnabled = true
```

Po zmianie wymagany jest restart serwera.

### Komendy

```text
/questaccess
/questaccess Player Name
/questreset Player Name, quest-id
```

`/questaccess` jest komendą god-only i pokazuje quest ID, GUID postaci odblokowującej oraz timestamp.

### Migracje

Quest ID:

```bash
python tools/account-quests/migrate_account_quests.py quest-id --from old-id --to new-id
python tools/account-quests/migrate_account_quests.py --apply --executed-by operator quest-id --from old-id --to new-id
```

Storage:

```bash
python tools/account-quests/migrate_account_quests.py storage --from 41950 --to 51950
python tools/account-quests/migrate_account_quests.py --apply --executed-by operator storage --from 41950 --to 51950 --conflict-policy abort
```

Polityki konfliktów:

- `abort`;
- `keep-target`;
- `keep-source`;
- `max`.

Przed migracją storage należy zatrzymać serwer i wykonać backup bazy.

---

## 6. Pozostały krok poza repozytorium

Kod oraz automatyczne testy są zakończone. Pozostaje wyłącznie test wdrożeniowy na realnym lub produkcyjno-podobnym świecie:

1. postać A kończy quest i zapisuje access;
2. postać B na tym samym koncie korzysta wyłącznie z trwałego współdzielonego dostępu;
3. postać C na innym koncie nie otrzymuje dostępu;
4. `/questreset` usuwa tylko progres wskazanej postaci;
5. restart zachowuje access konta;
6. reward room i finałowa walka nadal wymagają progresu konkretnej postaci.

To jest zadanie operatora serwera — CI nie ma dostępu do zewnętrznego świata gry.

---

## 7. Granice bezpieczeństwa

Nadal per postać:

- quest log i mission storage;
- nagrody fizyczne;
- reward roomy;
- boss/fight state;
- cooldowny;
- Yalahar final fight i wybór strony;
- New Frontier Tome of Knowledge oraz reward door;
- Wrath teleport states `2/3` i zachowanie zależne od przedmiotów.

Nie wolno:

- kopiować storage ukończenia między postaciami;
- uznawać unresolved AID/UID/itemId/position za obsłużone bez dowodu;
- rozszerzać jednego access flag na wcześniejsze etapy bez audytu;
- wykonywać migracji storage bez backupu i dry-run.

---

## 8. Pliki dokumentacyjne w repozytorium

Główny handoff:

```text
docs/systems/account-wide-quests-handoff.md
```

Główne pliki systemu:

```text
data-otservbr-global/account_quests.lua
data-otservbr-global/scripts/custom/account_quest_system.lua
data/scripts/actions/doors/quest_door.lua
tools/account-quests/
data-otservbr-global/migrations/62.lua
```

---

## 9. Załączniki zachowane w sesji

Poniższe pliki były dostępne przy archiwizacji, ale **nie były analizowane w ramach account-wide quests**:

| Plik | Rozmiar | SHA-256 |
|---|---:|---|
| `pasted.txt` | 173 B | `c97af05f7c7323a3f8e9e59be06251963c3dce62d00b0128ad5ce9da6868f760` |
| `otservbr(4).otbm` | ok. 177 MiB | `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2` |
| `assets(1).zip` | ok. 398 MiB | `01c45146e2fcec3f4087844e0cbc1817fb1d60b310a35ac5d88c07aab6f73d1a` |

Nie dołączono dużego OTBM ani archiwum assets do ZIP-a z handoffem — archiwum zawiera wyłącznie dokument i manifest, aby nie duplikować ponad 575 MiB danych.

---

## 10. Instrukcja dla następnego agenta — OTBM

Jeżeli następny etap dotyczy analizy `otservbr(4).otbm`, najpierw przeczytaj:

```text
AGENTS.md
docs/ai-agent/OTBM_HD_PIPELINE.md
docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md
docs/agents/MODULE_CATALOG.md
```

Wymagania:

- użyj istniejącej infrastruktury OTBM w repozytorium;
- nie buduj parsera ani renderera od zera;
- nie używaj generatora obrazów AI do wizualizacji mapy;
- wykonaj item/mechanic audit z dokładnymi pozycjami `x,y,z`;
- rozwiązuj AID/UID/itemId/position do aktywnych Lua/XML;
- wykrywaj brakujące handlery i konflikty;
- unresolved nie może zostać uznane za handled bez dowodu;
- do wizualizacji używaj istniejącego renderera i sprite exportu.

Repozytoria referencyjne:

- `https://github.com/opentibiabr/otclient`
- `https://github.com/opentibiabr/canary`
- `https://github.com/opentibiabr/remeres-map-editor`
- `https://github.com/opentibiabr/client-editor`

---

## 11. Polecenie startowe dla następnego agenta

```text
Pracujesz w projekcie OTS i repozytorium blakinio/canary.

Najpierw przeczytaj:
- docs/systems/account-wide-quests-handoff.md
- niniejsze archiwum sesji.

Account-wide quest access dla pięciu questów jest zakończony na main.
Nie otwieraj kolejnego PR-a dla tego systemu bez nowego, konkretnego błędu lub zakresu.
Pozostał jedynie operatorski smoke test A/B/C na działającym świecie.

Jeżeli zadanie dotyczy załączonej mapy otservbr(4).otbm:
przeczytaj wymagane dokumenty OTBM, użyj istniejących narzędzi audytu,
script resolution i renderera. Nie buduj własnego parsera i nie używaj AI
do generowania obrazu mapy.
```

---

## 12. Stan archiwizacji

- prace repozytoryjne: **zakończone**;
- PR #124: **merged**;
- CI: **green**;
- dokument handoff: **na `main`**;
- nowe zadania account-wide quests: **brak**;
- oczekiwany kolejny krok: **smoke test operatora lub osobna analiza OTBM**.
