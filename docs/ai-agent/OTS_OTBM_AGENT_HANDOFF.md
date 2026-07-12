# OTS / Canary — handoff projektu OTBM, TibiaMaps, assetów i audytu mechaniki

> **Stan dokumentu:** 2026-07-12 (aktualizowany na bieżąco)  
> **Przeznaczenie:** dokument przekazania pracy kolejnemu agentowi lub zespołowi agentów.  
> **Repozytorium zapisu:** `blakinio/canary`  
> **Bieżący aktywny PR:** `#104 feat(ai-agent): resolve OTBM script handlers`  
> **Ważne:** PR #104 **nie jest gotowy do merge** w aktualnej postaci.

---

## 1. Cel projektu

Celem jest zbudowanie bezpiecznego, powtarzalnego procesu, który pozwala:

1. analizować bardzo duże mapy OTBM bez ładowania całej mapy do pamięci;
2. porównywać istniejącą mapę serwera z aktualnymi danymi TibiaMaps;
3. wykrywać brakujące regiony, różnice przechodniości i obszary customowe;
4. sprawdzać zgodność wszystkich itemów z nowoczesnym `appearances.dat`, sprite’ami klienta i `items.xml`;
5. zachować mechanikę mapy: `actionId`, `uniqueId`, teleporty, drzwi domów, kontenery, questy i skrypty;
6. rekonstruować brakujące regiony etapami, jako odwracalne patche, bez nadpisywania mapy bazowej;
7. walidować każdy patch przez narzędzia OTBM, prawdziwy loader Canary, render sprite’ów i pełne CI.

### Cel końcowy

Docelowo powinna powstać zwalidowana mapa wynikowa oparta na `otservbr(2).otbm`, uzupełniona o wybrane brakujące obszary zgodne z najnowszą referencją, bez utraty customowej zawartości i bez uszkodzenia questów, teleportów, domów, spawnów lub skryptów.

---

## 2. Czego nie wolno robić

- Nie nadpisywać źródłowego `otservbr(2).otbm`.
- Nie pushować bezpośrednio do `main`.
- Nie merge’ować PR bez pełnego zielonego CI.
- Nie commitować OTBM, sprite-sheetów, `appearances.dat`, pełnych assetów klienta ani danych TibiaMaps.
- Nie traktować koloru minimapy jako informacji o dokładnym stacku itemów.
- Nie tworzyć „renderów” mapy przez generator obrazów. Render ma pochodzić z OTBM + prawdziwych assetów.
- Nie usuwać `actionId`/`uniqueId` tylko dlatego, że aktualny resolver nie znalazł handlera.
- Nie kopiować nowych regionów „w ciemno”.
- Nie usuwać pól OTBM-only: mogą być customowe, ukryte, techniczne albo starsze.
- Nie zgadywać zamiennika dla nieznanego item ID bez analizy lokalizacji i kontekstu.

---

## 3. Repozytoria

### Repozytorium robocze

- `https://github.com/blakinio/canary`
- Tylko tutaj wykonywać zmiany.
- Każda zmiana: osobna gałąź → PR → CI → squash merge.

### Repozytoria referencyjne

- `https://github.com/opentibiabr/canary`
- `https://github.com/opentibiabr/otclient`
- `https://github.com/opentibiabr/remeres-map-editor`
- `https://github.com/opentibiabr/client-editor`

Repozytoria referencyjne służą do porównywania formatów, zachowania loadera, assetów i edytora. Nie należy w nich wykonywać zmian w ramach tego projektu.

---

## 4. Dostępne dane wejściowe

### Mapa bazowa

- Plik: `otservbr(2).otbm`
- Rozmiar: `184,776,037` B
- SHA-256: `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`
- Lokalna ścieżka w obecnym środowisku: `/mnt/data/otservbr(2).otbm`

### Assety oficjalnego klienta

- Archiwum: `assets.zip`
- Wersja klienta: `15.25.bd5a04`
- Liczba appearance objects: `42,107`
- Zawiera `package.json`, `catalog-content.json`, `appearances.dat`, sprite-sheety CIP/LZMA i minimapy.
- Lokalna ścieżka: `/mnt/data/assets.zip`
- Nie commitować do GitHuba.

### Referencja TibiaMaps

