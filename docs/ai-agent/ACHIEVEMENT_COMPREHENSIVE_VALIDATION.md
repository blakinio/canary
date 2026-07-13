# Comprehensive Achievement Validation

> **State:** active evidence audit on draft PR #238
> **Observed source date:** 2026-07-13
> **Gameplay modified:** no
> **Evidence boundary:** definition, reference condition, static handler candidate, persistence/backfill and runtime attainability are separate proof layers.

## Scope

This is the durable human-readable index for the full current TibiaWiki/Fandom achievement table. It extends the existing validator rather than creating another registry parser or trigger scanner.

The factual catalogue records IDs, names, grade, secrecy, premium flag, points, implementation date, source page, conservative condition kinds, linked entities, numeric tokens and source hashes. Long description and spoiler prose are intentionally not copied.

## Methodology

1. Fetch the current MediaWiki parse payload through a bounded, hash-recorded retrieval.
2. Parse the rendered table deterministically with the Python standard library.
3. Match each reference row against the active Canary registry by ID and exact name.
4. Scan both active datapacks for achievement API references and preserve exact file/line evidence.
5. Keep dynamic Lua, wrappers, state machines and indirect C++ paths unresolved unless a deterministic resolver proves them.
6. Evaluate persistence/backfill, existing-player attainability, new-player attainability, runtime registration and tests independently.
7. Never change gameplay from a reference-only finding; use small follow-up PRs after sufficient evidence.

## Reference provenance

- page: `https://tibia.fandom.com/wiki/Achievements`
- retrieval endpoint: `https://tibia.fandom.com/api.php?action=parse&page=Achievements&prop=text%7Crevid&format=json&formatversion=2`
- page ID / revision ID: `49280` / `1188274`
- source bytes: `1026270`
- source SHA-256: `8a429425ab7b088758646b07f036afdd1d579188d056491aed8e77650306ae8b`
- raw source is not committed; the factual catalogue and hashes are committed.

## Current factual baseline

| Dimension | Current reference | Canary registry |
|---|---:|---:|
| listed/discovered rows | 564 | 541 |
| total including undiscovered secret | 565 | n/a |
| common | 363 | 350 |
| discovered secret | 201 | 191 |
| theoretical known points | 1475 | 1428 |
| unknown point rows | 5 | 0 |
| reference condition available | 558 | n/a |
| reference condition unavailable | 6 | n/a |

The current API revision is internally consistent at 564 listed/discovered achievements out of 565 total. Earlier cached text showing 562/563 is historical stale evidence and is not used as the current baseline.

## Classification model

- `confirmed` — condition, active handler, persistence and runtime/test evidence are all proven.
- `partially-confirmed` — definition and at least one active static award/progress candidate are proven, but semantic reachability or runtime remains unproven.
- `definition-only` — definition is proven and reviewed evidence proves no usable active handler in the inspected scope.
- `handler-missing` — a required award handler is specifically proven absent.
- `unresolved` — evidence is insufficient, dynamic, indirect or not yet reviewed.
- `conflicting` — reference and Canary identity/metadata/evidence disagree.
- `intentionally-unsupported` — an explicit version/scope decision with evidence excludes the achievement.

A simple absence of a literal API call never promotes a row to `definition-only` or `handler-missing`.

## Current status counts

- `confirmed`: 0
- `conflicting`: 31
- `definition-only`: 0
- `handler-missing`: 3
- `intentionally-unsupported`: 0
- `partially-confirmed`: 121
- `unresolved`: 409

## Trigger scan summary

- active API references: `182`
- resolved static references: `160`
- unknown static references: `0`
- dynamic references: `22`
- admin references: `2`

Static award/progress references are candidates only; they do not prove semantic reachability or runtime completion.

## Reference definitions absent from Canary

