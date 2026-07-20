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
5. Validate the checkpoint when the tooling is available.
6. Ensure the PR body contains the current high-level status when externally visible state changed.
7. Commit/push only coherent work that is safe to preserve; otherwise record uncommitted paths explicitly.
8. Generate a compact resume bundle when another session/mode/agent will continue.
9. End the current agent after writing one precise `next_action`.

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

The `## Context checkpoint` section is the authoritative machine-readable continuation state. Any additional prose `# Handoff` section is optional human-readable context and must not replace or override the checkpoint.

### Checkpoint compactness ceilings

`tools/agents/checkpoint.py` enforces generous hard ceilings on checkpoint list fields because continuation agents read the task record before the routed resume bundle can trim it. `docs/agents/CONTEXT_ROUTES.json` applies tighter limits to the generated evidence bundle.

When a checkpoint approaches a ceiling, replace superseded history with the current proven conclusion and exact references. Do not preserve chronological diaries, repeated CI outcomes, stale changed-path inventories, or every rejected hypothesis. Never remove a current blocker, unresolved conflict, first-failure marker, or evidence required to justify the next action merely to satisfy compactness.

Validate a checkpoint with:

```sh
python tools/agents/checkpoint.py <active-task-path> --require-checkpoint
```

The validator checks required fields, supported states/results, evidence-state overlap, compactness ceilings, and the requirement for one concrete top-level `next_action`. It does not replace live Git/PR/CI verification.

## Evidence rules

Use these states consistently:

- `PROVEN`: directly supported by source, deterministic tool output, logs, artifacts, tests, or live GitHub state;
- `DERIVED`: conclusion that follows from listed proven facts;
- `UNKNOWN`: not established; never replace with a guess;
- `CONFLICT`: authoritative evidence disagrees and must be resolved.

For failures, record the first unmet marker/check and the evidence-backed cause when known. Do not retain speculative root causes as facts.

A continuation worker must not spend context rediscovering PROVEN facts unless current Git/PR evidence has changed.

## Starting a continuation agent

The continuation prompt should be short. Prefer generating it from repository state:

```sh
python tools/agents/resume.py --task <active-task-path> --task-text "<bounded next task>"
```

Repository-relative `--task` and `--config` paths are resolved from the repository root, not the caller's current working directory. Absolute paths remain unchanged. The same command therefore works from the repository root and from subdirectories such as `tools/agents/`.

Add capability flags only when they are true, for example:

```sh
# local edit/build/test/runtime loop
python tools/agents/resume.py --task <task> --needs-local-execution

# broad multi-source research package
python tools/agents/resume.py --task <task> --broad-research --large-deliverable
```

The generated prompt follows this operating contract:

```text
Continue task <task-id> from the repository state.
Read only the routed required context, checkpoint, and current PR/head.
Verify head, PR, CI, ownership and next_action before changing state.
Do not rediscover PROVEN facts unless live evidence changed.
Do not rely on previous chat history.
```

The new agent must first verify:

1. repository is `blakinio/canary`;
2. branch/head still match the checkpoint or record the change;
3. PR state and required CI are current;
4. ownership has not developed a new conflict;
5. `next_action` is still valid against current evidence.

## Legacy checkpoint-less recovery

Legacy active task records may predate the checkpoint contract. They remain invalid under strict checkpoint validation; `resume.py` does not silently make them compliant.

When no `## Context checkpoint` exists, the context/resume tooling instead provides a bounded recovery prompt:

- emits an explicit `WARNING: CHECKPOINT_MISSING` line;
- derives only `head`, `branch`, `pr`, and `status` from explicit task frontmatter (`last_verified_commit`, `branch`, normalized `related_pr`, `status`);
- leaves PROVEN/UNKNOWN/CONFLICT evidence lists empty rather than reconstructing claims from prose;
- uses one safe recovery `next_action`: reconstruct and write a valid checkpoint from current Git, PR, and task evidence before substantive implementation;
- normalizes the PR reference once so REQUIRED_READS and EVIDENCE_BUNDLE use the same PR identity.

This fallback is a recovery mechanism, not evidence that the legacy task is current. The continuation agent must verify live Git/PR state before relying on the frontmatter values and should write a compliant checkpoint before substantive implementation.

## Mode-aware handoff

Use `docs/agents/EXECUTION_MODE_ROUTING.md` for CHAT/CODEX/WORK selection.

Default is `minimize_agentic_usage`:

- CHAT remains the coordinator while connector-based analysis, GitHub, PR and CI work is sufficient;
- CODEX receives only a bounded execution bundle when local edit/build/test/runtime capability is necessary;
- WORK receives only a bounded research/deliverable bundle when broad multi-source work is necessary;
- after the bounded CODEX or WORK package finishes, checkpoint the result and return coordination to CHAT unless another bounded agentic step is still required.

Do not pass full previous conversations into CODEX or WORK. The task checkpoint and generated evidence bundle are the handoff boundary.

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

Do not paste into the checkpoint or escalation bundle:

- full logs;
- full diffs;
- entire artifact contents;
- long chat summaries;
- source files already available in Git;
- whole-repository inventories;
- unrelated optional documentation.

Store references and exact identifiers instead: commit SHA, PR number, workflow/job, artifact name, path, line/symbol, test command, first failed marker.
