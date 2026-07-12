# OTS / Canary — handoff projektu OTBM, TibiaMaps, assetów i audytu mechaniki

> **Stan dokumentu:** 2026-07-12 — aktualizowany na bieżąco  
> **Repozytorium zapisu:** `blakinio/canary`  
> **Kanoniczny draft PR:** [#104 feat(ai-agent): resolve OTBM script handlers](https://github.com/blakinio/canary/pull/104)  
> **Gałąź:** `feat/otbm-script-resolution-audit`  
> **Baza po ostatnim przebudowaniu:** `1389489aa369fb6218aaab6e79224247cb9b64ef`  
> **Commit resolvera przed aktualizacją tego dokumentu:** `28d2e31f2e95537456b0bf8f13a68af0f667f2df`

---

## 1. Cel projektu

Celem projektu jest zbudowanie bezpiecznego i powtarzalnego procesu, który pozwala:

1. analizować bardzo duże mapy OTBM bez ładowania całego świata do pamięci;
2. porównywać mapę serwera z TibiaMaps i innymi wersjonowanymi referencjami;
3. wykrywać brakujące regiony, różnice przechodniości i obszary customowe;
4. sprawdzać zgodność itemów z `appearances.dat`, assetami klienta i `items.xml`;
5. zachować mechanikę mapy: `actionId`, `uniqueId`, teleporty, domy, kontenery, questy i skrypty;
6. przygotowywać odwracalne, przypięte hashem patche bez nadpisywania mapy źródłowej;
7. walidować każdy patch przez parser OTBM, prawdziwy loader Canary, audyty i CI.

### Cel końcowy

Docelowo ma powstać zwalidowana mapa wynikowa oparta na dostarczonym OTBM, uzupełniana etapami o brakujące obszary bez utraty customowej zawartości oraz bez uszkodzenia questów, teleportów, domów, spawnów i skryptów.

---

## 2. Zasady bezwzględne

- Nie nadpisywać źródłowego OTBM.
- Nie commitować `.otbm`, `items.otb`, `appearances.dat`, sprite-sheetów, assetów klienta ani pełnych danych TibiaMaps.
- Nie pushować bezpośrednio do `main`.
- Nie merge’ować PR bez pełnego przeglądu changed-files i zielonego CI.
- Nie usuwać `actionId` lub `uniqueId` tylko dlatego, że statyczny resolver nie znalazł handlera.
- Nie traktować pól OTBM-only jako automatycznego błędu.
- Nie zgadywać brakujących itemów, potworów, NPC ani funkcji obszaru.
- Nie rekonstruować dużych regionów przed zakończeniem audytu mechaniki.
- Każdy patch mapy musi mieć hash źródła, dry-run, diff, walidację i możliwość cofnięcia.
- Repozytoria `opentibiabr/*` są wyłącznie referencyjne i tylko do odczytu.

---

## 3. Repozytoria

### Zapisywalne

- `https://github.com/blakinio/canary`

### Referencyjne

- `https://github.com/opentibiabr/canary`
- `https://github.com/opentibiabr/otclient`
- `https://github.com/opentibiabr/remeres-map-editor`
- `https://github.com/opentibiabr/client-editor`

---

## 4. Mapa bazowa

```text
lokalna nazwa: /mnt/data/otservbr.otbm
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

Mapa nie znajduje się w GitHubie. Nowa sesja może nie mieć pliku z `/mnt/data`; wtedy należy poprosić użytkownika o ponowne przesłanie i zawsze sprawdzić SHA-256.

---

## 5. Assety i referencja

Poprzednie audyty korzystały z paczki oficjalnego klienta:

```text
wersja: 15.25.bd5a04
appearance objects: 42,107
```

Assety nie są częścią repozytorium i mogą nie przetrwać między sesjami.

Porównanie z TibiaMaps wykazało wcześniej:

```text
pola referencyjne: 11,434,263
wspólne pola: 10,560,778
pokrycie referencji: 92.36%
latest-only: 873,485
latest-only przechodnie: 210,148
OTBM-only: 7,326,317
```

`latest-only` to kandydaci do późniejszej rekonstrukcji, a nie gotowe patche. `OTBM-only` mogą być customowe, techniczne albo starsze i nie wolno ich automatycznie usuwać.

---

## 6. Historia narzędzi OTBM

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
- PR #98 — obsługa realnych nagłówków CIP i zredukowanych paczek.

### Porównanie i audyt

- PR #100 — porównanie OTBM z TibiaMaps i komponenty brakujących regionów.
- PR #101 — pełny audyt itemów i mechanik mapowych.

---

## 7. Kanoniczny resolver — PR #104

### Pliki implementacji

```text
tools/ai-agent/otbm_script_resolution.py
tools/ai-agent/otbm_script_resolution_tool.py
tools/ai-agent/test_otbm_script_resolution.py
docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md
docs/ai-agent/OTBM_SCRIPT_RESOLUTION_REPORT.schema.json
docs/ai-agent/OTBM_SCRIPT_REVIEW_RULES.json
```

Ten dokument jest siódmym zmienionym plikiem na gałęzi i służy wyłącznie przekazaniu projektu.

### Domyślnie aktywne datapacki

```text
data
data-otservbr-global
```

`data-canary` nie jest automatycznie mieszany z aktywnym contentem.

### Rozpoznawane wzorce

- `Action()` i `MoveEvent()`;
- bezpośrednie `:aid(...)`, `:uid(...)`, `:id(...)`, `:position(...)`;
- listy i numeryczne zakresy;
- numeryczne pętle `for`;
- `pairs()` i `ipairs()` po statycznych tabelach;
- rejestracje XML actions i movements;
- porównania `target.actionid` i `target.uid`;
- lookupy tabelowe typu `config[target.actionid]`;
- ograniczone target ranges;
- item-ID fallback dla drzwi i kluczy z `items.xml`;
- fallback quest chest, w tym `actionId 2000`;
- teleport destination i house-door ID jako mechanika silnika.

### Ważne rozdzielenie

Resolver osobno odpowiada na dwa pytania:

1. **Runtime resolution** — czy istnieje dowód, że Canary wykona mechanikę?
2. **Review disposition** — czy nierozwiązane ID zostało jawnie zaklasyfikowane do zachowania i dalszej analizy?

Reguła review nigdy nie zmienia `unresolved` na fałszywe `handled`.

### Review rules

`docs/ai-agent/OTBM_SCRIPT_REVIEW_RULES.json` zawiera 151 nierozwiązanych lub częściowo rozwiązanych identyfikatorów z dyspozycją:

```text
needs-manual-review
```

Dozwolone przyszłe dyspozycje:

```text
intentional-marker
legacy-unused
missing-script
needs-manual-review
preserve-until-reviewed
```

Dzięki temu raport domyślny może mieć `ok = true`, gdy nie ma konfliktów i każdy runtime-unresolved identyfikator ma jawną dyspozycję. Tryb `--strict-runtime` nadal poprawnie kończy się niepowodzeniem, dopóki pozostają braki runtime.

---

## 8. Wyniki pełnego audytu mapy

Walidacja wykonana dla dostarczonego OTBM i aktywnych datapacków:

```text
pliki Lua/XML: 5,384
rejestracje runtime: 1,182
reguły target/reference: 266
mechaniki mapowe: 9,339
runtime-resolved placements: 8,964
runtime unresolved/partial placements: 375
runtime unresolved/partial identifiers: 151
identyfikatory bez review disposition: 0
konflikty placements: 0
dynamiczne rejestracje zachowane jako ostrzeżenia: 253
raport domyślny: ok = true
strict runtime: false
```

Największe zachowane grupy do analizy:

```text
actionId 26002
actionId 50058..50088
actionId 48000..48006
actionId 2090..2096
uniqueId 62133
uniqueId 62135
```

Nie wolno ich automatycznie usuwać ani remapować.

---

## 9. Walidacja resolvera

Lokalnie wykonano:

```text
Python modules compile: PASS
focused resolver tests: PASS
pełny tools/ai-agent suite: 139 tests PASS
report schema validation: PASS
review-rules JSON validation: PASS
```

Testy obejmują:

- direct AID/UID;
- numeryczne zakresy;
- table loops;
- target tables i target ranges;
- osobne MoveEvent types bez fałszywych konfliktów;
- rzeczywiste konflikty;
- quest fallback;
- door/key fallback;
- mechanikę silnika;
- wybór aktywnych datapacków;
- dynamic-registration warnings;
- review dispositions.

GitHub Actions jest ostatecznym źródłem prawdy przed oznaczeniem PR jako gotowy.

---

## 10. Artefakty lokalne

```text
/mnt/data/otservbr.otbm
SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2

/mnt/data/OTBM_ITEM_SCAN.json
SHA-256: d6c28d476a5e9f12830f4d754744003d7c4addfb702a551354df7788c31d83e6

/mnt/data/OTBM_SCRIPT_RESOLUTION.json
SHA-256: 2438c312f802b9d1d9f8e3ebdfcebf219d67fe077f6e4b7c79f7ff29445ff220
```

Ostatni JSON pod powyższym hashem pochodzi z alternatywnej implementacji PR #128 i służy tylko jako pomocniczy artefakt. Kanoniczny finalny raport należy ponownie wygenerować narzędziem z PR #104 i zapisać jego nowy hash.

Ścieżki `/mnt/data` nie są trwałe między sesjami.

---

## 11. Item 2141

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
3. sprawdzić semantyczny diff ograniczony do pozycji `33572,32528,14`;
4. wczytać wynik przez prawdziwy loader C++ Canary;
5. ponownie uruchomić audyt itemów;
6. potwierdzić `missingAppearanceIds = 0`;
7. zachować kopię źródła i możliwość cofnięcia.

---

## 12. Status duplikatu PR #128

PR #128 powstał równolegle podczas tej samej sesji. Zawierał działający, ale mniej kompletny wariant resolvera bez wersjonowanej warstwy review dispositions.

Decyzja:

```text
kanoniczny PR: #104
PR #128: superseded / zamknąć bez merge
```

Nie przenosić implementacji #128 do #104 w ciemno. Jego lokalne wyniki i testy mogą służyć wyłącznie jako materiał porównawczy.

---

## 13. Co ma zrobić następny agent

### Start

1. Przeczytać `AGENTS.md`.
2. Otworzyć draft PR #104.
3. Potwierdzić:
   - target repository: `blakinio/canary`;
   - base: `main`;
   - head repository: `blakinio/canary`;
   - head: `feat/otbm-script-resolution-audit`;
   - upstream target: `NO`.
4. Sprawdzić aktualny head PR i aktualny SHA `main`.
5. Sprawdzić changed-files — dozwolone są tylko sześć plików resolvera oraz ten handoff.
6. Sprawdzić wszystkie workflow na najnowszym headzie.

### Finalny baseline

1. Uzyskać mapę o SHA-256 `a80de1...da2`.
2. Wygenerować świeży item audit wymagany przez CLI #104.
3. Uruchomić resolver z:
   - aktywnymi rootami `data` i `data-otservbr-global`;
   - `OTBM_SCRIPT_REVIEW_RULES.json`;
   - normalnym trybem;
   - osobno `--strict-runtime`.
4. Zweryfikować JSON według schema.
5. Zapisać:
   - dokładny head SHA;
   - hash mapy;
   - hash input audit;
   - hash finalnego raportu;
   - pełne liczniki.
6. Zaktualizować ten dokument.

### Ręczna klasyfikacja 151 ID

Dla każdego ID:

1. pogrupować po namespace, wartości, item ID, pozycji, piętrze i sąsiedztwie;
2. sprawdzić aktywne skrypty;
3. sprawdzić upstream i legacy wyłącznie jako referencję;
4. ustalić rzeczywistą funkcję obszaru;
5. zmienić `needs-manual-review` na:
   - `intentional-marker`,
   - `legacy-unused`,
   - `missing-script`,
   - albo pozostawić `needs-manual-review` z uzasadnieniem;
6. dla `missing-script` przygotować osobny issue lub PR;
7. nie zmieniać mapy przed ustaleniem znaczenia ID.

### Domknięcie PR #104

PR można oznaczyć jako gotowy dopiero, gdy:

- gałąź nie jest za `main`;
- wszystkie workflow są zielone;
- finalny raport pochodzi z dokładnego checkoutu PR #104;
- schema i review rules przechodzą walidację;
- changed-files nie zawierają zakazanych ścieżek;
- dynamiczne rejestracje pozostają jawne;
- ten dokument ma aktualne SHA i liczniki.

Nie merge’ować automatycznie. Merge wymaga osobnej, wyraźnej zgody użytkownika.

---

## 14. Późniejszy etap — rekonstrukcja świata

Rekonstrukcję brakujących regionów rozpocząć dopiero po audycie mechaniki.

Dla każdego pilotowego regionu:

1. wybrać mały i ograniczony obszar;
2. przypiąć hash mapy źródłowej;
3. przygotować patch do nowego pliku;
4. zweryfikować itemy, town, house, zone, spawn, NPC, teleport i quest;
5. uruchomić inspect, verify, diff, item audit i script resolver;
6. wczytać mapę przez Canary;
7. wyrenderować region przed/po z prawdziwych assetów;
8. zachować rollback.

---

## 15. Definicja ukończenia etapu audytu mapy

- [x] parser i narzędzia OTBM istnieją w repo;
- [x] pełny item audit mapy został wykonany;
- [x] produkcyjny resolver, CLI, schema, dokumentacja i testy istnieją w PR #104;
- [x] wszystkie 151 runtime-unresolved ID mają bezpieczną dyspozycję `needs-manual-review`;
- [x] konfliktów placements: 0;
- [x] gałąź #104 została przebudowana na aktualnym `main` podczas tej sesji;
- [ ] CI najnowszego headu #104 jest w pełni zielone;
- [ ] finalny raport został wygenerowany dokładnym checkoutem #104 po ostatnim rebase;
- [ ] wszystkie 151 ID mają docelową ręczną klasyfikację;
- [ ] item 2141 został poprawiony w kopii mapy albo świadomie odroczony;
- [ ] poprawiona mapa przechodzi loader Canary i ponowny item audit;
- [ ] użytkownik zatwierdził merge PR #104.

---

## 16. Changelog

### 2026-07-12 — kanoniczny resolver i przekazanie sesji

- wykonano pełny odczyt mapy i audyt 23,359,571 umieszczeń itemów;
- zbudowano produkcyjny, tylko-do-odczytu resolver handlerów;
- dodano CLI, schema, dokumentację, testy i review rules;
- wykonano pełny audyt 9,339 mechanik mapowych;
- runtime rozwiązano 8,964 placements;
- zachowano 375 runtime-unresolved/partial placements do dalszej analizy;
- 151 ID otrzymało bezpieczną dyspozycję `needs-manual-review`;
- wykryto 0 konfliktów placements;
- lokalne testy i walidacje przeszły;
- wybrano PR #104 jako kanoniczny;
- PR #128 oznaczono jako duplikat do zamknięcia bez merge;
- przebudowano gałąź #104 na `main` o SHA `1389489aa369fb6218aaab6e79224247cb9b64ef`;
- nie zmodyfikowano ani nie commitowano mapy, assetów, `items.otb`, aktywnego datapacka ani konfiguracji produkcyjnej.

### Szablon kolejnego wpisu

```markdown
### YYYY-MM-DD — nazwa etapu

- base i head SHA:
- PR:
- wykonane:
- testy i CI:
- wyniki audytu:
- artefakty i SHA-256:
- otwarte blokery:
- następny krok:
```
