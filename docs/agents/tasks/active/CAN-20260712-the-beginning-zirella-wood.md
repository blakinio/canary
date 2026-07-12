---
task_id: CAN-20260712-the-beginning-zirella-wood
status: in-progress
agent: "GPT-5.6 Thinking"
branch: fix/the-beginning-zirella-wood
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
  - data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_wood.lua
  - tools/ai-agent/test_the_beginning_zirella_wood.py
  - docs/agents/tasks/active/CAN-20260712-the-beginning-zirella-wood.md
  - docs/agents/ACTIVE_WORK.md
  - docs/agents/CHANGELOG.md
modules_touched:
  - The Beginning quest gameplay
  - World Semantic Review follow-up
reuses:
  - Storage.Quest.U8_2.TheBeginningQuest
  - existing Action registration API
  - merged PR #146 dependency report
cross_repo_tasks: []
---

# Goal

Restore the authentic Collecting Wood progression for Zirella without modifying the OTBM map: use one of the verified tutorial dead trees to create a movable branch on the ground, then use that branch on Zirella's verified cart to advance both Zirella storages to stage 7.

# Evidence contract

Current Canary evidence:

- dead tree item `7753` at five verified Tutorial Island positions;
- branch item `7772`;
- Zirella cart item `7751` at `32062,32271,7`;
- current NPC and quest catalogue require an external transition from stage 6 to stage 7;
- the active NPC and quest log consistently describe a single branch interaction.

Official-Tibia historical cross-check:

- TibiaWiki describes using a dead tree, moving the dropped branch to the cart, and returning to Zirella;
- historical ORTS implementations remove the branch, show green magic, and set both Zirella storages to 7 after one delivery;
- the old dialogue mentions two branches, but the actual historical server transition and current Canary state machine complete after one. The implementation follows the executable/current contract and records this discrepancy rather than inventing a counter storage.

# Acceptance criteria

- [ ] register exactly dead-tree item `7753` and branch item `7772`;
- [ ] bound dead-tree behavior to the five verified tutorial positions;
- [ ] require the accepted Zirella stage before branch creation;
- [ ] create branch `7772` on the player's ground tile, not directly in inventory;
- [ ] preserve the historical short-use exhaust and tutorial-hint progression;
- [ ] accept the branch only on cart `7751` at `32062,32271,7`;
- [ ] consume exactly one branch, show green magic, and set `ZirellaNpcGreetStorage` and `ZirellaQuestLog` to `7` exactly once;
- [ ] do not modify `.otbm`, items, NPCs, spawns, engine, or unrelated gameplay;
- [ ] add focused deterministic contract tests;
- [ ] required CI passes on the final head.

# Runtime tests

1. Stage 5: using a tutorial dead tree produces nothing.
2. Stage 6: using a tutorial dead tree creates branch `7772` on the player's tile and advances the hint to at least 15.
3. Reusing during exhaust produces no additional branch.
4. Using the branch on a non-cart target does not consume it.
5. Using the branch on a matching item outside Zirella's cart position does not consume it.
6. Stage 6: using one branch on the verified cart consumes it and writes both storages to 7.
7. Stage 7 or 8: repeated delivery does not consume another branch or duplicate progression.
8. Zirella dialogue at stage 7 grants the existing 50 XP reward and advances both storages to 8.

# Safety

No map or binary change is permitted. Historical code is corroborating evidence only; current map positions, current item IDs, current NPC storages, and the current quest catalogue are authoritative.