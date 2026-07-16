---
task_id: CAN-20260716-incremental-ci-final-gate
program_id: ""
coordination_id: ""
status: implementing
agent: chatgpt-ci-governance
branch: ci/incremental-validation-final-gate
base_branch: main
created: 2026-07-16T10:10:00+02:00
updated: 2026-07-16T10:51:00+02:00
last_verified_commit: 95c51e6032d3027032d130bebdc6cab3faca20fe
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
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
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
  - ci_incremental_validation.py decision contract
  - empty final-gate commit convention
cross_repo_tasks: []
---

# Goal

Reduce repeated heavy CI after non-impacting follow-up commits without reducing merge quality: reuse a successful parent workflow only for a proven non-impacting single-commit delta, fail closed otherwise, and force the full applicable validation set once on the final PR head before merge.

# Acceptance criteria

- [x] A tested standard-library helper classifies whether the current single-commit delta affects CI, physical E2E, or load validation.
- [x] Parent reuse is allowed only when the latest same-workflow pull-request run on `HEAD^` completed successfully.
- [x] Missing parent evidence, a failed/in-progress latest parent run, workflow changes, or an impacting delta fail closed to heavy validation.
- [ ] An empty final-gate commit forces the full applicable workflow set on the final head because empty single-commit path evidence fails closed.
- [ ] CI no longer performs Linux compilation for documentation-only PR scope.
- [x] Universal Agent E2E no longer triggers for load-only `tests/e2e/load/**` or `tests/e2e/test_load_runner.py` changes by path definition.
- [ ] Load and physical E2E can reuse proven parent success for non-impacting follow-up commits and still run fully on the empty final-gate commit.
- [ ] Agent policy batches checkpoint/docs mutations before final-gate validation and forbids a post-green checkpoint commit that would invalidate the final head.
- [ ] Focused helper tests and exact workflow checks pass.
- [ ] No branch-protection, test, assertion, throttle, or safety gate is weakened.

# Confirmed context

- Repository write target is exactly `blakinio/canary`.
- PR #393 merged successfully as squash commit `2f828672df010ff577c8e6076524b37c6dedd987` before this task branch was created.
- Draft PR #415 targets `blakinio/canary:main` from `blakinio/canary:ci/incremental-validation-final-gate`.
- The motivating waste was observed directly: docs/shared-index commits after green runtime heads repeatedly rebuilt Canary and the unchanged controlled OTClient before merge.
- Existing root policy already says to avoid wasteful builds for clearly non-build-affecting docs/scripts; this task makes workflow behavior match that policy.
- Baseline CI forced Linux release for every pull request; the branch now computes Linux scope from affected paths and suppresses heavy scopes only when the helper proves immediate-parent reuse.
- Universal Agent E2E now has a fail-closed scope job, excludes load-only E2E paths, and has a `Required physical E2E` aggregator that accepts heavy skips only with proven immediate-parent reuse.
- Universal Agent Load now has the same fail-closed scope/required pattern while keeping focused runner validation on every applicable head.
- Agent tooling tests live beside helpers under `tools/agents` and are executed by `.github/workflows/agent-task-ownership.yml`.
- Agent Task Ownership #1555, #1561 and #1570 compiled the helper and ran all focused unit tests successfully; their failures were task-record lifecycle schema issues, not helper/test failures.
- CI #2705, Universal Agent Load #39 and Universal Agent E2E #83 all completed successfully on implementation head `95c51e6032d3027032d130bebdc6cab3faca20fe`.
- Current `main` advanced after branch creation only through OTBM/Oteryn docs and `tools/ai-agent` work; synchronization is deferred until the current incremental reuse behavior is observed.

# Safety design

The optimization is evidence-preserving, not skip-by-assumption:

1. On a `synchronize` event, inspect only `HEAD^..HEAD`.
2. Reuse is possible only if that delta is non-impacting for the workflow.
3. Query the parent SHA's latest same-name `pull_request` workflow run; require `completed/success`.
4. If multiple commits were pushed at once, `HEAD^` normally has no workflow evidence, so the decision fails closed and heavy validation runs.
5. Any relevant workflow/helper path change is itself impacting and forces heavy validation.
6. Before merge, freeze implementation, task checkpoint and shared docs, then create exactly one empty commit with conventional message `chore(ci): run final validation gate`.
7. Empty single-commit path evidence fails closed, so every workflow family already applicable to the PR performs its full heavy validation on that exact final head.
8. Any later commit invalidates the final gate and requires another empty final-gate commit; no checkpoint/docs commit is allowed after the green final gate.

