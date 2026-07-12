# OTS AI Achievement Validation — cel, metodologia, stan i handoff

> **Stan dokumentu:** 2026-07-12  
> **Projekt nadrzędny:** `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`  
> **Repozytorium zapisywalne:** `blakinio/canary`  
> **Gałąź / PR audytu:** `feat/achievement-validation-audit`, `#165`  
> **Aktualny etap:** statyczny audyt rejestru i aktywnych triggerów ukończony; następne są małe fixy i walidacja semantyczna/runtime  
> **Najważniejsza zasada:** brak literalnego `addAchievement` nie jest dowodem, że achievement jest nieosiągalny.

---

## 1. Cel

Projekt ma odpowiedzieć osobno na cztery pytania:

1. Czy achievement jest poprawnie zdefiniowany?
2. Czy aktywny kod ma ścieżkę, która może go przyznać albo inkrementować?
3. Czy zależności gameplay tej ścieżki są spójne?
4. Czy testowa postać faktycznie może zdobyć achievement i zachować go po relogu/restarcie?

Definicja, statyczna referencja, semantycznie poprawny trigger i działający runtime są czterema oddzielnymi poziomami dowodu.

---

## 2. Źródła prawdy

### Canary

```text
data/scripts/lib/register_achievements.lua
data/
data-otservbr-global/
src/creatures/players/components/player_achievement.{hpp,cpp}
src/game/game.cpp
src/lua/functions/core/game/game_functions.cpp
```

### Referencja

```text
https://tibia.fandom.com/wiki/Achievements
```

Versioned snapshot:

```text
docs/ai-agent/ACHIEVEMENT_REFERENCE_BASELINE.json
```

Stan 2026-07-12:

- 562 odkryte / wymienione achievementy;
- 563 łącznie;
- 362 common;
- 200 odkrytych secret z 201 łącznie;
- 1470 punktów teoretycznie;
- 1425 po wykluczeniu wzajemnie wykluczających się wpisów.

Wiki jest źródłem porównawczym, nie automatyczną zgodą na zmianę Canary. Każda różnica musi zostać skorelowana z aktualnym contentem i runtime.

---

## 3. Narzędzie

```text
tools/ai-agent/achievement_validation.py
tools/ai-agent/test_achievement_validation.py
.github/workflows/achievement-validation.yml
```

Format raportu:

```text
canary-achievement-audit-v1
```

CLI:

```bash
python tools/ai-agent/achievement_validation.py \
  --repository-root . \
  --reference-baseline docs/ai-agent/ACHIEVEMENT_REFERENCE_BASELINE.json \
  --output artifacts/ACHIEVEMENT_AUDIT.json \
  --markdown artifacts/ACHIEVEMENT_AUDIT.md \
  --allow-findings
```

Narzędzie:

- parsuje jawne rekordy `[id] = { ... }`;
- wykrywa brakujące pola, błędne typy, duplikaty ID/nazw, kolejność i luki;
- waliduje grade/points z jawnym zero-point wyjątkiem informacyjnym;
- wykrywa błędne helpery rejestru;
- skanuje oba aktywne datapacki;
- rozpoznaje `addAchievement`, `addAchievementProgress`, `hasAchievement`, `removeAchievement`, bulk add/remove;
- odróżnia literalne ID/nazwy od argumentów dynamicznych;
- oddziela GOD/admin od normalnego gameplay;
- rozwiązuje statyczne referencje wobec aktywnego rejestru;
- generuje per-achievement dyspozycje;
- porównuje count/common/secret/points z baseline;
- publikuje pełny JSON jako artefakt CI.

---

## 4. Dyspozycje

- `direct-static-award` — aktywny literalny award;
- `static-progress-path` — aktywny literalny progress;
- `referenced-without-static-award` — check/remove bez literalnego awardu;
- `admin-only-static-reference` — wyłącznie ścieżka administracyjna;
- `no-direct-static-reference` — brak literalnej referencji;
- `needs-semantic-or-runtime-review` — dynamiczny albo pośredni przypadek wymagający dalszych dowodów;
- `confirmed-broken-static-trigger` — aktywna literalna nazwa/ID nie rozwiązuje się;
- `confirmed-infrastructure-defect` — helper/rejestracja ma potwierdzony błąd niezależny od konkretnego questa;
- `reference-entry-not-implemented` — wpis istnieje w bieżącej referencji, lecz nie w rejestrze Canary; nie oznacza automatycznej gotowości contentu.

