---
task_id: CAN-20260716-universal-e2e-gameplay-capabilities
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: "OTS-E2E-GAMEPLAY-V1"
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/universal-e2e-gameplay-capabilities
base_branch: main
created: 2026-07-16T21:30:00+02:00
updated: 2026-07-16T22:03:00+02:00
last_verified_commit: "65efa529803b85dafbf3a42d10fe7c0861662b3b"
risk: high
related_issue: ""
related_pr: "439"
depends_on:
  - CAN-PROGRAM-E2E-PLATFORM
blocks:
  - future physical movement scenario tasks
  - future physical combat scenario tasks
  - future physical item/inventory/container scenario tasks
  - future physical quest/NPC/depot/bank/trade scenario tasks
  - future multi-client and runtime-fault scenario tasks
owned_paths:
  exclusive:
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/client/agent_e2e_scenario.lua
    - tests/e2e/test_agent_e2e_scenario_plan.py
    - docs/agents/tasks/active/CAN-20260716-universal-e2e-gameplay-capabilities.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/client/agent_e2e.lua
    - tests/e2e/scenarios/**
modules_touched:
  - Universal OTS E2E automation
reuses:
  - existing scenario discovery and validation
  - existing physical Canary + MariaDB + controlled OTClient lifecycle
  - existing two-session login/logout/relog correctness sentinel
  - maintained OTClient g_game/g_map/LocalPlayer Lua bindings
public_interfaces:
  - optional scenario.steps declarative client action plan
  - generated scenario-plan.lua artifact
  - generic agent_e2e_scenario.lua physical client driver
cross_repo_tasks: []
---

# Goal

Extend the existing Universal OTS E2E platform with a reusable, declarative physical-client gameplay action plan without creating another orchestrator and without changing the active OAM-006 controlled-server workflow contract. The new platform layer must preserve the existing exact-head Canary/MariaDB/controlled-OTClient lifecycle and the two-session login/logout/relog persistence sentinel while adding reusable client actions and observations needed by movement, floor/teleport, combat, item/inventory/container, spell/chat, quest and NPC feature-owned scenarios.

# Acceptance criteria

- [ ] Preserve existing schema-v1 login/relog scenario behavior unchanged when `steps` is absent.
- [x] Add strict validation for optional declarative `steps` with bounded action types and exact required fields.
- [x] Reject unknown actions, unknown fields, unsafe text/newlines, invalid direction names, non-positive timing/count values and unbounded plans.
- [x] Resolve a validated action plan into a deterministic generated `scenario-plan.lua` beside the existing scenario manifest.
- [x] Add a generic OTClient Lua driver that uses only verified maintained-client bindings and always preserves two-session login/safe-logout/relog flow.
- [x] Support bounded generic actions for wait, directional walk, talk/spell text, attack-by-visible-name, inventory-item use, quest-log request and channel-list request.
- [x] Support bounded observations for online state, position change, floor change, health threshold, inventory count, visible-creature presence/absence and attack state.
- [x] Record every action start/result and observation as deterministic client event markers for existing required-marker assertions.
- [x] Fail closed on action timeout, missing local player/target/item, unexpected disconnect, login error or unknown runtime action.
- [x] Add focused Python tests for validation, deterministic Lua-plan generation, escaping and backward compatibility.
- [x] Do not modify `.github/workflows/universal-agent-e2e.yml` while OAM-006 PR #436 shares that path.
- [x] Do not add guessed feature-specific coordinates, item IDs, NPC names, monster names or gameplay expectations to the platform task.
- [x] Document that multi-client orchestration, forced TCP reconnect, server restart/crash recovery and concrete feature scenarios remain separate child tasks because they require shared runner/workflow or feature-owned fixtures.
- [ ] Pass exact-head relevant CI and E2E-platform validation before merge.

# Confirmed context

- Writable repository is exactly `blakinio/canary`; upstream and donor repositories remain read-only.
- Task-start main is `6503f5312dbf13d0fddcc1da98a10343ed30525c`.
- Universal Agent E2E already builds exact Canary head, controlled pinned OTClient, MariaDB 11.4 and executes a real two-session physical login/logout/relog scenario.
- OAM-006 PR #436 currently shares `.github/workflows/universal-agent-e2e.yml` and adds controlled server repository/ref inputs; this task treats that workflow as read-only to avoid ownership conflict.
- Maintained OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f` exposes verified bindings used by this task: `g_game.walk`, `g_game.talk`, `g_game.attack`, `g_game.useInventoryItem`, `g_game.requestQuestLog`, `g_game.requestChannels`, `g_game.getLocalPlayer`, `g_game.getAttackingCreature`, `g_map.getSpectators`, and LocalPlayer position/health/inventory accessors.
- Draft PR #439 is the live platform PR for this task.
- CI #2880 passed on implementation head `65efa529803b85dafbf3a42d10fe7c0861662b3b`; Ownership #1739 failed only because the checkpoint encoded `conflicts` as a map instead of the required scalar-list contract.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T22:03:00+02:00
head: 65efa529803b85dafbf3a42d10fe7c0861662b3b
branch: feat/universal-e2e-gameplay-capabilities
pr: 439
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - tools/e2e/run_agent_e2e.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tests/e2e/test_agent_e2e_scenario_plan.py
  - docs/agents/tasks/active/CAN-20260716-universal-e2e-gameplay-capabilities.md
proven:
  - repository write target is exactly blakinio/canary
  - task-start main is 6503f5312dbf13d0fddcc1da98a10343ed30525c
  - existing physical E2E owns disposable MariaDB, exact Canary, controlled OTClient, assets, Xvfb, evidence and cleanup
  - existing physical result gate requires two server logins, two packet records and persisted lastlogin/lastlogout
  - OAM-006 PR 436 shares universal-agent-e2e.yml and must not be overwritten
  - maintained OTClient bindings required for the bounded generic actions were verified at pinned ref 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
  - focused scenario-plan unit tests pass 8 of 8 and Python bytecode compilation passes
  - CI 2880 completed successfully on implementation head 65efa529803b85dafbf3a42d10fe7c0861662b3b
derived:
  - the safest non-overlapping next slice is a generic declarative action-plan compiler plus a new client automation driver
  - concrete gameplay scenarios need feature-owned deterministic fixtures rather than invented coordinates or IDs
unknown:
  - exact first deterministic movement/combat/item fixture coordinates and actors
  - final OAM-006 workflow merge SHA
conflicts:
  - PR 436 owns shared workflow .github/workflows/universal-agent-e2e.yml; this task keeps that path read-only
first_failure:
  marker: Agent Task Ownership 1739 / Validate changed active task checkpoints
  evidence: checkpoint parser rejected a mapping-style conflicts entry; implementation CI was green and the checkpoint is corrected to a scalar list
rejected_hypotheses:
  - one giant feature scenario PR should invent coordinates and item/monster/NPC identifiers
  - a second physical-client orchestrator is needed
  - OAM-006 workflow changes may be overwritten by this task
changed_paths:
  - docs/agents/tasks/active/CAN-20260716-universal-e2e-gameplay-capabilities.md
  - tools/e2e/run_agent_e2e.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tests/e2e/test_agent_e2e_scenario_plan.py
validation:
  - command: python -m py_compile tools/e2e/run_agent_e2e.py tests/e2e/test_agent_e2e_scenario_plan.py
    result: PASS
    evidence: local bytecode compilation completed successfully
  - command: python -m unittest -v tests/e2e/test_agent_e2e_scenario_plan.py
    result: PASS
    evidence: 8 focused scenario validation and deterministic plan-generation tests passed
  - command: CI 2880
    result: PASS
    evidence: repository CI completed successfully on 65efa529803b85dafbf3a42d10fe7c0861662b3b
  - command: Agent Task Ownership 1739
    result: FAIL
    evidence: checkpoint conflicts field used mapping syntax unsupported by the compact checkpoint parser; corrected in the next task-record commit
blockers: []
next_action: Verify the corrected ownership checkpoint and current Universal Agent E2E run, then close the runtime evidence hash gap by making the physical runner hash the scenario-selected automation without modifying the OAM-006 shared workflow.
```
