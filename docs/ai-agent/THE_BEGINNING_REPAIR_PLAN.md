# The Beginning — ordered repair plan

## 1. Purpose and authority

This plan follows the evidence report in PR #204. It does not replace that report and does not authorize map edits. All identifiers, item IDs, storage IDs and positions below come from the audited current map and active Canary sources.

```text
map SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
confirmed quest conflicts: 0
OTBM changes planned: none
items.otb changes planned: none
client asset changes planned: none
```

The plan uses five evidence classes:

- `confirmed`: ready for a focused implementation PR once current `main` is rechecked;
- `map-only`: preserve the map object/identifier; implementation needs a proved gameplay contract;
- `script-only`: current text/code expects behavior absent from runtime; implementation still needs its missing contract;
- `unresolved`: no implementation until additional evidence resolves the uncertainty;
- `conflicting`: stop implementation until competing active handlers are reconciled.

## 2. Delivery order

| Order | Work package | Evidence state | Implementation state | Risk |
|---:|---|---|---|---|
| 1 | Carlos outfit/trade state machine | `confirmed` | implementation-ready | medium |
| 2 | Santiago `easy` persistence parity | `confirmed` | implementation-ready | low/medium |
| 3 | rope-success hint state 22 | `confirmed` | implementation-ready | low |
| 4 | AID `50999` terminal border | `map-only` plus terminal state `script-only` | contract-resolution first; code blocked | high |
| 5 | cockroach kill/chase/corpse hints | `map-only` | exact tutorial contract first | low/medium |
| 6 | advertised `skip tutorial` | `script-only`; implementation `unresolved` | blocked | high |
| 7 | snake-head lever, static cart branch, extra dead trees, `0,0,0` teleports | `map-only` / `unresolved` | preserve; separate audits only | unknown |

The first three packages may be developed independently in separate PRs because they do not require an OTBM change and touch different active files. Package 4 must follow Carlos because the border's minimum legal state depends on the repaired Carlos state machine.

## 3. Package 1 — Carlos outfit and trade flow

### Problem

Current `data-otservbr-global/npc/carlos.lua` has three confirmed defects:

1. the `outfit` keyword at the initial state jumps to `CarlosQuestLog = 7` and `CarlosNpcGreetStorage = 8`;
2. `onTradeRequest` is defined but not registered as `CALLBACK_ON_TRADE_REQUEST`;
3. selling meat `3577` or ham `3582` does not persist the intended transition from stage `6` to stage `7`.

### Exact intended contract

- `outfit` at conversation state 1 must reuse the existing normal outfit lesson: set greet/log to 2, send tutorial 12, end interaction;
- Carlos' shop still sells no items and buys only meat `3577` or ham `3582` for two gold;
- trade opening is allowed only when `CarlosNpcGreetStorage == 6`, `CarlosQuestLog == 6` and the existing trade permission is active;
- opening the shop sends tutorial 13 once but does not complete the mission;
- progression to stage 7 occurs only after the shop runtime confirms at least one accepted meat/ham item was actually sold;
- the existing shop transaction remains responsible for item removal and payment;
- after a successful sale, both greet/log become 7, the tutorial trade permission closes, and `ready` remains the final dialogue step to greet 8;
- no teleport, town assignment or final log-8 write belongs in the Carlos NPC PR.

### Planned files

- `data-otservbr-global/npc/carlos.lua`;
- a new focused test under `tools/ai-agent/test_the_beginning_carlos_flow.py`;
- task record/changelog only as required.

### Reuse and stale PR policy

PR #157 contains candidate implementation and tests but is based on an obsolete `main` and must not be merged or rewritten in place. Create a fresh branch from current `main`, reapply only behavior that still matches the report, inspect the final diff, and run current checks. Close #157 as superseded only after the replacement PR exists and its changed-file list is verified.

### Tests required before merge

1. initial `outfit` cannot write stage 7 or greet 8;
2. normal `yes` and `outfit` paths call the same outfit transition;
3. trade request outside exact stage 6 returns false;
4. first valid trade request sends tutorial 13 and records an opened state without writing stage 7;
5. repeated shop opening does not repeat tutorial 13;
6. failed sale and unrelated item sale cannot advance the quest;
7. successful sale of meat `3577` advances exactly once;
8. successful sale of ham `3582` advances exactly once;
9. amount zero cannot advance;
10. no manual `removeItem`, `addMoney` or duplicate shop economy code is introduced;
11. `ready` remains stage-7-only and writes greet 8 without writing terminal log 8;
12. Lua format/tests, AI Agent Tools and global datapack runtime smoke pass on the final head.

### Regression risk

