# Canary Multi-Channel — Agent Handoff, Audit i Plan Dalszych Prac

> **Stan zweryfikowany:** 2026-07-12, Europe/Warsaw  
> **Repozytorium:** `blakinio/canary`  
> **Zweryfikowany `main` podczas audytu:** `97954d5d468190aeb46f223e87309396e2bfc3fa`  
> **Cel dokumentu:** przekazanie pełnego kontekstu kolejnemu agentowi rozwijającemu system kanałów.  
> **Ważne:** ten dokument dotyczy systemu **multi-channel**, a nie klasycznego multiworld ani projektu instancji.

---

## 1. Dyspozycja właściciela projektu

Wcześniejszy ogólny handoff silnika (`docs/architecture/CANARY_ENGINE_PROJECT_HANDOFF.md`) zawierał zasadę:

> Multiworld jest wstrzymany i nie wolno dodawać kolejnej fazy multi-channel bez wyraźnej decyzji właściciela.

Niniejsze zlecenie właściciela jest właśnie takim **wyraźnym ponownym otwarciem prac nad multi-channel**.

Nie oznacza to zgody na bezpośrednie zmiany w `main`, pomijanie CI ani wdrażanie niekompletnego systemu produkcyjnie.

Obowiązuje nadal:

- świeża gałąź z aktualnego `main`;
- małe, przeglądalne PR-y;
- jedna odpowiedzialność na PR;
- brak merge przy failed/cancelled/stale CI;
- brak obchodzenia testów;
- brak włączania `multiChannelEnabled` na produkcji przed spełnieniem bram bezpieczeństwa opisanych dalej.

---

## 2. Co budujemy i po co

### 2.1. Wybrany model

Budujemy:

> **jedną grę, jedną ekonomię i jedną globalną tożsamość postaci, uruchomione jako kilka równoległych kanałów mapy w osobnych procesach Canary.**

Początkowa topologia:

| Kanał | Typ |
|---|---|
| Channel 1 | No-PvP |
| Channel 2 | No-PvP |
| Channel 3 | Open PvP |

Liczba kanałów, nazwy, porty, typ PvP, limity i maintenance są konfigurowalne.

### 2.2. Dlaczego nie klasyczny multiworld

Klasyczny multiworld byłby łatwiejszy technicznie i bezpieczniejszy przez pełną izolację, ale nie spełnia celu produktu:

- gracz musiałby mieć osobną postać;
- ekonomie byłyby rozdzielone;
- nie dałoby się przejść tą samą postacią na kopię zajętego expowiska;
- społeczność zostałaby rozdzielona.

### 2.3. Dlaczego nie instancja całej mapy

Instancje są dobrym rozwiązaniem dla boss roomów, questów, dungeonów, aren i prywatnych lokacji.

Instancjowanie całej mapy wewnątrz jednego procesu byłoby gorsze od kanałów:

- wszystkie kopie walczą o jeden główny game loop;
- jeden crash zabija wszystkie kopie;
- trzeba dodać `instance_id` niemal do każdego lookupu tile/creature;
- rośnie zużycie pamięci i złożoność izolacji.

Docelowo właściwy model to:

```text
jedna globalna gra
├── Channel 1 — osobny proces, No-PvP
├── Channel 2 — osobny proces, No-PvP
├── Channel 3 — osobny proces, PvP
└── małe instancje bossów/questów wewnątrz kanałów
```

Projekt instancji istnieje osobno i nie należy mieszać jego zakresu z multi-channel bez świadomego kontraktu.

---

## 3. Wiążące decyzje produktowe

Poniższych decyzji nie należy ponownie negocjować bez pytania właściciela.

### 3.1. Globalne między kanałami

Ta sama postać na każdym kanale zachowuje:

- GUID i nazwę;
- level, experience, skille i vocation;
- inventory oraz equipment;
- depot, stash, inbox i store inbox;
- bank balance;
- market;
- pocztę i parcele;
- quest progress, storages, boss cooldowns, daily reward i jednorazowe nagrody;
- prey, charms, bestiary, bosstiary, wheel i pozostały rozwój;
- gildie, członkostwo i guild chat;
- VIP i grupy VIP;
- globalne publiczne chaty i private messages;
- skull, fragi, PZ lock oraz trwałe statusy PvP;
- highscores.

**Globalne między kanałami nie oznacza automatycznie account-wide.**

