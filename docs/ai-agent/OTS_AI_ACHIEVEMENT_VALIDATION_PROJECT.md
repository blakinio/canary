# OTS AI Achievement Validation — projekt v2

> **Stan dokumentu:** 2026-07-13  
> **Repozytorium:** `blakinio/canary`  
> **Gałąź / PR:** `feat/achievements-comprehensive-validation`, draft `#238`  
> **Formaty:** `canary-achievement-reference-catalog-v1`, `canary-achievement-audit-v2`, `canary-achievement-reviewed-evidence-v1`  
> **Zasada nadrzędna:** definicja ani literalna referencja nie są dowodem osiągalności achievementu.

## Cel

Projekt tworzy powtarzalną, evidence-based walidację każdego achievementu z bieżącej tabeli TibiaWiki/Fandom. Dla każdego wpisu rozdziela:

1. definicję w rejestrze Canary;
2. fakty referencyjne i klasę warunku;
3. statyczne lub reviewed ścieżki award/progress/check/remove;
4. persistence i wymagania backfill;
5. osiągalność dla obecnych i nowych graczy;
6. rejestrację runtime oraz testy;
7. końcowy konserwatywny status.

Dozwolone statusy:

```text
confirmed
partially-confirmed
definition-only
handler-missing
unresolved
conflicting
intentionally-unsupported
```

`unresolved` jest poprawnym wynikiem, gdy dowód jest niewystarczający. Nie wolno go promować przez zgadywanie dynamicznego Lua, pośrednich ścieżek C++ ani same istnienie wpisu na wiki.

## Źródła

### Canary

```text
data/scripts/lib/register_achievements.lua
data/
data-otservbr-global/
src/creatures/players/components/player_achievement.{hpp,cpp}
src/game/game.cpp
src/lua/functions/core/game/game_functions.cpp
```

### Referencja zewnętrzna

```text
page: https://tibia.fandom.com/wiki/Achievements
retrieval: https://tibia.fandom.com/api.php?action=parse&page=Achievements&prop=text%7Crevid&format=json&formatversion=2
page ID: 49280
revision ID: 1188274
observed: 2026-07-13
source bytes: 1,026,270
source SHA-256: 8a429425ab7b088758646b07f036afdd1d579188d056491aed8e77650306ae8b
```

Surowy payload i długie opisy/spoilery nie są commitowane. Repo przechowuje fakty, linki encji, klasy warunków, liczby, hashe oraz długości tekstu.

## Trwałe pliki

```text
tools/ai-agent/achievement_validation.py
tools/ai-agent/test_achievement_validation.py
.github/workflows/achievement-validation.yml
docs/ai-agent/ACHIEVEMENT_REFERENCE_BASELINE.json
docs/ai-agent/ACHIEVEMENT_REFERENCE_CATALOG.json
docs/ai-agent/ACHIEVEMENT_REVIEWED_EVIDENCE.json
docs/ai-agent/ACHIEVEMENT_COMPREHENSIVE_VALIDATION.md
docs/ai-agent/ACHIEVEMENT_VALIDATION_REPORT.md
docs/ai-agent/ACHIEVEMENT_RUNTIME_TEST_PLAN.json
```

Pełna tabela 564 wierszy, metodologia, per-row evidence i plan napraw znajdują się w `ACHIEVEMENT_COMPREHENSIVE_VALIDATION.md` oraz w artefakcie workflow.

## Aktualny baseline

### Referencja

```text
listed/discovered: 564
total including undiscovered secret: 565
common: 363
secret discovered/total: 201/202
known theoretical points: 1475
maximum excluding coinciding: 1430
unknown point rows: 5
conditions available/unavailable: 558/6
ID range/gaps: 1..595 / 31
```

### Canary

```text
definitions: 541
public/secret: 350/191
points: 1428
ID range/gaps: 1..570 / 29
```

### Pełny skan aktywnych datapacków

```text
API references: 182
resolved static references: 160
unknown static references: 0
dynamic references: 22
admin references: 2
direct-static-award definitions: 89
static-progress-path definitions: 32
referenced-without-static-award definitions: 1
no-direct-static-reference definitions: 419
```

### Statusy v2

```text
confirmed: 0
partially-confirmed: 121
definition-only: 0
handler-missing: 3
unresolved: 409
conflicting: 31
intentionally-unsupported: 0
```

Brak `confirmed` jest celowy: statyczny skan nie dowodzi jednocześnie reachability, persistence/backfill i runtime/E2E.

## Potwierdzone różnice

- 24 wpisy bieżącej referencji nie mają definicji w Canary;
- 7 istniejących definicji różni się grade/secret/points;
- pięć bieżących wpisów ma nieznane punkty, a sześć nie ma dostępnego warunku źródłowego;
- ID 564–566 mają definicje, ale reviewed audit nie znalazł award hooków;
- ID 567 ma zweryfikowany kontrakt dwunastu itemów/proficiency, lecz brak definicji, awardu i backfillu;
- persistence jest kluczowane kanoniczną nazwą, więc rename wymaga migracji lub aliasu.

Nie jest to zgoda na automatyczne zmiany gameplayu.

## Metodologia

Validator v2:

- zachowuje parser i legacy rows z v1;
- parsuje commitowany factual reference catalogue;
- łączy referencję z definicjami po ID i nazwie;
- zapisuje dokładne path/line dla definicji oraz statycznych API references;
- oddziela gameplay od GOD/admin;
- pozostawia dynamiczne argumenty nierozwiązane;
- pozwala na silniejsze statusy tylko przez versioned reviewed evidence;
- zapisuje persistence/backfill, attainability, registration i test evidence osobno;
- publikuje JSON i Markdown w dedykowanym workflow.

## Walidacja

Zweryfikowany implementation head:

```text
commit: 741c0c40593c894c97212977485f073d8c2e52bb
Achievement Validation run: 29237298141 (success)
artifact: 8273938137
artifact digest: sha256:3a36eec8d0eebb87010a5b12309ab5f2d8015160cbb6f0be7b2b497ba032c140
AI Agent Tools run: 29237298034 (success)
Agent Task Ownership run: 29237298047 (success)
focused tests: 13/13
```

Finalny current-head CI musi zostać powtórzony po rebase/refresh i aktualizacji dokumentów.

## Granica audytu i napraw

Ten PR nie zmienia:

- aktywnego rejestru;
- Lua/C++ gameplayu;
- questów, NPC, bossów, actions ani movements;
- KV lub schematu bazy;
- map, `items.otb`, assetów i konfiguracji produkcyjnej.

Kolejne prace muszą być małymi PR-ami rozdzielającymi:

1. metadata conflicts;
2. missing definitions z pełnym content proof;
3. dynamic resolvers;
4. award/progress handlers;
5. existing-player backfill;
6. runtime/E2E i denied-path tests.

## Handoff

Najpierw przeczytaj:

1. aktywny task `CAN-20260713-achievements-validation.md`;
2. `ACHIEVEMENT_COMPREHENSIVE_VALIDATION.md`;
3. `ACHIEVEMENT_REFERENCE_CATALOG.json`;
4. `ACHIEVEMENT_REVIEWED_EVIDENCE.json`;
5. najnowszy artefakt `Achievement Validation`.

Nie powtarzaj parsera rejestru ani skanera API. Nie edytuj ręcznie `ACTIVE_WORK.md`. Nie traktuj `no-direct-static-reference` jako błędu. Nie zmieniaj kanonicznych nazw bez analizy name-keyed KV.
