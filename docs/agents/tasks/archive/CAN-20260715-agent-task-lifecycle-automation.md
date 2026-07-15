---
task_id: CAN-20260715-agent-task-lifecycle-automation
program_id: CAN-PROGRAM-AGENT-ORCHESTRATION
coordination_id: ""
status: completed
agent: "GPT-5.5 Thinking"
branch: feat/agent-task-lifecycle-automation
base_branch: main
created: 2026-07-15T16:30:00Z
updated: 2026-07-15T16:56:37Z
last_verified_commit: "0d47a18e2cf1e4d81a3c16f85947299bda4afc0e"
risk: medium
related_issue: ""
related_pr: "391"
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
completed: 2026-07-15T16:56:37Z
---

# Goal

Implement ACO-002: enforce checkpoint quality only for active task records changed by a PR/push, detect lifecycle inconsistencies deterministically, and automatically create a bounded cleanup PR after a same-repository feature PR merges when its matching active task record still exists.

# Acceptance criteria

- [x] Changed active task records are checkpoint-validated in Agent Task Ownership CI without forcing a repository-wide migration of untouched legacy tasks.
- [x] Changed-task validation checks frontmatter/checkpoint consistency for branch, current/related PR, active status, ownership and checkpoint validity.
- [x] A deterministic lifecycle tool discovers active tasks by `related_pr` and archives only exact matches.
- [x] Archive operation updates lifecycle metadata while preserving task evidence and never touches paths outside task roots.
- [x] A post-merge workflow checks out trusted `main`, never the untrusted PR head, archives matching same-repository tasks, opens a cleanup PR, and enables normal auto-merge rather than bypassing branch protection.
- [x] Focused tests cover changed-task validation, current-PR binding, exact PR matching, archive metadata, no-match behavior, and path confinement.
- [x] Existing ownership and orchestration tests remain green on current-head CI.
- [ ] Ready-state branch-protection checks pass and PR merges.

# Safety boundary

- Workflow writes only to `blakinio/canary` via the repository-scoped GitHub token.
- `pull_request_target` workflow never checks out or executes the contributor PR head.
- Automation operates only on `docs/agents/tasks/active/*.md` records whose parsed `related_pr` exactly equals the merged PR number.
- Cleanup is delivered through a normal PR with CI/branch protection and auto-merge; no direct protected-branch push.
- Generic automation does not rewrite free-form program records.
- No gameplay, runtime, datapack, map, OTBM, asset, production configuration, or cross-repository behavior changes.

# Overlap check

- Open PR #384 owns Universal Agent E2E load/stress paths and does not overlap the planned agent lifecycle tooling/workflows.
- Open PR #316 owns bounded Targuna OTBM donor audit paths and does not overlap the planned agent lifecycle tooling/workflows.
- ACO-001 is completed and archived by PR #390; no active ACO ownership remains.

# Plan

1. Add deterministic `task_lifecycle.py` with changed-task validation and exact-PR archive support. — completed.
2. Add focused tests. — completed.
3. Integrate changed-task checkpoint validation into Agent Task Ownership CI. — completed.
4. Add trusted post-merge lifecycle workflow that opens a cleanup PR and enables auto-merge. — completed.
5. Document lifecycle contract, changelog and ACO program state. — completed.
6. Complete final ready-state CI and merge. — in progress.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T16:48:00Z
head: 31ccd23641fced92d9a54c06da82deac7a6bc9d3
branch: feat/agent-task-lifecycle-automation
pr: 391
status: ready
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
  - PR 391 is the ACO-002 feature PR
  - stale active task records previously caused real ownership conflicts in PR 389
  - task_lifecycle.py reuses task_ownership.py and checkpoint.py rather than introducing duplicate parsers
  - changed active tasks are bound to the current PR in pull request CI
  - lifecycle archive selection uses exact parsed related_pr equality
  - post-merge workflow checks out trusted default branch and never the feature head
  - cleanup is delivered through a normal PR with auto-merge instead of direct main push
  - Agent Task Ownership 1385 passes on head 31ccd23641fced92d9a54c06da82deac7a6bc9d3
  - repository CI 2511 passes on head 31ccd23641fced92d9a54c06da82deac7a6bc9d3
  - open PR 384 and PR 316 do not own the ACO-002 paths
derived:
  - changed-task-only checkpoint enforcement improves new work without forcing immediate migration of every historical active record
  - exact related_pr matching plus path confinement limits automated archive scope
unknown:
  - ready-state branch-protection result after final task and program checkpoint updates
  - whether the new post-merge workflow will trigger for its own first feature merge because it is introduced by that merge
conflicts: []
first_failure:
  marker: none
  evidence: earlier changed-task heading failure is resolved and Agent Task Ownership 1385 passes
rejected_hypotheses:
  - lifecycle unit tests caused the ownership failure: rejected because the focused unit-test step passed
  - validate every historical active task checkpoint immediately: rejected because it would create an unrelated migration blast radius
  - push archive changes directly to protected main: rejected because it bypasses normal review and CI gates
  - auto-edit free-form program records after every merge: rejected because generic semantics cannot be inferred safely
changed_paths:
  - .github/workflows/agent-task-lifecycle.yml
  - .github/workflows/agent-task-ownership.yml
  - docs/agents/CHANGELOG.md
  - docs/agents/TASK_LIFECYCLE.md
  - docs/agents/programs/AGENT_CONTEXT_ORCHESTRATION_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260715-agent-task-lifecycle-automation.md
  - tools/agents/task_lifecycle.py
  - tools/agents/test_task_lifecycle.py
validation:
  - command: Agent Task Ownership 1385
    result: PASS
    evidence: compile, focused tests, changed-task validation and ownership index all passed
  - command: repository CI 2511
    result: PASS
    evidence: Required gate passed on 31ccd23641fced92d9a54c06da82deac7a6bc9d3
  - command: changed-task diagnostic artifact
    result: PASS
    evidence: canonical double-hash Context checkpoint heading now validates
blockers:
  - final ready-state branch-protection checks pending
next_action: Update the ACO program to ready, review PR 391 exact diff and review threads, then mark ready and merge only after current-head required checks pass.
```

# Completion

- Final status: ready
- PR: #391
- Merge commit: pending
- Program record updated: yes
- Changelog updated: yes
- Archived at: expected from post-merge lifecycle automation or one-time manual fallback

## Automated lifecycle completion

- Feature PR: #391.
- Feature head: `2e3271d62b99d1dddbc919ccc7041966a14eb587`.
- Merge commit: `0d47a18e2cf1e4d81a3c16f85947299bda4afc0e`.
- Merged at: `2026-07-15T16:56:37Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