Należy zachować aktualny model właściciela danych Canary:

- dane gracza pozostają pod `player_id`;
- dane konta pozostają pod `account_id`;
- nie wolno bez potrzeby przenosić banku, inventory ani depotów z postaci na konto;
- wyjątkiem jest globalny limit jednego domu na konto.

### 3.2. Lokalne dla kanału

Osobne per kanał są:

- gracze fizycznie obecni na mapie;
- potwory, NPC runtime, summony, corpses i spawny;
- runtime eventów;
- domy i ich właściciele;
- house items, beds, doors i access lists;
- house auctions i rent state;
- `tile_store` i lokalny stan mapy;
- party, shared experience i direct trade;
- say/whisper/yell i NPC channel;
- boss roomy i lokalne instancje;
- pojemność i status kanału.

### 3.3. Market

Market jest całkowicie globalny:

- jedna lista ofert i jedna historia;
- jedna ekonomia;
- oferta utworzona na jednym kanale może zostać kupiona na innym;
- `channel_id` nie może wejść do biznesowej tożsamości oferty;
- `source_channel_id` może być wyłącznie audytem;
- zakup, anulowanie, dostarczenie itemu i wypłata pieniędzy muszą być transakcyjne i idempotentne.

### 3.4. Pozycja postaci

Pozycja jest globalna.

Po wejściu na inny kanał kolejność próby umieszczenia postaci to:

1. te same `x, y, z`;
2. najbliższy legalny publiczny tile w ograniczonym promieniu;
3. ostatnia bezpieczna publiczna pozycja;
4. temple.

Nielegalne są między innymi:

- brak tile lub zablokowany tile;
- cudzy/niedostępny dom na kanale docelowym;
- instancja;
- boss room lub quest room zakazujący switcha;
- strefa `NO_CHANNEL_SWITCH`;
- obszar wymagający specjalnego wejścia;
- niezgodna mapa.

Wyszukiwanie najbliższego tile musi być ograniczone promieniem i budżetem odwiedzonych node’ów.

### 3.5. Domy

- Każdy kanał ma osobny stan domów.
- Konto może posiadać maksymalnie **jeden dom w całym klastrze**.
- Dom istnieje fizycznie na jednym kanale.
- Itemy leżące w domu są dostępne wyłącznie na kanale domu.
- Ta sama kopia budynku na innym kanale może należeć do innego konta.
- Tożsamość fizycznego domu to `(channel_id, house_id)`.
- Limit jednego domu na konto musi być wymuszony w DB, nie tylko kodem C++/Lua.
- Należy rozwijać istniejące `houseOwnedByAccount`, a nie tworzyć drugi konkurencyjny model.

### 3.6. Party

- Party jest wyłącznie lokalne.
- Wszyscy członkowie muszą być na tym samym kanale.
- Shared EXP i party chat są lokalne.
- Domyślna polityka przy switchu: `deny`.
- Opcjonalna polityka: `leave`.

### 3.7. PvP i wojny gildii

- Channel 1 i 2: No-PvP.
- Channel 3: Open PvP.
- Typ PvP jest konfigurowany per kanał.
- Statusy PvP postaci są globalne.
- Zmiana kanału jest zawsze blokowana przy combat/PZ lock.
- Domyślnie skull blokuje wejście na No-PvP.
- Wojny są globalnie zdefiniowane, ale walka i fragi wojenne działają tylko na kanałach PvP.
- Na No-PvP gracze walczących gildii nie mogą się atakować.
- Nie wolno uciec z aktywnej walki na No-PvP.

### 3.8. Jedna aktywna postać na konto

W całym klastrze może być online tylko jedna postać danego konta.

Wymagane zabezpieczenia:

- globalny lock `account_id`;
- globalny lock `player_id`;
- lease + heartbeat;
- losowy `session_id`;
- fencing token;
- trwała obrona w DB;
- brak przejęcia sesji tylko na podstawie TTL;
- stary proces nie może zapisać danych po przejęciu sesji przez nowy.

### 3.9. Awaria Redis i DB

#### Redis

Fail closed:

- brak nowych loginów i channel switch;
- brak przejęcia sesji;
- krótki grace period dla już online;
- przed wygaśnięciem lease: freeze, save i disconnect;
- stary proces nie może kontynuować po utracie fencing tokena.

#### Baza danych

Jeszcze ostrzej fail closed:

