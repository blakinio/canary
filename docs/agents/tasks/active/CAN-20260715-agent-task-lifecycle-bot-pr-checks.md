---
task_id: CAN-20260715-agent-task-lifecycle-bot-pr-checks
program_id: CAN-PROGRAM-AGENT-ORCHESTRATION
coordination_id: ""
status: implementing
agent: "GPT-5.5 Thinking"
branch: fix/agent-task-lifecycle-bot-pr-checks
base_branch: main
created: 2026-07-15T17:00:00Z
updated: 2026-07-15T17:00:00Z
last_verified_commit: "783481f84aaaa24c683bdfeb43ff617a57a3a6e3"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260715-agent-task-lifecycle-automation
blocks:
  - ACO-003
  - ACO-004
owned_paths:
  exclusive:
    - .github/workflows/agent-task-lifecycle.yml
    - docs/agents/tasks/active/CAN-20260715-agent-task-lifecycle-bot-pr-checks.md
    - docs/agents/tasks/archive/CAN-20260715-agent-task-lifecycle-automation.md
    - docs/agents/tasks/active/CAN-20260715-agent-task-lifecycle-automation.md
  shared:
    - docs/agents/programs/AGENT_CONTEXT_ORCHESTRATION_PROGRAM.md
    - docs/agents/TASK_LIFECYCLE.md
    - docs/agents/CHANGELOG.md
  read_only:
    - .github/workflows/agent-task-ownership.yml
    - .github/workflows/ci.yml
    - tools/agents/task_lifecycle.py
modules_touched:
  - agent-governance
  - agent-coordination
reuses:
  - ACO-002 exact-PR lifecycle archive tooling
  - CI workflow_dispatch entrypoints
  - existing branch protection and auto-merge
public_interfaces:
  - automated lifecycle cleanup check dispatch
cross_repo_tasks: []
---

# Goal

Repair the first production ACO-002 lifecycle cleanup so PRs created by the repository `GITHUB_TOKEN` explicitly obtain required workflow checks through trusted `workflow_dispatch` runs on the cleanup head, while preserving normal branch protection and avoiding direct writes to `main`.

# Evidence

- PR #391 merged successfully as `0d47a18e2cf1e4d81a3c16f85947299bda4afc0e`.
- The new post-merge workflow created cleanup PR #392 from trusted `main` with one changed task record.
- On cleanup head `e61f6691e5bdd4440f3a00b3ca26493658ba5511`, both `Agent Task Ownership` #1389 and `CI` #2516 concluded `action_required`.
- Therefore ordinary PR-triggered checks are not sufficient for cleanup PRs created by the repository automation token.

# Acceptance criteria

- [ ] ACO-002 task is archived and removed from active ownership in this repair PR.
- [ ] Bot-generated cleanup PRs explicitly dispatch Agent Task Ownership and CI against their exact cleanup branch after creation.
- [ ] Auto-merge remains enabled only after dispatch; branch protection remains authoritative.
- [ ] Workflow still checks out trusted default branch and never the merged feature head.
- [ ] Cleanup dispatch is bounded to the newly created cleanup branch/PR.
- [ ] Documentation records the `GITHUB_TOKEN` recursion/check-trigger limitation and explicit dispatch behavior.
- [ ] Focused/current repository checks pass and repair PR merges.

# Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T17:00:00Z
head: UNKNOWN
branch: fix/agent-task-lifecycle-bot-pr-checks
pr: none
status: implementing
context_routes:
  - agent-governance
  - ci-repair
owned_paths:
  - .github/workflows/agent-task-lifecycle.yml
  - docs/agents/tasks/active/CAN-20260715-agent-task-lifecycle-bot-pr-checks.md
  - docs/agents/tasks/archive/CAN-20260715-agent-task-lifecycle-automation.md
  - docs/agents/tasks/active/CAN-20260715-agent-task-lifecycle-automation.md
proven:
  - PR 391 merged as 0d47a18e2cf1e4d81a3c16f85947299bda4afc0e
  - automated cleanup PR 392 was created from trusted main
  - PR 392 changes exactly one lifecycle task record
  - PR 392 head workflows Agent Task Ownership 1389 and CI 2516 concluded action_required
  - ACO-002 active task has been archived on this repair branch
derived:
  - cleanup automation must explicitly request trusted workflow_dispatch runs for its own bot-created PR head
unknown:
  - whether explicit workflow_dispatch check runs satisfy the repository required-check contexts on a bot-created cleanup PR
conflicts: []
first_failure:
  marker: cleanup PR required checks
  evidence: PR 392 head e61f6691e5bdd4440f3a00b3ca26493658ba5511 has action_required Agent Task Ownership 1389 and CI 2516
rejected_hypotheses:
  - merge bot cleanup PR without checks: rejected because branch protection must remain authoritative
  - direct push archive to main: rejected because it bypasses normal protected-branch lifecycle
changed_paths:
  - docs/agents/tasks/archive/CAN-20260715-agent-task-lifecycle-automation.md
  - docs/agents/tasks/active/CAN-20260715-agent-task-lifecycle-automation.md
  - docs/agents/tasks/active/CAN-20260715-agent-task-lifecycle-bot-pr-checks.md
validation:
  - command: PR 392 workflow state
    result: FAIL
    evidence: both required workflow runs concluded action_required
blockers:
  - explicit-dispatch repair not implemented yet
next_action: Open the repair PR, bind this task to it, update the lifecycle workflow to dispatch required workflows on the cleanup branch, and verify current-head CI.
```

# Completion

- Final status: implementing
- PR: pending
- Merge commit: pending
- Program record updated: pending
- Archived at: pending via repaired lifecycle automation
