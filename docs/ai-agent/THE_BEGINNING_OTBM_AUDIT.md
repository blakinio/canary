# The Beginning — OTBM, runtime and visual evidence audit

## 1. Decision and scope

```text
quest: The Beginning
missions: The Cockroach Plague; Collecting Wood; A Hungry Tailor
area: Rookgaard Tutorial Island
map SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
asset catalogue SHA-256: 93ea5888174ef44b352d7c2b1f8061573a4a260bfaba4b7ec32ea836b9e411ab
appearances SHA-256: aa44a154f30c7ed59acc25f246286396e4043851ef0b54ef3cf3951e46d1ce50
Canary review snapshot: 366b3d4e6bba4cb8d3dee09a8c5a0181cc3d7423
OTBM changed by this audit: no
runtime E2E proven: no
```

This report is evidence-only. It does not modify the OTBM, items, assets, Lua, XML, NPCs, spawns, engine or production configuration. It reuses the existing item/mechanic audit, map export, script resolver, companion-XML reader and factual renderer. No new parser or renderer was created and no AI-generated map image was used.

The shell environment could not resolve GitHub, so a complete fresh clone was unavailable. The existing PR #104 tooling snapshot was used only as the executable tooling base. Every active The Beginning file that affects the classifications below was fetched from current `main` and overlaid exactly before the final resolver run. Therefore global resolver totals are diagnostic; the accepted conclusions are the quest-scoped identifier, position and source matches documented below.

### Classification vocabulary

- `confirmed`: the claimed relationship is supported by the current map and active code/companion data;
- `map-only`: the object/identifier exists in the OTBM but no active handler for the claimed gameplay role was confirmed;
- `script-only`: active script/dialogue/catalogue expects behavior or an object that the audited map/handler set does not provide;
- `unresolved`: evidence is insufficient to decide safely;
- `conflicting`: two or more competing active handlers claim the same event. The final quest-scoped resolver run found **zero** such conflicts.

## 2. Reused tooling and commands

- `tools/ai-agent/otbm_item_audit_tool.py` / native scan output: full-map item and mechanic inventory;
- `tools/ai-agent/otbm_map_tool.py export`: bounded export `31980,32240,5` through `32100,32300,9`;
- `tools/ai-agent/otbm_script_resolution_tool.py`: AID/UID/item/position to active Lua/XML resolution;
- `tools/ai-agent/otbm_render_tool.py`: bounded PNG renders from the real OTBM and real client assets;
- `tools/ai-agent/otbm_world.py`: existing town and companion spawn readers.

Final resolver input contained current-main versions of:

- `data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua`;
- `data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_wood.lua`;
- `data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_door.lua`;
- `data-otservbr-global/scripts/actions/other/others/quest_system1.lua`.

Quest-scoped result: all map-present tutorial AIDs `50058..50081` selected by the active tutorial MoveEvents are handled directly, UID `50085` is handled directly by the Zirella door Action, reward UIDs `50080/50082/50093/50094` resolve through the generic AID `2000` quest reward flow, and AID `50999` remains unresolved. No quest-scoped competing handlers were found.

## 3. Related active files

| Area | Active source |
|---|---|
| storage definitions | `data-otservbr-global/lib/core/storages.lua` |
| quest catalogue | `data-otservbr-global/lib/core/quests/catalog/018_the_beginning.lua` |
| Santiago | `data-otservbr-global/npc/santiago.lua` |
| Zirella | `data-otservbr-global/npc/zirella.lua` |
| Carlos | `data-otservbr-global/npc/carlos.lua` |
| NPC placements | `data-otservbr-global/world/otservbr-npc.xml` |
| monster placements | `data-otservbr-global/world/otservbr-monster.xml` |
| tutorial tiles/gates | `data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua` |
| Zirella wood | `data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_wood.lua` |
| Zirella door | `data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_door.lua` |
| generic quest chests | `data-otservbr-global/scripts/actions/other/others/quest_system1.lua` |
| ladder/sewer | `data/scripts/actions/items/ladder_up.lua` |
| shovel/rope helpers | `data-otservbr-global/scripts/lib/register_actions.lua` |
| monster loot | `data-otservbr-global/monster/vermins/cockroach.lua`, `monster/mammals/deer.lua`, `monster/mammals/rabbit.lua` |
| level-two bridge nearby | `data-otservbr-global/scripts/movements/rookgaard/level_bridge.lua` |

