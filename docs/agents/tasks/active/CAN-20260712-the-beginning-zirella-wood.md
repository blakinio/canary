---
task_id: CAN-20260712-the-beginning-zirella-wood
status: in-progress
agent: "GPT-5.6 Thinking"
branch: fix/the-beginning-zirella-wood
base_branch: main
created: 2026-07-12
updated: 2026-07-12
risk: medium
related_pr: "#149"
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

# Implemented contract

- `the_beginning_zirella_wood.lua` registers only item `7753` and item `7772` actions.
- Tree behavior is bounded to the five map-verified Tutorial Island coordinates.
- Both Zirella storages must equal stage `6` before either action can progress.
- A successful tree use creates branch `7772` on the player's tile, starts its decay, sends tutorial `24`, advances the hint to at least `15`, and applies a five-second per-character in-memory cooldown.
- The cooldown uses current Canary-compatible `os.time()` logic and does not allocate a new persistent storage or combat condition.
- A successful branch use requires cart `7751` at exactly `32062,32271,7`, removes one branch, emits `CONST_ME_MAGIC_GREEN`, and writes both Zirella storages to stage `7`.
- Stage `7+` cannot consume another branch because the exact stage-6 gate is no longer satisfied.

# Acceptance criteria

- [x] register exactly dead-tree item `7753` and branch item `7772`;
- [x] bound dead-tree behavior to the five verified tutorial positions;
- [x] require the accepted Zirella stage before branch creation;
- [x] create branch `7772` on the player's ground tile, not directly in inventory;
- [x] preserve the historical five-second use delay and tutorial-hint progression through current Canary APIs;
- [x] accept the branch only on cart `7751` at `32062,32271,7`;
- [x] consume exactly one branch, show green magic, and set `ZirellaNpcGreetStorage` and `ZirellaQuestLog` to `7` exactly once;
- [x] do not modify `.otbm`, items, NPCs, spawns, engine, or unrelated gameplay;
- [x] add focused deterministic contract tests;
- [ ] final-head CI and global datapack runtime smoke pass.

# Runtime tests

1. Stage 5: using a tutorial dead tree produces nothing.
2. Stage 6: using a tutorial dead tree creates branch `7772` on the player's tile and advances the hint to at least 15.
3. Reusing during cooldown produces no additional branch.
4. Using the branch on a non-cart target does not consume it.
5. Using the branch on a matching item outside Zirella's cart position does not consume it.
6. Stage 6: using one branch on the verified cart consumes it and writes both storages to 7.
7. Stage 7 or 8: repeated delivery does not consume another branch or duplicate progression.
8. Zirella dialogue at stage 7 grants the existing 50 XP reward and advances both storages to 8.

# Validation notes

- Head `679f8b48f9811a86828d2e0c8d81e373522b7d98` passed Lua tests, fast checks, AI Agent Tools and Account Quests, but global datapack runtime smoke failed during script loading.
- Runtime log identified `Condition(CONDITION_EXHAUST_WEAPON)` as an invalid condition type in current Canary, leaving `treeExhaust` nil.
- The invalid historical condition was replaced by a five-second per-character `os.time()` cooldown with no new persistent storage.
- Focused tests now explicitly reject `CONDITION_EXHAUST_WEAPON` and validate the replacement cooldown contract.
- Final-head CI, including global datapack runtime smoke, is required before merge.
- Runtime E2E remains required on an actual Canary world after repository validation.

# Safety

No map or binary change is permitted. Historical code is corroborating evidence only; current map positions, current item IDs, current NPC storages, and the current quest catalogue are authoritative.
