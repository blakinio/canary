---
task_id: CAN-20260716-incremental-ci-final-gate
program_id: "CAN-PROGRAM-AGENT-ORCHESTRATION"
coordination_id: ""
status: implementing
agent: chatgpt-ci-governance
branch: ci/incremental-validation-final-gate
base_branch: main
created: 2026-07-16T10:10:00+02:00
updated: 2026-07-16T11:44:00+02:00
last_verified_commit: 623069ab3a01edc25df9923b849c83775dfd4ced
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
- [x] Missing parent evidence, a failed/in-progress latest parent run, workflow changes, helper changes, or an impacting delta fail closed to heavy validation.
- [ ] An empty final-gate commit forces the full applicable workflow set on the final head because empty single-commit path evidence fails closed.
- [x] CI no longer performs Linux compilation for documentation-only PR scope.
- [x] Universal Agent E2E no longer triggers for load-only `tests/e2e/load/**` or `tests/e2e/test_load_runner.py` changes by path definition.
- [x] Load and physical E2E can reuse proven parent success for non-impacting follow-up commits and still run fully on the empty final-gate commit.
- [ ] Agent policy batches checkpoint/docs mutations before final-gate validation and forbids a post-green checkpoint commit that would invalidate the final head.
- [x] Focused helper tests and exact implementation workflow checks pass.
- [x] No branch-protection, test, assertion, throttle, or safety gate is weakened.

# Confirmed context

- Repository write target is exactly `blakinio/canary`.
- PR #393 merged successfully as squash commit `2f828672df010ff577c8e6076524b37c6dedd987` before this task branch was created.
- Draft PR #415 targets `blakinio/canary:main` from `blakinio/canary:ci/incremental-validation-final-gate`.
- The motivating waste was observed directly: docs/shared-index commits after green runtime heads repeatedly rebuilt Canary and the unchanged controlled OTClient before merge.
- Existing root policy already says to avoid wasteful builds for clearly non-build-affecting docs/scripts; this task makes workflow behavior match that policy.
- Baseline CI forced Linux release for every pull request; the branch now computes Linux scope from affected paths and suppresses heavy scopes only when the helper proves immediate-parent reuse.
- Universal Agent E2E now has a fail-closed scope job, excludes load-only E2E paths, and has a `Required physical E2E` aggregator that accepts heavy skips only with proven immediate-parent reuse.
- Universal Agent Load now has the same fail-closed scope/required pattern while keeping focused runner validation on every applicable head.
- The helper itself is explicitly impacting for both physical E2E and Load profiles, and focused regressions preserve `.github/**` dotfile path matching.
- Full implementation head `bc0a3b72148ff3719c51292af36b7635f5267140` passed Ownership #1594, CI #2729, Universal Agent Load #43 and Universal Agent E2E #87 after helper self-change hardening; the heavy Canary/OTClient paths ran rather than being reused.
- Docs-only checkpoint head `623069ab3a01edc25df9923b849c83775dfd4ced` then passed Ownership #1601, CI #2737, Load #44 and E2E #88 through immediate-parent reuse, proving the expensive jobs are skipped after a green parent while current-head Required checks remain green.
- Current `main@44cd23bec185a5e0a6167d6180008eddd47ac594` is six commits ahead of the task-start base and changes unrelated OTBM/Oteryn paths plus shared agent docs; synchronization is the next step before final shared-doc edits.

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

Implementation and focused tests are complete and green. The process has been proven in both directions: docs-only children reused successful immediate-parent CI/Load/E2E evidence and skipped expensive jobs, while the helper self-change forced full Load and physical E2E validation. The remaining work is current-main synchronization, one frozen shared-doc/policy batch, PR readiness, an empty exact-head final-gate commit, and squash merge if the final gate and live merge checks pass.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T11:44:00+02:00
head: 623069ab3a01edc25df9923b849c83775dfd4ced
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
  - Full implementation head bc0a3b72148ff3719c51292af36b7635f5267140 passed Ownership 1594, CI 2729, Load 43 and E2E 87 with heavy paths executed.
  - Docs-only head 623069ab3a01edc25df9923b849c83775dfd4ced passed Ownership 1601, CI 2737, Load 44 and E2E 88 using immediate-parent reuse.
  - The helper profile treats tools/agents/ci_incremental_validation.py as impacting for CI, physical E2E and Load.
  - Focused tests cover helper self-change and preservation of leading .github dotfile paths.
derived:
  - Parent-success plus non-impacting HEAD^..HEAD evidence safely avoids repeated heavy work while an empty final-gate commit preserves exact-final-head quality.
unknown:
  - Final current-main merge-result and shared-doc contents until synchronization is completed.
  - Empty final-gate Git-object delivery behavior until exercised on the frozen content head.
conflicts: []
first_failure:
  marker: Agent Task Ownership 1555 / Validate changed active task checkpoints
  evidence: Task-record schema issues were exposed sequentially and repaired; helper compilation/tests remained green, and Ownership is now consistently green.
rejected_hypotheses:
  - Path filters alone solve docs-only follow-up reruns: pull_request path filters use the cumulative PR change set, so relevant earlier files continue to match on later synchronize events.
  - A successful workflow on any older SHA is sufficient: reuse is bounded to the immediate parent chain and the latest same-workflow parent run must be successful.
  - A label-triggered final gate is necessary: an empty final commit creates a new exact PR head, triggers normal synchronize semantics, and the helper fails closed on empty changed-path evidence without introducing same-name no-op checks.
  - Helper changes may reuse older E2E/Load evidence: helper self-change is an explicit impacting path and full Load 43/E2E 87 validation proved the heavy paths run.
changed_paths:
  - .github/workflows/agent-task-ownership.yml
  - .github/workflows/ci.yml
  - .github/workflows/universal-agent-e2e.yml
  - .github/workflows/universal-agent-load.yml
  - docs/agents/tasks/active/CAN-20260716-incremental-ci-final-gate.md
  - tools/agents/ci_incremental_validation.py
  - tools/agents/test_ci_incremental_validation.py
validation:
  - command: Agent Task Ownership 1594
    result: PASS
    evidence: Task ownership, helper compilation and focused unit tests succeeded on bc0a3b72148ff3719c51292af36b7635f5267140.
  - command: CI 2729
    result: PASS
    evidence: Exact implementation head bc0a3b72148ff3719c51292af36b7635f5267140.
  - command: Universal Agent Load 43
    result: PASS
    evidence: Helper-hardening head ran full Canary build, status-smoke and Required load validation successfully.
  - command: Universal Agent E2E 87
    result: PASS
    evidence: Helper-hardening head ran DB preflight, Canary build, controlled OTClient build, physical login/relog scenario and Required physical E2E successfully.
  - command: CI 2737 / docs-only reuse
    result: PASS
    evidence: Heavy build jobs were suppressed by proven immediate-parent reuse and Required succeeded on 623069ab3a01edc25df9923b849c83775dfd4ced.
  - command: Universal Agent Load 44 / docs-only reuse
    result: PASS
    evidence: Focused load validation remained current-head while heavy Canary/load jobs were reused from the successful parent.
  - command: Universal Agent E2E 88 / docs-only reuse
    result: PASS
    evidence: Resolve/current-head gate remained while DB, Canary, OTClient and physical-client heavy jobs were reused from the successful parent.
blockers: []
next_action: Synchronize the branch conservatively with current main@44cd23bec185a5e0a6167d6180008eddd47ac594, verify the merge result preserves only intended PR paths, then write one frozen shared-doc/policy batch before the empty final validation gate.
```
