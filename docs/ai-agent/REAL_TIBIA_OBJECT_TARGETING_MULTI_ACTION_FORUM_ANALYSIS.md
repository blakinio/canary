# Real Tibia Improved Object Targeting and Multi-Action Forum Analysis

> Status: official announcement and bounded community-feedback evidence, not Canary or OTClient implementation proof
>
> Sources observed: 2026-07-23
>
> Target use: requirements discovery and validation planning for `blakinio/canary`

## Executive summary

The October 2025 official announcement, its linked forum thread, and the November 2025 release summary describe two client-facing quality-of-life features:

1. **Improved Object Targeting** adds an action-bar option named **Use at cursor position**. It applies a rune or object to the position under the mouse cursor with one activation instead of opening the normal second targeting step.
2. **Multi-Action Button** assigns up to three spells or objects to one action-bar button. Every execution still requires player input; the feature selects an eligible action according to its configured order and cooldown state.

The visible first forum page is strongly positive but also exposes the implementation questions most likely to create user-visible inconsistencies:

- whether priority means a fixed first-ready scan or a literal rotation;
- what happens when an action is off cooldown but cannot execute for another reason;
- how cooldown-reset mechanics such as Momentum affect selection;
- whether holding a key repeats player-triggered actions without becoming automation;
- which objects, potions, equipment, friendly targets, and battle-list entries are supported;
- how the feature differs from prohibited macros and automatic healing.

This report converts those statements into a bounded requirements and test inventory. It does not prove that either feature exists in current Canary or the maintained OTClient, and it does not authorize a server or client implementation.

## Sources and provenance

