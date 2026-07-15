---
task_id: CAN-20260715-agent-context-orchestration-foundation
program_id: CAN-PROGRAM-AGENT-ORCHESTRATION
coordination_id: ""
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/agent-context-orchestration-foundation
base_branch: main
created: 2026-07-15T16:00:00Z
updated: 2026-07-15T16:00:00Z
last_verified_commit: "42a4d4a41829ecdd66b360e9847c21b6368d8393"
risk: low
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260715-agent-context-routing-handoff
blocks: []
owned_paths:
  exclusive:
    - tools/agents/context.py
    - tools/agents/resume.py
    - tools/agents/checkpoint.py
    - tools/agents/execution_mode.py
    - tools/agents/test_context_orchestration.py
    - docs/agents/CONTEXT_ROUTES.json
    - docs/agents/EXECUTION_MODE_ROUTING.md
    - docs/agents/programs/AGENT_CONTEXT_ORCHESTRATION_PROGRAM.md
    - docs/agents/tasks/active/CAN-20260715-agent-context-orchestration-foundation.md
    - docs/agents/tasks/archive/CAN-20260715-agent-context-routing-handoff.md
    - docs/agents/tasks/active/CAN-20260715-agent-context-routing-handoff.md
    - .github/workflows/agent-task-ownership.yml
  shared:
    - AGENTS.md
    - docs/agents/CONTEXT_ROUTING.md
    - docs/agents/CONTEXT_HANDOFF.md
    - docs/agents/CHANGELOG.md
  read_only:
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/BUILD_TEST_MATRIX.md
    - tools/agents/task_ownership.py
    - tools/agents/test_task_ownership.py
modules_touched:
  - agent-governance
  - agent-coordination
  - agent-tooling
reuses:
  - merged lean context routing and checkpoint contract from PR #385
  - existing task frontmatter parser and ownership workflow patterns
  - Python 3.12 standard library only
public_interfaces:
  - machine-readable agent context routing
  - compact continuation prompt generation
  - checkpoint quality validation
  - execution-mode and agentic-budget recommendation
cross_repo_tasks: []
---

# Goal

Automate the merged context-routing and handoff policy so Chat, Codex and Work receive the smallest useful context, continuation agents can resume without old chat history, and expensive agentic modes are recommended only when their execution capability justifies their limited usage budget.

# Acceptance criteria

- [ ] Machine-readable route configuration exists beside the human routing contract.
- [ ] `context.py` resolves minimal required/optional context from task routes and task state.
- [ ] `resume.py` emits a compact continuation/evidence bundle without full chat history.
- [ ] `checkpoint.py` validates required checkpoint fields, evidence-state separation and exactly one concrete `next_action`.
- [ ] `execution_mode.py` recommends CHAT, CODEX or WORK with explicit rationale and `minimize_agentic_usage` as the default budget policy.
- [ ] Codex/Work escalation bundles are bounded and avoid rediscovery of already-PROVEN facts.
- [ ] Agent Task Ownership CI compiles and tests the new tooling.
- [ ] Focused unit tests cover routing, budget-aware mode choice, checkpoint validation and resume output.
- [ ] Existing PR #385 stale active task is archived so ownership state reflects the merged result.
- [ ] Current-head GitHub checks pass and autonomous merge gate is satisfied.

# Confirmed context

- Writable repository: `blakinio/canary` only.
- Task-start `main`: `42a4d4a41829ecdd66b360e9847c21b6368d8393`.
- PR #385 merged as `9f388e1a79802e7d507842883aeb04d1c9ffc7a2` but its active task record remained stale on `main`; this task archives it as a direct prerequisite to reusing the same agent-governance paths.
- Open PR #384 owns Universal E2E load/stress work; open PR #316 owns bounded Targuna OTBM donor audit. No overlap with the planned `tools/agents/**` orchestration files was identified.
- `AGENTS.md`, `CONTEXT_ROUTING.md` and `CONTEXT_HANDOFF.md` already define lean startup and durable handoff; this task automates those rules rather than replacing them.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| PR #385 | Lean routing/handoff policy | `AGENTS.md`, `docs/agents/CONTEXT_ROUTING.md`, `docs/agents/CONTEXT_HANDOFF.md` | Canonical human contract to automate |
| Agent ownership tooling | Frontmatter and CI conventions | `tools/agents/task_ownership.py`, `.github/workflows/agent-task-ownership.yml` | Existing standard-library tooling and focused test workflow |
| Task records | Durable state | `docs/agents/tasks/active/**` | Existing source of truth for continuation |

