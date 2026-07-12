# The Beginning — quest dependency and runtime audit

## Decision

```text
component: World Semantic Review
quest: The Beginning
area: Rookgaard Tutorial Island
map SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
overall status: conflicting
confidence: high
runtime E2E proven: no
map change required: no
```

The current world contains the complete geographical route, all three NPCs, the quest catalogue, current storages, tutorial cockroach spawns, generic ladder/sewer/tool mechanics and the four principal reward chests. The quest is nevertheless **not complete as an intended Santiago → Zirella → Carlos → Rookgaard runtime chain**.

Static evidence confirms four blocking gaps:

1. no active use handler creates branch item `7772` from dead tree item `7753`;
2. no active use-with handler delivers that branch to Zirella's cart item `7751` and writes Zirella stage `7`;
3. Carlos' intended food sale has no persistent completion transition;
4. the current Rookgaard border tiles use unresolved `actionId 50999`, while no active handler writes terminal `CarlosQuestLog = 8`.

There are also confirmed bypasses and state conflicts: Zirella's UID `50085` door lacks its quest seal, Carlos' `outfit` keyword can skip the complete food/trade mission, Santiago's alternate `easy` branch persists the wrong resume state, and the shovel/rope chest tutorial mappings still point at old UIDs.

No OTBM patch is indicated. The map already contains the required objects, identifiers and route. Repairs belong in small Lua/NPC PRs with focused tests.

---

## 1. Baseline and sources

- Semantic AID classification: merged PR `#144`.
- Tutorial MoveEvent restoration: merged PR `#145`, commit `b1992c7380416139f4a0a2eb7ea0d593be47fdb2`.
- Verified map: `otservbr(3).otbm`.
- Verified map SHA-256: `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`.
- Active NPC scripts:
  - `data-otservbr-global/npc/santiago.lua`
  - `data-otservbr-global/npc/zirella.lua`
  - `data-otservbr-global/npc/carlos.lua`
- Active quest catalogue:
  - `data-otservbr-global/lib/core/quests/catalog/018_the_beginning.lua`
- Shared actions:
  - `data-otservbr-global/scripts/actions/other/others/quest_system1.lua`
  - `data-otservbr-global/scripts/lib/register_actions.lua`
  - `data/scripts/actions/items/ladder_up.lua`
- Companion world files:
  - `data-otservbr-global/world/otservbr-npc.xml`
  - `data-otservbr-global/world/otservbr-monster.xml`

Historical ORTS code was used only to corroborate intended relationships. All final classifications below also require evidence from the current map and active Canary files.

---

## 2. Current storage graph

| Storage | Numeric value | Intended range/use |
|---|---:|---|
| `TutorialHintsStorage` | 41670 | tutorial route hints and cave stages |
| `SantiagoNpcGreetStorage` | 41671 | Santiago dialogue state `1..13` |
| `SantiagoQuestLog` | 41672 | mission 1 state `1..11` |
| `ZirellaNpcGreetStorage` | 41673 | Zirella dialogue state `1..8` |
| `ZirellaQuestLog` | 41674 | mission 2 state `1..8` |
| `CarlosNpcTradeStorage` | 41675 | permission/state for food trade |
| `CarlosNpcGreetStorage` | 41676 | Carlos dialogue state `1..8` |
| `CarlosQuestLog` | 41677 | mission 3 state `1..8` |

The catalogue's final state requires `CarlosQuestLog = 8`, described as having passed the bridge to Rookgaard. No current active source writes that value.

---

## 3. Santiago chain

### Confirmed active

- Santiago spawns at `32034,32273,6`.
- Chest UID `50080` at `32032,32276,5` is an AID `2000` generic quest chest containing a bag and coat item `3562`.
- `quest_system1.lua` maps UID `50080` to tutorial `5` and writes `SantiagoNpcGreetStorage = 3`.
- Chest UID `50082` at `32033,32278,8` contains torch item `2920` and maps to tutorial `6`.
- Sewer grate item `435` at `32035,32285,8` and ladder item `1948` at `32038,32273,8` are both registered by the generic ladder action. The verified map does not contain historical UID `50083`.
- Six nearby cockroach spawn placements exist. Cockroach loot guarantees one item `7882` leg; Santiago removes three legs at dialogue state `6`.
- PR `#145` registers the relevant route AIDs.

### Missing but non-blocking tutorial behavior

No active creature/corpse event sends the historical first-kill, chase-control or corpse-looting hints. The player can still obtain the required legs, so this is `missing-script` but not a core progression blocker.

### Confirmed persistence conflict