## 4. Storage graph

| Storage | Numeric ID | Active range/role | Status |
|---|---:|---|---|
| `TutorialHintsStorage` | 41670 | route/tutorial hints, observed values 1..21; rope helper checks `<22` | `confirmed` |
| `SantiagoNpcGreetStorage` | 41671 | Santiago dialogue 1..13 | `confirmed` |
| `SantiagoQuestLog` | 41672 | mission 1 states 1..11 | `confirmed` |
| `ZirellaNpcGreetStorage` | 41673 | Zirella dialogue 1..8 | `confirmed` |
| `ZirellaQuestLog` | 41674 | mission 2 states 1..8 | `confirmed` |
| `CarlosNpcTradeStorage` | 41675 | trade permission; current script writes 1 | `confirmed` |
| `CarlosNpcGreetStorage` | 41676 | Carlos dialogue 1..8 | `confirmed` |
| `CarlosQuestLog` | 41677 | mission 3 states 1..8; state 8 means bridge crossed | `confirmed` |

## 5. NPC and spawn evidence

### NPCs

| NPC | Exact companion-XML position | Spawn time | Script | Status |
|---|---|---:|---|---|
| Santiago | `32034,32273,6` | 60 s | `npc/santiago.lua` | `confirmed` |
| Zirella | `32058,32268,7` | 60 s | `npc/zirella.lua` | `confirmed` |
| Carlos | `32082,32263,7` | 60 s | `npc/carlos.lua` | `confirmed` |

### Required monsters and loot

Six cockroaches are placed in the intended cellar at `32035,32284,9`, `32038,32291,9`, `32036,32292,9`, `32038,32293,9`, `32038,32294,9`, and `32034,32296,9`. The active cockroach definition drops one cockroach leg with 100% chance; `items.xml` maps cockroach leg to item `7882`, and Santiago removes three item `7882`. This chain is `confirmed`.

The Carlos hunting area contains active deer and rabbit spawns. Representative quest-adjacent placements include deer at `32074,32265,7` and `32061,32272,7`, and rabbits at `32083,32273,7`, `32088,32258,7`, `32092,32260,7`, `32094,32261,7`, `32092,32265,7`, `32096,32263,7`, `32095,32266,7`, and `32098,32266,7`. Deer loot includes meat `3577` and ham `3582`; rabbit loot includes meat `3577`. Carlos' shop accepts both IDs for two gold. The source items and shop catalogue are `confirmed`.

No boss spawn is part of The Beginning in the audited region: `confirmed`.

## 6. Mission 1 — The Cockroach Plague

### Route, rewards and passages

| Element | Map evidence | Active handler/evidence | Classification |
|---|---|---|---|
| Santiago coat chest | chest `7757`, AID `2000`, UID `50080` at `32032,32276,5`; bag `2853` contains coat `3562` | generic `questSystem1`; tutorial `5`; Santiago greet set to 3 | `confirmed` |
| torch chest | chest `7757`, AID `2000`, UID `50082` at `32033,32278,8`; contains torch `2920` | generic `questSystem1`; tutorial `6` | `confirmed` |
| sewer grate | item `435` at `32035,32285,8` | generic ladder Action registers item `435` | `confirmed` |
| cellar ladder | item `1948` at `32035,32285,9` | generic ladder table Action | `confirmed` |
| return ladder | item `1948` at `32038,32273,8` | generic ladder table Action | `confirmed` |
| cockroach proof | six cellar spawns; loot item `7882` | Santiago removes 3 legs and grants 100 XP | `confirmed` |
| first-kill/chase tutorial event | cockroaches and route exist | no active current creature event was found that emits the historical first-kill/chase hints | `map-only` |
| corpse-looting tutorial event | cockroach corpses can exist | no active current corpse Action was found for the historical corpse hint | `map-only` |
| snake-head lever | small snake head `5058` at `32034,32272,8`; lever `2772` at `32034,32274,8` | no UID and no active link/storage dependency | `map-only` |