- brak loginów i switcha;
- brak operacji ekonomicznych;
- brak dalszego normalnego expienia, lootowania, śmierci i mutowania trwałego stanu;
- bounded reconnect;
- jeżeli DB nie wróci: kontrolowane rozłączenie/shutdown i dirty session.

---

## 4. Model konfiguracji

Stosować model hybrydowy.

### 4.1. `config.lua.dist`

Globalne zachowanie i polityki:

- `multiChannelEnabled`;
- cooldown switcha;
- polityka pozycji i promień wyszukiwania;
- party policy i PvP exit policy;
- Redis connection;
- session TTL i heartbeat;
- failure grace periods;
- login gateway flag;
- cluster chat i channel tag.

### 4.2. Tabela `channels`

Źródło prawdy dla kanałów:

- id, name, pvp_type;
- host, game/status port;
- max players;
- enabled, sort order;
- temple town;
- maintenance;
- login gateway;
- map hash.

### 4.3. CLI/environment

Id procesu kanału:

1. `--channel-id`;
2. `CANARY_CHANNEL_ID`;
3. fallback `1` w trybie legacy.

Nie opierać process-specific `channelId` wyłącznie na wspólnym `config.lua`.

### 4.4. Twarde invariants bez przełączników

Nie wolno dodawać opcji pozwalających wyłączyć:

- session locks;
- fencing;
- save-before-release;
- version checks;
- idempotency;
- transakcje ekonomiczne;
- fail-closed;
- DB uniqueness domu;
- walidację pozycji;
- odrzucanie starego writer’a.

---

## 5. Changelog decyzji i implementacji

### Etap koncepcyjny

1. Rozważono multiworld, kanały i instancje.
2. Wybrano kanały jako właściwy model dla jednej postaci i jednej ekonomii.
3. Ustalono dwa kanały No-PvP i jeden PvP.
4. Ustalono wspólny market.
5. Ustalono globalną pozycję z fallbackiem.
6. Ustalono jeden dom na konto niezależnie od kanału.
7. Ustalono lokalność itemów domu.
8. Ustalono globalne boss cooldowny i quest progress.
9. Ustalono lokalne party.
10. Ustalono wojny działające bojowo tylko na PvP.
11. Ustalono wyłącznie jedną aktywną postać na konto.
12. Ustalono fail-closed dla Redis i DB.
13. Ustalono konfigurację hybrydową: Lua + DB + twarde invariants.
14. Ustalono docelową architekturę: osobny proces Canary per kanał.

### Etap implementacyjny

- PR #69: fundament architektury, schema, config, login list i algorytmy.
- PR #75: poprawka błędnego oczekiwania testu sortowania kanałów.
- PR #74: realny Redis client, runtime lease/session lifecycle i switch wiring.
- PR #102: mirror własności domu do `account_house_ownership`.

### Etap oceny wydajności

Nie istnieje gwarantowany limit bez benchmarku produkcyjnego.

Przyjęty plan po testach:

- start produkcyjny: 500–600 graczy łącznie;
- realistyczny cel: 800–1000;
- cel architektoniczny po optymalizacji: około 1500;
- więcej wymaga rozdzielenia procesów na maszyny i profilowania.

Nie używać tych liczb jako gwarancji. Limit ustalać na podstawie aktywnego obciążenia, nie idle klientów.

---

## 6. Audyt PR-ów multi-channel

### 6.1. PR #69 — Phase 1

**Link:** https://github.com/blakinio/canary/pull/69  
**Tytuł:** `feat: add production-safe multi-channel cluster (Phase 1)`  
**Stan:** closed + merged  
**Merge commit:** `c5c1c2829a003b16ec7077d068b181f2c08889de`

Dostarczono między innymi:

- `channels` i channel registry;
- per-channel schema dla houses/house_lists/tile_store;
- `account_house_ownership`;
- `cluster_sessions`;
- `channel_switch_audit`;
- `economic_ledger`;
- Redis lease/fencing core;
- channel switch policy;
- position resolver;
- config surface;
- login list per channel;
- Docker Compose przykład;
- komplet dokumentów `docs/multichannel/*`.

**CI:** finalny head PR #69 miał CI `failure`.

Ustalona przyczyna związana z multi-channel:

- błędne oczekiwanie w teście sortowania `ChannelRegistry`;
- poprawione osobnym PR #75;
- PR #75 miał zielone CI;
- późniejsze PR-y #74 i #102 również miały zielone CI.