- Referencja: najnowszy zestaw 16 pięter.
- Początek świata: `[31744, 30976]`
- Rozmiar jednego piętra: `2560 × 2048`
- Zakres współrzędnych: `31744..34303 × 30976..33023`
- Każdy piksel odpowiada jednemu polu świata.
- Referencja zawiera geometrię/minimapę/pathfinding, ale nie dokładne stacki itemów ani skrypty.

> Nowa sesja lub inny agent może nie mieć plików z `/mnt/data`. Wtedy należy poprosić o ponowne udostępnienie OTBM i assetów albo pobrać wcześniej utworzone artefakty workflow, jeżeli jeszcze nie wygasły.

---

## 5. Najważniejsze wyniki analizy

### 5.1 Pokrycie najnowszej referencji

- Pola referencyjne: `11,434,263`
- Pola OTBM w analizowanym zakresie: `17,887,095`
- Wspólne pola: `10,560,778`
- Pokrycie najnowszej referencji: `92.36%`
- Pola obecne tylko w najnowszej referencji: `873,485`
- Z nich przechodnie: `210,148`
- Pola obecne tylko w OTBM: `7,326,317`

Interpretacja:

- `latest-only` to kandydaci do rekonstrukcji, nie gotowe patche;
- `OTBM-only` nie są automatycznie błędem;
- porównanie jest strukturalne, nie odtwarza dokładnych itemów.

### 5.2 Audyt itemów

Zweryfikowany przebieg na całej mapie:

- kafle: `17,972,761`;
- wszystkie umieszczenia itemów: `23,359,571`;
- unikalne item ID: `23,852`;
- umieszczenia z mechaniką mapową: `9,339`;
- nieznane lub ucięte atrybuty: `0`;
- brak appearance klienta 15.25: tylko item ID `2141`, użyty jeden raz.

### 5.3 Audyt handlerów skryptowych

Aktualny lokalny raport resolvera:

- pliki przeskanowane: `5,272`;
- wykryte rejestracje: `964`;
- mechaniki mapowe: `9,339`;
- rozwiązane umieszczenia: `8,963`;
- nierozwiązane umieszczenia: `376`;
- konflikty umieszczeń: `0`;
- status `unresolved`: `150` identyfikatorów;
- status `partially-resolved`: `1` identyfikator;
- nierozwiązane dynamiczne rejestracje parsera: `242`.

Aktualne klasyfikacje obejmują:

- `handled-directly`
- `handled-by-range`
- `handled-generically`
- `handled-by-item-id`
- `handled-as-target`
- `handled-by-fallback`
- `handled-by-engine`
- `handled-multiple`
- `partially-resolved`
- `unresolved`

### Największe znane grupy do dalszej analizy

- `actionId 26002`
- zakres `50058..50088`
- zakres `48000..48006`
- zakres `2090..2096`
- `uniqueId 62133`
- `uniqueId 62135`
- pojedyncze starsze ID, m.in. `1500`, `3000`, `13004`, `24867`
- wcześniej wykryte `actionId 8026` na itemach `10735/10736/10737/10740`

Nie wolno uznać ich automatycznie za błędne. Część może być markerami mapy, mechaniką silnika, pozostałością starszego datapacka albo brakującym skryptem.

---

## 6. Znany problem itemu 2141

### Lokalizacja

- pozycja: `33572, 32528, 14`
- liczba wystąpień: `1`
- brak `actionId`
- brak `uniqueId`
- brak teleport destination
- brak house-door ID

### Obecny stan

Istnieje poprawny dry-run operacji `remove_item`:

- raport: `/mnt/data/REMOVE_RESERVED_ITEM_2141.report.json`
- operacja dotyczy dokładnie jednego wpisu;
- walidacja patcha: `ok = true`;
- źródłowy OTBM nie został jeszcze zmodyfikowany;
- planowany plik wynikowy: `/mnt/data/otservbr-fixed-reserved-item.otbm`.

### Co należy zrobić

1. wykonać prawdziwy patch do nowego pliku;
2. nie zmieniać pliku źródłowego;
3. uruchomić `inspect` i `verify`;
4. wczytać wynik przez prawdziwy loader C++ Canary;
5. potwierdzić brak zmian poza pozycją `33572,32528,14`;
6. ponownie uruchomić audyt itemów;
7. potwierdzić `missingAppearanceIds = 0`;
8. dopiero potem uznać problem za zamknięty.

---

## 7. Changelog wykonanych prac

