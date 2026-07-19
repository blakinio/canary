---
task_id: CAN-20260719-agent-task-lifecycle-app-token
program_id: CAN-PROGRAM-AGENT-GOVERNANCE
status: implementing
agent: "GPT-5.5 Thinking"
branch: ci/agent-task-lifecycle-app-token
base_branch: main
created: 2026-07-19T12:44:28+02:00
updated: 2026-07-19T12:44:28+02:00
last_verified_commit: "7b517aec1dfe9e89befc68a53d7aece383098623"
risk: medium
related_issue: ""
related_pr: ""
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260719-agent-task-lifecycle-app-token.md
    - .github/workflows/agent-task-lifecycle.yml
modules_touched:
  - Agent Task Lifecycle
reuses:
  - existing post-merge agent-task lifecycle workflow
  - actions/create-github-app-token
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Remove the manual `Approve workflows to run` gate from automation-created agent-task lifecycle cleanup pull requests by authenticating cleanup branch/PR operations with the repository-installed `canary-automation-bot` GitHub App instead of the workflow `GITHUB_TOKEN`.

# Acceptance criteria

- [ ] Generate a repository-scoped GitHub App installation token from `APP_CLIENT_ID` and `APP_PRIVATE_KEY` without committing either credential.
- [ ] Use the GitHub App token for checkout credentials, lifecycle branch push, cleanup PR creation and cleanup auto-merge.
- [ ] Let normal cleanup-PR `pull_request` events trigger required checks without manual approval.
- [ ] Remove the explicit required-check dispatch workaround so the GitHub App does not need Actions write permission and checks are not duplicated.
- [ ] Preserve trusted-default-branch checkout, exact `related_pr` archival matching, branch protection and squash auto-merge behavior.
- [ ] Keep the change limited to the lifecycle workflow and this task record.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T12:44:28+02:00
head: UNKNOWN
branch: ci/agent-task-lifecycle-app-token
pr: UNKNOWN
status: implementing
next_action: Update .github/workflows/agent-task-lifecycle.yml to generate and use the GitHub App installation token, remove the explicit workflow-dispatch workaround, then open the same-repository draft PR and bind this task record to it.
first_failure:
  marker: No failure observed at task start.
  evidence: Preflight only; implementation and CI have not run yet.
context_routes:
  - agent-governance
  - ci-repair
owned_paths:
  - docs/agents/tasks/active/CAN-20260719-agent-task-lifecycle-app-token.md
  - .github/workflows/agent-task-lifecycle.yml
proven:
  - The current Agent Task Lifecycle workflow creates cleanup PRs with github.token.
  - GitHub documents that pull_request workflows from GITHUB_TOKEN-created or updated PRs enter an approval-required state, while a GitHub App installation token can trigger them without that manual approval gate.
  - The user created and installed canary-automation-bot on blakinio/canary and stored APP_CLIENT_ID and APP_PRIVATE_KEY in repository Actions configuration.
  - Current workflow cleanup operations are confined to blakinio/canary and trusted main-derived lifecycle branches.
derived:
  - Using the GitHub App token for branch push and PR creation removes the reason for the explicit workflow_dispatch workaround.
unknown:
  - Exact CI and Agent Task Ownership conclusions on the implementation PR head.
conflicts: []
rejected_hypotheses:
  - Disable branch protection or required checks.
  - Store the private key in the repository.
  - Grant the GitHub App Actions write permission solely to preserve redundant explicit workflow dispatches.
changed_paths:
  - docs/agents/tasks/active/CAN-20260719-agent-task-lifecycle-app-token.md
blockers: []
validation:
  - command: Live workflow and open-PR ownership preflight
    result: PASS
    evidence: .github/workflows/agent-task-lifecycle.yml was inspected on current main; no open PR search result claimed agent-task-lifecycle.yml.
next_action: Update .github/workflows/agent-task-lifecycle.yml to generate and use the GitHub App installation token, remove the explicit workflow-dispatch workaround, then open the same-repository draft PR and bind this task record to it.
```
