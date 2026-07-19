---
task_id: CAN-20260719-agent-task-lifecycle-app-token
program_id: CAN-PROGRAM-AGENT-GOVERNANCE
status: ready
agent: "GPT-5.5 Thinking"
branch: ci/agent-task-lifecycle-app-token
base_branch: main
created: 2026-07-19T12:44:28+02:00
updated: 2026-07-19T12:50:30+02:00
last_verified_commit: "6a0876493a57de6da17bc83e3f13bfdb9f64cf22"
risk: medium
related_issue: ""
related_pr: "582"
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
- [x] Replace the approval-prone `GITHUB_TOKEN` cleanup-PR creation path with the GitHub App installation-token path documented by GitHub for automatically triggered follow-on workflows.
- [x] Remove the explicit required-check dispatch workaround so the GitHub App does not need Actions write permission and checks are not duplicated.
- [x] Preserve trusted-default-branch checkout, exact `related_pr` archival matching, branch protection and squash auto-merge behavior.
- [x] Keep the implementation change limited to the lifecycle workflow and this task record.

The first cleanup PR created after this workflow reaches `main` is the post-merge end-to-end observation point for confirming the approval banner is absent; that observation does not require another implementation commit.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T12:50:30+02:00
head: 6a0876493a57de6da17bc83e3f13bfdb9f64cf22
branch: ci/agent-task-lifecycle-app-token
pr: 582
status: ready
next_action: Wait for the exact-final-head Agent Task Ownership and CI runs triggered by this final checkpoint commit, then verify unchanged two-file scope, review state, mergeability and main drift and squash-merge PR #582 with expected head.
first_failure:
  marker: No implementation failure observed before the final gate.
  evidence: Preflight, bounded diff review and GitHub App token contract review all passed; prior current-head workflows were queued when the final-gate checkpoint was prepared.
context_routes:
  - agent-governance
  - ci-repair
owned_paths:
  - docs/agents/tasks/active/CAN-20260719-agent-task-lifecycle-app-token.md
  - .github/workflows/agent-task-lifecycle.yml
proven:
  - The previous Agent Task Lifecycle workflow created cleanup PRs with github.token.
  - GitHub documents that pull_request workflows from GITHUB_TOKEN-created or updated PRs enter an approval-required state and recommends a GitHub App installation access token or PAT when approval-free workflow-created PR runs are required.
  - The user created and installed canary-automation-bot on blakinio/canary and stored APP_CLIENT_ID and APP_PRIVATE_KEY in repository Actions configuration.
  - The workflow now generates a current-repository GitHub App installation token with contents write and pull-requests write permissions.
  - Checkout persists the GitHub App token for lifecycle branch push and gh uses the same token for cleanup PR creation and auto-merge.
  - The redundant explicit workflow_dispatch step was removed, so the GitHub App does not require Actions write permission for this flow.
  - Current workflow cleanup operations remain confined to blakinio/canary and trusted main-derived lifecycle branches.
  - PR #582 is the same-repository draft PR with base main and head ci/agent-task-lifecycle-app-token.
  - PR #582 changes exactly .github/workflows/agent-task-lifecycle.yml and this active task record.
  - PR #582 has no review comments, submitted reviews or review threads at the final-gate checkpoint.
  - The branch was zero commits behind main at the final-gate checkpoint and PR #582 was mergeable.
  - ci:final-gate was applied before this final checkpoint commit.
derived:
  - Normal pull_request events from the App-created cleanup PR replace the previous explicit workflow_dispatch workaround.
unknown:
  - Exact-final-head CI and Agent Task Ownership conclusions after this final checkpoint commit.
  - Post-merge end-to-end observation of the first cleanup PR created by canary-automation-bot.
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
  - command: PR #582 changed-file and patch review
    result: PASS
    evidence: Exactly the lifecycle workflow and this task record change; explicit CI/ownership dispatches are removed and all branch push, PR creation and auto-merge authentication uses the App token.
  - command: PR #582 ownership and mergeability pre-final-gate review
    result: PASS
    evidence: No comments, reviews or review threads; branch behind_by 0; PR mergeable true before the final checkpoint commit.
```
