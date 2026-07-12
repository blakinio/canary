# OTS / Canary — OTBM, TibiaMaps, assety i mechanika mapy — handoff

> **Stan:** 2026-07-12  
> **Repozytorium robocze:** `blakinio/canary`  
> **Etap narzędziowy:** zakończony i zmergowany  
> **Kanoniczny resolver:** PR #104, merge `0b355669ebe66c9d9c604c2a9221f47280699581`  
> **Dokument dla:** kolejnego agenta kontynuującego techniczną pracę z OTBM, resolverem albo pilotową rekonstrukcją regionu.

---

## 0. Podsumowanie zakończonego czatu

Zakres tej sesji dotyczył **technicznego warsztatu OTBM**, a nie budowy ogólnego systemu AI review questów, NPC i świata.

Wykonano:

1. parser, writer, inspect, verify, diff, patch i walidację semantyczną OTBM;
2. obsługę `actionId`, `uniqueId`, townów, waypointów, houses, zones, spawnów, NPC i companion XML;
3. parser współczesnego `appearances.dat`, dekoder sprite-sheetów CIP/LZMA i renderer zgodny z kolejnością warstw OTClient;
4. rzeczywisty render fragmentu Thais z assetów klienta, bez brakujących appearances i sprite'ów;
5. pełne porównanie geometrii OTBM z TibiaMaps;
6. audyt `23,359,571` umieszczeń itemów i `9,339` mechanik mapowych;
7. produkcyjny resolver wiążący identyfikatory mapy z handlerami Lua/XML;
8. poprawioną lokalną kopię mapy bez pojedynczego nieobsługiwanego itemu `2141`;
9. natywne potwierdzenie struktury poprawionej kopii przez Canary `OTB::Loader::parseTree()`.

Najważniejszy wynik: **warstwa narzędziowa jest gotowa**. Pozostały ręczny audyt 151 nierozwiązanych identyfikatorów, opcjonalny pełny test `Map::load()` / `IOMap` i pierwsza mała rekonstrukcja regionu.

Szerszy projekt AI review map, questów, NPC i spawnów jest osobnym zadaniem i nie należy mieszać go z tym handoffem.

---

## 1. Cel projektu

Projekt ma zapewnić bezpieczny i powtarzalny proces pracy z dużą mapą OTBM:

1. odczyt, zapis, diff i patch OTBM bez nadpisywania źródła;
2. porównanie geometrii świata z aktualną TibiaMaps;
3. audyt itemów względem `appearances.dat`, sprite'ów klienta i `items.xml`;
4. audyt `actionId`, `uniqueId`, teleportów i house-door IDs;
5. powiązanie identyfikatorów mapy z aktywnymi handlerami Lua/XML;
6. zachowanie customowej zawartości i niejasnych markerów do czasu ręcznej decyzji;
7. rekonstrukcja brakujących regionów jako małych, odwracalnych patchy;
8. walidacja przez testy, raporty, prawdziwy loader Canary i CI.

Docelowy wynik to mapa oparta na dostarczonym OTBM, uzupełniana etapami bez uszkodzenia questów, teleportów, domów, spawnów, NPC i skryptów.

---

## 2. Repozytoria

### Zapisywalne

- `https://github.com/blakinio/canary`

Obowiązujący przepływ:

```text
osobna gałąź -> PR -> pełne CI -> squash merge
```

### Referencyjne — tylko do odczytu

- `https://github.com/opentibiabr/canary`
- `https://github.com/opentibiabr/otclient`
- `https://github.com/opentibiabr/remeres-map-editor`
- `https://github.com/opentibiabr/client-editor`

Nie twórz zmian w repozytoriach `opentibiabr/*` w ramach tego projektu.

### Kanoniczne dokumenty tego zakresu

```text
docs/ai-agent/OTS_OTBM_AGENT_HANDOFF.md
docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md
docs/ai-agent/OTBM_SCRIPT_REVIEW_RULES.json
docs/ai-agent/OTBM_SCRIPT_RESOLUTION_REPORT.schema.json
```

