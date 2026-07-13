# Canary achievements — comprehensive evidence report v2

## Decyzja

```text
status: comprehensive-static-audit-complete
runtimeE2EProvenForAllRows: false
referenceRevision: 1188274
referenceRows: 564
referenceTotal: 565
registryDefinitions: 541
activeApiReferences: 182
resolvedStaticReferences: 160
unknownStaticReferences: 0
dynamicReferences: 22
```

Audyt objął każdy wiersz bieżącej tabeli TibiaWiki/Fandom i każdy aktywny wpis rejestru Canary. Wynik jest kompletny jako katalog i klasyfikacja dowodowa, ale nie dowodzi pełnej osiągalności runtime wszystkich achievementów.

Pełna tabela, warunki, exact path/line evidence, persistence/backfill, attainability, test gaps i plan napraw:

```text
docs/ai-agent/ACHIEVEMENT_COMPREHENSIVE_VALIDATION.md
docs/ai-agent/ACHIEVEMENT_REFERENCE_CATALOG.json
docs/ai-agent/ACHIEVEMENT_REVIEWED_EVIDENCE.json
docs/ai-agent/ACHIEVEMENT_RUNTIME_TEST_PLAN.json
```

## Źródło referencyjne

```text
page: https://tibia.fandom.com/wiki/Achievements
MediaWiki revision: 1188274
observed: 2026-07-13
source SHA-256: 8a429425ab7b088758646b07f036afdd1d579188d056491aed8e77650306ae8b
```

Aktualna rewizja zawiera:

| Wymiar | Wartość |
|---|---:|
| listed/discovered | 564 |
| total incl. undiscovered secret | 565 |
| common | 363 |
| secret discovered/total | 201/202 |
| known theoretical points | 1475 |
| maximum excluding coinciding | 1430 |
| unknown point rows | 5 |
| available/unavailable conditions | 558/6 |

Wcześniejsze 562/563 było wynikiem starszego cache/renderu i nie jest aktualnym baseline.

## Canary

| Wymiar | Wartość |
|---|---:|
| definitions | 541 |
| public | 350 |
| secret | 191 |
| points | 1428 |
| ID range | 1..570 |
| ID gaps | 29 |

## Statusy per-achievement

| Status | Liczba | Znaczenie |
|---|---:|---|
| confirmed | 0 | wszystkie warstwy wraz z runtime/E2E potwierdzone |
| partially-confirmed | 121 | definicja i statyczna ścieżka kandydująca, bez pełnego proof |
| definition-only | 0 | wyłącznie definicja z reviewed dowodem braku handlera niepotwierdzonym |
| handler-missing | 3 | reviewed subsystem evidence potwierdza brak award hooka |
| unresolved | 409 | dowód niewystarczający lub ścieżka dynamiczna/pośrednia |
| conflicting | 31 | brak definicji, metadata mismatch lub inny jawny konflikt |
| intentionally-unsupported | 0 | brak dowodu świadomego wyłączenia |

Brak `confirmed` nie jest błędem validatora. To konsekwencja rygorystycznego wymagania jednoczesnego proof warunku, reachability, persistence/backfill i runtime/E2E.

## Skan statyczny

| Dyspozycja | Liczba definicji |
|---|---:|
| direct-static-award | 89 |
| static-progress-path | 32 |
| referenced-without-static-award | 1 |
| no-direct-static-reference | 419 |

Znaleziono `182` aktywne referencje API: `160` statycznych rozwiązanych, `0` statycznych nierozwiązanych, `22` dynamiczne i `2` administracyjne.

Literalna referencja jest tylko kandydatem handlera. Brak literalnej referencji nie dowodzi braku mechaniki.

## 24 brakujące definicje

```text
195 Smart Thinking
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
591 Purrfectly Addicted
592 Six Steps Ahead
593 Radiant Nimbus
594 Amati's Echo
595 Enlightened, Indeed
```

Nie wolno dodawać ich tylko na podstawie wiki. Każdy wymaga content, storage, handler, backfill i runtime proof.

## 7 konfliktów metadata

```text
406 The More the Merrier: reference grade 0, Canary 1
513 Soul Mender: reference secret true, Canary false
526 King's Council: reference points 2, Canary 0
555 Inner Peace: reference points 3, Canary 2
556 Fiend Rider: reference points 3, Canary 2
559 Hope of the Merudri: reference points 2, Canary 3
562 Alpha Rider: reference points 3, Canary 2
```

Nie zmieniono żadnej wartości. Każdy konflikt musi zostać rozstrzygnięty względem wspieranej wersji i aktywnego contentu.

## Niepełne komórki źródłowe

Nieznane punkty: `574`, `587`, `588`, `591`, `595`.

Brak warunku: `195`, `561`, `574`, `587`, `588`, `595`.

Pozostają unresolved; niczego nie uzupełniono przez domysł.

## Persistence i backfill

`PlayerAchievement` przechowuje unlocked state pod kanoniczną nazwą:

```text
src/creatures/players/components/player_achievement.cpp:35  save by canonical name
src/creatures/players/components/player_achievement.cpp:103 load stored name
src/creatures/players/components/player_achievement.cpp:87  points persistence
```

Rename może osierocić istniejący KV. Zmiana nazwy wymaga migracji lub aliasu. Per-achievement backfill pozostaje unresolved bez osobnego planu subsystemowego.

## Reviewed Weapon Proficiency

- `564`–`566`: `handler-missing`; definicje istnieją, award hooków nie ma;
- `567`: `conflicting`; kontrakt 12 itemów/proficiency jest zweryfikowany, ale definicji, awardu i backfillu brak;
- PR #212 naprawił stan mastery i dodał count API, bez implementowania achievementów.

## Walidacja

```text
implementation commit: 741c0c40593c894c97212977485f073d8c2e52bb
Achievement Validation run: 29237298141 — success
artifact: 8273938137
artifact digest: sha256:3a36eec8d0eebb87010a5b12309ab5f2d8015160cbb6f0be7b2b497ba032c140
AI Agent Tools run: 29237298034 — success
Agent Task Ownership run: 29237298047 — success
focused tests: 13/13
```

Finalne gate'y muszą zostać wykonane ponownie po czystym refreshu na aktualnym `main`.

## Co zostało naprawione wcześniej

Historyczne findings z PR #165 nie są już aktywne:

- sparse registry/helper i `Game.isAchievementSecret` naprawiono w #176;
- dwa błędne literalne triggery naprawiono w #184;
- current scan ma `unknownStaticReferences=0`.

## Granica bezpieczeństwa

Ten PR nie modyfikuje rejestru, Lua/C++ gameplayu, storage, KV schema, DB, map ani assetów. Naprawy muszą być osobnymi, małymi PR-ami: metadata, missing definitions, dynamic resolvers, handlers, backfill i runtime/E2E osobno.
