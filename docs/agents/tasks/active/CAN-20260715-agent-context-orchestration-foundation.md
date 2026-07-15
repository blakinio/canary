---
task_id: CAN-20260715-agent-context-orchestration-foundation
program_id: CAN-PROGRAM-AGENT-ORCHESTRATION
coordination_id: ""
status: validating
agent: "GPT-5.5 Thinking"
branch: feat/agent-context-orchestration-foundation
base_branch: main
created: 2026-07-15T16:00:00Z
updated: 2026-07-15T15:59:22Z
last_verified_commit: "e7cb0a388d627b31888b92b2c1537b5bab7c3a5a"
risk: low
related_issue: ""
related_pr: "389"
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
    - docs/agents/tasks/archive/CAN-20260713-agent-program-ownership.md
    - docs/agents/tasks/active/CAN-20260713-agent-program-ownership.md
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

- [x] Machine-readable route configuration exists beside the human routing contract.
- [x] `context.py` resolves minimal required/optional context from task routes and task state.
- [x] `resume.py` emits a compact continuation/evidence bundle without full chat history.
- [x] `checkpoint.py` validates required checkpoint fields, evidence-state separation and exactly one concrete `next_action`.
- [x] `execution_mode.py` recommends CHAT, CODEX or WORK with explicit rationale and `minimize_agentic_usage` as the default budget policy.
- [x] Codex/Work escalation bundles are bounded and avoid rediscovery of already-PROVEN facts.
- [x] Agent Task Ownership CI compiles and tests the new tooling.
- [x] Focused unit tests cover routing, budget-aware mode choice, checkpoint validation and resume output.
- [x] Existing PR #385 stale active task is archived so ownership state reflects the merged result.
- [x] Existing merged PR #222 stale ownership task is archived so the ownership workflow is not falsely locked.
- [ ] Current-head GitHub checks pass and autonomous merge gate is satisfied.

# Confirmed context

- Writable repository: `blakinio/canary` only.
- Task-start `main`: `42a4d4a41829ecdd66b360e9847c21b6368d8393`.
- PR #385 merged as `9f388e1a79802e7d507842883aeb04d1c9ffc7a2` but its active task record remained stale on `main`; this task archives it as a direct prerequisite to reusing the same agent-governance paths.
- PR #222 merged as `e1519a76c2e33cbd3726bec460f0b2f815a7333f` but its active task record remained `status: ready` and still exclusively claimed `.github/workflows/agent-task-ownership.yml`; this stale record caused the first ownership failure on PR #389 and is now archived.
- Open PR #384 owns Universal E2E load/stress work; open PR #316 owns bounded Targuna OTBM donor audit. No overlap with the planned `tools/agents/**` orchestration files was identified.
- `AGENTS.md`, `CONTEXT_ROUTING.md` and `CONTEXT_HANDOFF.md` already define lean startup and durable handoff; this task automates those rules rather than replacing them.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| PR #385 | Lean routing/handoff policy | `AGENTS.md`, `docs/agents/CONTEXT_ROUTING.md`, `docs/agents/CONTEXT_HANDOFF.md` | Canonical human contract to automate |
| Agent ownership tooling | Frontmatter and CI conventions | `tools/agents/task_ownership.py`, `.github/workflows/agent-task-ownership.yml` | Existing standard-library tooling and focused test workflow |
| Task records | Durable state | `docs/agents/tasks/active/**` | Existing source of truth for continuation |

# Ownership and overlap check

- Program: `CAN-PROGRAM-AGENT-ORCHESTRATION`.
- Open PRs inspected: #384 and #316; no planned-path overlap identified.
- Stale merged-task overlap #385: archived and removed from active tasks on this branch.
- Stale merged-task overlap #222: archived and removed from active tasks on this branch after ownership run #1361 proved its obsolete exclusive workflow claim blocked current work.
- Exclusive claims: new orchestration tools/config/program/task, the ownership workflow integration, and the two directly related stale lifecycle cleanups.
- Shared claims: root/routing/handoff/changelog narrow integration edits.
- Resolution: proceed with bounded agent-governance/tooling work only; do not weaken ownership validation.

# Current state

Implementation is complete. Current validation head before this checkpoint update was `e7cb0a388d627b31888b92b2c1537b5bab7c3a5a`: focused orchestration tests and ownership-tool compilation passed, Agent Task Ownership #1363 passed, and repository CI #2488 was still in progress.

# Plan