All map-present AIDs `50058..50072` except absent `50073` resolve to the merged tutorial MoveEvent. AID `50073` is not present in the audited region and must not be registered merely because it existed historically: `confirmed` absence.

### Santiago persistence discrepancy

The normal transition after the fish lesson writes `SantiagoNpcGreetStorage = 12` and `SantiagoQuestLog = 10`. The alternate `easy` keyword writes the same quest-log state but persists greet storage `11`, while advancing the in-memory conversation to the Zirella question. The mismatch is directly present in current code: `confirmed`. It can resume the wrong dialogue after focus loss/relogin and belongs in the later repair plan; it does not require an OTBM edit.

## 7. Mission 2 — Collecting Wood

### Trees, branch and cart

The OTBM contains dead tree item `7753` at eight positions:

- handler-whitelisted quest trees: `32066,32288,7`, `32067,32281,7`, `32073,32276,7`, `32079,32285,7`, `32081,32276,7` — `confirmed`;
- additional map trees outside the exact quest whitelist: `32076,32291,7`, `32086,32283,7`, `32088,32278,7` — `map-only` for this quest mechanic, but not automatically defects because they may be ambient scenery.

The current Action requires both Zirella storages at stage `6`, creates branch item `7772` on the player's map tile, applies a five-second per-character cooldown, sends tutorial `24`, and advances the hint to at least `15`. The cart is item `7751` at `32062,32271,7`; using branch `7772` with that exact cart consumes one branch, sends green magic and writes both Zirella storages to `7`. This chain is `confirmed`.

A static branch item `7772` also exists on the cart tile. Its presence and the item-ID Action are confirmed, but whether that static item is intentionally usable, a visual marker, or should be immovable is not established by the OTBM attributes: `unresolved`. The audit does not remove or alter it.

### Zirella reward room

| Element | Map evidence | Active handler/evidence | Classification |
|---|---|---|---|
| sealed door | item `6898`, UID `50085`, `32058,32266,7` | current UID Action requires `ZirellaNpcGreetStorage >= 8`, transforms `6898 ↔ 6899`, uses normal sounds and obstruction check | `confirmed` |
| shovel chest | chest `7757`, AID `2000`, UID `50093`, `32059,32265,7`; contains shovel `3457` | generic reward flow; tutorial `10` now maps to UID `50093` | `confirmed` |
| cave-entry stone pile | inline item `7749`, `32070,32266,7` | shared shovel helper writes hint `19`, transforms to hole `594`, reverts after 30 s | `confirmed` |

The merged door/tutorial correction is present in current `main`; it is not an outstanding finding in this report.

## 8. Cave and rope route

| Element | Map evidence | Active handler/evidence | Classification |
|---|---|---|---|
| rope chest | chest `7757`, AID `2000`, UID `50094`, `32067,32264,8`; contains rope `3003` | generic reward flow; tutorial `11` maps to UID `50094` | `confirmed` |
| rope spot | item `7762`, AID `50079`, `32070,32266,8` | shared rope helper and tutorial MoveEvent | `confirmed` |
| cave tutorial zone | AIDs `50078`, `50079`, `50081` at exact appendix positions | active tutorial MoveEvent | `confirmed` |

The rope helper sends the successful-exit message while `TutorialHintsStorage < 22` but does not write state `22`. The message can therefore repeat on later uses when the storage remains `21`: `confirmed` code discrepancy. The passage itself works, so this is not a progression blocker.

## 9. Mission 3 — A Hungry Tailor

### Confirmed map/spawn inputs

Carlos is present at `32082,32263,7`. Deer/rabbit spawns and loot provide meat `3577` and ham `3582`, and the shop advertises both for two gold: `confirmed`.

### Current runtime defects

