---
task_id: CAN-20260716-incremental-ci-final-gate
program_id: "CAN-PROGRAM-AGENT-ORCHESTRATION"
coordination_id: ""
status: completed
agent: chatgpt-ci-governance
branch: ci/incremental-validation-final-gate
base_branch: main
created: 2026-07-16T10:10:00+02:00
updated: 2026-07-16T17:59:36Z
last_verified_commit: "0f25e7fd4d41e90f17fc95d13dba84b7e81d1681"
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
completed: 2026-07-16T17:59:36Z
---

# Goal

Reduce repeated heavy PR validation for proven non-impacting follow-up commits without reducing merge quality. Reuse is limited to successful immediate-parent workflow evidence and uncertainty fails closed. The exact final head must pass full applicable CI, Load and physical E2E validation.

# Acceptance criteria

- [x] Standard-library helper classifies CI, physical E2E and load impact.
- [x] Reuse requires the immediate parent's latest same-workflow PR run to be completed successfully.
- [x] Missing/non-success evidence, empty or unresolvable deltas, impacting paths and workflow/helper changes fail closed.
- [x] Current-head focused validation and stable Required aggregators remain active when expensive jobs are reused.
- [x] Load-only E2E paths do not affect the physical-client profile.
- [x] Helper self-change, `.github/**` path handling and exact `ci:final-gate` label detection have focused regressions.
- [x] `ci:final-gate` forces full Load/E2E and explicitly selects all main-CI scopes: Linux matrix, Windows, macOS, Docker, quickstart and runtime smokes.
- [x] PR is ready-for-review before the corrected final synchronize event, so Fast Checks and Lua checks cannot be draft-skipped.
- [x] Root policy and build matrix require batched docs/checkpoints and forbid a post-green final-gate commit.
- [x] No test, assertion, throttle, branch-protection gate or physical-client sentinel is weakened.

# Confirmed context

- Repository writes are limited to `blakinio/canary`; upstream/donor repositories remain read-only.
- PR #393 merged as `2f828672df010ff577c8e6076524b37c6dedd987` before this task.
- PR #415 is the live task PR from `ci/incremental-validation-final-gate` to `main` and is no longer draft.
- Full code head `2c6370418d0bd8d966289d5a1cf7c075ed75459f` passed Ownership #1626, CI #2763, Load #52 and physical E2E #96.
- Docs-only heads `9c02a95a6c7deb0d65c2c8a3956031c8ff2d9044`, `27163653e43454df9d51ee465143e5f3ab94ccf9` and `fe618730149d4a7d2c5d5ffa997f3935f4f08bc9` proved immediate-parent reuse while current-head Required gates remained green.
- E2E #94 had one transient failure in the unchanged pinned OTClient build; one allowed failed-job rerun on the same SHA passed without a code patch.
- Current main `368319e6e20672339a6409504d1a9f69c15ea077` was conservatively synchronized into the branch through verified Git objects because the connector has no native update-branch action.
- Merge commit `f529e34dc6b7c7c7a4e8c8fbfb820aff91705660` was verified before branch update: relative to current main it contains exactly the eleven intended PR paths; relative to the previous branch head it adds only the six new OTBM planner/archive files from main.
- Sync head `f529e34dc6b7c7c7a4e8c8fbfb820aff91705660` passed Ownership #1650, CI #2787, Load #56 including real status-smoke, and physical E2E #100 including DB, Canary, pinned OTClient and physical-client validation.
- The first labeled final head `59ed0e233250ef66a61aad548e803cf397a4598d` correctly forced full Load/E2E, but job-level inspection showed main CI heavy jobs were still skipped because the PR was draft and CI scopes still depended on path filters. That head was explicitly rejected as final merge evidence.
- PR #415 was marked ready before the corrective commit.
- Corrective head `4d4005958dd442dabaa4e992f020fd84c054abe4` makes `ci:final-gate` explicitly select all main-CI heavy scopes in addition to the helper's fail-closed decision.
- PR #415 still carries `ci:final-gate`, so this final task commit must trigger the corrected full gate on its exact SHA.

# Safety design

1. Normal synchronize decisions inspect only `HEAD^..HEAD`.
2. Reuse requires a non-impacting delta and successful latest same-workflow immediate-parent PR run.
3. Missing, non-success, empty or unresolvable evidence fails closed.
4. Relevant workflow/helper changes force full validation.
5. Focused current-head checks and stable Required aggregators remain active during reuse.
6. `ci:final-gate` forces full Load/E2E and all main-CI scopes; the PR must be non-draft so Fast Checks/Lua/heavy jobs execute.
7. No commit is allowed after the corrected final gate turns green; a later commit invalidates that evidence and must pass the full gate again.

# Current state

Implementation, tests, policy, catalogue, changelog and current-main synchronization are complete. A job-level final-gate audit found and repaired the last CI-scope/draft gap before merge. This task file is the final content commit. Exact final-head workflows under `ci:final-gate` are the remaining merge evidence.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T14:31:43+02:00
head: 4d4005958dd442dabaa4e992f020fd84c054abe4
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
  - Job-level inspection rejected 59ed0e233250ef66a61aad548e803cf397a4598d as final evidence because main CI heavy jobs were draft/path-filter skipped even though Load/E2E ran fully.
  - PR 415 is ready-for-review and still carries ci:final-gate before this corrected final commit.
derived:
  - Proven non-impacting immediate-parent reuse avoids repeated heavy work while the corrected labeled final synchronize preserves a full exact-final-head gate.
unknown:
  - Exact corrected final-head workflow results are pending on this final task commit under ci:final-gate.
conflicts: []
first_failure:
  marker: Agent Task Ownership 1555 / changed active task checkpoint validation
  evidence: Early task-record schema defects were repaired without weakening validation; helper compilation and focused tests remained green.
rejected_hypotheses:
  - Path filters alone solve docs-only reruns; pull_request path filters use cumulative PR scope inconsistently with the desired final-gate semantics.
  - Any older successful SHA is sufficient; reuse is immediate-parent only.
  - Helper force_full alone makes every main-CI scope execute; job-level evidence on 59ed0e23 disproved this and ci.yml now explicitly selects all scopes for ci:final-gate.
  - A draft PR can prove the full final main-CI gate; draft conditions skip Fast Checks/Lua/heavy jobs, so PR 415 was marked ready before the corrected final synchronize.
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
next_action: Verify the corrected full exact-head workflows triggered by this final task commit under ci:final-gate; if all are green, perform the live merge gate and squash-merge PR 415 without further commits.
```

## Automated lifecycle completion

- Feature PR: #415.
- Feature head: `67664c1fea87ae1010dad0e120476e5eec78d91c`.
- Merge commit: `0f25e7fd4d41e90f17fc95d13dba84b7e81d1681`.
- Merged at: `2026-07-16T17:59:36Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
- Lifecycle validation was retriggered on the cleanup branch after GitHub marked the bot-created `pull_request` runs as approval-required; no feature code changed.