### Fundament OTBM

- **PR #84** — parser/writer OTBM, inspect, verify, export, diff, apply.
- **PR #85** — katalog `items.xml` i semantyczna walidacja patchy.
- **PR #87** — indeks świata, towns, waypoints, houses, zones i companion spawn XML.
- **PR #88** — skaner rejestru `actionId`/`uniqueId`.
- **PR #90** — bezpieczne authoring companion XML.
- **PR #91** — test ładowania wygenerowanego OTBM przez prawdziwy loader C++ Canary.

### Assety i render

- **PR #93** — indeks paczek assetów OTClient/RME.
- **PR #94** — parser protobuf `appearances.dat`.
- **PR #95** — dekoder CIP/raw-LZMA sprite-sheetów.
- **PR #96** — deterministyczny renderer regionów OTBM do PNG.
- **PR #98** — poprawna obsługa realnych nagłówków CIP i zredukowanych paczek renderujących.

### Porównanie i audyt mapy

- **PR #100**, merge commit `a730508243d70e6828e53b35ee863ae7c3b91ee5`  
  Porównanie OTBM z TibiaMaps, szybki skaner zajętości, komponenty brakujących regionów, pathfinding i mapy różnic.

- **PR #101**, merge commit `a911ecb09a6b282a439df5283cb814a41548628c`  
  Audyt wszystkich itemów, atrybutów, `actionId`, `uniqueId`, teleportów i drzwi domów.

### PR-y operacyjne, których nie merge’owano

- **PR #97** — tymczasowy eksport assetów klienta 15.11; zamknięty bez merge.
- **PR #99** — tymczasowe pobieranie pełnych danych TibiaMaps; zamknięty bez merge.

---


### Dokumentacja handoff

- Docelowa ścieżka w repozytorium: `docs/ai-agent/OTS_OTBM_AGENT_HANDOFF.md`.
- Ten plik ma być aktualizowany po każdym większym etapie: nowy PR, merge, zmiana wyników audytu, zamknięcie itemu `2141`, rozpoczęcie rekonstrukcji regionu.
- Zmiany dokumentacji również powinny przechodzić przez osobny PR lub być częścią właściwego PR funkcjonalnego.


## 8. Bieżący stan PR #104

PR:

- numer: `#104`
- tytuł: `feat(ai-agent): resolve OTBM script handlers`
- gałąź: `feat/otbm-script-resolution-audit`
- stan: `open`
- GitHub obecnie pokazuje `draft = false`, mimo że treść PR mówi o fazie draft/discovery;
- head SHA: `f393717500d6e4fda691ab96cb546dac6fe1846a`;
- aktualny `main` podczas ostatniej aktualizacji dokumentu: `209289d38e64aafe7ce3e036867bb632cd0363b8`;
- gałąź: `5` commitów do przodu i `6` commitów za `main`;
- zmienione są tylko dwa pliki tymczasowe:
  - `.github/script-audit-discovery/discover.py`
  - `.github/workflows/script-registration-discovery.yml`

### Krytyczne ostrzeżenie

**Nie merge’ować PR #104 w obecnej postaci.**

PR nie zawiera jeszcze finalnego resolvera, CLI, schematu, dokumentacji ani testów. Zawiera wyłącznie tymczasowy mechanizm discovery i musi zostać oczyszczony.

---

## 9. Co dokładnie zostało do zrobienia

### Priorytet P0 — finalny resolver handlerów

Należy dodać do repo produkcyjne narzędzie rozstrzygające, czy każde `actionId`/`uniqueId` z OTBM ma obsługę.

#### Minimalne wymagania parsera

1. skanować tylko aktywne datapacki:
   - `data`
   - `data-otservbr-global`
   - nie mieszać automatycznie `data-canary`, jeżeli nie jest aktywnym datapackiem danego uruchomienia;
2. rozpoznawać:
   - `Action()`
   - `MoveEvent()`
   - bezpośrednie `:aid(...)`
   - bezpośrednie `:uid(...)`
   - zakresy `from..to`
   - pętle numeryczne
   - `pairs()` i `ipairs()` po stałych tabelach
   - rejestracje przez `:id(...)`
   - `target.actionid`, `target.uid`, `item.actionid`, `item.uid`
   - starsze rejestracje XML;
3. rozróżniać typy MoveEvent:
   - step-in
   - step-out
   - add-item
   - remove-item
   - equip
   - de-equip;
