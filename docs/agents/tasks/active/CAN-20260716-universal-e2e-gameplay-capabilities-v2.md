---
task_id: CAN-20260716-universal-e2e-gameplay-capabilities-v2
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: "OTS-E2E-GAMEPLAY-V1"
status: ready
agent: "GPT-5.5 Thinking"
branch: feat/universal-e2e-gameplay-capabilities-v3
base_branch: main
created: 2026-07-16T22:30:00+02:00
updated: 2026-07-16T23:47:48+02:00
last_verified_commit: "207a89455e0ce8f2b60631c5678074d6bf19c705"
risk: high
related_issue: ""
related_pr: "446"
depends_on:
  - CAN-PROGRAM-E2E-PLATFORM
blocks:
  - future physical gameplay fixture scenarios
  - future multi-client scenarios
  - future runtime-fault scenarios
owned_paths:
  exclusive:
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/client/agent_e2e_scenario.lua
    - tests/e2e/test_agent_e2e_scenario_plan.py
    - tests/e2e/scenarios/platform/action-plan-contract.json
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
    - docs/agents/tasks/active/CAN-20260716-universal-e2e-gameplay-capabilities-v2.md
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
  - existing physical Canary MariaDB controlled-OTClient lifecycle
  - existing two-session login logout relog sentinel
public_interfaces:
  - optional scenario.steps action plan
  - generated scenario-plan.lua
  - generic agent_e2e_scenario.lua driver
cross_repo_tasks: []
---

# Goal

Add bounded declarative physical-client gameplay actions to the existing Universal OTS E2E platform without creating another orchestrator or modifying the shared OAM-006 workflow contract.

# Delivered

- Backward-compatible scenarios with no `steps` remain supported.
- Strict bounded step validation and deterministic `scenario-plan.lua` generation are implemented.
- The controlled OTClient driver supports bounded wait, movement, text, visible-target combat selection, inventory-item use, quest/channel requests and state observations.
- Unknown or invalid actions fail closed.
- Focused regressions include declared-action to runtime-driver parity.
- The platform contract scenario contains no invented map coordinates, item IDs, NPC names or monster names.
- Existing MariaDB, exact Canary, controlled OTClient and two-session relog lifecycle remains authoritative.
- Shared workflow and legacy physical runner paths remain read-only in this task.
- PR #446 contains exactly eight intended changed files; CHANGELOG and MODULE_CATALOG each add one E2E entry.
- The branch is synchronized through Canary main `b0ea0ba9508cc78d5580f44181115e9b304eb7da`.

# Validation before final gate

- Agent Task Ownership #1803: PASS on `9a847007576efc0ca9c1b32be67624d12c483012`.
- CI #2946: PASS on `9a847007576efc0ca9c1b32be67624d12c483012`.
- Universal Agent E2E #131 selected the full heavy path, passed scenario resolution and database bootstrap, and started exact Canary plus controlled OTClient builds before the final-head transition.
- `ci:final-gate` is applied to PR #446.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T23:47:48+02:00
head: 207a89455e0ce8f2b60631c5678074d6bf19c705
branch: feat/universal-e2e-gameplay-capabilities-v3
pr: 446
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
  - docs/agents/tasks/active/CAN-20260716-universal-e2e-gameplay-capabilities-v2.md
proven:
  - PR 446 supersedes closed unmerged PR 439 without rewriting published history
  - implementation blobs were transferred byte-for-byte from the audited draft
  - branch is synchronized with main b0ea0ba9508cc78d5580f44181115e9b304eb7da
  - changed-path scope is exactly eight intended files
  - CHANGELOG and MODULE_CATALOG each contain only one intended E2E addition
  - pre-final Ownership 1803 and CI 2946 passed
  - pre-final Universal Agent E2E 131 selected the full heavy path
unknown:
  - exact-final-head gate conclusion
conflicts: []
first_failure:
  marker: superseded-pr-439-mergeability
  evidence: replacement PR 446 was created from current main instead of rewriting published history
rejected_hypotheses:
  - create a second E2E orchestrator
  - invent feature-specific fixture identifiers in the platform contract
changed_paths:
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260716-universal-e2e-gameplay-capabilities-v2.md
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - tests/e2e/scenarios/platform/action-plan-contract.json
  - tests/e2e/test_agent_e2e_scenario_plan.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tools/e2e/run_agent_e2e.py
validation:
  - command: Agent Task Ownership 1803
    result: PASS
  - command: CI 2946
    result: PASS
blockers: []
next_action: Let all ci:final-gate workflows finish on this exact final head. If they succeed, make no further commit; audit reviews, threads, changed paths and mergeability, mark PR 446 ready, then squash-merge with the exact expected head SHA.
```