Wniosek:

- #69 jest scalony;
- jego historyczny finalny head nie był zielony;
- znany błąd został domknięty przez #75;
- nie należy przedstawiać #69 jako samodzielnie „zielonego” PR-a.

Brak nierozwiązanych inline review threads.

### 6.2. PR #75 — test fix

**Link:** https://github.com/blakinio/canary/pull/75  
**Tytuł:** `fix(test): correct ChannelRegistry login-list sort tie-break expectation`  
**Stan:** closed + merged  
**Merge commit:** `fe4ec9a1c93ab03bf41ccec4cf84c95237232c16`  
**CI:** success  
**Review threads:** brak nierozwiązanych.

PR naprawił jedyny opisany błąd testowy odziedziczony po #69.

### 6.3. PR #74 — Phase 2

**Link:** https://github.com/blakinio/canary/pull/74  
**Tytuł:** `feat: wire multi-channel cluster session lifecycle into real engine (Phase 2)`  
**Stan:** closed + merged  
**Merge commit:** `d73f4f0e7e44b142747bb05ad8597c7e96d7985f`  
**CI:** success  
**MySQL Schema Check:** success  
**Review threads:** brak nierozwiązanych.

Dostarczono między innymi:

- `HiredisRedisClient`;
- `ClusterRuntime`;
- acquire przy loginie;
- release przy logout;
- lease renew + force disconnect;
- `EnginePositionLegality`;
- `ChannelSwitchAuditStore`;
- `Game::playerRequestChannelSwitch`;
- Lua `player:requestChannelSwitch(channelId)`;
- pending switch arrival position;
- migrację 61;
- dodatkowe testy.

### 6.4. PR #102 — Phase 3

**Link:** https://github.com/blakinio/canary/pull/102  
**Tytuł:** `feat: mirror house ownership into account_house_ownership (Phase 3)`  
**Stan:** closed + merged  
**Merge commit:** `2242618fc62329d7a5f9a1f48ea96684d8c7e851`  
**CI:** success, dwa zakończone poprawnie runy  
**Review threads:** brak nierozwiązanych.

Dostarczono:

- synchronizację `House::setOwner` → `account_house_ownership`;
- grant, revoke i przeniesienie wpisu tego samego konta na inny dom;
- aktualizację dokumentacji.

### 6.5. Czy są otwarte PR-y/gałęzie multi-channel w `blakinio/canary`

Podczas audytu:

- brak otwartego PR-a pasującego do `multichannel`/`multi-channel`;
- brak gałęzi znalezionej po nazwie `multichannel`;
- wszystkie trzy właściwe fazy są w `main`;
- nie istnieje aktywny PR domykający pozostałe braki produkcyjne.

### 6.6. Upstream Canary #2826

**Link:** https://github.com/opentibiabr/canary/pull/2826  
**Tytuł:** `feat: multiworld system`  
**Stan:** open  
**Draft:** tak  
**Merged:** nie  
**Mergeable:** nie  
**Zakres:** klasyczny multiworld, nie nasz docelowy model kanałów.

Nierozwiązane review threads:

1. wyjątek przy zakupie domu w `src/map/house/house.cpp`;
2. konflikt `players_online` przy wielu światach w `src/game/game.cpp`.

Nie merge’ować ani nie cherry-pickować hurtowo.

Można korzystać wyłącznie jako źródło historycznych pomysłów po niezależnej weryfikacji.

### 6.7. Upstream MyAAC #110

**Link:** https://github.com/opentibiabr/myaac/pull/110  
**Stan:** closed, not merged.

Nie stanowi gotowej integracji panelu dla naszego modelu kanałów.

W `blakinio/canary` istnieje tylko kontrakt:

`docs/multichannel/MYAAC_INTEGRATION.md`

Osobna implementacja MyAAC nadal jest wymagana.

---

## 7. Wniosek z audytu PR-ów

### Zamknięcie administracyjne

Tak:

- #69 zamknięty i scalony;
- #75 zamknięty i scalony;
- #74 zamknięty i scalony;
- #102 zamknięty i scalony;
- brak nierozwiązanych review threads;
- brak pozostawionego otwartego PR-a multi-channel.

### Kompletność funkcjonalna

Nie.

Scalenie faz 1–3 nie oznacza kompletnego systemu produkcyjnego.

