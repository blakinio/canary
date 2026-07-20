---
task_id: CAN-20260720-e2e-agent-context-routing
program_id: CAN-PROGRAM-AGENT-ORCHESTRATION
coordination_id: ACO-E2E-READ-ROUTING
status: implementing
agent: "GPT-5.5 Thinking"
branch: docs/e2e-agent-context-routing-20260720
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "9a7c5ebfa4cb35066293a8b75039fb61b8d8afe5"
risk: low
related_issue: ""
related_pr: ""
depends_on:
  - merged ACO context routing and compact resume infrastructure
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260720-e2e-agent-context-routing.md
  shared:
    - docs/agents/CONTEXT_ROUTES.json
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
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

- [ ] `universal-e2e` route requires the durable E2E architecture document.
- [ ] E2E programme guidance explicitly distinguishes per-agent branch/worktree isolation from programme-wide task blocking.
- [ ] Independent lifecycle cleanup may proceed when ownership paths do not overlap and no dependency/atomic hold exists.
- [ ] Existing ownership and overlap protections remain fail-closed.
- [ ] No E2E runtime, OTBM, workflow, map, client asset, persistence, or gameplay code changes.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20T19:15:00+02:00
head: 9a7c5ebfa4cb35066293a8b75039fb61b8d8afe5
branch: docs/e2e-agent-context-routing-20260720
pr: none
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/CONTEXT_ROUTES.json
  - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260720-e2e-agent-context-routing.md
proven:
  - Canary AGENTS multi-agent concurrency defines one branch and one worktree per agent and advisory owned_paths locks, not a programme-wide single-task mutex.
  - The universal-e2e context route currently requires E2E_AUTOMATION_PROGRAM.md but not docs/architecture/universal-e2e-gameplay-validation.md.
  - The E2E programme itself names docs/architecture/universal-e2e-gameplay-validation.md as durable architecture and requires future agents to read it.
derived:
  - A continuation agent can miss durable architecture through route-based resume even though the programme handoff expects it.
  - Same-program active work should block lifecycle cleanup only when ownership paths, dependencies, atomic ordering, or another explicit hold actually conflict.
unknown: []
conflicts: []
first_failure:
  marker: e2e-agent-overconstrained-concurrency
  evidence: user-provided screenshot showed an agent declining independent lifecycle cleanup because another E2E-related task was active.
rejected_hypotheses:
  - same programme implies a global mutex: root AGENTS.md defines per-agent branch/worktree isolation and path-overlap ownership checks instead.
changed_paths:
  - docs/agents/tasks/active/CAN-20260720-e2e-agent-context-routing.md
validation:
  - command: live AGENTS and E2E route/program audit
    result: PASS
    evidence: current main files inspected before branch creation
blockers: []
next_action: Update the universal-e2e route and E2E programme handoff/concurrency guidance, then validate the changed task and exact branch diff.
```
