# Bounty and Weekly Tasks Forum Evidence

## Status and purpose

This report aggregates the official `New Task System II` forum evidence into a bounded input for future Canary work on Bounty Tasks, Weekly Tasks, the Hunting Task Shop and Soulseals.

It complements, but does not modify or replace:

- `docs/ai-agent/OTS_BOUNTY_AND_WEEKLY_TASKS_REWORK.md`, which records custom product direction;
- `docs/agents/real-tibia/registry/modules/prey.yaml`, which identifies the current Canary module boundary.

This is evidence and requirements analysis, not proof that Canary or a maintained client already implements the described behavior.

## Evidence labels

- `OFFICIAL-RELEASED`: current official Tibia guide or released-update statement.
- `OFFICIAL-PREVIEW`: official pre-release announcement.
- `OFFICIAL-FORUM`: direct clarification by a Tibia Community Manager.
- `FORUM-TOPIC-INDEX`: topic named in the thread's official-reply index, without a captured reply body.
- `COMMUNITY-FEEDBACK`: player concern, question or preference; not an official rule.
- `DERIVED-REQUIREMENT`: implementation or test implication derived from the evidence.
- `UNKNOWN`: not established by the collected evidence.

## Collection boundary

`PROVEN`

- Source thread: `New Task System II`, thread `4989324`.
- The thread reports 172 results across 9 pages and is closed.
- The complete first displayed page was captured from the user's selected Chrome tab on 2026-07-23.
- The capture includes the official-reply topic index, five direct Community Manager clarifications and the first set of community replies.
- Official news items and the current official game guide were checked separately to reconcile preview behavior with the released system.

`LIMITATION`

The bodies of all posts on pages 2-9 were not captured. Cloudflare blocked direct HTTP collection, Chrome control became unavailable after the first-page capture, and public search indexing did not expose the missing replies reliably. Consequently:

- this report does not claim exhaustive per-post coverage;
- it does not assign frequency or sentiment percentages to the whole thread;
- topics listed only in the official-reply index remain topic evidence, not quoted clarification;
- no uncaptured reply is reconstructed from memory or inference.

## Primary source set