4. uwzględniać mechaniki silnika:
   - teleport destination;
   - house-door ID;
   - mechanikę quest chest `actionId 2000`;
5. zachowywać:
   - plik;
   - numer linii;
   - typ rejestracji;
   - namespace;
   - zakres;
   - event type;
   - poziom pewności;
6. wykrywać konflikty tylko wtedy, gdy rejestracje faktycznie konkurują dla tego samego event type;
7. nie oznaczać jako konflikt prawidłowych par `stepin/stepout`.

#### Sugerowane pliki

Nazwy mogą zostać dostosowane, ale spójny układ to:

```text
tools/ai-agent/otbm_script_resolution.py
tools/ai-agent/otbm_script_resolution_tool.py
tools/ai-agent/test_otbm_script_resolution.py
docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md
docs/ai-agent/OTBM_SCRIPT_RESOLUTION_REPORT.schema.json
```

#### Testy obowiązkowe

- bezpośredni `aid`;
- bezpośredni `uid`;
- zakres ID;
- pętla numeryczna;
- tabela `pairs/ipairs`;
- `target.actionid`;
- `target.uid`;
- XML action/moveevent;
- MoveEvent `stepin` i `stepout` dla tego samego ID bez fałszywego konfliktu;
- actionId `2000` jako obsługa generyczna;
- teleport i house-door jako mechanika silnika;
- częściowo rozwiązany identyfikator;
- prawdziwy konflikt;
- nierozwiązana dynamiczna rejestracja z jawnym ostrzeżeniem.

### Priorytet P0 — klasyfikacja ostatnich ID

Dla wszystkich bieżących `150 unresolved + 1 partially-resolved`:

1. pogrupować po ID, item ID, pozycji, piętrze i sąsiednich polach;
2. sprawdzić aktywne skrypty;
3. sprawdzić starsze/upstreamowe datapacki tylko jako referencję;
4. nadać jedną z decyzji:
   - `handled`
   - `engine-handled`
   - `intentional-marker`
   - `legacy-unused`
   - `missing-script`
   - `needs-manual-review`;
5. nie pisać brakujących skryptów bez ustalenia funkcji obszaru;
6. dla `missing-script` utworzyć osobny issue/raport z pozycjami i kontekstem.

### Priorytet P0 — oczyszczenie i domknięcie PR #104

1. zaktualizować gałąź do aktualnego `main`;
2. usunąć oba pliki discovery;
3. dodać wyłącznie finalny resolver, CLI, testy, schemat i dokumentację;
4. zaktualizować opis PR;
5. sprawdzić changed-files;
6. uruchomić:
   - OTBM Map Tools;
   - AI Agent Tools;
   - ogólne CI;
7. merge tylko przy wszystkich zielonych workflow;
8. squash merge z blokadą na sprawdzony head SHA.

### Priorytet P1 — zamknięcie itemu 2141

Wykonać kroki z sekcji 6. Najlepiej osobny PR dotyczący narzędzia/testu albo artefakt mapy lokalny. Nie commitować OTBM.

### Priorytet P1 — raport końcowy mechaniki

Po merge resolvera wygenerować aktualny raport zawierający:

- wszystkie ID;
- status;
- handler;
- źródło i linie;
- pozycje OTBM;
- konflikty;
- dynamiczne nierozstrzygnięte rejestracje;
- listę rzeczywistych braków.

Docelowe kryterium:

- `conflictingPlacements = 0`;
- wszystkie nierozwiązane ID mają ręcznie zatwierdzoną klasyfikację;
- żadna niejasność nie jest ukryta jako „handled”.

### Priorytet P2 — rekonstrukcja brakujących regionów

Dopiero po zakończeniu audytu mechaniki:

1. posortować komponenty `latest-only` według:
   - liczby przechodnich pól;
   - wielkości komponentu;
   - ciągłości z istniejącą mapą;
   - ryzyka mechaniki;
2. wybrać mały pilotowy region;
3. nie rekonstruować od razu całego świata;
4. przygotować patch OTBM bez nadpisywania źródła;
5. dodać itemy wyłącznie na podstawie wiarygodnego źródła;
6. dodać/zweryfikować:
   - town;
   - house;
   - zone;
   - spawn;
   - NPC;
   - teleport;
   - quest;
   - action/unique IDs;
