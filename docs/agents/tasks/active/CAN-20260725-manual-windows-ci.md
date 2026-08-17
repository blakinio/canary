---
task_id: CAN-20260725-manual-windows-ci
program_id: none
status: implementing
agent: "GPT-5.6 Thinking"
branch: ci/linux-docker-only-builds
base_branch: main
created: 2026-07-25T23:00:00+02:00
updated: 2026-08-17T09:18:00+02:00
risk: medium
related_pr: ""
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

- [ ] `CI` has no Windows or macOS build caller job.
- [ ] `workflow_dispatch` cannot select a Windows/macOS build.
- [ ] `Required` evaluates only build jobs that can actually be selected by the workflow.
- [ ] `Release` has no Windows or macOS build job.
- [ ] Release artifact publishing does not request Windows/macOS build artifacts.
- [ ] Linux and Docker build jobs remain active.
- [ ] Reusable Windows/macOS workflow definitions remain unchanged and uncalled by `CI`/`Release`.
- [ ] YAML parses successfully for both changed workflow files.
- [ ] Exact emitted check names and final-head GitHub Actions runs are inspected before merge.

## Context checkpoint

```yaml
checkpoint_version: 2
updated_at: 2026-08-17T09:18:00+02:00
base_head: d1b7c6c9abe58d8e4e192ece3bb143c7141573e4
branch: ci/linux-docker-only-builds
status: implementing
context_routes:
  - agent-governance
  - ci
proven:
  - PR 946 merged a manual opt-in Windows CI policy rather than disabling Windows completely
  - current main CI still exposes workflow_dispatch input run_windows and can call reusable-build-windows.yml
  - current main release workflow still contains build-windows and build-macos jobs
  - current main release publishing still requests Windows and macOS artifacts
  - macOS caller is already absent from the normal CI workflow
  - stale CAN-20260712-required-ci-gate task corresponded to merged PR 197 and has been archived on this correction branch to release obsolete ci.yml ownership
derived:
  - the owner-requested Linux/Docker-only policy is not satisfied until both CI and Release stop invoking Windows/macOS builds
unknown:
  - final-head GitHub Actions result after implementation
conflicts: []
rejected_hypotheses:
  - keep Windows available through manual workflow_dispatch
  - remove only the CI Windows caller while leaving Windows/macOS release builds active
  - delete reusable platform workflow definitions when disabling their callers is sufficient
changed_paths:
  - docs/agents/tasks/archive/CAN-20260712-required-ci-gate.md
  - docs/agents/tasks/active/CAN-20260712-required-ci-gate.md
  - docs/agents/tasks/active/CAN-20260725-manual-windows-ci.md
validation:
  - command: fresh main/head and PR-state inspection
    result: PASS
    evidence: main d1b7c6c9abe58d8e4e192ece3bb143c7141573e4; PR 197 merged; PR 946 merged
blockers: []
next_action: Open an early draft PR, implement CI/Release Linux-Docker-only callers, validate YAML and emitted checks.
```