| Source | Date/status | Role | Proves | Does not prove |
|---|---|---|---|---|
| [Forum thread 4989324](https://www.tibia.com/forum/?action=thread&threadid=4989324) | opened 2025-11-03; closed | official clarifications and community feedback | statements captured on page 1; official-reply topic inventory | full contents of pages 2-9; Canary behavior |
| [New Task System I](https://www.tibia.com/news/?id=8566&subtopic=newsarchive) | 2025-10-31 preview | original Bounty preview | three offers, difficulty selection, Bounty rewards and original ring concept | final released balance |
| [New Task System II](https://www.tibia.com/news/?id=8567&subtopic=newsarchive) | 2025-11-03 preview | original Weekly preview | weekly task counts, reward timing, Soulseals, expansion conversion and shop direction | final post-test-server values |
| [Winter Update Changes during Test Server](https://www.tibia.com/news/?id=8598&subtopic=newsarchive) | 2025-11-18 final change summary | preview-to-release reconciliation | material Bounty/Weekly changes made during testing | packet, persistence or Canary implementation |
| [Winter Update 2025](https://www.tibia.com/news/?id=8570&subtopic=newsarchive) | released update | release existence and final feature summary | interconnected Bounty/Weekly system shipped | complete numeric rules |
| [Current combat game guide](https://www.tibia.com/gameguides/?section=combat&subtopic=manual) | observed 2026-07-23 | current official behavior baseline | released counts, multipliers, rewards, Talisman and Task Board rules | internal formulas, packet layout or server storage |
| [Current product game guide](https://www.tibia.com/gameguides/?section=products&subtopic=manual) | observed 2026-07-23 | current store-product baseline | Permanent Weekly Task Expansion grants 3 Kill and 3 Delivery tasks | historical migration implementation |

## Executive synthesis

The official system consists of two related but distinct loops:

1. Bounty Tasks are repeatable combat contracts. The character chooses one of three offers, earns experience, Reroll Tokens and Bounty Points, and permanently develops a character-bound Bounty Talisman.
2. Weekly Tasks are a weekly set of Kill and Delivery objectives. They grant experience plus weekly Hunting Task Points and Soulseals, use completion-count multipliers, feed the Hunting Task Shop and provide Soulpit access.

The forum evidence adds several compatibility and usability constraints:

- task generation is per character;
- legacy achievement progress is retained;
- the old Hunting Task system is expanded/reworked rather than simply deleting its achievements and rewards;
- difficulty is tied to Bestiary difficulty groupings;
- a Soulseal starts an eligible solo Soulpit fight without requiring the character to own or consume a Soul Core;
- Prey remains a separate system;
- players are concerned about stamina/Prey consumption, spawn contention, delivery-task economic effects, unclear Soulpit value and migration safety.

For Canary, the most important architectural implication is separation of state and settlement boundaries. Bounty progression, weekly-cycle generation, immediate task completion rewards, Monday settlement, legacy migration, shop currency and Soulpit authorization should not be collapsed into one ambiguous task counter.

## Official preview contract

### Weekly inventory and expansion

`OFFICIAL-PREVIEW`

- A normal weekly cycle offers 6 Kill Tasks and 6 Delivery Tasks.
- The Permanent Weekly Task Expansion adds 3 Kill Tasks and 3 Delivery Tasks, for 18 total.
- The expansion replaces the Permanent Hunting Task Slot store product.
- The Tibia Coin price was announced as unchanged.
- A character that already owned the Permanent Hunting Task Slot was announced to receive automatic conversion when the update went live.

### Completion and settlement

`OFFICIAL-PREVIEW`

- Experience is granted immediately when a task is completed.
- Hunting Task Points and Soulseals are settled after the Monday server save for characters that completed at least one task.
- The reward window presents the weekly result and lets the character choose the next cycle's difficulty.
- Choosing a new weekly difficulty replaces the current task set with tasks aligned to that difficulty for the next cycle.

### Soulseals and Soulpit

`OFFICIAL-PREVIEW`

- Every completed Weekly Task grants 1 Soulseal.
- Soulseals are represented as a Weekly Task currency.
- They start solo Soulpit battles against eligible Common Creatures.
- The preview stated a difficulty-dependent cost between 10 and 60 Soulseals.
- The selected creature must be a creature for which a Soul Core exists.

### Shop and collection rewards

`OFFICIAL-PREVIEW`

- Hunting Task Points are spent in the Hunting Task Shop.
- The preview announced an expanded shop with a new mount and a new outfit with add-ons.
- New titles and achievements were announced.

## Direct official forum clarifications

The following statements were captured directly in Community Manager post `#39550011`.

| Question | Official clarification | Evidence level | Implementation significance |
|---|---|---|---|
| Are weekly tasks the same for every player? | Tasks differ for every character. | `OFFICIAL-FORUM` | Generation and persistence are character-scoped, not account- or world-global. |
| Is existing `Taskmaster` progress reset? | Existing progress is maintained. | `OFFICIAL-FORUM` | Migration must preserve legacy counters used by achievements. |
| Is task difficulty related to Bestiary difficulty? | Yes, that is a valid way to describe it. | `OFFICIAL-FORUM` | Difficulty pools must use established creature-difficulty classification rather than an unrelated label. |
| Is the old Hunting Task system obsolete? | It is expanded, and the old achievements remain available. | `OFFICIAL-FORUM` | Existing rewards, achievements and visible progress require explicit compatibility treatment. |
| What does a Soulseal-funded Soulpit fight reward, and is a Soul Core required? | The reward is Soulpit experience; a Soul Core is not required. | `OFFICIAL-FORUM` | The player need not own or consume a Soul Core. Creature eligibility and inventory consumption must be modeled separately. |
| Did the test server open on 2025-11-03? | No. | `OFFICIAL-FORUM` | Historical only; no product requirement. |

### Soul Core wording reconciliation

The preview says the character selects a creature that possesses a Soul Core. The forum clarification says a Soul Core is not required.

`DERIVED-REQUIREMENT`

These statements are consistent if the system:

- restricts the selectable creature catalogue to creatures with a defined Soul Core/Soulpit representation;
- does not require the player's inventory to contain a Soul Core;
- spends Soulseals, not a Soul Core item, to start the solo fight.

An implementation must test catalogue eligibility and inventory consumption independently.

## Official-reply topic inventory

The thread's first post indexes later official replies by topic. The captured bodies are unavailable, so these entries are preserved only as discovery pointers.

### November 3 topic index

`FORUM-TOPIC-INDEX`

- test server timing;
- different tasks per character;
- legacy progress retention;
- Bestiary-linked difficulty;
- Soulseals;
- Soulseals and Animus Mastery;
- new outfit and mount;
- old progress and rewards remaining available;
- no changes to the Prey system;
- additional slot/expansion;
- Prey Wildcards remaining available;
- difficulty.

### November 4 topic index

`FORUM-TOPIC-INDEX`

- test server;
- reward multiplier;
- Soulseals;
- trophies;
- confirmation that answers were being read.

`UNKNOWN`

The exact wording and any numeric details in these uncaptured replies must be collected before they are used as an implementation contract.

## Current released official baseline

The current game guide observed on 2026-07-23 is stronger evidence for released behavior than the preview-era forum.

### Bounty Tasks

`OFFICIAL-RELEASED`

- The Task Board presents three Bounty offers.
- Completing a Bounty grants experience, Reroll Tokens and Bounty Points.
- Difficulty can be changed at any time, but the change affects the next selected task; an active task remains unchanged.
- Difficulty groups are:
  - Beginner: Easy creatures;
  - Adept: Easy and Medium creatures;
  - Expert: Medium and Hard creatures;
  - Master: Hard and Challenging creatures.
- The Preferred List influences which task types can appear.
- Available offers can be rerolled with Reroll Tokens.
- One Reroll Token can be claimed free each day, and a character can hold up to 10.
- Silver and Gold offers may appear and provide greater rewards.
- A Bounty Talisman costs 5,000 gold at a jeweller.
- Talisman upgrades are permanent and character-bound.
- Current upgrade families are damage, Life Leech, additional loot and a chance for double Bestiary progress.
- Talisman bonuses apply only while the item is equipped and the character fights creatures from the active Bounty.

### Weekly Tasks

`OFFICIAL-RELEASED`

- Each character receives 6 Kill Tasks and 6 Delivery Tasks per week.
- The Permanent Weekly Task Expansion adds 3 of each type.
- Completed weekly rewards are granted after the Monday server save.
- Base Hunting Task Point values are:
  - 25 points for a Kill Task;
  - 75 points for a Delivery Task.
- Completion-count multipliers are:
  - at least 4 tasks: 2x;
  - at least 8 tasks: 3x;
  - at least 12 tasks: 5x;
  - at least 16 tasks: 8x.
- Each completed Weekly Task grants 1 Soulseal.
- Hunting Task Points fund the Hunting Task Shop.
- The shop offers outfits, mounts, trophies, decorative items and promotion points.
- Soulseals fund solo Soulpit challenges.

### Test-server changes that supersede preview assumptions

`OFFICIAL-RELEASED`

The final test-server summary records these material changes:

- the Bounty defensive damage-reduction effect was replaced by Life Leech;
- the Bounty Talisman maximum effect was doubled and later upgrades became more expensive;
- Bounty and Weekly Tasks were disabled on Rookgaard;
- Weekly Hunting Task Point multipliers were increased;
- Weekly XP was increased and Weekly Kill Task XP received a per-task cap;
- up to 50 Wheel of Destiny Promotion Points were added to the Hunting Task Shop;
- Bounty Point and completed Weekly Task highscores were added.

`DERIVED-REQUIREMENT`

Future parity work must not implement the early preview literally where the released guide or final test-server summary supersedes it.

## Community feedback themes from the captured page

The table below aggregates only the first displayed page. Post IDs identify the captured evidence without implying that one post represents the whole community.

| Theme | Captured examples | Product risk | Derived requirement or test candidate |
|---|---|---|---|
| Legacy progression and achievements | `#39549994`, `#39550002`, `#39550005` ask about old achievements and `Taskmaster` progress. | A migration that resets counters destroys long-term progression. | Preserve old achievement availability and counters; test migration from partial progress. |
| Soulpit value and Soul Core semantics | `#39549991`, `#39549995`, `#39549999` question the reward, low-difficulty cores and Core requirement. | Unclear value or item-consumption rules make Soulseals feel pointless or misleading. | Show cost, eligibility and XP reward clearly; prove that no owned Soul Core is consumed. |
| Stamina and Prey consumption | `#39549997`, `#39550004` argue that task participation burns stamina and active Prey time. | The system can discourage participation or create hidden opportunity cost. | Decide and document stamina/Prey behavior explicitly; test it rather than inherit it accidentally. |
| Spawn contention | `#39550006` predicts short task-driven spawn invasions. | Random targets can increase congestion and social conflict. | Offer rerolls/preferences and avoid concentrating too many characters on the same scarce target. |
| Delivery-task economy | `#39550007`, `#39550009`, `#39550010` discuss gold-to-XP conversion, buying items and item-sink value. | Delivery tasks can become an unchecked XP purchase or distort item prices. | Configure eligible items, quantities and XP using sink/market telemetry; consume items atomically. |
| Per-character fairness | `#39550001` asks whether every character receives the same items. | Character-specific randomness can produce unequal cost or completion difficulty. | Persist generated offers per character and measure variance across equivalent characters. |
| Difficulty clarity | `#39550003` asks whether difficulty follows Bestiary categories. | Players cannot predict commitment if difficulty labels do not map to known classifications. | Expose a stable difficulty explanation and test pool membership. |
| Store expansion and participation | `#39549997` connects acceptance to buying extra tasks; the preview converts the old permanent slot. | Paid expansion can amplify a system players avoid for stamina or poor task quality. | Keep the expansion additive, migrate prior entitlement and avoid better per-task rewards for paid slots. |
| Collection rewards | `#39549993` asks how differently coloured mounts interact with achievements. | Ambiguous collection criteria cause irreversible purchase regret. | Define achievement unlock rules per variant before release. |
| Positive interest | `#39549993`, `#39549996` welcome the feature and want to test it. | Positive reception can be lost if reward clarity and migration are weak. | Preserve the accessible weekly-goal loop while addressing the above risks. |

## Requirements for a future Canary implementation

The following are implementation-analysis inputs, not authorization to modify runtime code.

### State separation

`DERIVED-REQUIREMENT`

Keep at least these concepts independently representable:

- active Bounty offer set;
- active Bounty contract and progress;
- Reroll Token balance and daily claim;
- Bounty Point balance and Talisman upgrades;
- weekly cycle identity and chosen difficulty;
- generated Weekly Kill and Delivery tasks;
- per-task completion and immediate XP state;
- pending/settled Monday Hunting Task Points;
- pending/settled Monday Soulseals;
- legacy Hunting Task progress and achievement counters;
- Permanent Weekly Task Expansion entitlement;
- Hunting Task Shop purchases;
- Soulpit authorization and Soulseal spend.

One generic `task_points` value or one completion flag is insufficient to express the official boundaries safely.

### Character scope

`DERIVED-REQUIREMENT`

- Offers, selected tasks, progress, rewards and permanent entitlements are character-scoped unless stronger evidence proves otherwise.
- Two characters on one account must not overwrite each other's generated Weekly Tasks.
- Generation should be persisted for the whole cycle so relogging does not reroll tasks.

### Weekly settlement

`DERIVED-REQUIREMENT`

- Monday settlement must be idempotent.
- A retry after crash or database reconnect must not duplicate Hunting Task Points or Soulseals.
- A completion immediately around server save must belong to exactly one cycle.
- Multiplier calculation should use the finalized completed-task count for that cycle.
- Immediate XP and deferred weekly currencies need separate claimed/settled markers if the preview timing is followed.

### Legacy migration

`DERIVED-REQUIREMENT`

- Preserve partial achievement counters and completed-achievement state.
- Preserve access to old achievements and still-supported rewards.
- Convert Permanent Hunting Task Slot entitlement exactly once.
- Do not turn the character's full Hunting Task Point balance into Wheel points; shop purchases and Wheel Promotion Points are a separate boundary.

### Delivery tasks

`DERIVED-REQUIREMENT`

- Validate the complete requested quantity before mutation.
- Remove items and mark completion atomically.
- A failed completion must leave inventory and task state unchanged.
- Item pools and amounts require economy review; the captured forum does not define them.
- Whether market-purchased items are acceptable must be an explicit rule, not an accidental consequence.

### Soulpit

`DERIVED-REQUIREMENT`

- Check creature eligibility separately from player inventory.
- Spend Soulseals atomically with fight creation.
- Do not consume a Soul Core item.
- Prevent concurrent requests from starting multiple fights for one spend.
- Surface required Soulseals and expected reward before confirmation.

### Bounty and Prey separation

`DERIVED-REQUIREMENT`

The official-reply index states that Prey is unchanged and Prey Wildcards remain available, while the released Bounty system uses Reroll Tokens. A future implementation should therefore avoid:

- silently spending Prey Wildcards for a Bounty reroll;
- treating Bounty offers as Prey slot state;
- changing active Prey because a Bounty is selected;
- conflating Permanent Prey Slot with Permanent Weekly Task Expansion.

## Acceptance-test candidates

These scenarios can seed later bounded runtime, persistence, protocol and physical-client tasks.

| ID | Scenario | Expected observable result | Required proof level |
|---|---|---|---|
| BWT-001 | Generate a weekly cycle for two characters on one account. | Each character keeps its own persisted tasks across relog. | persistence-proven |
| BWT-002 | Compare a normal character and a character with the permanent expansion. | The first receives 6 Kill + 6 Delivery tasks; the second receives 9 + 9. | behavior-proven |
| BWT-003 | Complete one Weekly Task before Monday settlement. | Completion is retained; immediate and deferred rewards follow the chosen official timing without duplication. | persistence-proven |
| BWT-004 | Run Monday settlement twice for the same cycle. | Hunting Task Points and Soulseals are credited exactly once. | behavior-proven |
| BWT-005 | Complete 3, 4, 8, 12 and 16 Weekly Tasks. | Hunting Task Point multipliers change only at 4/8/12/16 and equal 1x/2x/3x/5x/8x. | behavior-proven |
| BWT-006 | Change weekly difficulty while tasks are active. | Current tasks do not mutate unexpectedly; the intended next-cycle rule is applied. | gameplay-proven |
| BWT-007 | Load a character with partial legacy `Taskmaster` progress. | Counter and available legacy achievement path remain intact. | persistence-proven |
| BWT-008 | Migrate a character with a Permanent Hunting Task Slot. | The Weekly Task Expansion entitlement appears exactly once. | persistence-proven |
| BWT-009 | Attempt a Delivery completion with insufficient, exact and excessive quantities. | Only the exact-success path consumes the required amount and completes atomically. | behavior-proven |
| BWT-010 | Start an eligible Soulpit fight with enough Soulseals and no Soul Core item. | Fight starts, Soulseals are spent once and no Soul Core inventory item is required. | gameplay-proven |
| BWT-011 | Start an ineligible or unaffordable Soulpit fight. | No fight starts and no currency/item is lost. | behavior-proven |
| BWT-012 | Generate or select Bounty/Weekly tasks on Rookgaard. | Released restrictions are enforced. | gameplay-proven |
| BWT-013 | Claim daily Reroll Tokens at balances 9 and 10. | Balance reaches but never exceeds 10; a second daily claim is rejected safely. | behavior-proven |
| BWT-014 | Change Bounty difficulty with an active task. | Active task stays unchanged; the next selection uses the new difficulty. | behavior-proven |
| BWT-015 | Equip and unequip a character-bound Talisman while fighting active and non-active targets. | Bonuses apply only when equipped and only to the active Bounty target. | gameplay-proven |
| BWT-016 | Reroll Bounty offers while Prey is active. | Reroll Tokens are spent; Prey Wildcards, Prey target and Prey bonus are unchanged. | behavior-proven |
| BWT-017 | Buy Wheel Promotion Points in the Hunting Task Shop. | Only purchased Promotion Points affect the Wheel; remaining Hunting Task Points remain ordinary currency. | persistence-proven |

## Explicit unknowns and blockers for implementation

`UNKNOWN`

- Exact current Canary server coverage for released Bounty and Weekly behavior.
- Exact maintained-client packet layout, UI interpretation and capability gates.
- Exact official task-generation algorithms, offer probabilities and creature pools.
- Exact Bounty XP, Reroll Token, Bounty Point and Talisman upgrade formulas.
- Exact Weekly XP formula and per-task Kill XP cap.
- Exact Delivery item pools, quantities and economic selection rules.
- Exact Soulseal cost table after release; the 10-60 range is preview evidence.
- Exact legacy achievement counter/storage mappings in current Canary.
- Exact wording of official forum replies indexed on pages 2-9.
- Whether stamina and Prey consumption were intentionally changed after the captured feedback.
- Achievement rules for the three mount colour variants.

These unknowns block parity claims and numeric implementation, but they do not block preserving the evidence or creating narrow audit tasks.

## Recommended next bounded tasks

1. Audit current Canary Task Board, Prey, Soulseals, Hunting Task Shop, persistence and protocol paths against the released guide; produce a comparison matrix without changing gameplay.
2. Audit the maintained client for Task Board, Bounty, Weekly and Soulseals packet interpretation; create a cross-repository coordination record only if a server change is actually required.
3. Trace legacy Hunting Task achievements, counters and Permanent Hunting Task Slot entitlement before proposing migration.
4. Model Monday settlement and idempotency as a standalone persistence finding.
5. Model Delivery Task inventory/economy rules as a separate bounded design and abuse-analysis task.
6. Add physical-client scenarios only through the repository's shared universal E2E platform.

## Conclusion

The forum evidence is most valuable as a compatibility and risk register:

- keep character-specific generation;
- preserve old progress, achievements and entitlements;
- separate Bounty, Weekly, Prey, shop and Soulpit state;
- make weekly settlement idempotent;
- make Soul Core eligibility distinct from Soul Core inventory;
- treat stamina, congestion and Delivery economy as explicit design decisions;
- use the current official guide and final test-server changes, not the preview alone, for released behavior.

No runtime parity conclusion can be made until current Canary and maintained-client paths are audited at the required evidence levels.