# Ownership and overlap check

- Program: `CAN-PROGRAM-AGENT-ORCHESTRATION` (created by this task).
- Open PRs inspected: #384 and #316; no planned-path overlap identified.
- Stale merged-task overlap: PR #385 task record still claimed the same governance paths but no longer represents live work; it is archived in this branch before new implementation.
- Exclusive claims: new orchestration tools/config/program/task and the directly related PR #385 lifecycle cleanup.
- Shared claims: root/routing/handoff/changelog narrow integration edits.
- Resolution: proceed with bounded agent-governance/tooling work only.

# Current state

Task branch created from current `main`; stale PR #385 task lifecycle cleanup is committed. New orchestration task is now authoritative for the implementation branch.

# Plan

1. Create durable program record and machine-readable route/mode policy.
2. Implement checkpoint parsing/validation and budget-aware execution-mode advisor.
3. Implement minimal-context resolver and compact resume/evidence-bundle generator.
4. Add focused tests and Agent Task Ownership CI coverage.
5. Update human contracts narrowly, review exact diff, fix CI, and merge only on current-head green checks.

# Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T16:00:00Z
head: 00f7291e757f2b14262a0efc54388beb8f24bec7
branch: feat/agent-context-orchestration-foundation
pr: none
status: implementing
context_routes:
  - agent-governance
  - ci-repair
owned_paths:
  - tools/agents/context.py
  - tools/agents/resume.py
  - tools/agents/checkpoint.py
  - tools/agents/execution_mode.py
  - tools/agents/test_context_orchestration.py
  - docs/agents/CONTEXT_ROUTES.json
  - docs/agents/EXECUTION_MODE_ROUTING.md
  - docs/agents/programs/AGENT_CONTEXT_ORCHESTRATION_PROGRAM.md
  - .github/workflows/agent-task-ownership.yml
proven:
  - PR 385 merged as 9f388e1a79802e7d507842883aeb04d1c9ffc7a2
  - stale PR 385 active task was archived and removed on this branch
  - task-start main is 42a4d4a41829ecdd66b360e9847c21b6368d8393
  - open PR 384 concerns E2E load stress and PR 316 concerns Targuna OTBM donor audit
  - Python 3.12 standard-library tooling already exists under tools/agents
  - user requires CHAT-first cost optimization and minimal Codex Work token usage
  - user wants the agent to suggest when CHAT CODEX or WORK is more efficient
derived:
  - a machine resolver can reduce repeated documentation discovery while retaining the human contracts as authoritative
  - Codex and Work should receive bounded evidence bundles rather than repository-wide context
unknown:
  - current-head CI after implementation
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - preload full repository context for Codex or Work: rejected because agentic usage limits are intentionally scarce
changed_paths:
  - docs/agents/tasks/archive/CAN-20260715-agent-context-routing-handoff.md
  - docs/agents/tasks/active/CAN-20260715-agent-context-routing-handoff.md
  - docs/agents/tasks/active/CAN-20260715-agent-context-orchestration-foundation.md
validation:
  - command: live GitHub preflight
    result: PASS
    evidence: writable repository and open PR scopes verified
blockers:
  - none
next_action: Create the program record and machine-readable route plus execution-mode policy, then implement focused standard-library tooling.
```

# Completion

- Final status: implementing
- PR: pending
- Merge commit: pending
- Program record updated: pending
- Catalogue updated: not expected unless a reusable runtime/public interface is introduced
- Changelog updated: pending
- Archived at: pending after merge
