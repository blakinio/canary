---
task_id: CAN-20260715-agent-multi-agent-supervisor-queue
program_id: CAN-PROGRAM-AGENT-ORCHESTRATION
coordination_id: ""
status: completed
agent: "GPT-5.5 Thinking"
branch: feat/agent-multi-agent-supervisor-queue
base_branch: main
created: 2026-07-15T18:43:00Z
updated: 2026-07-15T18:56:04Z
last_verified_commit: "f170d604e1657e3d81c38363c59027d20423e39d"
risk: low
related_issue: ""
related_pr: "402"
depends_on:
  - CAN-20260715-agent-efficiency-evals
blocks: []
owned_paths:
  exclusive:
    - tools/agents/supervisor_queue.py
    - tools/agents/test_supervisor_queue.py
    - docs/agents/AGENT_SUPERVISOR_QUEUE.md
    - docs/agents/schemas/agent-supervisor-queue.schema.json
    - docs/agents/tasks/active/CAN-20260715-agent-multi-agent-supervisor-queue.md
  shared:
    - .github/workflows/agent-task-ownership.yml
    - docs/agents/programs/AGENT_CONTEXT_ORCHESTRATION_PROGRAM.md
  read_only:
    - docs/agents/CHANGELOG.md
    - tools/agents/resume.py
    - tools/agents/context.py
    - tools/agents/execution_mode.py
    - tools/agents/task_ownership.py
    - tools/agents/task_lifecycle.py
modules_touched:
  - agent-governance
  - agent-coordination
  - agent-supervision
reuses:
  - ACO-001 bounded resume and execution-mode routing
  - ACO-002 task lifecycle and ownership validation
  - ACO-003 efficiency evaluation contract
  - Python 3.12 standard library only
public_interfaces:
  - deterministic supervisor queue schema
  - bounded CHAT CODEX WORK batch plan
cross_repo_tasks: []
completed: 2026-07-15T18:56:04Z
---

# Goal

Deliver ACO-004: a deterministic optional supervisor queue that allows an external or higher-license orchestrator to consume bounded Canary task handoffs safely, while ordinary Chat remains the default coordinator and the repository itself never pretends to spawn workers.

# Acceptance criteria

- [x] Queue schema bounds item count, parallelism, task paths, modes and dependency metadata.
- [x] Standard-library planner reuses `resume.py` and existing execution-mode routing.
- [x] CHAT items remain coordinator-side; only CODEX/WORK become external worker candidates.
- [x] Non-read-only ownership overlap and same-branch work serialize conservatively.
- [x] Dependency order and completed prerequisites are deterministic and cycles fail closed.
- [x] CODEX candidates receive suggested worktree metadata without creating worktrees.
- [x] Worker prompts remain bounded and exclude full chat/log/source/repository dumps.
- [x] Focused tests cover parallel batching, overlap serialization, dependencies, CHAT placement, cycles, same-branch safety and bounded prompts.
- [x] Agent Task Ownership CI compiles and runs supervisor queue tests.
- [x] Program record marks ACO-001 through ACO-004 complete in lifecycle PR #403.
- [x] Final ready-state CI and merge gates passed before feature merge.

# Confirmed context

- Writable repository: `blakinio/canary` only.
- Task-start main: `554a34aaa328a10ed351f62406550f127dbd3092`.
- ACO-001 merged via PR #389.
- ACO-002 merged via PR #391 with repair PR #394 and production proof cleanup PR #397.
- ACO-003 merged via PR #400 and lifecycle cleanup PR #401.
- ACO-004 feature PR #402 merged as `f170d604e1657e3d81c38363c59027d20423e39d` after final ready-state CI #2558 passed.
- Ordinary Chat cannot be assumed to spawn external workers; ACO-004 is an advisory/planning interface for an explicitly capable orchestrator.
- The bootstrap marker used only to obtain PR #402 was removed before validation.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T18:56:04Z
head: 3d4eb75ca69f25f2d86301df1023eb9e50a9d158
branch: feat/agent-multi-agent-supervisor-queue
pr: 402
status: ready
context_routes:
  - agent-governance
owned_paths:
  - tools/agents/supervisor_queue.py
  - tools/agents/test_supervisor_queue.py
  - docs/agents/AGENT_SUPERVISOR_QUEUE.md
  - docs/agents/schemas/agent-supervisor-queue.schema.json
proven:
  - ACO 001 through ACO 003 feature packages and ACO 003 lifecycle cleanup are merged
  - ACO 004 feature PR 402 merged as f170d604e1657e3d81c38363c59027d20423e39d
  - ordinary Chat cannot be assumed to spawn external agents
  - supervisor queue implementation compiles and focused tests pass in Agent Task Ownership run 1425
  - changed-task checkpoint and ownership index validation pass in Agent Task Ownership run 1425
  - ready-state repository CI run 2558 Required passed before merge
  - planner reuses bounded resume bundles and existing execution mode routing
  - planner serializes same-branch and overlapping non-read-only ownership claims
derived:
  - a repository-local queue planner can prepare safe bounded worker batches without becoming an execution engine
  - shared ownership surfaces should serialize for autonomous parallel workers even though coordinated shared edits are permitted
unknown: []
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - repository tool should spawn agents directly: rejected because execution capability is platform-dependent and ordinary Chat does not provide that guarantee
  - parallelize shared ownership edits by default: rejected because shared permits coordination but does not prove concurrent autonomous writes are safe
changed_paths:
  - .github/workflows/agent-task-ownership.yml
  - docs/agents/AGENT_SUPERVISOR_QUEUE.md
  - docs/agents/programs/AGENT_CONTEXT_ORCHESTRATION_PROGRAM.md
  - docs/agents/schemas/agent-supervisor-queue.schema.json
  - tools/agents/supervisor_queue.py
  - tools/agents/test_supervisor_queue.py
validation:
  - command: Agent Task Ownership 1425
    result: PASS
    evidence: feature head 3d4eb75ca69f25f2d86301df1023eb9e50a9d158
  - command: repository CI 2558 Required
    result: PASS
    evidence: feature head 3d4eb75ca69f25f2d86301df1023eb9e50a9d158
  - command: feature PR 402 auto merge
    result: PASS
    evidence: merged as f170d604e1657e3d81c38363c59027d20423e39d
blockers:
  - none
next_action: Merge lifecycle PR 403 after its current-head required checks pass; then verify no ACO task remains active.
```

# Completion

- Final status: completed
- PR: #402
- Merge commit: `f170d604e1657e3d81c38363c59027d20423e39d`
- Program record updated: yes; final ACO-001 through ACO-004 completion state is included in lifecycle PR #403
- Changelog updated: not required; dedicated supervisor contract and ACO program record are authoritative
- Archived at: `docs/agents/tasks/archive/CAN-20260715-agent-multi-agent-supervisor-queue.md`

## Automated lifecycle completion

- Feature PR: #402.
- Feature head: `3d4eb75ca69f25f2d86301df1023eb9e50a9d158`.
- Merge commit: `f170d604e1657e3d81c38363c59027d20423e39d`.
- Merged at: `2026-07-15T18:56:04Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
- Lifecycle PR #403 also atomically records final ACO program completion.