---

## 3. Zasady bezpieczeństwa

- Nie nadpisuj źródłowego OTBM.
- Nie commituj `.otbm`, `items.otb`, `appearances.dat`, sprite-sheetów, paczek klienta ani danych TibiaMaps.
- Nie pushuj bezpośrednio do `main`.
- Nie merge'uj PR bez przeglądu changed-files i zielonych wymaganych workflow.
- Nie usuwaj `actionId` ani `uniqueId` tylko dlatego, że resolver nie znalazł handlera.
- Nie traktuj `OTBM-only` jako automatycznego błędu.
- Nie odtwarzaj dokładnych item stacków na podstawie samych kolorów minimapy.
- Nie używaj generatora obrazów do renderowania mapy. Render ma pochodzić z OTBM i prawdziwych assetów.
- Nie zgaduj funkcji nierozpoznanego identyfikatora.
- Każdy patch mapy musi mieć:
  - SHA-256 źródła;
  - dry-run;
  - semantyczny diff;
  - walidację;
  - możliwość cofnięcia.

---

## 4. Dane wejściowe i artefakty lokalne

### Mapa źródłowa

```text
plik sesji: /mnt/data/otservbr(2).otbm
rozmiar: 184,776,037 B
SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
kafle: 17,972,761
umieszczenia itemów: 23,359,571
unikalne item ID: 23,852
mechaniki mapowe: 9,339
```

Nowa sesja może nie mieć plików z `/mnt/data`. W takim przypadku użytkownik musi ponownie przesłać mapę; przed pracą obowiązkowo sprawdź SHA-256.

### Oficjalne assety klienta

```text
plik sesji: /mnt/data/assets.zip
wersja: 15.25.bd5a04
appearance objects: 42,107
```

Archiwum zawiera m.in. `catalog-content.json`, `appearances.dat`, sprite-sheety CIP/LZMA i minimapy. Nie commituj go.

### Najważniejsze raporty lokalne

```text
/mnt/data/OTBM_LATEST_AUDIT.md
/mnt/data/OTBM_LATEST_AUDIT.json
/mnt/data/OTBM_LATEST_DIFF_OVERVIEW.png
/mnt/data/resolver-dev/OTBM_SCRIPT_RESOLUTION_FINAL.json
/mnt/data/CANARY_FILELOADER_2141_VALIDATION.log
```

Kanoniczny raport resolvera:

```text
SHA-256: 596e119470ae43b07a86ab2fd61e47af98900746d3360e8f49747241917d9bd3
```

Raporty są artefaktami lokalnymi i nie są commitowane.

---

## 5. Wyniki porównania z TibiaMaps

```text
pola referencyjne: 11,434,263
pola wspólne: 10,560,778
pokrycie referencji: 92.36%
latest-only: 873,485
latest-only przechodnie: 210,148
OTBM-only: 7,326,317
duplikaty OTBM w zakresie referencji: 0
```

Interpretacja:

- `latest-only` to kandydaci do rekonstrukcji, a nie gotowe patche;
- `OTBM-only` mogą być customowe, ukryte, techniczne albo pochodzić ze starszej wersji;
- TibiaMaps nie opisuje dokładnych item ID, stack order, questów, teleport destinations, houses, spawnów ani skryptów.

---

## 6. Audyt itemów i poprawka 2141

Pełny skan mapy:

```text
kafle: 17,972,761
umieszczenia itemów: 23,359,571
unikalne item ID: 23,852
umieszczenia z actionId/uniqueId/teleport/house-door: 9,339
nieznane lub ucięte atrybuty: 0
```

Tylko item ID `2141`, użyty raz na pozycji `33572,32528,14`, nie miał appearance w kliencie 15.25.

Brak wpisu w `items.xml` nie oznacza automatycznie nieobsługiwanego itemu — Canary tworzy bazowe `ItemType` z `appearances.dat`, a XML nakłada nadpisania.