# Current state

The helper, focused tests, Agent Task Ownership test wiring, main CI incremental scope, Universal Agent E2E scope/required aggregation, and Universal Agent Load scope/required aggregation are implemented. The first full implementation head passed CI, Load and physical E2E. This commit changes only the task lifecycle record from unsupported `active` to supported `implementing` and is intentionally used to prove immediate-parent reuse before the remaining helper hardening, base synchronization, shared docs and final empty-commit gate.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T10:51:00+02:00
head: 95c51e6032d3027032d130bebdc6cab3faca20fe
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
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - Repository write target is exactly blakinio/canary.
  - PR 393 merged as 2f828672df010ff577c8e6076524b37c6dedd987 before task creation.
  - Draft PR 415 is the live PR for this task.
  - The helper and focused tests are implemented under tools/agents.
  - Ownership runs 1555, 1561 and 1570 compiled the helper and all focused unit tests passed.
  - Ownership 1555 failed only because first_failure was null instead of a mapping.
  - Ownership 1561 and 1570 failed only because the active task frontmatter used unsupported status active; this commit repairs it to implementing.
  - CI 2705 passed on 95c51e6032d3027032d130bebdc6cab3faca20fe.
  - Universal Agent Load 39 passed full scope, runner validation, exact Canary build, status-smoke and Required load validation on 95c51e6032d3027032d130bebdc6cab3faca20fe.
  - Universal Agent E2E 83 passed the full physical-client workflow on 95c51e6032d3027032d130bebdc6cab3faca20fe.
derived:
  - Parent-success plus non-impacting HEAD^..HEAD evidence can safely avoid repeated heavy work while an empty final-gate commit preserves exact-final-head quality.
unknown:
  - Live immediate-parent reuse behavior for this docs-only lifecycle commit until its CI, Load and E2E workflow jobs complete.
  - Final behavior after current main synchronization and helper self-change hardening until validated.
conflicts: []
first_failure:
  marker: Agent Task Ownership 1555 / Validate changed active task checkpoints
  evidence: The checkpoint first exposed first_failure null; later runs exposed unsupported frontmatter status active. Helper compilation and focused unit tests passed in every failing Ownership run.
rejected_hypotheses:
  - Path filters alone solve docs-only follow-up reruns: pull_request path filters use the cumulative PR change set, so relevant earlier files continue to match on later synchronize events.
  - A successful workflow on any older SHA is sufficient: reuse is bounded to the immediate parent chain and the latest same-workflow parent run must be successful.
  - A label-triggered final gate is necessary: an empty final commit is safer because it creates a new exact PR head, triggers normal synchronize semantics, and the helper fails closed on empty changed-path evidence without introducing same-name no-op checks.
  - Ownership failures prove the incremental helper failed: compile and focused unit tests passed; only task-record lifecycle schema validation failed.
changed_paths:
  - .github/workflows/agent-task-ownership.yml
  - .github/workflows/ci.yml
  - .github/workflows/universal-agent-e2e.yml
  - .github/workflows/universal-agent-load.yml
  - docs/agents/tasks/active/CAN-20260716-incremental-ci-final-gate.md
  - tools/agents/ci_incremental_validation.py
  - tools/agents/test_ci_incremental_validation.py
validation:
  - command: Agent Task Ownership 1555, 1561 and 1570 / Compile agent tooling + Run focused unit tests
    result: PASS
    evidence: Compile and focused test steps completed successfully in all three runs.
  - command: CI 2705
    result: PASS
    evidence: Workflow completed successfully on implementation head 95c51e6032d3027032d130bebdc6cab3faca20fe.
  - command: Universal Agent Load 39
    result: PASS
    evidence: Full load path and Required load validation completed successfully on implementation head 95c51e6032d3027032d130bebdc6cab3faca20fe.
  - command: Universal Agent E2E 83
    result: PASS
    evidence: Full physical-client workflow completed successfully on implementation head 95c51e6032d3027032d130bebdc6cab3faca20fe.
blockers: []
next_action: Verify that this docs-only lifecycle commit reuses the successful immediate-parent CI, Load and E2E evidence while Ownership passes, then harden helper self-change classification before synchronizing current main and writing final shared docs.
```
