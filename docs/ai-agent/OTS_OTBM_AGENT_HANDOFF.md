# OTS / Canary — OTBM, TibiaMaps, assety i mechanika mapy — handoff

> **Stan:** 2026-07-12  
> **Repozytorium robocze:** `blakinio/canary`  
> **Etap narzędziowy:** zakończony i zmergowany  
> **Kanoniczny resolver:** PR #104, merge `0b355669ebe66c9d9c604c2a9221f47280699581`  
> **Aktualny ręczny audyt:** PR #137 klasyfikuje `actionId 26002` jako `legacy-unused`; po zastosowaniu reguł zostaje 150 ID z dyspozycją `needs-manual-review`  
> **Dokument dla:** kolejnego agenta kontynuującego audyt mechaniki, walidację świata lub pilotową rekonstrukcję regionu.

---

## 0. Podsumowanie zakończonej sesji

W tej sesji zbudowano i zweryfikowano kompletny warsztat do bezpiecznej pracy z dużą mapą OTBM:

1. parser, writer, inspect, verify, diff, patch i walidację semantyczną OTBM;
2. obsługę `actionId`, `uniqueId`, townów, waypointów, houses, zones, spawnów, NPC i companion XML;
3. parser współczesnego `appearances.dat`, dekoder sprite-sheetów CIP/LZMA i renderer zgodny z kolejnością warstw OTClient;
4. rzeczywisty render fragmentu Thais z assetów klienta, bez brakujących appearances i sprite'ów;
5. pełne porównanie geometrii OTBM z TibiaMaps;
6. audyt 23,359,571 umieszczeń itemów i 9,339 mechanik mapowych;
7. produkcyjny resolver wiążący identyfikatory mapy z handlerami Lua/XML;
8. poprawioną lokalną kopię mapy bez pojedynczego nieobsługiwanego itemu `2141`;
9. natywne potwierdzenie poprawności struktury tej kopii przez Canary `OTB::Loader::parseTree()`;
10. pierwszy ręczny review nierozwiązanego identyfikatora: `actionId 26002`.

Najważniejszy wniosek: **warstwa narzędziowa jest gotowa**. Dalsza praca to już evidence-based gameplay review pozostałych identyfikatorów oraz małe, odwracalne rekonstrukcje wybranych regionów.

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

## 2. Repozytoria i źródła prawdy

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

### Dokumenty kanoniczne

```text
docs/ai-agent/OTS_OTBM_AGENT_HANDOFF.md
docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md
docs/ai-agent/OTBM_SCRIPT_REVIEW_RULES.json
docs/ai-agent/OTBM_ACTIONID_26002_REVIEW.md
docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md
```

`OTS_OTBM_AGENT_HANDOFF.md` pozostaje technicznym handoffem narzędzi OTBM.  
`OTS_AI_WORLD_VALIDATION_PROJECT.md` opisuje szerszy projekt walidacji map, questów, NPC, spawnów, itemów i przyszłych testów runtime/E2E.

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
- Dyspozycja review nie zmienia statusu runtime `unresolved` na `handled`.
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

Kanoniczny raport resolvera sprzed pierwszej klasyfikacji manualnej:

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

Test użył rzeczywistego `src/io/fileloader.cpp` i niezmienionej logiki `OTB::Loader::parseTree()`. Pełny test semantyczny `Map::load()` / `IOMap` z kompletnymi zależnościami serwera nadal pozostaje zalecanym testem przed produkcyjnym wdrożeniem mapy.

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

### Wynik bazowy resolvera

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

---

## 8. Pierwszy ręczny review — `actionId 26002`

PR #137 klasyfikuje ten identyfikator na podstawie mapy i aktywnych ścieżek runtime:

```text
ID: 26002
namespace: actionId
placements: 71
obszar: Soul War — Ebb and Flow / Bony Sea Devil
itemy: 4394..4410, rock soil
aktywny mechanizm: ebbAndFlowBoatTeleports
rejestracja runtime: bezpośrednio po pozycjach
decision: legacy-unused
confidence: high
map change: none
gameplay change: none
```

Najważniejsze dowody:

- wszystkie 71 markerów leży na `z=8` w Ebb and Flow;
- aktywny `MoveEvent` korzysta z `SoulWarQuest.ebbAndFlowBoatTeleportPositions`;
- runtime ma 173 rejestracje pozycyjne;
- 64 z 71 pozycji z AID 26002 pokrywa się z aktywnymi handlerami;
- 109 aktywnych pozycji nie ma AID 26002, więc ten AID nie jest kluczem wykonawczym;
- aktywne datapacki, `data-canary` i C++ nie rejestrują handlera po `actionId 26002`;
- siedem niepokrywających się markerów pozostaje zachowanych jako legacy metadata;
- nie usunięto żadnego atrybutu mapy.

Po zastosowaniu reguł z PR #137:

```text
runtime-unresolved identifiers: 151
legacy-unused: 1
needs-manual-review: 150
conflicts: 0
normal resolver: ok = true
strict runtime: exit 2, oczekiwany
```

Review disposition nie udaje handlera runtime. `actionId 26002` nadal pozostaje nierozwiązany w trybie strict, ale jego funkcja historyczna została określona z wysoką pewnością.

Pełny raport:

```text
docs/ai-agent/OTBM_ACTIONID_26002_REVIEW.md
```

---

## 9. Walidacja wykonanych etapów

### PR #104

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

PR #104 zawierał dokładnie sześć produkcyjnych plików i został wykonany jako squash merge. PR #128 został zamknięty bez merge jako duplikat.

### PR #137 — walidacja lokalna

```text
focused resolver tests: 4 PASS
pełny tools/ai-agent suite: 139 PASS
normal resolver: ok = true
legacy-unused: 1
needs-manual-review: 150
conflicts: 0
strict runtime: exit 2, oczekiwany
```

