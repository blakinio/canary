---
task_id: CAN-20260720-e2e-agent-context-routing
program_id: CAN-PROGRAM-AGENT-ORCHESTRATION
coordination_id: ACO-E2E-READ-ROUTING
status: validating
agent: "GPT-5.5 Thinking"
branch: docs/e2e-agent-context-routing-replay-20260720
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "8ed836aae47d6bb882fb646169d2930f951c6c0d"
risk: low
related_issue: ""
related_pr: "633"
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
updated_at: 2026-07-20T21:49:00+02:00
head: 3b30f8fac424b26d5774bf1f6ee6e320cd4e45fd
branch: docs/e2e-agent-context-routing-replay-20260720
pr: 633
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
  - The universal-e2e context route requires E2E_AUTOMATION_PROGRAM.md, docs/architecture/universal-e2e-gameplay-validation.md, and docs/agents/E2E_AGENT_CONTINUATION.md.
  - E2E_AGENT_CONTINUATION.md explicitly permits independent lifecycle cleanup when the merged feature task record has no live overlapping owner or ordering hold.
  - Original PR 629 exact head 3712f0a96ed107b0462f1bafc4d257378aceb196 passed Agent Task Ownership and CI and had no review threads, but main advanced by two unrelated OAM commits before merge.
  - Clean replay PR 633 starts from current main 8ed836aae47d6bb882fb646169d2930f951c6c0d and changes the same three bounded governance paths.
derived:
  - A clean replay from current main preserves the exact three-path scope without force-updating published history.
  - Same-program active work blocks lifecycle cleanup only when a real ownership overlap, dependency/order constraint, atomic hold, or explicit repository stop condition exists.
unknown:
  - Exact-head PR 633 ownership, CI, review and mergeability outcomes.
conflicts: []
first_failure:
  marker: base-modified-before-merge
  evidence: expected-head squash merge of PR 629 returned GitHub 405 because main advanced after final validation.
rejected_hypotheses:
  - force-rewrite published PR branch: repository policy requires force-with-lease semantics unavailable through the connector.
changed_paths:
  - docs/agents/CONTEXT_ROUTES.json
  - docs/agents/E2E_AGENT_CONTINUATION.md
  - docs/agents/tasks/active/CAN-20260720-e2e-agent-context-routing.md
validation:
  - command: original PR 629 exact-head Agent Task Ownership and CI
    result: PASS
    evidence: head 3712f0a96ed107b0462f1bafc4d257378aceb196; ownership and CI succeeded
  - command: original PR 629 review-thread audit
    result: PASS
    evidence: zero review threads
  - command: original PR 629 main-drift audit
    result: FAIL
    evidence: current main advanced to 8ed836aae47d6bb882fb646169d2930f951c6c0d with two unrelated OAM commits
  - command: clean replay scope reconstruction
    result: PASS
    evidence: PR 633 starts at current main and recreates only the same three task paths
blockers: []
next_action: Close superseded PR 629, verify PR 633 exact-head Agent Task Ownership, CI, route-resolution behavior, review state, mergeability and main drift, then squash-merge only if all required gates pass.
```