7. uruchomić:
   - inspect;
   - verify;
   - diff;
   - audyt itemów;
   - resolver skryptów;
   - loader C++ Canary;
   - render regionu przed/po;
8. zachować raport i możliwość cofnięcia patcha.

---

## 10. Definicja ukończenia bieżącego etapu

Etap „audyt mapy i mechaniki” jest skończony dopiero, gdy:

- [ ] PR #104 nie zawiera plików discovery;
- [ ] finalny resolver jest w repo;
- [ ] resolver ma testy i schemat raportu;
- [ ] gałąź jest aktualna z `main`;
- [ ] wszystkie workflow są zielone;
- [ ] PR #104 jest zmergowany;
- [ ] wszystkie nierozwiązane ID mają klasyfikację;
- [ ] item `2141` został usunięty w kopii mapy lub świadomie odroczony z uzasadnieniem;
- [ ] mapa po poprawce przechodzi loader Canary;
- [ ] nowy audyt nie wykazuje brakującego appearance;
- [ ] powstało końcowe podsumowanie dla użytkownika.

Etap „aktualizacja świata do najnowszej mapy” jest osobnym, późniejszym etapem i nie jest jeszcze rozpoczęty produkcyjnie.

---

## 11. Walidacja i zasady PR

Każdy PR:

1. musi pochodzić z osobnej gałęzi;
2. nie może zawierać map ani assetów;
3. musi mieć testy syntetyczne;
4. musi mieć schemat JSON dla raportu;
5. musi mieć dokumentację CLI;
6. musi przejść wszystkie workflow;
7. musi mieć końcowy przegląd changed-files;
8. może być zmergowany tylko po sprawdzeniu dokładnego head SHA.

Po merge należy ponownie sprawdzić `main` i zapisać merge commit w changelogu.

---

## 12. Istniejące narzędzia, z których należy korzystać

W `tools/ai-agent` istnieją już narzędzia dla:

- parsera/writera OTBM;
- patch/diff/apply;
- katalogu `items.xml`;
- indeksu świata;
- companion XML;
- actionId/uniqueId registry;
- asset package index;
- appearances index;
- sprite-sheet decode;
- renderowania regionów;
- porównania OTBM z TibiaMaps;
- pełnego audytu itemów.

Nie tworzyć drugi raz tej samej funkcji. Rozszerzać istniejące moduły albo korzystać z ich raportów.

### Przykładowe istniejące punkty wejścia

```text
tools/ai-agent/otbm_reference_tool.py
tools/ai-agent/otbm_item_audit_tool.py
tools/ai-agent/otbm_appearances_tool.py
```

Dokładne opcje zawsze sprawdzić przez `--help` w aktualnym `main`.

---

## 13. Artefakty bieżącej sesji

