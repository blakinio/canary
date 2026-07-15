---
task_id: CAN-20260715-context-handoff-repair
program_id: ""
coordination_id: ""
status: implementing
agent: "GPT-5.5 Thinking"
branch: fix/context-handoff-repair
base_branch: main
created: 2026-07-15T19:32:23Z
updated: 2026-07-15T19:32:23Z
last_verified_commit: ""
risk: low
related_issue: ""
related_pr: ""
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/templates/TASK.md
    - tools/agents/context.py
    - tools/agents/resume.py
    - tools/agents/test_context_orchestration.py
    - docs/agents/tasks/active/CAN-20260715-context-handoff-repair.md
  shared:
    - docs/agents/CONTEXT_HANDOFF.md
    - docs/agents/README.md
    - docs/agents/CHANGELOG.md
  read_only:
    - AGENTS.md
    - docs/agents/CONTEXT_ROUTING.md
    - docs/agents/CONTEXT_ROUTES.json
    - tools/agents/checkpoint.py
    - tools/agents/task_ownership.py
    - tools/agents/task_lifecycle.py
    - .github/workflows/agent-task-ownership.yml
modules_touched:
  - agent-governance
  - agent-context-handoff
  - agent-tooling
reuses:
  - existing checkpoint schema and validator
  - existing bounded context resolver and resume prompt generator
  - existing task frontmatter parser
public_interfaces:
  - task template checkpoint contract
  - repository-root-relative context resolution
  - legacy checkpoint-less resume fallback
cross_repo_tasks: []
---

# Goal

Repair the context-handoff pipeline so newly created tasks are checkpoint-compliant by default and `resume.py` produces a usable, internally consistent continuation prompt from both compliant tasks and checkpoint-less legacy tasks, independent of the caller's current working directory.

# Acceptance criteria

- [ ] `docs/agents/templates/TASK.md` contains the authoritative `## Context checkpoint` skeleton from `CONTEXT_HANDOFF.md`.
- [ ] Any retained prose `# Handoff` section is explicitly non-authoritative human-readable context.
- [ ] Repository-relative task/config paths used by context/resume tooling are anchored to repository root; absolute paths remain unchanged.
- [ ] `resume.py` succeeds from repository root and from `tools/agents/` for repository-relative task/config paths.
- [ ] A checkpoint-less legacy task yields an explicit warning and frontmatter-derived head/branch/PR/status without inventing PROVEN/UNKNOWN/CONFLICT evidence.
- [ ] `related_pr` is normalized consistently so REQUIRED_READS and EVIDENCE_BUNDLE cannot disagree or render a doubled `#` prefix.
- [ ] A checkpoint-less legacy task gets a safe concrete recovery `next_action` instructing the next agent to reconstruct a valid checkpoint from live evidence.
- [ ] Missing-checkpoint validation remains a failure in `checkpoint.py`/lifecycle validation.
- [ ] Focused `tools/agents` tests cover template compliance, CWD independence, fallback behavior and PR normalization.
- [ ] No C++/CMake/runtime changes are made; no local C++ build is required. Existing branch-protection workflows may still run repository-required checks and must not be weakened.
- [ ] This task maintains a valid `## Context checkpoint` with exactly one concrete `next_action`.
- [ ] Current-head GitHub checks pass and autonomous merge gate is satisfied.

# Confirmed context

Verified on current `main` immediately before task creation:

