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
updated_at: 2026-07-15T15:00:00Z
head: 818d62eb68b9e11a9915e48301a6680d4c120090
branch: docs/agent-context-routing-handoff
pr: none
status: validating
context_routes:
  - agent-governance
owned_paths:
  - AGENTS.md
  - docs/agents/README.md
  - docs/agents/CONTEXT_ROUTING.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/tasks/active/CAN-20260715-agent-context-routing-handoff.md
proven:
  - Previous root AGENTS.md mandated broad startup reads including README, ACTIVE_WORK/task/PR state, MODULE_CATALOG, REPOSITORY_MAP, KNOWN_RISKS, BUILD_TEST_MATRIX and cross-repo contracts.
  - Previous docs/agents/README.md defined a second broad read order while also stating that chat history is not authoritative.
  - Root AGENTS.md now uses a lean startup protocol and targeted context routes.
  - docs/agents/README.md now tells agents to search large indexes before full-file reads.
  - CONTEXT_HANDOFF.md defines checkpoint timing, a compact evidence schema and a continuation-agent startup contract.
  - Compared with current main, the branch changes only five agent-governance documentation/task files.
derived:
  - Narrow tasks can start with materially less unrelated context while preserving existing safety gates.
  - A slowing or near-exhausted agent can terminate cleanly after persisting one deterministic next_action instead of carrying chat history forward.
unknown:
  - CI result after draft PR creation.
conflicts: []
first_failure:
  marker: none
  evidence: documentation optimization task
rejected_hypotheses: []
changed_paths:
  - AGENTS.md
  - docs/agents/README.md
  - docs/agents/CONTEXT_ROUTING.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/tasks/active/CAN-20260715-agent-context-routing-handoff.md
validation:
  - command: GitHub compare main...docs/agent-context-routing-handoff
    result: PASS
    evidence: five expected documentation/task files only; no binary/map/datapack/runtime paths changed
blockers:
  - Branch is one commit behind current main and must be brought current before merge if required by repository policy/CI.
next_action: Open a draft PR, inspect required CI on the PR head, and update/rebase the branch before merge if necessary.
```
