# OTS / Canary — handoff projektu OTBM, TibiaMaps, assetów i audytu mechaniki

> **Stan dokumentu:** 2026-07-12, aktualizowany na bieżąco  
> **Repozytorium zapisu:** `blakinio/canary`  
> **Aktywny draft PR:** [#128 feat(ai-agent): resolve OTBM script handlers](https://github.com/blakinio/canary/pull/128)  
> **Gałąź:** `feat/otbm-script-resolution-20260712`  
> **Baza PR podczas utworzenia:** `5ec66ee6501c799fcb6186b477c39206176db9d2`  
> **Commit z resolverem przed aktualizacją handoffu:** `18fe5ee32428dc93e5dd140dfee905b91516fea6`

---

## 1. Cel projektu

Celem jest bezpieczny, powtarzalny proces, który pozwala:

1. analizować bardzo duże mapy OTBM bez ładowania całego świata do pamięci;
2. porównywać mapę serwera z TibiaMaps i innymi wersjonowanymi referencjami;
3. wykrywać brakujące regiony, różnice przechodniości i obszary customowe;
4. sprawdzać zgodność itemów z `appearances.dat`, assetami klienta i `items.xml`;
5. zachować mechanikę mapy: `actionId`, `uniqueId`, teleporty, domy, kontenery, questy i skrypty;
6. przygotowywać odwracalne, przypięte hashem patche bez nadpisywania mapy źródłowej;
7. walidować każdy patch przez parser OTBM, prawdziwy loader Canary, audyty i CI.

### Cel końcowy

Powinna powstać zwalidowana mapa wynikowa oparta na dostarczonym OTBM, uzupełniana etapami o wybrane brakujące obszary bez utraty customowej zawartości oraz bez uszkodzenia questów, teleportów, domów, spawnów i skryptów.

---

## 2. Zasady bezwzględne

- Nie nadpisywać źródłowego OTBM.
- Nie commitować `.otbm`, `items.otb`, `appearances.dat`, sprite-sheetów, assetów klienta ani pełnych danych TibiaMaps.
- Nie pushować bezpośrednio do `main`.
- Nie merge’ować PR bez sprawdzenia zmienionych plików i zielonego CI.
- Nie usuwać `actionId` lub `uniqueId` tylko dlatego, że statyczny resolver nie znalazł handlera.
- Nie traktować pól OTBM-only jako automatycznego błędu.
- Nie zgadywać brakujących itemów, potworów, NPC ani funkcji obszaru.
- Nie rekonstruować dużych regionów przed zakończeniem audytu mechaniki.
- Każdy patch mapy musi mieć hash źródła, dry-run, diff, walidację i możliwość cofnięcia.

---

## 3. Repozytoria

### Zapisywalne

- `https://github.com/blakinio/canary`

### Referencyjne, tylko do odczytu

- `https://github.com/opentibiabr/canary`
- `https://github.com/opentibiabr/otclient`
- `https://github.com/opentibiabr/remeres-map-editor`
- `https://github.com/opentibiabr/client-editor`

---

## 4. Dane wejściowe i ich pochodzenie

### Mapa bazowa

```text
nazwa lokalna: /mnt/data/otservbr.otbm
rozmiar: 184,776,037 B
SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
format: OTBM v4
rozmiar świata: 35143 × 34812
edytor zapisujący: Canary Map Editor 4.0.0
```

Pełny odczyt struktury:

```text
kafle: 17,972,761
umieszczenia itemów: 23,359,571
unikalne item ID: 23,852
mechaniki mapowe: 9,339
miasta: 30
domy: 993
teleporty: 2,342
```

Mapa nie została dodana do GitHuba. Nowa sesja może nie mieć pliku w `/mnt/data`; wtedy trzeba poprosić użytkownika o ponowne przesłanie i zweryfikować SHA-256.

### Assety klienta

Poprzednia sesja korzystała z paczki klienta `15.25.bd5a04` z 42,107 appearance objects. Assety nie są częścią repozytorium i mogą nie być dostępne w nowej sesji.

### Snapshot użyty w bieżącym audycie resolvera

Pełny audyt mapy wykonano na zachowanym snapshotcie źródeł z wcześniejszego workflow, head:

```text
f393717500d6e4fda691ab96cb546dac6fe1846a
```

To ważne ograniczenie: wynik potwierdza działanie resolvera na realnym datapacku, ale **nie jest jeszcze finalnym baseline’em dokładnego checkoutu PR #128**. Następny agent musi uruchomić raport ponownie po pobraniu gałęzi PR.

---

## 5. Historia narzędzi OTBM

### Fundament mapy

- PR #84 — parser/writer OTBM, inspect, verify, export, diff i apply.
- PR #85 — katalog `items.xml` i semantyczna walidacja patchy.
- PR #87 — indeks świata, town, waypoint, house, zone i companion XML.
- PR #88 — skaner `actionId`/`uniqueId` z mapy.
- PR #90 — bezpieczne patche companion XML.
- PR #91 — ładowanie wygenerowanego OTBM przez prawdziwy loader C++ Canary.

### Assety i render

- PR #93 — indeks paczek assetów OTClient/RME.
- PR #94 — parser protobuf `appearances.dat`.
- PR #95 — dekoder CIP/raw-LZMA sprite-sheetów.
- PR #96 — deterministyczny renderer regionów OTBM.
- PR #98 — poprawiona obsługa realnych nagłówków CIP i zredukowanych paczek.

### Porównanie mapy i audyt itemów

- PR #100 — porównanie OTBM z TibiaMaps oraz komponenty brakujących regionów.
- PR #101 — pełny audyt itemów i mechanik mapowych.

### Stary PR #104

- `#104 feat(ai-agent): resolve OTBM script handlers`
- zamknięty bez merge;
- końcowo miał 0 commitów i 0 zmienionych plików;
- tymczasowe pliki discovery nie zostały scalone;
- został zastąpiony przez czysty draft PR #128.

---

## 6. Nowy resolver — PR #128

### Pliki

```text
tools/ai-agent/otbm_script_resolution_parser.py
tools/ai-agent/otbm_script_resolution_scan.py
tools/ai-agent/otbm_script_resolution.py
tools/ai-agent/otbm_script_resolution_tool.py
tools/ai-agent/test_otbm_script_resolution.py
docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md
docs/ai-agent/OTBM_SCRIPT_RESOLUTION_REPORT.schema.json
```

### Zakres

Resolver domyślnie skanuje tylko aktywne datapacki:

```text
data
data-otservbr-global
```

`data-canary` nie jest automatycznie mieszany z aktywnym contentem.

Rozpoznawane wzorce:

- `Action()`;
- `MoveEvent()`;
- helper `BossLever(...)`;
- `:aid(...)`, `:uid(...)`, `:id(...)`, `:position(...)`;
- listy i ciągłe zakresy;
- numeryczne pętle `for`;
- `pairs()` i `ipairs()` po statycznych tabelach;
- współdzielone tabele drzwi z `data/libs/tables`;
- statyczne budowanie kolekcji przez `table.insert(...)`;
- legacy XML `<action>` i `<moveevent>`;
- `item.actionid`, `target.actionid`, `item.uid`, `target.uid` i gettery;
- fallback dispatchu po item ID;
- generyczny quest chest `actionId 2000`;
- teleport destination i house-door ID jako mechanika silnika.

Resolver nie uruchamia Lua. Nierozstrzygalne wyrażenia pozostają w `dynamicRegistrations` i nie są zgadywane.

### Priorytet dispatchu

Dla akcji należy zachować semantykę Canary:

```text
pozycja → unique ID → action ID → item ID
```

Dla movementów:

```text
unique ID → action ID → item ID
```

Konflikt jest zgłaszany tylko wtedy, gdy aktywne rejestracje konkurują w tym samym namespace, handler kind i event type. Para `stepin`/`stepout` nie jest konfliktem.

---

## 7. Walidacja wykonana lokalnie

### Testy

```text
python3 -m py_compile ...                         PASS
python3 -m unittest test_otbm_script_resolution  5/5 PASS
python3 -m unittest discover -s tools/ai-agent   140/140 PASS
```

Pełny raport przeszedł walidację JSON Schema Draft 2020-12 bez błędów.

Formatery `ruff` i `black` nie były dostępne lokalnie. GitHub CI jest źródłem prawdy dla formatowania.

### Audyt pełnej mapy

Polecenie:

```sh
python tools/ai-agent/otbm_script_resolution_tool.py \
  --root . \
  --item-scan /mnt/data/OTBM_ITEM_SCAN.json \
  --output /mnt/data/OTBM_SCRIPT_RESOLUTION.json \
  --map /mnt/data/otservbr.otbm \
  --expected-map-sha256 a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2 \
  --allow-unresolved
```

Wynik:

```text
pliki przeskanowane: 5,384
rejestracje: 1,470
nierozstrzygnięte dynamiczne rejestracje: 155
mechaniki mapowe: 9,339
rozwiązane umieszczenia: 8,907
częściowo rozwiązane umieszczenia: 76
nierozwiązane umieszczenia: 356
nierozwiązane identyfikatory: 205
częściowo rozwiązane identyfikatory: 1
konflikty dispatchu: 0
```

Statusy mechanik:

```text
handled-by-engine: 7,016
handled-multiple: 933
handled-directly: 667
handled-as-target: 405
handled-by-item-id: 353
handled-by-range: 45
unresolved: 432
```

Nie porównywać wprost liczby `205` z dawnym, niezachowanym wynikiem `150` jako regresji contentu. Różnią się parser, snapshot źródła i konserwatywność klasyfikacji. Finalny baseline musi pochodzić z dokładnego checkoutu PR #128.

---

## 8. Artefakty lokalne

```text
/mnt/data/OTBM_ITEM_SCAN.json
SHA-256: d6c28d476a5e9f12830f4d754744003d7c4addfb702a551354df7788c31d83e6

/mnt/data/OTBM_SCRIPT_RESOLUTION.json
SHA-256: 2438c312f802b9d1d9f8e3ebdfcebf219d67fe077f6e4b7c79f7ff29445ff220

/mnt/data/otservbr.otbm
SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
```

Artefakty nie są commitowane. Ścieżki `/mnt/data` nie są trwałe między sesjami.

---

## 9. Największe nierozwiązane grupy

Największe nierozwiązane `actionId` w bieżącym raporcie:

```text
26002  — 71 umieszczeń
50069  — 21
50081  — 16
50076  — 15
50075  — 14
50061  — 12
50066  — 10
50080  — 10
24867  — 8
50058  — 8
50067  — 7
50078  — 7
50088  — 6
1500   — 5
8000   — 4
13004  — 4
50060  — 4
50071  — 4
50999  — 4
35443  — 3
```

Wiele nierozwiązanych `uniqueId` to pojedyncze umieszczenia, między innymi zakresy rozpoczynające się od `1021`, `1029`, `1030`, `1036`, `1073`, `1075..1090+`.

Przykłady poprawnie rozpoznanych target references:

```text
actionId 4200
actionId 8024
actionId 50118
uniqueId 3071..3074
```

Każdy nierozwiązany identyfikator musi dostać ręcznie zatwierdzoną klasyfikację:

```text
handled
engine-handled
intentional-marker
legacy-unused
missing-script
needs-manual-review
```

Nie pisać brakującego skryptu bez ustalenia rzeczywistej funkcji obszaru.

---

## 10. Item 2141

Potwierdzony przypadek:

```text
item ID: 2141
pozycja: 33572,32528,14
wystąpienia: 1
brak actionId
brak uniqueId
brak teleport destination
brak house-door ID
brak appearance w kliencie 15.25
```

Istniał poprawny dry-run usunięcia tego jednego wpisu, ale mapa źródłowa nie została zmieniona.

Przed zamknięciem przypadku należy:

1. wykonać patch wyłącznie do nowej kopii mapy;
2. uruchomić inspect i verify;
3. sprawdzić semantyczny diff ograniczony do jednej pozycji;
4. wczytać wynik przez prawdziwy loader C++ Canary;
5. ponownie uruchomić audyt itemów;
6. potwierdzić `missingAppearanceIds = 0`;
7. zachować kopię źródła i możliwość cofnięcia.

---

## 11. Co ma zrobić następny agent

### Start sesji

1. Przeczytać `AGENTS.md`.
2. Otworzyć draft PR #128.
3. Potwierdzić repo `blakinio/canary`, base `main`, head `feat/otbm-script-resolution-20260712`.
4. Sprawdzić, czy `main` nie przesunął się od bazy PR.
5. Sprawdzić changed-files — dozwolone są tylko narzędzia i dokumentacja.
6. Odczytać wszystkie wyniki CI; nie zakładać, że są zielone.

### Walidacja PR #128

1. Uruchomić focused test resolvera.
2. Uruchomić cały zestaw `tools/ai-agent`.
3. Uruchomić repozytoryjne formatery/lintery dostępne w CI.
4. Sprawdzić schema validation.
5. Usunąć błędy CI minimalnym patchem.
6. Nie modyfikować datapacka ani mapy w tym PR.

### Finalny baseline mapy

Po checkout PR #128:

1. uzyskać mapę o oczekiwanym SHA-256;
2. skompilować `otbm_item_audit_scan.cpp`;
3. wygenerować świeży `OTBM_ITEM_SCAN.json`;
4. uruchomić resolver z `--expected-map-sha256`;
5. zapisać nowy SHA raportu i dokładny commit źródeł;
6. porównać wyniki z sekcją 7;
7. zaktualizować ten dokument.

### Klasyfikacja ID

Dla wszystkich nierozwiązanych ID:

1. pogrupować po namespace, ID, item ID, pozycji i sąsiedztwie;
2. sprawdzić aktywne skrypty;
3. sprawdzić upstream/legacy tylko jako referencję;
4. przypisać jedną z zatwierdzonych klasyfikacji;
5. dla `missing-script` przygotować osobny raport/issue;
6. nie modyfikować mapy przed zakończeniem klasyfikacji.

### Domknięcie PR

PR #128 można oznaczyć jako gotowy dopiero, gdy:

- wszystkie workflow są zielone;
- finalny raport pochodzi z checkoutu tego PR;
- schema jest zgodna z raportem;
- changed-files nie zawierają zakazanych ścieżek;
- dynamiczne rejestracje pozostają widoczne;
- dokument handoff zawiera aktualny head SHA i wyniki.

Nie merge’ować automatycznie. Merge wymaga osobnej, wyraźnej zgody użytkownika.

---

## 12. Późniejszy etap — rekonstrukcja świata

Rekonstrukcję brakujących regionów rozpocząć dopiero po audycie mechaniki.

Dla każdego pilotowego regionu:

1. wybrać mały, ograniczony obszar;
2. przypiąć hash mapy źródłowej;
3. przygotować patch do nowego pliku;
4. zweryfikować itemy, town, house, zone, spawn, NPC, teleport i quest;
5. uruchomić inspect, verify, diff, item audit i script resolver;
6. wczytać mapę przez Canary;
7. wyrenderować region przed/po z prawdziwych assetów;
8. zachować rollback.

---

## 13. Definicja ukończenia etapu audytu mapy

- [x] stary discovery-only PR #104 został zamknięty bez merge;
- [x] finalny resolver, CLI, schema, dokumentacja i testy istnieją w draft PR #128;
- [x] gałąź PR została utworzona z aktualnego `main` w momencie publikacji;
- [x] lokalnie przeszło 140 testów;
- [x] wykonano pełny audyt dostarczonej mapy;
- [x] konflikty dispatchu w raporcie: 0;
- [x] CI PR #128 jest w pełni zielone;
- [ ] raport został ponownie wygenerowany z dokładnego checkoutu PR #128;
- [ ] wszystkie nierozwiązane ID mają ręczną klasyfikację;
- [ ] item 2141 został bezpiecznie usunięty w kopii mapy albo świadomie odroczony;
- [ ] mapa po ewentualnej poprawce przechodzi loader Canary;
- [ ] końcowy raport został zatwierdzony przez użytkownika.

---

## 14. Changelog

### 2026-07-12 — finalny resolver i przekazanie sesji

- zamknięto nieużyteczny PR #104 bez merge;
- utworzono świeżą gałąź `feat/otbm-script-resolution-20260712`;
- dodano produkcyjny, tylko-do-odczytu resolver Lua/XML;
- dodano parser statycznego podzbioru Lua, skaner aktywnych datapacków i warstwę resolution;
- dodano CLI, JSON Schema, dokumentację i testy;
- focused testy: 5/5 PASS;
- cały `tools/ai-agent`: 140/140 PASS;
- przeskanowano 9,339 mechanik dostarczonej mapy;
- rozwiązano 8,907 umieszczeń, 76 oznaczono częściowo, 356 pozostało nierozwiązanych;
- wykryto 0 konfliktów dispatchu;
- otwarto draft PR #128;
- workflow `CI`, `OTBM Map Tools` i `AI Agent Tools` zakończyły się sukcesem na head `79a5df066e681b2c9249ac723b41ca3b86fc6fd7`;
- zaktualizowano niniejszy handoff dla nowego agenta;
- nie zmodyfikowano ani nie commitowano mapy, assetów, `items.otb`, datapacka ani produkcyjnej konfiguracji.

### Szablon kolejnego wpisu

```markdown
### YYYY-MM-DD — nazwa etapu

- baza i head SHA:
- PR:
- zakres:
- wykonane:
- testy i CI:
- wyniki audytu:
- artefakty i SHA-256:
- otwarte blokery:
- następny krok:
```