Medium. NPC shops are asynchronous UI/runtime flows; the callback must be proved to run only after a successful transaction and must not let ordinary Carlos trading affect characters outside the tutorial stage.

## 4. Package 2 — Santiago `easy` persistence parity

### Problem

The normal response after the fish lesson writes:

```text
SantiagoNpcGreetStorage = 12
SantiagoQuestLog = 10
```

The alternative `easy` keyword advances to the same in-memory question but writes greet storage 11. Relogging or losing focus can therefore resume the previous fish stage.

### Exact intended contract

- both paths that arrive at the Zirella question persist greet 12 and log 10;
- neither path grants another fish;
- the final Zirella response continues to greet 13/log 11 and retains the existing map mark;
- no dialogue text, reward amount, item ID, map or other NPC behavior changes.

### Planned files

- `data-otservbr-global/npc/santiago.lua`;
- focused contract test.

### Tests required before merge

1. normal continuation writes greet 12/log 10;
2. `easy` writes the same values;
3. `easy` does not call `addItem(3578, 1)`;
4. reconnect simulation from persisted greet 12 selects the Zirella question;
5. fish reward remains only in the preceding transition;
6. no change to coat `3562`, weapon `3270`, legs `7882`, XP or map mark;
7. Lua tests/format and global datapack runtime smoke pass.

### Regression risk

Low/medium. It is a one-value correction, but reconnect/focus-loss behavior and duplicate reward prevention must be covered.

## 5. Package 3 — rope-success hint state 22

### Problem

The shared rope helper sends the tutorial-success text while `TutorialHintsStorage < 22` but does not write state 22, allowing the message to repeat after the player remains at state 21.

### Exact intended contract

- only the existing Tutorial Island rope-success branch writes hint state 22;
- the success message appears once after the stage-21 rope lesson;
- generic rope behavior outside this quest remains unchanged;
- item `3003`, rope spot `7762`, AID `50079`, positions and teleport behavior do not change.

### Planned files

- `data-otservbr-global/scripts/lib/register_actions.lua`;
- focused contract test.

### Tests required before merge

1. the Tutorial Island success branch requires the same existing preconditions;
2. it writes `TutorialHintsStorage = 22` immediately after successful use;
3. subsequent successful uses do not repeat the message;
4. no global rope item/spot registration changes;
5. no destination coordinate changes;
6. Lua tests/format and global datapack runtime smoke pass.

### Regression risk

Low, provided the write is bounded to the existing quest-specific branch.

## 6. Package 4 — AID `50999` terminal border contract

### Current evidence

- four item `7886` placements carry AID `50999` at `32073..32076,32252,6`;
- their description identifies the border to Rookgaard;
- no active handler resolves AID `50999`;
- `CarlosQuestLog = 7` means the player should cross the bridge;
- `CarlosQuestLog = 8` means the bridge was crossed;
- current OTBM town table assigns Rookgaard ID **3**, temple `32097,32219,7`;
- historical AID `50089` is absent and historical `Town(6)` is invalid for this map.

This proves the missing terminal transition but does **not** prove all movement semantics. Implementation is blocked until the following contract is resolved.

### Contract-resolution task

Use only existing OTBM tools and a disposable live world to determine:

1. tutorial-island side and Rookgaard side of each of the four tiles;
2. exact intended crossing direction;
3. whether the stepping player should remain on the trigger tile, move one tile north, or be placed at another verified position;
4. whether the reverse direction is blocked after completion;
5. canonical rejection text before Carlos stage 7;
6. whether town ID 3 must be assigned on crossing or whether current character creation already assigns it;
7. whether tutorial 14 is emitted on entry, after movement or after storage write;
8. idempotent behavior for log 8 characters;
9. whether party summons, monsters or non-player creatures are ignored normally;
10. destination walkability, floor presence and protection-zone semantics.

Required evidence:

- bounded factual renders north and south of the border;
- item/mechanic export for at least `32068,32247,6`–`32081,32258,6`;
- resolver report before and after candidate implementation;
- live step-in traces from both directions at Carlos logs 6, 7 and 8;
- current town before and after crossing.

### Candidate implementation shape after contract approval

- one `MoveEvent()` of type `stepin` registered only for AID `50999`;
- no OTBM edit;
- non-player creatures return true without state changes;
- exact Carlos stage gate;
- one terminal log-8 write;
- only current Rookgaard town ID 3 if runtime evidence requires reassignment;
- exact verified direction/destination, never historical coordinates by default.

### Tests required before merge