| Source | Date | Identifier | Coverage used | Evidence role |
|---|---:|---|---|---|
| [Improved Object Targeting and Multiaction Button](https://www.tibia.com/news/?id=8560&subtopic=newsarchive) | 2025-10-29 | news `8560` | official announcement indexed on 2026-07-23 | Official feature name, intended interaction and examples |
| [Forum thread: Improved Object Targeting and Multiaction Button](https://www.tibia.com/forum/?action=thread&threadid=4989143) | 2025-10-29 onward | thread `4989143` | complete first displayed page plus its official-reply index; 20 visible posts out of 340 displayed results | Official summary, clarification topics and bounded community feedback |
| [Winter Update 2025](https://www.tibia.com/news/?id=8570&subtopic=newsarchive) | 2025-11-24 | news `8570` | official release summary indexed on 2026-07-23 | Confirms both features were announced as part of the live update |

Collection boundary:

- The forum reported 340 results and was closed when observed.
- The captured first displayed page contained 20 posts: two community-manager posts and 18 community posts.
- The opening post exposed an edited official-reply index dated October 29-30, 2025.
- Cloudflare rejected direct HTTP collection. The current Chrome page supplied the first-page rendered text, but the remaining pages and the bodies of the indexed official replies were not collected.
- Counts in this report therefore describe the first-page sample only. They must not be presented as full-thread sentiment or issue frequency.
- No account data, cookie, browser profile, raw HTML corpus, proprietary client files, or forum attachment is committed.

## Evidence boundary

The official sources are strong evidence for:

- the announced names and user-visible purpose of both features;
- the visible interaction described by the community managers;
- that a button press or key press remains necessary for each action;
- the themes explicitly listed in the official-reply index;
- questions, requests, praise, and concerns present in the captured community sample.

They are not sufficient evidence for:

- exact current official-client behavior after the collection date;
- packet layout, opcode, field order, capability gate, or server-side implementation;
- current Canary or maintained OTClient support;
- exact cooldown, resource, target-validity, retry, key-repeat, or failure semantics not fully stated in the captured text;
- permission to reproduce proprietary client code or assets;
- a balanced gameplay value or a Canary defect.

Any implementation follow-up must use `docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md`, inspect the current maintained client and Canary separately, and add deterministic behavior evidence.

## Official feature contract

### Improved Object Targeting

The official announcement and forum summary establish the following visible contract:

- A new action-bar targeting option is named **Use at cursor position**.
- The option is selected while dragging an object into the action bar.
- Activating the slot applies the object directly to what is under the mouse cursor in the game window.
- The normal two-step use-then-target flow becomes one activation.
- The announcement describes the supported payload as objects and runes.
- If the cursor is outside the game window, the action is not executed and a short message is shown.
- Existing use constraints remain authoritative. The announcement's rope example says the character still moves to a valid adjacent field before use when the item requires adjacency.
- The option can be used with the Battle List.

The official-reply index contains the label **object targeting only runes and objects**. Because the linked reply body was not captured, the defensible conclusion is limited to the category boundary already consistent with the announcement. It does not prove support for equipment switching, arbitrary UI widgets, spells, automatic friendly-target selection, or every object subtype.

### Multi-Action Button

The official announcement and forum summary establish:

- A button can contain up to three actions.
- Players open an assignment interface from an action-bar button and place spells or objects into three slots.
- The action order is configurable.
- Each activation still requires a click or key press.
- No timer-driven or event-driven automatic execution is described.
- The announcement describes selection as the first available action that is not on cooldown.
- The button icon changes to reflect the next action that would be executed.
- Official examples mix spell rotations and spell-plus-rune fallback.

The captured forum summary uses the shorter phrase **cycling through them with repeated clicks or key presses**. The announcement instead describes a priority scan for the first action not on cooldown. These descriptions can coexist if “cycling” is colloquial, but the exact selection state machine must be proven by observation or maintained-client tests before implementation.

### Official-reply index

The opening community-manager post lists the following edited clarification topics:

| Date | Indexed topic | Safe use in this report |
|---|---|---|
| 2025-10-29 | prioritise / priority | Confirms priority was a recurring official clarification topic; exact tie and failure behavior remain uncollected |
| 2025-10-29 | battle list | Corroborates the announcement's Battle List support |
| 2025-10-29 | no automation I-III | Reinforces that the feature requires player input and must not become automatic execution |
| 2025-10-29 | multiple multiaction buttons possible | Indicates the feature is not limited to one configured button |
| 2025-10-29 | holding button | Identifies key-hold behavior as an official clarification topic; the linked behavior is not inferred |
| 2025-10-29 | object targeting only runes and objects | Corroborates the category boundary |
| 2025-10-30 | only check for cd | Indicates cooldown-only eligibility was clarified; exact behavior for insufficient resources or invalid targets still requires the reply body or runtime proof |
| 2025-10-30 | please check test server | Directs uncertain behavior to empirical validation rather than assumption |

The index labels are navigation summaries, not substitutes for the complete linked replies. Future work should retrieve the exact post identifiers and text before treating these labels as a full specification.

## First-page community sample

### Composition

| Classification | Posts | Share of 18 community posts |
|---|---:|---:|
| Clearly positive or thankful | 10 | 55.6% |
| Questions or extension requests | 5 | 27.8% |
| Criticism, macro-policy comparison, or fairness concern | 3 | 16.7% |

This is a manual, mutually exclusive top-level classification of the captured page. A positive post can still mention a design implication, and the sample is not representative of the remaining 322 displayed results.

### Recurring first-page themes

| Theme | Minimum posts in sample | Observed signal |
|---|---:|---|
| Spell rotation and Momentum | 3 | Players expected smoother rotations and asked how priority interacts with cooldown resets |
| Macro, automation, or fairness boundary | 4 | Two posts compared the feature with historical macro enforcement, one asked for auto-heal, and one proposed a penalty for the easier rotation |
| Broader object or equipment use | 3 | Requests covered rings/amulets, potions, and combining rune variants |
| Healing or friendly-target use | 2 | Requests mentioned auto-heal and easier Ultimate Healing Rune targeting |
| Reduced input fatigue | 1 | One player explicitly connected the feature with returning to a less tiring playstyle |

Counts overlap and are lower-bound manual theme coding. They measure which questions appeared on page one, not votes or independent proof.

### What the sample does and does not say

The sample supports these design observations:

- The features were welcomed primarily as input-efficiency and rotation-quality improvements.
- Momentum is an immediate compatibility concern because it can change cooldown availability between presses.
- Some players perceive priority-based repeated input as “auto rotation” even when every action requires a press.
- Equipment, potions, healing, and friendly targeting are natural extension requests, but the captured official contract does not prove they are included.
- The macro-policy comparison makes transparent input and automation boundaries important for user trust.

The sample does not establish:

- that the broader requests should be implemented;
- that one-press selection is equivalent to a prohibited macro;
- that a cooldown penalty is balanced or intended;
- how the full 340-result thread is distributed;
- any exact server or client defect.

## Aggregated requirements inventory

### Object targeting requirements

| ID | Requirement | Evidence state |
|---|---|---|
| `IOT-01` | Expose **Use at cursor position** for an action-bar object assignment. | official |
| `IOT-02` | Execute against the current game-window cursor position with one activation. | official |
| `IOT-03` | Do not execute when the cursor is outside the game window; provide short feedback. | official |
| `IOT-04` | Preserve ordinary use restrictions, pathing and adjacency rules. | official example; exact edge behavior unproven |
| `IOT-05` | Support the Battle List as a target surface. | official |
| `IOT-06` | Limit the announced targeting mode to runes and objects. | official announcement/index |
| `IOT-07` | Preserve authoritative server validation for range, line of sight, floor, ownership and use legality. | derived safety requirement; current path not assessed |
| `IOT-08` | Define deterministic behavior when the cursor target disappears or changes during movement. | unresolved |
| `IOT-09` | Define friendly, hostile, self, tile and creature target filtering per object. | unresolved |

### Multi-action requirements

| ID | Requirement | Evidence state |
|---|---|---|
| `MAB-01` | Allow one to three configured actions in an explicit order. | official |
| `MAB-02` | Accept spells and objects as slot contents. | official |
| `MAB-03` | Require a player click or key press for every executed action. | official |
| `MAB-04` | Do not initiate actions from cooldown completion, health, mana, target state or time alone. | official no-automation boundary; derived negative requirement |
| `MAB-05` | Select according to priority and cooldown availability. | official announcement/index |
| `MAB-06` | Update the icon to the action expected to execute next. | official |
| `MAB-07` | Support more than one independently configured multi-action button. | official-reply index; exact limit unproven |
| `MAB-08` | Define held-key repeat behavior without creating autonomous execution. | official topic; exact contract unresolved |
| `MAB-09` | Define whether insufficient mana, missing ammunition, invalid target or other execution failure advances to another action. | unresolved; index suggests cooldown-only eligibility |
| `MAB-10` | Re-evaluate availability after cooldown-changing mechanics such as Momentum. | community question; derived compatibility requirement |
| `MAB-11` | Make the priority and next-action state visible enough to explain the result of a press. | derived usability requirement |
| `MAB-12` | Keep separate buttons' configuration, priority and visual state independent. | derived from multiple-button support |

## Risk and ambiguity register

| Priority | Risk or ambiguity | Why it matters | Minimum evidence needed |
|---:|---|---|---|
| P0 | Priority scan versus literal rotation | Different state machines produce different spells after cooldown changes | Exact official-reply text or controlled current-client observation |
| P0 | Cooldown-only eligibility | A ready spell may still lack mana, target, weapon or ammunition | Tests for every failure class and whether fallback occurs |
| P0 | Hold-to-repeat versus automation | Input repeat can be accessible and still cross an anti-automation boundary if implemented incorrectly | Exact key-down/key-repeat behavior and one-action-per-input-event tests |
| P0 | Server authority | Client convenience must not bypass use, range, cooldown or target validation | Current Canary packet and action-validation path |
| P1 | Momentum and cooldown resets | Availability and the displayed next action can change between presses | Deterministic reset and priority fixtures |
| P1 | Cursor target stability | Auto-walk or latency can make the original cursor target stale | Target snapshot/resolve contract and movement tests |
| P1 | Battle List identity | A list row represents a creature rather than a ground coordinate | Maintained-client target-resolution trace |
| P1 | User trust around macros | Opaque selection can look like forbidden automation | Clear UI state, documented boundaries and no background triggers |
| P2 | Equipment, potions and friendly healing | These are prominent extension requests but outside the captured category proof | Separate official/current-client evidence before scope expansion |

## Bounded acceptance-test candidates

These are test candidates, not claims that a current implementation exists.

### Improved Object Targeting

1. A configured rune activates once on the creature or tile currently under the game-window cursor without opening a second crosshair step.
2. An eligible object behaves the same way while retaining its ordinary range and line-of-sight validation.
3. An adjacency-limited object causes only the ordinary legal movement and use sequence.
4. A cursor outside the game window sends no use action and shows bounded feedback.
5. A supported Battle List row resolves to the intended creature, including row movement caused by list resorting.
6. An unsupported action category cannot be configured with this targeting mode.
7. Target disappearance, floor change, movement, blocked path and stale creature identity fail safely.
8. The server rejects invalid use exactly as it does for the ordinary targeting flow.

### Multi-Action Button

1. Empty, one-slot, two-slot and three-slot configurations have deterministic UI and execution behavior.
2. When slot one is ready, one press executes slot one only.
3. When slot one is on cooldown and slot two is ready, one press executes slot two only.
4. When all configured actions are on cooldown, one press executes nothing and gives the intended feedback.
5. Repeated presses never schedule a later action automatically.
6. A held key produces only the exact supported input-repeat behavior and stops immediately on release or focus loss.
7. A cooldown reset between presses changes selection and the next-action icon consistently.
8. Insufficient mana, missing ammunition, invalid target, wrong equipment and other non-cooldown failures follow one documented fallback rule.
9. Mixed spell/object configurations preserve each action's ordinary targeting mode.
10. Two or more multi-action buttons keep independent ordering, cooldown display and next-action state.
11. Rebinding, deleting, moving, logging out and client restart preserve or clear configuration according to an explicit persistence contract.
12. No health, mana, target, cooldown-completion or timer event executes an action without a new player input event.

## Canary and client boundary

The announced features appear primarily client-facing because they concern action-bar configuration, cursor/Battle List resolution, priority display and input handling. Canary remains authoritative for ordinary action legality, cooldowns, resources, range and target validation.

This report does not establish:

- that a new wire message is required;
- that existing use/spell messages are sufficient;
- that the server should know a button contains multiple actions;
- that Canary should reproduce client-side priority logic;
- that the maintained OTClient already implements equivalent behavior.

A future implementation investigation should begin in the maintained client and trace the exact existing packets into Canary. If the wire contract is unchanged, record that proof. If it changes, create an explicit Canary-OTClient coordination record with byte-exact tests and rollout behavior. No `blakinio/otclient` write is authorized by this task.

## Prioritized follow-up questions

1. Retrieve the exact official reply bodies linked by the opening post, including post identifiers and wording for priority, cooldown-only checking and held-button behavior.
2. Observe the released feature in a current supported official client or another provenance-pinned build and record the exact selection state machine.
3. Inspect the maintained OTClient for existing cursor-use, Battle List, action-bar and key-repeat surfaces.
4. Trace current Canary object-use, rune-use, spell, cooldown and invalid-target validation paths.
5. Determine whether the existing wire contract is sufficient without trusting client-side validation.
6. Build one client-side deterministic state-machine test matrix before proposing UI or server changes.
7. Treat potions, equipment switching, friendly healing and automatic health/mana conditions as separate scopes requiring independent evidence.

## Conclusion

The official material supports a narrow design principle:

> Reduce target-selection and rotation input overhead while preserving one explicit player input per action and all ordinary action constraints.

The page-one forum sample shows why the details matter. Players welcome reduced fatigue and smoother rotations, but immediately test the boundary against Momentum, equipment, healing, macro policy and fairness. For Canary, the safe next step is not implementation from forum prose. It is a bounded maintained-client and server-path investigation that turns the unresolved priority, cooldown, target and key-repeat rules into deterministic tests.
