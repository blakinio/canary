---
task_id: CAN-20260725-manual-windows-ci
status: validating
agent: "GPT-5.6 Thinking"
branch: ci/manual-windows-build-20260725
base_branch: main
created: 2026-07-25T23:00:00+02:00
updated: 2026-07-25T23:44:00+02:00
risk: medium
related_pr: "946"
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

- [x] Ordinary pull requests do not run `Build - Windows`.
- [x] Pushes to `main` do not run `Build - Windows`.
- [x] Manual `CI` dispatch exposes a `run_windows` boolean input, disabled by default.
- [x] Manual dispatch with `run_windows=true` selects the existing Windows workflow.
- [x] `Required` accepts a skipped Windows job unless Windows was explicitly selected.
- [x] YAML and exact check-name logic are reviewed.
- [ ] Current-head CI passes before merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T23:44:00+02:00
head: b0b54150ba59366bd211cd168f6f11c291627813
branch: ci/manual-windows-build-20260725
pr: "946"
status: validating
context_routes:
  - agent-governance
owned_paths:
  - .github/workflows/ci.yml
  - docs/agents/tasks/active/CAN-20260725-manual-windows-ci.md
proven:
  - current CI invokes reusable-build-windows.yml through the build-windows job
  - run_windows is a boolean workflow_dispatch input with default false
  - build-windows now depends on the dedicated windows scope instead of full_matrix
  - the Required aggregator maps build-windows to the dedicated windows scope
  - PR run 30176156378 passed and Build - Windows was skipped while Required succeeded
  - changed files are limited to ci.yml and this task record
derived:
  - pull requests and main pushes cannot select Windows because the windows scope is true only for workflow_dispatch with run_windows true
  - Linux full_matrix behavior remains independent from the Windows selector
unknown:
  - post-merge manual run_windows true runtime evidence
conflicts: []
rejected_hypotheses:
  - keep Windows coupled to full_matrix and rely on path filters
changed_paths:
  - .github/workflows/ci.yml
  - docs/agents/tasks/active/CAN-20260725-manual-windows-ci.md
first_failure:
  marker: checkpoint-schema-missing-fields
  evidence: Agent Task Ownership run 30176156288 rejected the initial task checkpoint before workflow ownership validation
validation:
  - command: inspect PR diff and changed-file list
    result: PASS
    evidence: PR 946 contains only ci.yml and the bounded task record
  - command: CI pull_request run
    result: PASS
    evidence: run 30176156378; Required passed and Build - Windows was skipped
  - command: checkpoint schema repair
    result: PASS
    evidence: all required checkpoint fields are now present for the final ownership run
blockers: []
next_action: Wait for exact-final-head CI and ownership, then mark PR 946 ready and squash-merge without further commits.
```
