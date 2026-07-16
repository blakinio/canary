---
task_id: CAN-20260716-incremental-ci-final-gate
program_id: "CAN-PROGRAM-AGENT-ORCHESTRATION"
coordination_id: ""
status: ready
agent: chatgpt-ci-governance
branch: ci/incremental-validation-final-gate
base_branch: main
created: 2026-07-16T10:10:00+02:00
updated: 2026-07-16T14:22:41+02:00
last_verified_commit: f529e34dc6b7c7c7a4e8c8fbfb820aff91705660
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
  - existing Universal Agent E2E physical login/relog sentinel
  - existing Universal Agent Load exact-head status-smoke sentinel
  - existing Agent Task Ownership focused validation
public_interfaces:
  - ci_incremental_validation.py decision contract
  - ci:final-gate PR-label final-head convention
cross_repo_tasks: []
---

# Goal

Reduce repeated heavy PR validation for proven non-impacting follow-up commits without reducing merge quality. Reuse is limited to successful immediate-parent workflow evidence and every uncertain case fails closed. The exact final head must still pass full applicable validation.

# Acceptance criteria

- [x] Standard-library helper classifies CI, physical E2E and load impact.
- [x] Reuse requires the immediate parent's latest same-workflow PR run to be completed successfully.
- [x] Missing/non-success evidence, empty or unresolvable deltas, impacting paths and workflow/helper changes fail closed.
- [x] Current-head focused validation and stable Required aggregators remain active when expensive jobs are reused.
- [x] Load-only E2E paths do not affect the physical-client profile.
- [x] Helper self-change and `.github/**` path handling have focused regressions.
- [x] Exact `ci:final-gate` label detection from the GitHub event payload forces full applicable validation.
- [x] Root policy and build matrix require batched docs/checkpoints and forbid a post-green final-gate commit.
- [x] No test, assertion, throttle, branch-protection gate or physical-client sentinel is weakened.

# Confirmed context

- Repository writes are limited to `blakinio/canary`; upstream/donor repositories remain read-only.
- PR #393 merged as `2f828672df010ff577c8e6076524b37c6dedd987` before this task.
- PR #415 is the live task PR from `ci/incremental-validation-final-gate` to `main`.
- Full code head `2c6370418d0bd8d966289d5a1cf7c075ed75459f` passed Ownership #1626, CI #2763, Load #52 and physical E2E #96.
- Docs-only heads `9c02a95a6c7deb0d65c2c8a3956031c8ff2d9044`, `27163653e43454df9d51ee465143e5f3ab94ccf9` and `fe618730149d4a7d2c5d5ffa997f3935f4f08bc9` proved immediate-parent reuse while current-head Required gates remained green.
- E2E #94 had one transient failure in the unchanged pinned OTClient build; one allowed failed-job rerun on the same SHA passed without a code patch.
- Current main `368319e6e20672339a6409504d1a9f69c15ea077` was merged conservatively into the branch through verified Git objects because the connector has no native update-branch action.
- Merge commit `f529e34dc6b7c7c7a4e8c8fbfb820aff91705660` was verified before branch update: relative to current main it contains exactly the eleven intended PR paths; relative to the previous branch head it adds only the six new OTBM planner/archive files from main.
- Sync head `f529e34dc6b7c7c7a4e8c8fbfb820aff91705660` passed Ownership #1650, CI #2787, Load #56 including real status-smoke, and physical E2E #100 including DB, Canary, pinned OTClient and physical-client validation.
- Main remained `368319e6e20672339a6409504d1a9f69c15ea077` immediately before the final commit.
- PR #415 carries `ci:final-gate` before this final task commit.

# Safety design

1. Normal synchronize decisions inspect only `HEAD^..HEAD`.
2. Reuse requires a non-impacting delta and successful latest same-workflow immediate-parent PR run.
3. Missing, non-success, empty or unresolvable evidence fails closed.
4. Relevant workflow/helper changes force full validation.
5. Focused current-head checks and stable Required aggregators remain active during reuse.
6. `ci:final-gate` is applied before the last content commit; the final synchronize event therefore sets `force_full` for CI, Load and physical E2E on that exact SHA.
7. No commit is allowed after the final gate turns green; a later commit invalidates that evidence and must pass the full gate again.

