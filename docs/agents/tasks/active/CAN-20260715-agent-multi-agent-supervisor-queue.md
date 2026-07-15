---
task_id: CAN-20260715-agent-multi-agent-supervisor-queue
program_id: CAN-PROGRAM-AGENT-ORCHESTRATION
coordination_id: ""
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/agent-multi-agent-supervisor-queue
base_branch: main
created: 2026-07-15T18:43:00Z
updated: 2026-07-15T18:43:00Z
last_verified_commit: "6142d2d7396ffd1a4bcc584d97d979d0c8caf9ee"
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
    - docs/agents/tasks/active/.aco004-pr-bootstrap
  shared:
    - .github/workflows/agent-task-ownership.yml
    - docs/agents/programs/AGENT_CONTEXT_ORCHESTRATION_PROGRAM.md
    - docs/agents/CHANGELOG.md
  read_only:
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

- [ ] Queue schema bounds item count, parallelism, task paths, modes and dependency metadata.
- [ ] Standard-library planner reuses `resume.py` and existing execution-mode routing.
- [ ] CHAT items remain coordinator-side; only CODEX/WORK become external worker candidates.
- [ ] Non-read-only ownership overlap and same-branch work serialize conservatively.
- [ ] Dependency order and completed prerequisites are deterministic and cycles fail closed.
- [ ] CODEX candidates receive suggested worktree metadata without creating worktrees.
- [ ] Worker prompts remain bounded and exclude full chat/log/source/repository dumps.
- [ ] Focused tests cover parallel batching, overlap serialization, dependencies, CHAT placement, cycles, same-branch safety and bounded prompts.
- [ ] Agent Task Ownership CI compiles and runs supervisor queue tests.
- [ ] Program record marks ACO-001 through ACO-004 complete after feature merge.
- [ ] Current-head CI and merge gates pass.

# Confirmed context

- Writable repository: `blakinio/canary` only.
- Task-start main: `554a34aaa328a10ed351f62406550f127dbd3092`.
- ACO-001 merged via PR #389.
- ACO-002 merged via PR #391 with repair PR #394 and production proof cleanup PR #397.
- ACO-003 merged via PR #400 and lifecycle cleanup PR #401.
- Open PR #393 concerns Universal E2E load/stress runtime paths; open PR #316 concerns Targuna OTBM audit paths. No planned ACO-004 exclusive-path overlap was identified.
- Ordinary Chat cannot be assumed to spawn external workers; ACO-004 is an advisory/planning interface for an explicitly capable orchestrator.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T18:43:00Z
head: 6142d2d7396ffd1a4bcc584d97d979d0c8caf9ee
branch: feat/agent-multi-agent-supervisor-queue
pr: 402
status: implementing
context_routes:
  - agent-governance
owned_paths:
  - tools/agents/supervisor_queue.py
  - tools/agents/test_supervisor_queue.py
  - docs/agents/AGENT_SUPERVISOR_QUEUE.md
  - docs/agents/schemas/agent-supervisor-queue.schema.json
proven:
  - ACO 001 through ACO 003 feature packages are merged
  - ACO 003 lifecycle cleanup PR 401 merged successfully
  - ordinary Chat cannot be assumed to spawn external agents
  - existing resume tooling emits bounded CHAT CODEX WORK handoffs
  - existing ownership tooling provides conservative path overlap detection
derived:
  - a repository-local queue planner can prepare safe bounded worker batches without becoming an execution engine
  - shared ownership surfaces should serialize for autonomous parallel workers even though coordinated shared edits are permitted
unknown:
  - current-head ACO 004 CI after final integration
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - repository tool should spawn agents directly: rejected because execution capability is platform-dependent and ordinary Chat does not provide that guarantee
  - parallelize shared ownership edits by default: rejected because shared permits coordination but does not prove concurrent autonomous writes are safe
changed_paths:
  - docs/agents/AGENT_SUPERVISOR_QUEUE.md
  - docs/agents/schemas/agent-supervisor-queue.schema.json
  - tools/agents/supervisor_queue.py
  - tools/agents/test_supervisor_queue.py
validation:
  - command: ACO 003 lifecycle cleanup PR 401
    result: PASS
    evidence: merged as 554a34aaa328a10ed351f62406550f127dbd3092
blockers:
  - none
next_action: Integrate supervisor queue tests into Agent Task Ownership CI, update the ACO program, remove the bootstrap marker, and validate PR 402.
```

# Completion

- Final status: implementing
- PR: #402
- Merge commit: pending
- Program record updated: pending
- Changelog updated: pending
- Archived at: pending via lifecycle automation