- Root `AGENTS.md` requires substantial active tasks to maintain `## Context checkpoint` and continuation agents to rely on that durable state.
- `docs/agents/templates/TASK.md` has no `## Context checkpoint`; it still ends with an older prose `# Handoff` structure.
- `tools/agents/context.py` defines `DEFAULT_CONFIG = Path("docs/agents/CONTEXT_ROUTES.json")`, so the default config is CWD-relative.
- `context.py` builds `required_reads` from frontmatter `related_pr` but builds the evidence bundle from checkpoint data only.
- `docs/agents/tasks/active/CAN-20260714-protocolgame-player-session-cleanup.md` has no checkpoint, has `branch: fix/protocolgame-player-session-cleanup`, `status: ready_for_merge`, `last_verified_commit: 41f8be155c80c29bc51c4c1ead6ad91e7e2159dc`, and `related_pr: blakinio/canary#339`.
- `.github/workflows/agent-task-ownership.yml` validates checkpoints only for changed active task paths through `task_lifecycle.py validate-changed`.
- The historical report that 11/11 active records lacked checkpoints was verified on head `618769f`; the exact current legacy count is not relied on by this repair and remains to be re-measured separately if needed.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Checkpoint contract | Exact schema and validation behavior | `docs/agents/CONTEXT_HANDOFF.md`, `tools/agents/checkpoint.py` | Already authoritative; template should copy it rather than invent a second schema |
| Context resolver | Route selection and bounded evidence bundle | `tools/agents/context.py` | Repair root anchoring and fallback in place |
| Resume generator | Continuation prompt rendering | `tools/agents/resume.py` | Add warning rendering without creating another handoff path |
| Task frontmatter parser | Legacy task metadata | `tools/agents/task_ownership.py` | Source for non-evidence fallback fields when checkpoint is absent |

# Ownership and overlap check

- Program record: none; this is a bounded post-ACO repair and does not reopen completed ACO-001 through ACO-004.
- Open PRs inspected: no known ACO PR remains open after #403; current work is isolated to agent-governance tooling/docs.
- Active tasks inspected: targeted legacy session-cleanup record only as read-only fallback evidence.
- Ownership checker result: pending CI/local-equivalent validation after draft PR creation.
- Exclusive claims: task template, context/resume implementation, focused orchestration tests, this task record.
- Shared claims: handoff/README/changelog narrow behavior documentation.
- Read-only dependencies: governance, routing, checkpoint/lifecycle/ownership implementation and ownership workflow.
- Overlaps: none proven at task start.
- Resolution: proceed only with the declared agent-governance paths.

# Current state

Task branch created from current `main`; task record created before implementation. Draft PR is the next action.

# Plan

1. Open an early draft PR and bind its number into this task/checkpoint.
2. Add the authoritative checkpoint skeleton to the task template and demote legacy prose handoff to non-authoritative context.
3. Anchor repository-relative config/task paths to repo root and normalize PR references.
4. Add checkpoint-less fallback metadata plus warning and safe checkpoint-reconstruction next action.
5. Extend focused tests for template compliance, fallback, PR normalization and non-root CWD invocation.
6. Update handoff/README/changelog narrowly, run CI, repair failures, review exact diff, mark ready and merge.

# Follow-up candidates — out of scope

- Per-task migration or archival of legacy active task records that still lack checkpoints; archive candidates and migration candidates must be decided individually.
- Level-triggered CI validating all active tasks on a schedule or every PR.
- `resume.py --verify` mode cross-checking checkpoint head against live Git/PR state.
- Canonical task-status enum enforcement across divergent historical status values.
- `ACTIVE_WORK.md` regeneration automation.
- Root `CLAUDE.md` stub.
- Root cleanup of `pasted.txt`, `apply.patch`, `gdb_debug`.
- `key.pem` annotation in `KNOWN_RISKS.md`.

# Work log

## 2026-07-15T19:32:23Z

