---
task_id: CAN-20260715-agent-multi-agent-supervisor-queue
program_id: CAN-PROGRAM-AGENT-ORCHESTRATION
coordination_id: ""
status: review
agent: "GPT-5.5 Thinking"
branch: feat/agent-multi-agent-supervisor-queue
base_branch: main
created: 2026-07-15T18:43:00Z
updated: 2026-07-15T18:48:00Z
last_verified_commit: "47ae4c7ec716567b9f68cc13ca6940b83756a8a1"
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
- [ ] Program record marks ACO-001 through ACO-004 complete after feature merge.
- [ ] Final ready-state CI and merge gates pass.

# Confirmed context

- Writable repository: `blakinio/canary` only.
- Task-start main: `554a34aaa328a10ed351f62406550f127dbd3092`.
- ACO-001 merged via PR #389.
- ACO-002 merged via PR #391 with repair PR #394 and production proof cleanup PR #397.
- ACO-003 merged via PR #400 and lifecycle cleanup PR #401.
- Open PR #393 concerns Universal E2E load/stress runtime paths; open PR #316 concerns Targuna OTBM audit paths. No ACO-004 exclusive-path overlap was identified.
- Ordinary Chat cannot be assumed to spawn external workers; ACO-004 is an advisory/planning interface for an explicitly capable orchestrator.
- The bootstrap marker used only to obtain PR #402 was removed before validation.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T18:48:00Z
head: 47ae4c7ec716567b9f68cc13ca6940b83756a8a1
branch: feat/agent-multi-agent-supervisor-queue
pr: 402
status: validating
context_routes:
  - agent-governance
owned_paths:
  - tools/agents/supervisor_queue.py
  - tools/agents/test_supervisor_queue.py
  - docs/agents/AGENT_SUPERVISOR_QUEUE.md
  - docs/agents/schemas/agent-supervisor-queue.schema.json
proven:
  - ACO 001 through ACO 003 feature packages and ACO 003 lifecycle cleanup are merged
  - ordinary Chat cannot be assumed to spawn external agents
  - supervisor queue implementation compiles and focused tests pass in Agent Task Ownership run 1424
  - changed-task checkpoint and ownership index validation pass in Agent Task Ownership run 1424
  - repository CI run 2556 Required passes on implementation head 47ae4c7ec716567b9f68cc13ca6940b83756a8a1
  - planner reuses bounded resume bundles and existing execution mode routing
  - planner serializes same-branch and overlapping non-read-only ownership claims
derived:
  - a repository-local queue planner can prepare safe bounded worker batches without becoming an execution engine
  - shared ownership surfaces should serialize for autonomous parallel workers even though coordinated shared edits are permitted
unknown:
  - final ready-state checks after this checkpoint update
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
  - command: Agent Task Ownership 1424
    result: PASS
    evidence: implementation head 47ae4c7ec716567b9f68cc13ca6940b83756a8a1
  - command: repository CI 2556 Required
    result: PASS
    evidence: implementation head 47ae4c7ec716567b9f68cc13ca6940b83756a8a1
blockers:
  - none
next_action: Verify the new current head, exact PR diff, comments and review threads; then mark PR 402 ready and merge only after final required checks pass.
```

# Completion

- Final status: review
- PR: #402
- Merge commit: pending
- Program record updated: yes; final completed state pending feature merge/lifecycle cleanup
- Changelog updated: not required; dedicated supervisor contract and ACO program record are authoritative
- Archived at: pending via lifecycle automation
