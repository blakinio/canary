---
task_id: CAN-20260720-otbm-e2e-006-failure-triage
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-006
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-006-failure-triage
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "060fe0fa018e55725c93daee5dd4cadec0a68162"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - merged and archived OTBM-E2E-005 / PR #600
  - existing Universal Physical E2E artifact lifecycle
blocks:
  - OTBM-E2E-007 and later second-stage routing enhancements
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260720-otbm-e2e-006-failure-triage.md
    - tools/e2e/otbm_route_failure_triage.py
    - tests/e2e/test_otbm_route_failure_triage.py
  shared:
    - .github/workflows/universal-agent-e2e.yml
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
    - docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md
    - tools/e2e/prepare_otbm_route.py
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/route_plan_execution.py
    - tools/e2e/client/agent_e2e_route.lua
    - tools/e2e/client/agent_e2e_scenario.lua
modules_touched:
  - OTBM-aware Universal E2E deterministic failure triage
reuses:
  - existing Universal E2E retained artifact directory
  - result.json
  - client-events.tsv
  - route-preparation.json
  - route-*-preflight.json
  - route-*.json
  - existing route executor failure codes
  - existing safe logout/persistence/relog markers
public_interfaces:
  - deterministic machine-readable OTBM route physical E2E first-failure classification artifact
cross_repo_tasks: []
---

# Goal

Deliver `OTBM-E2E-006 — Automatic E2E failure triage` as a deterministic, artifact-only classifier for the existing Universal Physical E2E route lifecycle. The classifier identifies the first supported failure category from retained route preparation, exact-map preflight, route plan, client event, result and lifecycle evidence without natural-language guessing and without creating a second runner, parser or physical-client lifecycle.

# Acceptance criteria

- [ ] Emit one deterministic machine-readable triage result for route-aware Universal Physical E2E evidence.
- [ ] Support the programme categories `ROUTE_RESOLUTION_FAILURE`, `ROUTE_PREFLIGHT_FAILURE`, `PLAN_LOAD_FAILURE`, `INITIAL_POSITION_MISMATCH`, `MOVEMENT_DIVERGENCE`, `BLOCKED_TILE`, `INTERACTION_UNSUPPORTED`, `INTERACTION_TIMEOUT`, `TELEPORT_NOT_TRIGGERED`, `WRONG_TRANSITION_DESTINATION`, `WRONG_FLOOR_DELTA`, `SERVER_DISCONNECT`, `PERSISTENCE_FAILURE`, and `RELOG_FAILURE`.
- [ ] Base classification only on retained deterministic artifacts and explicit existing failure markers/codes; do not guess the runtime actor or cause of a blocked tile.
- [ ] Preserve exact first-failure evidence and route edge/transition context when available.
- [ ] Distinguish route resolution from exact-map preflight failure using existing route/preflight evidence rather than a second static analyzer.
- [ ] Treat successful route physical E2E as `status=success` with no failure category.
- [ ] Fail closed to an explicit unclassified result when evidence is insufficient or contradictory instead of inventing a supported category.
- [ ] Integrate the classifier into the existing Universal E2E physical job with an `always()` post-processing step so retained artifacts include triage even when route preparation or physical execution fails.
- [ ] Do not modify OTClient route execution or persistence code owned by open PR #615.
- [ ] Add focused Python regression coverage for every required category plus success/unclassified behavior.
- [ ] Update `MODULE_CATALOG.md` only after its current overlap with open PR #615 is resolved; do not edit the shared path concurrently.
- [ ] Run focused validation plus required Universal Agent E2E proof on the exact final head.
- [ ] Apply `ci:final-gate` before the final checkpoint commit and make no post-final-head commits.
- [ ] Require exact-final-head required checks, clean review/comment/thread state, live-main overlap recheck and mergeability before squash merge with expected head SHA.
- [ ] After feature merge, complete exact active-to-archive lifecycle before declaring OTBM-E2E-006 complete.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20
head: 060fe0fa018e55725c93daee5dd4cadec0a68162
branch: feat/otbm-e2e-006-failure-triage
pr: null
status: implementing
context_routes:
  - agent-governance
  - otbm
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260720-otbm-e2e-006-failure-triage.md
  - tools/e2e/otbm_route_failure_triage.py
  - tests/e2e/test_otbm_route_failure_triage.py
  - .github/workflows/universal-agent-e2e.yml
  - docs/agents/MODULE_CATALOG.md
proven:
  - live main at task start is 060fe0fa018e55725c93daee5dd4cadec0a68162
  - OTBM-E2E-005 feature PR #600 and lifecycle PR #617 are merged and archived
  - the programme explicitly defines OTBM-E2E-006 as deterministic first-failure classification after the reference route
  - open PR #615 explicitly excludes workflow, route execution and OTBM changes but modifies tools/e2e/client/agent_e2e_scenario.lua and docs/agents/MODULE_CATALOG.md
  - open PR #514 has no overlap with OTBM route E2E paths
  - existing route executor emits explicit route failure codes into the existing client error event
  - existing physical runner retains result.json, client-events.tsv and lifecycle/database evidence
  - existing route preparation retains route-preparation.json on success and route-*-preflight.json before raising on exact-map preflight failure
  - existing Universal workflow already has an always() artifact upload step after route preparation and physical execution
unknown:
  - final exact classifier schema and CLI shape until focused tests lock it
  - whether MODULE_CATALOG overlap with PR #615 will be resolved before implementation is otherwise ready
blockers:
  - do not edit docs/agents/MODULE_CATALOG.md while open PR #615 owns that shared path
conflicts:
  - docs/agents/MODULE_CATALOG.md overlaps open PR #615; deferred until that PR merges or ownership is otherwise resolved
rejected_hypotheses:
  - modifying tools/e2e/client/agent_e2e_scenario.lua is rejected because open PR #615 currently owns that path and existing error events already expose deterministic route failure codes
  - a second E2E workflow or runner is rejected by programme architecture
  - log-only natural-language guessing is rejected; classification must prefer structured artifacts and explicit event codes
changed_paths:
  - docs/agents/tasks/active/CAN-20260720-otbm-e2e-006-failure-triage.md
validation: []
next_action: Publish the draft PR, then implement the standalone deterministic artifact classifier and focused tests without touching MODULE_CATALOG.md until PR #615 resolves its shared-path ownership.
```
