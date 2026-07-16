---
task_id: CAN-20260716-incremental-ci-final-gate
program_id: ""
coordination_id: ""
status: active
agent: chatgpt-ci-governance
branch: ci/incremental-validation-final-gate
base_branch: main
created: 2026-07-16T10:10:00+02:00
updated: 2026-07-16T10:10:00+02:00
last_verified_commit: 2f828672df010ff577c8e6076524b37c6dedd987
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260715-universal-agent-load-platform
blocks: []
owned_paths:
  exclusive:
    - .github/workflows/ci.yml
    - .github/workflows/universal-agent-e2e.yml
    - .github/workflows/universal-agent-load.yml
    - tools/agents/ci_incremental_validation.py
    - tests/agents/test_ci_incremental_validation.py
    - docs/agents/tasks/active/CAN-20260716-incremental-ci-final-gate.md
  shared:
    - AGENTS.md
    - docs/agents/BUILD_TEST_MATRIX.md
  read_only: []
modules_touched:
  - CI validation orchestration
  - Universal Agent E2E workflow gating
  - Universal Agent Load workflow gating
reuses:
  - existing CI Detect Build Scope and Required aggregation
  - existing workflow_dispatch full validation paths
  - existing Universal Agent E2E physical login/relog sentinel
  - existing Universal Agent Load exact-head status-smoke sentinel
public_interfaces:
  - ci:final-gate pull-request label convention
  - ci_incremental_validation.py decision contract
cross_repo_tasks: []
---

# Goal

Reduce repeated heavy CI after non-impacting follow-up commits without reducing merge quality: reuse a successful parent workflow only for a proven non-impacting single-commit delta, fail closed otherwise, and force the full applicable validation set once on the final PR head before merge.

# Acceptance criteria

- [ ] A tested standard-library helper classifies whether the current single-commit delta affects CI, physical E2E, or load validation.
- [ ] Parent reuse is allowed only when the latest same-workflow pull-request run on `HEAD^` completed successfully.
- [ ] Missing parent evidence, a failed/in-progress latest parent run, workflow changes, or an impacting delta fail closed to heavy validation.
- [ ] `ci:final-gate` forces the full applicable workflow on the current head and bypasses incremental reuse.
- [ ] CI no longer performs Linux compilation for documentation-only PR scope.
- [ ] Universal Agent E2E no longer triggers for load-only `tests/e2e/load/**` or `tests/e2e/test_load_runner.py` changes.
- [ ] Load and physical E2E can reuse proven parent success for non-impacting follow-up commits but still run on final-gate label events.
- [ ] Agent policy batches checkpoint/docs mutations before final-gate validation and forbids a post-green checkpoint commit that would invalidate the final head.
- [ ] Focused helper tests and exact workflow checks pass.
- [ ] No branch-protection, test, assertion, throttle, or safety gate is weakened.

# Confirmed context

- Repository write target is exactly `blakinio/canary`.
- PR #393 merged successfully as squash commit `2f828672df010ff577c8e6076524b37c6dedd987` before this task branch was created.
- Current `main` equaled `2f828672df010ff577c8e6076524b37c6dedd987` when this branch was created.
- The motivating waste was observed directly: docs/shared-index commits after green runtime heads repeatedly rebuilt Canary and the unchanged controlled OTClient before merge.
- Existing root policy already says to avoid wasteful builds for clearly non-build-affecting docs/scripts; this task makes workflow behavior match that policy.
- Current CI uses cumulative PR path filtering and forces Linux release for every pull request, so a docs-only follow-up on a code PR repeats heavy work.
- Current Universal Agent E2E uses broad `tests/e2e/**`, causing load-only test paths to trigger physical-client E2E.

# Safety design

The optimization is evidence-preserving, not skip-by-assumption:

1. On a `synchronize` event, inspect only `HEAD^..HEAD`.
2. Reuse is possible only if that delta is non-impacting for the workflow.
3. Query the parent SHA's latest same-name `pull_request` workflow run; require `completed/success`.
4. If multiple commits were pushed at once, `HEAD^` normally has no workflow evidence, so the decision fails closed and heavy validation runs.
5. Any relevant workflow/helper path change is itself impacting and forces heavy validation.
6. Before merge, a `ci:final-gate` label event forces the full applicable workflow set on the current head regardless of reusable parent evidence.
7. Any commit after the final-gate run changes the head and requires the final-gate label to be triggered again.

# Current state

Task claimed; no implementation files changed yet.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T10:10:00+02:00
head: 2f828672df010ff577c8e6076524b37c6dedd987
branch: ci/incremental-validation-final-gate
pr: null
status: active
context_routes:
  - agent-governance
  - universal-e2e
  - ci-repair
owned_paths:
  - .github/workflows/ci.yml
  - .github/workflows/universal-agent-e2e.yml
  - .github/workflows/universal-agent-load.yml
  - tools/agents/ci_incremental_validation.py
  - tests/agents/test_ci_incremental_validation.py
  - docs/agents/tasks/active/CAN-20260716-incremental-ci-final-gate.md
  - AGENTS.md
  - docs/agents/BUILD_TEST_MATRIX.md
proven:
  - Repository write target is exactly blakinio/canary.
  - PR 393 merged as 2f828672df010ff577c8e6076524b37c6dedd987 before task creation.
  - Branch ci/incremental-validation-final-gate was created from that exact main head.
  - Current CI forces Linux validation for every pull request.
  - Universal Agent E2E broadly matches tests/e2e/** including load-only tests.
derived:
  - Parent-success plus non-impacting HEAD^..HEAD evidence can safely avoid repeated heavy work while a final forced gate preserves merge quality.
unknown:
  - Exact implementation edits and resulting workflow behavior until focused tests and live PR validation run.
conflicts: []
first_failure: null
rejected_hypotheses:
  - Path filters alone solve docs-only follow-up reruns: pull_request path filters use the PR change set, so relevant earlier files continue to match on later synchronize events.
  - A successful workflow on any older SHA is sufficient: reuse is bounded to the immediate parent chain and the latest same-workflow parent run must be successful.
changed_paths:
  - docs/agents/tasks/active/CAN-20260716-incremental-ci-final-gate.md
validation: []
blockers: []
next_action: Open the draft PR for this claimed task, then implement and test the parent-success incremental validation helper before wiring it into CI, E2E and Load workflows.
```