- `otservbr(2).otbm` — 184,776,037 B — SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2` — `/mnt/data/otservbr(2).otbm`
- `assets.zip` — 416,822,274 B — SHA-256 `01c45146e2fcec3f4087844e0cbc1817fb1d60b310a35ac5d88c07aab6f73d1a` — `/mnt/data/assets.zip`
- `OTBM_LATEST_AUDIT.md` — 5,965 B — SHA-256 `7416e0ef1913097bf8178e040a2cdd189678b685393de130434c127b5b0d91cc` — `/mnt/data/OTBM_LATEST_AUDIT.md`
- `OTBM_LATEST_AUDIT.json` — 724,531 B — SHA-256 `01770673246e217c8de31134cd1137bd995f056b8a4536eab28a48b2c8eeeb60` — `/mnt/data/OTBM_LATEST_AUDIT.json`
- `OTBM_LATEST_DIFF_OVERVIEW.png` — 241,986 B — SHA-256 `53026fc0b32914a3515f7e131a6061013c814a84565ad62b44f852197a8c2def` — `/mnt/data/OTBM_LATEST_DIFF_OVERVIEW.png`
- `OTBM_SCRIPT_AUDIT.json` — 32,677,764 B — SHA-256 `3d1193649c8a5cb2aa8ba822ddae9328557a0c7a8de0880ff688d40c05153fd6` — `/mnt/data/OTBM_SCRIPT_AUDIT.json`
- `REMOVE_RESERVED_ITEM_2141.report.json` — 911 B — SHA-256 `ce5570f146c0c3f14ab019321b2505511b97e76a2871ea4e55d6a4eb16294751` — `/mnt/data/REMOVE_RESERVED_ITEM_2141.report.json`
- `thais-15.25.png` — 1,335,594 B — SHA-256 `1ccf9f1c22811b9801241d128ce1a33d54b868ed83319851500a099afe0848fd` — `/mnt/data/thais-15.25.png`
- `thais-15.25-render.json` — 6,264 B — SHA-256 `032f008d1e803fb7680b790c2148625912ffae03a7a6fd6718af6dd84aac2f39` — `/mnt/data/thais-15.25-render.json`

### Najważniejsze pliki

- `OTBM_LATEST_AUDIT.md` — czytelne podsumowanie pokrycia świata;
- `OTBM_LATEST_AUDIT.json` — pełny raport maszynowy;
- `OTBM_LATEST_DIFF_OVERVIEW.png` — mapa różnic wszystkich pięter;
- `OTBM_SCRIPT_AUDIT.json` — aktualny raport resolvera;
- `REMOVE_RESERVED_ITEM_2141.report.json` — dry-run bezpiecznej operacji;
- `thais-15.25.png` — prawdziwy render testowy OTBM z assetami 15.25;
- `thais-15.25-render.json` — raport renderu.

---

## 14. Ograniczenia danych

TibiaMaps/minimapa pozwala wiarygodnie ustalić:

- współrzędne;
- poziom `z`;
- obecność terenu;
- kolor minimapy;
- przybliżoną przechodniość/pathfinding;
- granice i ciągłość obszarów.

Nie pozwala ustalić:

- dokładnych item ID;
- kolejności stacku;
- dekoracji;
- teleport destinations;
- `actionId`;
- `uniqueId`;
- town/house/zone;
- spawnów;
- NPC;
- skryptów;
- questów;
- wymagań poziomowych;
- mechaniki drzwi;
- fabuły.

Dlatego automatyczna zamiana minimapy na gotowy OTBM nie jest bezpiecznym rozwiązaniem.

---

## 15. Decyzje projektowe

1. **Najnowsza TibiaMaps jest referencją docelowej geometrii**, ale nie źródłem kompletnego OTBM.
2. **Obecny OTBM pozostaje bazą i nie jest nadpisywany.**
3. **Każdy region jest osobnym patchem.**
4. **Assety klienta są używane lokalnie i nie są publikowane w repo.**
5. **Render jest deterministyczny i pochodzi z danych gry, nie z AI graficznego.**
6. **Brak wpisu w `items.xml` nie oznacza automatycznie braku obsługi**, ponieważ Canary buduje bazowy ItemType z appearances.
7. **Nierozwiązany ID nie jest automatycznie błędem mapy.**
8. **Mechanika jest ważniejsza niż wizualna zgodność.**
9. **Pełny merge dopiero po loaderze Canary i zielonym CI.**

---

## 16. Zalecana kolejność pracy następnego agenta

1. Przeczytać ten dokument.
2. Sprawdzić aktualny `main`.
3. Sprawdzić PR #104 i jego changed-files.
4. Nie merge’ować discovery.
5. Przywrócić lub ponownie wygenerować lokalny `OTBM_SCRIPT_AUDIT.json`.
6. Zaimplementować finalny resolver.
7. Dodać testy i schema.
8. Oczyścić PR #104.
9. Zaktualizować gałąź do `main`.
10. Uruchomić CI.
11. Zmergować PR #104 dopiero na zielono.
12. Zamknąć item `2141`.
13. Wygenerować finalny raport mechaniki.
14. Dopiero później rozpocząć pilotową rekonstrukcję jednego regionu.

---

## 17. Krótkie podsumowanie dla agenta

Nie zaczynaj od budowania nowych obszarów. Najpierw domknij resolver i audyt mechaniki. Obecne narzędzia dobrze wykrywają geometrię i itemy, ale ostatnia warstwa bezpieczeństwa — pewne powiązanie `actionId`/`uniqueId` z aktywnymi handlerami — nie jest jeszcze zmergowana. PR #104 jest tylko szkieletem discovery i wymaga zastąpienia produkcyjną implementacją. Następnie należy bezpiecznie usunąć pojedynczy niezgodny item `2141` w kopii mapy i zweryfikować wynik prawdziwym loaderem Canary. Dopiero wtedy można zacząć rekonstruować najnowsze regiony.
