---
task_id: CAN-20260712-the-beginning-zirella-door-rewards
status: in-progress
agent: "GPT-5.6 Thinking"
branch: fix/the-beginning-zirella-door-rewards
base_branch: main
created: 2026-07-12
updated: 2026-07-12
risk: medium
related_pr: ""
depends_on:
  - "PR #146 The Beginning dependency audit"
  - "PR #149 Zirella Collecting Wood restoration"
blocks:
  - "The Beginning runtime E2E completion"
owned_paths:
  - data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_door.lua
  - data-otservbr-global/scripts/actions/other/others/quest_system1.lua
  - tools/ai-agent/test_the_beginning_zirella_door_rewards.py
  - docs/agents/tasks/active/CAN-20260712-the-beginning-zirella-door-rewards.md
  - docs/agents/ACTIVE_WORK.md
  - docs/agents/CHANGELOG.md
modules_touched:
  - The Beginning quest gameplay
  - generic quest reward tutorial mapping
reuses:
  - Storage.Quest.U8_2.TheBeginningQuest
  - QuestDoorTable door pair 6898/6899
  - existing questSystem1 AID 2000 reward flow
cross_repo_tasks: []
---

# Goal

Restore the authentic post-Zirella reward-room gate and align the shovel/rope tutorial popups with the UIDs actually present in the verified map, without modifying the OTBM.

# Evidence contract

Current Canary/map evidence:

- Zirella's closed reward-room door is item `6898`, UID `50085`, at `32058,32266,7`;
- `QuestDoorTable` pairs closed item `6898` with open item `6899`;
- Zirella grants permission to enter only when `ZirellaNpcGreetStorage` reaches stage `8`;
- shovel chest UID `50093` at `32059,32265,7` contains item `3457` and uses generic quest AID `2000`;
- rope chest UID `50094` at `32067,32264,8` contains item `3003` and uses generic quest AID `2000`;
- `quest_system1.lua` still assigns tutorials `10/11` to absent/stale UIDs `50084/50086`.

Historical real-Tibia cross-check:

- The Beginning quest transcript grants access to Zirella's house only after the player reports successful wood delivery and receives the reward dialogue;
- the historical handler denies the closed door before Zirella stage `8`, opens `6898 → 6899` after completion, and uses the standard sealed-door message;
- the historical route then teaches taking the shovel from Zirella's reward chest and the rope from the cave box.

# Acceptance criteria

- [ ] add one UID `50085` Action handling both door states `6898/6899`;
- [ ] deny opening while `ZirellaNpcGreetStorage < 8` with the canonical sealed-door message;
- [ ] open and teleport using current door semantics, with the normal opening sound;
- [ ] close only when no creature blocks the doorway, with the normal closing sound;
- [ ] map tutorial `10` to current shovel chest UID `50093`;
- [ ] map tutorial `11` to current rope chest UID `50094`;
- [ ] remove stale tutorial mappings `50084/50086` without changing reward storage or contents;
- [ ] add deterministic focused contract tests;
- [ ] do not modify `.otbm`, items, NPC dialogue, spawns, engine, or unrelated quest rewards;
- [ ] final-head CI passes.

# Runtime tests

1. Stage `7`: closed UID `50085` door remains closed and sends the sealed-door message.
2. Stage `8`: closed door transforms `6898 → 6899`, emits the open sound, and moves the player through.
3. Open door transforms `6899 → 6898` when the doorway is clear.
4. Open door stays open when a creature occupies the doorway.
5. Taking UID `50093` shovel reward sends tutorial `10` exactly once through the existing one-shot chest storage.
6. Taking UID `50094` rope reward sends tutorial `11` exactly once.
7. Existing reward contents, capacity errors, storage keys, and AID `2000` registration remain unchanged.

# Safety

No binary or map edit is permitted. The door pair, UID, positions, storages, reward UIDs, contents, and tutorial IDs are all fixed by current map/datapack evidence; historical sources only corroborate the intended gameplay order.