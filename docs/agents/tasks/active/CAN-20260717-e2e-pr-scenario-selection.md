---
task_id: CAN-20260717-e2e-pr-scenario-selection
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-PR-SCENARIO-SELECTION-001
status: validating
agent: "GPT-5.5 Thinking"
branch: feat/e2e-pr-scenario-selection
base_branch: main
created: 2026-07-17T13:15:00+02:00
updated: 2026-07-17T13:48:00+02:00
last_verified_commit: "6ab0252424aa48580dda13c4f6bb4b4d5a97f918"
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
---

# Goal

Let a same-repository pull request changing exactly one existing E2E scenario manifest select that scenario through the existing Universal Agent E2E resolver. Preserve explicit workflow-dispatch inputs and canonical `login/relog` fallback. No second workflow or runner.

# Acceptance criteria

- [x] Deterministic Python 3.12 standard-library selector.
- [x] Same-repo PR with exactly one existing changed scenario selects its suite and declared scenario ID.
- [x] Zero, multiple, deleted-only or fork-PR candidates fall back to `login/relog`.
- [x] Explicit workflow-dispatch suite/scenario inputs remain unchanged.
- [x] Existing `run_agent_e2e.py resolve` remains the validation boundary and integrates the selector only for the canonical PR fallback pair.
- [x] Focused selector tests cover success, shallow-checkout API fallback and fail-closed/fallback cases.
- [x] Existing Universal Agent E2E workflow and physical runner remain unchanged.
- [x] Durable E2E interface documentation is updated in `docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md`; full-file writes to shared catalogue/changelog were rejected by the repository write guard and were not forced or bypassed. The existing Universal E2E module catalogue entry remains present on `main`.
- [ ] Exact-final-head ownership, CI and Universal Agent E2E pass before squash merge.

# Proven blocker

PR #457 owns only its movement scenario and cannot modify shared E2E platform paths. PR-triggered Universal Agent E2E passes canonical `login/relog` to the resolver; the current connector exposes no workflow-dispatch mutation. The E2E program requires a separate platform task for a reusable common-interface change. The workflow itself remains read-only after the repository write guard rejected that shared-workflow mutation; the stable resolver is the narrower approved integration point.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T13:48:00+02:00
head: 6ab0252424aa48580dda13c4f6bb4b4d5a97f918
branch: feat/e2e-pr-scenario-selection
pr: 477
status: validating
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
  - PR 457 is owned by GPT-5.5 Thinking and is blocked on selected physical movement execution
  - E2E program requires shared platform changes to use a separate platform task
  - selector uses exact local git delta first and GitHub exact-SHA compare fallback for shallow PR checkout
  - resolver integration runs only for canonical login/relog on pull_request and preserves explicit noncanonical selections
  - zero multiple deleted-only and fork candidates preserve canonical fallback
  - invalid unique manifest or unverifiable exact same-repo delta fails closed
  - current Universal Agent E2E workflow and physical runner have no diff in PR 477
  - CI run 29577724300 passed on implementation/documentation head 6ab0252424aa48580dda13c4f6bb4b4d5a97f918
  - Agent Task Ownership run 29577724191 passed on implementation/documentation head 6ab0252424aa48580dda13c4f6bb4b4d5a97f918
  - Universal Agent E2E run 29577724327 resolved the scenario successfully on the unchanged workflow and is the pre-final physical validation run
  - repository write guard rejected direct Universal Agent E2E workflow mutation and later shared MODULE_CATALOG full-file mutation; neither was forced or bypassed
derived:
  - integrating selection inside the existing resolver only when it receives canonical PR fallback values is narrower than changing shared workflow behavior and preserves workflow-dispatch inputs
  - PR 477 itself changes no scenario manifest so its physical E2E remains the canonical login/relog sentinel
unknown: []
conflicts: []
first_failure:
  marker: shared-file-write-guard-rejected
  evidence: direct full-file Universal Agent E2E workflow update and later full-file MODULE_CATALOG update were rejected by the repository write safety guard; no rejected mutation was committed or bypassed
rejected_hypotheses:
  - second E2E workflow
  - second physical runner
  - movement-specific branch special case
  - modifying canonical login/relog scenario
  - bypassing repository write guard with low-level Git object mutation
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-e2e-pr-scenario-selection.md
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - tests/e2e/test_agent_e2e_pr_scenario_selection.py
  - tools/e2e/pr_scenario_selection.py
  - tools/e2e/run_agent_e2e.py
validation:
  - command: CI run 29577724300
    result: PASS
    evidence: required CI passed on implementation/documentation head 6ab0252424aa48580dda13c4f6bb4b4d5a97f918
  - command: Agent Task Ownership run 29577724191
    result: PASS
    evidence: task ownership and checkpoint validation passed on implementation/documentation head 6ab0252424aa48580dda13c4f6bb4b4d5a97f918
  - command: Universal Agent E2E run 29577724327 resolve job
    result: PASS
    evidence: existing unchanged workflow resolved canonical PR fallback successfully through the new resolver integration
blockers: []
next_action: Freeze this checkpoint commit as the exact final head, run all ci:final-gate checks including full Universal Agent E2E, make no post-green commits, then mark PR 477 ready and squash merge only if the exact head remains unchanged and green.
```
