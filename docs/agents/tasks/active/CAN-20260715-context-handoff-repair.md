---
task_id: CAN-20260715-context-handoff-repair
program_id: CAN-PROGRAM-AGENT-ORCHESTRATION
coordination_id: ""
status: implementing
agent: "GPT-5.5 Thinking"
branch: fix/context-handoff-repair
base_branch: main
created: 2026-07-15T19:32:23Z
updated: 2026-07-15T19:42:00Z
last_verified_commit: "d121ff9bf5065806c983c25d37bd1f3bc5c9da60"
risk: low
related_issue: ""
related_pr: "404"
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
    - docs/agents/programs/AGENT_CONTEXT_ORCHESTRATION_PROGRAM.md
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

Repair the context-handoff pipeline so newly created tasks are checkpoint-compliant by default and `resume.py` produces a usable, internally consistent continuation prompt from both compliant tasks and checkpoint-less legacy tasks, independent of caller CWD.

# Acceptance criteria

- [x] `docs/agents/templates/TASK.md` contains the authoritative `## Context checkpoint` skeleton from `CONTEXT_HANDOFF.md`.
- [x] Retained prose `# Handoff` is explicitly non-authoritative human-readable context.
- [x] Repository-relative task/config paths are anchored to repo root; absolute paths remain unchanged.
- [x] Checkpoint-less fallback derives only head/branch/PR/status from frontmatter and emits an explicit warning.
- [x] PR references use one canonical normalization path for required reads and evidence.
- [x] Checkpoint-less fallback uses a safe checkpoint-reconstruction `next_action` without inventing project evidence.
- [x] Strict missing-checkpoint validation remains unchanged.
- [x] Focused tests cover template compliance, fallback, PR normalization and non-root CWD invocation.
- [x] Focused tests pass on implementation head `d121ff9bf5065806c983c25d37bd1f3bc5c9da60` in Agent Task Ownership #1438.
- [ ] Current-head GitHub checks pass and autonomous merge gate is satisfied.

# Confirmed context

Verified from `main` before implementation:

- root `AGENTS.md` requires `## Context checkpoint` for substantial active tasks;
- the previous `TASK.md` template had no checkpoint and retained only an older prose handoff structure;
- the previous `context.py` default config was CWD-relative;
- required reads used frontmatter `related_pr` while evidence used checkpoint-only data;
- the inspected legacy session-cleanup task has explicit frontmatter metadata, `related_pr: blakinio/canary#339`, and no checkpoint;
- ownership CI validates changed active task checkpoints edge-triggered through `task_lifecycle.py validate-changed`;
- historical 11/11 checkpoint-less count on head `618769f` is not required as a correctness premise for this repair.

# Delivered implementation

- `TASK.md` now ships the same checkpoint schema as `CONTEXT_HANDOFF.md` and labels prose handoff as optional human context.
- `context.py` defines `REPO_ROOT`, anchors relative task/config paths there, preserves absolute paths, and keeps display paths repo-relative where possible.
- `context.py` canonicalizes PR references such as `339`, `#339`, `blakinio/canary#339`, and GitHub pull URLs to one numeric identity when possible.
- Required reads and evidence now use the same canonical PR reference.
- A task without a checkpoint receives `CHECKPOINT_MISSING`, frontmatter-derived head/branch/PR/status, empty evidence-state lists, and a safe recovery next action.
- `resume.py` renders warnings explicitly.
- Focused tests cover template checkpoint validity, fallback semantics, normalization, and CLI execution from both repo root and `tools/agents/`.
- Handoff and coordination docs document the recovery contract without declaring legacy tasks compliant.

# Follow-up candidates — out of scope

- Per-task migration or archival of legacy active task records lacking checkpoints.
- Level-triggered CI validating all active tasks on a schedule or every PR.
- `resume.py --verify` live Git/PR cross-checking.
- Canonical task-status enum enforcement across historical values.
- `ACTIVE_WORK.md` regeneration automation.
- Root `CLAUDE.md` stub.
- Root cleanup of `pasted.txt`, `apply.patch`, `gdb_debug`.
- `key.pem` annotation in `KNOWN_RISKS.md`.

# Ownership and overlap check

