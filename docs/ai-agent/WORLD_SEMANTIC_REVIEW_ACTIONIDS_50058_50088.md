# World Semantic Review — OTBM `actionId 50058..50088`

## Decision

```text
component: World Semantic Review
quest/area: The Beginning / Rookgaard Tutorial Island
selected unresolved identifiers: 24
selected placements: 157
decision: missing-script
confidence: high
runtime status after this review: runtime-unresolved
map change: none
required follow-up: separate gameplay/Lua restoration PR
```

The selected action IDs are not legacy decorations. They are the retained map-side keys for two missing `MoveEvent` families that historically implemented the Rookgaard tutorial:

1. tutorial hint tiles (`50058..50069`, `50075..50079`, `50081`);
2. tutorial stop/progression tiles (`50070`, `50071`, `50072`, `50074`, `50080`, `50088`).

The active Canary datapack contains no handler for these values. Current quest data still retains the matching NPC flow, storages, reward chests and exact tutorial-effect positions, so the behavior was not replaced by a different active mechanism.

**Preserve every map attribute.** The correct repair surface is Lua/gameplay, not OTBM.

---

## 1. Scope

Reviewed unresolved values present in the verified map:

```text
50058 50059 50060 50061 50062 50063 50064 50065
50066 50067 50068 50069 50070 50071 50072
50074 50075 50076 50077 50078 50079 50080 50081
50088
```

Not classified by this decision:

- `50073`: no placement in the verified map;
- `50082..50087`: present elsewhere and already runtime-resolved by unrelated Pits of Inferno / Deeper Banuta handlers;
- `50089`: present in historical tutorial code but absent from the verified map and outside this selected unresolved set.

Numeric adjacency must not be used as quest evidence.

---

## 2. Verified map baseline

```text
source: /mnt/data/otservbr(3).otbm
size: 184,776,037 bytes
SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2

full map:
tiles: 17,972,761
item placements: 23,359,571
mechanic placements: 9,339

selected group:
action IDs: 24
placements: 157
unique map tiles: 156
bounds: 31984,32260,5 to 32078,32287,9
```

`actionId 50069` has 21 placements on 20 tiles because two marked items share tile `32036,32286,9`.

---

## 3. Area identification

The placement cluster is the tutorial route used by **The Beginning** quest:

- Santiago is placed at `32034,32273,6`;
- Zirella is placed at `32058,32268,7`;
- Carlos is placed at `32082,32263,7`;
- the map contains the nearby sign text `To the Village`;
- the active quest catalogue defines the Santiago, Zirella and Carlos mission chain;
- the active NPC scripts use `Storage.Quest.U8_2.TheBeginningQuest.*`;
- active NPC effects point at exact selected marker positions:
  - Santiago points at `32033,32277,6`, the single `actionId 50072` tile;
  - Santiago marks `32045,32270,6` as `To Zirella`, one of the `actionId 50071` tiles;
  - Zirella points at `32064,32273,7`, one of the `actionId 50066` tiles.

This is direct active-world evidence, not identification from coordinate proximity alone.

---

## 4. Current runtime evidence

### 4.1. No active handlers

The canonical resolver finds no active Lua/XML handler for any of the 24 selected identifiers. Exact source searches also find no:

- `MoveEvent:aid(...)` registrations;
- legacy movement XML registrations;
- active positional replacement covering the complete tile groups;
- generic engine path consuming these AIDs;
- active dynamic registration table containing these values.

Therefore all 157 placements remain **runtime-unresolved**.

### 4.2. Matching quest state still exists

Current Canary retains:

```text
Storage.Quest.U8_2.TheBeginningQuest.TutorialHintsStorage = 41670
Storage.Quest.U8_2.TheBeginningQuest.SantiagoNpcGreetStorage = 41671
Storage.Quest.U8_2.TheBeginningQuest.SantiagoQuestLog = 41672
Storage.Quest.U8_2.TheBeginningQuest.ZirellaNpcGreetStorage = 41673
Storage.Quest.U8_2.TheBeginningQuest.ZirellaQuestLog = 41674
Storage.Quest.U8_2.TheBeginningQuest.CarlosNpcTradeStorage = 41675
Storage.Quest.U8_2.TheBeginningQuest.CarlosNpcGreetStorage = 41676
Storage.Quest.U8_2.TheBeginningQuest.CarlosQuestLog = 41677
```

