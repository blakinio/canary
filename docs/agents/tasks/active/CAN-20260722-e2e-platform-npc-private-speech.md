---
task_id: CAN-20260722-e2e-platform-npc-private-speech
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-PLATFORM-NPC-PRIVATE-SPEECH
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/e2e-platform-npc-private-speech
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "9f8e736a62058eab6afced43c095edef7becc692"
risk: low
related_issue: ""
related_pr: "708"
depends_on:
  - Universal E2E physical evidence from PR #685 run 29872645552 artifact 8512445446
blocks:
  - CAN-20260721-e2e-gameplay-003-canary-promotion
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260722-e2e-platform-npc-private-speech.md
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/client/agent_e2e_scenario.lua
    - tests/e2e/test_npc_private_speech_action.py
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - docs/architecture/universal-e2e-gameplay-validation.md
    - data/npclib/npc_system/npc_handler.lua
    - data-canary/npc/canary.lua
modules_touched:
  - Universal E2E declarative scenario action contract
  - controlled OTClient generic gameplay-plan executor
reuses:
  - controlled OTClient Game::talkPrivate API
  - maintained OTClient MessageModes.NpcTo constant
  - existing scenario validation and Lua-plan rendering pipeline
public_interfaces:
  - Universal E2E scenario action talk_npc with receiver and text fields
cross_repo_tasks: []
---

# CAN-20260722 — Universal E2E generic NPC-private speech action

## Goal

Add one bounded generic Universal E2E scenario action that sends focused NPC follow-up speech through the controlled OTClient's existing NPC-private protocol path, without embedding feature-specific NPC names, keywords, timing, or assertions in the shared platform.

## Acceptance criteria

- [ ] Add one declarative `talk_npc` action with exactly `id`, `action`, `receiver`, and `text` fields.
- [ ] Validate `receiver` and `text` with the existing bounded safe-text contract and reject unknown fields.
- [ ] Execute the action through `g_game.talkPrivate(MessageModes.NpcTo, receiver, text)`; do not expose arbitrary protocol message modes through scenario data.
- [ ] Preserve existing public `talk` behavior unchanged.
- [ ] Add focused tests for accepted rendering, missing/unsafe fields, and the controlled-client execution contract.
- [ ] Document the stable action contract and register the reusable interface in the module catalogue.
- [ ] Do not modify feature-owned scenario files, NPC gameplay source, fixtures, persistence assertions, OTBM/maps, controlled OTClient source, or client assets.
- [ ] Pass ownership, focused validation, CI, and applicable Universal E2E gates before merge.
- [ ] Merge through the normal autonomous gate, then archive this task in a separate lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T07:13:00Z
head: 9f8e736a62058eab6afced43c095edef7becc692
branch: feat/e2e-platform-npc-private-speech
pr: 708
status: implementing
context_routes:
  - universal-e2e
  - agent-governance
  - cpp-runtime
owned_paths:
  - docs/agents/tasks/active/CAN-20260722-e2e-platform-npc-private-speech.md
  - tools/e2e/run_agent_e2e.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tests/e2e/test_npc_private_speech_action.py
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - docs/agents/MODULE_CATALOG.md
proven:
  - PR #685 physical artifact 8512445446 proves its current generic talk action sends focused follow-up NPC words as public MessageSay and the promotion does not occur.
  - controlled OTClient Game::talk always delegates to MessageSay, while Game::talkPrivate accepts an explicit message mode and receiver.
  - maintained OTClient console code uses MessageModes.NpcTo for player-to-NPC private speech.
  - Canary NpcHandler processes focused-player keywords only for TALKTYPE_PRIVATE_PN, so a generic NPC-private speech surface is required for real focused dialogue flows.
  - PR #708 is the draft platform PR for this bounded capability; its initial Agent Task Ownership run 29899291064 failed only because the new task record had empty related_pr while the current PR is 708.
  - CI run 29899291505 passed on the initial task-only head 9f8e736a62058eab6afced43c095edef7becc692.
derived:
  - the smallest reusable platform change is one fixed-purpose talk_npc action rather than a generic arbitrary-message-mode action.
unknown:
  - whether any ownership conflict remains after correcting related_pr to 708.
  - whether the first feature consumer needs additional bounded waits after switching to NPC-private speech; that remains feature-owned physical validation.
conflicts: []
first_failure:
  marker: PR #685 persistence_check_promoted-vocation failed actual=2 expected=12
  evidence: run 29872645552 artifact 8512445446 plus packet and source evidence isolated public MessageSay versus required focused NPC-private speech.
rejected_hypotheses:
  - PR #708 initial ownership failure proves a path conflict; ownership artifact 8521219893 reports only related_pr mismatch.
  - modify Canary NPC handling to accept focused public speech; that changes gameplay behavior instead of the E2E client interaction surface.
  - expose arbitrary message modes in scenario JSON; the required capability is narrower and can fail closed to NPC-private speech only.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-e2e-platform-npc-private-speech.md
validation:
  - command: Agent Task Ownership run 29899291064 on 9f8e736a62058eab6afced43c095edef7becc692
    result: FAIL
    evidence: artifact 8521219893 reports changed active task related_pr empty must match current PR 708; no path-overlap validation was reached.
  - command: CI run 29899291505 on 9f8e736a62058eab6afced43c095edef7becc692
    result: PASS
    evidence: task-only platform PR CI passed.
blockers: []
next_action: Verify Agent Task Ownership on the corrected PR #708 head, then implement the bounded talk_npc validator/runtime/test/documentation surface only if ownership is green.
```
