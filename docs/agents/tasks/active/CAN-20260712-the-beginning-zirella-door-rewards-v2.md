---
task_id: CAN-20260712-the-beginning-zirella-door-rewards-v2
status: in-progress
agent: "GPT-5.6 Thinking"
branch: fix/the-beginning-zirella-door-rewards-v2
base_branch: main
created: 2026-07-12
updated: 2026-07-12
risk: medium
related_pr: "#186"
depends_on:
  - "PR #149 Zirella Collecting Wood restoration"
blocks:
  - "The Beginning runtime E2E completion"
owned_paths:
  - data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_door.lua
  - data-otservbr-global/scripts/actions/other/others/quest_system1.lua
  - tools/ai-agent/test_the_beginning_zirella_door_rewards.py
  - docs/agents/tasks/active/CAN-20260712-the-beginning-zirella-door-rewards-v2.md
modules_touched:
  - The Beginning quest gameplay
  - generic quest reward tutorial mapping
reuses:
  - Storage.Quest.U8_2.TheBeginningQuest
  - QuestDoorTable pair 6898/6899
  - existing questSystem1 AID 2000 reward flow
---

# Goal

Refresh the previously validated Zirella reward-room fix onto the current `main` without carrying stale branch history or shared-document conflicts.

# Implemented contract

- UID `50085` at `32058,32266,7` stays sealed until `ZirellaNpcGreetStorage >= 8`.
- Door states use the existing `6898 <-> 6899` pair, standard sounds, movement and obstruction check.
- Tutorial `10` maps to current shovel chest UID `50093`.
- Tutorial `11` maps to current rope chest UID `50094`.
- Generic reward contents, storage ownership and AID `2000` remain unchanged.

# Acceptance criteria

- [x] clean branch from current `main`;
- [x] no OTBM, item, NPC, spawn or engine changes;
- [x] focused deterministic contract test;
- [ ] final-head CI and global datapack smoke pass;
- [ ] squash merge after green final head.

# Runtime follow-up

Verify stage-7 denial, stage-8 passage, occupied doorway behavior and one-shot tutorial popups on a live Canary world.