The active rope/shovel helper still reads `TutorialHintsStorage` and the shovel branch advances it to `19`, but no active movement script advances the earlier/later stages used by the map markers.

### 4.3. Matching world objects remain

The verified map retains the tutorial route and rewards, including:

```text
Santiago tutorial chest UID 50080: 32032,32276,5
Santiago cellar chest UID 50082: 32033,32278,8
Zirella door UID 50085: 32058,32266,7
Tutorial shovel chest UID 50093: 32059,32265,7
Tutorial rope chest UID 50094: 32067,32264,8
```

The map-side AIDs therefore coexist with an active quest skeleton; they are not orphaned geometry from an unrelated area.

---

## 5. Independent historical corroboration

The same two event families appear in multiple independent historical ORTS/TFS distributions.

Primary historical reference:

```text
repository: slawkens/orts2
commit: 87d2f3e3e15d5d53da81152cef287dff591ab4c5
path: data/scripts/quests/missions/rookgaard_tutorial_island.lua
```

It registers:

```text
tutorialTiles:aid(
  50058,50059,50060,50061,50062,50063,50064,50065,
  50066,50067,50068,50069,50075,50076,50077,50078,
  50079,50081
)

tutorialStopTiles:aid(
  50070,50071,50072,50073,50074,50080,50088,50089
)
```

Independent corroboration:

```text
victorperin/tibia-server@db4b430136521156d4b0e33549a83edb147a1786
igorkiel/PRIS-OPEN@3fc0c7c07b01f1668c0294d0862f081d1370f685
```

Those sources reproduce the same ID-to-behavior mapping. They are historical evidence only; they do not count as active Canary runtime handlers.

---

## 6. Placement inventory

| AID | Placements | Item IDs | z | Bounds | Historical role |
|---:|---:|---|---|---|---|
| 50058 | 8 | 4515, 7761 | 7 | `31984..31985,32273..32280` | opening tutorial / map mark to village |
| 50059 | 3 | 7764 | 7 | `32001,32277..32279` | sign and look/server-log hint |
| 50060 | 4 | 7764 | 7 | `32008,32276..32279` | map mark to Santiago |
| 50061 | 12 | 103,4515,4518,4524 | 7 | `32019,32268..32279` | stairs/ramp tutorial |
| 50062 | 3 | 4515 | 7 | `32024,32272..32274` | NPC/Santiago introduction |
| 50063 | 3 | 4394,4406,4409 | 6 | `32032,32272..32274` | tutorial window 22 |
| 50064 | 1 | 7769 | 5 | `32032,32277` | tutorial window 4 |
| 50065 | 1 | 7770 | 8 | `32038,32273` | dark cellar / torch chest hint |
| 50066 | 10 | 4515,4522,4524,7761 | 7 | `32057..32070,32273..32275` | return-firewood reminder |
| 50067 | 7 | 7770 | 8 | `32033..32039,32284` | sewer grate hint |
| 50068 | 1 | 7756 | 9 | `32035,32285` | cockroach combat tutorial |
| 50069 | 21 | 6475,6476,6478,6480,6481,6485,7756 | 9 | `32032..32037,32283..32287` | ladder tutorial and progression |
| 50070 | 3 | 7880 | 6 | `32025,32272..32274` | Santiago progression gate |
| 50071 | 4 | 4394,4397,4402 | 6 | `32045,32270..32273` | Santiago gate / temporary allow-pass |
| 50072 | 1 | 7881 | 6 | `32033,32277` | Santiago room gate |
| 50074 | 3 | 7887 | 7 | `32046,32270..32272` | paired direction/progression gate |
| 50075 | 14 | 4522,4525,4530,7761 | 7 | `32058..32072,32273..32278` | dead-tree branch hint |
| 50076 | 15 | 7761 | 7 | `32059..32067,32270..32274` | post-branch tutorial continuation |
| 50077 | 3 | 7764 | 7 | `32057..32059,32267` | Zirella door / shovel guidance |
| 50078 | 7 | 4515,7761 | 7 | `32065..32068,32261..32266` | shovel hint and shovel prerequisite gate |
| 50079 | 1 | 7762 | 8 | `32070,32266` | cave / rope chest hint |
| 50080 | 10 | 315,4515,4521,4522 | 7 | `32067,32260..32269` | Zirella progression/direction gate |
| 50081 | 16 | 4534,4537,7756 | 8 | `32066..32069,32263..32271` | rope-use hint |
| 50088 | 6 | 304,407,7761 | 7 | `32078,32266..32271` | exit gate until cave/shovel/rope lesson |

