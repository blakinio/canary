# OTS AI World Validation — cel, historia, metodologia i handoff

> **Stan dokumentu:** 2026-07-12  
> **Projekt:** automatyczna i wspomagana przez AI walidacja zgodności świata OTS  
> **Repozytorium zapisywalne:** `blakinio/canary`  
> **Aktualny etap:** ręczna, evidence-based klasyfikacja nierozwiązanych mechanik mapowych  
> **Aktualny PR roboczy:** `#137`, gałąź `docs/otbm-aid-26002-review`  
> **Najważniejsza zasada:** AI ma gromadzić dowody i wykrywać niespójności, ale nie może zgadywać funkcji questa ani samodzielnie usuwać nieznanych danych z mapy.

---

## 1. Po co istnieje ten projekt

Canary, mapa OTBM, datapack, pliki świata, klient i baza danych tworzą jeden system. Każdy z tych elementów może być poprawny osobno, a mimo to całość może nie działać.

Przykładowe problemy:

- mapa zawiera `actionId`, ale żaden aktywny skrypt go nie obsługuje;
- skrypt questa oczekuje pozycji, itemu, potwora lub NPC, których nie ma w świecie;
- NPC istnieje w pliku, ale nie jest umieszczony albo nie ładuje się;
- spawn wskazuje nieistniejącego potwora;
- teleport ma błędny cel albo prowadzi na nieprzechodni kafel;
- quest ma poprawne storage, ale brakuje jednego kroku, eventu lub rejestracji;
- mapa używa itemu niewystępującego w assetach klienta;
- stary marker pozostaje na mapie, mimo że nowa implementacja działa już po pozycji;
- skrypt jest obecny w repozytorium, ale znajduje się w nieaktywnym datapacku;
- serwer uruchamia się, lecz określony quest nadal nie jest możliwy do ukończenia.

Celem projektu jest zbudowanie powtarzalnego procesu, który wykrywa takie rozbieżności i zapisuje dowody potrzebne do bezpiecznej poprawki.

Nie chodzi wyłącznie o test pliku OTBM. Docelowo jest to **walidacja całego świata gry**.

---

## 2. Co dokładnie ma być walidowane

### 2.1. Mapa OTBM

- poprawność binarnej struktury;
- możliwość odczytu przez prawdziwy loader Canary;
- kafle, itemy i ich stack order;
- `actionId`;
- `uniqueId`;
- teleport destinations;
- house-door IDs;
- towny, waypointy, houses i zones;
- zgodność ograniczonych regionów przed i po patchu.

### 2.2. Itemy i assety klienta

- występowanie itemu w `appearances.dat`;
- zgodność z `items.xml` i bazowym `ItemType`;
- dostępność wymaganych sprite’ów;
- brak przypadkowego użycia zarezerwowanych lub usuniętych ID;
- zgodność wersji assetów z analizowaną mapą.

### 2.3. Skrypty i rejestracje runtime

- `Action()`;
- `MoveEvent()`;
- legacy XML actions/movements;
- bezpośrednie i tabelaryczne rejestracje `aid`, `uid`, `id` i `position`;
- eventy `stepin`, `stepout`, `additem`, `removeitem`, `equip`, `deequip`;
- rejestracje dynamiczne, których analiza statyczna nie może bezpiecznie rozwinąć;
- mechaniki obsługiwane natywnie przez silnik.

### 2.4. Questy

Docelowo dla każdego questa powinno być możliwe sprawdzenie:

- punktu startowego;
- wymaganych NPC, potworów, itemów, pozycji i teleportów;
- storage i ich zakresów;
- kolejności misji;
- nagród;
- boss roomów i resetów;
- warunków wejścia i wyjścia;
- możliwości ukończenia pełnej ścieżki na testowej postaci.

Obecny etap nie dowodzi jeszcze pełnej przechodniości wszystkich questów. Buduje fundament danych i korelacji potrzebny do takich testów.

### 2.5. NPC

Docelowa walidacja powinna potwierdzać:

- istnienie definicji NPC;
- poprawną rejestrację i umieszczenie w świecie;
- poprawne skrypty dialogowe;
- zależności od storage, itemów i questów;
- brak odwołań do nieistniejących nazw, lokacji i funkcji;
- możliwość przejścia wymaganych gałęzi dialogowych w teście runtime.

