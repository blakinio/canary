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
last_verified_commit: "9ff0e5b7dbcb2c1e9ebab8c2960d2c9d6c88f58c"
risk: medium
related_issue: ""
related_pr: "477"
depends_on:
  - CAN-20260717-e2e-scenario-server-selection
blocks:
  - CAN-20260717-physical-movement-e2e
owned_paths:
  exclusive:
    - tools/e2e/pr_scenario_selection.py
    - tests/e2e/test_agent_e2e_pr_scenario_selection.py
    - docs/agents/tasks/active/CAN-20260717-e2e-pr-scenario-selection.md
  shared:
    - tools/e2e/run_agent_e2e.py
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  read_only:
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/client/agent_e2e_scenario.lua
    - tests/e2e/scenarios/**
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
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

# Acceptance criteria

- [x] Standard-library deterministic selector and focused tests.
- [x] Exactly one existing changed scenario selects its suite and declared manifest ID.
- [x] Zero, multiple, deleted-only and fork candidates preserve `login/relog`.
- [x] Explicit noncanonical dispatch inputs are never replaced.
- [x] `run_agent_e2e.py resolve` remains the validation boundary.
- [x] Existing workflow and physical runner remain unchanged.
- [x] Durable interface documentation updated in `PHYSICAL_GAMEPLAY_ACTION_PLANS.md`.
- [ ] Exact-final-head ownership, CI and Universal Agent E2E pass before merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T13:55:00+02:00
head: 0ce740075699a2bc7cf007a847e5567b33284467
branch: feat/e2e-pr-scenario-selection
pr: 477
status: implementing
context_routes:
  - universal-e2e
  - agent-governance
owned_paths:
  - tools/e2e/pr_scenario_selection.py
  - tests/e2e/test_agent_e2e_pr_scenario_selection.py
  - tools/e2e/run_agent_e2e.py
  - docs/agents/tasks/active/CAN-20260717-e2e-pr-scenario-selection.md
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
proven:
  - PR 468 merged and its lifecycle record is archived
  - PR 457 is owned by GPT-5.5 Thinking and awaits selected physical movement execution
  - selector uses exact local git delta with exact-SHA GitHub compare fallback for shallow PR checkout
  - resolver integration applies only to canonical login/relog on pull_request
  - current Universal Agent E2E workflow and physical runner have no diff in PR 477
  - CI run 29577724300 passed on 6ab0252424aa48580dda13c4f6bb4b4d5a97f918
  - Agent Task Ownership run 29577724191 passed on 6ab0252424aa48580dda13c4f6bb4b4d5a97f918
  - Universal Agent E2E run 29577724327 resolved successfully on the unchanged workflow
  - ownership run 29578116436 failed only because active task status was validating instead of implementing
derived:
  - resolver integration is narrower than changing the shared workflow and preserves explicit dispatch behavior
  - PR 477 changes no scenario manifest so its own physical E2E remains the canonical sentinel
unknown: []
conflicts: []
first_failure:
  marker: active-task-status-must-remain-implementing
  evidence: Agent Task Ownership run 29578116436 rejected non-active status validating under tasks/active; corrected here without implementation changes
rejected_hypotheses:
  - second E2E workflow
  - second physical runner
  - movement-specific branch special case
  - bypassing repository write guard
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-e2e-pr-scenario-selection.md
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - tests/e2e/test_agent_e2e_pr_scenario_selection.py
  - tools/e2e/pr_scenario_selection.py
  - tools/e2e/run_agent_e2e.py
validation:
  - command: CI run 29577724300
    result: PASS
    evidence: required CI passed on implementation/documentation head
  - command: Agent Task Ownership run 29577724191
    result: PASS
    evidence: ownership passed before final checkpoint
  - command: Universal Agent E2E run 29577724327 resolve job
    result: PASS
    evidence: unchanged workflow resolved through new resolver integration
  - command: Agent Task Ownership run 29578116436
    result: FAIL
    evidence: checkpoint status only; corrected in this commit
blockers: []
next_action: Treat this checkpoint-only commit as the new exact final head; require green ownership, full CI and Universal Agent E2E before squash merge.
```

## Automated lifecycle completion

- Feature PR: #477.
- Feature head: `7867621e94876f571738c7d1a09ebbdc7ddb52fd`.
- Merge commit: `9ff0e5b7dbcb2c1e9ebab8c2960d2c9d6c88f58c`.
- Merged at: `2026-07-17T12:59:53Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