---

## 5. Zweryfikowany baseline Canary

Pełny skan workflow na commit:

```text
8642fdfa78d83bd41b6948ddf6aee10593cfcdbe
```

Wynik:

```text
registry definitions: 541
ID range: 1..570
ID gaps: 29
public: 350
secret: 191
points: 1428
API references: 182
resolved static references: 160
unknown static references: 2
dynamic references: 22
admin references: 3
```

Trigger coverage:

```text
direct-static-award: 87
static-progress-path: 32
referenced-without-static-award: 1
no-direct-static-reference: 421
```

`421` nie oznacza 421 błędów. To kolejka do bezpiecznej analizy tabel, wrapperów, questów i runtime.

---

## 6. Potwierdzone findings

### 6.1. Rzadka tabela + `#ACHIEVEMENTS`

Rejestr ma luki, ale helper używa operatora długości jako granicy. Wysokie ID mogą zostać zarejestrowane przez `pairs`, a pominięte przez helper iterujący `1..#ACHIEVEMENTS`.

Dyspozycja: `confirmed-infrastructure-defect`.

### 6.2. `Game.isAchievementSecret`

Helper:

- wyszukuje `foundAchievement`, ale zwraca `achievement.secret` z argumentu;
- w invalid path używa niezdefiniowanej zmiennej `ach`.

Dyspozycja: `confirmed-infrastructure-defect`.

### 6.3. `You got Horse Power`

```text
data/scripts/actions/items/usable_phantasmal_jade_items.lua:36
trigger: You got Horse Power
registry: ID 514, You Got Horse Power
```

C++ wykonuje dokładny `std::map::find(name)`, więc różnica wielkości litery blokuje award.

Dyspozycja: `confirmed-broken-static-trigger`.

### 6.4. `The Professors Nut`

```text
data-otservbr-global/scripts/quests/hero_of_rathleton/actions_reward.lua:9
trigger: The Professors Nut
registry: ID 360, The Professor's Nut
```

Brak apostrofu i formy dzierżawczej blokuje lookup.

Dyspozycja: `confirmed-broken-static-trigger`.

### 6.5. Persistence po nazwie

Unlocked KV jest kluczowane nazwą achievementu. Rename może osierocić dane gracza, dlatego błędne call sites należy poprawić do kanonicznych nazw zamiast zmieniać nazwy rejestru.

---

## 7. Braki względem bieżącej referencji

Canary ma 541 definicji wobec 562 odkrytych wpisów referencyjnych. Ręcznie potwierdzono 21 nieobecnych ID/nazw:

```text
550 A Friend in Need
551 Holzkopf
567 The Forbidden Build
572 Errand Runner
573 Workhorse
574 Taskaholic
575 Pest Control
576 Mimic
577 Bastard
578 Razor's Edge
579 Lost Letters
580 Stagmeister
581 Feral Trapper
582 Castle Crasher
585 A reliable Friend
586 Echo Initiate
587 Echo Hunter
588 Echo Walker
592 Six Steps Ahead
593 Radiant Nimbus
594 Amati's Echo
```

Szczegóły i daty są zapisane w baseline JSON oraz w:

```text
docs/ai-agent/ACHIEVEMENT_VALIDATION_REPORT.md
```

Nie wolno masowo dodawać tych wpisów bez potwierdzenia odpowiadającego contentu. ID `550`, `551` i `567` są szczególnie ważne, ponieważ nie są wyłącznie przyszłymi ID ponad obecnym maksimum rejestru.

---

## 8. Runtime plan

```text
docs/ai-agent/ACHIEVEMENT_RUNTIME_TEST_PLAN.json
```

Obejmuje:

- pełną rejestrację wszystkich jawnych ID;
- enumerację wysokich ID po lukach;
- lookup public/secret po ID i nazwie;
- invalid lookup;
- idempotencję award/remove i punkty;
- persistence/reload;
- progress threshold;
- bulk admin add/remove;
- reprezentatywne E2E dla NPC, questów, bossów, movement, item-use, progress i secret achievements.

---

## 9. CI i artefakty

Na audytowanym headzie:

```text
Achievement Validation run 29202931191: success
AI Agent Tools run 29202931162: success
CI run 29202931226: success
focused tests: 8/8
artifact: achievement-validation-audit
artifact id: 8262907252
artifact sha256: 4e127d6c708b6422f520f5833394b652331addcbf989f345523f9d31b9171baa
```

Pełny raport per-achievement pozostaje artefaktem CI. Do Git trafiają tylko narzędzie, testy, mały evidence report, baseline i runtime plan.

---

## 10. Bezpieczeństwo

Audytowy PR nie modyfikuje:

- aktywnego rejestru achievementów;
- questów, NPC, actions, movements ani creature events;
- C++ runtime;
- `.otbm`, `items.otb`, assetów ani produkcyjnej konfiguracji.

Każdy gameplay/infrastructure fix musi mieć osobny task, branch, PR i focused testy.

---

## 11. Kolejność dalszej pracy

1. Naprawić helpery `#ACHIEVEMENTS` i `Game.isAchievementSecret` w osobnym PR.
2. Naprawić dwa literalne triggery w osobnym PR.
3. Rozszerzyć skaner o bezpieczne resolvery wybranych dynamicznych tabel.
4. Walidować istniejące achievementy grupami systemowymi.
5. Osobno przeanalizować ID `550`, `551`, `567`.
6. Osobno przeanalizować Winter Update 2025 `572..581`.
7. Osobno przeanalizować Spring/Summer 2026 `582`, `585..588`, `592..594`.
8. Uruchamiać małe scenariusze runtime/E2E przed zmianą produkcyjnego rejestru.

---

## 12. Handoff

### Zacznij od

1. `AGENTS.md`;
2. `docs/agents/ACTIVE_WORK.md`;
3. `docs/agents/MODULE_CATALOG.md`;
4. tego dokumentu;
5. `ACHIEVEMENT_VALIDATION_REPORT.md`;
6. aktywnego task recordu i aktualnych PR-ów;
7. najnowszego artefaktu workflow.

### Nie powtarzaj

- nie licz wpisów przez najwyższy ID;
- nie używaj `#ACHIEVEMENTS` jako liczby rekordów;
- nie uznawaj `no-direct-static-reference` za brak mechaniki;
- nie mieszaj GOD commands z gameplay;
- nie zmieniaj kanonicznych nazw bez planu migracji KV;
- nie dopisuj brakujących ID wyłącznie na podstawie wiki;
- nie commituj pełnego wygenerowanego raportu;
- nie mieszaj helper fixów, typo triggerów i nowych content definitions w jednym PR.

### Trwałe pliki

```text
docs/ai-agent/OTS_AI_ACHIEVEMENT_VALIDATION_PROJECT.md
docs/ai-agent/ACHIEVEMENT_VALIDATION_REPORT.md
docs/ai-agent/ACHIEVEMENT_REFERENCE_BASELINE.json
docs/ai-agent/ACHIEVEMENT_RUNTIME_TEST_PLAN.json
tools/ai-agent/achievement_validation.py
tools/ai-agent/test_achievement_validation.py
.github/workflows/achievement-validation.yml
docs/agents/tasks/active/CAN-20260712-achievement-validation.md
```

---

## 13. Changelog

### 2026-07-12 — pełny statyczny audyt

- uruchomiono skan obu aktywnych datapacków;
- zapisano 541 definicji, 182 wywołania API i 22 dynamiczne referencje;
- wykryto dwa nierozwiązywalne statyczne triggery;
- potwierdzono trzy findings helperów;
- porównano aggregate metadata z bieżącą referencją;
- zapisano 21 brakujących referencyjnych wpisów;
- dodano evidence report, runtime plan, focused tests i CI artifact;
- wszystkie wymagane workflow na audytowanym headzie zakończyły się sukcesem.
