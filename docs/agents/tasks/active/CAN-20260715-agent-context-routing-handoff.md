# CAN-20260715-agent-context-routing-handoff

## Summary

Reduce mandatory agent context loading and define deterministic continuation when a conversation slows down or approaches context exhaustion.

## Ownership

- owned_paths:
  - `AGENTS.md`
  - `docs/agents/README.md`
  - `docs/agents/CONTEXT_ROUTING.md`
  - `docs/agents/CONTEXT_HANDOFF.md`
  - `docs/agents/tasks/active/CAN-20260715-agent-context-routing-handoff.md`
- modules_touched:
  - agent governance
  - agent coordination
- reuses:
  - existing task-record source-of-truth model
  - existing `REPOSITORY_MAP.md`
  - existing module catalogue and program records
- depends_on: []
- blocks: []
- cross_repository_task_ids: []

## Acceptance criteria

- Agents no longer need to preload all large coordination/index documents for every task.
- Large indexes are searched before full-file reads.
- Task-specific context is selected through explicit routes.
- Context pressure/exhaustion has a deterministic checkpoint and handoff procedure.
- A continuation agent can resume from Git + task record + PR without previous chat history.
- Existing repository safety and merge rules remain intact.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T00:00:00Z
head: UNKNOWN
branch: docs/agent-context-routing-handoff
pr: none
status: implementing
context_routes:
  - agent-governance
owned_paths:
  - AGENTS.md
  - docs/agents/README.md
  - docs/agents/CONTEXT_ROUTING.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/tasks/active/CAN-20260715-agent-context-routing-handoff.md
proven:
  - Root AGENTS.md currently mandates broad startup reads including README, ACTIVE_WORK/task/PR state, MODULE_CATALOG, REPOSITORY_MAP, KNOWN_RISKS, BUILD_TEST_MATRIX and cross-repo contracts.
  - docs/agents/README.md defines another broad read order and already states that chat history is not authoritative.
derived:
  - Mandatory broad startup loading creates avoidable context pressure for narrow tasks.
unknown: []
conflicts: []
first_failure:
  marker: none
  evidence: documentation optimization task
rejected_hypotheses: []
changed_paths:
  - docs/agents/CONTEXT_ROUTING.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/tasks/active/CAN-20260715-agent-context-routing-handoff.md
validation:
  - command: documentation review
    result: NOT_RUN
    evidence: pending final diff review
blockers: []
next_action: Update root AGENTS.md and docs/agents/README.md to route context instead of preloading broad documentation.
```