- Changed: created bounded task branch and this compliant task record.
- Learned: current template/tooling inconsistency is directly visible on `main`; exact historical 11/11 legacy count is not required for the repair.
- Failed/blocked: none.
- Result: ready to open the early draft PR.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Preserve missing-checkpoint validation failure | Fallback is for usable recovery, not silent compliance | none |
| Derive only head/branch/PR/status from frontmatter | These are explicit metadata; evidence lists must not be fabricated | none |
| Use a recovery next_action for checkpoint-less tasks | A continuation prompt must provide one safe concrete action without guessing project work | none |
| Normalize PR references once and reuse the canonical value | Prevent REQUIRED_READS/EVIDENCE_BUNDLE disagreement | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `docs/agents/templates/TASK.md` | exclusive | compliant task creation | planned |
| `tools/agents/context.py` | exclusive | repo-root path resolution and fallback bundle | planned |
| `tools/agents/resume.py` | exclusive | explicit warning rendering | planned |
| `tools/agents/test_context_orchestration.py` | exclusive | regression coverage | planned |
| `docs/agents/CONTEXT_HANDOFF.md` | shared | document fallback/recovery behavior | planned |
| `docs/agents/README.md` | shared | task-start/resume guidance | planned |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| pending | focused agent tests | not-run | implementation not started |
| pending | Agent Task Ownership | not-run | draft PR not yet opened |
| pending | repository required checks | not-run | draft PR not yet opened |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

None yet.

# Risks and compatibility

- Runtime: none; Python/docs-only agent tooling.
- Data/migration: no legacy task migration in this PR.
- Security: no secret or external-repository changes.
- Backward compatibility: legacy task records remain invalid for strict checkpoint validation but become recoverable by `resume.py` with an explicit warning.
- Cross-repo rollout: none.
- Rollback: revert this PR; no persistent runtime/data migration.

# Remaining work

1. Open the early draft PR, bind its number into this task, then implement the bounded repair.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T19:32:23Z
head: UNKNOWN
branch: fix/context-handoff-repair
pr: none
status: implementing
context_routes:
  - agent-governance
owned_paths:
  - docs/agents/templates/TASK.md
  - tools/agents/context.py
  - tools/agents/resume.py
  - tools/agents/test_context_orchestration.py
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/README.md
proven:
  - root AGENTS requires substantial active tasks to maintain a Context checkpoint
  - current TASK template has no Context checkpoint and still carries the legacy prose Handoff structure
  - context.py default config is CWD-relative
  - context.py reads PR references from frontmatter for required reads but evidence only from checkpoint data
  - the inspected legacy session-cleanup task has frontmatter metadata but no Context checkpoint
derived:
  - newly templated tasks can be born non-compliant with the current checkpoint contract
  - a checkpoint-less legacy task can produce an unusable or internally inconsistent resume bundle
unknown:
  - exact current count of checkpoint-less legacy active tasks
  - current-head CI after implementation
conflicts: []
first_failure:
  marker: none
  evidence: implementation validation has not started
rejected_hypotheses:
  - migrate all legacy tasks in this repair: rejected because lifecycle disposition is per-task and explicitly out of scope
changed_paths:
  - docs/agents/tasks/active/CAN-20260715-context-handoff-repair.md
validation:
  - command: current main source inspection
    result: PASS
    evidence: AGENTS TASK template context resume handoff README workflow and legacy task inspected via GitHub
blockers:
  - none
next_action: Open an early draft PR for fix/context-handoff-repair and update this task with the PR number before implementation.
```

# Handoff

This section is human-readable context only. The authoritative machine-readable continuation state is `## Context checkpoint` above.

## Start here

Read root `AGENTS.md`, `CONTEXT_ROUTING.md`, this task checkpoint and the live PR.

## Do not repeat

Do not migrate legacy tasks or broaden CI validation in this repair.

## Required reads

- `AGENTS.md`
- `docs/agents/CONTEXT_HANDOFF.md`
- `docs/agents/templates/TASK.md`
- `tools/agents/context.py`
- `tools/agents/resume.py`
- `tools/agents/test_context_orchestration.py`

## Open questions

- Exact current legacy checkpoint-less count is intentionally non-blocking for this repair.

# Completion

- Final status: implementing
- PR: pending
- Merge commit: pending
- Program record updated: not applicable
- Catalogue updated: not applicable unless a new reusable interface is introduced
- Changelog updated: pending
- Archived at: pending lifecycle cleanup after merge