### Poprawiona lokalna kopia

```text
plik: /mnt/data/otservbr-fixed-reserved-item.otbm
rozmiar: 184,776,032 B
SHA-256: 0eb5672a315704b816b430af29b1bc8e51b031fbe20689e271437319973ae83b
```

Potwierdzone:

- źródłowy plik pozostał nietknięty;
- zmieniono tylko pozycję `33572,32528,14`;
- usunięto dokładnie jedno umieszczenie itemu `2141`;
- liczba kafli pozostała `17,972,761`;
- liczba itemów spadła do `23,359,570`;
- liczba unikalnych ID spadła do `23,851`;
- mechaniki mapowe pozostały bez zmian;
- `missingAppearanceIds = 0`;
- ponowny audyt: `ok = true`.

### Natywna walidacja Canary

```text
wynik: PASS
wyjście: ok root_type=0 root_children=1
exit status: 0
czas: 13.37 s
maksymalna pamięć RSS: 2,141,672 KiB
SHA-256 logu: 74192e23cd8f74e43715575d7acb000a8b7f6fe67fbba0c4cadcb3a3529e860b
```

Test użył rzeczywistego `src/io/fileloader.cpp` i niezmienionej logiki `OTB::Loader::parseTree()`.

To zamyka walidację strukturalną binarnego drzewa OTBM. Pełny test semantyczny `Map::load()` / `IOMap` z kompletnymi zależnościami serwera nadal pozostaje zalecanym testem przed produkcyjnym wdrożeniem mapy.

---

## 7. Produkcyjny resolver handlerów

PR #104 został zmergowany:

```text
PR: https://github.com/blakinio/canary/pull/104
merge SHA: 0b355669ebe66c9d9c604c2a9221f47280699581
```

Dodane pliki:

```text
tools/ai-agent/otbm_script_resolution.py
tools/ai-agent/otbm_script_resolution_tool.py
tools/ai-agent/test_otbm_script_resolution.py
docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md
docs/ai-agent/OTBM_SCRIPT_RESOLUTION_REPORT.schema.json
docs/ai-agent/OTBM_SCRIPT_REVIEW_RULES.json
```

Resolver skanuje domyślnie aktywne datapacki:

```text
data
data-otservbr-global
```

`data-canary` nie jest mieszany automatycznie.

Obsługiwane wzorce obejmują:

- `Action()` i `MoveEvent()`;
- bezpośrednie `:aid()`, `:uid()`, `:id()`, `:position()`;
- listy, zakresy i pętle numeryczne;
- `pairs()` i `ipairs()` po statycznych tabelach;
- starsze rejestracje XML;
- porównania i lookupy `target.actionid` / `target.uid`;
- ograniczone target ranges;
- item-ID fallback dla drzwi i kluczy;
- quest chest fallback, w tym `actionId 2000`;
- teleport destinations i house-door IDs jako mechaniki silnika.

MoveEventy `stepin`, `stepout`, `additem`, `removeitem`, `equip` i `deequip` są rozdzielone, więc prawidłowe pary nie tworzą fałszywych konfliktów.

### Wyniki resolvera

```text
pliki Lua/XML: 5,384
rejestracje runtime: 1,182
reguły target/reference: 266
mechaniki mapowe: 9,339
runtime-resolved placements: 8,964
runtime-unresolved/partial placements: 375
runtime-unresolved/partial identifiers: 151
identyfikatory bez review disposition: 0
konflikty placements: 0
dynamiczne rejestracje zachowane jako ostrzeżenia: 253
raport domyślny: ok = true
strict runtime: false
```

Największe zachowane grupy:

```text
actionId 26002
actionId 50058..50088
actionId 48000..48006
actionId 2090..2096
uniqueId 62133
uniqueId 62135
```

`docs/ai-agent/OTBM_SCRIPT_REVIEW_RULES.json` nadaje wszystkim 151 ID dyspozycję `needs-manual-review`.