1. At initial conversation state 1, saying `outfit` sends the final tutorial-completion dialogue and writes `CarlosQuestLog = 7` plus `CarlosNpcGreetStorage = 8`, bypassing the food/hunting/trade chain: `confirmed`.
2. `onTradeRequest` exists and checks `CarlosNpcTradeStorage == 1`, but it is not registered as `CALLBACK_ON_TRADE_REQUEST`: `confirmed`.
3. `onSellItem` only sends the sale message. No successful meat/ham sale writes persistent stage `7`: `confirmed`.
4. The existing `ready` path requires conversation state `7`, so the intended path cannot reach it without the `outfit` bypass: `confirmed`.
5. Tutorial `13` is not emitted by the current trade-opening path: `confirmed`.

These are NPC/runtime defects; no OTBM change is indicated.

## 10. Rookgaard border and terminal state

Four wooden-floor items `7886` carry AID `50999` and the description "This is the border to the village of Rookgaard":

- `32073,32252,6`;
- `32074,32252,6`;
- `32075,32252,6`;
- `32076,32252,6`.

The final resolver finds no active handler for AID `50999`. The quest catalogue defines `CarlosQuestLog = 8` as having passed the bridge, and no other active source found in this audit writes that terminal value. The border is therefore `map-only` and is the remaining map-to-runtime progression blocker after Carlos stage 7.

AID `50089`, used by historical implementations, is absent from the audited region. It must not be registered or copied onto the map by inference: `confirmed` absence. The nearby current AID `50998` is a separate level-two bridge at `32091,32175,6` and is not the tutorial terminal border.

The OTBM town table defines **Rookgaard as town ID 3** with temple `32097,32219,7`: `confirmed`. Historical examples using `Town(6)` are incompatible with this current map and must not be copied.

The exact one-way movement, rejection side, final destination offset, tutorial `14` timing and town reassignment behavior still require a focused contract/runtime test before implementation: `unresolved`.

## 11. Advertised `skip tutorial`

Carlos' completion dialogue and quest catalogue advertise saying `skip tutorial` to Santiago, but Santiago has no active matching keyword/callback. The advertised feature is `script-only`. Safe implementation is still `unresolved` because current evidence does not define eligibility, partial-progress handling, destination, town assignment, terminal storages, or forfeited rewards/experience. Historical code alone is insufficient.

## 12. OTBM teleport and house-door inventory

- Quest route: no required OTBM teleport-destination attribute is used; movement is performed by stairs, ladders, the temporary shovel hole, rope spot and ordinary walking: `confirmed`.
- Nearby map items `1758` at `32032,32285,7` and `32032,32286,7` have teleport destination `0,0,0`. The engine recognizes map teleport attributes, but their intended gameplay role and relation to this quest are not established: `unresolved`. They are not modified.
- House-door attributes in the audited region: none. Zirella's gate is a normal door with UID `50085`, not a house-door ID: `confirmed`.

## 13. Factual render evidence

All renders were produced by the existing OTBM renderer from the map and client assets named in section 1. Every render report records `missingAppearanceCount = 0` and `missingSpriteCount = 0`. PNG/JSON outputs remain local artifacts and are not committed.

| Artifact | Bounds | PNG SHA-256 | Visual purpose |
|---|---|---|---|
| `the-beginning-floor5-coat-chest.png` | `32028,32272,5`–`32037,32280,5` | `d99f5648fd1f0a5000adab58cf9b289244707c4bc7787b785433ce990de2f75b` | Santiago upstairs/coat chest |
| `the-beginning-santiago-hut.png` | `32027,32269,6`–`32042,32289,6` | `6dfe52ac99b7426c59492ec221e0099302cb68079cc0738c11cbe92b22ed7767` | Santiago hut and approach |
| `the-beginning-rookgaard-border.png` | `32068,32247,6`–`32081,32258,6` | `0858f729e1dc476000edc7fd0298e2eaf94a6aca812b2cdfbf4a666da6eb3ad7` | four-tile wooden border |
| `the-beginning-zirella-house-cart.png` | `32054,32261,7`–`32076,32278,7` | `5e7653bdc847702d1551ff0525d93d8930f479257664faf27d6f25762e666d7b` | Zirella house, door, reward room, cart/forest route |
| `the-beginning-carlos-hunt.png` | `32078,32255,7`–`32100,32277,7` | `4898da0e56b8d2c80a4caf62c509c96e889a1a4514a632939b4adea612def4cc` | Carlos hunting area |
| `the-beginning-cave-rope.png` | `32063,32261,8`–`32074,32271,8` | `b0cbf57e5b2b8d4059264212d4cbb4bf4d3940eb3022f1b37b30c5c210fce267` | rope chest and cave exit |
| `the-beginning-cellar.png` | `32031,32282,9`–`32040,32298,9` | `2624f4eced00228e9038504cbaa7147181863bb6fcf8ff7931129ebbf7aababc` | tutorial cockroach cellar |

