# Agent Context Handoff

This document defines how an agent preserves work when context is under pressure, a session must be replaced, or another agent continues the same task.

## Principle

Chat history is disposable. Git, the task record, the live PR, and deterministic evidence are durable state. A continuation agent must be able to resume without reading the previous conversation.

## Contract revision

Checkpoint structure remains version 1. Policy revision 2 is backward-compatible and adds task statuses `waiting` and `completed`, validation result `NOT_APPLICABLE`, and a formal distinction between task status and terminal invocation result. Existing valid version 1 checkpoints remain valid.

Checkpoint task statuses:

```text
investigating | implementing | validating | ready | waiting | blocked | completed
```

Terminal invocation results:

```text
DONE | WAITING | BLOCKED | ROTATE
```

`ROTATE` is never a checkpoint task status. Before returning it, persist `ready`, `waiting`, or `blocked` with exactly one concrete `next_action`.

## When to checkpoint

Update the active task record when:

- a root cause or blocker is proven;
- a hypothesis is rejected by evidence;
- files are modified;
- validation or CI changes task state;
- branch, head, or PR state changes;
- review feedback changes required work;
- context quality degrades or grows excessively;
- before compaction, session replacement, or context exhaustion.

Do not wait until the end of the session.

## Context pressure protocol

1. Stop broad exploration and do not start an unrelated subtask.
2. Verify current branch, head, PR, and working-tree state.
3. Update the active task checkpoint.
4. Validate the checkpoint when tooling is available.
5. Preserve only coherent work; otherwise record uncommitted paths.
6. Generate a compact resume bundle when another session or agent continues.
7. Leave exactly one concrete `next_action`.
8. End or rotate the current worker; do not rely on previous chat.

## Checkpoint schema

```yaml
checkpoint_version: 1
updated_at: YYYY-MM-DDTHH:MM:SSZ
head: <commit-sha-or-UNKNOWN>
branch: <branch>
pr: <number-or-none>
status: investigating|implementing|validating|ready|waiting|blocked|completed
context_routes:
  - <route>
owned_paths:
  - <path/glob>
proven:
  - <fact backed by source/tool/test evidence>
derived:
  - <explicitly derived conclusion>
unknown:
  - <unresolved fact>
conflicts:
  - <conflicting evidence that still needs resolution>
first_failure:
  marker: <first unmet invariant/check or none>
  evidence: <artifact/log/test reference>
rejected_hypotheses:
  - <hypothesis>: <disproving evidence>
changed_paths:
  - <path>
validation:
  - command: <command/workflow/job>
    result: PASS|FAIL|BLOCKED|NOT_RUN|NOT_APPLICABLE
    evidence: <short reference; concrete reason required for NOT_APPLICABLE>
blockers:
  - <blocker or none>
next_action: <one concrete next step>
```

Use `waiting` when an external event is pending and no worker should remain active. Use `blocked` for a real decision, permission, safety, resource, or exhausted-repair barrier. Use `ready` when a fresh session can execute `next_action`. Use `completed` only after repository closeout gates pass.

The `## Context checkpoint` section is authoritative machine-readable continuation state. Optional prose handoff sections must not replace or override it.

## Compactness and validation

`tools/agents/checkpoint.py` enforces required fields, accepted states and results, evidence-state overlap, compactness ceilings, and one concrete top-level `next_action`.

Validate with:

```sh
python tools/agents/checkpoint.py <active-task-path> --require-checkpoint
```

When a checkpoint approaches a ceiling, replace superseded history with the current proven conclusion and exact references. Never remove a current blocker, unresolved conflict, first-failure marker, or evidence required for `next_action` merely to satisfy compactness.

The validator checks structure only; live Git, PR, CI, ownership, and evidence still require verification.

## Evidence rules

- `PROVEN`: directly supported by source, deterministic tool output, logs, artifacts, tests, or live GitHub state.
- `DERIVED`: conclusion that follows from listed proven facts.
- `UNKNOWN`: not established; never replace with a guess.
- `CONFLICT`: authoritative evidence disagrees and must be resolved.

Record the first unmet marker and evidence-backed cause when known. A continuation worker must not rediscover `PROVEN` facts unless live evidence changed.

## Starting a continuation agent

Prefer generating a bounded prompt from repository state:

```sh
python tools/agents/resume.py --task <active-task-path> --task-text "<bounded next task>"
```

Add capability flags only when true. The new agent verifies repository identity, branch/head, PR and CI, ownership conflicts, and validity of `next_action` before changing state.

Legacy checkpoint-less task records require a bounded recovery action: reconstruct and write a valid checkpoint from current Git, PR, CI, ownership, and task evidence before substantive implementation.

## Mode-aware handoff

Use `EXECUTION_MODE_ROUTING.md` for Chat, Codex, and Work selection. Pass only the bounded task checkpoint and routed evidence bundle, never the full previous conversation.

## Handoff quality gate

A handoff is incomplete if the next agent cannot determine:

- current branch, PR, and head;
- proven, derived, unknown, and conflicting facts;
- first failure, if any;
- changed paths;
- validation results;
- current task status;
- remaining blocker;
- the single next action.

## Anti-bloat

Do not paste full logs, full diffs, whole source files, artifact contents, long chat summaries, whole-repository inventories, or unrelated documentation into checkpoints. Store exact identifiers and references instead.