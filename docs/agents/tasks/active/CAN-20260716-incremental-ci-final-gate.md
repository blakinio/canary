---
task_id: CAN-20260716-incremental-ci-final-gate
program_id: ""
coordination_id: ""
status: active
agent: chatgpt-ci-governance
branch: ci/incremental-validation-final-gate
base_branch: main
created: 2026-07-16T10:10:00+02:00
updated: 2026-07-16T10:30:00+02:00
last_verified_commit: 36efff20a681f72c05f07d60f6a38cba6ee760a6
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
- [x] Universal Agent E2E no longer triggers for load-only `tests/e2e/load/**` or `tests/e2e/test_load_runner.py` changes by path definition.
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
- Universal Agent E2E now has a fail-closed scope job, excludes load-only E2E paths, and has a Required physical E2E aggregator that accepts heavy skips only with proven immediate-parent reuse.
- Agent tooling tests live beside helpers under `tools/agents` and are executed by `.github/workflows/agent-task-ownership.yml`.
- Agent Task Ownership #1555 and #1561 both compiled the helper and ran all focused unit tests successfully. #1555 failed because `first_failure` was null; #1561 failed because checkpoint status `active` is unsupported. Both are task-record schema issues, not helper/test failures.

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

The helper, focused tests, Agent Task Ownership test wiring, main CI incremental scope, and Universal Agent E2E scope/required aggregation are implemented. Focused unit tests pass in live CI. Two Ownership failures were isolated to checkpoint schema and are repaired here by using supported checkpoint status `implementing`. Universal Agent Load wiring, final-gate dispatcher, policy docs, and live behavioral validation remain.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T10:30:00+02:00
head: 36efff20a681f72c05f07d60f6a38cba6ee760a6
branch: ci/incremental-validation-final-gate
pr: 415
status: implementing
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
  - Agent Task Ownership 1555 and 1561 compiled the helper and all focused unit tests passed.
  - Ownership 1555 failed only because first_failure was null instead of a mapping.
  - Ownership 1561 failed only because checkpoint status active is unsupported.
  - CI 2689 completed successfully on head 815c895d95df0929aacdc57d6879403951a3639f after the main CI scope wiring.
  - Universal Agent E2E scope and Required physical E2E aggregation are implemented on head 36efff20a681f72c05f07d60f6a38cba6ee760a6.
derived:
  - Parent-success plus non-impacting HEAD^..HEAD evidence can safely avoid repeated heavy work while a final forced gate preserves merge quality.
  - Ownership failures 1555 and 1561 are task-record schema failures, not helper logic or unit-test failures.
unknown:
  - Universal Agent E2E live conclusion on the latest workflow-wiring head until run 81 completes.
  - Universal Agent Load behavior until its incremental scope wiring is implemented and exercised.
  - Final-gate dispatcher behavior until implemented and tested.
conflicts: []
first_failure:
  marker: Agent Task Ownership 1555 / Validate changed active task checkpoints
  evidence: The checkpoint encoded first_failure as null; task_lifecycle requires a YAML mapping. Ownership 1561 then exposed unsupported checkpoint status active. Helper compilation and focused unit tests passed in both runs.
rejected_hypotheses:
  - Path filters alone solve docs-only follow-up reruns: pull_request path filters use the PR change set, so relevant earlier files continue to match on later synchronize events.
  - A successful workflow on any older SHA is sufficient: reuse is bounded to the immediate parent chain and the latest same-workflow parent run must be successful.
  - Ownership 1555 or 1561 proves the incremental helper failed: compile and focused unit tests passed; only checkpoint schema validation failed.
changed_paths:
  - .github/workflows/agent-task-ownership.yml
  - .github/workflows/ci.yml
  - .github/workflows/universal-agent-e2e.yml
  - docs/agents/tasks/active/CAN-20260716-incremental-ci-final-gate.md
  - tools/agents/ci_incremental_validation.py
  - tools/agents/test_ci_incremental_validation.py
validation:
  - command: Agent Task Ownership 1555 and 1561 / Compile agent tooling + Run focused unit tests
    result: PASS
    evidence: Both steps completed successfully in both runs.
  - command: Agent Task Ownership 1555 / Validate changed active task checkpoints
    result: FAIL
    evidence: first_failure must be a YAML mapping; repaired.
  - command: Agent Task Ownership 1561 / Validate changed active task checkpoints
    result: FAIL
    evidence: checkpoint status active is unsupported; repaired to implementing here.
  - command: CI 2689
    result: PASS
    evidence: Workflow completed successfully on 815c895d95df0929aacdc57d6879403951a3639f.
blockers: []
next_action: Verify the repaired Ownership checkpoint and E2E run, then wire Universal Agent Load through a blob/tree commit because plaintext workflow replacement is blocked by tool safeguards on existing test-password fields.
```
