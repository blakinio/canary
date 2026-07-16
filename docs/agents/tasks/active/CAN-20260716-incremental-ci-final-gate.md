---
task_id: CAN-20260716-incremental-ci-final-gate
program_id: ""
coordination_id: ""
status: active
agent: chatgpt-ci-governance
branch: ci/incremental-validation-final-gate
base_branch: main
created: 2026-07-16T10:10:00+02:00
updated: 2026-07-16T10:25:00+02:00
last_verified_commit: 815c895d95df0929aacdc57d6879403951a3639f
risk: medium
related_issue: ""
related_pr: "415"
depends_on:
  - CAN-20260715-universal-agent-load-platform
blocks: []
owned_paths:
  exclusive:
    - .github/workflows/ci.yml
    - .github/workflows/universal-agent-e2e.yml
    - .github/workflows/universal-agent-load.yml
    - .github/workflows/agent-task-ownership.yml
    - tools/agents/ci_incremental_validation.py
    - tools/agents/test_ci_incremental_validation.py
    - docs/agents/tasks/active/CAN-20260716-incremental-ci-final-gate.md
  shared:
    - AGENTS.md
    - docs/agents/BUILD_TEST_MATRIX.md
  read_only: []
modules_touched:
  - CI validation orchestration
  - Universal Agent E2E workflow gating
  - Universal Agent Load workflow gating
  - Agent tooling focused validation
reuses:
  - existing CI Detect Build Scope and Required aggregation
  - existing workflow_dispatch full validation paths
  - existing Universal Agent E2E physical login/relog sentinel
  - existing Universal Agent Load exact-head status-smoke sentinel
  - existing Agent Task Ownership Python compile/unit-test job
public_interfaces:
  - ci:final-gate pull-request label convention
  - ci_incremental_validation.py decision contract
cross_repo_tasks: []
---

# Goal

Reduce repeated heavy CI after non-impacting follow-up commits without reducing merge quality: reuse a successful parent workflow only for a proven non-impacting single-commit delta, fail closed otherwise, and force the full applicable validation set once on the final PR head before merge.

# Acceptance criteria

- [x] A tested standard-library helper classifies whether the current single-commit delta affects CI, physical E2E, or load validation.
- [x] Parent reuse is allowed only when the latest same-workflow pull-request run on `HEAD^` completed successfully.
- [x] Missing parent evidence, a failed/in-progress latest parent run, workflow changes, or an impacting delta fail closed to heavy validation.
- [ ] `ci:final-gate` forces the full applicable workflow on the current head and bypasses incremental reuse.
- [ ] CI no longer performs Linux compilation for documentation-only PR scope.
- [ ] Universal Agent E2E no longer triggers for load-only `tests/e2e/load/**` or `tests/e2e/test_load_runner.py` changes.
- [ ] Load and physical E2E can reuse proven parent success for non-impacting follow-up commits but still run on final-gate dispatch.
- [ ] Agent policy batches checkpoint/docs mutations before final-gate validation and forbids a post-green checkpoint commit that would invalidate the final head.
- [ ] Focused helper tests and exact workflow checks pass.
- [ ] No branch-protection, test, assertion, throttle, or safety gate is weakened.

# Confirmed context

- Repository write target is exactly `blakinio/canary`.
- PR #393 merged successfully as squash commit `2f828672df010ff577c8e6076524b37c6dedd987` before this task branch was created.
- Current `main` equaled `2f828672df010ff577c8e6076524b37c6dedd987` when this branch was created.
- Draft PR #415 targets `blakinio/canary:main` from `blakinio/canary:ci/incremental-validation-final-gate`.
- The motivating waste was observed directly: docs/shared-index commits after green runtime heads repeatedly rebuilt Canary and the unchanged controlled OTClient before merge.
- Existing root policy already says to avoid wasteful builds for clearly non-build-affecting docs/scripts; this task makes workflow behavior match that policy.
- Baseline CI forced Linux release for every pull request; the branch now computes Linux scope from affected paths and suppresses heavy scopes only when the helper proves immediate-parent reuse.
- Baseline Universal Agent E2E uses broad `tests/e2e/**`, causing load-only test paths to trigger physical-client E2E; workflow wiring remains pending.
- Agent tooling tests live beside helpers under `tools/agents` and are executed by `.github/workflows/agent-task-ownership.yml`.
- Agent Task Ownership #1555 compiled the new helper and ran all focused unit tests successfully; the workflow failed later only because this checkpoint used `first_failure: null`, which violates the required mapping schema.

# Safety design

