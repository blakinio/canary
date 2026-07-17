---
task_id: CAN-20260717-e2e-pr-scenario-selection
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-PR-SCENARIO-SELECTION-001
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-pr-scenario-selection
base_branch: main
created: 2026-07-17T13:15:00+02:00
updated: 2026-07-17T13:22:00+02:00
last_verified_commit: "f7f7c76da5e3593d797f3730f1fb48113403c06d"
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
    - .github/workflows/universal-agent-e2e.yml
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/e2e/run_agent_e2e.py
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
---

# Goal

Let a same-repository pull request changing exactly one existing E2E scenario manifest select that scenario in the existing Universal Agent E2E workflow. Preserve explicit workflow-dispatch inputs and canonical `login/relog` fallback. No second workflow or runner.

# Acceptance criteria

- [ ] Deterministic Python 3.12 standard-library selector.
- [ ] Same-repo PR with exactly one existing changed scenario selects its suite and declared scenario ID.
- [ ] Zero, multiple, deleted-only or fork-PR candidates fall back to `login/relog`.
- [ ] Explicit workflow-dispatch suite/scenario inputs remain unchanged.
- [ ] Existing `run_agent_e2e.py resolve` remains the validation boundary.
- [ ] Focused selector tests cover success and fail-closed/fallback cases.
- [ ] Existing Universal Agent E2E workflow remains the only physical lifecycle.
- [ ] Durable E2E docs/catalogue/changelog are updated narrowly.
- [ ] Exact-final-head ownership, CI and Universal Agent E2E pass before squash merge.

# Proven blocker

PR #457 owns only its movement scenario and cannot modify shared E2E platform paths. PR-triggered Universal Agent E2E currently resolves canonical `login/relog`; the current connector exposes no workflow-dispatch mutation. The E2E program requires a separate platform task for a reusable common-interface change.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T13:22:00+02:00
head: f7f7c76da5e3593d797f3730f1fb48113403c06d
branch: feat/e2e-pr-scenario-selection
pr: 477
status: implementing
context_routes:
  - universal-e2e
  - agent-governance
owned_paths:
  - tools/e2e/pr_scenario_selection.py
  - tests/e2e/test_agent_e2e_pr_scenario_selection.py
  - docs/agents/tasks/active/CAN-20260717-e2e-pr-scenario-selection.md
  - .github/workflows/universal-agent-e2e.yml
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - PR 468 merged and its lifecycle record is archived
  - PR 457 is owned by GPT-5.5 Thinking and is blocked on selected physical movement execution
  - E2E program requires shared platform changes to use a separate platform task
derived:
  - a single-existing-changed-manifest rule is deterministic and reusable while ambiguous cases can retain canonical fallback
unknown: []
conflicts: []
first_failure:
  marker: workflow-dispatch-surface-unavailable
  evidence: current connector supports workflow inspection and reruns but exposes no workflow-dispatch mutation
rejected_hypotheses:
  - second E2E workflow
  - second physical runner
  - movement-specific branch special case
  - modifying canonical login/relog scenario
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-e2e-pr-scenario-selection.md
validation: []
blockers: []
next_action: Implement the deterministic selector and integrate it into the existing Universal Agent E2E workflow.
```
