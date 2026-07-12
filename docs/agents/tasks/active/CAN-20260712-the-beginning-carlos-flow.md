---
task_id: CAN-20260712-the-beginning-carlos-flow
status: in-progress
agent: "GPT-5.6 Thinking"
branch: fix/the-beginning-carlos-flow
base_branch: main
created: 2026-07-12
updated: 2026-07-12
risk: medium
related_pr: ""
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

# Planned contract

- `outfit` at stage 1 follows the same outfit-instruction transition as `yes/help/ok`: stages 1 -> 2 and tutorial `12`.
- trade opens only while both Carlos greet/log progression are at stage 6 and trade permission is active.
- opening the permitted trade window sends tutorial `13` once without completing the mission.
- the first successful sale of meat or ham while stage 6 advances `CarlosQuestLog` and `CarlosNpcGreetStorage` to 7 and disables further tutorial trade access.
- saying `ready` at stage 7 preserves the existing final dialogue and advances greet storage to 8.
- no inventory removal or gold handling is reimplemented; the existing shop transaction remains authoritative.

# Acceptance criteria

- [ ] remove the `outfit` completion bypass;
- [ ] register and enforce `CALLBACK_ON_TRADE_REQUEST`;
- [ ] send tutorial `13` only for the valid stage-6 trade request;
- [ ] advance to stage 7 only after a successful meat/ham sale;
- [ ] prevent unrelated items, wrong stages, or repeated sales from altering quest state;
- [ ] preserve current item prices and shop transaction implementation;
- [ ] add focused deterministic contract tests;
- [ ] pass Lua tests, fast checks, AI Agent Tools, Account Quests, and global datapack runtime smoke;
- [ ] do not modify `.otbm`, `items.otb`, NPC placement, spawns, engine, or other quests.

# Runtime tests

1. Stage 1: saying `outfit` shows the outfit instruction, sends tutorial 12, and advances only to stage 2.
2. Before stage 6: requesting trade is denied and no trade tutorial/state change occurs.
3. Stage 6 with trade permission: requesting trade opens the existing two-item shop and sends tutorial 13.
4. Opening trade without selling leaves both quest storages at stage 6.
5. Selling meat advances both storages to stage 7 and disables tutorial trade permission.
6. Selling ham has the same transition.
7. Wrong item or repeated sale does not alter completed state.
8. Saying `ready` at stage 7 performs the existing completion dialogue and advances greet storage to 8.

# Safety

No map, binary, item, economy, or engine change is permitted. Current quest catalogue, dialogue, item IDs, shop prices, and callback APIs define the implementation contract.