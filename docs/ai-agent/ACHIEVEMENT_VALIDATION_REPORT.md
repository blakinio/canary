# Canary achievements — statyczny audyt rejestru i triggerów

## Decyzja

```text
status: conflicting
confidence: high dla findings statycznych
runtimeE2EProven: false
registryDefinitions: 541
referenceListed: 562
referenceTotal: 563
activeApiReferences: 182
undefinedStaticReferences: 2
dynamicReferences: 22
```

Aktualny system achievementów ładuje istniejący rejestr, ale nie jest zgodny z bieżącym źródłem referencyjnym i zawiera potwierdzone błędy infrastrukturalne oraz dwa aktywne triggery, które nie mogą rozwiązać achievementu po nazwie. Audyt nie dowodzi jeszcze osiągalności wszystkich wpisów w gameplay; wyznacza bezpieczną kolejność dalszych napraw i testów runtime.

## Zakres i źródła

Audyt wykonano na headzie PR `#165` po scaleniu aktualnego `main`:

```text
commit: 8642fdfa78d83bd41b6948ddf6aee10593cfcdbe
```

Źródła aktywne:

- `data/scripts/lib/register_achievements.lua`;
- wszystkie pliki Lua pod `data/`;
- wszystkie pliki Lua pod `data-otservbr-global/`;
- C++ achievement registry i player persistence;
- TibiaWiki/Fandom `Achievements`, stan zweryfikowany 2026-07-12.

Pełny per-achievement JSON i lista referencji są artefaktem workflow `Achievement Validation`, nie plikiem commitowanym do repozytorium.

## Wynik rejestru

| Wymiar | Canary | Referencja | Różnica |
|---|---:|---:|---:|
| jawne / odkryte wpisy | 541 | 562 | -21 |
| common | 350 | 362 | -12 |
| odkryte secret | 191 | 200 | -9 |
| suma punktów | 1428 | 1470 | -42 |

Rejestr używa ID `1..570`, ale ma 29 luk. Najwyższy ID nie jest liczbą achievementów.

Dwa wpisy mają świadomie zapisane `0` punktów i są raportowane jako wyjątki informacyjne, nie jako automatyczna korupcja:

- ID `406` — `The More the Merrier`;
- ID `526` — `King's Council`.

## 21 referencyjnych wpisów nieobecnych w rejestrze

Poniższe ID i nazwy zostały ręcznie potwierdzone na bieżącej stronie referencyjnej i nie występują w audytowanym rejestrze Canary:

| ID | Nazwa | Wersja / data źródłowa |
|---:|---|---|
| 550 | A Friend in Need | 2024-07-01 |
| 551 | Holzkopf | 2024-07-01 |
| 567 | The Forbidden Build | 2025-07-21 |
| 572 | Errand Runner | 2025-11-24 |
| 573 | Workhorse | 2025-11-24 |
| 574 | Taskaholic | 2025-11-24 |
| 575 | Pest Control | 2025-11-24 |
| 576 | Mimic | 2025-11-24 |
| 577 | Bastard | 2025-11-24 |
| 578 | Razor's Edge | 2025-11-24 |
| 579 | Lost Letters | 2025-11-24 |
| 580 | Stagmeister | 2025-11-24 |
| 581 | Feral Trapper | 2025-11-24 |
| 582 | Castle Crasher | 2026-03-17 |
| 585 | A reliable Friend | 2026-03-17 |
| 586 | Echo Initiate | Summer 2026 |
| 587 | Echo Hunter | Summer 2026 |
| 588 | Echo Walker | Summer 2026 |
| 592 | Six Steps Ahead | Summer 2026 |
| 593 | Radiant Nimbus | Summer 2026 |
| 594 | Amati's Echo | Summer 2026 |

To nie jest zgoda na dopisanie samych definicji. Każdy wpis wymaga potwierdzenia, że odpowiadający content, storage, item, quest, task board, mount, outfit albo event istnieje i działa w analizowanej wersji Canary. Szczególnie wpisy Summer 2026 muszą być skorelowane z faktycznie zaimportowanym contentem, a nie dodane wyłącznie dlatego, że istnieją na wiki.

Różnicy `42` punktów nie wolno przypisywać mechanicznie tym 21 wpisom. Niektóre bieżące wartości punktowe pozostają niepotwierdzone, a mutually exclusive achievements wymagają osobnego modelu semantycznego.

## Potwierdzony defekt 1 — rzadka tabela używana z `#ACHIEVEMENTS`

Rejestr ma jawne luki, ale helper Lua używa operatora długości jako granicy:

```lua
ACHIEVEMENT_LAST = #ACHIEVEMENTS
```

oraz iteruje `Player.getAchievements` po zakresie `1..#ACHIEVEMENTS`.

Lua nie gwarantuje użytecznej długości dla rzadkiej tabeli. Rejestracja przez `pairs` może dodać wysokie ID, podczas gdy helpery zakresowe mogą ich nie zwrócić.

Dyspozycja: `confirmed-infrastructure-defect`.

Wymagany osobny fix:

- iteracja po jawnych kluczach lub po runtime `Game.getAchievements()`;
- test ID przed i po pierwszej luce;
- test najwyższego jawnego ID;
- test bulk add/remove;
- brak zmiany ID istniejących wpisów.

## Potwierdzony defekt 2 — `Game.isAchievementSecret`

Helper rozwiązuje `foundAchievement`, lecz zwraca:

```lua
return achievement.secret
```

Argument `achievement` jest ID albo nazwą, nie tabelą metadata. Ścieżka invalid dodatkowo formatuje komunikat niezdefiniowaną zmienną `ach`.