### 2.6. Spawny i potwory

- istnienie definicji potwora;
- poprawność nazw w plikach spawnów;
- poprawność pozycji i promienia;
- zgodność bossów z questami i eventami;
- brak spawnów poza mapą albo na niewłaściwym piętrze;
- możliwość utworzenia potwora przez serwer.

### 2.7. Runtime Canary

Najwyższy poziom walidacji powinien uruchamiać prawdziwy serwer i sprawdzać:

- pełne `Map::load()` / `IOMap`;
- ładowanie companion XML;
- ładowanie NPC i spawnów;
- rejestrację eventów;
- błędy i ostrzeżenia startowe;
- wykonywanie wybranych scenariuszy questowych;
- teleporty, skrzynie, bossów, nagrody i storage;
- brak regresji po zmianie mapy lub datapacka.

---

## 3. Rola AI

AI w tym projekcie ma:

1. wykonywać deterministyczne skany narzędziami repozytorium;
2. korelować mapę z aktywnymi skryptami i danymi świata;
3. grupować anomalie według ID, pozycji, piętra, itemu i obszaru;
4. wyszukiwać aktywne oraz historyczne implementacje;
5. rozróżniać definicję, rejestrację i zwykłe odwołanie;
6. przygotowywać evidence report dla każdej decyzji;
7. proponować najmniejszą bezpieczną poprawkę;
8. generować testy regresyjne;
9. aktualizować trwały handoff, aby kolejny agent mógł kontynuować pracę.

AI nie może:

- uznać braku wyniku wyszukiwania za dowód, że mechanika jest błędna;
- zgadywać znaczenia nierozpoznanego `actionId`;
- usuwać markerów tylko dlatego, że resolver ich nie rozwiązał;
- uznać statycznej zgodności za dowód pełnej przechodniości questa;
- automatycznie rekonstruować dokładnych item stacków z minimapy;
- commitować map, assetów klienta ani dużych wygenerowanych raportów;
- modyfikować produkcyjnego datapacka bez oddzielnej, uzasadnionej zmiany i testów.

---

## 4. Warstwy walidacji

Projekt powinien rozwijać się warstwowo. Wynik wyższej warstwy nie może być udawany na podstawie niższej.

### Warstwa A — struktura plików

Pytanie: czy pliki dają się poprawnie odczytać?

Przykłady:

- parser OTBM;
- schema JSON;
- składnia Lua/XML;
- loader assetów;
- companion XML.

### Warstwa B — referencje statyczne

Pytanie: czy wszystkie odwołania mają istniejące cele?

Przykłady:

- AID/UID → handler;
- spawn → monster;
- NPC placement → NPC definition;
- quest → storage/item/position;
- item mapowy → appearance.

### Warstwa C — spójność semantyczna

Pytanie: czy powiązane elementy opisują tę samą mechanikę?

Przykłady:

- skrypt teleportu jest przypisany do właściwych pozycji;
- boss room ma wejście, wyjście, spawny i reset;
- NPC dialog używa storage tego samego questa;
- nagroda istnieje i jest możliwa do dodania graczowi.

### Warstwa D — uruchomienie świata

Pytanie: czy Canary ładuje pełny świat bez błędów krytycznych?

### Warstwa E — scenariusze gameplay

Pytanie: czy testowa postać może wykonać rzeczywisty przepływ?

Przykłady:

- rozpoczęcie misji;
- użycie obiektu;
- wejście do obszaru;
- zabicie bossa;
- odebranie nagrody;
- ukończenie questa.

### Warstwa F — regresja ciągła

Pytanie: czy każda przyszła zmiana zachowuje potwierdzone zachowanie?

Docelowo CI powinno uruchamiać szybkie testy statyczne zawsze, a cięższe testy świata i scenariusze według zakresu zmiany albo harmonogramu.

---

## 5. Aktualny zweryfikowany baseline

### 5.1. Mapa źródłowa

```text
rozmiar: 184,776,037 B
SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
kafle: 17,972,761
umieszczenia itemów: 23,359,571
unikalne item ID: 23,852
mechaniki mapowe: 9,339
```

Nazwa przesłanego pliku może zmieniać się między sesjami. To SHA-256, a nie nazwa pliku, identyfikuje baseline.

