# Agent Supervisor Queue

ACO-004 defines a deterministic queue and handoff contract for optional multi-agent execution by an external or higher-license orchestrator.

## Boundary

The repository planner does **not** spawn chats, Codex workers, Work sessions, processes, or worktrees. Ordinary Chat remains the coordinator when its connector capabilities are sufficient. The planner only validates a queue, resolves bounded task context through the existing ACO-001 tooling, identifies CHAT/CODEX/WORK placement, detects unsafe parallel overlaps, and emits deterministic batches for a capable external orchestrator.

All repository writes remain subject to task ownership, one-task/branch/PR discipline, CI, review and branch protection.

## Queue contract

The machine contract is `docs/agents/schemas/agent-supervisor-queue.schema.json`.

A queue contains:

- `schema_version: 1`;
- a unique `queue_id`;
- `budget_policy`, defaulting to `minimize_agentic_usage`;
- `max_parallel`, bounded from 1 through 16;
- optional already-completed item IDs;
- one to 64 bounded items referencing existing active task records.

Each item may declare dependencies and the same capability signals accepted by `resume.py`: local execution, broad research, large deliverable, parallel-worker value, GitHub-only work, changed paths, extra routes, and optional explicit target mode.

## Mode placement

The planner reuses `resume.build_resume_bundle()` and therefore the existing deterministic execution-mode advisor.

- `CHAT`: stays coordinator-side and is not emitted as an external worker dispatch.
- `CODEX`: emitted as a bounded worker candidate with a deterministic suggested worktree path.
- `WORK`: emitted as a bounded worker candidate without a repository worktree requirement.

A suggested worktree path is metadata only. The planner never creates it.

With `minimize_agentic_usage`, the planner does not spend CODEX/WORK capacity merely because parallel execution is possible. The underlying execution-mode policy must still justify the agentic mode.

## Parallel safety

Two external workers may share a batch only when all of these are true:

1. their declared dependencies are satisfied;
2. the batch does not exceed `max_parallel`;
3. their task branches differ;
4. none of their non-`read_only` ownership claims overlap under the existing conservative `task_ownership.patterns_overlap()` rule.

Both `exclusive` and `shared` claims are treated as write/coordination surfaces for parallel planning. This is intentionally more conservative than ownership-conflict validation: `shared` means coordinated edits are allowed, not that two autonomous workers should edit the surface concurrently without a supervisor decision.

Conflicting workers are serialized into later batches. Dependency cycles, unknown dependencies, missing/inactive task records, unsafe task paths, duplicate IDs, unsupported modes and invalid queue bounds fail closed.

## Dependency behavior

Dependencies listed in `completed` are already satisfied.

A CHAT coordinator item is treated as locally satisfiable for planning so downstream external work can be shown in the plan, but the external orchestrator must not actually dispatch a dependent batch until the coordinator has completed that prerequisite and checkpointed the result.

## Bounded worker prompt

Every CODEX or WORK candidate receives the compact prompt from `resume.py`, containing only routed required reads and bounded evidence:

- task/program identity;
- current checkpoint head/branch/PR/status;
- recommended mode and budget policy;
- required/search-first/optional context;
- PROVEN, UNKNOWN and CONFLICT evidence;
- first failure;
- changed paths and validation references;
- blockers;
- exactly one next action.

Full chat history, full logs, full diffs, whole source trees and whole-repository dumps are not part of the worker contract.

## Usage

```sh
python tools/agents/supervisor_queue.py path/to/queue.json
python tools/agents/supervisor_queue.py path/to/queue.json --json
```

The Markdown output is intended for human/supervisor review. JSON output is intended for an external orchestrator that already has explicit authority and capability to create isolated workers or worktrees.

## Example

```json
{
  "schema_version": 1,
  "queue_id": "CAN-QUEUE-EXAMPLE",
  "budget_policy": "minimize_agentic_usage",
  "max_parallel": 2,
  "completed": [],
  "items": [
    {
      "id": "runtime-fix",
      "task": "docs/agents/tasks/active/CAN-RUNTIME-FIX.md",
      "task_text": "Implement the bounded runtime fix and run focused tests",
      "depends_on": [],
      "target_mode": "auto",
      "needs_local_execution": true,
      "parallel_workers": true
    },
    {
      "id": "research-package",
      "task": "docs/agents/tasks/active/CAN-RESEARCH.md",
      "task_text": "Prepare the bounded multi-source research package",
      "depends_on": [],
      "target_mode": "auto",
      "broad_research": true,
      "large_deliverable": true
    }
  ]
}
```

The two items may appear in one batch only if their active-task ownership claims and branches do not overlap.

## Supervisor responsibilities

A capable external supervisor remains responsible for:

1. verifying live repository head, PR and ownership state before dispatch;
2. creating isolated branch/worktree/session state where supported;
3. sending only the generated bounded prompt and exact task paths;
4. collecting worker checkpoints/results;
5. stopping or serializing work when ownership changes or conflicts appear;
6. returning PR/CI/review/merge coordination to CHAT or another authorized coordinator;
7. never bypassing required checks or branch protection.

## Failure semantics

The queue planner is advisory and fail-closed. It does not claim that a worker actually exists, started, completed, or merged anything. Those facts remain `UNKNOWN` until proven by the external execution platform and live repository evidence.