- resolver handles all four placements with zero conflicts;
- each exact placement exercises the same handler;
- stage-below-7 denial;
- legal one-way crossing at stage 7;
- exact destination walkability assertion using audited coordinates;
- log-8 idempotence;
- reverse-side behavior;
- town ID 3 behavior if enabled;
- tutorial 14 once;
- no effect on nearby AID `50998` level bridge;
- global datapack smoke and live-world E2E.

### Regression risk

High. A wrong direction, offset or town assignment can trap players, bypass content or corrupt their home-town state. No code PR should open before the contract-resolution record is complete.

## 7. Package 5 — cockroach tutorial events

### Current evidence

The cellar, six cockroaches, guaranteed leg loot and Santiago turn-in are confirmed. Historical first-kill/chase and corpse-looting hints have no active current handlers.

### Missing contract

Before implementation, determine:

- exact tutorial IDs and order for first kill, chase control and corpse opening in the current client;
- whether the kill event is per character, per corpse or per mission state;
- owner/party rules for corpse hints;
- storage ownership and values without allocating guessed global storage IDs;
- whether current tutorial hint storage can encode the events safely or whether existing reserved fields are available.

### Planned response

No implementation yet. Create a separate evidence task only if these hints are desired. Progression does not depend on them.

### Regression risk

Low/medium. Incorrect creature-event registration can affect every cockroach or duplicate client tutorials globally.

## 8. Package 6 — `skip tutorial`

### Current evidence

Carlos' completion dialogue and quest-log state 8 advertise saying `skip tutorial` to Santiago. Santiago has no active keyword/callback.

### Blocking questions

- Is eligibility character-based, account-based or based on another completed character?
- Can a partially progressed character skip safely?
- What exact destination and town are used?
- Which Santiago, Zirella, Carlos and hint storages become terminal?
- Are chest storages marked claimed or left available?
- Which item and XP rewards are forfeited?
- Is the option available only before the first Santiago stage?
- How does the current client expose/confirm the action?

Historical implementations are insufficient because current account-wide quest infrastructure and current map/town IDs differ.

### Planned response

Keep `script-only`/`unresolved`. Do not code, teleport or allocate storage until the full current contract is approved and tested. A safe alternative may be to correct the misleading text, but that is also a user-facing gameplay decision and requires explicit approval.

### Regression risk

High. This feature can bypass rewards, corrupt quest state or teleport characters irreversibly.

## 9. Preserved findings — no repair in this programme

### Snake-head lever

Map objects `5058` and `2772` exist without an active identifier or quest dependency. Preserve as `map-only`; no cosmetic handler unless separately requested.

### Static branch on Zirella's cart

Item `7772` exists on the cart tile, but its intended static behavior is unresolved. Do not remove, make movable/immovable or repurpose it.

### Extra dead trees

Three map trees `7753` lie outside the exact quest whitelist. Preserve; their existence is not proof that all dead trees should generate branches.

### Two `0,0,0` teleport attributes

Items `1758` at `32032,32285,7` and `32032,32286,7` carry teleport destinations `0,0,0`. Their quest role is unresolved. Treat as a separate map-mechanic audit; never repair them incidentally.

## 10. Branch, PR and merge discipline

Each implementation-ready package must:

1. start from then-current `main`;
2. declare exact owned paths in a task record;
3. inspect open PRs for overlap;
4. open as draft before implementation grows;
5. contain one logical behavior change;
6. avoid shared-document churn when not necessary;
7. review the complete changed-file list and diff;
8. prove no `.otbm`, `items.otb` or asset changes;
9. pass focused tests, relevant Lua/AI-agent checks and global datapack smoke on the final head;
10. remain unmerged until the user approves merge under the project-specific boundary.

Merge order after approval:

```text
Carlos repair
  -> Santiago persistence repair (independent, may validate in parallel)
  -> rope hint repair (independent, may validate in parallel)
  -> AID 50999 contract-resolution report
  -> AID 50999 implementation only after contract approval
  -> optional non-blocking tutorial event work
  -> skip tutorial only after a complete approved contract
```

## 11. Definition of complete

The core intended runtime chain is complete only when:

- Santiago can finish without resume-state divergence;
- Zirella wood/cart, reward door, shovel and rope route remain functional;
- Carlos can reach stage 7 through a real successful sale without a bypass;
- the four AID `50999` tiles enforce the approved border rule and write terminal log 8 exactly once;
- the final resolver reports no unresolved The Beginning progression identifier and no conflicts;
- a live character completes Santiago → Zirella → cave → Carlos → Rookgaard from clean storages;
- reconnect tests at every NPC boundary preserve the correct state;
- no map binary or client asset was modified.

Non-blocking tutorial hints and `skip tutorial` are complete only under their own approved contracts; they must not delay truthful reporting of the core chain's state.