## 14. Complete discrepancy list and priority

| Priority | Finding | Classification | Regression risk | Likely files if later approved |
|---|---|---|---|---|
| P0 | Carlos `outfit` bypass, unregistered trade callback and missing successful-sale transition | `confirmed` | medium: NPC trade/state machine | `data-otservbr-global/npc/carlos.lua`; focused tests |
| P0 | AID `50999` has four border placements but no terminal handler; `CarlosQuestLog = 8` unreachable | `map-only` | high: one-way travel, town and terminal storage | new focused MoveEvent under `scripts/quests/the_beginning`; tests; no OTBM edit |
| P1 | Santiago `easy` persists greet state 11 instead of the normal state 12 | `confirmed` | low/medium: dialogue resume and duplicate reward prevention | `data-otservbr-global/npc/santiago.lua`; focused tests |
| P1 | advertised `skip tutorial` has no implementation and lacks a safe current contract | `script-only` / implementation `unresolved` | high: teleport/town/rewards/storage bypass | do not implement until contract is proven |
| P2 | rope-success message can repeat because stage 22 is checked but never written | `confirmed` | low: hint-only | `data-otservbr-global/scripts/lib/register_actions.lua`; focused test |
| P2 | first-kill/chase and corpse-looting tutorial hints have no active handlers | `map-only` | low/medium: creature/corpse event scope | separate creature/action scripts and tests only after exact current contract |
| P3 | snake-head lever has map objects but no active mechanic or quest dependency | `map-only` | medium for cosmetic-only gain | preserve; no repair without requirement |
| P3 | two nearby item-1758 teleport attributes target `0,0,0` | `unresolved` | unknown; potentially broader map issue | separate map-mechanic audit; no edit here |
| none | three extra dead trees are outside the exact whitelist | `map-only` for quest use | low | preserve unless gameplay requirement proves otherwise |

Already fixed on current `main` and therefore excluded from outstanding repair scope: Zirella branch/cart progression, UID `50085` door seal, shovel/rope tutorial UID mapping, and the map-present tutorial AID MoveEvents.

## 15. Required tests before any repair merge

### Carlos

- stage 1 `outfit` advances only to stage 2 and tutorial 12;
- shop cannot open outside accepted stage 6;
- opening trade emits tutorial 13 without completing the mission;
- failed sale does not advance state;
- successful sale of exactly meat `3577` or ham `3582` advances both relevant states to 7 once;
- shop transaction remains authoritative for item removal and payment;
- `ready` completes only from stage 7;
- global datapack runtime smoke.

### AID 50999 border

- all four exact placements select the same MoveEvent;
- below-required Carlos stage is returned to the correct side with canonical text;
- allowed crossing writes `CarlosQuestLog = 8` exactly once;
- Rookgaard town ID is 3 from the current OTBM, not historical ID 6;
- exact destination is walkable and has floor;
- reverse crossing/one-way rule is explicit and tested;
- tutorial 14 timing is tested;
- relog/re-entry is idempotent;
- resolver reports all four placements handled and zero conflicts;
- global datapack runtime smoke plus live-world E2E.

### Santiago and hint-only fixes

- `easy` and normal response persist identical greet/log states;
- fish cannot be granted twice through reconnect/focus-loss paths;
- rope message advances to state 22 once and does not repeat;
- creature/corpse events, if implemented, are owner-safe and fire only at the intended tutorial state;
- no effect outside the exact Tutorial Island context.