- Program record: `CAN-PROGRAM-AGENT-ORCHESTRATION` as the completed foundation being maintained; this task is a new separately owned repair and does not reopen ACO-001 through ACO-004.
- PR: #404 in `blakinio/canary`, draft, base `main`, head `fix/context-handoff-repair`.
- Exclusive claims: template, context/resume implementation, focused tests and this task record.
- Shared claims: handoff/README/changelog only.
- Overlaps: none proven at task start.
- Resolution: keep changes within declared agent-governance paths.

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `d121ff9bf5065806c983c25d37bd1f3bc5c9da60` | Agent Task Ownership focused unit tests | passed | compile, focused tests and changed checkpoint validation all passed in run #1438 before ownership index step |
| `d121ff9bf5065806c983c25d37bd1f3bc5c9da60` | Agent Task Ownership #1438 | failed | task ownership index rejected the active structured task because `program_id` was blank; implementation tests were green |
| `d121ff9bf5065806c983c25d37bd1f3bc5c9da60` | repository CI #2571 | passed | current implementation head before metadata-only task fix |
| current head | Agent Task Ownership | not-run | rerun triggered by metadata fix |

# Risks and compatibility

- Runtime: none; docs/Python agent tooling only.
- Data/migration: no legacy task migration.
- Security: no secrets or external-repository writes.
- Backward compatibility: strict validation still rejects checkpoint-less tasks; resume fallback is recovery-only.
- Cross-repo rollout: none.
- Rollback: revert PR #404; no runtime/data migration.

# Remaining work

1. Verify current-head ownership and repository checks after the task metadata fix, update changelog/final checkpoint, review exact diff, then mark ready and merge through the normal gate.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T19:42:00Z
head: d121ff9bf5065806c983c25d37bd1f3bc5c9da60
branch: fix/context-handoff-repair
pr: 404
status: validating
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
  - task template now contains the authoritative Context checkpoint skeleton
  - prose Handoff is explicitly non-authoritative human context
  - relative task and config paths are anchored to repository root in context.py
  - checkpoint-less fallback preserves strict validation failure while producing an explicit recovery warning
  - fallback derives only head branch PR status from task frontmatter and leaves evidence lists empty
  - required reads and evidence use one normalized PR reference
  - focused orchestration tests passed in Agent Task Ownership run 1438
  - repository CI run 2571 passed on d121ff9bf5065806c983c25d37bd1f3bc5c9da60
derived:
  - newly created tasks can start compliant with the checkpoint contract
  - legacy tasks can produce a usable recovery prompt without being silently treated as compliant
unknown:
  - current-head Agent Task Ownership result after program_id metadata fix
  - final ready-state required check result
conflicts: []
first_failure:
  marker: Agent Task Ownership Validate tasks and render ownership index
  evidence: run 1438 failed after compile tests and changed checkpoint validation passed because active structured task program_id was blank
rejected_hypotheses:
  - implementation tests caused run 1438 failure: disproven because focused unit tests passed
  - migrate all legacy tasks in this repair: rejected because lifecycle disposition is per-task and out of scope
  - infer PROVEN facts from legacy prose: rejected because prose is not deterministic evidence
changed_paths:
  - docs/agents/templates/TASK.md
  - tools/agents/context.py
  - tools/agents/resume.py
  - tools/agents/test_context_orchestration.py
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/README.md
  - docs/agents/tasks/active/CAN-20260715-context-handoff-repair.md
validation:
  - command: Agent Task Ownership 1438 focused tests
    result: PASS
    evidence: compile focused unit tests and changed checkpoint validation passed
  - command: Agent Task Ownership 1438 ownership index
    result: FAIL
    evidence: active structured task requires nonempty program_id; fixed by binding this repair to CAN-PROGRAM-AGENT-ORCHESTRATION
  - command: repository CI 2571
    result: PASS
    evidence: implementation head d121ff9bf5065806c983c25d37bd1f3bc5c9da60
blockers:
  - none
next_action: Verify current-head Agent Task Ownership and CI after the program_id fix, then update changelog and final readiness state.
```

# Handoff

This section is human-readable context only. The authoritative machine-readable continuation state is `## Context checkpoint` above.

## Start here

Read root `AGENTS.md`, this checkpoint, and PR #404.

## Do not repeat

Do not migrate legacy tasks or broaden all-task CI validation in this repair.

## Required reads

- `AGENTS.md`
- `docs/agents/CONTEXT_HANDOFF.md`
- `docs/agents/templates/TASK.md`
- `tools/agents/context.py`
- `tools/agents/resume.py`
- `tools/agents/test_context_orchestration.py`

## Open questions

- Exact current checkpoint-less legacy count remains non-blocking and out of scope.

# Completion

- Final status: validating
- PR: #404
- Merge commit: pending
- Program record updated: not applicable; existing completed foundation referenced only
- Catalogue updated: not applicable; no gameplay/runtime module interface
- Changelog updated: pending
- Archived at: pending lifecycle cleanup after merge
