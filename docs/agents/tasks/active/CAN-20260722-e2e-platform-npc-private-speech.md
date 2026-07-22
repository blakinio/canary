---
task_id: CAN-20260722-e2e-platform-npc-private-speech
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-PLATFORM-NPC-PRIVATE-SPEECH
status: review
agent: "GPT-5.6 Thinking"
branch: feat/e2e-platform-npc-private-speech
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "5a5582d21fff2fc9bd96f88500fdfcea7501b2b0"
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
  shared:
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

- [x] Add one declarative `talk_npc` action with exactly `id`, `action`, `receiver`, and `text` fields.
- [x] Validate `receiver` and `text` with the existing bounded safe-text contract and reject unknown fields.
- [x] Execute the action through `g_game.talkPrivate(MessageModes.NpcTo, receiver, text)`; do not expose arbitrary protocol message modes through scenario data.
- [x] Preserve existing public `talk` behavior unchanged.
- [x] Add focused tests for accepted rendering, missing/unsafe fields, and the controlled-client execution contract.
- [x] Document the stable action contract and register the reusable interface in the module catalogue.
- [x] Do not modify feature-owned scenario files, NPC gameplay source, fixtures, persistence assertions, OTBM/maps, controlled OTClient source or client assets.
- [ ] Pass ownership, focused validation, CI and applicable Universal E2E gates on the exact final head before merge.
- [ ] Merge through the normal autonomous gate, then archive this task in a separate lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T07:34:00Z
head: 5a5582d21fff2fc9bd96f88500fdfcea7501b2b0
branch: feat/e2e-platform-npc-private-speech
pr: 708
status: validating
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
  - PR #708 implements one fixed-purpose talk_npc manifest action with exactly receiver and text in addition to id/action; both values use the existing bounded safe-text validator and unknown fields remain rejected.
  - the controlled-client executor handles talk_npc only through g_game.talkPrivate(MessageModes.NpcTo, step.receiver, step.text), while the existing talk branch continues to call g_game.talk(step.text).
  - focused tests cover accepted validation/Lua-plan rendering, missing and unsafe receiver rejection, arbitrary message-mode rejection, the fixed NpcTo runtime contract and preservation of public talk.
  - PHYSICAL_GAMEPLAY_ACTION_PLANS.md documents the stable bounded talk_npc contract and MODULE_CATALOG.md registers PR #708 without unrelated catalogue drift.
  - Agent Task Ownership run 29899797781 passed after correcting task metadata and checkpoint ownership syntax.
  - CI run 29900201989 passed on implementation head 9092e9ba9d7fda24c2dce4e80d7eaf36c5508ab3, but its incremental profile skipped Fast Checks and Lua Tests, so exact-final-head full validation remains required.
  - ci:final-gate was applied to PR #708 before this final checkpoint commit, per the repository final-head gate contract.
derived:
  - the smallest reusable platform change is one fixed-purpose talk_npc action rather than a generic arbitrary-message-mode action.
unknown:
  - whether exact-final-head full CI and Universal Agent E2E pass after the final checkpoint commit.
  - whether the first feature consumer needs additional bounded waits after switching to NPC-private speech; that remains feature-owned physical validation.
  - whether PR #685 promotion and both M3 persistence assertions pass after consuming talk_npc.
conflicts: []
first_failure:
  marker: PR #685 persistence_check_promoted-vocation failed actual=2 expected=12
  evidence: run 29872645552 artifact 8512445446 plus packet and source evidence isolated public MessageSay versus required focused NPC-private speech.
rejected_hypotheses:
  - PR #708 initial ownership failures prove a path conflict; both observed failures occurred in changed-task checkpoint validation before the global ownership-index step, and corrected ownership run 29899797781 passed.
  - modify Canary NPC handling to accept focused public speech; that changes gameplay behavior instead of the E2E client interaction surface.
  - expose arbitrary message modes in scenario JSON; the delivered talk_npc action fixes the protocol mode to MessageModes.NpcTo.
  - add only a longer bounded wait to PR #685; timing cannot change public MessageSay into required focused NPC-private speech.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-e2e-platform-npc-private-speech.md
  - tools/e2e/run_agent_e2e.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tests/e2e/test_npc_private_speech_action.py
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - docs/agents/MODULE_CATALOG.md
validation:
  - command: Agent Task Ownership run 29899291064 on 9f8e736a62058eab6afced43c095edef7becc692
    result: FAIL
    evidence: artifact 8521219893 reports changed active task related_pr empty must match current PR 708; no path-overlap validation was reached.
  - command: Agent Task Ownership run 29899663981 on 1ccbf5e5c561df29a7c50f77aa07ea16f18c2e90
    result: FAIL
    evidence: artifact 8521357280 reports invalid nested list item under checkpoint owned_paths; global ownership-index validation was skipped.
  - command: Agent Task Ownership run 29899797781 on 53ec4c30d29d00e7e0f5bdef467d0908f0390f93
    result: PASS
    evidence: corrected task metadata, categorized frontmatter ownership and flat checkpoint owned_paths passed the ownership gate.
  - command: CI run 29900201989 on 9092e9ba9d7fda24c2dce4e80d7eaf36c5508ab3
    result: PASS
    evidence: implementation-head incremental CI passed; full focused/final-head coverage remains pending because Fast Checks and Lua Tests were skipped by the incremental profile.
blockers: []
next_action: Validate PR #708 exact-final-head Agent Task Ownership, full CI and Universal Agent E2E; merge only if all required gates pass, then return to PR #685 to consume talk_npc.
```
