# OTS / Canary — handoff projektu OTBM, TibiaMaps, assetów i audytu mechaniki

> **Stan dokumentu:** 2026-07-12 — finalne przekazanie bieżącej sesji  
> **Repozytorium:** `blakinio/canary`  
> **Resolver handlerów:** scalony w PR [#104](https://github.com/blakinio/canary/pull/104)  
> **Merge SHA resolvera:** `0b355669ebe66c9d9c604c2a9221f47280699581`  
> **PR aktualizujący ten handoff:** gałąź `docs/otbm-final-handoff-20260712`

---

## 1. Cel projektu

Projekt ma stworzyć bezpieczny i powtarzalny proces pozwalający:

1. analizować duże mapy OTBM bez ładowania całego świata do pamięci;
2. porównywać mapę serwera z TibiaMaps i innymi wersjonowanymi referencjami;
3. wykrywać brakujące regiony, różnice przechodniości i obszary customowe;
4. sprawdzać zgodność itemów z `appearances.dat`, assetami klienta i `items.xml`;
5. zachować mechanikę mapy: `actionId`, `uniqueId`, teleporty, domy, kontenery, questy i skrypty;
6. przygotowywać odwracalne, przypięte hashem patche bez nadpisywania mapy źródłowej;
7. walidować każdy patch przez parser OTBM, prawdziwy loader Canary, audyty i CI.

### Cel końcowy

Powinna powstać zwalidowana mapa wynikowa oparta na dostarczonym OTBM, uzupełniana etapami o brakujące obszary bez utraty customowej zawartości i bez uszkodzenia questów, teleportów, domów, spawnów lub skryptów.

---

## 2. Zasady bezwzględne

- Nie nadpisywać źródłowego OTBM.
- Nie commitować `.otbm`, `items.otb`, `appearances.dat`, sprite-sheetów, assetów klienta ani pełnych danych TibiaMaps.
- Nie pushować bezpośrednio do `main`.
- Nie usuwać `actionId` lub `uniqueId` tylko dlatego, że statyczny resolver nie znalazł handlera.
- Nie traktować pól OTBM-only jako automatycznego błędu.
- Nie zgadywać brakujących itemów, potworów, NPC ani funkcji obszaru.
- Nie rekonstruować dużych regionów przed zakończeniem audytu mechaniki.
- Każdy patch mapy musi mieć hash źródła, dry-run, diff, walidację i możliwość cofnięcia.
- Repozytoria `opentibiabr/*` traktować jako referencyjne i tylko do odczytu.

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
lokalna ścieżka w tej sesji: /mnt/data/otservbr.otbm
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

## 5. Assety i referencja TibiaMaps

Poprzednie audyty używały paczki oficjalnego klienta:

```text
wersja: 15.25.bd5a04
appearance objects: 42,107
```

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
- PR #91 — test ładowania wygenerowanego OTBM przez prawdziwy loader C++ Canary.

### Assety i render

- PR #93 — indeks paczek assetów OTClient/RME.
- PR #94 — parser protobuf `appearances.dat`.
- PR #95 — dekoder CIP/raw-LZMA sprite-sheetów.
- PR #96 — deterministyczny renderer regionów OTBM.
- PR #98 — obsługa realnych nagłówków CIP i zredukowanych paczek.

### Porównanie i audyt

- PR #100 — porównanie OTBM z TibiaMaps i komponenty brakujących regionów.
- PR #101 — pełny audyt itemów i mechanik mapowych.
- PR #104 — produkcyjny resolver handlerów skryptowych OTBM.

---

## 7. Resolver handlerów — stan ukończony

PR #104 został scalony do `main` jako:

```text
merge SHA: 0b355669ebe66c9d9c604c2a9221f47280699581
```

Scalone pliki:

```text
tools/ai-agent/otbm_script_resolution.py
tools/ai-agent/otbm_script_resolution_tool.py
tools/ai-agent/test_otbm_script_resolution.py
docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md
docs/ai-agent/OTBM_SCRIPT_RESOLUTION_REPORT.schema.json
docs/ai-agent/OTBM_SCRIPT_REVIEW_RULES.json
```

### Domyślnie aktywne datapacki

```text
data
data-otservbr-global
```

`data-canary` nie jest automatycznie mieszany z aktywnym contentem.

### Obsługiwane wzorce

- `Action()` i `MoveEvent()`;
- `:aid(...)`, `:uid(...)`, `:id(...)`, `:position(...)`;
- listy i numeryczne zakresy;
- numeryczne pętle `for`;
- `pairs()` i `ipairs()` po statycznych tabelach;
- rejestracje XML actions i movements;
- porównania `target.actionid` i `target.uid`;
- lookupy typu `config[target.actionid]`;
- ograniczone target ranges;
- item-ID fallback dla drzwi i kluczy z `items.xml`;
- fallback quest chest, w tym `actionId 2000`;
- teleport destination i house-door ID jako mechanika silnika.

### Runtime kontra review disposition

Resolver osobno odpowiada na dwa pytania:

1. **Runtime resolution** — czy istnieje dowód, że Canary wykona mechanikę?
2. **Review disposition** — czy nierozwiązane ID zostało jawnie zaklasyfikowane do zachowania i dalszej analizy?

Reguła review nigdy nie zmienia `unresolved` na fałszywe `handled`.

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

---

## 8. Finalny audyt dokładnego kodu z PR #104

Dokładny checkout kodu scalonego w #104 został wyeksportowany przez tymczasowy workflow, pobrany lokalnie i uruchomiony z dostarczoną mapą.

### Item audit

```text
kafle: 17,972,761
umieszczenia: 23,359,571
unikalne item ID: 23,852
mechaniki: 9,339
missing appearance IDs: 1
missing appearance placements: 1
nieznane ogony atrybutów: 0
```

### Resolver

```text
pliki Lua/XML: 5,384
rejestracje runtime: 1,182
reguły target/reference: 266
mechaniki mapowe: 9,339
runtime-resolved placements: 8,964
runtime unresolved/partial placements: 375
konflikty placements: 0
action IDs: 697
unique IDs: 587
runtime unresolved/partial identifiers: 151
identyfikatory bez review disposition: 0
dynamiczne rejestracje zachowane jako ostrzeżenia: 253
raport domyślny: ok = true
strictRuntimeOk: false
strict-runtime exit code: 2
```

Statusy identyfikatorów:

```text
handled-as-target: 79
handled-by-action-id: 15
handled-by-fallback: 41
handled-by-item-id: 251
handled-by-range: 56
handled-directly: 676
handled-generically: 13
handled-multiple: 2
partially-resolved: 2
unresolved: 149
```

Statusy placements:

```text
handled-as-target: 437
handled-by-engine: 6,707
handled-by-item-id: 194
handled-by-range: 56
handled-directly: 1,064
handled-generically: 13
handled-multiple: 493
partially-resolved: 19
unresolved: 356
```

### Walidacja

- Python modules compile: PASS.
- Focused resolver tests: 4/4 PASS.
- OTBM Map Tools CI: PASS.
- AI Agent Tools CI: PASS.
- Full repository CI na scalonym headzie PR #104: PASS.
- Raport przechodzi JSON Schema Draft 2020-12.
- Tryb `--strict-runtime` poprawnie zwraca kod `2`.

---

## 9. Artefakty finalnego audytu

```text
/mnt/data/PR104_APPEARANCES_INDEX.json
SHA-256: 213bcc708ff6017eef0bf102f68172ba85f18456efea579555e3c3dfe40dcdd7

/mnt/data/PR104_OTBM_ITEM_SCAN.json
SHA-256: d6c28d476a5e9f12830f4d754744003d7c4addfb702a551354df7788c31d83e6

/mnt/data/PR104_OTBM_ITEM_AUDIT.json
SHA-256: 34ff0cc78c6ef0ffc5003da5c5d59bcef7d992bab2ee638f8d96dfad866d1a17

/mnt/data/PR104_OTBM_SCRIPT_RESOLUTION.json
SHA-256: d5de1dea6154d8dea7ede7a30679f93df7eb70dfaa61f07a674aecbe6016bd33

/mnt/data/PR104_OTBM_SCRIPT_RESOLUTION_STRICT.json
SHA-256: d5de1dea6154d8dea7ede7a30679f93df7eb70dfaa61f07a674aecbe6016bd33
```

Ścieżki `/mnt/data` nie są trwałe między sesjami. Raport normalny i strict mają identyczną treść; `--strict-runtime` zmienia kod wyjścia, nie dokument JSON.

---

## 10. Największe grupy do ręcznej analizy

Największe zachowane grupy:

```text
actionId 26002
actionId 50058..50088
actionId 48000..48006
actionId 2090..2096
uniqueId 62133
uniqueId 62135
```

Każdy z 151 identyfikatorów należy docelowo sklasyfikować jako:

```text
intentional-marker
legacy-unused
missing-script
needs-manual-review
preserve-until-reviewed
```

Nie wolno pisać brakującego skryptu ani usuwać atrybutu mapy bez ustalenia rzeczywistej funkcji obszaru.

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

Przed zamknięciem przypadku należy:

1. wykonać patch wyłącznie do nowej kopii mapy;
2. uruchomić inspect i verify;
3. sprawdzić semantyczny diff ograniczony do pozycji `33572,32528,14`;
4. wczytać wynik przez prawdziwy loader C++ Canary;
5. ponownie uruchomić audyt itemów;
6. potwierdzić `missingAppearanceIds = 0`;
7. zachować kopię źródła i możliwość cofnięcia.

---

## 12. Zamknięte PR-y operacyjne i duplikaty

- PR #128 — równoległy, mniej kompletny resolver; zamknięty bez merge jako duplikat #104.
- PR #129 — tymczasowy eksport dokładnego źródła #104; zamknięty bez merge po pobraniu artefaktu.

Nie wznawiać tych PR-ów.

---

## 13. Co ma zrobić następny agent

### Start

1. Przeczytać `AGENTS.md`.
2. Potwierdzić, że `main` zawiera merge SHA `0b355669...` lub jego potomka.
3. Otworzyć ten dokument i dokumentację `OTBM_SCRIPT_RESOLUTION.md`.
4. Sprawdzić dostępność mapy oraz jej SHA-256.
5. Nie odtwarzać resolvera — jest już w `main`.

### Priorytet P0 — klasyfikacja 151 ID

1. Wczytać `PR104_OTBM_SCRIPT_RESOLUTION.json` albo wygenerować go ponownie.
2. Pogrupować ID po namespace, wartości, item ID, pozycji, piętrze i sąsiedztwie.
3. Sprawdzić aktywne skrypty.
4. Sprawdzić upstream i legacy wyłącznie jako referencję.
5. Ustalić rzeczywistą funkcję obszaru.
6. Aktualizować `OTBM_SCRIPT_REVIEW_RULES.json` małymi, udokumentowanymi partiami.
7. Dla `missing-script` przygotować osobny issue lub PR.
8. Nie zmieniać mapy przed ustaleniem znaczenia ID.

### Priorytet P1 — item 2141

1. Przygotować patch do kopii mapy.
2. Wykonać inspect, verify i semantic diff.
3. Uruchomić loader Canary.
4. Ponowić item audit.
5. Potwierdzić zero brakujących appearance.

### Priorytet P2 — rekonstrukcja brakujących regionów

Dopiero po klasyfikacji mechanik:

1. wybrać mały pilotowy obszar;
2. przypiąć hash mapy źródłowej;
3. przygotować patch do nowego pliku;
4. zweryfikować itemy, town, house, zone, spawn, NPC, teleport i quest;
5. uruchomić inspect, verify, diff, item audit i script resolver;
6. wczytać mapę przez Canary;
7. wyrenderować region przed/po z prawdziwych assetów;
8. zachować rollback.

---

## 14. Definicja ukończenia etapu audytu mapy

- [x] parser i narzędzia OTBM istnieją w repo.
- [x] pełny item audit mapy został wykonany.
- [x] produkcyjny resolver, CLI, schema, dokumentacja, tests i review rules są w `main`.
- [x] finalny raport został wygenerowany dokładnym kodem PR #104.
- [x] wszystkie 151 runtime-unresolved ID mają bezpieczną dyspozycję `needs-manual-review`.
- [x] konfliktów placements: 0.
- [x] CI resolvera jest zielone.
- [ ] wszystkie 151 ID mają docelową ręczną klasyfikację.
- [ ] item 2141 został poprawiony w kopii mapy albo świadomie odroczony.
- [ ] poprawiona mapa przechodzi loader Canary i ponowny item audit.
- [ ] rozpoczęto kontrolowaną rekonstrukcję pierwszego regionu.

---

## 15. Changelog

### 2026-07-12 — zakończenie resolvera i finalny baseline

- przeprowadzono pełny odczyt mapy i audyt 23,359,571 umieszczeń itemów;
- scalono produkcyjny resolver handlerów w PR #104;
- dodano CLI, schema, dokumentację, testy i review rules;
- wygenerowano raport dokładnym kodem scalonego resolvera;
- runtime rozwiązano 8,964 z 9,339 placements;
- zachowano 375 unresolved/partial placements do dalszej analizy;
- 151 ID otrzymało bezpieczną dyspozycję `needs-manual-review`;
- wykryto 0 konfliktów placements;
- potwierdzono `ok = true` i `strictRuntimeOk = false`;
- potwierdzono kod wyjścia `2` dla `--strict-runtime`;
- zamknięto duplikat #128 i operacyjny PR #129 bez merge;
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