## Appendix A — exact AID placement and resolver inventory

The table intentionally separates AID namespace from UID namespace. Values `50082..50087` are absent as The Beginning AIDs in this region even though some of the same numbers are used as UIDs or unrelated AIDs elsewhere.

| AID | Placements in audited region | Exact positions | Resolver evidence |
|---:|---:|---|---|
| `50058` | 8 | 31984,32273,7; 31985,32274,7; 31985,32275,7; 31985,32276,7; 31985,32277,7; 31985,32278,7; 31985,32279,7; 31985,32280,7 | {'handled-directly': 8}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50059` | 3 | 32001,32277,7; 32001,32278,7; 32001,32279,7 | {'handled-directly': 3}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50060` | 4 | 32008,32276,7; 32008,32277,7; 32008,32278,7; 32008,32279,7 | {'handled-directly': 4}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50061` | 12 | 32019,32268,7; 32019,32269,7; 32019,32270,7; 32019,32271,7; 32019,32272,7; 32019,32273,7; 32019,32274,7; 32019,32275,7; 32019,32276,7; 32019,32277,7; 32019,32278,7; 32019,32279,7 | {'handled-directly': 12}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50062` | 3 | 32024,32272,7; 32024,32273,7; 32024,32274,7 | {'handled-directly': 3}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50063` | 3 | 32032,32272,6; 32032,32273,6; 32032,32274,6 | {'handled-directly': 3}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50064` | 1 | 32032,32277,5 | {'handled-directly': 1}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50065` | 1 | 32038,32273,8 | {'handled-directly': 1}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50066` | 10 | 32057,32275,7; 32058,32275,7; 32060,32273,7; 32062,32273,7; 32063,32273,7; 32064,32273,7; 32065,32273,7; 32067,32273,7; 32069,32273,7; 32070,32273,7 | {'handled-directly': 10}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50067` | 7 | 32033,32284,8; 32034,32284,8; 32035,32284,8; 32036,32284,8; 32037,32284,8; 32038,32284,8; 32039,32284,8 | {'handled-directly': 7}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50068` | 1 | 32035,32285,9 | {'handled-directly': 1}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50069` | 21 | 32032,32283,9; 32033,32283,9; 32034,32283,9; 32035,32283,9; 32036,32283,9; 32037,32283,9; 32032,32286,9; 32032,32287,9; 32033,32286,9; 32033,32287,9; 32034,32284,9; 32034,32285,9; 32034,32286,9; 32034,32287,9; 32035,32286,9; 32036,32284,9; 32036,32286,9; 32036,32286,9; 32036,32287,9; 32037,32286,9; 32037,32287,9 | {'handled-directly': 21}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50070` | 3 | 32025,32272,6; 32025,32273,6; 32025,32274,6 | {'handled-directly': 3}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50071` | 4 | 32045,32270,6; 32045,32271,6; 32045,32272,6; 32045,32273,6 | {'handled-directly': 4}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50072` | 1 | 32033,32277,6 | {'handled-directly': 1}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50073` | 0 | — | absent in audited region |
| `50074` | 3 | 32046,32270,7; 32046,32271,7; 32046,32272,7 | {'handled-directly': 3}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50075` | 14 | 32058,32277,7; 32058,32278,7; 32060,32277,7; 32061,32277,7; 32062,32277,7; 32063,32277,7; 32068,32275,7; 32069,32275,7; 32070,32274,7; 32071,32274,7; 32072,32273,7; 32064,32277,7; 32065,32277,7; 32066,32277,7 | {'handled-directly': 14}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50076` | 15 | 32059,32274,7; 32061,32272,7; 32061,32274,7; 32062,32272,7; 32062,32274,7; 32063,32272,7; 32063,32274,7; 32065,32270,7; 32065,32271,7; 32064,32272,7; 32064,32274,7; 32065,32272,7; 32065,32274,7; 32066,32274,7; 32067,32274,7 | {'handled-directly': 15}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50077` | 3 | 32057,32267,7; 32058,32267,7; 32059,32267,7 | {'handled-directly': 3}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50078` | 7 | 32065,32262,7; 32068,32261,7; 32068,32262,7; 32068,32263,7; 32068,32264,7; 32068,32265,7; 32068,32266,7 | {'handled-directly': 7}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50079` | 1 | 32070,32266,8 | {'handled-directly': 1}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50080` | 10 | 32067,32260,7; 32067,32261,7; 32067,32262,7; 32067,32263,7; 32067,32264,7; 32067,32265,7; 32067,32266,7; 32067,32267,7; 32067,32268,7; 32067,32269,7 | {'handled-directly': 10}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50081` | 16 | 32069,32263,8; 32068,32264,8; 32068,32265,8; 32068,32266,8; 32068,32267,8; 32069,32264,8; 32069,32265,8; 32069,32266,8; 32069,32267,8; 32066,32268,8; 32067,32268,8; 32068,32268,8; 32069,32268,8; 32069,32269,8; 32069,32270,8; 32069,32271,8 | {'handled-directly': 16}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50082` | 0 | — | absent in audited region |
| `50083` | 0 | — | absent in audited region |
| `50084` | 0 | — | absent in audited region |
| `50085` | 0 | — | absent in audited region |
| `50086` | 0 | — | absent in audited region |
| `50087` | 0 | — | absent in audited region |
| `50088` | 6 | 32078,32266,7; 32078,32267,7; 32078,32268,7; 32078,32269,7; 32078,32270,7; 32078,32271,7 | {'handled-directly': 6}; data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua |
| `50089` | 0 | — | absent in audited region |
| `50998` | 0 | — | absent in audited region |
| `50999` | 4 | 32073,32252,6; 32074,32252,6; 32075,32252,6; 32076,32252,6 | {'unresolved': 4}; no active handler |

## Appendix B — key UID/item inventory

| UID/AID | Item | Exact position | Contents/destination | Classification |
|---|---:|---|---|---|
| UID `50080`, AID `2000` | chest `7757` | `32032,32276,5` | bag `2853` → coat `3562` | `confirmed` |
| UID `50082`, AID `2000` | chest `7757` | `32033,32278,8` | torch `2920` | `confirmed` |
| UID `50085` | door `6898` | `32058,32266,7` | opens to `6899` after Zirella stage 8 | `confirmed` |
| UID `50093`, AID `2000` | chest `7757` | `32059,32265,7` | shovel `3457` | `confirmed` |
| UID `50094`, AID `2000` | chest `7757` | `32067,32264,8` | rope `3003` | `confirmed` |
| AID `50999` | wooden floor `7886` ×4 | `32073..32076,32252,6` | terminal border; no active handler | `map-only` |
| — | cart `7751` | `32062,32271,7` | branch target | `confirmed` |
| — | static branch `7772` | `32062,32271,7` | intended static role not proven | `unresolved` |
| — | loose stone pile `7749` | `32070,32266,7` | temporary hole `594` | `confirmed` |
| AID `50079` | rope spot `7762` | `32070,32266,8` | rope exit | `confirmed` |
| — | small snake head `5058` | `32034,32272,8` | no active link | `map-only` |
| — | lever `2772` | `32034,32274,8` | no active link | `map-only` |
| teleport attr | item `1758` | `32032,32285,7` | destination `0,0,0` | `unresolved` |
| teleport attr | item `1758` | `32032,32286,7` | destination `0,0,0` | `unresolved` |

## Final audit conclusion

The intended Santiago → Zirella → cave → Carlos route is geographically present and visually coherent. Current `main` has complete Santiago route MoveEvents, functional reward chests, working Zirella wood/cart progression, the Zirella door gate, shovel/rope route and valid food sources. The remaining core blockers are in active runtime state transitions: Carlos cannot finish normally, and AID `50999` does not complete the final bridge crossing. The map does not need to be edited for either confirmed blocker.

No repair is authorized by this document. The next deliverable is a separate, ordered repair plan grounded in this report.
