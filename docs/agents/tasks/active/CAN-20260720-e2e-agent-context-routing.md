---
task_id: CAN-20260720-e2e-agent-context-routing
program_id: CAN-PROGRAM-AGENT-ORCHESTRATION
coordination_id: ACO-E2E-READ-ROUTING
status: validating
agent: "GPT-5.5 Thinking"
branch: docs/e2e-agent-context-routing-20260720
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "9a7c5ebfa4cb35066293a8b75039fb61b8d8afe5"
risk: low
related_issue: ""
related_pr: "629"
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
updated_at: 2026-07-20T19:24:00+02:00
head: 56ae1bebf41773560bce708a374ae2ac1317b1b0
branch: docs/e2e-agent-context-routing-20260720
pr: 629
status: validating
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/CONTEXT_ROUTES.json
  - docs/agents/E2E_AGENT_CONTINUATION.md
  - docs/agents/tasks/active/CAN-20260720-e2e-agent-context-routing.md
proven:
  - Canary AGENTS multi-agent concurrency defines one branch and one worktree per agent and advisory owned_paths locks, not a programme-wide single-task mutex.
  - The universal-e2e context route now requires E2E_AUTOMATION_PROGRAM.md, docs/architecture/universal-e2e-gameplay-validation.md, and docs/agents/E2E_AGENT_CONTINUATION.md.
  - E2E_AGENT_CONTINUATION.md explicitly permits independent lifecycle cleanup when the merged feature task record has no live overlapping owner or ordering hold.
  - Draft PR 629 is open against current main and changes only agent context routing, E2E continuation guidance, and this task record.
derived:
  - Universal E2E resume routing now supplies durable architecture without copying that architecture into a long handover.
  - Same-program active work blocks lifecycle cleanup only when a real ownership overlap, dependency/order constraint, atomic hold, or explicit repository stop condition exists.
unknown:
  - Final exact-head Agent Task Ownership and CI outcomes after this checkpoint update.
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
    evidence: current main files inspected before branch creation
  - command: changed-file scope audit
    result: PASS
    evidence: PR 629 contains only agent governance and continuation documentation paths
blockers: []
next_action: Verify PR 629 exact-head Agent Task Ownership, CI, route-resolution behavior, review state, mergeability and main drift, then merge only if all required gates pass.
```
