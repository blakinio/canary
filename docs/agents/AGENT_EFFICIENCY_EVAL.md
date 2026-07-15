# Agent Efficiency Evaluation

This document defines ACO-003 efficiency measurement for Canary agent workflows.

## Goal

Measure whether routed context, compact checkpoints and bounded handoffs reduce unnecessary agent overhead without pretending that repository tooling can see exact ChatGPT/Codex/Work token or credit balances.

The evaluator uses observable proxies only.

## Trace format

Schema:

`docs/agents/schemas/agent-efficiency-trace.schema.json`

A trace records one bounded agent run with:

- `run_id`;
- cohort: `baseline`, `routed`, or `custom`;
- mode: `CHAT`, `CODEX`, or `WORK`;
- run start/end timestamps;
- whether a handoff was attempted and whether it succeeded;
- bounded events only.

Allowed event types:

- `file_read` with a repository path;
- `tool_call` with a tool name;
- `action` for the first concrete patch/test/decision-producing action;
- `context_expand` when the working set is intentionally broadened;
- `optional_context_load` when optional routed context is actually loaded;
- `handoff` for a handoff event marker.

Do not place full prompts, full chat history, source contents, logs, secrets, credentials, private artifacts or model chain-of-thought into traces.

## Metrics

For each run the evaluator reports:

- files read;
- unique files read;
- repeated reads;
- repeated-read ratio;
- tool calls;
- time to first concrete action;
- context expansions;
- optional-context loads;
- handoff attempted/success.

For baseline-versus-routed cohorts it reports averages and `routed - baseline` deltas.

Lower is generally better for:

- files read;
- repeated reads and repeat ratio;
- tool calls;
- time to first action;
- context expansions;
- optional-context loads.

Higher is better for handoff success rate.

These metrics are not a substitute for correctness. A run that reads fewer files but misses required evidence is worse, not better.

## Usage

Evaluate one or more JSON trace files:

```sh
python tools/agents/efficiency_eval.py artifacts/agent-evals/*.json
```

Emit machine-readable JSON:

```sh
python tools/agents/efficiency_eval.py artifacts/agent-evals/*.json --json
```

Each input may contain one trace object or a JSON array of trace objects.

## Baseline protocol

For meaningful comparison:

1. Use the same bounded task or equivalent task class.
2. Record at least one `baseline` run using the previous/broad-context workflow.
3. Record at least one `routed` run using current routing/checkpoint/resume tooling.
4. Keep acceptance criteria and required evidence equivalent.
5. Compare metrics only after both cohorts satisfy their correctness/validation gate.

Do not interpret a lower metric as proof of improvement when the routed run failed to complete the same task.

## Handoff-success definition

A handoff is successful when the continuation agent can resume from repository state and the checkpoint/evidence bundle without asking for missing answers to the handoff quality gate in `CONTEXT_HANDOFF.md`.

Set:

- `handoff_attempted: false`, `handoff_success: null` when no handoff was exercised;
- `handoff_attempted: true`, `handoff_success: true` when continuation succeeds;
- `handoff_attempted: true`, `handoff_success: false` when missing durable state forces rediscovery or clarification.

## Privacy and context discipline

The evaluator intentionally avoids exact transcript capture.

Store only event metadata necessary for metrics. Paths and tool names should be bounded identifiers, not source contents. Evaluation artifacts should remain local/CI artifacts unless a small reviewed summary is intentionally committed.

## Interpretation boundary

Repository tooling cannot reliably know:

- exact remaining ChatGPT/Codex/Work credits;
- exact hidden model token consumption;
- internal model reasoning length.

Therefore the evaluator must never claim exact tokens saved or exact cost savings without an external authoritative measurement source.

Its purpose is to answer narrower questions such as:

- Did routed agents read fewer files before acting?
- Did they reread fewer files?
- Did they use fewer tool calls?
- Did they reach the first concrete action sooner?
- Did they avoid unnecessary optional-context expansion?
- Could a fresh agent resume successfully from durable state?

## Recommended target

Use ACO-003 metrics to identify regressions and compare routing changes before considering ACO-004 multi-agent parallelism. Parallel workers should not be added merely to reduce wall-clock time when they multiply context/tool overhead without a measurable benefit.