### Exact positions

```text
50058: (31984,32273,7) (31984,32274,7) (31984,32275,7) (31984,32276,7) (31985,32277,7) (31985,32278,7) (31985,32279,7) (31985,32280,7)
50059: (32001,32277,7) (32001,32278,7) (32001,32279,7)
50060: (32008,32276,7) (32008,32277,7) (32008,32278,7) (32008,32279,7)
50061: (32019,32268,7) (32019,32269,7) (32019,32270,7) (32019,32271,7) (32019,32272,7) (32019,32273,7) (32019,32274,7) (32019,32275,7) (32019,32276,7) (32019,32277,7) (32019,32278,7) (32019,32279,7)
50062: (32024,32272,7) (32024,32273,7) (32024,32274,7)
50063: (32032,32272,6) (32032,32273,6) (32032,32274,6)
50064: (32032,32277,5)
50065: (32038,32273,8)
50066: (32057,32273,7) (32058,32273,7) (32059,32273,7) (32060,32273,7) (32061,32273,7) (32062,32273,7) (32063,32273,7) (32064,32273,7) (32069,32275,7) (32070,32275,7)
50067: (32033,32284,8) (32034,32284,8) (32035,32284,8) (32036,32284,8) (32037,32284,8) (32038,32284,8) (32039,32284,8)
50068: (32035,32285,9)
50069: (32032,32283,9) (32032,32284,9) (32032,32285,9) (32032,32286,9) (32032,32287,9) (32033,32283,9) (32033,32284,9) (32033,32285,9) (32033,32286,9) (32033,32287,9) (32034,32283,9) (32034,32284,9) (32034,32285,9) (32034,32286,9) (32034,32287,9) (32035,32283,9) (32035,32284,9) (32035,32285,9) (32035,32286,9) (32036,32286,9)x2 (32037,32286,9)
50070: (32025,32272,6) (32025,32273,6) (32025,32274,6)
50071: (32045,32270,6) (32045,32271,6) (32045,32272,6) (32045,32273,6)
50072: (32033,32277,6)
50074: (32046,32270,7) (32046,32271,7) (32046,32272,7)
50075: (32058,32273,7) (32059,32273,7) (32060,32273,7) (32061,32273,7) (32062,32273,7) (32063,32273,7) (32064,32273,7) (32065,32273,7) (32066,32273,7) (32067,32273,7) (32068,32273,7) (32069,32276,7) (32070,32277,7) (32072,32278,7)
50076: (32059,32270,7) (32060,32270,7) (32061,32270,7) (32062,32270,7) (32063,32270,7) (32064,32270,7) (32065,32270,7) (32066,32270,7) (32067,32270,7) (32059,32271,7) (32060,32271,7) (32061,32271,7) (32062,32271,7) (32063,32272,7) (32064,32274,7)
50077: (32057,32267,7) (32058,32267,7) (32059,32267,7)
50078: (32065,32261,7) (32065,32262,7) (32065,32263,7) (32066,32264,7) (32067,32265,7) (32068,32265,7) (32068,32266,7)
50079: (32070,32266,8)
50080: (32067,32260,7) (32067,32261,7) (32067,32262,7) (32067,32263,7) (32067,32264,7) (32067,32265,7) (32067,32266,7) (32067,32267,7) (32067,32268,7) (32067,32269,7)
50081: (32066,32263,8) (32066,32264,8) (32066,32265,8) (32066,32266,8) (32066,32267,8) (32066,32268,8) (32066,32269,8) (32066,32270,8) (32066,32271,8) (32067,32263,8) (32067,32264,8) (32067,32265,8) (32068,32263,8) (32068,32264,8) (32069,32263,8) (32069,32264,8)
50088: (32078,32266,7) (32078,32267,7) (32078,32268,7) (32078,32269,7) (32078,32270,7) (32078,32271,7)
```