Dyspozycja: `confirmed-infrastructure-defect`.

Wymagany osobny fix i testy:

- public po ID;
- secret po ID;
- public po nazwie;
- secret po nazwie;
- niepoprawne ID i nazwa bez wtórnego błędu Lua.

## Potwierdzone defekty 3–4 — dwa aktywne triggery z błędną nazwą

C++ rejestruje nazwy w `std::map<std::string, uint16_t>` i wykonuje dokładne `find(name)`. Lookup jest case-sensitive i uwzględnia apostrofy.

### Phantasmal jade mount

```text
plik: data/scripts/actions/items/usable_phantasmal_jade_items.lua
linia: 36
trigger: You got Horse Power
rejestr: ID 514, You Got Horse Power
```

Różnica wielkości litery `got/Got` powoduje brak rozwiązania achievementu.

### Hero of Rathleton reward

```text
plik: data-otservbr-global/scripts/quests/hero_of_rathleton/actions_reward.lua
linia: 9
trigger: The Professors Nut
rejestr: ID 360, The Professor's Nut
```

Brak apostrofu i formy dzierżawczej powoduje brak rozwiązania achievementu.

Dyspozycja obu: `confirmed-broken-static-trigger`.

Poprawki powinny znaleźć się w osobnym focused PR z testem kontraktowym, który sprawdza każdą literalną nazwę wobec aktywnego rejestru.

## Pokrycie triggerów statycznych

| Dyspozycja | Liczba |
|---|---:|
| bezpośredni statyczny award | 87 |
| statyczna ścieżka progress | 32 |
| referencja bez statycznego awardu | 1 |
| brak bezpośredniej statycznej referencji | 421 |

Łącznie znaleziono `182` wywołania API, w tym `22` argumenty dynamiczne.

`421` wpisów bez literalnego triggera nie oznacza `421` uszkodzonych achievementów. Część jest przyznawana przez:

- wspólne tabele itemów, mountów, outfitów lub skinningu;
- wrappery questowe;
- dynamiczne zmienne nazw;
- liczniki progress;
- NPC i state machines;
- ścieżki wymagające analizy engine/runtime.

Każdy taki wpis pozostaje `needs-semantic-or-runtime-review`.

## Persistence i kompatybilność nazw

C++ zapisuje unlocked achievement w KV pod jego nazwą, a przy ładowaniu mapuje nazwę ponownie na aktualne ID.

Konsekwencje:

- rename może osierocić istniejący zapis gracza;
- zmiana ID przy tej samej nazwie może przepiąć zapis na nowe ID;
- duplikat nazwy jest krytyczny;
- każda korekta nazwy definicji wymaga migracji lub aliasu kompatybilności.

Dlatego dwa błędne triggery należy poprawić w call sites, a nie przez zmianę kanonicznych nazw rejestru.

## Walidacja wykonana

Na commit `8642fdfa78d83bd41b6948ddf6aee10593cfcdbe`:

- `Achievement Validation` run `29202931191`: success;
- `AI Agent Tools` run `29202931162`: success;
- główny `CI` run `29202931226`: success;
- focused unit tests skanera: 8/8;
- pełny skan obu aktywnych datapacków zakończony;
- JSON baseline i runtime plan poprawne składniowo;
- artefakt `achievement-validation-audit`, ID `8262907252`, SHA-256 `4e127d6c708b6422f520f5833394b652331addcbf989f345523f9d31b9171baa`;
- diff PR obejmuje wyłącznie narzędzie, testy, workflow i dokumentację;
- brak zmian `.otbm`, `items.otb`, assetów, aktywnego rejestru, gameplay i C++.

## Czego ten audyt jeszcze nie dowodzi

- pełnej osiągalności 541 istniejących definicji;
- prawidłowych progów wszystkich progress counters;
- zgodności każdego description/grade/secret z aktualną Tibią;
- działania questów, NPC, bossów i itemów zależnych;
- persistence po rzeczywistym restarcie serwera;
- poprawności mutually exclusive achievements;
- gotowości 21 brakujących wpisów do bezpiecznego dodania.

Scenariusze runtime są zapisane w:

```text
docs/ai-agent/ACHIEVEMENT_RUNTIME_TEST_PLAN.json
```

## Kolejność dalszych prac

1. Osobny PR: naprawa `#ACHIEVEMENTS` i `Game.isAchievementSecret`.
2. Osobny PR: poprawa dwóch literalnych nazw triggerów wraz z kontraktowym skanem regresyjnym.
3. Rozszerzenie skanera o bezpieczne rozwiązywanie wybranych dynamicznych tabel i wrapperów.
4. Grupowa walidacja semantyczna istniejących achievementów według systemu: quest, boss, NPC, mount/outfit, item-use, progress.
5. Osobny audyt contentu dla ID `550`, `551`, `567`.
6. Osobny audyt Winter Update 2025 dla ID `572..581`.
7. Osobny audyt Spring/Summer 2026 dla ID `582`, `585..588`, `592..594`.
8. Runtime smoke i reprezentatywne E2E przed każdą zmianą produkcyjnego rejestru.

## Końcowy wniosek

Warstwa statyczna jest gotowa i powtarzalna w CI. Canary ma trzy potwierdzone defekty helperów, dwa nieskuteczne literalne triggery oraz co najmniej 21 bieżących referencyjnych definicji nieobecnych w rejestrze. Nie należy jednak masowo dopisywać achievementów ani uznawać pozostałych `no-direct-static-reference` za uszkodzone. Następna bezpieczna praca to małe PR-y naprawiające potwierdzone błędy, równolegle z semantyczną i runtime walidacją kolejnych grup.