The normal fish lesson path writes `SantiagoNpcGreetStorage = 12` before asking about Zirella. The alternate `easy` keyword branch advances the in-memory conversation to the same question but persists value `11`. A disconnect or focus loss can therefore resume the preceding fish stage.

A focused Santiago NPC fix should make both paths persist the same state and verify that the fish reward cannot repeat.

---

## 4. Zirella chain

### NPC state machine

Zirella is active at `32058,32268,7`. Her script advances both quest storages through stage `6`, then explicitly waits for an external interaction to set:

```text
ZirellaNpcGreetStorage = 7
ZirellaQuestLog = 7
```

Only after that does the NPC grant experience, advance both values to `8` and point at the reward room.

### Dead trees — confirmed blocking `missing-script`

The map contains dead tree item `7753`, including exact tutorial effect targets:

```text
32073,32276,7
32067,32281,7
32079,32285,7
32081,32276,7
32066,32288,7
```

The item's active description instructs the player to use it to break a branch. The expected branch is item `7772`. No active action handles item `7753`, creates item `7772`, applies an eligibility condition or advances tutorial state.

### Branch on cart — confirmed blocking `missing-script`

Zirella's cart item `7751` is at `32062,32271,7`; branch item `7772` is represented on the same map tile. The active NPC and catalogue require using a branch with this cart, but no active use-with action references either item or writes Zirella stage `7`.

This missing transition makes the intended Zirella mission statically impossible to finish.

### Door UID 50085 — confirmed gate bypass

The closed door item `6898` at `32058,32266,7` retains UID `50085`. Zirella promises access only after mission completion. No UID handler exists, so the generic door path has no quest-specific check against `ZirellaNpcGreetStorage >= 8`.

This does not block the player; it removes the intended gate and permits early access to the shovel room.

### Shovel reward — active with stale tutorial mapping

Chest UID `50093` at `32059,32265,7` has AID `2000` and contains shovel item `3457`. Generic reward acquisition is active and one-shot.

However, `quest_system1.lua` maps tutorial `10` to stale UID `50084`, not current UID `50093`. The shovel reward works but the expected tutorial window does not.

---

## 5. Cave and rope chain

### Confirmed active

- The shared shovel helper handles loose stone pile item `7749`, transforms it to hole `594`, persists `TutorialHintsStorage = 19` and reverts the opening after 30 seconds.
- PR `#145` advances the cave hint route to stages `20` and `21`.
- Chest UID `50094` at `32067,32264,8` contains rope item `3003` and is an active generic AID `2000` reward.
- Rope spot item `7762` at `32070,32266,8` is handled by the shared rope helper.

### Confirmed minor conflicts

- Tutorial `11` is mapped to stale UID `50086`, not current rope chest UID `50094`.
- The rope helper checks whether `TutorialHintsStorage < 22` before sending its success message but does not write stage `22`; the message can repeat on later uses.

Neither issue prevents the cave exit.

---

## 6. Snake-head lever

The current map retains:

- small snake head item `5058` at `32034,32272,8`;
- lever item `2772` at `32034,32274,8`.

Neither item has the historical unique ID and no active handler connects them. No current quest storage, reward or route transition depends on the visual interaction.

Decision: `legacy-unused`, non-blocking. Preserve the map objects and do not restore this cosmetic interaction without a separate gameplay requirement.

---

## 7. Carlos chain

Carlos is active at `32082,32263,7`. His intended state machine is outfit lesson → food task → hunt → trade → ready → bridge.

### Confirmed full-mission bypass

At the initial `storeTalkCid == 1` state, the `outfit` keyword branch sends the final completion dialogue and writes:

```text
CarlosQuestLog = 7
CarlosNpcGreetStorage = 8
```

This skips the complete food and trade chain. It conflicts directly with the quest catalogue and the normal `yes` path.

### Confirmed missing trade completion

The intended food path can reach:

```text
CarlosQuestLog = 6
CarlosNpcGreetStorage = 6
CarlosNpcTradeStorage = 1
```

The shop accepts meat item `3577` and ham item `3582`. However:

- `onSellItem` only prints a sale message;
- no current callback changes the persistent NPC state after a valid sale;
- no code sets `storeTalkCid` or `CarlosNpcGreetStorage` to stage `7` through the intended trade;
- the `ready` branch requires `storeTalkCid == 7`.

Therefore, without exploiting the `outfit` bypass, the intended Carlos completion dialogue is unreachable.

---

## 8. Rookgaard border and terminal quest state

The current map contains four wooden-floor tiles at:

```text
32073,32252,6
32074,32252,6
32075,32252,6
32076,32252,6
```

Each tile uses item `7886`, whose current description is:

```text
This is the border to the village of Rookgaard.
```