`multiChannelEnabled` powinno pozostać wyłączone na produkcji do czasu domknięcia bram P0.

---

## 8. Co jest faktycznie gotowe

### Shipped

- schema kanałów i konfiguracja kanałów;
- rozpoznanie channel id z CLI/env;
- login list pokazująca tę samą postać na kanałach;
- per-channel `pvp_type`;
- podstawowa walidacja startup;
- Redis CAS scripts i production hiredis client;
- session lease/fencing core;
- Redis acquire/renew/release w realnych call sites;
- channel switch policy i bounded position resolver;
- realny adapter Map/Tile/House;
- relog-based switch triggerowany Lua;
- pending switch position i channel switch audit;
- schema per-channel houses/house lists/tile store;
- mirror własności domu;
- dokumentacja i przykładowy Docker Compose;
- testy jednostkowe i realne testy Redis/MariaDB dla części mechanizmów.

### Nie oznacza to jeszcze

- bezpiecznej produkcji;
- gotowego globalnego marketu w multi-process race;
- exactly-once mail;
- globalnego chat/PM;
- realnego heartbeat kanałów;
- recovery po crashu;
- pełnego fail-closed DB;
- pełnego testu trzech procesów;
- kompletnej integracji MyAAC.

---

## 9. Krytyczne braki — P0

Poniższe elementy muszą być domknięte przed produkcyjnym włączeniem.

### P0.1. Dual-write `cluster_sessions` do DB

Obecnie realne call sites egzekwują sesję przez Redis.

Tabela `cluster_sessions` istnieje, ale nie jest autorytatywnie dual-written.

Ryzyko:

- wipe/bypass/misconfiguration Redis może pozbawić system DB defense-in-depth;
- schema constraint nie chroni, jeżeli call sites nie zapisują rekordu.

Wymagane:

- atomowy DB acquire/release;
- spójność z Redis session id i fencing token;
- jasno zdefiniowana kolejność locków;
- recovery po częściowym sukcesie Redis/DB;
- unikalność `account_id` i `player_id`;
- test dwóch procesów.

### P0.2. Fencing na trwałym save

Monotoniczny fencing token istnieje w Redis, ale każdy trwały zapis musi sprawdzać, że writer nadal ma aktualny token.

Wymagane:

- state version/fencing guard w save pipeline;
- odrzucenie starego procesu;
- brak „last write wins”;
- konflikt oznacza dirty session i brak clean release.

### P0.3. Clean logout i crash recovery

Pełna kolejność:

```text
freeze actions
→ session SAVING
→ pełny DB save
→ COMMIT
→ state version update
→ OFFLINE
→ compare-and-release lock
```

Wymagane:

- brak zwolnienia przed commit;
- dirty session recovery;
- brak automatycznego reuse tylko dlatego, że TTL wygasł;
- admin inspect/clear z audytem;
- crash/pause tests.

### P0.4. Realny runtime heartbeat kanałów

`channel_runtime_status` istnieje jako schema, ale live heartbeat jest niedokończony.

Aktualne braki:

- target online/full w switchu ma optymistyczne placeholdery;
- login gateway nie ma wiarygodnego live statusu;
- nie ma pewnej agregacji online per kanał;
- nie ma bezpiecznego usuwania martwego kanału z listy.

Wymagane:

- heartbeat Redis + diagnostyczny mirror DB;
- stale cutoff;
- instance id, players online, build SHA i map/data hash;
- gateway/live ownership;
- test crash jednego kanału.

### P0.5. Fail-closed przy utracie DB

Dokumentacja istnieje, ale live engine policy nie jest kompletna.

Wymagane:

- wykrycie utraty DB;
- blokada login/switch;
- blokada mutacji ekonomicznych;
- emergency freeze gameplay mutations;
- reconnect z backoff;
- kontrolowany disconnect/shutdown;
- dirty sessions;
- testy outage.

### P0.6. Globalna ekonomia — transakcje i idempotency

`economic_ledger` jest schema-only.

Niewpięte call sites:

- market create/buy/cancel/delivery;
- bank transfer;
- mail/parcel send/receive;
- house purchase/transfer;
- kosztowne operacje, które mogą retry’ować.

Wymagane:

- `transaction_uuid`;
- transaction boundary i row locking;
- exactly-once efekt;
- replay zwraca poprzedni rezultat;
- before/after audit;
- race tests.