| ID | Name | Grade | Secret | Points | Implemented | Condition |
|---:|---|---:|---|---:|---|---|
| 195 | [Smart Thinking](https://tibia.fandom.com/wiki/Smart_Thinking) | 1 | true | 2 | December 8, 2010 | unresolved |
| 550 | [A Friend in Need](https://tibia.fandom.com/wiki/A_Friend_in_Need) | 1 | true | 2 | July 01, 2024 | quest-or-task |
| 551 | [Holzkopf](https://tibia.fandom.com/wiki/Holzkopf) | 1 | true | 1 | July 01, 2024 | item-or-interaction |
| 567 | [The Forbidden Build](https://tibia.fandom.com/wiki/The_Forbidden_Build) | 1 | true | 3 | July 21, 2025 | other |
| 572 | [Errand Runner](https://tibia.fandom.com/wiki/Errand_Runner) | 1 | false | 3 | November 24, 2025 | quest-or-task, combat |
| 573 | [Workhorse](https://tibia.fandom.com/wiki/Workhorse) | 2 | false | 5 | November 24, 2025 | quest-or-task, combat |
| 574 | [Taskaholic](https://tibia.fandom.com/wiki/Taskaholic) | 3 | false | ? | November 24, 2025 | unresolved |
| 575 | [Pest Control](https://tibia.fandom.com/wiki/Pest_Control) | 3 | false | 7 | November 24, 2025 | quest-or-task |
| 576 | [Mimic](https://tibia.fandom.com/wiki/Mimic_(Achievement)) | 1 | true | 1 | November 24, 2025 | progress-threshold |
| 577 | [Bastard](https://tibia.fandom.com/wiki/Bastard) | 2 | false | 5 | November 24, 2025 | quest-or-task |
| 578 | [Razor's Edge](https://tibia.fandom.com/wiki/Razor%27s_Edge) | 2 | true | 4 | November 24, 2025 | combat |
| 579 | [Lost Letters](https://tibia.fandom.com/wiki/Lost_Letters) | 1 | true | 3 | November 24, 2025 | other |
| 580 | [Stagmeister](https://tibia.fandom.com/wiki/Stagmeister) | 1 | true | 1 | November 24, 2025 | item-or-interaction |
| 581 | [Feral Trapper](https://tibia.fandom.com/wiki/Feral_Trapper) | 1 | false | 2 | November 24, 2025 | quest-or-task |
| 582 | [Castle Crasher](https://tibia.fandom.com/wiki/Castle_Crasher) | 1 | true | 1 | March 17, 2026 | other |
| 585 | [A reliable Friend](https://tibia.fandom.com/wiki/A_reliable_Friend) | 1 | false | 1 | March 17, 2026 | mount-taming |
| 586 | [Echo Initiate](https://tibia.fandom.com/wiki/Echo_Initiate) | 1 | false | 1 | Summer 2026 | item-or-interaction, event-or-raid |
| 587 | [Echo Hunter](https://tibia.fandom.com/wiki/Echo_Hunter) | 1 | false | 4 | Summer 2026 | unresolved |
| 588 | [Echo Walker](https://tibia.fandom.com/wiki/Echo_Walker) | 2 | false | ? | Summer 2026 | unresolved |
| 591 | [Purrfectly Addicted](https://tibia.fandom.com/wiki/Purrfectly_Addicted) | 1 | true | 1 | Summer 2026 | item-or-interaction, progress-threshold |
| 592 | [Six Steps Ahead](https://tibia.fandom.com/wiki/Six_Steps_Ahead) | 1 | false | 2 | Summer 2026 | mount-taming |
| 593 | [Radiant Nimbus](https://tibia.fandom.com/wiki/Radiant_Nimbus) | 1 | false | ? | Summer 2026 | mount-taming |
| 594 | [Amati's Echo](https://tibia.fandom.com/wiki/Amati%27s_Echo) | 2 | false | 4 | Summer 2026 | quest-or-task |
| 595 | [Enlightened, Indeed](https://tibia.fandom.com/wiki/Enlightened,_Indeed) | 1 | false | ? | Summer 2026 | unresolved |

A missing reference definition is not evidence that the corresponding quest, item, event, mount, outfit or system is implemented in Canary.

## Metadata conflicts for existing Canary definitions

| ID | Name | Field | Reference | Canary | Registry evidence |
|---:|---|---|---|---|---|
| 406 | The More the Merrier | grade | 0 | 1 | `data/scripts/lib/register_achievements.lua:407` |
| 513 | Soul Mender | secret | True | False | `data/scripts/lib/register_achievements.lua:514` |
| 526 | King's Council | points | 2 | 0 | `data/scripts/lib/register_achievements.lua:527` |
| 555 | Inner Peace | points | 3 | 2 | `data/scripts/lib/register_achievements.lua:554` |
| 556 | Fiend Rider | points | 3 | 2 | `data/scripts/lib/register_achievements.lua:555` |
| 559 | Hope of the Merudri | points | 2 | 3 | `data/scripts/lib/register_achievements.lua:558` |
| 562 | Alpha Rider | points | 3 | 2 | `data/scripts/lib/register_achievements.lua:561` |

These are audit conflicts only. No grade, secrecy, points or name is changed in this PR.

## Reference rows with incomplete source metadata

- unknown point values (5): `561 Hell Rider`, `574 Taskaholic`, `588 Echo Walker`, `593 Radiant Nimbus`, `595 Enlightened, Indeed`
- unavailable condition cells (6): `195 Smart Thinking`, `561 Hell Rider`, `574 Taskaholic`, `587 Echo Hunter`, `588 Echo Walker`, `595 Enlightened, Indeed`

These remain unresolved; no condition or value is inferred.

## Full achievement catalogue

| ID | Reference achievement | Grade | Secret | Premium | Points | Implemented | Condition kinds | Canary definition | Registry evidence | Status | Active static path evidence |
|---:|---|---:|---|---|---:|---|---|---|---|---|---|
| 1 | [Castlemania](https://tibia.fandom.com/wiki/Castlemania) | 2 | true | True | 5 | June 30, 2010 | quest-or-task, collection, exploration, dialogue | confirmed | `data/scripts/lib/register_achievements.lua:2` | unresolved | unresolved |
| 2 | [Chorister](https://tibia.fandom.com/wiki/Chorister) | 1 | false | False | 1 | June 30, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:3` | unresolved | unresolved |
| 3 | [The Milkman](https://tibia.fandom.com/wiki/The_Milkman) | 1 | false | True | 2 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:4` | unresolved | unresolved |
| 4 | [Vive la Resistance](https://tibia.fandom.com/wiki/Vive_la_Resistance) | 1 | false | True | 2 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:5` | unresolved | unresolved |
| 5 | [Culinary Master](https://tibia.fandom.com/wiki/Culinary_Master) | 2 | false | True | 4 | June 30, 2010 | quest-or-task, item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:6` | unresolved | unresolved |
| 6 | [Shell Seeker](https://tibia.fandom.com/wiki/Shell_Seeker) | 1 | true | True | 3 | June 30, 2010 | collection | confirmed | `data/scripts/lib/register_achievements.lua:7` | partially-confirmed | `data/scripts/actions/objects/large_seashell.lua:18` addAchievementProgress |
| 7 | [Backpack Tourist](https://tibia.fandom.com/wiki/Backpack_Tourist) | 1 | true | False | 1 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:8` | partially-confirmed | `data-otservbr-global/npc/sam.lua:119` addAchievement |
| 8 | [Dread Lord](https://tibia.fandom.com/wiki/Dread_Lord) | 3 | true | True | 8 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:9` | partially-confirmed | `data-otservbr-global/npc/the_bone_master.lua:129` addAchievement |
| 9 | [Lord Protector](https://tibia.fandom.com/wiki/Lord_Protector) | 3 | true | True | 8 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:10` | partially-confirmed | `data-otservbr-global/npc/the_dream_master.lua:125` addAchievement |
| 10 | [Nightmare Knight](https://tibia.fandom.com/wiki/Nightmare_Knight) | 1 | false | True | 1 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:11` | partially-confirmed | `data-otservbr-global/npc/the_dream_master.lua:95` addAchievement |
| 11 | [Bone Brother](https://tibia.fandom.com/wiki/Bone_Brother) | 1 | false | True | 1 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:12` | partially-confirmed | `data-otservbr-global/npc/the_bone_master.lua:98` addAchievement |
| 12 | [Blessed!](https://tibia.fandom.com/wiki/Blessed!) | 1 | false | True | 2 | June 30, 2010 | quest-or-task, collection, dialogue | confirmed | `data/scripts/lib/register_achievements.lua:13` | partially-confirmed | `data-otservbr-global/npc/chondur.lua:244` addAchievement |
| 13 | [Recognised Trader](https://tibia.fandom.com/wiki/Recognised_Trader) | 1 | false | True | 3 | June 30, 2010 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:14` | partially-confirmed | `data-otservbr-global/npc/rashid.lua:116` addAchievement; `data-otservbr-global/npc/rashid_custom.lua:118` addAchievement |
| 14 | [Fountain of Life](https://tibia.fandom.com/wiki/Fountain_of_Life) | 1 | true | True | 1 | June 30, 2010 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:15` | partially-confirmed | `data-otservbr-global/scripts/quests/the_pits_of_inferno_quest/actions_fountain.lua:9` addAchievement |
| 15 | [Lord of the Elements](https://tibia.fandom.com/wiki/Lord_of_the_Elements_(Achievement)) | 2 | false | True | 5 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:16` | unresolved | unresolved |
| 16 | [Beach Tamer](https://tibia.fandom.com/wiki/Beach_Tamer) | 1 | false | True | 2 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:17` | unresolved | unresolved |
| 17 | [Follower of Azerus](https://tibia.fandom.com/wiki/Follower_of_Azerus) | 2 | false | True | 4 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:18` | unresolved | unresolved |
| 18 | [Follower of Palimuth](https://tibia.fandom.com/wiki/Follower_of_Palimuth) | 2 | false | True | 4 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:19` | unresolved | unresolved |
| 19 | [Elite Hunter](https://tibia.fandom.com/wiki/Elite_Hunter) | 2 | false | True | 5 | June 30, 2010 | quest-or-task, combat | confirmed | `data/scripts/lib/register_achievements.lua:20` | unresolved | unresolved |
| 20 | [Huntsman](https://tibia.fandom.com/wiki/Huntsman_(Achievement)) | 1 | false | True | 2 | June 30, 2010 | quest-or-task, combat | confirmed | `data/scripts/lib/register_achievements.lua:21` | unresolved | unresolved |
| 21 | [Passionate Kisser](https://tibia.fandom.com/wiki/Passionate_Kisser) | 1 | false | False | 3 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:22` | unresolved | unresolved |
| 22 | [Top AVIN Agent](https://tibia.fandom.com/wiki/Top_AVIN_Agent) | 2 | false | True | 4 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:23` | partially-confirmed | `data-otservbr-global/npc/uncle.lua:110` addAchievement |
| 23 | [Top CGB Agent](https://tibia.fandom.com/wiki/Top_CGB_Agent) | 2 | false | True | 4 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:24` | partially-confirmed | `data-otservbr-global/npc/emma.lua:122` addAchievement |
| 24 | [Top TBI Agent](https://tibia.fandom.com/wiki/Top_TBI_Agent) | 2 | false | True | 4 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:25` | unresolved | unresolved |
| 25 | [Secret Agent](https://tibia.fandom.com/wiki/Secret_Agent) | 1 | false | False | 1 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:26` | partially-confirmed | `data-otservbr-global/npc/emma.lua:65` addAchievement; `data-otservbr-global/npc/uncle.lua:65` addAchievement |
| 26 | [Golem in the Gears](https://tibia.fandom.com/wiki/Golem_in_the_Gears) | 2 | false | True | 4 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:27` | unresolved | unresolved |
| 27 | [Poet Laureate](https://tibia.fandom.com/wiki/Poet_Laureate) | 1 | true | True | 2 | June 30, 2010 | quest-or-task, collection, exploration | confirmed | `data/scripts/lib/register_achievements.lua:28` | unresolved | unresolved |
| 28 | [Minstrel](https://tibia.fandom.com/wiki/Minstrel) | 1 | true | True | 2 | June 30, 2010 | item-or-interaction, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:29` | unresolved | unresolved |
| 29 | [Friend of the Apes](https://tibia.fandom.com/wiki/Friend_of_the_Apes) | 2 | false | True | 4 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:30` | partially-confirmed | `data-otservbr-global/npc/hairycles.lua:192` addAchievement |
| 30 | [Territorial](https://tibia.fandom.com/wiki/Territorial) | 1 | true | True | 1 | June 30, 2010 | dialogue | confirmed | `data/scripts/lib/register_achievements.lua:31` | unresolved | unresolved |
| 31 | [Marid Ally](https://tibia.fandom.com/wiki/Marid_Ally) | 1 | false | True | 3 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:32` | partially-confirmed | `data-otservbr-global/npc/gabel.lua:138` addAchievement |
| 32 | [Efreet Ally](https://tibia.fandom.com/wiki/Efreet_Ally) | 1 | false | True | 3 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:33` | partially-confirmed | `data-otservbr-global/npc/malor.lua:149` addAchievement |
| 33 | [Lucid Dreamer](https://tibia.fandom.com/wiki/Lucid_Dreamer) | 1 | false | True | 2 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:34` | unresolved | unresolved |
| 34 | [Explorer](https://tibia.fandom.com/wiki/Explorer) | 2 | false | True | 4 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:35` | unresolved | unresolved |
| 35 | [Sea Scout](https://tibia.fandom.com/wiki/Sea_Scout) | 1 | false | True | 2 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:36` | unresolved | unresolved |
| 36 | [Unlikely Pathfinder](https://tibia.fandom.com/wiki/Unlikely_Pathfinder) | 1 | true | True | 2 | June 30, 2010 | exploration | confirmed | `data/scripts/lib/register_achievements.lua:37` | unresolved | unresolved |
| 37 | [Bearhugger](https://tibia.fandom.com/wiki/Bearhugger) | 1 | false | True | 1 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:38` | partially-confirmed | `data-otservbr-global/scripts/quests/barbarian_test/action_horn.lua:24` addAchievement |
| 38 | [Ghostwhisperer](https://tibia.fandom.com/wiki/Ghostwhisperer) | 1 | false | True | 3 | June 30, 2010 | quest-or-task, dialogue | confirmed | `data/scripts/lib/register_achievements.lua:39` | unresolved | unresolved |
| 39 | [Animal Activist](https://tibia.fandom.com/wiki/Animal_Activist) | 1 | false | True | 2 | June 30, 2010 | quest-or-task, combat | confirmed | `data/scripts/lib/register_achievements.lua:40` | partially-confirmed | `data-otservbr-global/npc/duncan.lua:168` addAchievement; `data-otservbr-global/scripts/quests/the_ice_islands_quest/actions_paint.lua:23` addAchievement |
| 40 | [Honorary Barbarian](https://tibia.fandom.com/wiki/Honorary_Barbarian) | 1 | false | True | 1 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:41` | partially-confirmed | `data-otservbr-global/npc/sven.lua:113` addAchievement |
| 41 | [High Inquisitor](https://tibia.fandom.com/wiki/High_Inquisitor) | 2 | false | True | 5 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:42` | partially-confirmed | `data-otservbr-global/npc/henricus.lua:239` addAchievement |
| 42 | [Worm Whacker](https://tibia.fandom.com/wiki/Worm_Whacker) | 1 | true | False | 1 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:43` | unresolved | unresolved |
| 43 | [King Tibianus Fan](https://tibia.fandom.com/wiki/King_Tibianus_Fan) | 1 | false | True | 3 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:44` | unresolved | unresolved |
| 44 | [Just in Time](https://tibia.fandom.com/wiki/Just_in_Time) | 1 | false | True | 1 | June 30, 2010 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:45` | unresolved | unresolved |
| 45 | [Perfect Fool](https://tibia.fandom.com/wiki/Perfect_Fool) | 1 | false | True | 3 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:46` | partially-confirmed | `data-otservbr-global/npc/bozo.lua:755` addAchievement |
| 46 | [Mathemagician](https://tibia.fandom.com/wiki/Mathemagician) | 1 | false | True | 1 | June 30, 2010 | quest-or-task, dialogue | confirmed | `data/scripts/lib/register_achievements.lua:47` | partially-confirmed | `data-otservbr-global/npc/a_prisoner.lua:129` addAchievement |
| 47 | [Archpostman](https://tibia.fandom.com/wiki/Archpostman) | 1 | false | True | 3 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:48` | partially-confirmed | `data-otservbr-global/npc/kevin.lua:297` addAchievement |
| 48 | [Matchmaker](https://tibia.fandom.com/wiki/Matchmaker) | 1 | false | False | 1 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:49` | partially-confirmed | `data-otservbr-global/npc/marina.lua:87` addAchievement |
| 49 | [His True Face](https://tibia.fandom.com/wiki/His_True_Face) | 1 | true | True | 3 | June 30, 2010 | quest-or-task, exploration, dialogue | confirmed | `data/scripts/lib/register_achievements.lua:50` | unresolved | unresolved |
| 50 | [Razing!](https://tibia.fandom.com/wiki/Razing!) | 3 | true | False | 7 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:51` | unresolved | unresolved |
| 51 | [Master Thief](https://tibia.fandom.com/wiki/Master_Thief) | 2 | false | True | 4 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:52` | unresolved | unresolved |
| 52 | [Amateur Actor](https://tibia.fandom.com/wiki/Amateur_Actor) | 1 | false | True | 2 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:53` | unresolved | unresolved |
| 53 | [Scrapper](https://tibia.fandom.com/wiki/Scrapper) | 1 | false | True | 3 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:54` | unresolved | unresolved |
| 54 | [Greenhorn](https://tibia.fandom.com/wiki/Greenhorn) | 1 | false | True | 2 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:55` | unresolved | unresolved |
| 55 | [Warlord of Svargrond](https://tibia.fandom.com/wiki/Warlord_of_Svargrond) | 2 | false | True | 5 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:56` | unresolved | `data-otservbr-global/npc/iskan.lua:60` hasAchievement |
| 56 | [Herbicide](https://tibia.fandom.com/wiki/Herbicide) | 3 | true | True | 8 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:57` | unresolved | unresolved |
| 57 | [Annihilator](https://tibia.fandom.com/wiki/Annihilator) | 2 | false | True | 5 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:58` | unresolved | unresolved |
| 58 | [Master of the Nexus](https://tibia.fandom.com/wiki/Master_of_the_Nexus) | 2 | false | True | 6 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:59` | partially-confirmed | `data-otservbr-global/scripts/quests/the_inquisition_quest/actions_rewards.lua:21` addAchievement |
| 59 | [Talented Dancer](https://tibia.fandom.com/wiki/Talented_Dancer) | 1 | false | True | 1 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:60` | partially-confirmed | `data-otservbr-global/scripts/quests/unnatural_selection/movements_mission3_dance_dance_evolution.lua:60` addAchievement |
| 60 | [Allow Cookies?](https://tibia.fandom.com/wiki/Allow_Cookies%3F) | 1 | false | True | 2 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:61` | partially-confirmed | `data-otservbr-global/npc/ariella.lua:107` addAchievement; `data-otservbr-global/npc/avar_tar.lua:87` addAchievement; `data-otservbr-global/npc/hairycles.lua:473` addAchievement; `data-otservbr-global/npc/hjaern.lua:219` addAchievement; `data-otservbr-global/npc/lorbas.lua:78` addAchievement; `data-otservbr-global/npc/markwin.lua:117` addAchievement; `data-otservbr-global/npc/nah_bob.lua:107` addAchievement; `data-otservbr-global/npc/simon_the_beggar.lua:252` addAchievement; `data-otservbr-global/npc/the_orc_king.lua:122` addAchievement; `data-otservbr-global/npc/wyda.lua:99` addAchievement; `data-otservbr-global/npc/yaman.lua:136` addAchievement |
| 61 | [Ruthless](https://tibia.fandom.com/wiki/Ruthless) | 2 | false | True | 5 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:62` | unresolved | unresolved |
| 62 | [Champion of Chazorai](https://tibia.fandom.com/wiki/Champion_of_Chazorai) | 2 | false | True | 4 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:63` | partially-confirmed | `data-otservbr-global/scripts/quests/the_new_frontier/creaturescripts_tirecz_kill.lua:26` addAchievement |
| 63 | [Wayfarer](https://tibia.fandom.com/wiki/Wayfarer) | 1 | true | True | 3 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:64` | partially-confirmed | `data-otservbr-global/npc/a_sleeping_dragon.lua:197` addAchievement |
| 64 | [Waverider](https://tibia.fandom.com/wiki/Waverider) | 1 | true | False | 2 | June 30, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:65` | unresolved | unresolved |
| 65 | [Rockstar](https://tibia.fandom.com/wiki/Rockstar) | 1 | true | False | 3 | June 30, 2010 | item-or-interaction, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:66` | partially-confirmed | `data-otservbr-global/scripts/actions/other/music.lua:63` addAchievementProgress |
| 66 | [Allowance Collector](https://tibia.fandom.com/wiki/Allowance_Collector) | 1 | true | False | 2 | June 30, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:67` | partially-confirmed | `data/scripts/actions/items/piggy_bank.lua:9` addAchievementProgress |
| 67 | [High-Flyer](https://tibia.fandom.com/wiki/High-Flyer) | 2 | true | True | 4 | June 30, 2010 | quest-or-task, exploration, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:68` | unresolved | unresolved |
| 68 | [Clay Fighter](https://tibia.fandom.com/wiki/Clay_Fighter) | 1 | true | False | 3 | June 30, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:69` | partially-confirmed | `data/scripts/actions/items/clay_lump.lua:31` addAchievement |
| 69 | [Masquerader](https://tibia.fandom.com/wiki/Masquerader) | 1 | true | False | 3 | June 30, 2010 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:70` | partially-confirmed | `data/scripts/actions/items/costume_bags.lua:17` addAchievementProgress |
| 70 | [Deep Sea Diver](https://tibia.fandom.com/wiki/Deep_Sea_Diver) | 2 | true | True | 4 | June 30, 2010 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:71` | unresolved | unresolved |
| 71 | [Firewalker](https://tibia.fandom.com/wiki/Firewalker) | 2 | true | False | 4 | June 30, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:72` | unresolved | unresolved |
| 72 | [Here, Fishy Fishy!](https://tibia.fandom.com/wiki/Here,_Fishy_Fishy!) | 1 | true | False | 1 | June 30, 2010 | event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:73` | partially-confirmed | `data-otservbr-global/scripts/actions/other/fishing.lua:134` addAchievementProgress |
| 73 | [Green Thumb](https://tibia.fandom.com/wiki/Green_Thumb) | 2 | true | False | 4 | June 30, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:74` | unresolved | unresolved |
| 74 | [Potion Addict](https://tibia.fandom.com/wiki/Potion_Addict) | 2 | true | False | 4 | June 30, 2010 | item-or-interaction, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:75` | partially-confirmed | `data/scripts/actions/items/potions.lua:107` addAchievementProgress |
| 75 | [Ice Sculptor](https://tibia.fandom.com/wiki/Ice_Sculptor) | 1 | true | False | 3 | June 30, 2010 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:76` | partially-confirmed | `data-otservbr-global/scripts/actions/tools/skinning.lua:246` addAchievement |
| 76 | [Interior Decorator](https://tibia.fandom.com/wiki/Interior_Decorator) | 2 | true | False | 4 | June 30, 2010 | collection, item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:77` | partially-confirmed | `data-otservbr-global/scripts/actions/other/construction_kits.lua:131` addAchievementProgress |
| 77 | [Jinx](https://tibia.fandom.com/wiki/Jinx) | 1 | true | False | 2 | June 30, 2010 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:78` | unresolved | unresolved |
| 78 | [Lucky Devil](https://tibia.fandom.com/wiki/Lucky_Devil) | 2 | true | False | 4 | June 30, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:79` | unresolved | unresolved |
| 79 | [Marblelous](https://tibia.fandom.com/wiki/Marblelous) | 1 | true | False | 3 | June 30, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:80` | partially-confirmed | `data-otservbr-global/scripts/actions/tools/skinning.lua:224` addAchievement |
| 80 | [Party Animal](https://tibia.fandom.com/wiki/Party_Animal) | 1 | true | False | 1 | June 30, 2010 | item-or-interaction, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:81` | partially-confirmed | `data/scripts/actions/items/party_hat.lua:10` addAchievementProgress |
| 81 | [Fireworks in the Sky](https://tibia.fandom.com/wiki/Fireworks_in_the_Sky) | 1 | true | False | 2 | June 30, 2010 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:82` | partially-confirmed | `data/scripts/actions/items/fireworks_rocket.lua:14` addAchievementProgress |
| 82 | [Quick as a Turtle](https://tibia.fandom.com/wiki/Quick_as_a_Turtle) | 1 | true | True | 2 | June 30, 2010 | exploration, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:83` | unresolved | unresolved |
| 83 | [Polisher](https://tibia.fandom.com/wiki/Polisher) | 2 | true | False | 4 | June 30, 2010 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:84` | partially-confirmed | `data/scripts/actions/items/rust_remover.lua:107` addAchievementProgress |
| 84 | [Ship's Kobold](https://tibia.fandom.com/wiki/Ship%27s_Kobold) | 2 | true | True | 4 | June 30, 2010 | exploration, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:85` | partially-confirmed | `data/npclib/npc_system/modules.lua:248` addAchievementProgress |
| 85 | [Steampunked](https://tibia.fandom.com/wiki/Steampunked) | 1 | true | False | 2 | June 30, 2010 | quest-or-task, exploration, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:86` | unresolved | unresolved |
| 86 | [Vanity](https://tibia.fandom.com/wiki/Vanity) | 1 | true | False | 3 | June 30, 2010 | item-or-interaction, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:87` | unresolved | unresolved |
| 87 | [Superstitious](https://tibia.fandom.com/wiki/Superstitious) | 1 | true | False | 2 | June 30, 2010 | item-or-interaction, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:88` | unresolved | unresolved |
| 88 | [Turncoat](https://tibia.fandom.com/wiki/Turncoat) | 2 | true | True | 4 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:89` | unresolved | unresolved |
| 89 | [Marble Madness](https://tibia.fandom.com/wiki/Marble_Madness) | 2 | true | False | 6 | June 30, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:90` | partially-confirmed | `data-otservbr-global/scripts/actions/tools/skinning.lua:225` addAchievementProgress |
| 90 | [Clay to Fame](https://tibia.fandom.com/wiki/Clay_to_Fame) | 2 | true | False | 6 | June 30, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:91` | partially-confirmed | `data/scripts/actions/items/clay_lump.lua:32` addAchievementProgress |
| 91 | [Cold as Ice](https://tibia.fandom.com/wiki/Cold_as_Ice) | 2 | true | False | 6 | June 30, 2010 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:92` | partially-confirmed | `data-otservbr-global/scripts/actions/tools/skinning.lua:247` addAchievementProgress |
| 92 | [Exquisite Taste](https://tibia.fandom.com/wiki/Exquisite_Taste) | 1 | true | True | 2 | June 30, 2010 | collection | confirmed | `data/scripts/lib/register_achievements.lua:93` | partially-confirmed | `data-otservbr-global/scripts/actions/other/fishing.lua:121` addAchievementProgress; `data-otservbr-global/scripts/actions/other/fishing.lua:125` addAchievementProgress; `data-otservbr-global/scripts/actions/other/fishing.lua:129` addAchievementProgress |
| 93 | [Jamjam](https://tibia.fandom.com/wiki/Jamjam) | 2 | true | True | 5 | June 30, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:94` | unresolved | unresolved |
| 94 | [I Did My Part](https://tibia.fandom.com/wiki/I_Did_My_Part) | 1 | true | False | 2 | August 23, 2010 | quest-or-task, combat, item-or-interaction, exploration | confirmed | `data/scripts/lib/register_achievements.lua:95` | unresolved | unresolved |
| 96 | [Teamplayer](https://tibia.fandom.com/wiki/Teamplayer) | 1 | true | False | 2 | August 23, 2010 | quest-or-task, combat, exploration | confirmed | `data/scripts/lib/register_achievements.lua:97` | unresolved | unresolved |
| 97 | [Daring Trespasser](https://tibia.fandom.com/wiki/Daring_Trespasser) | 1 | true | True | 3 | August 23, 2010 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:98` | unresolved | unresolved |
| 98 | [Slayer of Anmothra](https://tibia.fandom.com/wiki/Slayer_of_Anmothra) | 1 | true | False | 2 | August 23, 2010 | quest-or-task, combat, event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:99` | unresolved | unresolved |
| 99 | [Slayer of Chikhaton](https://tibia.fandom.com/wiki/Slayer_of_Chikhaton) | 1 | true | True | 2 | August 23, 2010 | quest-or-task, combat, event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:100` | unresolved | unresolved |
| 100 | [Slayer of Irahsae](https://tibia.fandom.com/wiki/Slayer_of_Irahsae) | 1 | true | True | 2 | August 23, 2010 | quest-or-task, combat, event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:101` | unresolved | unresolved |
| 101 | [Slayer of Phrodomo](https://tibia.fandom.com/wiki/Slayer_of_Phrodomo) | 1 | true | False | 2 | August 23, 2010 | quest-or-task, combat, event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:102` | unresolved | unresolved |
| 102 | [Slayer of Teneshpar](https://tibia.fandom.com/wiki/Slayer_of_Teneshpar) | 1 | true | False | 2 | August 23, 2010 | quest-or-task, combat, event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:103` | unresolved | unresolved |
| 103 | [Cocoon of Doom](https://tibia.fandom.com/wiki/Cocoon_of_Doom) | 1 | true | True | 3 | August 23, 2010 | quest-or-task, combat | confirmed | `data/scripts/lib/register_achievements.lua:104` | unresolved | unresolved |
| 104 | [Devovorga's Nemesis](https://tibia.fandom.com/wiki/Devovorga%27s_Nemesis) | 2 | true | True | 5 | August 23, 2010 | quest-or-task, combat | confirmed | `data/scripts/lib/register_achievements.lua:105` | unresolved | unresolved |
| 105 | [Mister Sandman](https://tibia.fandom.com/wiki/Mister_Sandman) | 1 | true | True | 2 | September 22, 2010 | item-or-interaction, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:106` | unresolved | unresolved |
| 106 | [Rock Me to Sleep](https://tibia.fandom.com/wiki/Rock_Me_to_Sleep) | 1 | true | True | 1 | September 22, 2010 | item-or-interaction, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:107` | unresolved | unresolved |
| 107 | [Modest Guest](https://tibia.fandom.com/wiki/Modest_Guest) | 1 | true | True | 1 | September 22, 2010 | progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:108` | unresolved | unresolved |
| 108 | [Joke's on You](https://tibia.fandom.com/wiki/Joke%27s_on_You) | 1 | true | False | 1 | September 22, 2010 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:109` | partially-confirmed | `data/scripts/actions/items/explosive_present.lua:6` addAchievement |
| 109 | [Oops](https://tibia.fandom.com/wiki/Oops) | 1 | true | False | 2 | September 22, 2010 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:110` | partially-confirmed | `data-otservbr-global/scripts/actions/other/birdcage.lua:6` addAchievement |
| 110 | [Bluebarian](https://tibia.fandom.com/wiki/Bluebarian) | 1 | true | False | 2 | September 22, 2010 | item-or-interaction, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:111` | partially-confirmed | `data/scripts/actions/items/blueberry_bush.lua:7` addAchievementProgress |
| 111 | [Demonic Barkeeper](https://tibia.fandom.com/wiki/Demonic_Barkeeper) | 1 | false | False | 3 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:112` | partially-confirmed | `data/scripts/actions/items/potions.lua:143` addAchievementProgress |
| 112 | [The Snowman](https://tibia.fandom.com/wiki/The_Snowman) | 1 | true | False | 1 | September 22, 2010 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:113` | unresolved | unresolved |
| 113 | [Number of the Beast](https://tibia.fandom.com/wiki/Number_of_the_Beast) | 1 | false | False | 2 | September 22, 2010 | progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:114` | partially-confirmed | `data/scripts/actions/items/die.lua:22` addAchievement |
| 114 | [I Need a Hug](https://tibia.fandom.com/wiki/I_Need_a_Hug) | 1 | false | False | 2 | September 22, 2010 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:115` | unresolved | unresolved |
| 115 | [Slim Chance](https://tibia.fandom.com/wiki/Slim_Chance) | 1 | false | False | 1 | September 22, 2010 | item-or-interaction, exploration, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:116` | unresolved | unresolved |
| 116 | [Rocket in Pocket](https://tibia.fandom.com/wiki/Rocket_in_Pocket) | 1 | true | False | 1 | September 22, 2010 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:117` | partially-confirmed | `data/scripts/actions/items/fireworks_rocket.lua:10` addAchievementProgress |
| 117 | [Make a Wish](https://tibia.fandom.com/wiki/Make_a_Wish) | 1 | true | False | 1 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:118` | unresolved | unresolved |
| 118 | [Santa's Li'l Helper](https://tibia.fandom.com/wiki/Santa%27s_Li%27l_Helper) | 1 | true | False | 2 | September 22, 2010 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:119` | unresolved | unresolved |
| 119 | [Cursed!](https://tibia.fandom.com/wiki/Cursed!) | 1 | true | False | 3 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:120` | partially-confirmed | `data/scripts/actions/tools/claw_of_the_noxious_spawn.lua:19` addAchievement |
| 120 | [Free Items!](https://tibia.fandom.com/wiki/Free_Items!) | 1 | true | False | 3 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:121` | unresolved | unresolved |
| 121 | [Rollercoaster](https://tibia.fandom.com/wiki/Rollercoaster) | 1 | false | False | 1 | September 22, 2010 | progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:122` | partially-confirmed | `data-otservbr-global/scripts/actions/kazordoon/ore_wagons.lua:63` addAchievementProgress |
| 122 | [Transmutator](https://tibia.fandom.com/wiki/Transmutator) | 2 | true | True | 5 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:123` | unresolved | unresolved |
| 123 | [Berserker](https://tibia.fandom.com/wiki/Berserker_(Achievement)) | 1 | false | False | 3 | September 22, 2010 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:124` | unresolved | unresolved |
| 124 | [Mastermind](https://tibia.fandom.com/wiki/Mastermind) | 1 | false | False | 3 | September 22, 2010 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:125` | unresolved | unresolved |
| 125 | [Sharpshooter](https://tibia.fandom.com/wiki/Sharpshooter_(Achievement)) | 1 | false | False | 3 | September 22, 2010 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:126` | unresolved | unresolved |
| 126 | [Do Not Disturb](https://tibia.fandom.com/wiki/Do_Not_Disturb) | 1 | true | False | 1 | September 22, 2010 | progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:127` | unresolved | unresolved |
| 127 | [Let the Sunshine In](https://tibia.fandom.com/wiki/Let_the_Sunshine_In) | 1 | true | False | 1 | September 22, 2010 | item-or-interaction, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:128` | unresolved | unresolved |
| 128 | [Bad Timing](https://tibia.fandom.com/wiki/Bad_Timing) | 1 | true | False | 2 | September 22, 2010 | progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:129` | partially-confirmed | `data/scripts/actions/tools/toolgear.lua:15` addAchievementProgress |
| 129 | [Nothing Can Stop Me](https://tibia.fandom.com/wiki/Nothing_Can_Stop_Me) | 1 | true | False | 1 | September 22, 2010 | item-or-interaction, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:130` | unresolved | unresolved |
| 130 | [Happy Farmer](https://tibia.fandom.com/wiki/Happy_Farmer) | 1 | true | False | 1 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:131` | unresolved | unresolved |
| 131 | [Natural Sweetener](https://tibia.fandom.com/wiki/Natural_Sweetener) | 1 | true | True | 1 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:132` | unresolved | unresolved |
| 132 | [Homebrewed](https://tibia.fandom.com/wiki/Homebrewed) | 1 | true | True | 1 | September 22, 2010 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:133` | unresolved | unresolved |
| 133 | [Gold Digger](https://tibia.fandom.com/wiki/Gold_Digger) | 2 | true | True | 4 | September 22, 2010 | exploration | confirmed | `data/scripts/lib/register_achievements.lua:134` | partially-confirmed | `data-otservbr-global/scripts/lib/register_actions.lua:420` addAchievementProgress |
| 134 | [The Undertaker](https://tibia.fandom.com/wiki/The_Undertaker) | 1 | true | False | 2 | September 22, 2010 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:135` | partially-confirmed | `data-otservbr-global/scripts/lib/register_actions.lua:410` addAchievementProgress |
| 135 | [Cookie Monster](https://tibia.fandom.com/wiki/Cookie_Monster) | 1 | true | False | 1 | September 22, 2010 | progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:136` | unresolved | unresolved |
| 136 | [The Cake's the Truth](https://tibia.fandom.com/wiki/The_Cake%27s_the_Truth) | 1 | true | False | 1 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:137` | unresolved | unresolved |
| 137 | [Sweet Tooth](https://tibia.fandom.com/wiki/Sweet_Tooth) | 1 | true | False | 2 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:138` | unresolved | unresolved |
| 138 | [With a Cherry on Top](https://tibia.fandom.com/wiki/With_a_Cherry_on_Top) | 1 | true | False | 1 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:139` | unresolved | unresolved |
| 139 | [Mutated Presents](https://tibia.fandom.com/wiki/Mutated_Presents) | 1 | true | True | 1 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:140` | partially-confirmed | `data-otservbr-global/scripts/actions/tools/skinning.lua:188` addAchievement |
| 140 | [Keeper of the Flame](https://tibia.fandom.com/wiki/Keeper_of_the_Flame) | 1 | true | False | 2 | September 22, 2010 | event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:141` | unresolved | unresolved |
| 141 | [True Lightbearer](https://tibia.fandom.com/wiki/True_Lightbearer) | 2 | true | True | 5 | September 22, 2010 | event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:142` | unresolved | unresolved |
| 142 | [Godslayer](https://tibia.fandom.com/wiki/Godslayer) | 2 | false | True | 4 | September 22, 2010 | quest-or-task, item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:143` | unresolved | unresolved |
| 143 | [The Day After](https://tibia.fandom.com/wiki/The_Day_After) | 1 | true | False | 2 | September 22, 2010 | dialogue | confirmed | `data/scripts/lib/register_achievements.lua:144` | unresolved | unresolved |
| 144 | [Commitment Phobic](https://tibia.fandom.com/wiki/Commitment_Phobic) | 1 | true | False | 2 | September 22, 2010 | collection, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:145` | unresolved | unresolved |
| 145 | [Heartbreaker](https://tibia.fandom.com/wiki/Heartbreaker) | 1 | true | False | 1 | September 22, 2010 | dialogue, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:146` | unresolved | unresolved |
| 146 | [Swift Death](https://tibia.fandom.com/wiki/Swift_Death) | 2 | false | True | 6 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:147` | unresolved | unresolved |
| 147 | [Brutal Politeness](https://tibia.fandom.com/wiki/Brutal_Politeness) | 2 | false | True | 6 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:148` | partially-confirmed | `data-otservbr-global/npc/ajax.lua:143` addAchievement |
| 148 | [Life on the Streets](https://tibia.fandom.com/wiki/Life_on_the_Streets) | 2 | false | True | 4 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:149` | unresolved | unresolved |
| 149 | [Skull and Bones](https://tibia.fandom.com/wiki/Skull_and_Bones) | 2 | false | True | 6 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:150` | partially-confirmed | `data-otservbr-global/npc/the_bone_master.lua:117` addAchievement |
| 150 | [Nightmare Walker](https://tibia.fandom.com/wiki/Nightmare_Walker) | 2 | false | True | 6 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:151` | partially-confirmed | `data-otservbr-global/npc/the_dream_master.lua:113` addAchievement |
| 151 | [Exemplary Citizen](https://tibia.fandom.com/wiki/Exemplary_Citizen) | 2 | false | True | 4 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:152` | unresolved | unresolved |
| 152 | [Demonbane](https://tibia.fandom.com/wiki/Demonbane) | 2 | false | True | 6 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:153` | partially-confirmed | `data-otservbr-global/npc/henricus.lua:301` addAchievement |
| 153 | [Of Wolves and Bears](https://tibia.fandom.com/wiki/Of_Wolves_and_Bears) | 2 | false | True | 6 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:154` | unresolved | unresolved |
| 154 | [Hunting with Style](https://tibia.fandom.com/wiki/Hunting_with_Style) | 2 | false | True | 6 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:155` | unresolved | unresolved |
| 155 | [Fool at Heart](https://tibia.fandom.com/wiki/Fool_at_Heart) | 1 | false | True | 3 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:156` | partially-confirmed | `data-otservbr-global/npc/bozo.lua:756` addAchievement |
| 156 | [In Shining Armor](https://tibia.fandom.com/wiki/In_Shining_Armor) | 2 | false | True | 6 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:157` | unresolved | unresolved |
| 157 | [Aristocrat](https://tibia.fandom.com/wiki/Aristocrat) | 2 | false | True | 4 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:158` | unresolved | unresolved |
| 158 | [Out in the Snowstorm](https://tibia.fandom.com/wiki/Out_in_the_Snowstorm) | 2 | false | True | 4 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:159` | unresolved | unresolved |
| 159 | [One Thousand and One](https://tibia.fandom.com/wiki/One_Thousand_and_One) | 2 | false | True | 6 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:160` | unresolved | unresolved |
| 160 | [Swashbuckler](https://tibia.fandom.com/wiki/Swashbuckler) | 2 | false | True | 6 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:161` | unresolved | unresolved |
| 161 | [Way of the Shaman](https://tibia.fandom.com/wiki/Way_of_the_Shaman) | 2 | false | True | 6 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:162` | partially-confirmed | `data-otservbr-global/npc/chondur.lua:101` addAchievement; `data-otservbr-global/npc/chondur.lua:117` addAchievement |
| 162 | [Ritualist](https://tibia.fandom.com/wiki/Ritualist) | 2 | false | True | 6 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:163` | unresolved | unresolved |
| 163 | [Master of War](https://tibia.fandom.com/wiki/Master_of_War) | 2 | false | True | 6 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:164` | unresolved | unresolved |
| 164 | [Wild Warrior](https://tibia.fandom.com/wiki/Wild_Warrior_(Achievement)) | 2 | false | True | 6 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:165` | partially-confirmed | `data-otservbr-global/npc/cornelia.lua:84` addAchievementProgress; `data-otservbr-global/npc/morgan.lua:102` addAchievementProgress |
| 165 | [Peazzekeeper](https://tibia.fandom.com/wiki/Peazzekeeper) | 2 | false | True | 6 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:166` | unresolved | unresolved |
| 166 | [Yalahari of Wisdom](https://tibia.fandom.com/wiki/Yalahari_of_Wisdom) | 1 | false | True | 3 | September 22, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:167` | unresolved | unresolved |
| 167 | [Yalahari of Power](https://tibia.fandom.com/wiki/Yalahari_of_Power) | 1 | false | True | 3 | September 22, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:168` | unresolved | unresolved |
| 168 | [Piece of Cake](https://tibia.fandom.com/wiki/Piece_of_Cake) | 1 | false | False | 1 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:169` | unresolved | unresolved |
| 169 | [Alumni](https://tibia.fandom.com/wiki/Alumni) | 2 | false | True | 6 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:170` | unresolved | unresolved |
| 170 | [Warlock](https://tibia.fandom.com/wiki/Warlock_(Achievement)) | 2 | false | True | 6 | September 22, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:171` | partially-confirmed | `data-otservbr-global/npc/the_queen_of_the_banshees.lua:165` addAchievement |
| 171 | [Bunny Slipped](https://tibia.fandom.com/wiki/Bunny_Slipped) | 1 | true | False | 2 | December 8, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:172` | unresolved | unresolved |
| 172 | [Guinea Pig](https://tibia.fandom.com/wiki/Guinea_Pig) | 1 | false | True | 2 | December 8, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:173` | unresolved | unresolved |
| 173 | [Merry Adventures](https://tibia.fandom.com/wiki/Merry_Adventures) | 1 | false | False | 2 | December 8, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:174` | unresolved | unresolved |
| 174 | [Afraid of no Ghost!](https://tibia.fandom.com/wiki/Afraid_of_no_Ghost!) | 1 | false | True | 2 | December 8, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:175` | unresolved | unresolved |
| 175 | [Extreme Degustation](https://tibia.fandom.com/wiki/Extreme_Degustation) | 1 | true | True | 2 | December 8, 2010 | quest-or-task, collection | confirmed | `data/scripts/lib/register_achievements.lua:176` | unresolved | unresolved |
| 176 | [Cake Conqueror](https://tibia.fandom.com/wiki/Cake_Conqueror) | 1 | true | True | 1 | December 8, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:177` | unresolved | unresolved |
| 177 | [Baby Sitter](https://tibia.fandom.com/wiki/Baby_Sitter) | 1 | true | False | 1 | December 8, 2010 | event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:178` | unresolved | unresolved |
| 178 | [Nanny from Hell](https://tibia.fandom.com/wiki/Nanny_from_Hell) | 1 | true | False | 3 | December 8, 2010 | event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:179` | unresolved | unresolved |
| 179 | [Ghost Sailor](https://tibia.fandom.com/wiki/Ghost_Sailor) | 1 | true | False | 1 | December 8, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:180` | unresolved | unresolved |
| 180 | [Spectral Traveller](https://tibia.fandom.com/wiki/Spectral_Traveller) | 1 | true | False | 2 | December 8, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:181` | unresolved | unresolved |
| 181 | [Nether Pirate](https://tibia.fandom.com/wiki/Nether_Pirate) | 1 | true | False | 3 | December 8, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:182` | unresolved | unresolved |
| 182 | [Scourge of Death](https://tibia.fandom.com/wiki/Scourge_of_Death) | 2 | true | False | 5 | December 8, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:183` | unresolved | unresolved |
| 183 | [Fire Lighter](https://tibia.fandom.com/wiki/Fire_Lighter) | 1 | true | False | 1 | December 8, 2010 | item-or-interaction, event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:184` | unresolved | unresolved |
| 184 | [Witches Lil' Helper](https://tibia.fandom.com/wiki/Witches_Lil%27_Helper) | 1 | true | False | 1 | December 8, 2010 | event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:185` | unresolved | unresolved |
| 185 | [Banebringers' Bane](https://tibia.fandom.com/wiki/Banebringers%27_Bane) | 1 | true | False | 2 | December 8, 2010 | event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:186` | unresolved | unresolved |
| 186 | [Fire Devil](https://tibia.fandom.com/wiki/Fire_Devil_(Achievement)) | 1 | true | False | 3 | December 8, 2010 | item-or-interaction, event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:187` | unresolved | unresolved |
| 187 | [Pyromaniac](https://tibia.fandom.com/wiki/Pyromaniac) | 2 | true | False | 4 | December 8, 2010 | item-or-interaction, event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:188` | unresolved | unresolved |
| 188 | [Honorary Witch](https://tibia.fandom.com/wiki/Honorary_Witch) | 2 | true | False | 4 | December 8, 2010 | event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:189` | unresolved | unresolved |
| 189 | [Natural Born Cowboy](https://tibia.fandom.com/wiki/Natural_Born_Cowboy) | 1 | true | False | 1 | December 8, 2010 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:190` | partially-confirmed | `data/scripts/actions/items/music_box.lua:30` addAchievement; `data/scripts/actions/items/usable_mount_items.lua:31` addAchievement; `data/scripts/actions/items/usable_phantasmal_jade_items.lua:35` addAchievement; `data-otservbr-global/npc/appaloosa.lua:100` addAchievement; `data-otservbr-global/npc/palomino.lua:101` addAchievement; `data-otservbr-global/scripts/actions/mounts/mounts.lua:108` addAchievement; `data-otservbr-global/scripts/actions/mounts/mounts.lua:123` addAchievement; `data-otservbr-global/scripts/actions/mounts/mounts.lua:141` addAchievement; `data-otservbr-global/scripts/actions/mounts/mounts.lua:161` addAchievement; `data-otservbr-global/scripts/actions/mounts/mounts.lua:178` addAchievement; `data-otservbr-global/scripts/actions/mounts/mounts.lua:195` addAchievement |
| 190 | [Petrologist](https://tibia.fandom.com/wiki/Petrologist) | 1 | true | False | 2 | December 8, 2010 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:191` | partially-confirmed | `data-otservbr-global/scripts/lib/register_actions.lua:601` addAchievementProgress |
| 191 | [Hidden Powers](https://tibia.fandom.com/wiki/Hidden_Powers) | 1 | false | False | 2 | December 8, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:192` | unresolved | unresolved |
| 192 | [I Like it Fancy](https://tibia.fandom.com/wiki/I_Like_it_Fancy) | 1 | true | False | 1 | December 8, 2010 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:193` | unresolved | unresolved |
| 193 | [Skin-Deep](https://tibia.fandom.com/wiki/Skin-Deep) | 2 | true | False | 4 | December 8, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:194` | partially-confirmed | `data-otservbr-global/scripts/actions/tools/skinning.lua:256` addAchievementProgress |
| 194 | [Ashes to Dust](https://tibia.fandom.com/wiki/Ashes_to_Dust) | 2 | true | False | 4 | December 8, 2010 | item-or-interaction, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:195` | partially-confirmed | `data-otservbr-global/scripts/actions/tools/skinning.lua:254` addAchievementProgress |
| 195 | [Smart Thinking](https://tibia.fandom.com/wiki/Smart_Thinking) | 1 | true | ? | 2 | December 8, 2010 | unresolved | missing | none | conflicting | unresolved |
| 196 | [Safely Stored Away](https://tibia.fandom.com/wiki/Safely_Stored_Away) | 1 | true | False | 2 | December 8, 2010 | progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:197` | unresolved | unresolved |
| 197 | [Something's in There](https://tibia.fandom.com/wiki/Something%27s_in_There) | 1 | true | True | 1 | December 8, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:198` | unresolved | unresolved |
| 198 | [Silent Pet](https://tibia.fandom.com/wiki/Silent_Pet) | 1 | true | True | 1 | December 8, 2010 | collection | confirmed | `data/scripts/lib/register_achievements.lua:199` | unresolved | unresolved |
| 199 | [Snowbunny](https://tibia.fandom.com/wiki/Snowbunny) | 1 | true | False | 2 | December 8, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:200` | partially-confirmed | `data/scripts/movements/snow.lua:19` addAchievementProgress |
| 200 | [Dark Voodoo Priest](https://tibia.fandom.com/wiki/Dark_Voodoo_Priest) | 1 | true | False | 2 | December 8, 2010 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:201` | partially-confirmed | `data/scripts/actions/items/voodoo_doll.lua:11` addAchievement |
| 201 | [Nomad Soul](https://tibia.fandom.com/wiki/Nomad_Soul) | 1 | true | True | 2 | December 8, 2010 | other | confirmed | `data/scripts/lib/register_achievements.lua:202` | unresolved | unresolved |
| 202 | [Truth Be Told](https://tibia.fandom.com/wiki/Truth_Be_Told) | 1 | true | True | 2 | December 8, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:203` | partially-confirmed | `data-otservbr-global/npc/jack.lua:121` addAchievement |
| 203 | [You Don't Know Jack](https://tibia.fandom.com/wiki/You_Don%27t_Know_Jack) | 1 | true | True | 2 | December 8, 2010 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:204` | partially-confirmed | `data-otservbr-global/npc/jack.lua:149` addAchievement |
| 204 | [Berry Picker](https://tibia.fandom.com/wiki/Berry_Picker) | 2 | true | False | 4 | December 8, 2010 | event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:205` | unresolved | unresolved |
| 205 | [True Colours](https://tibia.fandom.com/wiki/True_Colours) | 1 | true | False | 3 | December 8, 2010 | event-or-raid, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:206` | unresolved | unresolved |
| 206 | [Master Shapeshifter](https://tibia.fandom.com/wiki/Master_Shapeshifter) | 1 | true | True | 2 | December 8, 2010 | event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:207` | unresolved | unresolved |
| 207 | [Slimer](https://tibia.fandom.com/wiki/Slimer) | 1 | true | True | 1 | July 6, 2011 | item-or-interaction, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:208` | unresolved | unresolved |
| 208 | [Mageslayer](https://tibia.fandom.com/wiki/Mageslayer) | 1 | true | True | 1 | July 6, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:209` | partially-confirmed | `data-otservbr-global/scripts/quests/raging_mage_tower/creaturescripts_raging_mage_1.lua:7` hasAchievement; `data-otservbr-global/scripts/quests/raging_mage_tower/creaturescripts_raging_mage_1.lua:11` addAchievement |
| 209 | [Biodegradable](https://tibia.fandom.com/wiki/Biodegradable) | 1 | true | True | 1 | July 6, 2011 | other | confirmed | `data/scripts/lib/register_achievements.lua:210` | unresolved | unresolved |
| 210 | [Eye of the Deep](https://tibia.fandom.com/wiki/Eye_of_the_Deep) | 1 | true | False | 1 | July 6, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:211` | unresolved | unresolved |
| 211 | [Invader of the Deep](https://tibia.fandom.com/wiki/Invader_of_the_Deep) | 1 | true | False | 2 | July 6, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:212` | unresolved | unresolved |
| 212 | [Firefighter](https://tibia.fandom.com/wiki/Firefighter) | 1 | true | False | 2 | July 6, 2011 | event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:213` | unresolved | unresolved |
| 213 | [Deer Hunt](https://tibia.fandom.com/wiki/Deer_Hunt) | 1 | true | False | 1 | July 6, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:214` | unresolved | unresolved |
| 214 | [Askarak Nemesis](https://tibia.fandom.com/wiki/Askarak_Nemesis) | 1 | true | True | 1 | July 6, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:215` | unresolved | unresolved |
| 215 | [Shaburak Nemesis](https://tibia.fandom.com/wiki/Shaburak_Nemesis) | 1 | true | True | 1 | July 6, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:216` | unresolved | unresolved |
| 216 | [Fearless](https://tibia.fandom.com/wiki/Fearless) | 1 | true | True | 1 | July 6, 2011 | event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:217` | unresolved | unresolved |
| 217 | [Doctor! Doctor!](https://tibia.fandom.com/wiki/Doctor!_Doctor!) | 1 | true | False | 2 | July 6, 2011 | other | confirmed | `data/scripts/lib/register_achievements.lua:218` | partially-confirmed | `data-otservbr-global/npc/ottokar.lua:74` addAchievementProgress |
| 218 | [Beak Doctor](https://tibia.fandom.com/wiki/Beak_Doctor) | 2 | false | True | 4 | July 6, 2011 | other | confirmed | `data/scripts/lib/register_achievements.lua:219` | partially-confirmed | `data/scripts/actions/items/usable_afflicted_outfit_items.lua:19` addAchievementProgress; `data/scripts/actions/items/usable_afflicted_outfit_items.lua:30` addAchievementProgress |
| 219 | [Mystic Fabric Magic](https://tibia.fandom.com/wiki/Mystic_Fabric_Magic) | 2 | false | True | 4 | July 6, 2011 | other | confirmed | `data/scripts/lib/register_achievements.lua:220` | unresolved | unresolved |
| 221 | [Arachnoise](https://tibia.fandom.com/wiki/Arachnoise) | 1 | false | True | 1 | September 27, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:222` | unresolved | unresolved |
| 222 | [Rootless Behaviour](https://tibia.fandom.com/wiki/Rootless_Behaviour) | 1 | false | True | 1 | September 27, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:223` | unresolved | unresolved |
| 223 | [Twisted Mutation](https://tibia.fandom.com/wiki/Twisted_Mutation) | 1 | false | True | 1 | September 27, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:224` | unresolved | unresolved |
| 224 | [Beautiful Agony](https://tibia.fandom.com/wiki/Beautiful_Agony) | 1 | false | True | 2 | September 27, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:225` | unresolved | unresolved |
| 225 | [Scorched Flames](https://tibia.fandom.com/wiki/Scorched_Flames) | 1 | false | True | 1 | September 27, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:226` | unresolved | unresolved |
| 226 | [Crawling Death](https://tibia.fandom.com/wiki/Crawling_Death) | 1 | false | True | 1 | September 27, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:227` | partially-confirmed | `data-otservbr-global/npc/irmana.lua:120` addAchievement; `data-otservbr-global/npc/irmana.lua:194` addAchievement |
| 227 | [The Serpent's Bride](https://tibia.fandom.com/wiki/The_Serpent%27s_Bride) | 1 | false | True | 2 | September 27, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:228` | unresolved | unresolved |
| 228 | [No More Hiding](https://tibia.fandom.com/wiki/No_More_Hiding) | 1 | false | True | 1 | September 27, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:229` | unresolved | unresolved |
| 229 | [The Gates of Hell](https://tibia.fandom.com/wiki/The_Gates_of_Hell) | 1 | false | True | 2 | September 27, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:230` | unresolved | unresolved |
| 230 | [The Drowned Sea God](https://tibia.fandom.com/wiki/The_Drowned_Sea_God) | 1 | false | True | 2 | September 27, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:231` | unresolved | unresolved |
| 231 | [Spareribs for Dinner](https://tibia.fandom.com/wiki/Spareribs_for_Dinner) | 1 | false | True | 1 | September 27, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:232` | unresolved | unresolved |
| 232 | [Breaking the Ice](https://tibia.fandom.com/wiki/Breaking_the_Ice) | 1 | false | True | 1 | September 27, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:233` | unresolved | unresolved |
| 233 | [Just Cracked Me Up!](https://tibia.fandom.com/wiki/Just_Cracked_Me_Up!) | 1 | false | True | 2 | September 27, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:234` | unresolved | unresolved |
| 234 | [Something Smells](https://tibia.fandom.com/wiki/Something_Smells) | 1 | false | True | 1 | September 27, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:235` | unresolved | unresolved |
| 235 | [Meat Skewer](https://tibia.fandom.com/wiki/Meat_Skewer) | 1 | false | True | 1 | September 27, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:236` | unresolved | unresolved |
| 236 | [One Less](https://tibia.fandom.com/wiki/One_Less) | 1 | false | True | 2 | September 27, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:237` | unresolved | unresolved |
| 237 | [Hissing Downfall](https://tibia.fandom.com/wiki/Hissing_Downfall) | 1 | false | True | 2 | September 27, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:238` | unresolved | unresolved |
| 238 | [Choking on Her Venom](https://tibia.fandom.com/wiki/Choking_on_Her_Venom) | 1 | false | True | 1 | September 27, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:239` | unresolved | unresolved |
| 239 | [Blood-Red Snapper](https://tibia.fandom.com/wiki/Blood-Red_Snapper) | 1 | false | True | 1 | September 27, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:240` | unresolved | unresolved |
| 240 | [Back into the Abyss](https://tibia.fandom.com/wiki/Back_into_the_Abyss) | 1 | false | True | 1 | September 27, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:241` | unresolved | unresolved |
| 241 | [Pwned a Lot of Fur](https://tibia.fandom.com/wiki/Pwned_a_Lot_of_Fur) | 3 | true | True | 8 | September 27, 2011 | quest-or-task, combat | confirmed | `data/scripts/lib/register_achievements.lua:242` | unresolved | unresolved |
| 242 | [Honest Finder](https://tibia.fandom.com/wiki/Honest_Finder) | 1 | false | False | 1 | December 14, 2011 | event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:243` | unresolved | unresolved |
| 243 | [Goldhunter](https://tibia.fandom.com/wiki/Goldhunter) | 1 | true | False | 2 | December 14, 2011 | event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:244` | unresolved | unresolved |
| 244 | [Trail of the Ape God](https://tibia.fandom.com/wiki/Trail_of_the_Ape_God) | 1 | true | True | 1 | December 14, 2011 | combat, event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:245` | unresolved | unresolved |
| 245 | [Someone's Bored](https://tibia.fandom.com/wiki/Someone%27s_Bored) | 1 | true | False | 1 | December 14, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:246` | partially-confirmed | `data/scripts/creaturescripts/monster/giant_spider_wyda_death.lua:7` addAchievement |
| 246 | [Whistle-Blower](https://tibia.fandom.com/wiki/Whistle-Blower) | 1 | true | False | 1 | December 14, 2011 | event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:247` | unresolved | unresolved |
| 247 | [Torn Treasures](https://tibia.fandom.com/wiki/Torn_Treasures) | 1 | true | False | 1 | December 14, 2011 | event-or-raid, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:248` | unresolved | unresolved |
| 248 | [Loyal Subject](https://tibia.fandom.com/wiki/Loyal_Subject) | 1 | true | False | 1 | December 14, 2011 | dialogue, event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:249` | unresolved | unresolved |
| 249 | [Desert Fisher](https://tibia.fandom.com/wiki/Desert_Fisher) | 1 | false | True | 1 | December 14, 2011 | event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:250` | unresolved | unresolved |
| 251 | [Dog Sitter](https://tibia.fandom.com/wiki/Dog_Sitter) | 1 | false | False | 1 | December 14, 2011 | collection, event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:252` | unresolved | unresolved |
| 252 | [Ice Harvester](https://tibia.fandom.com/wiki/Ice_Harvester) | 1 | false | True | 1 | December 14, 2011 | item-or-interaction, event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:253` | unresolved | unresolved |
| 253 | [Preservationist](https://tibia.fandom.com/wiki/Preservationist) | 1 | true | False | 1 | December 14, 2011 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:254` | unresolved | unresolved |
| 254 | [Chest Robber](https://tibia.fandom.com/wiki/Chest_Robber) | 1 | false | True | 1 | December 14, 2011 | event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:255` | unresolved | unresolved |
| 255 | [Down the Drain](https://tibia.fandom.com/wiki/Down_the_Drain) | 1 | false | False | 2 | December 14, 2011 | combat, event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:256` | unresolved | unresolved |
| 256 | [Fire from the Earth](https://tibia.fandom.com/wiki/Fire_from_the_Earth) | 1 | false | True | 2 | December 14, 2011 | combat, event-or-raid | confirmed | `data/scripts/lib/register_achievements.lua:257` | unresolved | unresolved |
| 257 | [Minor Disturbance](https://tibia.fandom.com/wiki/Minor_Disturbance) | 1 | false | True | 2 | December 14, 2011 | quest-or-task, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:258` | unresolved | unresolved |
| 258 | [Dazzler](https://tibia.fandom.com/wiki/Dazzler) | 1 | false | True | 3 | December 14, 2011 | quest-or-task, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:259` | unresolved | unresolved |
| 259 | [Hive Blinder](https://tibia.fandom.com/wiki/Hive_Blinder) | 2 | false | True | 4 | December 14, 2011 | quest-or-task, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:260` | unresolved | unresolved |
| 260 | [Hickup](https://tibia.fandom.com/wiki/Hickup) | 1 | false | True | 2 | December 14, 2011 | quest-or-task, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:261` | unresolved | unresolved |
| 261 | [Heartburn](https://tibia.fandom.com/wiki/Heartburn) | 1 | false | True | 3 | December 14, 2011 | quest-or-task, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:262` | unresolved | unresolved |
| 262 | [Stomach Ulcer](https://tibia.fandom.com/wiki/Stomach_Ulcer) | 2 | false | True | 4 | December 14, 2011 | quest-or-task, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:263` | unresolved | unresolved |
| 263 | [Planter](https://tibia.fandom.com/wiki/Planter) | 1 | false | True | 2 | December 14, 2011 | quest-or-task, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:264` | unresolved | unresolved |
| 264 | [Pimple](https://tibia.fandom.com/wiki/Pimple) | 1 | false | True | 3 | December 14, 2011 | quest-or-task, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:265` | unresolved | unresolved |
| 265 | [Suppressor](https://tibia.fandom.com/wiki/Suppressor) | 2 | false | True | 4 | December 14, 2011 | quest-or-task, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:266` | unresolved | unresolved |
| 266 | [Gatherer](https://tibia.fandom.com/wiki/Gatherer) | 1 | false | True | 2 | December 14, 2011 | quest-or-task, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:267` | unresolved | unresolved |
| 267 | [Supplier](https://tibia.fandom.com/wiki/Supplier) | 1 | false | True | 3 | December 14, 2011 | quest-or-task, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:268` | unresolved | unresolved |
| 268 | [Chitin Bane](https://tibia.fandom.com/wiki/Chitin_Bane) | 2 | false | True | 4 | December 14, 2011 | quest-or-task, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:269` | unresolved | unresolved |
| 269 | [Guard Killer](https://tibia.fandom.com/wiki/Guard_Killer) | 1 | false | True | 2 | December 14, 2011 | quest-or-task, combat, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:270` | unresolved | unresolved |
| 270 | [Hive Infiltrator](https://tibia.fandom.com/wiki/Hive_Infiltrator) | 1 | false | True | 3 | December 14, 2011 | quest-or-task, combat, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:271` | unresolved | unresolved |
| 271 | [Exterminator](https://tibia.fandom.com/wiki/Exterminator) | 2 | false | True | 4 | December 14, 2011 | quest-or-task, combat, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:272` | unresolved | unresolved |
| 272 | [Headache](https://tibia.fandom.com/wiki/Headache) | 1 | false | True | 2 | December 14, 2011 | quest-or-task, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:273` | unresolved | unresolved |
| 273 | [Confusion](https://tibia.fandom.com/wiki/Confusion) | 1 | false | True | 3 | December 14, 2011 | progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:274` | unresolved | unresolved |
| 274 | [Manic](https://tibia.fandom.com/wiki/Manic) | 2 | false | True | 4 | December 14, 2011 | progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:275` | unresolved | unresolved |
| 276 | [Navigational Error](https://tibia.fandom.com/wiki/Navigational_Error) | 2 | true | True | 5 | December 14, 2011 | quest-or-task, dialogue | confirmed | `data/scripts/lib/register_achievements.lua:277` | unresolved | unresolved |
| 277 | [Si, Ariki!](https://tibia.fandom.com/wiki/Si,_Ariki!) | 1 | false | False | 1 | December 14, 2011 | other | confirmed | `data/scripts/lib/register_achievements.lua:278` | partially-confirmed | `data-otservbr-global/npc/yasir.lua:822` addAchievement; `data-otservbr-global/npc/yasir.lua:828` addAchievement |
| 278 | [Guardian Downfall](https://tibia.fandom.com/wiki/Guardian_Downfall) | 2 | false | True | 4 | December 14, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:279` | unresolved | unresolved |
| 279 | [Death Song](https://tibia.fandom.com/wiki/Death_Song) | 1 | false | True | 3 | December 14, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:280` | unresolved | unresolved |
| 280 | [Depth Dwellers](https://tibia.fandom.com/wiki/Depth_Dwellers) | 1 | false | True | 3 | December 14, 2011 | combat | confirmed | `data/scripts/lib/register_achievements.lua:281` | unresolved | unresolved |
| 281 | [Gem Cutter](https://tibia.fandom.com/wiki/Gem_Cutter) | 1 | true | True | 1 | December 14, 2011 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:282` | unresolved | unresolved |
| 282 | [Spolium Profundis](https://tibia.fandom.com/wiki/Spolium_Profundis) | 2 | false | True | 4 | December 14, 2011 | other | confirmed | `data/scripts/lib/register_achievements.lua:283` | unresolved | unresolved |
| 283 | [Bane of the Hive](https://tibia.fandom.com/wiki/Bane_of_the_Hive) | 1 | false | True | 2 | December 14, 2011 | collection | confirmed | `data/scripts/lib/register_achievements.lua:284` | unresolved | unresolved |
| 285 | [Hive War Veteran](https://tibia.fandom.com/wiki/Hive_War_Veteran) | 1 | false | True | 1 | December 14, 2011 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:286` | unresolved | unresolved |
| 286 | [Hive Fighter](https://tibia.fandom.com/wiki/Hive_Fighter) | 1 | false | True | 1 | December 14, 2011 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:287` | unresolved | unresolved |
| 287 | [Howly Silence](https://tibia.fandom.com/wiki/Howly_Silence) | 1 | false | True | 1 | April 03, 2012 | combat | confirmed | `data/scripts/lib/register_achievements.lua:288` | unresolved | unresolved |
| 288 | [Dream's Over](https://tibia.fandom.com/wiki/Dream%27s_Over) | 1 | false | True | 1 | April 03, 2012 | combat | confirmed | `data/scripts/lib/register_achievements.lua:289` | unresolved | unresolved |
| 289 | [Zzztill Zzztanding!](https://tibia.fandom.com/wiki/Zzztill_Zzztanding!) | 1 | false | True | 1 | April 03, 2012 | combat | confirmed | `data/scripts/lib/register_achievements.lua:290` | unresolved | unresolved |
| 290 | [Stepped on a Big Toe](https://tibia.fandom.com/wiki/Stepped_on_a_Big_Toe) | 1 | false | True | 1 | April 03, 2012 | combat | confirmed | `data/scripts/lib/register_achievements.lua:291` | unresolved | unresolved |
| 291 | [Kapow!](https://tibia.fandom.com/wiki/Kapow!) | 1 | false | True | 1 | April 03, 2012 | combat | confirmed | `data/scripts/lib/register_achievements.lua:292` | unresolved | unresolved |
| 292 | [Enter zze Draken!](https://tibia.fandom.com/wiki/Enter_zze_Draken!) | 1 | false | True | 2 | April 03, 2012 | combat | confirmed | `data/scripts/lib/register_achievements.lua:293` | unresolved | unresolved |
| 293 | [King of the Ring](https://tibia.fandom.com/wiki/King_of_the_Ring) | 1 | false | True | 2 | April 03, 2012 | combat | confirmed | `data/scripts/lib/register_achievements.lua:294` | unresolved | unresolved |
| 294 | [Back from the Dead](https://tibia.fandom.com/wiki/Back_from_the_Dead) | 1 | false | True | 2 | April 03, 2012 | combat | confirmed | `data/scripts/lib/register_achievements.lua:295` | unresolved | unresolved |
| 295 | [Pwned All Fur](https://tibia.fandom.com/wiki/Pwned_All_Fur) | 3 | true | True | 8 | April 03, 2012 | quest-or-task, combat | confirmed | `data/scripts/lib/register_achievements.lua:296` | unresolved | unresolved |
| 297 | [Bibby's Bloodbath](https://tibia.fandom.com/wiki/Bibby%27s_Bloodbath) | 1 | true | False | 1 | July 11, 2012 | combat | confirmed | `data/scripts/lib/register_achievements.lua:298` | unresolved | unresolved |
| 298 | [Nestling](https://tibia.fandom.com/wiki/Nestling) | 1 | false | False | 1 | July 11, 2012 | combat, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:299` | unresolved | unresolved |
| 299 | [Becoming a Bigfoot](https://tibia.fandom.com/wiki/Becoming_a_Bigfoot) | 1 | false | False | 1 | July 11, 2012 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:300` | partially-confirmed | `data-otservbr-global/npc/gnomelvis.lua:92` addAchievement |
| 300 | [Gnome Little Helper](https://tibia.fandom.com/wiki/Gnome_Little_Helper) | 1 | false | False | 1 | July 11, 2012 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:301` | partially-confirmed | `data-otservbr-global/lib/functions/players.lua:30` addAchievement; `data-otservbr-global/lib/functions/players.lua:36` addAchievement; `data-otservbr-global/lib/functions/players.lua:43` addAchievement; `data-otservbr-global/lib/functions/players.lua:51` addAchievement |
| 301 | [Gnome Friend](https://tibia.fandom.com/wiki/Gnome_Friend) | 1 | false | False | 2 | July 11, 2012 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:302` | partially-confirmed | `data-otservbr-global/lib/functions/players.lua:37` addAchievement; `data-otservbr-global/lib/functions/players.lua:44` addAchievement; `data-otservbr-global/lib/functions/players.lua:52` addAchievement |
| 302 | [Gnomelike](https://tibia.fandom.com/wiki/Gnomelike) | 1 | false | False | 3 | July 11, 2012 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:303` | partially-confirmed | `data-otservbr-global/lib/functions/players.lua:45` addAchievement; `data-otservbr-global/lib/functions/players.lua:53` addAchievement |
| 303 | [Honorary Gnome](https://tibia.fandom.com/wiki/Honorary_Gnome) | 2 | false | False | 4 | July 11, 2012 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:304` | partially-confirmed | `data-otservbr-global/lib/functions/players.lua:54` addAchievement |
| 304 | [Crystals in Love](https://tibia.fandom.com/wiki/Crystals_in_Love) | 1 | false | True | 1 | July 11, 2012 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:305` | partially-confirmed | `data-otservbr-global/npc/gnomeral.lua:100` addAchievement |
| 305 | [Substitute Tinker](https://tibia.fandom.com/wiki/Substitute_Tinker) | 1 | false | True | 1 | July 11, 2012 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:306` | partially-confirmed | `data-otservbr-global/npc/gnomeral.lua:142` addAchievement |
| 306 | [Spore Hunter](https://tibia.fandom.com/wiki/Spore_Hunter) | 1 | false | True | 1 | July 11, 2012 | quest-or-task, collection | confirmed | `data/scripts/lib/register_achievements.lua:307` | partially-confirmed | `data-otservbr-global/npc/gnomeral.lua:184` addAchievement |
| 307 | [Grinding Again](https://tibia.fandom.com/wiki/Grinding_Again) | 1 | false | True | 1 | July 11, 2012 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:308` | partially-confirmed | `data-otservbr-global/npc/gnomeral.lua:224` addAchievement |
| 308 | [Dungeon Cleaner](https://tibia.fandom.com/wiki/Dungeon_Cleaner) | 1 | true | True | 3 | July 11, 2012 | other | confirmed | `data/scripts/lib/register_achievements.lua:309` | unresolved | unresolved |
| 309 | [Crystal Keeper](https://tibia.fandom.com/wiki/Crystal_Keeper) | 1 | false | False | 1 | July 11, 2012 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:310` | partially-confirmed | `data-otservbr-global/npc/commander_stone.lua:91` addAchievement |
| 310 | [Call Me Sparky](https://tibia.fandom.com/wiki/Call_Me_Sparky) | 1 | false | False | 1 | July 11, 2012 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:311` | partially-confirmed | `data-otservbr-global/npc/commander_stone.lua:128` addAchievement |
| 311 | [One Foot Vs. Many](https://tibia.fandom.com/wiki/One_Foot_Vs._Many) | 1 | false | False | 1 | July 11, 2012 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:312` | partially-confirmed | `data-otservbr-global/npc/commander_stone.lua:163` addAchievement |
| 312 | [The Picky Pig](https://tibia.fandom.com/wiki/The_Picky_Pig) | 1 | false | False | 1 | July 11, 2012 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:313` | partially-confirmed | `data-otservbr-global/npc/commander_stone.lua:205` addAchievement |
| 313 | [Diplomatic Immunity](https://tibia.fandom.com/wiki/Diplomatic_Immunity) | 2 | true | True | 4 | July 11, 2012 | item-or-interaction, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:314` | unresolved | unresolved |
| 314 | [Fall of the Fallen](https://tibia.fandom.com/wiki/Fall_of_the_Fallen) | 2 | true | True | 4 | July 11, 2012 | item-or-interaction, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:315` | unresolved | unresolved |
| 315 | [Death on Strike](https://tibia.fandom.com/wiki/Death_on_Strike) | 2 | true | True | 4 | July 11, 2012 | item-or-interaction, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:316` | unresolved | unresolved |
| 316 | [Death from Below](https://tibia.fandom.com/wiki/Death_from_Below) | 1 | true | True | 2 | July 11, 2012 | combat, item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:317` | unresolved | unresolved |
| 317 | [Gnomebane's Bane](https://tibia.fandom.com/wiki/Gnomebane%27s_Bane) | 1 | true | True | 2 | July 11, 2012 | combat, item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:318` | unresolved | unresolved |
| 318 | [Final Strike](https://tibia.fandom.com/wiki/Final_Strike) | 1 | true | True | 2 | July 11, 2012 | combat, item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:319` | unresolved | unresolved |
| 319 | [Goo Goo Dancer](https://tibia.fandom.com/wiki/Goo_Goo_Dancer) | 1 | true | True | 1 | July 11, 2012 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:320` | partially-confirmed | `data/scripts/actions/items/muck_remover.lua:30` addAchievementProgress |
| 320 | [Funghitastic](https://tibia.fandom.com/wiki/Funghitastic) | 1 | false | True | 3 | July 11, 2012 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:321` | unresolved | unresolved |
| 321 | [Crystal Clear](https://tibia.fandom.com/wiki/Crystal_Clear) | 1 | false | True | 3 | July 11, 2012 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:322` | unresolved | unresolved |
| 322 | [Gnomish Art Of War](https://tibia.fandom.com/wiki/Gnomish_Art_Of_War) | 1 | false | True | 3 | July 11, 2012 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:323` | unresolved | unresolved |
| 324 | [True Dedication](https://tibia.fandom.com/wiki/True_Dedication) | 2 | true | True | 5 | December 12, 2012 | other | confirmed | `data/scripts/lib/register_achievements.lua:325` | unresolved | unresolved |
| 325 | [Task Manager](https://tibia.fandom.com/wiki/Task_Manager) | 1 | true | False | 2 | December 12, 2012 | quest-or-task, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:326` | unresolved | unresolved |
| 326 | [Gravedigger](https://tibia.fandom.com/wiki/Gravedigger_(Achievement)) | 1 | false | True | 3 | July 17, 2013 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:327` | unresolved | unresolved |
| 327 | [Repenter](https://tibia.fandom.com/wiki/Repenter_(Achievement)) | 1 | true | False | 1 | July 17, 2013 | quest-or-task, dialogue | confirmed | `data/scripts/lib/register_achievements.lua:328` | unresolved | unresolved |
| 328 | [Umbral Swordsman](https://tibia.fandom.com/wiki/Umbral_Swordsman) | 2 | false | True | 6 | December 11, 2013 | other | confirmed | `data/scripts/lib/register_achievements.lua:329` | unresolved | unresolved |
| 331 | [Cave Completionist](https://tibia.fandom.com/wiki/Cave_Completionist) | 1 | false | True | 2 | September 18, 2013 | collection | confirmed | `data/scripts/lib/register_achievements.lua:332` | unresolved | unresolved |
| 332 | [Umbral Bladelord](https://tibia.fandom.com/wiki/Umbral_Bladelord) | 2 | false | True | 6 | December 11, 2013 | other | confirmed | `data/scripts/lib/register_achievements.lua:333` | unresolved | unresolved |
| 333 | [Umbral Headsman](https://tibia.fandom.com/wiki/Umbral_Headsman) | 2 | false | True | 6 | December 11, 2013 | other | confirmed | `data/scripts/lib/register_achievements.lua:334` | unresolved | unresolved |
| 334 | [Umbral Executioner](https://tibia.fandom.com/wiki/Umbral_Executioner) | 2 | false | True | 6 | December 11, 2013 | other | confirmed | `data/scripts/lib/register_achievements.lua:335` | unresolved | unresolved |
| 335 | [Umbral Brawler](https://tibia.fandom.com/wiki/Umbral_Brawler) | 2 | false | True | 6 | December 11, 2013 | other | confirmed | `data/scripts/lib/register_achievements.lua:336` | unresolved | unresolved |
| 336 | [Umbral Berserker](https://tibia.fandom.com/wiki/Umbral_Berserker) | 2 | false | True | 6 | December 11, 2013 | other | confirmed | `data/scripts/lib/register_achievements.lua:337` | unresolved | unresolved |
| 337 | [Umbral Archer](https://tibia.fandom.com/wiki/Umbral_Archer) | 2 | false | True | 6 | December 11, 2013 | other | confirmed | `data/scripts/lib/register_achievements.lua:338` | unresolved | unresolved |
| 338 | [Umbral Marksman](https://tibia.fandom.com/wiki/Umbral_Marksman) | 2 | false | True | 6 | December 11, 2013 | other | confirmed | `data/scripts/lib/register_achievements.lua:339` | unresolved | unresolved |
| 339 | [Umbral Harbinger](https://tibia.fandom.com/wiki/Umbral_Harbinger) | 2 | false | True | 6 | December 11, 2013 | other | confirmed | `data/scripts/lib/register_achievements.lua:340` | unresolved | unresolved |
| 340 | [Umbral Master](https://tibia.fandom.com/wiki/Umbral_Master) | 3 | false | True | 8 | December 11, 2013 | other | confirmed | `data/scripts/lib/register_achievements.lua:341` | unresolved | unresolved |
| 341 | [Nevermending Story](https://tibia.fandom.com/wiki/Nevermending_Story) | 1 | true | True | 3 | December 11, 2013 | quest-or-task, collection | confirmed | `data/scripts/lib/register_achievements.lua:342` | unresolved | unresolved |
| 342 | [Luring Silence](https://tibia.fandom.com/wiki/Luring_Silence) | 1 | false | True | 2 | December 11, 2013 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:343` | unresolved | unresolved |
| 343 | [Never Surrender](https://tibia.fandom.com/wiki/Never_Surrender) | 1 | false | True | 3 | December 11, 2013 | combat | confirmed | `data/scripts/lib/register_achievements.lua:344` | unresolved | unresolved |
| 344 | [Dream Wright](https://tibia.fandom.com/wiki/Dream_Wright) | 1 | false | True | 1 | December 11, 2013 | quest-or-task, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:345` | unresolved | unresolved |
| 345 | [Ending the Horror](https://tibia.fandom.com/wiki/Ending_the_Horror) | 1 | false | True | 2 | December 11, 2013 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:346` | unresolved | unresolved |
| 346 | [Sleepwalking](https://tibia.fandom.com/wiki/Sleepwalking) | 1 | false | True | 1 | December 11, 2013 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:347` | unresolved | unresolved |
| 347 | [Dream Warden](https://tibia.fandom.com/wiki/Dream_Warden) | 2 | false | True | 5 | December 11, 2013 | other | confirmed | `data/scripts/lib/register_achievements.lua:348` | unresolved | unresolved |
| 348 | [Prison Break](https://tibia.fandom.com/wiki/Prison_Break) | 3 | false | True | 8 | December 11, 2013 | combat | confirmed | `data/scripts/lib/register_achievements.lua:349` | unresolved | unresolved |
| 349 | [Noblesse Obliterated](https://tibia.fandom.com/wiki/Noblesse_Obliterated) | 2 | false | True | 6 | December 11, 2013 | combat | confirmed | `data/scripts/lib/register_achievements.lua:350` | unresolved | unresolved |
| 350 | [Elementary, My Dear](https://tibia.fandom.com/wiki/Elementary,_My_Dear) | 1 | false | True | 1 | July 7, 2014 | quest-or-task, item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:351` | unresolved | unresolved |
| 351 | [Rathleton Commoner](https://tibia.fandom.com/wiki/Rathleton_Commoner) | 1 | false | True | 1 | July 7, 2014 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:352` | unresolved | unresolved |
| 352 | [Rathleton Inhabitant](https://tibia.fandom.com/wiki/Rathleton_Inhabitant) | 1 | false | True | 1 | July 7, 2014 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:353` | unresolved | unresolved |
| 353 | [Rathleton Citizen](https://tibia.fandom.com/wiki/Rathleton_Citizen) | 1 | false | True | 1 | July 7, 2014 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:354` | unresolved | unresolved |
| 354 | [Combo Master](https://tibia.fandom.com/wiki/Combo_Master) | 1 | true | True | 1 | July 7, 2014 | quest-or-task, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:355` | unresolved | unresolved |
| 355 | [Glooth Engineer](https://tibia.fandom.com/wiki/Glooth_Engineer) | 2 | false | True | 5 | July 7, 2014 | other | confirmed | `data/scripts/lib/register_achievements.lua:356` | unresolved | unresolved |
| 356 | [Lion's Den Explorer](https://tibia.fandom.com/wiki/Lion%27s_Den_Explorer) | 1 | true | True | 1 | December 10, 2014 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:357` | partially-confirmed | `data-otservbr-global/scripts/quests/lions_rock/actions_lions_rock.lua:131` addAchievement |
| 357 | [Seasoned Adventurer](https://tibia.fandom.com/wiki/Seasoned_Adventurer) | 1 | false | False | 1 | September 24, 2014 | other | confirmed | `data/scripts/lib/register_achievements.lua:358` | unresolved | unresolved |
| 358 | [Mind the Step!](https://tibia.fandom.com/wiki/Mind_the_Step!) | 1 | false | True | 1 | December 10, 2014 | quest-or-task, collection | confirmed | `data/scripts/lib/register_achievements.lua:359` | unresolved | unresolved |
| 359 | [Rathleton Squire](https://tibia.fandom.com/wiki/Rathleton_Squire) | 1 | false | True | 1 | December 10, 2014 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:360` | unresolved | unresolved |
| 360 | [The Professor's Nut](https://tibia.fandom.com/wiki/The_Professor%27s_Nut) | 1 | false | True | 3 | December 10, 2014 | quest-or-task, item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:361` | partially-confirmed | `data-otservbr-global/scripts/quests/hero_of_rathleton/actions_reward.lua:9` addAchievement |
| 361 | [Plant vs. Minos](https://tibia.fandom.com/wiki/Plant_vs._Minos) | 2 | true | True | 4 | December 10, 2014 | combat | confirmed | `data/scripts/lib/register_achievements.lua:362` | unresolved | unresolved |
| 362 | [Rumble in the Plant](https://tibia.fandom.com/wiki/Rumble_in_the_Plant) | 2 | true | True | 4 | December 10, 2014 | combat | confirmed | `data/scripts/lib/register_achievements.lua:363` | unresolved | unresolved |
| 363 | [Robo Chop](https://tibia.fandom.com/wiki/Robo_Chop) | 2 | true | True | 4 | December 10, 2014 | combat | confirmed | `data/scripts/lib/register_achievements.lua:364` | unresolved | unresolved |
| 364 | [Go with da Lava Flow](https://tibia.fandom.com/wiki/Go_with_da_Lava_Flow) | 1 | true | True | 1 | December 10, 2014 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:365` | partially-confirmed | `data-otservbr-global/scripts/quests/hero_of_rathleton/movements_lava.lua:20` addAchievement |
| 365 | [Wail of the Banshee](https://tibia.fandom.com/wiki/Wail_of_the_Banshee) | 1 | true | True | 1 | December 10, 2014 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:366` | partially-confirmed | `data-otservbr-global/npc/one_eyed_joe.lua:71` addAchievement |
| 366 | [Publicity](https://tibia.fandom.com/wiki/Publicity) | 1 | false | True | 1 | December 10, 2014 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:367` | unresolved | unresolved |
| 367 | [Snake Charmer](https://tibia.fandom.com/wiki/Snake_Charmer) | 1 | false | True | 1 | December 10, 2014 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:368` | unresolved | unresolved |
| 368 | [Hoard of the Dragon](https://tibia.fandom.com/wiki/Hoard_of_the_Dragon) | 1 | true | True | 1 | July 21, 2015 | quest-or-task, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:369` | partially-confirmed | `data-otservbr-global/scripts/quests/the_great_dragon_hunt_quest/actions_treasure.lua:37` addAchievement |
| 370 | [Little Ball of Wool](https://tibia.fandom.com/wiki/Little_Ball_of_Wool) | 1 | false | False | 1 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:371` | unresolved | unresolved |
| 371 | [Luminous Kitty](https://tibia.fandom.com/wiki/Luminous_Kitty) | 1 | false | True | 3 | July 21, 2015 | other | confirmed | `data/scripts/lib/register_achievements.lua:372` | unresolved | unresolved |
| 372 | [The Right Tone](https://tibia.fandom.com/wiki/The_Right_Tone) | 1 | false | False | 1 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:373` | unresolved | unresolved |
| 373 | [Loyal Lad](https://tibia.fandom.com/wiki/Loyal_Lad) | 1 | false | False | 1 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:374` | unresolved | unresolved |
| 374 | [Dragon Mimicry](https://tibia.fandom.com/wiki/Dragon_Mimicry) | 1 | false | True | 2 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:375` | unresolved | unresolved |
| 375 | [Scales and Tail](https://tibia.fandom.com/wiki/Scales_and_Tail) | 1 | false | True | 2 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:376` | unresolved | unresolved |
| 376 | [Fata Morgana](https://tibia.fandom.com/wiki/Fata_Morgana) | 1 | false | True | 2 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:377` | unresolved | unresolved |
| 377 | [Fabled Construction](https://tibia.fandom.com/wiki/Fabled_Construction) | 1 | false | True | 3 | July 21, 2015 | other | confirmed | `data/scripts/lib/register_achievements.lua:378` | unresolved | unresolved |
| 378 | [Mind the Dog!](https://tibia.fandom.com/wiki/Mind_the_Dog!) | 1 | false | True | 2 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:379` | unresolved | unresolved |
| 379 | [Magnetised](https://tibia.fandom.com/wiki/Magnetised) | 1 | false | True | 2 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:380` | unresolved | unresolved |
| 380 | [Golden Sands](https://tibia.fandom.com/wiki/Golden_Sands) | 1 | false | True | 3 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:381` | unresolved | unresolved |
| 381 | [Friend of Elves](https://tibia.fandom.com/wiki/Friend_of_Elves) | 1 | false | False | 1 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:382` | unresolved | unresolved |
| 382 | [Lovely Dots](https://tibia.fandom.com/wiki/Lovely_Dots) | 1 | false | True | 3 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:383` | unresolved | unresolved |
| 383 | [Way to Hell](https://tibia.fandom.com/wiki/Way_to_Hell) | 1 | false | True | 2 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:384` | unresolved | unresolved |
| 384 | [Beneath the Sea](https://tibia.fandom.com/wiki/Beneath_the_Sea) | 1 | false | True | 3 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:385` | unresolved | unresolved |
| 385 | [Starless Night](https://tibia.fandom.com/wiki/Starless_Night) | 1 | false | True | 3 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:386` | unresolved | unresolved |
| 386 | [Lion King](https://tibia.fandom.com/wiki/Lion_King) | 1 | false | True | 1 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:387` | unresolved | unresolved |
| 387 | [Pecking Order](https://tibia.fandom.com/wiki/Pecking_Order) | 1 | false | True | 1 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:388` | unresolved | unresolved |
| 388 | [Pig-Headed](https://tibia.fandom.com/wiki/Pig-Headed) | 1 | false | False | 2 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:389` | unresolved | unresolved |
| 389 | [Personal Nightmare](https://tibia.fandom.com/wiki/Personal_Nightmare) | 1 | false | True | 3 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:390` | unresolved | unresolved |
| 390 | [Thick-Skinned](https://tibia.fandom.com/wiki/Thick-Skinned) | 1 | false | True | 2 | July 21, 2015 | collection, mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:391` | unresolved | unresolved |
| 391 | [Chequered Teddy](https://tibia.fandom.com/wiki/Chequered_Teddy) | 1 | false | True | 1 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:392` | unresolved | unresolved |
| 392 | [Blacknailed](https://tibia.fandom.com/wiki/Blacknailed) | 1 | false | True | 1 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:393` | unresolved | unresolved |
| 393 | [Slugging Around](https://tibia.fandom.com/wiki/Slugging_Around) | 1 | false | False | 2 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:394` | unresolved | unresolved |
| 394 | [Knock on Wood](https://tibia.fandom.com/wiki/Knock_on_Wood) | 1 | false | True | 3 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:395` | unresolved | unresolved |
| 395 | [Fried Shrimp](https://tibia.fandom.com/wiki/Fried_Shrimp) | 1 | false | True | 2 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:396` | unresolved | unresolved |
| 396 | [Out of the Stone Age](https://tibia.fandom.com/wiki/Out_of_the_Stone_Age) | 1 | false | True | 3 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:397` | unresolved | unresolved |
| 397 | [Stuntman](https://tibia.fandom.com/wiki/Stuntman) | 1 | false | True | 3 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:398` | unresolved | unresolved |
| 398 | [Gear Up](https://tibia.fandom.com/wiki/Gear_Up) | 1 | false | True | 3 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:399` | unresolved | unresolved |
| 399 | [Bearbaiting](https://tibia.fandom.com/wiki/Bearbaiting) | 1 | false | False | 1 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:400` | unresolved | unresolved |
| 400 | [Lucky Horseshoe](https://tibia.fandom.com/wiki/Lucky_Horseshoe) | 1 | false | False | 1 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:401` | unresolved | unresolved |
| 401 | [Swamp Beast](https://tibia.fandom.com/wiki/Swamp_Beast) | 1 | false | False | 1 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:402` | unresolved | unresolved |
| 402 | [Spin-Off](https://tibia.fandom.com/wiki/Spin-Off) | 1 | false | True | 1 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:403` | unresolved | unresolved |
| 403 | [Icy Glare](https://tibia.fandom.com/wiki/Icy_Glare) | 1 | false | True | 1 | July 21, 2015 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:404` | unresolved | unresolved |
| 404 | [Cartography 101](https://tibia.fandom.com/wiki/Cartography_101) | 1 | false | True | 2 | July 21, 2015 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:405` | unresolved | unresolved |
| 405 | [Lost Palace Raider](https://tibia.fandom.com/wiki/Lost_Palace_Raider) | 1 | true | True | 2 | July 21, 2015 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:406` | unresolved | unresolved |
| 406 | [The More the Merrier](https://tibia.fandom.com/wiki/The_More_the_Merrier) | 0 | true | False | 0 | August 11, 2015 | other | conflicting | `data/scripts/lib/register_achievements.lua:407` | conflicting | unresolved |
| 408 | [Rift Warrior](https://tibia.fandom.com/wiki/Rift_Warrior) | 1 | false | True | 3 | December 8, 2015 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:409` | partially-confirmed | `data-otservbr-global/npc/cledwyn.lua:188` addAchievement; `data-otservbr-global/npc/cledwyn.lua:203` addAchievement |
| 410 | [Hat Hunter](https://tibia.fandom.com/wiki/Hat_Hunter) | 2 | false | True | 5 | December 8, 2015 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:411` | partially-confirmed | `data-otservbr-global/scripts/quests/ferumbras_ascension/actions_reward.lua:21` addAchievement |
| 411 | [Ogre Chef](https://tibia.fandom.com/wiki/Ogre_Chef) | 1 | false | True | 1 | December 8, 2015 | quest-or-task, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:412` | unresolved | unresolved |
| 412 | [The Call of the Wild](https://tibia.fandom.com/wiki/The_Call_of_the_Wild) | 1 | false | True | 2 | December 8, 2015 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:413` | unresolved | unresolved |
| 413 | [Ender of the End](https://tibia.fandom.com/wiki/Ender_of_the_End) | 2 | false | True | 5 | May 31, 2016 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:414` | partially-confirmed | `data-otservbr-global/scripts/quests/heart_of_destruction/actions_reward.lua:13` addAchievement |
| 414 | [Vortex Tamer](https://tibia.fandom.com/wiki/Vortex_Tamer) | 2 | false | True | 5 | May 31, 2016 | item-or-interaction, mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:415` | partially-confirmed | `data/scripts/actions/items/usable_mount_items.lua:27` addAchievementProgress |
| 415 | [Rhino Rider](https://tibia.fandom.com/wiki/Rhino_Rider) | 1 | false | True | 1 | December 6, 2016 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:416` | unresolved | unresolved |
| 416 | [Forbidden Fruit](https://tibia.fandom.com/wiki/Forbidden_Fruit_(Achievement)) | 1 | true | False | 1 | December 6, 2016 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:417` | unresolved | unresolved |
| 417 | [Forbidden Knowledge](https://tibia.fandom.com/wiki/Forbidden_Knowledge) | 1 | true | False | 1 | December 6, 2016 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:418` | unresolved | unresolved |
| 418 | [Treasure Hunter](https://tibia.fandom.com/wiki/Treasure_Hunter) | 1 | true | True | 3 | December 15, 2016 | quest-or-task, item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:419` | partially-confirmed | `data-otservbr-global/scripts/quests/the_first_dragon/actions_treasure_chest.lua:101` addAchievement |
| 419 | [Reason to Celebrate](https://tibia.fandom.com/wiki/Reason_to_Celebrate) | 1 | false | True | 1 | December 15, 2016 | other | confirmed | `data/scripts/lib/register_achievements.lua:420` | unresolved | unresolved |
| 420 | [Toothfairy Assistant](https://tibia.fandom.com/wiki/Toothfairy_Assistant) | 1 | false | True | 1 | July 25, 2017 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:421` | unresolved | unresolved |
| 421 | [Fairy Teasing](https://tibia.fandom.com/wiki/Fairy_Teasing) | 1 | true | False | 1 | July 25, 2017 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:422` | partially-confirmed | `data-otservbr-global/scripts/actions/object/dancingfairy.lua:28` addAchievementProgress |
| 422 | [Corruption Contained](https://tibia.fandom.com/wiki/Corruption_Contained) | 2 | false | True | 5 | July 25, 2017 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:423` | partially-confirmed | `data-otservbr-global/npc/gerimor.lua:439` addAchievement |
| 430 | [Little Adventure](https://tibia.fandom.com/wiki/Little_Adventure) | 1 | false | False | 1 | December 5, 2017 | other | confirmed | `data/scripts/lib/register_achievements.lua:431` | unresolved | unresolved |
| 431 | [Little Big Adventure](https://tibia.fandom.com/wiki/Little_Big_Adventure) | 1 | true | False | 2 | December 5, 2017 | other | confirmed | `data/scripts/lib/register_achievements.lua:432` | unresolved | unresolved |
| 432 | [Contender](https://tibia.fandom.com/wiki/Contender) | 1 | false | False | 3 | December 5, 2017 | other | confirmed | `data/scripts/lib/register_achievements.lua:433` | unresolved | unresolved |
| 433 | [Serious Contender](https://tibia.fandom.com/wiki/Serious_Contender) | 2 | true | False | 4 | December 5, 2017 | other | confirmed | `data/scripts/lib/register_achievements.lua:434` | unresolved | unresolved |
| 434 | [Skilled Hunter](https://tibia.fandom.com/wiki/Skilled_Hunter) | 2 | false | False | 5 | December 5, 2017 | other | confirmed | `data/scripts/lib/register_achievements.lua:435` | unresolved | unresolved |
| 435 | [Master Hunter](https://tibia.fandom.com/wiki/Master_Hunter) | 2 | true | False | 6 | December 5, 2017 | other | confirmed | `data/scripts/lib/register_achievements.lua:436` | unresolved | unresolved |
| 436 | [Hunting Permit](https://tibia.fandom.com/wiki/Hunting_Permit) | 1 | false | False | 1 | December 5, 2017 | other | confirmed | `data/scripts/lib/register_achievements.lua:437` | unresolved | unresolved |
| 437 | [Over the Moon](https://tibia.fandom.com/wiki/Over_the_Moon) | 2 | false | True | 5 | December 5, 2017 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:438` | unresolved | unresolved |
| 438 | [His Days are Counted](https://tibia.fandom.com/wiki/His_Days_are_Counted) | 1 | false | True | 1 | December 5, 2017 | quest-or-task, combat, item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:439` | partially-confirmed | `data-otservbr-global/scripts/quests/dangerous_depth/actions_crude_lava_pump_achievements.lua:43` addAchievement |
| 439 | [Duked It Out](https://tibia.fandom.com/wiki/Duked_It_Out) | 1 | false | True | 1 | December 5, 2017 | quest-or-task, combat, item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:440` | partially-confirmed | `data-otservbr-global/scripts/quests/dangerous_depth/actions_crude_lava_pump_achievements.lua:50` addAchievement |
| 440 | [Buried the Baron](https://tibia.fandom.com/wiki/Buried_the_Baron) | 1 | false | True | 1 | December 5, 2017 | quest-or-task, combat, item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:441` | partially-confirmed | `data-otservbr-global/scripts/quests/dangerous_depth/actions_crude_lava_pump_achievements.lua:36` addAchievement |
| 441 | [Death in the Depths](https://tibia.fandom.com/wiki/Death_in_the_Depths) | 1 | false | True | 2 | December 5, 2017 | combat | confirmed | `data/scripts/lib/register_achievements.lua:442` | partially-confirmed | `data-otservbr-global/scripts/quests/dangerous_depth/actions_crude_lava_pump_achievements.lua:57` addAchievement |
| 442 | [Scourge of Scarabs](https://tibia.fandom.com/wiki/Scourge_of_Scarabs) | 1 | false | True | 3 | December 5, 2017 | quest-or-task, combat, item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:443` | unresolved | unresolved |
| 443 | [Cobbled and Patched](https://tibia.fandom.com/wiki/Cobbled_and_Patched) | 2 | false | True | 6 | January 09, 2018 | other | confirmed | `data/scripts/lib/register_achievements.lua:444` | unresolved | unresolved |
| 444 | [Up the Molehill](https://tibia.fandom.com/wiki/Up_the_Molehill) | 1 | false | True | 3 | January 09, 2018 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:445` | unresolved | unresolved |
| 445 | [Master Debater](https://tibia.fandom.com/wiki/Master_Debater) | 1 | true | True | 1 | July 3, 2018 | quest-or-task, combat | confirmed | `data/scripts/lib/register_achievements.lua:446` | unresolved | unresolved |
| 446 | [High and Dry](https://tibia.fandom.com/wiki/High_and_Dry) | 1 | true | True | 2 | July 3, 2018 | dialogue, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:447` | unresolved | unresolved |
| 447 | [Elven Woods](https://tibia.fandom.com/wiki/Elven_Woods) | 1 | false | False | 1 | July 3, 2018 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:448` | unresolved | unresolved |
| 448 | [Long Live the Queen](https://tibia.fandom.com/wiki/Long_Live_the_Queen) | 1 | false | False | 1 | July 3, 2018 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:449` | unresolved | unresolved |
| 449 | [Stronghold of Edron](https://tibia.fandom.com/wiki/Stronghold_of_Edron) | 1 | false | True | 1 | July 3, 2018 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:450` | unresolved | unresolved |
| 450 | [Dwarven Mines](https://tibia.fandom.com/wiki/Dwarven_Mines_(Achievement)) | 1 | false | False | 1 | July 3, 2018 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:451` | unresolved | unresolved |
| 451 | [All Hail the King](https://tibia.fandom.com/wiki/All_Hail_the_King) | 1 | false | False | 1 | July 3, 2018 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:452` | unresolved | unresolved |
| 452 | [Jewel in the Swamp](https://tibia.fandom.com/wiki/Jewel_in_the_Swamp) | 1 | false | False | 1 | July 3, 2018 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:453` | unresolved | unresolved |
| 453 | [The Ogre Steppe](https://tibia.fandom.com/wiki/The_Ogre_Steppe) | 1 | false | True | 1 | July 3, 2018 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:454` | unresolved | unresolved |
| 454 | [Realms of Dreams](https://tibia.fandom.com/wiki/Realms_of_Dreams) | 1 | false | True | 1 | July 3, 2018 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:455` | unresolved | unresolved |
| 455 | [Mummy's Dearest](https://tibia.fandom.com/wiki/Mummy%27s_Dearest) | 1 | false | True | 1 | July 3, 2018 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:456` | unresolved | unresolved |
| 456 | [Daraman's Footsteps](https://tibia.fandom.com/wiki/Daraman%27s_Footsteps) | 1 | false | True | 1 | July 3, 2018 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:457` | unresolved | unresolved |
| 457 | [King of the Jungle](https://tibia.fandom.com/wiki/King_of_the_Jungle) | 1 | false | True | 1 | July 3, 2018 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:458` | unresolved | unresolved |
| 458 | [Ancient Splendor](https://tibia.fandom.com/wiki/Ancient_Splendor) | 1 | false | True | 1 | July 3, 2018 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:459` | unresolved | unresolved |
| 459 | [Liberty Bay Watch](https://tibia.fandom.com/wiki/Liberty_Bay_Watch) | 1 | false | True | 1 | July 3, 2018 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:460` | unresolved | unresolved |
| 460 | [Race to the Pole](https://tibia.fandom.com/wiki/Race_to_the_Pole) | 1 | false | True | 1 | July 3, 2018 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:461` | unresolved | unresolved |
| 461 | [Lizard Kingdom](https://tibia.fandom.com/wiki/Lizard_Kingdom) | 1 | false | True | 1 | July 3, 2018 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:462` | unresolved | unresolved |
| 462 | [Trip to the Beach](https://tibia.fandom.com/wiki/Trip_to_the_Beach) | 1 | false | True | 1 | July 3, 2018 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:463` | unresolved | unresolved |
| 463 | [Glooth Punk](https://tibia.fandom.com/wiki/Glooth_Punk) | 1 | false | True | 1 | July 3, 2018 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:464` | unresolved | unresolved |
| 464 | [Twisted Dreams](https://tibia.fandom.com/wiki/Twisted_Dreams) | 1 | false | True | 1 | July 3, 2018 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:465` | unresolved | unresolved |
| 465 | [Library Liberator](https://tibia.fandom.com/wiki/Library_Liberator) | 1 | false | True | 3 | July 3, 2018 | combat | confirmed | `data/scripts/lib/register_achievements.lua:466` | unresolved | unresolved |
| 466 | [Spectulation](https://tibia.fandom.com/wiki/Spectulation) | 1 | true | True | 1 | July 3, 2018 | exploration | confirmed | `data/scripts/lib/register_achievements.lua:467` | unresolved | unresolved |
| 467 | [Millennial Falcon](https://tibia.fandom.com/wiki/Millennial_Falcon) | 1 | true | True | 3 | July 3, 2018 | quest-or-task, combat | confirmed | `data/scripts/lib/register_achievements.lua:468` | unresolved | unresolved |
| 468 | [Bibliomaniac](https://tibia.fandom.com/wiki/Bibliomaniac) | 1 | false | True | 3 | July 3, 2018 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:469` | unresolved | unresolved |
| 469 | [Battle Mage](https://tibia.fandom.com/wiki/Battle_Mage) | 2 | false | True | 6 | July 3, 2018 | combat | confirmed | `data/scripts/lib/register_achievements.lua:470` | partially-confirmed | `data-otservbr-global/npc/dedoras.lua:192` addAchievement |
| 470 | [Widely Travelled](https://tibia.fandom.com/wiki/Widely_Travelled) | 3 | false | True | 7 | July 3, 2018 | other | confirmed | `data/scripts/lib/register_achievements.lua:471` | unresolved | unresolved |
| 471 | [Running the Rift](https://tibia.fandom.com/wiki/Running_the_Rift) | 1 | false | True | 3 | July 31, 2018 | item-or-interaction, mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:472` | unresolved | unresolved |
| 473 | [Exalted Battle Mage](https://tibia.fandom.com/wiki/Exalted_Battle_Mage) | 1 | false | True | 2 | July 31, 2018 | combat | confirmed | `data/scripts/lib/register_achievements.lua:474` | unresolved | unresolved |
| 474 | [Areas of Effect](https://tibia.fandom.com/wiki/Areas_of_Effect) | 1 | true | False | 3 | September 11, 2018 | other | confirmed | `data/scripts/lib/register_achievements.lua:475` | unresolved | unresolved |
| 475 | [Tied the Knot](https://tibia.fandom.com/wiki/Tied_the_Knot) | 1 | true | True | 1 | December 03, 2018 | quest-or-task, collection | confirmed | `data/scripts/lib/register_achievements.lua:476` | partially-confirmed | `data-otservbr-global/scripts/quests/the_dream_courts_quest/actions_containerRewards.lua:134` addAchievement |
| 476 | [Keeper of the 7 Keys](https://tibia.fandom.com/wiki/Keeper_of_the_7_Keys) | 1 | false | True | 2 | December 03, 2018 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:477` | partially-confirmed | `data-otservbr-global/scripts/quests/the_dream_courts_quest/actions_oldLock.lua:16` addAchievement |
| 477 | [Dream Warrior](https://tibia.fandom.com/wiki/Dream_Warrior) | 2 | false | True | 6 | December 03, 2018 | other | confirmed | `data/scripts/lib/register_achievements.lua:478` | unresolved | unresolved |
| 478 | [Moth Whisperer](https://tibia.fandom.com/wiki/Moth_Whisperer) | 1 | false | True | 3 | December 03, 2018 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:479` | unresolved | unresolved |
| 479 | [Lacewing Catcher](https://tibia.fandom.com/wiki/Lacewing_Catcher) | 1 | false | True | 3 | December 03, 2018 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:480` | unresolved | unresolved |
| 480 | [No Horse Open Sleigh](https://tibia.fandom.com/wiki/No_Horse_Open_Sleigh) | 1 | false | True | 3 | December 11, 2018 | collection | confirmed | `data/scripts/lib/register_achievements.lua:481` | unresolved | unresolved |
| 481 | [Raider in the Dark](https://tibia.fandom.com/wiki/Raider_in_the_Dark) | 2 | false | True | 6 | December 11, 2018 | other | confirmed | `data/scripts/lib/register_achievements.lua:482` | unresolved | unresolved |
| 482 | [Dream Catcher](https://tibia.fandom.com/wiki/Dream_Catcher_(Achievement)) | 1 | false | True | 3 | December 03, 2018 | combat | confirmed | `data/scripts/lib/register_achievements.lua:483` | unresolved | unresolved |
| 483 | [Champion of Summer](https://tibia.fandom.com/wiki/Champion_of_Summer) | 1 | true | True | 2 | December 03, 2018 | quest-or-task, combat | confirmed | `data/scripts/lib/register_achievements.lua:484` | unresolved | unresolved |
| 484 | [Champion of Winter](https://tibia.fandom.com/wiki/Champion_of_Winter) | 1 | true | True | 2 | December 03, 2018 | quest-or-task, combat | confirmed | `data/scripts/lib/register_achievements.lua:485` | unresolved | unresolved |
| 486 | [Bewitcher](https://tibia.fandom.com/wiki/Bewitcher) | 2 | true | False | 5 | March 26, 2019 | event-or-raid, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:487` | unresolved | unresolved |
| 487 | [Gryphon Rider](https://tibia.fandom.com/wiki/Gryphon_Rider) | 1 | false | True | 3 | July 29, 2019 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:488` | unresolved | unresolved |
| 488 | [Sculptor Apprentice](https://tibia.fandom.com/wiki/Sculptor_Apprentice) | 1 | true | True | 2 | July 29, 2019 | other | confirmed | `data/scripts/lib/register_achievements.lua:489` | partially-confirmed | `data-otservbr-global/npc/alyxo.lua:199` addAchievement |
| 489 | [Sun and Sea](https://tibia.fandom.com/wiki/Sun_and_Sea) | 2 | false | True | 5 | July 29, 2019 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:490` | unresolved | unresolved |
| 490 | [A Study in Scarlett](https://tibia.fandom.com/wiki/A_Study_in_Scarlett) | 1 | true | True | 3 | July 29, 2019 | combat | confirmed | `data/scripts/lib/register_achievements.lua:491` | partially-confirmed | `data-otservbr-global/scripts/quests/grave_danger_quest/creaturescripts_boss_kill.lua:70` addAchievement |
| 491 | [Avid Spectral Reader](https://tibia.fandom.com/wiki/Avid_Spectral_Reader) | 1 | true | True | 1 | July 29, 2019 | item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:492` | unresolved | unresolved |
| 492 | [Hippofoddermus](https://tibia.fandom.com/wiki/Hippofoddermus) | 1 | true | True | 1 | July 29, 2019 | other | confirmed | `data/scripts/lib/register_achievements.lua:493` | unresolved | unresolved |
| 493 | [Inquisition's Hand](https://tibia.fandom.com/wiki/Inquisition%27s_Hand) | 1 | false | True | 3 | July 29, 2019 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:494` | partially-confirmed | `data-otservbr-global/npc/jack_springer.lua:171` addAchievement |
| 494 | [The Empire's Glory](https://tibia.fandom.com/wiki/The_Empire%27s_Glory) | 1 | false | True | 1 | July 29, 2019 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:495` | unresolved | unresolved |
| 495 | [Inquisition's Arm](https://tibia.fandom.com/wiki/Inquisition%27s_Arm) | 1 | false | True | 2 | August 21, 2019 | other | confirmed | `data/scripts/lib/register_achievements.lua:496` | unresolved | unresolved |
| 496 | [Traditionalist](https://tibia.fandom.com/wiki/Traditionalist) | 2 | false | True | 6 | October 09, 2019 | other | confirmed | `data/scripts/lib/register_achievements.lua:497` | unresolved | unresolved |
| 497 | [Do a Barrel Roll!](https://tibia.fandom.com/wiki/Do_a_Barrel_Roll!) | 1 | false | True | 3 | October 09, 2019 | collection | confirmed | `data/scripts/lib/register_achievements.lua:498` | unresolved | unresolved |
| 499 | [Orcsoberfest Welcome](https://tibia.fandom.com/wiki/Orcsoberfest_Welcome) | 1 | true | True | 3 | October 09, 2019 | combat | confirmed | `data/scripts/lib/register_achievements.lua:500` | unresolved | unresolved |
| 500 | [Prospectre](https://tibia.fandom.com/wiki/Prospectre) | 1 | true | True | 1 | December 02, 2019 | quest-or-task, combat | confirmed | `data/scripts/lib/register_achievements.lua:501` | unresolved | unresolved |
| 501 | [Nothing but Hot Air](https://tibia.fandom.com/wiki/Nothing_but_Hot_Air) | 1 | false | False | 3 | December 02, 2019 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:502` | unresolved | unresolved |
| 502 | [Verminbane](https://tibia.fandom.com/wiki/Verminbane) | 1 | false | False | 1 | December 02, 2019 | quest-or-task, combat | confirmed | `data/scripts/lib/register_achievements.lua:503` | unresolved | unresolved |
| 503 | [Monsterhunter](https://tibia.fandom.com/wiki/Monsterhunter) | 1 | false | False | 2 | December 02, 2019 | quest-or-task, combat | confirmed | `data/scripts/lib/register_achievements.lua:504` | unresolved | unresolved |
| 504 | [Taskmaster](https://tibia.fandom.com/wiki/Taskmaster) | 1 | false | False | 3 | December 02, 2019 | quest-or-task, combat | confirmed | `data/scripts/lib/register_achievements.lua:505` | unresolved | unresolved |
| 505 | [Mainstreet Nightmare](https://tibia.fandom.com/wiki/Mainstreet_Nightmare) | 1 | false | True | 2 | December 02, 2019 | other | confirmed | `data/scripts/lib/register_achievements.lua:506` | unresolved | unresolved |
| 506 | [Falconer](https://tibia.fandom.com/wiki/Falconer) | 1 | false | False | 2 | December 02, 2019 | other | confirmed | `data/scripts/lib/register_achievements.lua:507` | unresolved | unresolved |
| 507 | [Steppe Elegance](https://tibia.fandom.com/wiki/Steppe_Elegance) | 1 | false | False | 3 | December 02, 2019 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:508` | unresolved | unresolved |
| 508 | [Beyonder](https://tibia.fandom.com/wiki/Beyonder) | 1 | false | True | 3 | December 02, 2019 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:509` | partially-confirmed | `data-otservbr-global/scripts/quests/feaster_of_souls/creaturescripts_pale_worm_death.lua:19` addAchievement |
| 510 | [Drama in Darama](https://tibia.fandom.com/wiki/Drama_in_Darama) | 1 | false | True | 3 | July 13, 2020 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:511` | unresolved | unresolved |
| 511 | [Malefitz](https://tibia.fandom.com/wiki/Malefitz) | 1 | true | True | 1 | July 13, 2020 | other | confirmed | `data/scripts/lib/register_achievements.lua:512` | unresolved | unresolved |
| 512 | [Lionheart](https://tibia.fandom.com/wiki/Lionheart) | 1 | false | True | 3 | July 13, 2020 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:513` | unresolved | unresolved |
| 513 | [Soul Mender](https://tibia.fandom.com/wiki/Soul_Mender) | 4 | true | True | 10 | July 13, 2020 | combat | conflicting | `data/scripts/lib/register_achievements.lua:514` | conflicting | unresolved |
| 514 | [You Got Horse Power](https://tibia.fandom.com/wiki/You_Got_Horse_Power) | 3 | false | True | 8 | July 13, 2020 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:515` | partially-confirmed | `data/scripts/actions/items/usable_phantasmal_jade_items.lua:36` addAchievement |
| 515 | [Unleash the Beast](https://tibia.fandom.com/wiki/Unleash_the_Beast) | 3 | false | True | 8 | July 13, 2020 | other | confirmed | `data/scripts/lib/register_achievements.lua:516` | unresolved | unresolved |
| 516 | [Well Roared, Lion!](https://tibia.fandom.com/wiki/Well_Roared,_Lion!) | 1 | false | True | 1 | July 13, 2020 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:517` | unresolved | unresolved |
| 518 | [Honorary Rascoohan](https://tibia.fandom.com/wiki/Honorary_Rascoohan) | 1 | false | True | 2 | November 30, 2020 | other | confirmed | `data/scripts/lib/register_achievements.lua:519` | unresolved | unresolved |
| 519 | [Release the Kraken](https://tibia.fandom.com/wiki/Release_the_Kraken) | 1 | false | True | 3 | November 30, 2020 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:520` | partially-confirmed | `data-otservbr-global/scripts/quests/a_pirates_tail/creaturescripts_tentugly_death.lua:13` addAchievement |
| 521 | [Pied Piper](https://tibia.fandom.com/wiki/Pied_Piper) | 1 | true | True | 3 | November 30, 2020 | quest-or-task, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:522` | unresolved | unresolved |
| 522 | [Woodcarver](https://tibia.fandom.com/wiki/Woodcarver) | 1 | true | True | 3 | July 12, 2021 | quest-or-task, combat | confirmed | `data/scripts/lib/register_achievements.lua:523` | unresolved | unresolved |
| 523 | [Bounacean Chivalry](https://tibia.fandom.com/wiki/Bounacean_Chivalry) | 1 | true | True | 2 | July 12, 2021 | combat, item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:524` | unresolved | unresolved |
| 524 | [Knowledge Raider](https://tibia.fandom.com/wiki/Knowledge_Raider_(Achievement)) | 1 | false | True | 3 | July 12, 2021 | quest-or-task, progress-threshold | confirmed | `data/scripts/lib/register_achievements.lua:525` | unresolved | unresolved |
| 525 | [Citizen of Issavi](https://tibia.fandom.com/wiki/Citizen_of_Issavi) | 1 | false | True | 2 | July 12, 2021 | other | confirmed | `data/scripts/lib/register_achievements.lua:526` | unresolved | unresolved |
| 526 | [King's Council](https://tibia.fandom.com/wiki/King%27s_Council) | 1 | false | True | 2 | July 12, 2021 | other | conflicting | `data/scripts/lib/register_achievements.lua:527` | conflicting | unresolved |
| 527 | [Hot on the Trail](https://tibia.fandom.com/wiki/Hot_on_the_Trail) | 1 | false | True | 3 | July 12, 2021 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:528` | partially-confirmed | `data/scripts/actions/items/fiery_horseshoe.lua:32` addAchievement |
| 528 | [Shell We Take a Ride](https://tibia.fandom.com/wiki/Shell_We_Take_a_Ride) | 1 | false | True | 3 | July 12, 2021 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:529` | unresolved | unresolved |
| 529 | [Phantastic!](https://tibia.fandom.com/wiki/Phantastic!) | 1 | false | False | 3 | July 12, 2021 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:530` | unresolved | unresolved |
| 530 | [Some Like It Hot](https://tibia.fandom.com/wiki/Some_Like_It_Hot) | 1 | false | True | 2 | July 12, 2021 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:531` | unresolved | unresolved |
| 531 | [First Achievement](https://tibia.fandom.com/wiki/First_Achievement) | 1 | true | False | 1 | January 07, 2022 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:532` | unresolved | unresolved |
| 532 | [Sharp Dressed](https://tibia.fandom.com/wiki/Sharp_Dressed) | 1 | false | True | 2 | January 07, 2022 | other | confirmed | `data/scripts/lib/register_achievements.lua:533` | unresolved | unresolved |
| 533 | [Engine Driver](https://tibia.fandom.com/wiki/Engine_Driver) | 1 | false | False | 3 | January 07, 2022 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:534` | unresolved | unresolved |
| 534 | [Friendly Fire](https://tibia.fandom.com/wiki/Friendly_Fire) | 1 | false | True | 2 | July 18, 2022 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:535` | unresolved | unresolved |
| 535 | [Wedding Planner](https://tibia.fandom.com/wiki/Wedding_Planner) | 1 | false | True | 3 | July 18, 2022 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:536` | unresolved | unresolved |
| 536 | [Beaver Away](https://tibia.fandom.com/wiki/Beaver_Away) | 1 | false | True | 1 | July 18, 2022 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:537` | unresolved | unresolved |
| 537 | [Snake Pit](https://tibia.fandom.com/wiki/Snake_Pit) | 1 | false | True | 1 | July 18, 2022 | quest-or-task, exploration | confirmed | `data/scripts/lib/register_achievements.lua:538` | unresolved | unresolved |
| 538 | [Royalty of Hazard](https://tibia.fandom.com/wiki/Royalty_of_Hazard) | 1 | false | True | 1 | July 18, 2022 | combat | confirmed | `data/scripts/lib/register_achievements.lua:539` | unresolved | unresolved |
| 539 | [Measuring the World](https://tibia.fandom.com/wiki/Measuring_the_World) | 1 | false | True | 2 | July 18, 2022 | other | confirmed | `data/scripts/lib/register_achievements.lua:540` | unresolved | unresolved |
| 540 | [Ripp-Ripp Hooray!](https://tibia.fandom.com/wiki/Ripp-Ripp_Hooray!) | 1 | false | True | 3 | July 18, 2022 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:541` | partially-confirmed | `data-otservbr-global/npc/gnomadness.lua:91` addAchievement |
| 541 | [Warrior of the Iks](https://tibia.fandom.com/wiki/Warrior_of_the_Iks) | 1 | false | True | 2 | November 28, 2022 | other | confirmed | `data/scripts/lib/register_achievements.lua:542` | unresolved | unresolved |
| 542 | [Mutagenius](https://tibia.fandom.com/wiki/Mutagenius) | 1 | false | True | 2 | November 28, 2022 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:543` | unresolved | unresolved |
| 543 | [Strangest Thing](https://tibia.fandom.com/wiki/Strangest_Thing) | 1 | false | True | 3 | November 28, 2022 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:544` | unresolved | unresolved |
| 544 | [Fully Decayed](https://tibia.fandom.com/wiki/Fully_Decayed) | 1 | false | True | 2 | July 10, 2023 | other | confirmed | `data/scripts/lib/register_achievements.lua:545` | unresolved | unresolved |
| 545 | [Like Fox and Mouse](https://tibia.fandom.com/wiki/Like_Fox_and_Mouse) | 1 | false | True | 3 | July 10, 2023 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:546` | unresolved | unresolved |
| 546 | [The Spirit of Purity](https://tibia.fandom.com/wiki/The_Spirit_of_Purity) | 1 | false | True | 3 | July 10, 2023 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:547` | partially-confirmed | `data/scripts/actions/items/spiritual_horseshoe.lua:32` addAchievement |
| 547 | [Museum Goer](https://tibia.fandom.com/wiki/Museum_Goer) | 1 | false | True | 2 | December 4, 2023 | combat | confirmed | `data/scripts/lib/register_achievements.lua:548` | unresolved | unresolved |
| 548 | [Mystic Predator](https://tibia.fandom.com/wiki/Mystic_Predator) | 1 | false | True | 3 | December 4, 2023 | mount-taming | confirmed | `data/scripts/lib/register_achievements.lua:549` | unresolved | unresolved |
| 549 | [The Rule of Raccool](https://tibia.fandom.com/wiki/The_Rule_of_Raccool) | 1 | false | True | 2 | December 4, 2023 | other | confirmed | `data/scripts/lib/register_achievements.lua:550` | unresolved | unresolved |
| 550 | [A Friend in Need](https://tibia.fandom.com/wiki/A_Friend_in_Need) | 1 | true | True | 2 | July 01, 2024 | quest-or-task | missing | none | conflicting | unresolved |
| 551 | [Holzkopf](https://tibia.fandom.com/wiki/Holzkopf) | 1 | true | True | 1 | July 01, 2024 | item-or-interaction | missing | none | conflicting | unresolved |
| 552 | [I Wanna Fly Away](https://tibia.fandom.com/wiki/I_Wanna_Fly_Away) | 1 | false | True | 3 | July 01, 2024 | quest-or-task, item-or-interaction | confirmed | `data/scripts/lib/register_achievements.lua:551` | unresolved | unresolved |
| 553 | [The Rootwalker](https://tibia.fandom.com/wiki/The_Rootwalker) | 1 | false | True | 2 | July 01, 2024 | other | confirmed | `data/scripts/lib/register_achievements.lua:552` | unresolved | unresolved |
| 554 | [Soul Crusher](https://tibia.fandom.com/wiki/Soul_Crusher) | 1 | false | True | 2 | July 01, 2024 | other | confirmed | `data/scripts/lib/register_achievements.lua:553` | unresolved | unresolved |
| 555 | [Inner Peace](https://tibia.fandom.com/wiki/Inner_Peace) | 1 | false | True | 3 | April 08, 2025 | item-or-interaction | conflicting | `data/scripts/lib/register_achievements.lua:554` | conflicting | unresolved |
| 556 | [Fiend Rider](https://tibia.fandom.com/wiki/Fiend_Rider) | 1 | false | True | 3 | November 25, 2024 | item-or-interaction, mount-taming | conflicting | `data/scripts/lib/register_achievements.lua:555` | conflicting | unresolved |
| 557 | [Fiend Slayer](https://tibia.fandom.com/wiki/Fiend_Slayer) | 1 | false | True | 2 | November 25, 2024 | other | confirmed | `data/scripts/lib/register_achievements.lua:556` | unresolved | unresolved |
| 558 | [Tear the Toxic Veil](https://tibia.fandom.com/wiki/Tear_the_Toxic_Veil) | 3 | false | True | 7 | November 25, 2024 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:557` | unresolved | unresolved |
| 559 | [Hope of the Merudri](https://tibia.fandom.com/wiki/Hope_of_the_Merudri) | 1 | false | True | 2 | April 08, 2025 | quest-or-task | conflicting | `data/scripts/lib/register_achievements.lua:558` | conflicting | unresolved |
| 560 | [Umbral Redeemer](https://tibia.fandom.com/wiki/Umbral_Redeemer) | 2 | false | True | 6 | April 08, 2025 | other | confirmed | `data/scripts/lib/register_achievements.lua:559` | unresolved | unresolved |
| 561 | [Hell Rider](https://tibia.fandom.com/wiki/Hell_Rider) | 1 | false | True | ? | February 18, 2025 | unresolved | confirmed | `data/scripts/lib/register_achievements.lua:560` | unresolved | unresolved |
| 562 | [Alpha Rider](https://tibia.fandom.com/wiki/Alpha_Rider) | 1 | false | True | 3 | February 18, 2025 | item-or-interaction, mount-taming | conflicting | `data/scripts/lib/register_achievements.lua:561` | conflicting | unresolved |
| 564 | [The First of Many](https://tibia.fandom.com/wiki/The_First_of_Many) | 1 | false | True | 3 | July 21, 2025 | other | confirmed | `data/scripts/lib/register_achievements.lua:563` | handler-missing | unresolved |
| 565 | [A Well-Honed Arsenal](https://tibia.fandom.com/wiki/A_Well-Honed_Arsenal) | 2 | false | True | 5 | July 21, 2025 | other | confirmed | `data/scripts/lib/register_achievements.lua:564` | handler-missing | unresolved |
| 566 | [Arsenal of War](https://tibia.fandom.com/wiki/Arsenal_of_War) | 3 | false | True | 7 | July 21, 2025 | other | confirmed | `data/scripts/lib/register_achievements.lua:565` | handler-missing | unresolved |
| 567 | [The Forbidden Build](https://tibia.fandom.com/wiki/The_Forbidden_Build) | 1 | true | True | 3 | July 21, 2025 | other | missing | none | conflicting | unresolved |
| 568 | [Bat Person](https://tibia.fandom.com/wiki/Bat_Person) | 1 | false | True | 3 | July 21, 2025 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:567` | unresolved | unresolved |
| 569 | [Illuminator](https://tibia.fandom.com/wiki/Illuminator) | 1 | false | True | 3 | July 21, 2025 | other | confirmed | `data/scripts/lib/register_achievements.lua:568` | unresolved | unresolved |
| 570 | [Power of Words](https://tibia.fandom.com/wiki/Power_of_Words) | 2 | false | True | 5 | July 21, 2025 | quest-or-task | confirmed | `data/scripts/lib/register_achievements.lua:569` | unresolved | unresolved |
| 572 | [Errand Runner](https://tibia.fandom.com/wiki/Errand_Runner) | 1 | false | False | 3 | November 24, 2025 | quest-or-task, combat | missing | none | conflicting | unresolved |
| 573 | [Workhorse](https://tibia.fandom.com/wiki/Workhorse) | 2 | false | False | 5 | November 24, 2025 | quest-or-task, combat | missing | none | conflicting | unresolved |
| 574 | [Taskaholic](https://tibia.fandom.com/wiki/Taskaholic) | 3 | false | False | ? | November 24, 2025 | unresolved | missing | none | conflicting | unresolved |
| 575 | [Pest Control](https://tibia.fandom.com/wiki/Pest_Control) | 3 | false | False | 7 | November 24, 2025 | quest-or-task | missing | none | conflicting | unresolved |
| 576 | [Mimic](https://tibia.fandom.com/wiki/Mimic_(Achievement)) | 1 | true | True | 1 | November 24, 2025 | progress-threshold | missing | none | conflicting | unresolved |
| 577 | [Bastard](https://tibia.fandom.com/wiki/Bastard) | 2 | false | True | 5 | November 24, 2025 | quest-or-task | missing | none | conflicting | unresolved |
| 578 | [Razor's Edge](https://tibia.fandom.com/wiki/Razor%27s_Edge) | 2 | true | True | 4 | November 24, 2025 | combat | missing | none | conflicting | unresolved |
| 579 | [Lost Letters](https://tibia.fandom.com/wiki/Lost_Letters) | 1 | true | False | 3 | November 24, 2025 | other | missing | none | conflicting | unresolved |
| 580 | [Stagmeister](https://tibia.fandom.com/wiki/Stagmeister) | 1 | true | True | 1 | November 24, 2025 | item-or-interaction | missing | none | conflicting | unresolved |
| 581 | [Feral Trapper](https://tibia.fandom.com/wiki/Feral_Trapper) | 1 | false | False | 2 | November 24, 2025 | quest-or-task | missing | none | conflicting | unresolved |
| 582 | [Castle Crasher](https://tibia.fandom.com/wiki/Castle_Crasher) | 1 | true | False | 1 | March 17, 2026 | other | missing | none | conflicting | unresolved |
| 585 | [A reliable Friend](https://tibia.fandom.com/wiki/A_reliable_Friend) | 1 | false | False | 1 | March 17, 2026 | mount-taming | missing | none | conflicting | unresolved |
| 586 | [Echo Initiate](https://tibia.fandom.com/wiki/Echo_Initiate) | 1 | false | ? | 1 | Summer 2026 | item-or-interaction, event-or-raid | missing | none | conflicting | unresolved |
| 587 | [Echo Hunter](https://tibia.fandom.com/wiki/Echo_Hunter) | 1 | false | ? | 4 | Summer 2026 | unresolved | missing | none | conflicting | unresolved |
| 588 | [Echo Walker](https://tibia.fandom.com/wiki/Echo_Walker) | 2 | false | ? | ? | Summer 2026 | unresolved | missing | none | conflicting | unresolved |
| 591 | [Purrfectly Addicted](https://tibia.fandom.com/wiki/Purrfectly_Addicted) | 1 | true | True | 1 | Summer 2026 | item-or-interaction, progress-threshold | missing | none | conflicting | unresolved |
| 592 | [Six Steps Ahead](https://tibia.fandom.com/wiki/Six_Steps_Ahead) | 1 | false | ? | 2 | Summer 2026 | mount-taming | missing | none | conflicting | unresolved |
| 593 | [Radiant Nimbus](https://tibia.fandom.com/wiki/Radiant_Nimbus) | 1 | false | ? | ? | Summer 2026 | mount-taming | missing | none | conflicting | unresolved |
| 594 | [Amati's Echo](https://tibia.fandom.com/wiki/Amati%27s_Echo) | 2 | false | ? | 4 | Summer 2026 | quest-or-task | missing | none | conflicting | unresolved |
| 595 | [Enlightened, Indeed](https://tibia.fandom.com/wiki/Enlightened,_Indeed) | 1 | false | ? | ? | Summer 2026 | unresolved | missing | none | conflicting | unresolved |

## Persistence and backfill evidence

- generic unlocked-state persistence: `name-keyed-kv-confirmed`
- `src/creatures/players/components/player_achievement.cpp:35` — save-by-canonical-name
- `src/creatures/players/components/player_achievement.cpp:103` — load-by-stored-name
- `src/creatures/players/components/player_achievement.cpp:87` — point-persistence
- compatibility risk: Renaming a canonical achievement can orphan name-keyed unlocked state without migration or aliasing.
- per-achievement historical backfill remains unresolved unless a reviewed subsystem-specific plan proves it.

## Reviewed subsystem evidence

- IDs 564–566: definitions exist, but the dedicated Weapon Proficiency audit proves no threshold award path; status `handler-missing`.
- ID 567: the exact twelve-item proficiency contract is proven, but definition/award/backfill remain absent; status `conflicting`.
- PR #212 repaired immediate first-entry mastery state and exposed `getMasteredWeaponCount()`; it deliberately did not add awards or backfill.

## Missing tests

- runtime registration equality for the complete current registry;
- semantic reachability tests for every static award/progress candidate;
- current-player backfill tests for every subsystem introducing a new award hook;
- denied-path tests proving achievements are not awarded early;
- persistence/reload and canonical-name compatibility tests;
- representative real-client E2E scenarios across quest, NPC, boss, movement, item-use, progress and newest supported content;
- explicit tests for mutually exclusive or intentionally unsupported achievements.

## Repair plan boundary

1. Extend deterministic resolver coverage for selected dynamic tables/wrappers.
2. Validate achievements in small subsystem groups with exact source/runtime evidence.
3. Split metadata conflicts, missing definitions, award hooks and historical backfill into separate focused PRs.
4. Do not add a definition from the wiki alone; prove corresponding content and a safe award/backfill contract.
5. Require focused regression tests and current-head CI for every gameplay PR.

## Current limitations

- this table does not claim full runtime completion;
- static Lua candidate handlers do not prove quest/map/NPC reachability;
- dynamic tables, wrappers, state machines and indirect C++ paths remain unresolved;
- no private map or client asset is required or committed;
- full machine-readable evidence remains a CI artifact; this document is the durable review index.

## Handoff

- branch: `feat/achievements-comprehensive-validation`
- PR: `#238` (draft)
- source revision: `1188274`
- source SHA-256: `8a429425ab7b088758646b07f036afdd1d579188d056491aed8e77650306ae8b`
- completed: source extraction, factual catalogue, full static API scan, registry join, conflict inventory and reviewed Weapon Proficiency overrides;
- incomplete: semantic/runtime validation for most rows, final shared-document refresh and required current-head CI;
- next action: inspect the generated artifact, update task/PR with run IDs and preserve unresolved rows until additional evidence exists.