PR #137 jest otwarty i gotowy do review; przed merge trzeba ponownie sprawdzić changed-files i workflow na aktualnym headzie.

---

## 10. Historia etapów

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

### Porównanie, audyt i handoff

- PR #100 — porównanie OTBM z TibiaMaps.
- PR #101 — pełny audyt itemów i mechaniki mapy.
- PR #104 — produkcyjny resolver skryptów.
- PR #116 — pierwsza wersja handoff.
- PR #130 — finalny stan resolvera i poprawki 2141 w handoff.
- PR #133 — natywna walidacja `OTB::Loader::parseTree()`.
- PR #137 — ręczny review `actionId 26002` i projekt walidacji świata; obecnie otwarty.

### PR-y operacyjne bez merge

- PR #97 — tymczasowy eksport assetów.
- PR #99 — tymczasowe pobieranie TibiaMaps.
- PR #128 — duplikat resolvera.
- PR #131 — nieaktualny duplikat handoff.

---

## 11. Co nadal zostało do zrobienia

### P0 — przejrzeć pozostałe 150 identyfikatorów

Następna zalecana grupa:

```text
actionId 50058..50088
```

Dla każdej grupy:

1. pogrupować po namespace, wartości, item ID, pozycji, piętrze i sąsiedztwie;
2. sprawdzić aktywne skrypty;
3. sprawdzić upstream/legacy tylko jako referencję;
4. ustalić rzeczywistą funkcję obszaru;
5. nadać jedną dyspozycję:
   - `intentional-marker`
   - `legacy-unused`
   - `missing-script`
   - `needs-manual-review`
   - `preserve-until-reviewed`
6. dla `missing-script` przygotować osobny PR;
7. nie usuwać atrybutu mapy przed potwierdzeniem funkcji.

### P0 — opcjonalny pełny test `Map::load()` / `IOMap`

- zbudować pełne testy integracyjne Canary z zależnościami vcpkg;
- uruchomić `Map::load()` na poprawionej kopii;
- wczytać companion XML, houses, zones, spawns i NPC;
- zachować wynik jako artefakt CI lub lokalny log.

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

## 12. Definicja ukończenia

### Zakończone

- [x] parser/writer i patchowanie OTBM;
- [x] porównanie z TibiaMaps;
- [x] audyt wszystkich itemów;
- [x] resolver handlerów;
- [x] CLI, schema, dokumentacja i testy;
- [x] wszystkie 151 ID mają bezpieczną dyspozycję review;
- [x] konflikty placements = 0;
- [x] poprawiona kopia mapy bez itemu 2141;
- [x] ponowny item audit bez brakujących appearances;
- [x] natywny `OTB::Loader::parseTree()` potwierdza strukturę poprawionej kopii;
- [x] pierwszy evidence-based review: `actionId 26002 -> legacy-unused`.

### Jeszcze nie zakończone

- [ ] PR #137 przeszedł pełny review i został zmergowany;
- [ ] opcjonalny pełny test integracyjny `Map::load()` / `IOMap`;
- [ ] pozostałe 150 ID ma docelową, evidence-based klasyfikację;
- [ ] wybrano i zwalidowano pierwszy pilotowy region;
- [ ] rozpoczęto produkcyjną rekonstrukcję świata.

---

## 13. Szybki start kolejnego agenta

1. Przeczytaj `AGENTS.md`.
2. Przeczytaj ten dokument.
3. Przeczytaj `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`.
4. Sprawdź aktualny `main` i stan PR #137.
5. Potwierdź obecność merge `0b355669ebe66c9d9c604c2a9221f47280699581`.
6. Sprawdź dostępność mapy i jej SHA-256.
7. Uruchom:

```bash
python tools/ai-agent/otbm_script_resolution_tool.py --help
```

8. Jeżeli kontynuujesz review, zacznij od `actionId 50058..50088`.
9. Jeżeli pracujesz nad mapą, nie używaj źródłowego OTBM jako pliku wyjściowego.
10. Każdą zmianę wykonuj na osobnej gałęzi i w osobnym PR.

---

## 14. Przykładowe uruchomienie resolvera

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

`--strict-runtime` nadal ma zakończyć się niepowodzeniem, ponieważ wszystkie 151 identyfikatorów pozostaje runtime-unresolved; manualne dyspozycje nie udają handlerów.

---

## 15. Changelog 2026-07-12

- zbudowano pełny warsztat OTBM i renderer wykorzystujący prawdziwe assety klienta;
- porównano pełny OTBM z TibiaMaps;
- wykonano audyt 23,359,571 umieszczeń itemów;
- wykryto i usunięto z lokalnej kopii pojedynczy brak appearance: item 2141;
- ponowny audyt wykazał zero brakujących appearances;
- `OTB::Loader::parseTree()` poprawnie sparsował całą poprawioną mapę w 13.37 s;
- zbudowano i zmergowano produkcyjny resolver handlerów;
- wykonano audyt 9,339 mechanik mapowych;
- potwierdzono 8,964 runtime-resolved placements i 375 unresolved/partial placements;
- zachowano 151 runtime-unresolved identifiers z bezpiecznymi dyspozycjami review;
- wykryto zero konfliktów placements;
- ręcznie sklasyfikowano `actionId 26002` jako `legacy-unused` z wysoką pewnością;
- po tej klasyfikacji pozostaje 150 ID z dyspozycją `needs-manual-review`;
- nie zmieniono mapy, gameplayu ani aktywnego datapacka w ramach review 26002;
- następną zalecaną grupą jest `actionId 50058..50088`;
- nie commitowano mapy, assetów ani dużych wygenerowanych raportów.
