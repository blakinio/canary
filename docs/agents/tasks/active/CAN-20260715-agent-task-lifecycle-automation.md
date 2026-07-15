---
task_id: CAN-20260715-agent-task-lifecycle-automation
program_id: CAN-PROGRAM-AGENT-ORCHESTRATION
coordination_id: ""
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/agent-task-lifecycle-automation
base_branch: main
created: 2026-07-15T16:30:00Z
updated: 2026-07-15T16:30:00Z
last_verified_commit: "UNKNOWN"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260715-agent-context-orchestration-foundation
blocks:
  - ACO-003
  - ACO-004
owned_paths:
  exclusive:
    - tools/agents/task_lifecycle.py
    - tools/agents/test_task_lifecycle.py
    - docs/agents/TASK_LIFECYCLE.md
    - .github/workflows/agent-task-lifecycle.yml
    - .github/workflows/agent-task-ownership.yml
    - docs/agents/tasks/active/CAN-20260715-agent-task-lifecycle-automation.md
  shared:
    - docs/agents/programs/AGENT_CONTEXT_ORCHESTRATION_PROGRAM.md
    - docs/agents/CHANGELOG.md
    - docs/agents/CONTEXT_HANDOFF.md
  read_only:
    - tools/agents/task_ownership.py
    - tools/agents/checkpoint.py
    - tools/agents/test_task_ownership.py
    - tools/agents/test_context_orchestration.py
modules_touched:
  - agent-governance
  - agent-coordination
  - agent-tooling
reuses:
  - task_ownership.py frontmatter and active ownership contracts
  - checkpoint.py checkpoint parser and validator
  - Agent Task Ownership workflow
public_interfaces:
  - changed-active-task checkpoint CI validation
  - deterministic active-to-archive task lifecycle command
  - post-merge lifecycle automation PR workflow
cross_repo_tasks: []
---

# Goal

Implement ACO-002: enforce checkpoint quality only for active task records changed by a PR/push, detect lifecycle inconsistencies deterministically, and automatically create a bounded cleanup PR after a same-repository feature PR merges when its matching active task record still exists.

# Acceptance criteria

- [ ] Changed active task records are checkpoint-validated in Agent Task Ownership CI without forcing a repository-wide migration of untouched legacy tasks.
- [ ] Changed-task validation checks frontmatter/checkpoint consistency for branch, related PR when known, active status, and checkpoint validity.
- [ ] A deterministic lifecycle tool discovers active tasks by `related_pr` and archives only exact matches.
- [ ] Archive operation updates lifecycle metadata while preserving task evidence and never touches paths outside task roots.
- [ ] A post-merge workflow checks out trusted `main`, never the untrusted PR head, archives matching same-repository tasks, opens a cleanup PR, and enables normal auto-merge rather than bypassing branch protection.
- [ ] Focused tests cover changed-task validation, exact PR matching, archive metadata, no-match behavior, and path confinement.
- [ ] Existing ownership and orchestration tests remain green.
- [ ] Current-head CI and review gates pass before merge.

# Safety boundary

- Workflow writes only to `blakinio/canary` via the repository-scoped GitHub token.
- `pull_request_target` workflow must never checkout or execute the contributor PR head.
- Automation operates only on `docs/agents/tasks/active/*.md` records whose parsed `related_pr` exactly equals the merged PR number.
- Cleanup is delivered through a normal PR with CI/branch protection and auto-merge; no direct protected-branch push.
- No gameplay, runtime, datapack, map, OTBM, asset, production configuration, or cross-repository behavior changes.

# Overlap check

- Open PR #384 owns Universal Agent E2E load/stress paths and does not overlap the planned agent lifecycle tooling/workflows.
- Open PR #316 owns bounded Targuna OTBM donor audit paths and does not overlap the planned agent lifecycle tooling/workflows.
- ACO-001 is completed and archived by PR #390; no active ACO ownership remains.

# Plan

1. Add deterministic `task_lifecycle.py` with changed-task validation and exact-PR archive support.
2. Add focused tests.
3. Integrate changed-task checkpoint validation into Agent Task Ownership CI.
4. Add trusted post-merge lifecycle workflow that opens a cleanup PR and enables auto-merge.
5. Document lifecycle contract and update ACO program status.
6. Open draft PR early, fix CI, review exact diff, mark ready and merge only on current-head green gates.

# Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T16:30:00Z
head: UNKNOWN
branch: feat/agent-task-lifecycle-automation
pr: none
status: implementing
context_routes:
  - agent-governance
  - ci-repair
owned_paths:
  - tools/agents/task_lifecycle.py
  - tools/agents/test_task_lifecycle.py
  - docs/agents/TASK_LIFECYCLE.md
  - .github/workflows/agent-task-lifecycle.yml
  - .github/workflows/agent-task-ownership.yml
proven:
  - ACO-001 merged in PR 389 and lifecycle cleanup merged in PR 390
  - ACO-002 is the next queued package in CAN-PROGRAM-AGENT-ORCHESTRATION
  - stale active task records previously caused real ownership conflicts in PR 389
  - task_ownership.py and checkpoint.py provide reusable deterministic parsers and validators
  - open PR 384 and PR 316 do not own the planned ACO-002 paths
derived:
  - changed-task-only checkpoint enforcement can improve new work without forcing immediate migration of every historical active record
  - post-merge cleanup should use a normal PR and branch protection rather than direct writes to main
unknown:
  - exact CI behavior after workflow integration
  - whether the new post-merge workflow will trigger for its own first feature merge because it is introduced by that merge
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - validate every historical active task checkpoint immediately: rejected because it would create an unrelated migration blast radius
  - push archive changes directly to protected main: rejected because it bypasses normal review and CI gates
changed_paths:
  - docs/agents/tasks/active/CAN-20260715-agent-task-lifecycle-automation.md
validation:
  - command: repository preflight and overlap review
    result: PASS
    evidence: ACO program plus open PR 384 and 316 scopes reviewed
blockers:
  - none
next_action: Open draft PR, then implement deterministic lifecycle validation and archive tooling with focused tests.
```

# Completion

- Final status: implementing
- PR: pending
- Merge commit: pending
- Program record updated: pending
- Changelog updated: pending
- Archived at: pending after merge
