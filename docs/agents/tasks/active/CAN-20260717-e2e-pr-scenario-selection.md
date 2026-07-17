---
task_id: CAN-20260717-e2e-pr-scenario-selection
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-PR-SCENARIO-SELECTION-001
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-pr-scenario-selection
base_branch: main
created: 2026-07-17T13:15:00+02:00
updated: 2026-07-17T13:15:00+02:00
last_verified_commit: "be7f50d484d8f988db4b3dafff195b027c6a9fb7"
risk: medium
related_issue: ""
related_pr: ""
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
  - existing pull-request exact-head checkout and physical lifecycle
public_interfaces:
  - deterministic same-repository PR selection of exactly one changed scenario manifest
cross_repo_tasks: []
---

# Goal

Add the smallest reusable Universal OTS E2E platform capability that lets a same-repository pull request changing exactly one scenario manifest physically validate that changed scenario automatically. Preserve explicit `workflow_dispatch` suite/scenario inputs and the canonical `login/relog` fallback. Do not create a second workflow or runner.

# Acceptance criteria

- [ ] Add one deterministic Python 3.12 standard-library selector for PR scenario selection; do not duplicate scenario execution or validation.
- [ ] On same-repository `pull_request`, select the suite directory and declared scenario `id` only when exactly one existing `tests/e2e/scenarios/<suite>/*.json` manifest changed between the exact base and head SHAs.
- [ ] Fall back to canonical `login/relog` for zero changed manifests, multiple changed manifests, deleted-only manifests, fork pull requests, or non-PR events without explicit dispatch inputs.
- [ ] Preserve explicit `workflow_dispatch` suite/scenario inputs unchanged.
- [ ] Keep the existing Universal Agent E2E workflow and physical runner as the only lifecycle/orchestrator.
- [ ] Feed the selected values through the existing `run_agent_e2e.py resolve` validation boundary before any physical runtime.
- [ ] Add focused tests for one-manifest selection, manifest `id` resolution, zero/multiple/deleted changes, invalid JSON/id, fork PR fallback, and workflow-dispatch preservation.
- [ ] Ensure selector/helper changes trigger the existing Universal Agent E2E workflow.
- [ ] Update durable E2E documentation/catalogue/changelog narrowly for the reusable interface.
- [ ] Pass exact-final-head ownership, CI and Universal Agent E2E, then squash merge and archive separately.

# Proven blocker

- Feature-owned physical scenario PR #457 changes exactly one deterministic movement manifest, but PR-triggered Universal Agent E2E currently hardcodes the fallback `login/relog` through `${{ inputs.suite || 'login' }}` / `${{ inputs.scenario || 'relog' }}`.
- The existing platform supports explicit `workflow_dispatch`, but this agent execution surface exposes no authenticated workflow-dispatch mutation.
- Per `CAN-PROGRAM-E2E-PLATFORM`, a feature task must keep shared platform paths read-only and a separate platform task must own a required common-interface change.
- Automatic single-changed-manifest selection is a reusable PR-validation capability, not movement-specific orchestration; ambiguous or unsafe cases remain on the canonical sentinel.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T13:15:00+02:00
head: be7f50d484d8f988db4b3dafff195b027c6a9fb7
branch: feat/e2e-pr-scenario-selection
pr: pending
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
  - PR 468 merged and its lifecycle task is archived; scenario.server datapack/map selection is now available on main
  - PR 457 is owned by GPT-5.5 Thinking and remains blocked only on physically executing its selected movement scenario
  - current PR-triggered Universal Agent E2E resolves login/relog regardless of a single changed feature scenario
  - E2E program interface-change rule requires this shared capability to be owned by a separate platform task
derived:
  - selecting exactly one existing changed scenario manifest on same-repository PRs is the narrowest reusable automatic validation rule that remains deterministic and fails back to the canonical sentinel when ambiguous
unknown: []
conflicts: []
first_failure:
  marker: workflow-dispatch-surface-unavailable
  evidence: current GitHub connector exposes workflow run inspection and rerun actions but no workflow_dispatch mutation; feature task explicitly rejects changing shared workflow solely inside the feature branch
rejected_hypotheses:
  - second E2E workflow
  - second physical runner
  - movement-specific branch-name special case
  - modifying canonical login/relog scenario
  - inferring physical movement success from static OTBM evidence
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-e2e-pr-scenario-selection.md
validation: []
blockers: []
next_action: Open an early draft PR, bind this task record to it, then implement and test the deterministic single-changed-scenario selector through the existing Universal Agent E2E workflow.
```
