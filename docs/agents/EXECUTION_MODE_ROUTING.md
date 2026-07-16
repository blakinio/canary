# Agent Execution Mode Routing

Use this policy to choose between Chat, Codex and Work without wasting scarce agentic usage.

## Default budget policy

`minimize_agentic_usage`

The cheapest sufficient mode wins. Do not recommend a more agentic mode only because it is available.

## CHAT

Prefer CHAT for:

- problem analysis, root-cause triage and architecture reasoning;
- repository/document discovery through available connectors;
- GitHub PR, review and CI inspection/repair when no local execution is required;
- planning, task decomposition, ownership, checkpoint and handoff management;
- prompt, policy and agent-governance work;
- small repository changes that available connector tools can safely perform.

Stay in CHAT until a concrete capability gap is proven.

Escalate from CHAT to CODEX only when the task materially requires a local edit/build/test/runtime loop, physical-client execution, local debugging, or isolated coding workers.

Escalate from CHAT to WORK only when the task materially requires broad multi-source research or a large final deliverable.

## CODEX

Use CODEX for a bounded executable package such as:

- iterative `edit -> compile/build -> test -> inspect failure -> edit` work;
- C++/CMake/runtime debugging that requires a real checkout;
- local server/client execution;
- physical-client or E2E scenario execution;
- tools that need local artifacts unavailable through connectors;
- independent parallel coding tasks with isolated branches/worktrees.

Do not spend CODEX usage on broad repository orientation that CHAT already completed.

Before CODEX starts, provide a compact evidence bundle containing only:

- task ID and acceptance criteria;
- current branch/head/PR;
- relevant context routes and required reads;
- exact source paths/symbols needed for the bounded execution step;
- PROVEN facts;
- UNKNOWN/CONFLICT items;
- first failed invariant/check and evidence;
- changed paths and validation already completed;
- one `next_action`.

After the bounded execution loop, checkpoint results and return coordination to CHAT for review, PR/CI orchestration and merge unless another local execution loop is still required.

## WORK

Use WORK only for a bounded package that benefits from large-scale research or deliverable production, for example:

- comparison across many external sources/documents;
- a broad evidence synthesis or research report;
- a large structured final deliverable where research and assembly dominate.

Do not use WORK as a replacement for CODEX code execution or ordinary CHAT analysis.

Before WORK starts, provide only the research question, source/evidence constraints, required routed documents, current PROVEN/UNKNOWN/CONFLICT state, deliverable contract and one `next_action`.

After the package is produced, return coordination to CHAT.

## Token and credit discipline

The platform may not expose exact remaining token/credit counts to repository tooling, so recommendations use capability and context-pressure signals rather than invented numeric budgets.

Mandatory rules:

1. Never preload whole chat history into CODEX or WORK.
2. Never preload the whole repository.
3. Never paste full logs or diffs when an exact artifact/job/path/commit reference is sufficient.
4. Search large indexes before full reads.
5. Do not rediscover PROVEN facts unless live evidence changed.
6. Keep optional context unloaded until a blocker proves it is needed.
7. Split unrelated work into separate bounded tasks rather than one giant agentic session.
8. Checkpoint before context exhaustion, then resume from repository state.
9. Prefer sequential CHAT-supervised workers when parallel agentic execution would consume credits without clear wall-clock benefit.
10. Use parallel CODEX workers only for independently owned paths/tasks.

## Deterministic advisor

Use:

```sh
python tools/agents/execution_mode.py --task-text "<task>" [capability flags]
```

Important flags:

- `--needs-local-execution`: strongly favors CODEX;
- `--broad-research`: strongly favors WORK;
- `--large-deliverable`: favors WORK;
- `--parallel-workers`: adds a bounded CODEX signal;
- `--github-only`: favors CHAT;
- `--budget-policy minimize_agentic_usage`: default and recommended for scarce limits.

A recommendation is advisory. Repository safety, ownership, CI and merge gates remain mandatory regardless of mode.
