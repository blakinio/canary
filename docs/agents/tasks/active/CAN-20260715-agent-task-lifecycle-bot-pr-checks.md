---
task_id: CAN-20260715-agent-task-lifecycle-bot-pr-checks
program_id: CAN-PROGRAM-AGENT-ORCHESTRATION
coordination_id: ""
status: implementing
agent: "GPT-5.5 Thinking"
branch: fix/agent-task-lifecycle-bot-pr-checks
base_branch: main
created: 2026-07-15T17:00:00Z
updated: 2026-07-15T17:06:00Z
last_verified_commit: "c8135fade0581f12b860cef8b2637b019bd07665"
risk: medium
related_issue: ""
related_pr: "394"
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
- PR #392 is closed without merge and replaced by repair PR #394.

# Acceptance criteria

- [x] ACO-002 task is archived and removed from active ownership in this repair PR.
- [x] Bot-generated cleanup PRs explicitly dispatch Agent Task Ownership and CI against their exact cleanup branch after creation.
- [x] Auto-merge remains enabled only after dispatch; branch protection remains authoritative.
- [x] Workflow still checks out trusted default branch and never the merged feature head.
- [x] Cleanup dispatch is bounded to the newly created cleanup branch/PR.
- [x] Documentation records the `GITHUB_TOKEN` recursion/check-trigger limitation and explicit dispatch behavior.
- [ ] Current-head and ready-state checks pass and repair PR merges.
- [ ] Real post-merge cleanup for PR #394 proves explicit dispatch and automatic merge end to end.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T17:06:00Z
head: c8135fade0581f12b860cef8b2637b019bd07665
branch: fix/agent-task-lifecycle-bot-pr-checks
pr: 394
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
  - PR 392 was closed without merge and repair continues in PR 394
  - lifecycle workflow now explicitly dispatches agent-task-ownership.yml and ci.yml on the exact cleanup branch before enabling auto-merge
  - TASK_LIFECYCLE documents the first production failure and fail-closed explicit dispatch behavior
derived:
  - explicit workflow_dispatch preserves protected cleanup PRs while avoiding dependence on recursive PR events from GITHUB_TOKEN
unknown:
  - whether explicit workflow_dispatch check runs satisfy the repository required-check contexts on the real cleanup PR generated after PR 394 merges
conflicts: []
first_failure:
  marker: cleanup PR required checks
  evidence: PR 392 head e61f6691e5bdd4440f3a00b3ca26493658ba5511 has action_required Agent Task Ownership 1389 and CI 2516
rejected_hypotheses:
  - merge bot cleanup PR without checks: rejected because branch protection must remain authoritative
  - direct push archive to main: rejected because it bypasses normal protected-branch lifecycle
changed_paths:
  - .github/workflows/agent-task-lifecycle.yml
  - docs/agents/TASK_LIFECYCLE.md
  - docs/agents/programs/AGENT_CONTEXT_ORCHESTRATION_PROGRAM.md
  - docs/agents/tasks/archive/CAN-20260715-agent-task-lifecycle-automation.md
  - docs/agents/tasks/active/CAN-20260715-agent-task-lifecycle-automation.md
  - docs/agents/tasks/active/CAN-20260715-agent-task-lifecycle-bot-pr-checks.md
validation:
  - command: PR 392 workflow state
    result: FAIL
    evidence: both required workflow runs concluded action_required
  - command: PR 394 CI 2522
    result: PASS
    evidence: repository CI passed before checkpoint heading correction
  - command: PR 394 Agent Task Ownership 1395
    result: FAIL
    evidence: focused tests passed; changed-task validator found single-hash Context checkpoint heading
blockers:
  - current-head ownership and ready-state checks pending after canonical heading fix
next_action: Verify PR 394 current-head ownership and CI, review exact diff and threads, then mark ready and auto-merge only on green gates; afterwards verify the generated cleanup PR end to end.
```

# Completion

- Final status: implementing
- PR: #394
- Merge commit: pending
- Program record updated: yes
- Archived at: pending via repaired lifecycle automation