Each tile carries `actionId 50999`. The canonical review rules currently classify it as `needs-manual-review`, and no active runtime handler was found.

This is direct current-world evidence for the missing terminal transition:

- Carlos and the catalogue stop at `CarlosQuestLog = 7` before the bridge;
- catalogue stage `8` means the bridge has been crossed;
- historical AID `50089` is absent from the current map;
- current border AID `50999` has no handler and no alternate source writes stage `8`.

Decision: `actionId 50999` is `missing-script`, high confidence. Preserve it. A focused gameplay PR must first verify the current one-way rule and Rookgaard town assignment, then gate passage and write terminal quest state exactly once.

The nearby level bridge uses active AID `50998`; it is a separate level-two gate and does not complete The Beginning.

---

## 9. Advertised skip tutorial feature

Carlos and the completed quest text tell players to say `skip tutorial` to Santiago. Santiago has no matching keyword or callback.

Decision: `missing-script`, but implementation must wait for an explicit contract covering:

- destination and town;
- terminal quest storage values;
- rewards and experience forfeited;
- whether the option is account-, character- or previous-completion-gated;
- safe behavior for partially completed characters.

Do not infer this contract solely from historical code.

---

## 10. Classification matrix

| Dependency | Status | Gameplay effect |
|---|---|---|
| Santiago/Zirella/Carlos spawns | `confirmed` | all NPCs present |
| coat and torch chests | `confirmed` | rewards and current tutorials active |
| cellar sewer grate and ladder | `confirmed` | generic navigation handler active |
| cockroach spawns and legs | `confirmed` | Santiago turn-in obtainable |
| cockroach tutorial events | `missing-script` | guidance missing; progress still possible |
| dead-tree branch creation | `missing-script` | blocks intended Zirella progress |
| branch use on cart | `missing-script` | blocks Zirella stages 7/8 |
| Zirella UID50085 door gate | `missing-script` | permits early room access |
| shovel/rope rewards | `confirmed` | items awarded once |
| shovel/rope tutorial UID mapping | `conflicting` | tutorial windows 10/11 missing |
| shovel and rope tools | `confirmed` | cave navigation active |
| snake-head lever | `legacy-unused` | cosmetic; no quest dependency |
| restored AID50058..50088 events | `confirmed` | statically registered; E2E still required |
| Santiago `easy` persistence | `conflicting` | reconnect can resume wrong stage |
| Carlos `outfit` keyword | `conflicting` | skips food/trade mission |
| Carlos valid-sale completion | `missing-script` | intended path cannot finish |
| Rookgaard border AID50999 | `missing-script` | final quest state 8 unreachable |
| skip tutorial phrase | `missing-script` | advertised feature absent |

---

## 11. Required follow-up PR order

### PR A — Zirella branch and cart

Owned gameplay paths only. Implement:

- dead tree item `7753` → branch `7772` for eligible stage-6 players;
- branch `7772` used with cart `7751`;
- atomic writes of both Zirella stage-7 storages;
- exhaustion, retry, wrong-target and duplicate safeguards;
- focused tests.

### PR B — Zirella door and chest tutorials

Implement:

- UID `50085` storage gate;
- current UID `50093/50094` tutorial mappings after confirming tutorial IDs `10/11` against the current client;
- rope terminal hint persistence if stage `22` remains the intended state.

### PR C — Carlos state machine

Repair:

- `outfit` keyword bypass;
- valid food-sale completion;
- persistent transition to ready/final dialogue;
- negative tests for wrong items, repeat sales and reconnects.

### PR D — Rookgaard border AID50999

Implement only after verifying the current town and directional policy:

- deny or guide incomplete characters according to current design;
- allow completed stage-7 characters;
- write `CarlosQuestLog = 8` exactly once;
- assign town/citizenship only if confirmed;
- prevent trapping in both directions.

### PR E — optional tutorial polish

After the full route passes E2E:

- cockroach kill/body hints;
- formally specified skip-tutorial flow;
- optional cosmetic snake-head interaction only if explicitly desired.

---

## 12. Runtime acceptance

The machine-readable plan is in `THE_BEGINNING_RUNTIME_TEST_PLAN.json`. The quest is accepted only when a fresh non-GM character can complete all three missions and reach catalogue state `8` without using the Carlos bypass, while completed and partially completed characters remain untrapped and cannot duplicate rewards.

## Final conclusion

The world geometry and most reusable mechanics are already present. The primary failures are in Lua/NPC state transitions, not the binary map. The correct next work is a sequence of focused gameplay PRs, beginning with Zirella's branch/cart chain, followed by Carlos and the AID `50999` terminal border transition.