### P0.7. Trzyprocesowy test E2E

Nie wykonano pełnego realnego testu:

- trzy Canary;
- wspólna MariaDB;
- wspólny Redis;
- jeden login gateway;
- realny klient/protokół.

Wymagane scenariusze znajdują się w:

`docker/multichannel/SCENARIOS.md`

Bez tego nie wolno uznać systemu za production-ready.

---

## 10. Braki wysokiego priorytetu — P1

### P1.1. `last_safe_position`

Resolver ma krok 3, ale trwała pozycja nie istnieje.

Dodać schema, load/save, bezpieczną aktualizację, migrację i testy fallbacku.

### P1.2. House gate przed zaakceptowaniem operacji

PR #102 tworzy mirror, nie gate.

Aktualnie możliwe jest zaakceptowanie drugiego bidu, transferu lub konkurencyjnej operacji domu, zanim outcome zostanie rozstrzygnięty podczas restartu/map load.

Wymagane:

- gate przy bid/transfer/trade acceptance;
- DB transaction;
- lock account ownership row;
- brak `DELETE old + INSERT new` bez spójnej transakcji;
- race tests.

### P1.3. Powtarzalne `house_id` per kanał

Pomimo composite identity nadal istnieje `houses_id_unique`.

Skutek:

- ten sam numeric house id nie może realnie wystąpić na dwóch kanałach;
- `channel_id` jest częściowo inert.

Wymagane:

- usunięcie globalnej unique constraint;
- audyt wszystkich zapytań po `house_id`;
- wszędzie `(channel_id, house_id)`;
- migracja i rollback;
- test dwóch domów z tym samym id na różnych kanałach.

### P1.4. Global chat, guild chat, PM i VIP presence

Nie jest wykonany cross-process routing.

Wymagane:

- jawny scope `local|cluster`;
- Redis Pub/Sub tylko dla efemerycznych wiadomości;
- ignore/mute respektowane globalnie;
- presence z channel id;
- PM routing i login/logout notifications;
- bounded queues i backpressure.

Nie używać Pub/Sub dla trwałych operacji ekonomicznych.

### P1.5. Guild war combat enforcement

Schema audytowa istnieje, ale call site walki nie jest kompletny.

Wymagane:

- war kill tylko na PvP;
- brak war combat na No-PvP;
- `guildwar_kills.channel_id`;
- switch block przy combat;
- testy wszystkich typów PvP.

### P1.6. Map hash boot hook

Algorytm istnieje, ale pełny boot join/seed/refuse wymaga weryfikacji i domknięcia.

Wymagane:

- seed pierwszego kanału;
- odmowa niezgodnej mapy;
- race start dwóch kanałów;
- data/datapack hash lub jasno opisany zakres;
- test mismatch.

---

## 11. Dalszy roadmap — P2

- leader election z fencing dla singleton jobs;
- inwentaryzacja zadań per-channel/cluster-singleton;
- market expiration, house rent i house auction settlement;
- global resets, boosted boss/creature i global events;
- status aggregate i GM cross-node commands;
- kick/locate/drain/maintenance/save;
- orphan session tooling;
- metryki per channel/instance;
- exiva cross-channel policy;
- MyAAC implementation;
- pełny item instance UID dopiero po stabilizacji podstawowych zabezpieczeń;
- anomaly detection dla itemów;
- globalny datapack compatibility hash.

---

## 12. Problem dokumentacji: część statusów jest niespójna

Aktualne dokumenty zostały rozwijane fazami i zawierają pozostałości starszego stanu.

Przykłady:

- `ARCHITECTURE.md` nadal w nagłówku opisuje Phase 1;
- część sekcji niżej została zaktualizowana o Phase 2 i 3;
- `DECISION_MATRIX.md` miejscami oznacza engine hook jako 📐 mimo że późniejsza sekcja architektury opisuje realne wiring;
- `TEST_PLAN.md` zawiera historyczne stwierdzenia, że scenariusze zależą od Phase 2, mimo że część Phase 2 została później scalona.

Pierwszy dokumentacyjny PR nowego agenta powinien:

1. nie zmieniać zachowania;
2. przeglądnąć kod w aktualnym `main`;
3. zaktualizować status każdego wiersza;
4. rozdzielić shipped, partially shipped, schema only, designed i roadmap;
5. dodać datę i SHA audytu;
6. wskazać krytyczne bramy produkcyjne;
7. nie przedstawiać aspiracji jako implementacji.

