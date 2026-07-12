---
task_id: CAN-20260712-the-beginning-carlos-flow
status: in-progress
agent: "GPT-5.6 Thinking"
branch: fix/the-beginning-carlos-flow
base_branch: main
created: 2026-07-12
updated: 2026-07-12
risk: medium
related_pr: "#157"
depends_on:
  - "PR #146 The Beginning dependency audit"
blocks:
  - "The Beginning runtime E2E completion"
owned_paths:
  - data-otservbr-global/npc/carlos.lua
  - tools/ai-agent/test_the_beginning_carlos_flow.py
  - docs/agents/tasks/active/CAN-20260712-the-beginning-carlos-flow.md
  - docs/agents/ACTIVE_WORK.md
  - docs/agents/CHANGELOG.md
modules_touched:
  - The Beginning Carlos NPC gameplay
  - current NPC shop callback flow
reuses:
  - Storage.Quest.U8_2.TheBeginningQuest
  - existing NpcType shop callbacks
  - CALLBACK_ON_TRADE_REQUEST
cross_repo_tasks: []
---

# Goal

Repair Carlos's current The Beginning state machine without changing the map, rewards, item definitions, or unrelated NPC behavior.

# Confirmed defects

- Saying `outfit` while Carlos is at stage 1 incorrectly jumps `CarlosQuestLog` to 7 and `CarlosNpcGreetStorage` to 8, bypassing the complete food/trade tutorial.
- The defined `onTradeRequest` gate is never registered, so its intended quest restriction is dead code.
- Selling meat `3577` or ham `3582` does not advance Carlos from stage 6 to stage 7, leaving the documented `ready` completion path unreachable.
- Tutorial `13`, present in the historical trade step, is not emitted by the current converted NPC.

# Evidence contract

Current Canary is authoritative:

- quest catalogue stage 1 teaches outfit selection;
- stage 6 requires asking Carlos for trade;
- stage 7 means the player successfully learnt NPC trading;
- Carlos's current dialogue says to sell the food and then say `ready`;
- current shop buys only meat `3577` and ham `3582` for two gold each.

Historical ORTS code is corroborating evidence only. It confirms tutorial `13` belongs to the trade-opening step, but its premature stage-7 write is not copied because current dialogue and quest text require an actual sale first.

# Implemented contract

- `outfit` at stage 1 calls the same `teachOutfit` transition as `yes/help/ok`: both Carlos storages become 2 and tutorial `12` is sent.
- `CALLBACK_ON_TRADE_REQUEST` is registered and requires both Carlos storages at stage 6 plus an active trade permission state.
- the first valid trade request sends tutorial `13` and records that the tutorial trade window was opened, without completing the mission;
- reopening the same valid trade remains allowed without repeating tutorial `13`;
- `NpcType.onSellItem` advances both Carlos storages to 7 only after a positive-amount sale of meat `3577` or ham `3582` while the valid tutorial trade is open;
- a successful tutorial sale marks the trade state completed and makes the existing same-session `ready` dialogue reachable;
- item removal and two-gold payment remain entirely inside the existing NPC shop transaction implementation.

# Acceptance criteria

- [x] remove the `outfit` completion bypass;
- [x] register and enforce `CALLBACK_ON_TRADE_REQUEST`;
- [x] send tutorial `13` only for the valid stage-6 trade request;
- [x] advance to stage 7 only after a successful meat/ham sale;
- [x] prevent unrelated items, wrong stages, or repeated sales from altering quest state;
- [x] preserve current item prices and shop transaction implementation;
- [x] add focused deterministic contract tests;
- [ ] pass Lua tests, fast checks, AI Agent Tools, Account Quests, and global datapack runtime smoke;
- [x] do not modify `.otbm`, `items.otb`, NPC placement, spawns, engine, or other quests.

# Runtime tests

1. Stage 1: saying `outfit` shows the outfit instruction, sends tutorial 12, and advances only to stage 2.
2. Before stage 6: requesting trade is denied and no trade tutorial/state change occurs.
3. Stage 6 with trade permission: requesting trade opens the existing two-item shop and sends tutorial 13.
4. Opening trade without selling leaves both quest storages at stage 6.
5. Selling meat advances both storages to stage 7 and disables tutorial trade permission.
6. Selling ham has the same transition.
7. Wrong item or repeated sale does not alter completed state.
8. Saying `ready` at stage 7 performs the existing completion dialogue and advances greet storage to 8.

# Validation notes

- Implementation commit: `86a857ba045d3830bea9932c41f12ee79ca29b44`.
- Focused contract test commit: `fa531c98964126d794ef9f50838d6a23c26d63d7`.
- Draft PR: #157.
- Runtime E2E remains required on an actual Canary world after repository validation.

# Safety

No map, binary, item, economy, or engine change is permitted. Current quest catalogue, dialogue, item IDs, shop prices, and callback APIs define the implementation contract.