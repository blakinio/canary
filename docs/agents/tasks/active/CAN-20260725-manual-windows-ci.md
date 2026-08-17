---
task_id: CAN-20260725-manual-windows-ci
program_id: none
status: implementing
agent: "GPT-5.6 Thinking"
branch: ci/linux-docker-only-builds
base_branch: main
created: 2026-07-25T23:00:00+02:00
updated: 2026-08-17T09:34:00+02:00
risk: medium
related_pr: "1071"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-manual-windows-ci.md
  shared:
    - .github/workflows/ci.yml
    - .github/workflows/release.yml
    - docs/agents/BUILD_TEST_MATRIX.md
  read_only:
    - .github/workflows/reusable-build-windows.yml
    - .github/workflows/reusable-build-macos.yml
modules_touched:
  - ci
public_interfaces:
  - CI workflow jobs
  - Release workflow jobs
cross_repo_tasks: []
---

# Goal

Correct the earlier Windows manual-opt-in policy from PR #946. Canary automated builds must use Linux and Docker only: no Windows or macOS build job may run from the normal `CI` workflow or the `Release` workflow.

# Scope

- Remove the `run_windows` manual-dispatch selector from `.github/workflows/ci.yml`.
- Remove the `build-windows` caller job and its `Required`-aggregator mapping from normal CI.
- Keep the existing macOS CI caller absent.
- Remove Windows and macOS build jobs from `.github/workflows/release.yml` and stop publishing their artifacts.
- Keep Linux and Docker build paths active.
- Keep reusable Windows/macOS workflow definitions unchanged and dormant so platform builds can be re-enabled explicitly in a future policy change without consuming runner capacity now.
- Update `docs/agents/BUILD_TEST_MATRIX.md` to match the enforced workflow policy.
- Do not change runtime, datapack, protocol, database, assets, Lua behavior, Linux build implementation, or Docker build implementation.

# Acceptance criteria

- [x] `CI` has no Windows or macOS build caller job.
- [x] `workflow_dispatch` cannot select a Windows/macOS build.
- [x] `Required` evaluates only build jobs that can actually be selected by the workflow.
- [x] `Release` has no Windows or macOS build job.
- [x] Release artifact publishing does not request Windows/macOS build artifacts.
- [x] Linux and Docker build jobs remain active.
- [x] Reusable Windows/macOS workflow definitions remain unchanged and uncalled by `CI`/`Release`.
- [ ] YAML validation and final exact-head GitHub Actions validation pass before merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-17T09:34:00+02:00
head: 723bdc7ac8cbf56c21900f0485487c4be7f2e525
branch: ci/linux-docker-only-builds
pr: 1071
status: validating
next_action: Mark PR 1071 ready for review and verify final-gate CI plus ownership on the exact final head.
context_routes:
  - agent-governance
  - ci
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-manual-windows-ci.md
  - .github/workflows/ci.yml
  - .github/workflows/release.yml
  - docs/agents/BUILD_TEST_MATRIX.md
proven:
  - PR 946 merged a manual opt-in Windows CI policy rather than disabling Windows completely.
  - PR 1071 diff removes run_windows, the CI build-windows caller, Windows scope evaluation, and the Required Windows dependency.
  - PR 1071 diff removes Release build-windows and build-macos callers, their publish dependencies, and their artifact downloads.
  - Draft CI run 32006011068 completed successfully and emitted Build - Linux, Build - Docker, Docker Quickstart Smoke, and Required with no Build - Windows or Build - macOS job.
  - Stale CAN-20260712-required-ci-gate ownership was archived because its implementation PR 197 is already merged.
derived:
  - The workflow caller graph represented by PR 1071 restricts automated build jobs to Linux and Docker.
unknown:
  - Exact final-head non-draft CI and ownership conclusions after this checkpoint commit.
  - Release workflow execution evidence; static workflow diff is verified but a release is not being published by this task.
conflicts: []
rejected_hypotheses:
  - Keep Windows available through manual workflow_dispatch.
  - Remove only the CI Windows caller while leaving Windows/macOS release builds active.
  - Delete reusable platform workflow definitions when disabling their callers is sufficient.
changed_paths:
  - .github/workflows/ci.yml
  - .github/workflows/release.yml
  - docs/agents/BUILD_TEST_MATRIX.md
  - docs/agents/tasks/active/CAN-20260712-required-ci-gate.md
  - docs/agents/tasks/active/CAN-20260725-manual-windows-ci.md
  - docs/agents/tasks/archive/CAN-20260712-required-ci-gate.md
first_failure:
  marker: agent-task-ownership-checkpoint-schema
  evidence: Run 32006010916 failed only at changed active task checkpoint validation because the first rewritten checkpoint used version 2 and omitted required head, pr, owned_paths, and first_failure fields.
validation:
  - command: Compare d1b7c6c9abe58d8e4e192ece3bb143c7141573e4 to ci/linux-docker-only-builds.
    result: PASS
    evidence: Six changed paths; ci.yml is 5 additions/25 deletions and release.yml is 1 addition/30 deletions with no unexpected runtime paths.
  - command: Inspect PR 1071 workflow patches.
    result: PASS
    evidence: CI removes run_windows/build-windows/Required Windows mapping; Release removes Windows/macOS jobs, publish dependencies, and artifact downloads.
  - command: Inspect draft CI run 32006011068 on head 723bdc7ac8cbf56c21900f0485487c4be7f2e525.
    result: PASS
    evidence: CI concluded success and its job list contains Linux/Docker build jobs only; heavy jobs were skipped because the PR was still draft.
  - command: Inspect Agent Task Ownership run 32006010916.
    result: FAIL
    evidence: The governance unit-test step passed 63 tests; changed-task validation then rejected the malformed checkpoint fields now corrected in this commit.
blockers: []
```
