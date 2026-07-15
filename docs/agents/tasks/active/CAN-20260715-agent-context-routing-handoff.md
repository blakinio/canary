---
task_id: CAN-20260715-agent-context-routing-handoff
program_id: ""
coordination_id: ""
status: active
agent: "ChatGPT"
branch: docs/agent-context-routing-handoff
base_branch: main
created: 2026-07-15T13:47:00Z
updated: 2026-07-15T15:55:00Z
last_verified_commit: c1ebc6b416c02a0f4c52eb65331401c9aa6b6891
risk: low
related_issue: ""
related_pr: "385"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/CONTEXT_ROUTING.md
    - docs/agents/CONTEXT_HANDOFF.md
    - docs/agents/tasks/active/CAN-20260715-agent-context-routing-handoff.md
  shared: []
  read_only:
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/KNOWN_RISKS.md
    - docs/agents/BUILD_TEST_MATRIX.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
modules_touched:
  - agent-governance
  - agent-coordination
reuses:
  - existing task-record source-of-truth model
  - existing REPOSITORY_MAP.md
  - existing module catalogue and program records
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Reduce mandatory agent context loading and define deterministic continuation when a conversation slows down or approaches context exhaustion.

# Acceptance criteria

- [x] Agents no longer need to preload all large coordination/index documents for every task.
- [x] Large indexes are searched before full-file reads.
- [x] Task-specific context is selected through explicit routes.
- [x] Context pressure/exhaustion has a deterministic checkpoint and handoff procedure.
- [x] A continuation agent can resume from Git + task record + PR without previous chat history.
- [x] Existing repository safety and merge rules remain intact.
- [ ] Current-head GitHub checks verified.
- [x] Module catalogue impact: none; no reusable runtime/public interface added.
- [x] Changelog impact: none; agent-governance documentation only.
- [x] Cross-repository impact: none.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- Previous root `AGENTS.md` mandated broad startup reads including coordination/index documents unrelated to many narrow tasks.
- Previous `docs/agents/README.md` defined a second broad read order while already treating chat history as non-authoritative.
- Current task is documentation/agent-governance only.
- PR #385 targets `blakinio/canary:main` from `blakinio/canary:docs/agent-context-routing-handoff`.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Task records | Durable handoff state | `docs/agents/tasks/active/**` | Existing repository source-of-truth model |
| Repository map | Lean navigation | `docs/agents/REPOSITORY_MAP.md` | Already compact and purpose-built |
| Module catalogue | Search-first discovery | `docs/agents/MODULE_CATALOG.md` | Existing reusable-system index |

# Ownership and overlap check

- Program record: none required.
- Open PRs inspected: current PR #385; no overlap blocker proven.
- Active tasks inspected: targeted ownership validation through CI.
- Ownership checker result: initial current-head run failed because this new task record did not follow the structured task frontmatter/ownership contract; task record corrected in this PR.
- Exclusive claims: five changed agent-governance documentation/task paths.
- Shared claims: none.
- Read-only dependencies: repository map and large shared indexes referenced by routing rules.
- Overlaps: none proven.
- Resolution: structured ownership claims now match `docs/agents/templates/TASK.md`.

# Current state

Implementation complete; validating CI and merge gate.

# Plan

1. Verify required GitHub checks on the new head, resolve any evidence-backed failure, then mark ready and squash-merge when all gates pass.

# Work log

## 2026-07-15T15:55:00Z