### 5.2. Resolver mechanik

```text
pliki Lua/XML: 5,384
rejestracje runtime: 1,182
reguły target/reference: 266
runtime-resolved placements: 8,964
runtime-unresolved/partial placements: 375
runtime-unresolved/partial identifiers: 151
konflikty placements: 0
```

`runtime-unresolved` nie oznacza automatycznie błędu. Identyfikator może być:

- markerem celowym;
- legacy data;
- obsługiwany po pozycji lub item ID;
- częścią dynamicznej rejestracji;
- rzeczywistym brakującym skryptem;
- nadal nierozpoznany.

### 5.3. Itemy

Pełny wcześniejszy audyt z oficjalnymi assetami klienta 15.25 wykrył jeden item bez appearance:

```text
item ID: 2141
pozycja: 33572,32528,14
liczba wystąpień: 1
```

Na kopii mapy usunięto ten pojedynczy zarezerwowany item, a natywny parser drzewa Canary poprawnie odczytał całą poprawioną kopię.

Nie należy jednak mieszać tego wyniku z bieżącą klasyfikacją mechanik. Poprawka 2141 była osobnym etapem.

---

## 6. Aktualny etap: klasyfikacja 151 identyfikatorów

Automatyczny resolver pozostawił 151 identyfikatorów wymagających interpretacji gameplay i mapy.

Dla każdego ID należy wykonać ten sam proces:

1. potwierdzić liczbę placementów;
2. wypisać pozycje, piętra i itemy;
3. pogrupować placementy przestrzennie;
4. ustalić nazwę obszaru i aktywne spawny/NPC/questy;
5. przeszukać aktywne datapacki;
6. oddzielnie sprawdzić dane historyczne i nieaktywne;
7. zidentyfikować rzeczywisty runtime key: AID, UID, item ID, pozycja albo mechanika silnika;
8. zapisać dowody przeciwko alternatywnym hipotezom;
9. nadać dyspozycję;
10. zachować mapę bez zmian, dopóki nie istnieje osobny, uzasadniony patch.

### Dyspozycje manual review

- `intentional-marker` — ID jest celowym markerem danych;
- `legacy-unused` — ID pozostał historycznie, ale runtime już go nie używa;
- `missing-script` — istnieją mocne dowody, że oczekiwana mechanika nie ma implementacji;
- `needs-manual-review` — dowody są nadal niewystarczające;
- `preserve-until-reviewed` — danych nie wolno zmieniać przed dodatkowym badaniem.

Dyspozycja manualna nie zmienia statusu runtime resolvera na `handled`. To dwa oddzielne wymiary raportu.

---

## 7. Pierwsza zakończona klasyfikacja — `actionId 26002`

### Wynik

```text
namespace: actionId
value: 26002
placementy: 71
piętro: z=8
obszar: Soul War — Ebb and Flow
itemy: rock soil 4394..4410
decyzja: legacy-unused
pewność: wysoka
zmiana mapy: brak
```

### Dowody

- nie istnieje aktywny handler czytający `actionId 26002`;
- aktywna mechanika łodzi Ebb and Flow jest rejestrowana po pozycjach;
- tabela `SoulWarQuest.ebbAndFlowBoatTeleportPositions` zawiera 173 pozycje;
- 64 z 71 placementów AID pokrywa się z aktywnymi pozycjami;
- 109 aktywnych pozycji nie ma tego AID;
- AID nie jest więc wymaganym kluczem wykonania mechaniki;
- wszystkie atrybuty mapy pozostają zachowane.

Szczegółowy raport:

```text
docs/ai-agent/OTBM_ACTIONID_26002_REVIEW.md
```

### Ważna odrzucona hipoteza

Wstępna korelacja współrzędnych sugerowała zawartość Winterlight/Percht. Spawny na właściwym piętrze i aktywne dane Soul War potwierdziły jednak Ebb and Flow. Nie należy ponownie klasyfikować `26002` wyłącznie na podstawie bliskości innych pięter.

---

## 8. Historia projektu

### Etap 1 — bezpieczna obsługa OTBM

Powstały narzędzia do:

- odczytu i zapisu OTBM;
- inspect/verify;
- eksportu regionów;
- semantycznego diffu;
- planowania i nakładania bezpiecznych patchy;
- indeksowania world XML, houses, towns, zones i waypointów;
- rejestru AID/UID;
- walidacji mapy prawdziwym loaderem Canary.

Najważniejsze PR-y: `#84`, `#85`, `#87`, `#88`, `#90`, `#91`.

### Etap 2 — assety i renderowanie

Powstały narzędzia do:

- indeksowania paczek klienta;
- parsowania `appearances.dat`;
- dekodowania sprite-sheetów;
- renderowania regionów z prawdziwych assetów;
- przygotowania zredukowanych paczek renderujących.

Najważniejsze PR-y: `#93`, `#94`, `#95`, `#96`, `#98`.

### Etap 3 — porównanie świata i audyt itemów

Wykonano:

- porównanie geometrii OTBM z TibiaMaps;
- pełny skan itemów;
- audyt appearance;
- inwentaryzację mechanik mapowych.

Najważniejsze PR-y: `#100`, `#101`.

### Etap 4 — resolver skryptów

Powstał produkcyjny resolver korelujący placementy mapowe z aktywnymi Lua/XML i mechanikami silnika.

Najważniejszy PR: `#104`, merge `0b355669ebe66c9d9c604c2a9221f47280699581`.

### Etap 5 — utrwalenie wiedzy i walidacja poprawki 2141

Powstał techniczny handoff OTBM. Zweryfikowano kopię mapy bez itemu 2141 przy użyciu natywnego parsera `src/io/fileloader.cpp`.

Najważniejsze PR-y: `#116`, `#130`, `#133`.

### Etap 6 — manual gameplay review

Rozpoczęto evidence-based analizę 151 nierozwiązanych identyfikatorów.

Pierwsza grupa: `actionId 26002`, aktualny PR `#137`.

---

## 9. Changelog tego projektu

### 2026-07-12 — utworzenie dokumentu projektu AI World Validation

- rozdzielono opis projektu walidacji świata od technicznego handoffu narzędzi OTBM;
- zapisano cel, zakres, warstwy walidacji i ograniczenia AI;
- opisano aktualny baseline mapy i resolvera;
- zapisano procedurę analizy 151 identyfikatorów;
- utrwalono decyzję `actionId 26002 = legacy-unused`;
- dodano rekomendowaną architekturę kolejnych etapów;
- dodano pełny handoff dla kolejnego agenta.

### 2026-07-12 — klasyfikacja `actionId 26002`

- ponownie potwierdzono SHA-256 mapy;
- odtworzono baseline 9,339 mechanik;
- odtworzono 8,964 resolved i 375 unresolved/partial placementów;
- zinwentaryzowano 71 placementów AID 26002;
- zidentyfikowano obszar Soul War — Ebb and Flow;
- potwierdzono pozycjny MoveEvent jako runtime path;
- nadano `legacy-unused` z wysoką pewnością;
- nie zmieniono mapy ani datapacka.

### Wcześniejsze etapy

Szczegółowa historia PR-ów narzędziowych pozostaje w:

```text
docs/ai-agent/OTS_OTBM_AGENT_HANDOFF.md
```

Ten dokument ma opisywać projekt walidacji świata, a nie zastępować techniczną dokumentację każdego parsera.

---

## 10. Co uważam za właściwy dalszy kierunek

Poniższe punkty są rekomendacją projektową, a nie potwierdzeniem już zaimplementowanych funkcji.

### 10.1. Najpierw zakończyć klasyfikację 151 ID

To najbardziej wartościowy i najmniej ryzykowny następny krok. Pozwala rozdzielić:

- martwe legacy data;
- celowe markery;
- realnie brakujące mechaniki;
- ograniczenia obecnego resolvera.

Identyfikatory należy analizować grupami należącymi do jednego obszaru lub systemu, nie wyłącznie numerycznie.

Rekomendowana następna grupa:

```text
actionId 50058..50088
```

### 10.2. Nie usuwać od razu `legacy-unused` z mapy

Klasyfikacja i czyszczenie mapy powinny być oddzielnymi etapami.

Powód:

- legacy marker może być nadal wykorzystywany przez zewnętrzne narzędzie;
- usunięcie nie daje istotnej korzyści runtime;
- mapa jest dużym binarnym artefaktem i wymaga osobnego dry-run, diffu, loader validation i rollbacku.

### 10.3. Zbudować graf zależności świata

Po klasyfikacji mechanik należy stworzyć indeks:

```text
quest
  -> storage
  -> NPC
  -> monster/boss
  -> item
  -> actionId/uniqueId
  -> position/region
  -> teleport
  -> script/event
```

Graf umożliwi wykrywanie osieroconych elementów i wybieranie pełnych scenariuszy testowych.

### 10.4. Dodać read-only audyt NPC i spawnów

Przed automatycznymi questami warto dodać szybkie, deterministyczne kontrole:

- każda nazwa NPC ze świata ma aktywną definicję;
- każda nazwa potwora w spawnach istnieje;
- pozycje są w granicach mapy;
- questowe bossy mają aktywne skrypty i miejsca utworzenia;
- duplikaty i nieaktywne datapacki są raportowane osobno.

### 10.5. Zbudować runtime smoke harness

Minimalny harness powinien:

1. uruchomić Canary z tymczasową konfiguracją i bazą;
2. załadować pełną mapę;
3. zebrać błędy NPC, spawnów, eventów i itemów;
4. utworzyć kontrolowaną testową postać;
5. wykonać kilka bezpiecznych operacji mapowych;
6. zakończyć proces i zapisać raport jako artefakt CI.

Nie należy zaczynać od automatyzacji wszystkich questów. Najpierw trzeba mieć stabilny, powtarzalny start świata.

### 10.6. Następnie dodać scenariusze questowe

Każdy scenariusz powinien jawnie deklarować:

- stan początkowy postaci;
- wymagane storage i itemy;
- pozycję początkową;
- kolejne akcje;
- oczekiwane teleporty, spawny, wiadomości i storage;
- stan końcowy;
- cleanup i powtarzalność.

Scenariusze powinny być małe i odseparowane. Nie należy budować jednego monolitycznego „testu całej Tibii”.

### 10.7. Raporty duże przechowywać jako CI artifacts

Do repozytorium powinny trafiać:

- schema;
- małe evidence reports;
- reguły klasyfikacji;
- testy;
- dokumentacja i handoff.

Nie powinny trafiać:

- `.otbm`;
- assety klienta;
- zrzuty baz;
- wielomegabajtowe surowe raporty;
- sprite-sheety i prywatne dane.

### 10.8. Każda automatyczna poprawka musi być odwracalna

Dla zmian mapy wymagane są:

- SHA-256 wejścia;
- praca na kopii;
- bounded region;
- dry-run;
- semantyczny diff;
- walidacja itemów i mechanik;
- prawdziwy loader Canary;
- rollback.

---

## 11. Kryteria ukończenia projektu

Projekt nie jest ukończony tylko dlatego, że resolver nie zgłasza konfliktów.

### Kamień milowy 1 — statyczny audyt mechanik

- [x] pełna inwentaryzacja mechanik mapowych;
- [x] korelacja z aktywnymi handlerami;
- [x] brak konfliktów placementów;
- [ ] wszystkie 151 ID ma końcową evidence-based klasyfikację.

### Kamień milowy 2 — światowe referencje

- [ ] audyt NPC;
- [ ] audyt spawnów i potworów;
- [ ] graf zależności questów;
- [ ] audyt teleportów i pozycji docelowych;
- [ ] audyt storage i nagród.

### Kamień milowy 3 — pełne ładowanie runtime

- [ ] pełne `Map::load()` / `IOMap` w kontrolowanym środowisku;
- [ ] companion XML, NPC i spawny ładują się;
- [ ] brak niezaakceptowanych błędów startowych;
- [ ] raport powtarzalny w CI.

### Kamień milowy 4 — scenariusze gameplay

- [ ] reprezentatywne questy mają testy E2E;
- [ ] boss roomy i reset mają testy;
- [ ] skrzynie, nagrody i teleporty mają testy;
- [ ] krytyczne questy przechodzą po każdej zmianie świata.

### Kamień milowy 5 — bezpieczna naprawa świata

- [ ] każdy `missing-script` ma osobny fix lub świadomą decyzję;
- [ ] każdy patch mapy ma pełny safety gate;
- [ ] potwierdzone customowe elementy pozostają zachowane;
- [ ] produkcyjna mapa jest walidowana przed wdrożeniem.

---

## 12. Źródła prawdy

### Dokument projektu

```text
docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md
```

Opisuje cel, historię, metodologię, kierunek rozwoju i awaryjny handoff.

### Techniczny handoff OTBM

```text
docs/ai-agent/OTS_OTBM_AGENT_HANDOFF.md
```

Opisuje narzędzia OTBM, historyczne artefakty, baseline i techniczne procedury.

### Resolver

```text
docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md
tools/ai-agent/otbm_script_resolution.py
tools/ai-agent/otbm_script_resolution_tool.py
```

### Reguły manual review

```text
docs/ai-agent/OTBM_SCRIPT_REVIEW_RULES.json
```

### Raport `actionId 26002`

```text
docs/ai-agent/OTBM_ACTIONID_26002_REVIEW.md
```

### Aktualne zadanie

```text
docs/agents/tasks/active/CAN-20260712-otbm-aid-26002.md
```

GitHub, aktualny `main`, otwarte PR-y i task records są ważniejsze niż pamięć rozmowy.

---

## 13. Handoff dla kolejnego agenta

Ta sekcja ma umożliwić kontynuację po utracie całego kontekstu czatu.

### 13.1. Zacznij od tego

1. Przeczytaj `AGENTS.md`.
2. Przeczytaj `docs/agents/README.md`.
3. Przeczytaj `docs/agents/ACTIVE_WORK.md`.
4. Sprawdź wszystkie otwarte PR-y; GitHub jest źródłem prawdy.
5. Przeczytaj `docs/agents/MODULE_CATALOG.md`, `REPOSITORY_MAP.md`, `KNOWN_RISKS.md` i `BUILD_TEST_MATRIX.md`.
6. Przeczytaj ten dokument.
7. Przeczytaj techniczny `OTS_OTBM_AGENT_HANDOFF.md`.
8. Przeczytaj aktualny task record i raport `OTBM_ACTIONID_26002_REVIEW.md`.
9. Sprawdź aktualny `main`; nie zakładaj, że SHA zapisane tutaj jest nadal headem.
10. Sprawdź stan PR `#137` i jego changed files/checks.

### 13.2. Bezpieczeństwo repozytorium

- jedyne repozytorium do zapisu: `blakinio/canary`;
- `opentibiabr/*` jest tylko referencją;
- nie pushuj bezpośrednio do `main`;
- nie commituj `.otbm`, `items.otb`, `appearances.dat`, assetów ani dużych raportów;
- nie modyfikuj mapy podczas klasyfikacji ID;
- nie merge’uj PR `#137` bez wyraźnej zgody użytkownika;
- przed każdym zapisem ponownie sprawdź repozytorium, branch i base.

### 13.3. Aktualny stan pracy

```text
branch: docs/otbm-aid-26002-review
PR: #137
base w momencie utworzenia: 7d8b5c1b54121f309614ecdfafbb445b00f8606b
map SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
mechanic placements: 9,339
runtime resolved: 8,964
runtime unresolved/partial: 375
unresolved identifiers: 151
conflicts: 0
```

`actionId 26002` jest zakończony jako `legacy-unused`, ale jego 71 atrybutów na mapie ma pozostać bez zmian.

Po zapisaniu tej decyzji pozostaje 150 ID z dyspozycją `needs-manual-review`.

### 13.4. Następny zalecany krok

Kontynuuj od grupy:

```text
actionId 50058..50088
```

Nie zaczynaj od implementowania fixa. Najpierw utwórz evidence report:

1. dokładne placementy;
2. itemy i piętra;
3. klastry pozycji;
4. aktywne NPC/spawny/questy w regionie;
5. wszystkie aktywne rejestracje;
6. źródła historyczne jako osobna warstwa;
7. hipotezy i dowody przeciwko nim;
8. finalna lub tymczasowa dyspozycja;
9. confidence;
10. rekomendacja: preserve, osobny fix albo dalszy review.

### 13.5. Mapa i pliki lokalne

Nowa sesja może nie mieć mapy w `/mnt/data`.

Wtedy:

- poproś użytkownika o ponowne przesłanie mapy;
- oblicz SHA-256;
- kontynuuj tylko wtedy, gdy wynosi:

```text
a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
```

Nazwa pliku może być inna, np. `otservbr(2).otbm` albo `otservbr(3).otbm`.