---

## 7. Intended behavior by family

### Tutorial hint tiles

The historical handler advanced `TutorialHintsStorage`, displayed tutorial windows/messages, emitted tutorial arrows/squares and added automap marks.

| AID | Intended effect |
|---:|---|
| 50058 | opening tutorial and `To the Village` map mark |
| 50059 | explain looking at signs and the server log |
| 50060 | add Santiago's hut map mark |
| 50061 | stairs/ramp tutorial |
| 50062 | introduce NPC interaction and Santiago |
| 50063 | tutorial window 22 |
| 50064 | tutorial window 4 |
| 50065 | point to the cellar torch chest |
| 50066 | remind the player to return firewood to Zirella |
| 50067 | point to the sewer grate |
| 50068 | explain attacking cockroaches |
| 50069 | explain using the ladder and enforce Santiago progress |
| 50075 | point to dead trees for a branch |
| 50076 | continue after obtaining the branch |
| 50077 | explain Zirella's door and shovel route |
| 50078 | explain the shovel and deny progress without the shovel reward |
| 50079 | explain the cave and rope chest |
| 50081 | explain using the rope |

### Stop/progression tiles

| AID | Intended effect |
|---:|---|
| 50070 | keep the player in Santiago's required route/state |
| 50071 | prompt return to Santiago and establish paired pass state |
| 50072 | deny Santiago room exploration before greeting/progress |
| 50074 | paired directional/progression gate after Santiago |
| 50080 | keep the player on Zirella's required route/state |
| 50088 | deny leaving toward Carlos before shovel/rope cave lesson |

---

## 8. Gameplay impact

### Confirmed lost guidance

Without the missing hint event:

- tutorial windows and explanatory text do not fire on the route;
- tutorial arrows and squares do not appear;
- automap marks for the village/Santiago route are not added by these tiles;
- `TutorialHintsStorage` does not progress through the intended stages;
- rope/shovel guidance that depends on those stages becomes inconsistent.

### Confirmed lost progression gates

Without the stop event:

- Santiago room/cellar/route restrictions are absent;
- the paired `50071`/`50074` direction gate is absent;
- Zirella route restrictions are absent;
- `50088` no longer prevents leaving before the cave/shovel/rope lesson.

These are behavioral defects, not cosmetic differences. A player can receive less guidance and bypass intended tutorial ordering.

---

## 9. Additional The Beginning dependencies requiring a separate audit

The AID decision does not prove that restoring only two MoveEvents completes the quest. The same review exposed related active-world gaps that must be verified in the follow-up gameplay PR:

- dead-tree branch acquisition action;
- using the branch on Zirella's cart;
- Zirella door UID `50085` behavior;
- tutorial cockroach kill/body hints;
- Santiago cellar ladder behavior;
- snake-head lever behavior;
- reward chest tutorial-window mapping, including current references to `50084/50086` versus verified map UIDs `50093/50094`;
- exact compatibility of historical storage numbers with current `41670..41677` storage keys.

Do not copy historical code unchanged. Port behavior to current Canary APIs, current storages and current quest conventions, then test it.

---

## 10. Fix specification for a separate gameplay PR

