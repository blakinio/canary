---
task_id: CAN-20260719-agent-task-lifecycle-app-token
program_id: CAN-PROGRAM-AGENT-GOVERNANCE
status: implementing
agent: "GPT-5.5 Thinking"
branch: ci/agent-task-lifecycle-app-token
base_branch: main
created: 2026-07-19T12:44:28+02:00
updated: 2026-07-19T12:45:35+02:00
last_verified_commit: "112a18d73f4131aa274f93b42ff4d470c6fb0849"
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

- [x] Generate a repository-scoped GitHub App installation token from `APP_CLIENT_ID` and `APP_PRIVATE_KEY` without committing either credential.
- [x] Use the GitHub App token for checkout credentials, lifecycle branch push, cleanup PR creation and cleanup auto-merge.
- [ ] Verify a cleanup PR created after merge starts normal required workflows without manual approval.
- [x] Remove the explicit required-check dispatch workaround so the GitHub App does not need Actions write permission and checks are not duplicated.
- [x] Preserve trusted-default-branch checkout, exact `related_pr` archival matching, branch protection and squash auto-merge behavior.
- [x] Keep the implementation change limited to the lifecycle workflow and this task record.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T12:45:35+02:00
head: 112a18d73f4131aa274f93b42ff4d470c6fb0849
branch: ci/agent-task-lifecycle-app-token
pr: UNKNOWN
status: implementing
next_action: Open the same-repository draft PR, bind this task record to the PR number and exact head, then validate workflow syntax and required checks before final-gate merge.
first_failure:
  marker: No failure observed at task start.
  evidence: Preflight and bounded implementation completed; PR validation has not run yet.
context_routes:
  - agent-governance
  - ci-repair
owned_paths:
  - docs/agents/tasks/active/CAN-20260719-agent-task-lifecycle-app-token.md
  - .github/workflows/agent-task-lifecycle.yml
proven:
  - The previous Agent Task Lifecycle workflow created cleanup PRs with github.token.
  - GitHub documents that pull_request workflows from GITHUB_TOKEN-created or updated PRs enter an approval-required state, while a GitHub App installation token can trigger them without that manual approval gate.
  - The user created and installed canary-automation-bot on blakinio/canary and stored APP_CLIENT_ID and APP_PRIVATE_KEY in repository Actions configuration.
  - The workflow now generates a current-repository GitHub App installation token with contents write and pull-requests write permissions.
  - Checkout persists the GitHub App token for lifecycle branch push and gh uses the same token for cleanup PR creation and auto-merge.
  - The redundant explicit workflow_dispatch step was removed, so the GitHub App does not require Actions write permission for this flow.
  - Current workflow cleanup operations remain confined to blakinio/canary and trusted main-derived lifecycle branches.
derived:
  - Normal pull_request events from the App-created cleanup PR should replace the previous explicit workflow_dispatch workaround.
unknown:
  - Exact CI and Agent Task Ownership conclusions on the implementation PR head.
  - End-to-end confirmation that the first post-merge App-created cleanup PR has no manual approval banner.
conflicts: []
rejected_hypotheses:
  - Disable branch protection or required checks.
  - Store the private key in the repository.
  - Grant the GitHub App Actions write permission solely to preserve redundant explicit workflow dispatches.
changed_paths:
  - docs/agents/tasks/active/CAN-20260719-agent-task-lifecycle-app-token.md
  - .github/workflows/agent-task-lifecycle.yml
blockers: []
validation:
  - command: Live workflow and open-PR ownership preflight
    result: PASS
    evidence: .github/workflows/agent-task-lifecycle.yml was inspected on current main; no open PR search result claimed agent-task-lifecycle.yml.
  - command: GitHub App token design review against official actions/create-github-app-token v3 contract
    result: PASS
    evidence: Current-repository token generation uses APP_CLIENT_ID and APP_PRIVATE_KEY and explicitly narrows the installation token to contents write and pull-requests write.
```
