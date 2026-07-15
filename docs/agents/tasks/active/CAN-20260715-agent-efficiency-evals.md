---
task_id: CAN-20260715-agent-efficiency-evals
program_id: CAN-PROGRAM-AGENT-ORCHESTRATION
coordination_id: ""
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/agent-efficiency-evals
base_branch: main
created: 2026-07-15T17:35:00Z
updated: 2026-07-15T17:35:00Z
last_verified_commit: "ec7c767cf93e00f3631441193fbef34da302882a"
risk: low
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260715-agent-task-lifecycle-automation
blocks:
  - CAN-20260715-agent-multi-agent-supervisor-queue
owned_paths:
  exclusive:
    - tools/agents/efficiency_eval.py
    - tools/agents/test_efficiency_eval.py
    - docs/agents/AGENT_EFFICIENCY_EVAL.md
    - docs/agents/schemas/agent-efficiency-trace.schema.json
    - docs/agents/tasks/active/CAN-20260715-agent-efficiency-evals.md
  shared:
    - .github/workflows/agent-task-ownership.yml
    - docs/agents/programs/AGENT_CONTEXT_ORCHESTRATION_PROGRAM.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/agents/context.py
    - tools/agents/resume.py
    - tools/agents/checkpoint.py
    - tools/agents/execution_mode.py
    - tools/agents/task_lifecycle.py
modules_touched:
  - agent-governance
  - agent-evaluation
reuses:
  - ACO-001 routed context and execution-mode policy
  - ACO-002 lifecycle and changed-task validation
  - Python 3.12 standard library only
public_interfaces:
  - deterministic agent efficiency trace schema
  - baseline versus routed-run comparison report
cross_repo_tasks: []
---

# Goal

Deliver ACO-003: deterministic, repository-local efficiency evaluation for agent sessions so Canary can measure whether routed context and handoffs reduce unnecessary reads/tool calls while preserving successful continuation.

# Acceptance criteria

- [ ] JSON trace schema defines bounded run events without storing full prompts, chats, source files, logs or secrets.
- [ ] Standard-library evaluator validates traces and reports files read, unique files, repeated reads, tool calls, time to first action, context expansions, optional-context loads and handoff success.
- [ ] Comparator supports baseline versus routed cohorts and reports deltas without inventing token counts that the platform does not expose.
- [ ] Evaluator can emit JSON and concise Markdown summaries.
- [ ] Focused tests cover validation, metrics, repeated reads, time-to-first-action, handoff success and cohort comparison.
- [ ] Agent Task Ownership CI compiles and runs the evaluator tests.
- [ ] Program record marks ACO-002 production proof complete and ACO-003 delivered after merge.
- [ ] Current-head CI and merge gates pass.

# Confirmed context

- Writable repository: `blakinio/canary` only.
- Task-start main: `ec7c767cf93e00f3631441193fbef34da302882a`.
- ACO-002 feature PR #391 merged as `0d47a18e2cf1e4d81a3c16f85947299bda4afc0e`.
- ACO-002 repair PR #394 merged as `2a8105760fe56c9d470b8b762f93711803e96633`.
- Automated production cleanup PR #397 merged as `075949166ca2af66cea468a4edd55f8ef7d66697`, proving the repaired lifecycle can create a bot cleanup PR, dispatch required checks and merge through branch protection.
- Open PR #393 owns Universal E2E load/stress paths; open PR #316 owns Targuna OTBM audit paths. Planned ACO-003 paths do not overlap those scopes.

# Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T17:35:00Z
head: ec7c767cf93e00f3631441193fbef34da302882a
branch: feat/agent-efficiency-evals
pr: none
status: implementing
context_routes:
  - agent-governance
owned_paths:
  - tools/agents/efficiency_eval.py
  - tools/agents/test_efficiency_eval.py
  - docs/agents/AGENT_EFFICIENCY_EVAL.md
  - docs/agents/schemas/agent-efficiency-trace.schema.json
proven:
  - ACO 002 repair production cleanup PR 397 merged successfully
  - task-start main is ec7c767cf93e00f3631441193fbef34da302882a
  - open PR 393 concerns Universal E2E load stress and PR 316 concerns Targuna OTBM audit
  - exact platform token counts are not exposed to repository tooling and must not be invented
derived:
  - repository-local trace metrics can measure context efficiency without collecting full conversations
  - repeated reads and time-to-first-action are useful observable proxies for agent overhead
unknown:
  - current-head CI after implementation
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - store full prompts or chat transcripts for evaluation: rejected because durable metrics do not require sensitive or bloated conversation content
changed_paths:
  - docs/agents/tasks/active/CAN-20260715-agent-efficiency-evals.md
validation:
  - command: production lifecycle proof PR 397
    result: PASS
    evidence: merged as 075949166ca2af66cea468a4edd55f8ef7d66697
blockers:
  - none
next_action: Implement the bounded trace schema and standard-library efficiency evaluator with focused tests.
```

# Completion

- Final status: implementing
- PR: pending
- Merge commit: pending
- Program record updated: pending
- Changelog updated: pending
- Archived at: pending via lifecycle automation
