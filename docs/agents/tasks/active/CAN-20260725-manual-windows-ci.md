---
task_id: CAN-20260725-manual-windows-ci
status: implementing
agent: "GPT-5.6 Thinking"
branch: ci/manual-windows-build-20260725
base_branch: main
created: 2026-07-25T23:00:00+02:00
updated: 2026-07-25T23:00:00+02:00
risk: medium
related_pr: ""
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - .github/workflows/ci.yml
    - docs/agents/tasks/active/CAN-20260725-manual-windows-ci.md
  shared: []
  read_only:
    - .github/workflows/reusable-build-windows.yml
modules_touched:
  - ci
reuses:
  - reusable-build-windows workflow
public_interfaces:
  - CI workflow_dispatch input run_windows
cross_repo_tasks: []
---

# Goal

Keep Canary Docker/Linux validation as the normal CI path and run the Windows build only when explicitly requested from the manual CI workflow dispatch form.

# Scope

- Add a boolean manual-dispatch input for Windows validation.
- Stop selecting the Windows build on pull requests and pushes to `main`.
- Keep the existing reusable Windows workflow unchanged.
- Keep the stable `Required` aggregator active and require Windows success only when the manual input selects it.
- Do not change Linux, Docker, Lua, formatting or runtime-smoke implementation.

# Acceptance criteria

- [ ] Ordinary pull requests do not run `Build - Windows`.
- [ ] Pushes to `main` do not run `Build - Windows`.
- [ ] Manual `CI` dispatch exposes a `run_windows` boolean input, disabled by default.
- [ ] Manual dispatch with `run_windows=true` runs the existing Windows workflow.
- [ ] `Required` accepts a skipped Windows job unless Windows was explicitly selected.
- [ ] YAML and exact check-name logic are reviewed.
- [ ] Current-head CI passes before merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T23:00:00+02:00
branch: ci/manual-windows-build-20260725
status: implementing
context_routes:
  - agent-governance
owned_paths:
  - .github/workflows/ci.yml
  - docs/agents/tasks/active/CAN-20260725-manual-windows-ci.md
proven:
  - current CI invokes reusable-build-windows.yml through the build-windows job
  - current full_matrix scope selects Windows on workflow_dispatch, main pushes and ci:final-gate
  - the Required aggregator currently maps build-windows to full_matrix
  - no open PR inspected owns .github/workflows/ci.yml
unknown:
  - current-head emitted check behavior after the workflow edit
conflicts: []
first_failure: null
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-manual-windows-ci.md
validation:
  - command: repository and workflow preflight
    result: PASS
    evidence: current main workflow and recent CI run inspected
blockers: []
next_action: Edit ci.yml to add the manual Windows selector and update Required scope mapping.
```