To nie jest potwierdzenie handlera. Dyspozycja review jest zapisem bezpieczeństwa i nie zmienia statusu runtime `unresolved` na `handled`.

---

## 8. Walidacja PR #104

Przed merge potwierdzono:

```text
focused resolver tests: PASS
pełny tools/ai-agent suite: 139 tests PASS
schema JSON: PASS
review-rules JSON: PASS
OTBM Map Tools: PASS
AI Agent Tools: PASS
ogólne CI: PASS
konflikty review: 0
zakazane pliki w diffie: 0
```

PR #104 zawierał dokładnie sześć produkcyjnych plików i został wykonany jako squash merge.

Równoległy PR #128 został zamknięty bez merge jako duplikat/superseded.

---

## 9. Historia zmergowanych etapów

### Fundament OTBM

- PR #84 — parser/writer OTBM, inspect, verify, export, diff i apply.
- PR #85 — katalog `items.xml` i semantyczna walidacja patchy.
- PR #87 — indeks świata, towns, waypoints, houses, zones i companion XML.
- PR #88 — rejestr `actionId` / `uniqueId`.
- PR #90 — bezpieczne authoring companion XML.
- PR #91 — test ładowania mapy przez prawdziwy loader C++ Canary.

### Assety i render

- PR #93 — indeks paczek assetów OTClient/RME.
- PR #94 — parser protobuf `appearances.dat`.
- PR #95 — dekoder CIP/raw-LZMA sprite-sheetów.
- PR #96 — deterministyczny renderer regionów.
- PR #98 — realne nagłówki CIP i zredukowane paczki renderujące.

### Porównanie i audyt

- PR #100 — porównanie OTBM z TibiaMaps.
- PR #101 — pełny audyt itemów i mechaniki mapy.
- PR #104 — produkcyjny resolver skryptów.
- PR #116 — pierwsza wersja tego handoffu.
- PR #130 — finalny stan resolvera i poprawki 2141 w handoffie.
- PR #133 — natywna walidacja `OTB::Loader::parseTree()`.

### PR-y operacyjne bez merge

- PR #97 — tymczasowy eksport assetów.
- PR #99 — tymczasowe pobieranie TibiaMaps.
- PR #128 — duplikat resolvera, zamknięty bez merge.
- PR #131 — nieaktualny duplikat handoffu, zamknięty bez merge.

---

## 10. Co nadal zostało do zrobienia

### P0 — opcjonalny pełny test `Map::load()` / `IOMap`

- zbudować pełne testy integracyjne Canary z zależnościami vcpkg;
- uruchomić `Map::load()` na poprawionej kopii;
- wczytać companion XML, houses, zones, spawns i NPC;
- zachować wynik jako artefakt CI lub lokalny log.

### P0 — ręczny audyt 151 identyfikatorów

Dla każdego ID:

1. pogrupować po namespace, wartości, item ID, pozycji, piętrze i sąsiedztwie;
2. sprawdzić aktywne skrypty;
3. sprawdzić upstream/legacy wyłącznie jako referencję;
4. ustalić rzeczywistą funkcję obszaru;
5. nadać jedną z dyspozycji:
   - `intentional-marker`
   - `legacy-unused`
   - `missing-script`
   - `needs-manual-review`
   - `preserve-until-reviewed`
6. dla `missing-script` przygotować osobny PR;
7. nie usuwać atrybutu mapy przed potwierdzeniem funkcji.

### P1 — pilotowa rekonstrukcja regionu

1. wybrać mały komponent `latest-only`;
2. przypiąć SHA źródłowej mapy;
3. przygotować patch do nowego pliku;
4. zweryfikować itemy, town, house, zone, spawn, NPC, teleport i quest;
5. uruchomić inspect, verify, diff, item audit i script resolver;
6. wczytać przez Canary;
7. wyrenderować przed/po z prawdziwych assetów;
8. zachować rollback.

Nie próbować automatycznie rekonstruować całego świata z minimapy.

---

