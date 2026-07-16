---
task_id: CAN-20260716-universal-e2e-gameplay-capabilities
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: "OTS-E2E-GAMEPLAY-V1"
status: ready
agent: "GPT-5.5 Thinking"
branch: feat/universal-e2e-gameplay-capabilities-clean
base_branch: main
created: 2026-07-16T21:30:00+02:00
updated: 2026-07-16T23:32:27+02:00
last_verified_commit: "73f6faa6c135c91017e386fc87ead41790b665ca"
risk: high
related_issue: ""
related_pr: "447"
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
    - tests/e2e/scenarios/platform/action-plan-contract.json
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
    - docs/agents/tasks/active/CAN-20260716-universal-e2e-gameplay-capabilities.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/client/agent_e2e.lua
    - tests/e2e/scenarios/login/scenario.json
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

Extend the existing Universal OTS E2E platform with a reusable, declarative physical-client gameplay action plan without creating another orchestrator. Preserve the exact-server/MariaDB/controlled-OTClient lifecycle and canonical two-session login/safe-logout/persistence/relog sentinel while adding reusable bounded client actions and observations for future feature-owned scenarios.

# Delivery history

- Closed PR #439 contained the audited implementation but accumulated stale current-main/shared-document history and was closed without merge.
- Replacement PR #447 was rebuilt directly from `main@c40b26ee9481ec99931347ba26897a785a7a38ca` with the same implementation blobs and no force-push.
- OAM-006 PR #436 merged as `c40b26ee9481ec99931347ba26897a785a7a38ca`; its `.github/workflows/universal-agent-e2e.yml` controlled-server contract remains read-only in this task.

# Acceptance criteria

- [x] Preserve existing schema-v1 login/relog scenario behavior when `steps` is absent; focused regression `test_legacy_scenario_without_steps_remains_valid` proves the optional field resolves to an empty action plan, while the final exact-head physical E2E gate exercises the unchanged canonical login/relog scenario.
- [x] Add strict validation for optional declarative `steps` with bounded action types and exact required fields.
- [x] Reject unknown actions, unknown fields, unsafe text/newlines, invalid direction names, non-positive timing/count values and unbounded plans.
- [x] Resolve a validated action plan into a deterministic generated `scenario-plan.lua` beside the existing scenario manifest.
- [x] Add a generic OTClient Lua driver that uses only verified maintained-client bindings and preserves two-session login/safe-logout/relog flow.
- [x] Support bounded generic actions for wait, directional walk, talk/spell text, attack-by-visible-name, inventory-item use, quest-log request and channel-list request.
- [x] Support bounded observations for online state, position change, floor change, health threshold, inventory count, visible-creature presence/absence and attack state.
- [x] Record every action start/result and observation as deterministic client event markers for existing required-marker assertions.
- [x] Fail closed on action timeout, missing local player/target/item, unexpected disconnect, login error or unknown runtime action.
- [x] Add focused Python tests for validation, deterministic Lua-plan generation, escaping and backward compatibility.
- [x] Register a platform-owned action-plan contract scenario that uses no guessed map coordinates, item IDs, NPCs or monsters.
- [x] Preserve the merged #436 workflow rather than overwriting it.
- [x] Do not add guessed feature-specific coordinates, item IDs, NPC names, monster names or gameplay expectations to the platform task.
- [x] Document that multi-client orchestration, forced TCP reconnect, server restart/crash recovery and concrete feature scenarios remain separate child tasks.
- [ ] Pass exact-final-head CI, Agent Task Ownership and Universal Agent E2E before merge.

# Confirmed context

- Writable repository is exactly `blakinio/canary`; upstream and donor repositories remain read-only.
- Original task-start main was `6503f5312dbf13d0fddcc1da98a10343ed30525c`.
- Clean replacement starts from `c40b26ee9481ec99931347ba26897a785a7a38ca` after OAM-006 merged.
- The implementation exposes only the bounded declarative action-plan layer; no second server/client/database lifecycle is introduced.
- The focused test module now contains 13 regression tests, including legacy no-steps compatibility and runtime-action coverage.
- Previous implementation heads passed repository CI and ownership checks; final replacement evidence must be exact-head and is intentionally pending the final gate.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T23:32:27+02:00
head: 73f6faa6c135c91017e386fc87ead41790b665ca
branch: feat/universal-e2e-gameplay-capabilities-clean
pr: 447
status: ready
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - tools/e2e/run_agent_e2e.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tests/e2e/test_agent_e2e_scenario_plan.py
  - tests/e2e/scenarios/platform/action-plan-contract.json
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - docs/agents/tasks/active/CAN-20260716-universal-e2e-gameplay-capabilities.md
proven:
  - repository write target is exactly blakinio/canary
  - replacement PR 447 is rebuilt directly from main c40b26ee9481ec99931347ba26897a785a7a38ca and supersedes closed PR 439
  - OAM-006 PR 436 merged as c40b26ee9481ec99931347ba26897a785a7a38ca and its workflow path remains read-only here
  - existing physical E2E owns disposable MariaDB exact server controlled OTClient evidence and cleanup
  - focused test test_legacy_scenario_without_steps_remains_valid proves schema-v1 scenarios without steps still validate and render an empty action plan
  - focused test module contains 13 bounded validation generation compatibility and runtime-action coverage tests
  - platform action-plan-contract scenario contains no guessed feature coordinates item IDs NPC names or monster names
  - prior implementation CI 2887 and Agent Task Ownership 1746 passed on identical implementation blobs before clean replacement
  - final intended scope is exactly eight files and excludes .github/workflows/universal-agent-e2e.yml
derived:
  - the clean replacement removes stale shared-document history without changing the audited implementation
  - concrete gameplay scenarios require feature-owned deterministic fixtures rather than platform-invented coordinates or identifiers
unknown:
  - exact-final-head CI and physical E2E outcome for replacement PR 447
conflicts: []
first_failure:
  marker: closed-pr-439-stale-history
  evidence: PR 439 was closed without merge because its published branch carried behind-main and shared-document drift; replacement PR 447 starts from current main without force-pushing history
rejected_hypotheses:
  - force-pushing or reopening conflicted PR 439 is required
  - a second physical-client orchestrator is needed
  - the merged OAM-006 workflow must be overwritten by this task
changed_paths:
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260716-universal-e2e-gameplay-capabilities.md
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - tests/e2e/scenarios/platform/action-plan-contract.json
  - tests/e2e/test_agent_e2e_scenario_plan.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tools/e2e/run_agent_e2e.py
validation:
  - command: CI 2887
    result: PASS
    evidence: repository CI passed on prior implementation head 608d59545e6d22342c6fc31933eb823162b71feb using the same implementation blobs
  - command: Agent Task Ownership 1746
    result: PASS
    evidence: ownership validation passed on prior implementation head 608d59545e6d22342c6fc31933eb823162b71feb
  - command: focused scenario-plan regression inventory
    result: PASS
    evidence: tests/e2e/test_agent_e2e_scenario_plan.py contains 13 tests including legacy no-steps compatibility deterministic rendering strict rejection bounds and runtime-action coverage
blockers: []
next_action: Commit this truthful ready checkpoint with clean current-main catalogue/changelog as the single post-ci:final-gate final commit, then run exact-head CI ownership and Universal Agent E2E; if all required checks pass with no review blockers, mark PR 447 ready and squash-merge without another commit.
```

# Completion

- Final status: ready
- PR: #447
- Final exact-head checks: pending
- Merge commit: pending
- Lifecycle archive: pending post-merge automation