1. Create durable program record and machine-readable route/mode policy. — completed.
2. Implement checkpoint parsing/validation and budget-aware execution-mode advisor. — completed.
3. Implement minimal-context resolver and compact resume/evidence-bundle generator. — completed.
4. Add focused tests and Agent Task Ownership CI coverage. — completed.
5. Update human contracts narrowly. — completed.
6. Review exact diff, current-base sync, CI, comments/reviews/threads and merge only on current-head green checks. — in progress.

# Work log

## 2026-07-15T15:52Z

- PROVEN: first `Agent Task Ownership` run #1361 failed only at `Validate tasks and render ownership index`; compile and focused unit tests passed.
- PROVEN: active merged task `CAN-20260713-agent-program-ownership` from PR #222 still had `status: ready` and an exclusive claim on `.github/workflows/agent-task-ownership.yml`.
- PROVEN: PR #222 was merged on 2026-07-12 with merge commit `e1519a76c2e33cbd3726bec460f0b2f815a7333f`.
- Changed: archived the stale PR #222 task and removed its active record; no ownership rule was weakened.
- Result: `Agent Task Ownership` run #1363 passed on head `e7cb0a388d627b31888b92b2c1537b5bab7c3a5a`.

# Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T15:59:22Z
head: e7cb0a388d627b31888b92b2c1537b5bab7c3a5a
branch: feat/agent-context-orchestration-foundation
pr: 389
status: validating
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
  - PR 385 merged as 9f388e1a79802e7d507842883aeb04d1c9ffc7a2 and its stale active task is archived on this branch
  - PR 222 merged as e1519a76c2e33cbd3726bec460f0b2f815a7333f and its stale active ownership task is archived on this branch
  - task-start main is 42a4d4a41829ecdd66b360e9847c21b6368d8393
  - open PR 384 concerns E2E load stress and PR 316 concerns Targuna OTBM donor audit
  - Python 3.12 standard-library tooling exists under tools/agents and focused orchestration unit tests pass in Agent Task Ownership CI
  - Agent Task Ownership run 1363 passed on e7cb0a388d627b31888b92b2c1537b5bab7c3a5a
  - user requires CHAT-first cost optimization and minimal Codex Work token usage
  - user wants the agent to suggest when CHAT CODEX or WORK is more efficient
derived:
  - a machine resolver can reduce repeated documentation discovery while retaining the human contracts as authoritative
  - Codex and Work should receive bounded evidence bundles rather than repository-wide context
  - stale completed task records can falsely hold exclusive locks and must be archived instead of weakening conflict detection
unknown:
  - final current-head repository CI result after the checkpoint update
conflicts: []
first_failure:
  marker: none
  evidence: ownership failure 1361 is resolved by stale task lifecycle cleanup and run 1363 passes
rejected_hypotheses:
  - tooling compile or focused unit tests caused ownership run 1361 failure: disproven because both steps passed before ownership index validation failed
  - weaken exclusive ownership conflict detection: rejected because the conflicting task was already merged and stale
  - preload full repository context for Codex or Work: rejected because agentic usage limits are intentionally scarce
changed_paths:
  - .github/workflows/agent-task-ownership.yml
  - docs/agents/CHANGELOG.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/CONTEXT_ROUTES.json
  - docs/agents/CONTEXT_ROUTING.md
  - docs/agents/EXECUTION_MODE_ROUTING.md
  - docs/agents/programs/AGENT_CONTEXT_ORCHESTRATION_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260715-agent-context-orchestration-foundation.md
  - docs/agents/tasks/archive/CAN-20260715-agent-context-routing-handoff.md
  - docs/agents/tasks/archive/CAN-20260713-agent-program-ownership.md
  - tools/agents/checkpoint.py
  - tools/agents/context.py
validation:
  - command: Agent Task Ownership 1361
    result: FAIL
    evidence: compile and focused tests passed; active ownership index validation failed on stale PR 222 exclusive workflow claim
  - command: Agent Task Ownership 1363
    result: PASS
    evidence: head e7cb0a388d627b31888b92b2c1537b5bab7c3a5a after stale task archive
  - command: repository CI 2486
    result: PASS
    evidence: previous implementation head 1c6de9638b12b7e3089c4d52abe4e2614a51b6ac
  - command: repository CI 2488
    result: NOT_RUN
    evidence: in progress when checkpoint was written
blockers:
  - current-head CI and final merge gate are pending
next_action: Verify all current-head PR #389 checks, synchronize with main if it advanced, review exact diff and review threads, then mark ready and merge only if every required gate passes.
```

# Completion

- Final status: validating
- PR: #389
- Merge commit: pending
- Program record updated: yes
- Catalogue updated: not applicable; no gameplay/runtime module interface introduced
- Changelog updated: yes
- Archived at: pending after merge
