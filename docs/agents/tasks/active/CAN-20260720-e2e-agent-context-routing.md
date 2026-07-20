---
task_id: CAN-20260720-e2e-agent-context-routing
program_id: CAN-PROGRAM-AGENT-ORCHESTRATION
coordination_id: ACO-E2E-READ-ROUTING
status: implementing
agent: "GPT-5.5 Thinking"
branch: docs/e2e-agent-context-routing-20260720-final
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "8ed836aae47d6bb882fb646169d2930f951c6c0d"
risk: low
related_issue: ""
related_pr: ""
depends_on:
  - merged ACO context routing and compact resume infrastructure
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260720-e2e-agent-context-routing.md
    - docs/agents/E2E_AGENT_CONTINUATION.md
  shared:
    - docs/agents/CONTEXT_ROUTES.json
modules_touched:
  - agent context routing
  - Universal OTS E2E handoff guidance
reuses:
  - existing Canary context router and resume.py
public_interfaces:
  - universal-e2e required read route
cross_repo_tasks: []
---

# Goal

Ensure Universal OTS E2E continuation agents automatically load the durable gameplay-validation architecture and do not treat unrelated active work in the same programme as a global mutex for non-overlapping lifecycle cleanup.

# Acceptance criteria

- [x] `universal-e2e` route requires the durable E2E architecture document.
- [x] E2E continuation guidance explicitly distinguishes per-agent branch/worktree isolation from programme-wide task blocking.
- [x] Independent lifecycle cleanup may proceed when ownership paths do not overlap and no dependency/atomic hold exists.
- [x] Existing ownership and overlap protections remain fail-closed.
- [x] No E2E runtime, OTBM, workflow, map, client asset, persistence, or gameplay code changes.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20T19:43:00+02:00
head: 8ed836aae47d6bb882fb646169d2930f951c6c0d
branch: docs/e2e-agent-context-routing-20260720-final
pr: none
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/CONTEXT_ROUTES.json
  - docs/agents/E2E_AGENT_CONTINUATION.md
  - docs/agents/tasks/active/CAN-20260720-e2e-agent-context-routing.md
proven:
  - Canary AGENTS multi-agent concurrency defines one branch and one worktree per agent and advisory owned_paths locks, not a programme-wide single-task mutex.
  - The universal-e2e context route requires E2E_AUTOMATION_PROGRAM.md, docs/architecture/universal-e2e-gameplay-validation.md, and docs/agents/E2E_AGENT_CONTINUATION.md.
  - E2E_AGENT_CONTINUATION.md explicitly permits independent lifecycle cleanup when the merged feature task record has no live overlapping owner or ordering hold.
  - Main drift since the original candidate touched only OAM-025 documentation and archive paths and did not overlap this task.
derived:
  - Universal E2E resume routing supplies durable architecture without copying that architecture into a long handover.
  - Same-program active work blocks lifecycle cleanup only when a real ownership overlap, dependency/order constraint, atomic hold, or explicit repository stop condition exists.
unknown:
  - Final PR number and exact-head gate outcomes for the replayed branch.
conflicts: []
first_failure:
  marker: e2e-agent-overconstrained-concurrency
  evidence: user-provided screenshot showed an agent declining independent lifecycle cleanup because another E2E-related task was active.
rejected_hypotheses:
  - same programme implies a global mutex: root AGENTS.md defines per-agent branch/worktree isolation and path-overlap ownership checks instead.
changed_paths:
  - docs/agents/CONTEXT_ROUTES.json
  - docs/agents/E2E_AGENT_CONTINUATION.md
  - docs/agents/tasks/active/CAN-20260720-e2e-agent-context-routing.md
validation:
  - command: live AGENTS and E2E route/program audit
    result: PASS
    evidence: authoritative main files inspected before replay
  - command: main drift overlap audit
    result: PASS
    evidence: two intervening main commits changed only OAM-025 documentation and archive paths
blockers: []
next_action: Open a fresh draft PR from the replayed branch, bind the PR number in this task record, then run exact-head Agent Task Ownership and CI gates.
```
