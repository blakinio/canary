---
task_id: CAN-20260715-agent-efficiency-evals
program_id: CAN-PROGRAM-AGENT-ORCHESTRATION
coordination_id: ""
status: review
agent: "GPT-5.5 Thinking"
branch: feat/agent-efficiency-evals
base_branch: main
created: 2026-07-15T17:35:00Z
updated: 2026-07-15T18:12:00Z
last_verified_commit: "f06b333e9a1b3d8a8716671e0cc0afdb92c0b7f5"
risk: low
related_issue: ""
related_pr: "400"
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
  read_only:
    - docs/agents/CHANGELOG.md
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

- [x] JSON trace schema defines bounded run events without storing full prompts, chats, source files, logs or secrets.
- [x] Standard-library evaluator validates traces and reports files read, unique files, repeated reads, tool calls, time to first action, context expansions, optional-context loads and handoff success.
- [x] Comparator supports baseline versus routed cohorts and reports deltas without inventing token counts that the platform does not expose.
- [x] Evaluator can emit JSON and concise Markdown summaries.
- [x] Focused tests cover validation, metrics, repeated reads, time-to-first-action, handoff success and cohort comparison.
- [x] Agent Task Ownership CI compiles and runs the evaluator tests.
- [x] Program record marks ACO-002 production proof complete and ACO-003 as the current bounded package.
- [ ] Current-head CI and merge gates pass.

# Confirmed context

- Writable repository: `blakinio/canary` only.
- Task-start main: `ec7c767cf93e00f3631441193fbef34da302882a`.
- ACO-002 feature PR #391 merged as `0d47a18e2cf1e4d81a3c16f85947299bda4afc0e`.
- ACO-002 repair PR #394 merged as `2a8105760fe56c9d470b8b762f93711803e96633`.
- Automated production cleanup PR #397 merged as `075949166ca2af66cea468a4edd55f8ef7d66697`, proving the repaired lifecycle can create a bot cleanup PR, dispatch required checks and merge through branch protection.
- Open PR #393 owns Universal E2E load/stress paths; open PR #316 owns Targuna OTBM audit paths. ACO-003 paths do not overlap those scopes.
- ACO-003 implementation is standard-library only and stores metric metadata rather than full conversations or source contents.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T18:12:00Z
head: f06b333e9a1b3d8a8716671e0cc0afdb92c0b7f5
branch: feat/agent-efficiency-evals
pr: 400
status: validating
context_routes:
  - agent-governance
  - ci-repair
owned_paths:
  - tools/agents/efficiency_eval.py
  - tools/agents/test_efficiency_eval.py
  - docs/agents/AGENT_EFFICIENCY_EVAL.md
  - docs/agents/schemas/agent-efficiency-trace.schema.json
proven:
  - ACO 002 repair production cleanup PR 397 merged successfully
  - task-start main is ec7c767cf93e00f3631441193fbef34da302882a
  - open PR 393 concerns Universal E2E load stress and PR 316 concerns Targuna OTBM audit
  - exact platform token counts are not exposed to repository tooling and are not inferred by the evaluator
  - evaluator and tests are integrated into Agent Task Ownership workflow
  - focused efficiency evaluator unit tests passed in ownership runs 1413 and 1414 before task contract validation
  - program record now treats ACO 002 production proof as complete and ACO 003 as current
derived:
  - repository-local trace metrics can measure context efficiency without collecting full conversations
  - repeated reads and time-to-first-action are useful observable proxies for agent overhead
unknown:
  - current-head CI and ownership result after frontmatter status repair
conflicts: []
first_failure:
  marker: none
  evidence: implementation tests pass; changed-task frontmatter status is repaired to review with checkpoint status validating
rejected_hypotheses:
  - evaluator implementation caused ownership failures 1413 or 1414: disproven because compile and focused tests passed before changed-task validation
  - store full prompts or chat transcripts for evaluation: rejected because durable metrics do not require sensitive or bloated conversation content
  - invent exact token savings: rejected because repository tooling has no authoritative exact token or credit source
changed_paths:
  - .github/workflows/agent-task-ownership.yml
  - docs/agents/AGENT_EFFICIENCY_EVAL.md
  - docs/agents/programs/AGENT_CONTEXT_ORCHESTRATION_PROGRAM.md
  - docs/agents/schemas/agent-efficiency-trace.schema.json
  - docs/agents/tasks/active/CAN-20260715-agent-efficiency-evals.md
  - tools/agents/efficiency_eval.py
  - tools/agents/test_efficiency_eval.py
validation:
  - command: production lifecycle proof PR 397
    result: PASS
    evidence: merged as 075949166ca2af66cea468a4edd55f8ef7d66697
  - command: Agent Task Ownership 1414 focused unit tests
    result: PASS
    evidence: compile and focused unit tests completed before frontmatter status validation failed
  - command: Agent Task Ownership current head
    result: NOT_RUN
    evidence: pending after frontmatter status repair
  - command: repository CI current head
    result: NOT_RUN
    evidence: pending after frontmatter status repair
blockers:
  - current-head CI and merge gate pending
next_action: Verify PR 400 current-head ownership and CI, fix any failure, review exact diff and threads, then mark ready and merge only on green required gates.
```

# Completion

- Final status: review
- PR: #400
- Merge commit: pending
- Program record updated: yes
- Changelog updated: not required; program and dedicated evaluation contract are authoritative for ACO-003
- Archived at: pending via lifecycle automation