The optimization is evidence-preserving, not skip-by-assumption:

1. On a `synchronize` event, inspect only `HEAD^..HEAD`.
2. Reuse is possible only if that delta is non-impacting for the workflow.
3. Query the parent SHA's latest same-name `pull_request` workflow run; require `completed/success`.
4. If multiple commits were pushed at once, `HEAD^` normally has no workflow evidence, so the decision fails closed and heavy validation runs.
5. Any relevant workflow/helper path change is itself impacting and forces heavy validation.
6. Before merge, a trusted `ci:final-gate` dispatcher will force the full applicable workflow set on the current head without creating a same-name no-op required check.
7. Any commit after the final-gate dispatch changes the head and requires the final gate again.

# Current state

The helper, focused tests, Agent Task Ownership test wiring, and main CI incremental scope wiring are implemented. Focused unit tests passed in live CI. Ownership checkpoint validation failed because `first_failure` was encoded as null; this update repairs that schema issue and records the evidence. E2E/Load wiring, final-gate dispatcher, policy docs, and live behavioral validation remain.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T10:25:00+02:00
head: 815c895d95df0929aacdc57d6879403951a3639f
branch: ci/incremental-validation-final-gate
pr: 415
status: active
context_routes:
  - agent-governance
  - universal-e2e
  - ci-repair
owned_paths:
  - .github/workflows/ci.yml
  - .github/workflows/universal-agent-e2e.yml
  - .github/workflows/universal-agent-load.yml
  - .github/workflows/agent-task-ownership.yml
  - tools/agents/ci_incremental_validation.py
  - tools/agents/test_ci_incremental_validation.py
  - docs/agents/tasks/active/CAN-20260716-incremental-ci-final-gate.md
  - AGENTS.md
  - docs/agents/BUILD_TEST_MATRIX.md
proven:
  - Repository write target is exactly blakinio/canary.
  - PR 393 merged as 2f828672df010ff577c8e6076524b37c6dedd987 before task creation.
  - Branch ci/incremental-validation-final-gate was created from that exact main head.
  - Draft PR 415 is the live PR for this task.
  - The helper and focused tests are implemented under tools/agents.
  - Agent Task Ownership 1555 compiled the helper and all focused unit tests passed.
  - Ownership 1555 failed only at changed-task checkpoint validation because first_failure was null instead of a mapping.
  - CI 2689 completed successfully on head 815c895d95df0929aacdc57d6879403951a3639f after the main CI scope wiring.
derived:
  - Parent-success plus non-impacting HEAD^..HEAD evidence can safely avoid repeated heavy work while a final forced gate preserves merge quality.
  - The Ownership 1555 failure is task-record schema, not helper logic or unit-test behavior.
unknown:
  - E2E and Load workflow behavior until their incremental scope wiring is implemented and exercised.
  - Final-gate dispatcher behavior until implemented and tested.
conflicts: []
first_failure:
  marker: Agent Task Ownership 1555 / Validate changed active task checkpoints
  evidence: The checkpoint encoded first_failure as null; task_lifecycle requires a YAML mapping. Helper compilation and focused unit tests passed earlier in the same job.
rejected_hypotheses:
  - Path filters alone solve docs-only follow-up reruns: pull_request path filters use the PR change set, so relevant earlier files continue to match on later synchronize events.
  - A successful workflow on any older SHA is sufficient: reuse is bounded to the immediate parent chain and the latest same-workflow parent run must be successful.
  - Ownership 1555 proves the incremental helper failed: compile and focused unit tests passed; only checkpoint schema validation failed.
changed_paths:
  - .github/workflows/agent-task-ownership.yml
  - .github/workflows/ci.yml
  - docs/agents/tasks/active/CAN-20260716-incremental-ci-final-gate.md
  - tools/agents/ci_incremental_validation.py
  - tools/agents/test_ci_incremental_validation.py
validation:
  - command: Agent Task Ownership 1555 / Compile agent tooling + Run focused unit tests
    result: PASS
    evidence: Both steps completed successfully on 815c895d95df0929aacdc57d6879403951a3639f.
  - command: Agent Task Ownership 1555 / Validate changed active task checkpoints
    result: FAIL
    evidence: first_failure must be a YAML mapping; repaired by this task-record update.
  - command: CI 2689
    result: PASS
    evidence: Workflow completed successfully on 815c895d95df0929aacdc57d6879403951a3639f.
blockers: []
next_action: Verify the repaired Ownership checkpoint run, then wire the proven helper into Universal Agent E2E and Universal Agent Load before implementing the trusted final-gate dispatcher.
```
