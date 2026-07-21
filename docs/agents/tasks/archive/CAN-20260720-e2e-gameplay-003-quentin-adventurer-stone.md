---
task_id: CAN-20260720-e2e-gameplay-003-quentin-adventurer-stone
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-003-QUENTIN-STONE
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-gameplay-003-quentin-adventurer-stone
base_branch: main
created: 2026-07-20
updated: 2026-07-21
last_verified_commit: "c42b40c6583b60f315639147e2044f1772915b7c"
risk: medium
related_issue: ""
related_pr: "637"
depends_on:
  - merged Universal physical gameplay action plans
  - merged typed player item presence persistence
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260720-e2e-gameplay-003-quentin-adventurer-stone.md
    - tests/e2e/scenarios/npc/quentin-adventurer-stone.json
    - tests/e2e/test_quentin_adventurer_stone.py
    - tools/e2e/client/quentin_adventurer_stone.lua
  read_only:
    - data-otservbr-global/npc/quentin.lua
    - data-otservbr-global/world/otservbr-npc.xml
    - data/npclib/npc_system/npc_handler.lua
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/persistence_assertions.py
    - tools/e2e/client/agent_e2e_scenario.lua
modules_touched:
  - Universal E2E feature-owned NPC scenario
reuses:
  - Universal Agent E2E two-session lifecycle
  - maintained OTClient g_game.talkPrivate and MessageModes.NpcTo
  - maintained OTClient g_game.onTalk callback
  - typed player_item_presence persistence
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Prove the bounded Quentin Adventurer Stone physical NPC flow and durable reward persistence while keeping focused NPC-specific dialogue in the feature adapter and reusing the canonical Universal E2E lifecycle unchanged.

# Acceptance criteria

- [x] Reuse the existing Universal E2E runner and lifecycle.
- [x] Use current Quentin spawn and Lua reward evidence.
- [x] Execute response-gated focused NPC dialogue through maintained OTClient `MessageModes.NpcTo`.
- [x] Observe greeting, free-stone offer and reward response via `g_game.onTalk`.
- [x] Complete safe logout, relog and second safe logout.
- [x] Prove inventory item `16277` through typed `player_item_presence` after the lifecycle.
- [x] Keep Quentin-specific dialogue and item evidence in feature-owned files.
- [ ] Pass exact-final-head CI, ownership and Universal Agent E2E after this final checkpoint commit.
- [ ] Merge only after final merge gates pass.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T09:20:00+02:00
head: c42b40c6583b60f315639147e2044f1772915b7c
branch: feat/e2e-gameplay-003-quentin-adventurer-stone
pr: 637
status: validating
context_routes:
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260720-e2e-gameplay-003-quentin-adventurer-stone.md
  - tests/e2e/scenarios/npc/quentin-adventurer-stone.json
  - tests/e2e/test_quentin_adventurer_stone.py
  - tools/e2e/client/quentin_adventurer_stone.lua
proven:
  - run 29805956537 loaded the observer and canonical driver, logged in twice and completed both safe logout cycles
  - retained evidence from run 29805956537 proved ordinary follow-up talk used MessageSay while focused NPC handling requires TALKTYPE_PRIVATE_PN
  - maintained OTClient exposes talkPrivate with MessageModes.NpcTo for player-to-NPC dialogue
  - the feature adapter sends adventurer stone only after the real Quentin greeting and yes only after the real free-stone offer
  - exact-head run 29808112467 passed controlled Canary build, controlled OTClient build and the physical Quentin scenario
  - run 29808112467 confirmed Quentin greeting, free-stone offer and reward response through g_game.onTalk
  - run 29808112467 completed safe logout, relog and second safe logout
  - run 29808112467 passed typed player_item_presence for inventory item 16277 after the complete lifecycle
derived:
  - response-gated feature-owned private NPC sends are sufficient for the bounded Quentin slice without adding a speculative shared action
  - the durable reward row proves the physical dialogue executed the intended server branch rather than only transporting client text
unknown:
  - exact-final-head CI, ownership and Universal Agent E2E outcomes after this checkpoint commit
conflicts: []
first_failure:
  marker: none
  evidence: no unresolved failure remains
rejected_hypotheses:
  - dialogue pacing alone
  - immediate generic inventory count as durable reward proof
  - observer loader failure after exact checkout source loading
  - persistence lifecycle failure
  - shared talk_npc action required for this bounded feature slice
changed_paths:
  - docs/agents/tasks/active/CAN-20260720-e2e-gameplay-003-quentin-adventurer-stone.md
  - tests/e2e/scenarios/npc/quentin-adventurer-stone.json
  - tests/e2e/test_quentin_adventurer_stone.py
  - tools/e2e/client/quentin_adventurer_stone.lua
validation:
  - command: CI and Agent Task Ownership on c42b40c6583b60f315639147e2044f1772915b7c
    result: PASS
    evidence: exact-head governance and CI passed
  - command: Universal Agent E2E run 29808112467
    result: PASS
    evidence: controlled builds and physical npc/quentin-adventurer-stone scenario passed
  - command: Required physical E2E job 88568533764
    result: PASS
    evidence: workflow accepted the retained physical evidence as complete
  - command: retained artifact universal-agent-e2e-npc-quentin-adventurer-stone from run 29808112467
    result: PASS
    evidence: response markers, two-session lifecycle and durable item 16277 assertion all passed
blockers: []
next_action: Verify exact-final-head CI, Agent Task Ownership and Universal Agent E2E after this checkpoint commit, then check reviews, threads, mergeability and live-main overlap before squash merge.
```
