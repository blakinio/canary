---
task_id: CAN-20260717-e2e-pr-scenario-selection
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-PR-SCENARIO-SELECTION-001
status: completed
agent: "GPT-5.5 Thinking"
branch: feat/e2e-pr-scenario-selection
base_branch: main
created: 2026-07-17T13:15:00+02:00
updated: 2026-07-17T12:59:53Z
last_verified_commit: "7867621e94876f571738c7d1a09ebbdc7ddb52fd"
risk: medium
related_issue: ""
related_pr: "477"
depends_on:
  - CAN-20260717-e2e-scenario-server-selection
blocks: []
owned_paths:
  exclusive:
    - tools/e2e/pr_scenario_selection.py
    - tests/e2e/test_agent_e2e_pr_scenario_selection.py
    - docs/agents/tasks/archive/CAN-20260717-e2e-pr-scenario-selection.md
  shared:
    - tools/e2e/run_agent_e2e.py
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  read_only:
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/client/agent_e2e_scenario.lua
    - tests/e2e/scenarios/**
modules_touched:
  - Universal OTS E2E pull-request scenario selection
reuses:
  - existing Universal Agent E2E workflow
  - existing scenario manifest resolver and validator
public_interfaces:
  - deterministic same-repository PR selection of exactly one changed scenario manifest
cross_repo_tasks: []
completed: 2026-07-17T12:59:53Z
---

# Goal

Select exactly one changed existing E2E scenario for same-repository pull requests through the existing Universal Agent E2E resolver, preserving explicit dispatch inputs and canonical `login/relog` fallback.

# Completed scope

- Added a deterministic standard-library selector with focused tests.
- Exactly one existing changed scenario selects its suite and declared manifest ID.
- Zero, multiple, deleted-only and fork candidates preserve `login/relog`.
- Explicit noncanonical dispatch inputs are never replaced.
- `run_agent_e2e.py resolve` remains the validation boundary.
- The existing workflow and physical runner remain unchanged.
- Durable interface documentation was updated.

# Completion evidence

- Feature PR: #477 `feat(e2e): select single changed scenario on same-repo PRs`.
- Exact final feature head: `7867621e94876f571738c7d1a09ebbdc7ddb52fd`.
- Agent Task Ownership run `29578297613`: success.
- Universal Agent E2E run `29578297767`: success.
- Full final-gate CI run `29580905802`: success after retrying failed jobs on the unchanged exact final head.
- Squash merge commit: `9ff0e5b7dbcb2c1e9ebab8c2960d2c9d6c88f58c`.
- Merged at: `2026-07-17T12:59:53Z`.
- No scenario manifest, map, binary asset, credential, second workflow, or second orchestrator was added.

# Lifecycle note

Automated archive PR #479 was closed without merge because its recursive token-created PR runs remained `action_required` and did not provide the required `Required` check. This manual lifecycle PR uses normal branch protection and does not bypass checks.

# Follow-up

None. The separate physical movement experiment was closed without merge and archived independently because it lacked selected physical-client movement evidence.