Nie zakładaj dostępności wcześniejszych artefaktów `/mnt/data`.

### 13.6. Ważna uwaga o assetach

Oficjalny wcześniejszy pełny item audit używał klienta 15.25 i 42,107 appearance objects.

W sesji klasyfikacji 26002 oryginalny `appearances.dat` nie był dostępny. Mechanic scan był dokładny i niezależny od appearance, natomiast surrogate appearance służył wyłącznie do odtworzenia struktury wejściowej resolvera.

Nie przedstawiaj surrogate jako pełnego, ponownego audytu zgodności itemów z oficjalnym klientem.

### 13.7. Minimalne komendy kontrolne

```bash
python tools/ai-agent/otbm_item_audit_tool.py --help
python tools/ai-agent/otbm_script_resolution_tool.py --help
python -m unittest tools/ai-agent/test_otbm_script_resolution.py -v
python -m unittest discover -s tools/ai-agent -p 'test_*.py' -v
```

Przykład resolvera:

```bash
python tools/ai-agent/otbm_script_resolution_tool.py \
  artifacts/OTBM_ITEM_AUDIT.json \
  --repository-root . \
  --script-root data \
  --script-root data-otservbr-global \
  --review-rules docs/ai-agent/OTBM_SCRIPT_REVIEW_RULES.json \
  --output artifacts/OTBM_SCRIPT_RESOLUTION.json
```

`--strict-runtime` ma pozostać czerwony, dopóki istnieją runtime-unresolved identyfikatory. Manual disposition nie może udawać runtime handlera.

### 13.8. Czego nie powtarzać

- nie identyfikuj 26002 jako Winterlight tylko z powodu bliskości współrzędnych;
- nie twórz nowego parsera OTBM — użyj istniejącego narzędzia;
- nie mieszaj `data-canary` z aktywnymi datapackami bez jawnego powodu;
- nie uznawaj braku tekstowego matcha za dowód `missing-script`;
- nie usuwaj AID z mapy;
- nie zaczynaj automatycznej rekonstrukcji całego świata;
- nie commituj wygenerowanych map ani assetów.

### 13.9. Obowiązki aktualizacyjne

Po każdym zakończonym ID lub grupie:

1. dodaj mały evidence report w `docs/ai-agent/`;
2. zaktualizuj `OTBM_SCRIPT_REVIEW_RULES.json`;
3. zaktualizuj ten changelog;
4. zaktualizuj techniczny handoff tylko wtedy, gdy zmienia się baseline lub istotny stan narzędzi;
5. zaktualizuj aktywny task record;
6. uruchom testy;
7. sprawdź pełny changed-file list i diff;
8. nie merge’uj bez spełnienia bieżących zasad repozytorium i instrukcji użytkownika.

### 13.10. Otwarta decyzja techniczna

Obecny resolver nie rozwija wszystkich statycznych tabel zdefiniowanych w innych plikach, np. pozycyjnej tabeli Soul War użytej przy 26002.

Możliwy osobny przyszły PR może dodać bezpieczną obsługę wybranych cross-file static tables, ale:

- musi mieć deterministyczne ograniczenia;
- musi odróżniać rejestrację od zwykłego odwołania;
- musi mieć focused regression tests;
- nie powinien być mieszany z PR-em dokumentującym klasyfikację gameplay.

---

## 14. Krótkie podsumowanie dla człowieka

Projekt ma odpowiedzieć na pytanie:

> Czy mapa, questy, NPC, spawny, itemy, teleporty, skrypty i serwer Canary tworzą jeden zgodny, działający świat?

Aktualnie potrafimy już bardzo dokładnie sprawdzać strukturę mapy, itemy i większość powiązań mechanik ze skryptami. Nie mamy jeszcze pełnego automatycznego testera przechodzącego wszystkie questy jak gracz.

Najrozsądniejszy plan to:

1. zakończyć klasyfikację 151 ID;
2. dodać audyt NPC i spawnów;
3. zbudować graf zależności questów;
4. uruchamiać pełny świat w kontrolowanym runtime;
5. dodawać małe scenariusze E2E dla najważniejszych questów;
6. dopiero na podstawie tych dowodów naprawiać mapę lub datapack.

To podejście maksymalizuje wykrywalność błędów i minimalizuje ryzyko uszkodzenia customowego świata.