```text
problem:
  The Beginning tutorial retains 24 map AIDs but lacks the two MoveEvent
  implementations that consume them.

area/quest:
  The Beginning / Rookgaard Tutorial Island

source positions:
  all positions listed in section 6

destination positions:
  none; no map teleport destination patch is requested

floor:
  z=5..9

item IDs:
  existing marked floor/ground/route items listed in section 6

actionId:
  50058..50072 excluding absent 50073
  50074..50081
  50088

uniqueId:
  related existing objects 50080,50082,50085,50093,50094;
  do not modify them in the AID restoration without separate evidence

storage:
  Storage.Quest.U8_2.TheBeginningQuest.TutorialHintsStorage
  Storage.Quest.U8_2.TheBeginningQuest.SantiagoNpcGreetStorage
  Storage.Quest.U8_2.TheBeginningQuest.SantiagoQuestLog
  Storage.Quest.U8_2.TheBeginningQuest.ZirellaNpcGreetStorage
  Storage.Quest.U8_2.TheBeginningQuest.ZirellaQuestLog
  Storage.Quest.U8_2.TheBeginningQuest.CarlosNpcTradeStorage
  Storage.Quest.U8_2.TheBeginningQuest.CarlosNpcGreetStorage
  Storage.Quest.U8_2.TheBeginningQuest.CarlosQuestLog

related scripts/NPCs:
  data-otservbr-global/npc/santiago.lua
  data-otservbr-global/npc/zirella.lua
  data-otservbr-global/npc/carlos.lua
  data-otservbr-global/scripts/lib/register_actions.lua
  data-otservbr-global/lib/core/quests/catalog/018_the_beginning.lua

expected behavior:
  Restore tutorial hints, map marks, effects and storage progression;
  restore Santiago/Zirella/cave route gates without trapping advanced players.

evidence:
  verified map placements and SHA;
  active quest/NPC/storage/world correlation;
  canonical resolver absence;
  multiple independent historical implementations.

risk:
  medium; wrong storage thresholds can trap new or existing characters,
  spam tutorial messages, or block quest progression.

proposed test:
  focused Lua tests for every AID branch plus runtime E2E route in section 11.
```

### Files the follow-up may change

A separate PR may add a current-convention quest movement script and focused tests. It must not change the OTBM, parser, renderer or resolver implementation.

### Files the follow-up must not change

- binary map and map attributes;
- unrelated NPCs, quests or spawns;
- historical storage numeric values without migration evidence;
- OTBM tooling.

---

## 11. Runtime/E2E acceptance plan

Use a fresh test character with tutorial storages unset.

### Route and Santiago

1. Step through `50058..50062`.
2. Verify tutorial windows, text and automap marks appear once and `TutorialHintsStorage` advances monotonically.
3. Attempt `50071/50072` before required Santiago state; verify bounce/message.
4. Talk to Santiago and claim chest UID `50080`.
5. Equip the coat, obtain the weapon, enter the cellar and collect three cockroach legs.
6. Verify `50063..50069` guidance and Santiago state transitions.

### Zirella

7. Verify `50070/50074` enforce the intended direction/state.
8. Start Zirella's quest.
9. Create a branch from a dead tree and use it on the cart.
10. Verify Zirella state reaches reward stage.
11. Verify door UID `50085` denies early entry and opens after completion.
12. Claim shovel chest UID `50093`.
13. Verify `50075..50078` hints/gates and dig the loose stone pile.

### Rope cave and exit

14. Enter the cave and claim rope chest UID `50094`.
15. Verify `50079` and `50081` guidance.
16. Use the rope and verify the corresponding storage/hint state.
17. Attempt `50088` before stage 20; verify bounce/message.
18. Complete the cave lesson and verify `50088` allows passage.
19. Confirm the route to Carlos remains reachable and no player can become trapped.

### Regression assertions

- tutorial text/effects fire once per intended stage;
- repeated crossings do not spam messages;
- map marks are not duplicated indefinitely;
- existing characters with advanced storages are not trapped;
- GM bypass behavior, if retained, is explicit and tested;
- no unrelated AID resolution changes;
- normal resolver reports the restored values as runtime-handled after the fix;
- strict runtime count decreases by exactly the restored identifiers unless related fixes resolve more documented values.

---

## 12. Validation of this review

```text
map SHA-256: PASS
exact placement extraction: PASS
active Lua/XML/C++ search: PASS
active NPC/quest/storage correlation: PASS
independent historical corroboration: PASS
normal resolver with review dispositions: PASS
strict runtime: expected failure (handlers still absent)
```

Resolver result with this manual classification:

```text
legacy-unused: 1
missing-script: 24
needs-manual-review: 126
runtime-unresolved identifiers: 151
normal ok: true
strict runtime exit: 2
```

The unresolved runtime count intentionally remains unchanged. A manual `missing-script` decision records meaning; it does not invent a handler.

---

## 13. Final conclusion

The selected group is a confirmed missing gameplay implementation for **The Beginning** tutorial.

No OTBM patch is needed. The map already carries the required AIDs in the correct tutorial route. The next engineering step is a separate, tested Lua restoration and full quest dependency audit, followed by a fresh resolver run and runtime E2E test.