# Current state

Implementation, tests, policy, catalogue, changelog, synchronization with current main and pre-final full runtime evidence are complete. This task file is the final content commit. Exact final-head workflows under `ci:final-gate` are the remaining merge evidence.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T14:22:41+02:00
head: f529e34dc6b7c7c7a4e8c8fbfb820aff91705660
branch: ci/incremental-validation-final-gate
pr: 415
status: ready
context_routes:
  - agent-governance
  - universal-e2e
  - ci-repair
owned_paths:
  - .github/workflows/agent-task-ownership.yml
  - .github/workflows/ci.yml
  - .github/workflows/universal-agent-e2e.yml
  - .github/workflows/universal-agent-load.yml
  - AGENTS.md
  - docs/agents/BUILD_TEST_MATRIX.md
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260716-incremental-ci-final-gate.md
  - tools/agents/ci_incremental_validation.py
  - tools/agents/test_ci_incremental_validation.py
proven:
  - Repository write target is exactly blakinio/canary.
  - PR 393 merged as 2f828672df010ff577c8e6076524b37c6dedd987 before task creation.
  - Full code head 2c6370418d0bd8d966289d5a1cf7c075ed75459f passed Ownership 1626, CI 2763, Load 52 and E2E 96 with heavy paths executed.
  - Documentation-only follow-up heads proved immediate-parent reuse while Required gates remained green.
  - Exact ci:final-gate label detection is regression-tested.
  - Sync merge f529e34dc6b7c7c7a4e8c8fbfb820aff91705660 contains current main 368319e6e20672339a6409504d1a9f69c15ea077 and exactly eleven PR paths relative to main.
  - Sync head f529e34dc6b7c7c7a4e8c8fbfb820aff91705660 passed Ownership 1650, CI 2787, Load 56 and E2E 100 with full heavy validation.
  - PR 415 carries ci:final-gate before this final task commit.
derived:
  - Proven non-impacting immediate-parent reuse avoids repeated heavy work while the labeled final synchronize preserves exact-final-head full validation.
unknown:
  - Exact final-head workflow results are pending on this final task commit under ci:final-gate.
conflicts: []
first_failure:
  marker: Agent Task Ownership 1555 / changed active task checkpoint validation
  evidence: Early task-record schema defects were repaired without weakening validation; helper compilation and focused tests remained green.
rejected_hypotheses:
  - Path filters alone solve docs-only reruns; pull_request path filters use cumulative PR scope.
  - Any older successful SHA is sufficient; reuse is immediate-parent only.
  - A separate no-op final check is required; the labeled final synchronize forces the existing workflow families on the final content SHA.
  - Helper changes may reuse older runtime evidence; the helper is explicitly impacting.
changed_paths:
  - .github/workflows/agent-task-ownership.yml
  - .github/workflows/ci.yml
  - .github/workflows/universal-agent-e2e.yml
  - .github/workflows/universal-agent-load.yml
  - AGENTS.md
  - docs/agents/BUILD_TEST_MATRIX.md
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260716-incremental-ci-final-gate.md
  - tools/agents/ci_incremental_validation.py
  - tools/agents/test_ci_incremental_validation.py
validation:
  - command: Full code gate / Ownership 1626, CI 2763, Load 52, E2E 96
    result: PASS
    evidence: Exact code/test head 2c6370418d0bd8d966289d5a1cf7c075ed75459f ran full applicable validation.
  - command: Documentation-only immediate-parent reuse
    result: PASS
    evidence: Multiple docs-only heads kept current-head gates green while expensive jobs were reused.
  - command: Full synchronized gate / Ownership 1650, CI 2787, Load 56, E2E 100
    result: PASS
    evidence: Exact synchronized head f529e34dc6b7c7c7a4e8c8fbfb820aff91705660 ran full applicable validation.
blockers: []
next_action: Verify the full exact-head workflows triggered by this final task commit under ci:final-gate; if all are green, perform the live merge gate and squash-merge PR 415 without further commits.
```