---

## 13. Zalecana kolejność nowych PR-ów

Nie robić jednego ogromnego, nieprzeglądalnego PR-a.

Można używać wielu agentów równolegle, ale integracja powinna być fazowa.

1. **PR A — truth audit + docs refresh**
2. **PR B — runtime heartbeat**
3. **PR C — DB session defense-in-depth**
4. **PR D — save fencing/state version**
5. **PR E — DB outage fail-closed**
6. **PR F — house gate + transaction**
7. **PR G — house composite identity completion**
8. **PR H — market atomicity**
9. **PR I — mail/parcel exactly-once**
10. **PR J — bank/economy remaining**
11. **PR K — global chat/PM/VIP/guild chat**
12. **PR L — PvP/war enforcement**
13. **PR M — 3-process integration suite**
14. **PR N — MyAAC w osobnym repo**

Każdy PR ma zawierać aktualizację dokumentacji i jasno opisać, czego nadal nie dostarcza.

---

## 14. Pliki kluczowe

### Dokumentacja

```text
docs/multichannel/ARCHITECTURE.md
docs/multichannel/DECISION_MATRIX.md
docs/multichannel/MIGRATION.md
docs/multichannel/OPERATIONS.md
docs/multichannel/TEST_PLAN.md
docs/multichannel/THREAT_MODEL.md
docs/multichannel/MYAAC_INTEGRATION.md
docker/multichannel/SCENARIOS.md
```

### Config/schema

```text
config.lua.dist
schema.sql
data-otservbr-global/migrations/59.lua
data-otservbr-global/migrations/60.lua
data-otservbr-global/migrations/61.lua
```

### Core multi-channel

```text
src/game/multichannel/channel_context.*
src/game/multichannel/channel_info.hpp
src/game/multichannel/channel_registry.*
src/game/multichannel/cluster_config_validator.*
src/game/multichannel/cluster_session_manager.*
src/game/multichannel/cluster_runtime.*
src/game/multichannel/hiredis_redis_client.*
src/game/multichannel/redis_client.hpp
src/game/multichannel/redis_scripts/*.lua
src/game/multichannel/channel_switch_service.*
src/game/multichannel/channel_switch_audit_store.*
src/game/multichannel/position_resolver.*
src/game/multichannel/engine_position_legality.*
src/game/multichannel/position_serialization.*
```

### Engine call sites

```text
src/canary_server.cpp
src/main.cpp
src/server/network/protocol/protocollogin.cpp
src/server/network/protocol/protocolgame.cpp
src/creatures/players/player.cpp
src/game/game.cpp
src/game/game.hpp
src/map/house/house.cpp
src/lua/functions/creatures/player/player_functions.cpp
```

### Testy

```text
tests/unit/game/multichannel/*
tests/shared/game/multichannel/fake_redis_client.hpp
docker/multichannel/*
```

---

## 15. Zasady bezpieczeństwa dla kolejnego agenta

### Zakazane skróty

Nie wolno:

- włączać feature produkcyjnie tylko dlatego, że PR-y są merged;
- zwalniać locka przed DB commit;
- traktować Redis TTL jako dowodu, że stary proces nie żyje;
- używać zwykłego `SET NX` bez owner compare i fencing;
- przesyłać zakupów/transferów przez Pub/Sub;
- wykonywać check-then-insert bez DB constraint;
- dodawać `channel_id` do globalnych danych postaci;
- robić osobnych postaci per kanał;
- łamać single-channel default;
- usuwać testów dla zielonego CI;
- ukrywać niedokończony zakres za opisem „production-safe”;
- kopiować upstream #2826 bez audytu;
- mieszać projektu instancji z kanałami przypadkowo.

### Wymagane praktyki

- prepared queries;
- transakcje i idempotency;
- explicit lock ordering;
- bounded retries i bounded queues;
- reconnect backoff;
- brak blokującego Redis I/O na game thread;
- callbacki wracają przez dispatcher;
- audit logs;
- feature default off;
- testy race/outage;
- migration + rollback;
- aktualizacja handoff po każdym merge.

---

## 16. Checklista startowa nowego agenta

Przed pierwszą zmianą:

1. `git fetch --all --prune`;
2. checkout aktualnego `main`;
3. zapisz SHA;
4. listuj wszystkie open PR-y;
5. pobierz changed filenames otwartych PR-ów;
6. sprawdź konflikty z planowanymi plikami;
7. przeczytaj cały `docs/multichannel/*`;
8. przeczytaj PR #69, #74, #75 i #102;
9. przeczytaj `docker/multichannel/SCENARIOS.md`;
10. zbuduj normalny single-channel;
11. uruchom pełne unit tests;
12. uruchom schema tests;
13. zbuduj z feature `multichannel`;
14. uruchom Redis/MariaDB lokalnie;
15. odtwórz baseline przed zmianami.

---

## 17. CI gate

Każdy runtime C++ PR powinien przejść:

- formatting/autofix;
- static analysis;
- unit tests;
- Lua tests;
- Linux debug i release;
- Canary oraz Global datapack smoke;
- Windows CMake;
- Windows Solution/MSBuild;
- macOS;
- Docker;
- dedykowane multi-channel tests;
- MySQL schema check.

PR-y dotyczące DB/Redis dodatkowo:

- real MariaDB integration;
- real Redis integration;
- concurrency/race;
- outage/reconnect;
- migration fresh install i upgrade;
- rollback;
- repeat/idempotency.

Nie scalać na podstawie samego „mergeable”.

---

## 18. Definition of done dla produkcyjnego multi-channel

System jest gotowy dopiero, gdy:

- trzy procesy działają równocześnie;
- login gateway pokazuje aktywne kanały;
- ta sama postać loguje się na dowolny kanał;
- jedna postać/konto nie może być online dwa razy;
- DB i Redis defense-in-depth są realnie aktywne;
- stary fencing token nie może zapisać;
- crash nie otwiera duplikacji;
- switch zachowuje legalną pozycję;
- `last_safe_position` działa;
- target online/full jest rzeczywisty;
- domy są per kanał i ten sam house id działa na różnych kanałach;
- konto ma jeden dom globalnie;
- house gate jest transakcyjny;
- market, mail/parcel i bank są exactly-once;
- questy i boss cooldowny są globalne;
- party/trade są lokalne;
- chat/PM/VIP/guild chat działają globalnie;
- wojny działają bojowo tylko na PvP;
- Redis outage i DB outage są fail-closed;
- singleton jobs nie wykonują się wielokrotnie;
- 30 scenariuszy E2E i race tests przechodzą;
- realny klient został zweryfikowany;
- single-channel pozostaje zgodny;
- MyAAC jest kompatybilny;
- pełne CI jest zielone;
- dokumentacja odzwierciedla kod, a nie plan.

---

## 19. Rekomendacja produkcyjna na dziś

Na stanie z 2026-07-12:

```text
multiChannelEnabled = false
```

Można rozwijać, budować testowy klaster, wykonywać testy, przygotowywać MyAAC i profilować wydajność.

Nie należy jeszcze:

- włączać systemu dla realnych graczy;
- ufać wspólnemu marketowi pod race;
- ufać mailowi exactly-once;
- ufać DB recovery;
- traktować heartbeat/status jako kompletny;
- deklarować pełnej odporności anti-dupe.

---

## 20. Źródła

### Własny fork

- https://github.com/blakinio/canary/pull/69
- https://github.com/blakinio/canary/pull/74
- https://github.com/blakinio/canary/pull/75
- https://github.com/blakinio/canary/pull/102
- https://github.com/blakinio/canary/tree/main/docs/multichannel
- https://github.com/blakinio/canary/tree/main/docker/multichannel

### Upstream — tylko materiał porównawczy

- https://github.com/opentibiabr/canary/pull/2826
- https://github.com/opentibiabr/myaac/pull/110

### Repozytoria projektu OTS

- https://github.com/opentibiabr/otclient
- https://github.com/opentibiabr/canary
- https://github.com/opentibiabr/remeres-map-editor
- https://github.com/opentibiabr/client-editor

---

## 21. Raport końcowy wymagany od kolejnego agenta

Po zakończeniu swojej fazy agent ma podać:

1. PR;
2. branch i head SHA;
3. zakres;
4. zmienione pliki;
5. migracje;
6. nowe configi;
7. testy lokalne;
8. CI;
9. real Redis/MariaDB wyniki;
10. race/outage wyniki;
11. backward compatibility;
12. znane ograniczenia;
13. aktualizację tego handoffu;
14. jasne `production-ready: tak/nie`.

Nie kończyć raportu samym planem.