- Changed: converted task record to current structured frontmatter and ownership format.
- Learned: `Agent Task Ownership` failed in `Validate active ownership` → `Validate tasks and render ownership index`; focused tooling/unit-test steps passed.
- Failed/blocked: previous task file lacked the current task-template frontmatter and structured ownership declaration.
- Result: root cause corrected; awaiting new-head CI.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Route large context instead of preloading it | Reduces unrelated working-set growth while preserving targeted authoritative reads | none |
| Persist compact checkpoint in task record | New agent can continue from Git/task/PR without old chat | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `AGENTS.md` | exclusive | Lean startup and context-pressure policy | changed |
| `docs/agents/README.md` | exclusive | Lean coordination lifecycle | changed |
| `docs/agents/CONTEXT_ROUTING.md` | exclusive | Task-specific context routing | added |
| `docs/agents/CONTEXT_HANDOFF.md` | exclusive | Context exhaustion/checkpoint protocol | added |
| current task record | exclusive | Durable task state and handoff | changed |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `c1ebc6b416c02a0f4c52eb65331401c9aa6b6891` | CI | passed | GitHub workflow run #2442 |
| `c1ebc6b416c02a0f4c52eb65331401c9aa6b6891` | Agent Task Ownership | failed | Job `Validate active ownership`, first failing step `Validate tasks and render ownership index`; task format corrected after inspecting current template |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- Initial task record used an ad-hoc Markdown ownership block instead of the repository's current structured task frontmatter. Ownership CI rejected the task validation stage.

# Risks and compatibility

- Runtime: none; documentation only.
- Data/migration: none.
- Security: repository allowlist and stop conditions remain mandatory.
- Backward compatibility: legacy task records remain discoverable; new task uses current structured ownership format.
- Cross-repo rollout: none.
- Rollback: revert PR #385.

# Remaining work

1. Verify new-head required checks and merge only after the autonomous merge gate is satisfied.

# Handoff

## Start here

Read the context checkpoint below, then verify current PR #385 head and current required checks.

## Do not repeat

Do not re-investigate the initial ownership failure as transient; the task record format was the concrete defect and has been corrected.

## Required reads

- `AGENTS.md`
- `docs/agents/REPOSITORY_MAP.md`
- `docs/agents/CONTEXT_ROUTING.md`
- this task checkpoint
- current PR #385 and current-head CI

## Open questions

- Do all required checks pass on the corrected head?

# Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T15:55:00Z
head: PENDING_NEW_COMMIT
branch: docs/agent-context-routing-handoff
pr: 385
status: validating
context_routes:
  - agent-governance
  - ci-repair
owned_paths:
  - AGENTS.md
  - docs/agents/README.md
  - docs/agents/CONTEXT_ROUTING.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/tasks/active/CAN-20260715-agent-context-routing-handoff.md
proven:
  - PR 385 is open, draft, and mergeable against main at the previously inspected head.
  - CI passed on c1ebc6b416c02a0f4c52eb65331401c9aa6b6891.
  - Agent Task Ownership failed on c1ebc6b416c02a0f4c52eb65331401c9aa6b6891 in Validate active ownership, first failing step Validate tasks and render ownership index.
  - The repository task template requires YAML frontmatter with structured owned_paths.exclusive/shared/read_only.
  - The initial task record lacked that required structured task format.
derived:
  - The ownership failure belongs to this PR task-record format, not to a transient runner failure.
unknown:
  - Current-head CI after correcting the task record.
conflicts: []
first_failure:
  marker: Agent Task Ownership / Validate active ownership / Validate tasks and render ownership index
  evidence: workflow run 29420736604, job 87370219474
rejected_hypotheses:
  - transient CI failure: focused ownership tooling compilation and unit tests passed before task/index validation failed
changed_paths:
  - AGENTS.md
  - docs/agents/README.md
  - docs/agents/CONTEXT_ROUTING.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/tasks/active/CAN-20260715-agent-context-routing-handoff.md
validation:
  - command: CI on c1ebc6b416c02a0f4c52eb65331401c9aa6b6891
    result: PASS
    evidence: workflow run 29420736898
  - command: Agent Task Ownership on c1ebc6b416c02a0f4c52eb65331401c9aa6b6891
    result: FAIL
    evidence: workflow run 29420736604; task record corrected afterwards
blockers:
  - current-head required checks not yet verified
next_action: Verify PR 385 new head and required CI; fix any new evidence-backed failure, otherwise mark ready and squash-merge.
```

# Completion

- Final status: active
- PR: #385
- Merge commit:
- Program record updated: not applicable
- Catalogue updated: not applicable
- Changelog updated: not applicable
- Archived at:
