# Agent Context Handoff

This document defines how an agent preserves work when the conversation becomes slow, the context window is close to exhaustion, a model/session must be replaced, or another agent must continue the same task.

## Principle

Chat history is disposable. Git, the task record, the PR, and deterministic evidence are the durable state.

A continuation agent must be able to resume without reading the previous conversation.

## When to checkpoint

Update the active task record immediately when any of these occurs:

- a root cause or blocker is proven;
- a hypothesis is rejected by evidence;
- files are modified;
- a test or CI result changes the task state;
- the current head changes;
- review feedback changes the required work;
- the agent notices degraded response quality, repeated rereading, loss of earlier facts, or excessive context growth;
- before deliberate compaction, session replacement, or context exhaustion.

Do not wait until the final tokens of a session.

## Context pressure protocol

When context pressure is suspected:

1. Stop broad exploration.
2. Do not start a new unrelated subtask.
3. Verify current branch/head and working-tree state.
4. Update the active task record using the checkpoint schema below.
5. Ensure the PR body contains the current high-level status when externally visible state changed.
6. Commit/push only coherent work that is safe to preserve; otherwise record uncommitted paths explicitly.
7. End the current agent after writing one precise `next_action`.

The next agent starts from the checkpoint, current Git state, current PR, and routed context. It must not reconstruct state from old chat messages.

## Checkpoint schema

Every substantial active task should maintain a compact `## Context checkpoint` section with this shape:

```yaml
checkpoint_version: 1
updated_at: YYYY-MM-DDTHH:MM:SSZ
head: <commit-sha-or-UNKNOWN>
branch: <branch>
pr: <number-or-none>
status: investigating|implementing|validating|blocked|ready
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
    result: PASS|FAIL|BLOCKED|NOT_RUN
    evidence: <short reference>
blockers:
  - <blocker or none>
next_action: <one concrete next step>
```

Omit empty historical detail; preserve only what a new agent needs to continue correctly.

## Evidence rules

Use these states consistently:

- `PROVEN`: directly supported by source, deterministic tool output, logs, artifacts, tests, or live GitHub state;
- `DERIVED`: conclusion that follows from listed proven facts;
- `UNKNOWN`: not established; never replace with a guess;
- `CONFLICT`: authoritative evidence disagrees and must be resolved.

For failures, record the first unmet marker/check and the evidence-backed cause when known. Do not retain speculative root causes as facts.

## Starting a continuation agent

The continuation prompt should be short:

```text
Continue task <task-id> from the repository state.
Read root AGENTS.md, REPOSITORY_MAP.md, CONTEXT_ROUTING.md, the active task checkpoint, and current PR/head.
Load only the context routes listed in the checkpoint.
Verify head and the first unresolved next_action before making changes.
Do not rely on previous chat history.
```

The new agent must first verify:

1. repository is `blakinio/canary`;
2. branch/head still match the checkpoint or record the change;
3. PR state and required CI are current;
4. ownership has not developed a new conflict;
5. `next_action` is still valid against current evidence.

## Handoff quality gate

A handoff is incomplete if the next agent would need to ask any of these before continuing:

- Which branch/PR/head am I on?
- What exactly failed first?
- Which facts are proven versus assumed?
- What files have already changed?
- What validation has run and with what result?
- What blocker remains?
- What is the next concrete action?

If any answer is missing, update the checkpoint before ending the session.

## Anti-bloat rules

Do not paste into the checkpoint:

- full logs;
- full diffs;
- entire artifact contents;
- long chat summaries;
- source files already available in Git.

Store references and exact identifiers instead: commit SHA, PR number, workflow/job, artifact name, path, line/symbol, test command, first failed marker.
