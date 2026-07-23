# Bounty Tasks Forum Evidence

## Purpose

This report turns Tibia forum thread
[`4989234` ("New Task System I")](https://www.tibia.com/forum/?action=thread&threadid=4989234)
into bounded product and implementation input for Canary.

It complements, but does not replace,
[`OTS_BOUNTY_AND_WEEKLY_TASKS_REWORK.md`](OTS_BOUNTY_AND_WEEKLY_TASKS_REWORK.md).
That document owns the broader custom design direction. This report owns source
provenance, official-versus-community separation, and a concrete question and
acceptance-criteria backlog derived from the forum discussion.

This is a research artifact. It does not prove that Canary currently implements
any behavior described below.

## Evidence labels

- `OFFICIAL-CURRENT`: current official Tibia game guide or release material.
- `OFFICIAL-TEASER`: the October 31, 2025 official feature announcement.
- `OFFICIAL-FORUM-INDEX`: the consolidated official-reply topic index in the
  thread opener.
- `COMMUNITY-SAMPLE`: paraphrased community feedback from the first forum page.
- `DERIVED`: a product or engineering conclusion inferred from cited evidence.
- `OPEN`: not resolved by the reviewed sources.

## Source coverage and limitations

### Reviewed sources

| Source | Coverage | Role |
|---|---|---|
| [Forum thread 4989234](https://www.tibia.com/forum/?action=thread&threadid=4989234) | Thread metadata, two official opener posts, 18 first-page community posts, and the opener's consolidated official-reply index | Primary community and staff-discussion evidence |
| [New Task System I](https://www.tibia.com/news/?id=8566&subtopic=newsarchive) | Original October 31, 2025 Bounty teaser | Historical announced design |
| [Combat game guide, Task Board](https://www.tibia.com/gameguides/?section=combat&subtopic=manual) | Current Bounty and Weekly Task rules | Current official baseline |
| [Winter Update 2025](https://www.tibia.com/news/?id=8570&subtopic=newsarchive) | Released-system overview | Confirms final naming and the combined Task System |

### Coverage boundary

`PROVEN`

- The forum reports 203 entries across 11 pages and is closed.
- Page 1 contains 20 entries: two official posts and 18 community posts.
- The opener contains a consolidated index of official reply topics from the
  thread.

`OPEN`

- This report does not claim an exhaustive per-post sentiment count across all
  203 entries.
- Later-page community posts were not copied or inferred when the public forum
  blocked reliable automated pagination.
- The official-reply index uses terse labels. Where a label lacks enough
  context, this report preserves the ambiguity instead of inventing a rule.

The coverage is sufficient to establish the announced mechanics, the current
official baseline, the first wave of recurring player questions, and the
official clarifications highlighted by CipSoft. It is not sufficient for a
statistically representative sentiment study.

# 1. Official baseline

## 1.1 Original teaser

`OFFICIAL-TEASER`

The October 31, 2025 teaser announced:

- a Task Board with three randomly generated creature tasks;
- four selectable difficulty levels: Beginner, Adept, Expert, and Master;
- completion rewards consisting of experience, Reroll Tokens, and Bounty
  Points;
- permanent, character-bound upgrades to a "Bounty Ring";
- target-scoped damage, damage-reduction, loot, and Bestiary bonuses;
- preferred and avoided creatures influencing offer generation;
- uncommon Silver and Gold tasks with larger rewards;
- an endless task loop rather than a finite one-time list.

## 1.2 Current released system

`OFFICIAL-CURRENT`

The current game guide documents:

- exactly three Bounty offers;
- four difficulty groups;
- a difficulty change that applies to the next selection, not the active task;
- a Preferred List that influences future task rolls;
- rerolling the current task selection with Reroll Tokens;
- one free token claim per day and a character cap of 10 tokens;
- standard, Silver, and Gold task grades;
- a Bounty Talisman purchasable from jewellers for 5,000 gold;
- Bounty Point upgrades for damage, life leech, loot, and double Bestiary
  progress;
- bonuses active only while the Talisman is equipped and only against active
  Bounty targets;
- permanent, character-bound Talisman upgrades.

## 1.3 Teaser-to-release deltas

`OFFICIAL-CURRENT`

| Surface | Teaser | Current guide | Engineering consequence |
|---|---|---|---|
| Item name | Bounty Ring | Bounty Talisman | Use current naming in new code, storage, protocol, UI, tests, and docs. |
| Defensive/sustain bonus | Reduced incoming damage | Life leech | Do not implement the teaser's damage-reduction wording as current parity. |
| Bestiary bonus | Accelerated progress | Chance for double progress | Model the current effect as a chance-based event, subject to source audit. |
| Item acquisition | Not specified | Jeweller purchase for 5,000 gold | Acquisition and item state need an explicit server path. |
| Reroll token limits | Not specified | One daily claim, maximum 10 held | Persistence and overflow behavior need tests. |
| Difficulty change | Difficulty selectable | Change applies to next task selection | Active tasks must remain immutable when difficulty preference changes. |

`DERIVED`: current official documentation overrides teaser-era terminology and
effect descriptions for a parity implementation. The teaser remains valuable
for understanding the design intent and forum questions.

# 2. Official forum clarifications

The opener's official-reply index highlights the following clarifications.
Duplicates in the index are consolidated here.

| Clarification | Evidence | Implementation reading |
|---|---|---|
| Bounty offers do not require buying an extra offer slot. | `OFFICIAL-FORUM-INDEX`, supported by the current guide's three offers | The base Bounty offer set is three. Do not reuse Prey-slot monetisation. |
| Talisman effects apply only to the chosen/current task creatures. | `OFFICIAL-FORUM-INDEX`, `OFFICIAL-CURRENT` | Every effect needs an active-task target check. |
| There is no task cooldown. | `OFFICIAL-FORUM-INDEX` | Completion can lead directly to the next offer/selection cycle. |
| The item must be equipped. | `OFFICIAL-FORUM-INDEX`, `OFFICIAL-CURRENT` | Stored progression alone must not grant passive bonuses. |
| Existing Hunting Task Points are retained. | `OFFICIAL-FORUM-INDEX` | Migration must preserve the legacy currency; verify current Canary state before changing it. |
| A reroll replaces all three displayed offers. | `OFFICIAL-FORUM-INDEX` | Reroll is atomic at offer-set level, not a per-card reroll. |
| Upgrade progression is character-bound. | `OFFICIAL-FORUM-INDEX`, `OFFICIAL-CURRENT` | Persist progression on the character, independent of a particular physical Talisman instance. |
| A paid third-slot topic was answered separately. | `OFFICIAL-FORUM-INDEX` | The terse index is ambiguous; current documentation resolves paid expansion as Weekly Tasks, not a paid third Bounty offer. |
| Fine-tuning and a "drunk effect" were discussed. | `OFFICIAL-FORUM-INDEX` | Preserve as unresolved historical discussion; do not derive a mechanic without the direct reply context. |

# 3. First-page community aggregation

## 3.1 Sample profile

`COMMUNITY-SAMPLE`

The first page contains 18 community posts:

- nine use explicitly positive or excited language;
- most positive posts still ask for rules, migration, equipment, or abuse
  clarification;
- one post directly criticises the lack of an obvious gold sink;
- the remaining posts are predominantly neutral questions rather than
  rejection.

This indicates high initial interest but low confidence about system boundaries.
It does not establish whole-thread sentiment.

## 3.2 Recurring themes

| Theme | Representative post IDs | Aggregated concern | Product/engineering response |
|---|---|---|---|
| Offer-slot monetisation | `39549454`, `39549463`, `39549468` | Are all three offers free, and what exactly is sold for Tibia Coins? | Keep Bounty's three offers separate from the Weekly Task Expansion and describe Store surfaces explicitly. |
| Talisman scope | `39549456`, `39549463`, `39549464` | Do bonuses apply to the active creature only, and do upgrades persist between tasks? | Target-scope every effect; persist upgrade levels across task changes. |
| Equipment conflict | `39549461`, `39549467`, `39549473` | Must the item occupy an equipment slot, and does that displace normal hunt equipment? | Current parity requires equipped state. Custom dedicated-slot work must be classified as an extension. |
| Upgrade limits | `39549460` | Are upgrade levels capped? | Treat exact levels, costs, caps, and formulas as source-audit inputs, not forum-derived values. |
| Party kill credit | `39549461` | Does party participation, any damage, or highest damage grant progress? | Define an explicit credit policy with summon, party, range, and anti-leech tests. |
| Completion cadence | `39549461` | Is another task immediately available or gated by a daily timer? | Official forum index says no cooldown; selection flow should continue immediately. |
| Legacy-system migration | `39549465`, `39549472`, `39549473` | Does the new system replace old Prey Hunting Tasks, and what happens to saved points? | Preserve Hunting Task Points and document which old UI/state is retired, migrated, or retained. |
| Gold sinks | `39549456`, `39549458` | Should rerolls or resets consume gold? | Current parity uses Reroll Tokens and a 5,000-gold Talisman purchase. Additional gold sinks are custom balance decisions. |
| Stamina and alternate progress | `39549471` | Can players progress tasks without consuming stamina or gaining ordinary XP/loot? | Keep stamina interaction `OPEN` until current runtime behavior is observed or tested. |
| Power and exploitation | `39549456`, `39549463`, `39549464`, `39549471` | Can permanent progression be exploited for unrestricted hunting power? | Require active task, matching target, and equipped Talisman checks; test task transitions and stale-state cleanup. |

Post IDs are recorded for traceability. Community text is paraphrased rather
than copied wholesale.

# 4. Product requirements derived from the evidence

## 4.1 Must-match parity requirements

`DERIVED` from current official material and forum clarifications:

1. The Task Board exposes three Bounty offers.
2. A character has one active Bounty Task at a time.
3. Offers are generated within the selected difficulty and affected by
   preferred/avoided configuration.
4. Changing difficulty does not mutate the active task.
5. Reroll replaces the full three-offer set atomically.
6. Task completion has no cooldown before another selection cycle.
7. Standard, Silver, and Gold grades are data-driven and produce distinct
   reward values.
8. Completion can grant experience, Reroll Tokens, and Bounty Points.
9. Daily free-token claims and the 10-token inventory cap are character state.
10. Talisman upgrade progression is permanent and character-bound.
11. Talisman bonuses require equipped state.
12. Talisman bonuses require the damaged, damaging, looted, or Bestiary-counted
    creature to be an active Bounty target.
13. The current effect families are damage, life leech, loot, and chance for
    double Bestiary progress.
14. Existing Hunting Task Points survive migration.
15. The paid Weekly Task Expansion must not be implemented as a paid Bounty
    offer slot.

## 4.2 Custom-extension candidates

`DERIVED`

The following first-page ideas may be useful, but are not current parity
requirements:

- gold-paid rerolls or reset sinks beyond the documented Talisman purchase;
- a dedicated Bounty equipment slot;
- stamina-free task-only progress;
- additional post-Bestiary conversion rewards;
- alternate task targeting or progression-control unlocks;
- dynamic spawn allowances for active Bounties.

These belong in the existing custom design document and must keep explicit
`TIBIA-EXTENSION` classification.

# 5. Open behavior questions

The reviewed official sources do not fully specify these server contracts.

| ID | Question | Why it matters | Minimum proof needed |
|---|---|---|---|
| `BNT-OPEN-001` | What grants kill credit in a party? | Prevents leeching and inconsistent shared progress. | Current Canary audit plus official runtime observation. |
| `BNT-OPEN-002` | How do summons, environmental damage, and last-hit ownership count? | Affects every vocation and automation edge case. | Deterministic runtime scenarios. |
| `BNT-OPEN-003` | What happens when a completion reward would exceed 10 Reroll Tokens? | Defines loss, clamping, or deferred reward behavior. | Official-client observation or current server trace. |
| `BNT-OPEN-004` | What are the exact task pools, kill counts, grade probabilities, and rewards? | Core balance and offer generation cannot be guessed. | Version-pinned authoritative data/runtime evidence. |
| `BNT-OPEN-005` | What are the exact Talisman levels, caps, costs, and formulas? | Prevents forum speculation from becoming permanent balance. | Current official data/runtime evidence. |
| `BNT-OPEN-006` | How are creature variants, summons, bosses, and shared race families matched? | Incorrect matching can enable exploits or block valid progress. | Exact identity tables plus regression tests. |
| `BNT-OPEN-007` | How do stamina, zero-XP state, and reward boosts interact? | Determines whether progress is possible when ordinary XP is disabled. | Official runtime scenario. |
| `BNT-OPEN-008` | What happens to active offers/tasks on logout, death, character trade, or migration? | Persistence and rollback must be deterministic. | Load/save trace, migration test, and relog/death scenarios. |
| `BNT-OPEN-009` | What exactly did the indexed "drunk effect" clarification address? | The index label alone is insufficient evidence. | Direct official reply context. |

# 6. Suggested implementation backlog

This backlog is ordered to avoid encoding unknown balance values too early.

## `BNT-001` Current-state audit

- inventory Canary Prey/Hunting Task definitions, registrations, persistence,
  protocol, data modules, and tests;
- map current behavior to the 15 must-match requirements;
- classify every missing behavior as parity, extension, or unresolved.

## `BNT-002` Versioned definitions

- define task pools, difficulty membership, kill counts, grade weights, and
  rewards in a reviewable data contract;
- reject unknown creature identifiers and duplicate task definitions;
- keep grade selection deterministic under a seeded test source.

## `BNT-003` Offer-set lifecycle

- generate exactly three offers;
- apply preference and avoidance weights;
- select one task;
- atomically reroll all three;
- continue without a completion cooldown;
- preserve the active task when difficulty preference changes.

## `BNT-004` Kill-credit contract

- resolve `BNT-OPEN-001`, `002`, and `006`;
- cover solo, party, summon, range, damage ownership, logout, death, and stale
  task cases;
- add anti-leech and duplicate-credit tests.

## `BNT-005` Rewards and currency

- grant XP, Bounty Points, and Reroll Tokens transactionally;
- implement daily claim and the 10-token cap;
- preserve Hunting Task Points;
- cover overflow, retry, rollback, and duplicate-completion cases.

## `BNT-006` Talisman progression

- purchase for 5,000 gold through the authoritative NPC/item path;
- store character-bound upgrade state;
- require equipped state and matching active target;
- implement only current effect families with evidence-backed values;
- clear or reject stale task-target state.

## `BNT-007` Protocol and maintained-client contract

- audit Task Board, Kill Tracker, task selection, reroll, progression, and
  Talisman payloads against maintained OTClient;
- create a cross-repository coordination task if server payload changes are
  required;
- use byte-exact tests and capability/version handling.

## `BNT-008` Runtime and physical-client proof

- complete and immediately replace a task;
- reroll and verify all three offers changed as one set;
- change difficulty while preserving the active task;
- verify bonuses off when unequipped or fighting a non-target;
- verify each current effect against a target;
- relog with active task and permanent upgrades;
- verify legacy Hunting Task Point preservation.

# 7. Acceptance-test outline

The following are candidate assertions, not claims about current Canary.

| Contract | Acceptance assertion |
|---|---|
| Offer count | A fresh eligible character receives exactly three Bounty offers. |
| Difficulty immutability | Changing preferred difficulty leaves the active task unchanged and affects only the next offer generation. |
| Atomic reroll | One reroll consumes the correct token state and replaces the entire offer set exactly once. |
| No cooldown | Completing a task permits the next selection flow immediately. |
| Target scope | The same combat action receives a Talisman bonus against an active target and no bonus against a non-target. |
| Equipment gate | Unequipping the Talisman disables all four effect families without erasing upgrades. |
| Persistence | Upgrade levels and active task state survive a clean relog according to the defined contract. |
| Character binding | Moving or replacing the physical item does not transfer progression to another character. |
| Token cap | Daily claim and completion rewards cannot create an invalid token count above 10. |
| Migration | A fixture with legacy Hunting Task Points retains the same balance after migration. |
| Grade rewards | Silver and Gold tasks use their configured grade rewards without changing target matching rules. |
| Idempotency | Retried completion cannot grant duplicate rewards. |

# 8. Risks

## Gameplay power

- Applying bonuses to a creature family instead of the exact active target may
  create unintended global farming power.
- Applying progression without equipped-state validation contradicts current
  official behavior.
- Copying the teaser's damage reduction instead of the released life-leech
  effect would implement obsolete behavior.

## Economy

- Loot bonuses and repeatable no-cooldown tasks can amplify supply.
- Token overflow or duplicate completion can create unbounded rerolls.
- Custom gold sinks should be evaluated separately from parity behavior.

## Persistence

- Character-bound progression must not accidentally bind to one item instance.
- Active task, offers, reroll state, daily claim, points, and upgrade state need
  explicit transaction and rollback boundaries.
- Legacy Hunting Task Point preservation is a migration acceptance criterion.

## Client compatibility

- The Task Board, Kill Tracker, effect display, and Store/expansion distinction
  may require maintained-client protocol/UI support.
- No server payload should be changed without checking the `prey` module's
  maintained-client dependency.

# 9. Recommended next action

Run `BNT-001` as a separate bounded audit task against current `main`.

The audit should produce a matrix with:

```text
requirement
definition
registration
runtime path
persistence
protocol/client
automated test
physical-client proof
current status
```

Do not start with formulas, caps, creature pools, or protocol bytes from memory.
Use the forum as requirement discovery, the current official guide as the
released-behavior baseline, and current Canary plus maintained OTClient as the
implementation authority.