## 11. Definicja ukończenia

### Etap narzędziowy — zakończony

- [x] parser/writer i patchowanie OTBM;
- [x] porównanie z TibiaMaps;
- [x] audyt wszystkich itemów;
- [x] resolver handlerów;
- [x] CLI, schema, dokumentacja i testy;
- [x] 151 ID ma bezpieczne review disposition;
- [x] konflikty placements = 0;
- [x] PR #104 zmergowany na zielonym CI;
- [x] poprawiona kopia mapy bez itemu 2141;
- [x] ponowny item audit bez brakujących appearances;
- [x] natywny `OTB::Loader::parseTree()` potwierdza strukturę poprawionej kopii.

### Jeszcze nie zakończone

- [ ] opcjonalny pełny test integracyjny `Map::load()` / `IOMap`;
- [ ] 151 ID ma docelową, evidence-based klasyfikację;
- [ ] wybrano i zwalidowano pierwszy pilotowy region;
- [ ] rozpoczęto produkcyjną rekonstrukcję świata.

---

## 12. Szybki start kolejnego agenta

1. Przeczytaj `AGENTS.md`.
2. Przeczytaj ten dokument.
3. Sprawdź aktualny `main`.
4. Potwierdź obecność merge `0b355669ebe66c9d9c604c2a9221f47280699581`.
5. Sprawdź dostępność mapy i jej SHA-256.
6. Uruchom:

```bash
python tools/ai-agent/otbm_script_resolution_tool.py --help
```

7. Zapoznaj się z logiem natywnego `FileLoader` i w razie dostępnego pełnego środowiska uruchom dodatkowo `Map::load()`.
8. Wybierz jedną grupę z 151 ID do ręcznej analizy albo jeden mały region pilotowy.
9. Każdą zmianę wykonuj na osobnej gałęzi i w osobnym PR.

---

## 13. Przykładowe uruchomienie resolvera

```bash
python tools/ai-agent/otbm_script_resolution_tool.py \
  artifacts/OTBM_ITEM_AUDIT.json \
  --repository-root . \
  --script-root data \
  --script-root data-otservbr-global \
  --review-rules docs/ai-agent/OTBM_SCRIPT_REVIEW_RULES.json \
  --output artifacts/OTBM_SCRIPT_RESOLUTION.json
```

Tryb wymagający braku wszystkich nierozwiązanych runtime ID:

```bash
python tools/ai-agent/otbm_script_resolution_tool.py \
  artifacts/OTBM_ITEM_AUDIT.json \
  --repository-root . \
  --review-rules docs/ai-agent/OTBM_SCRIPT_REVIEW_RULES.json \
  --strict-runtime \
  --output artifacts/OTBM_SCRIPT_RESOLUTION.json
```

`--strict-runtime` ma obecnie zakończyć się niepowodzeniem, ponieważ 151 ID nadal wymaga ręcznego audytu.

---

## 14. Changelog 2026-07-12

- zbudowano pełny warsztat OTBM i renderer wykorzystujący prawdziwe assety klienta;
- porównano pełny OTBM z TibiaMaps;
- wykonano audyt `23,359,571` umieszczeń itemów;
- wykryto jeden brak appearance: item `2141`;
- utworzono poprawioną lokalną kopię bez itemu `2141`;
- ponowny audyt wykazał zero brakujących appearances;
- dokładny `src/io/fileloader.cpp` Canary poprawnie sparsował całą poprawioną mapę w `13.37 s`;
- zbudowano i zmergowano produkcyjny resolver handlerów;
- wykonano audyt `9,339` mechanik mapowych;
- potwierdzono `8,964` runtime-resolved placements;
- zachowano `375` unresolved/partial placements i `151` identyfikatorów do ręcznego audytu;
- wykryto zero konfliktów placements;
- nie commitowano mapy, assetów ani dużych wygenerowanych raportów;
- oddzielono ten techniczny handoff od późniejszego, szerszego projektu AI review map, questów, NPC i spawnów.
