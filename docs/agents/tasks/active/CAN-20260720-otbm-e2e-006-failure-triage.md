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
related_pr: "620"
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

- [x] Emit one deterministic machine-readable triage result for route-aware Universal Physical E2E evidence.
- [x] Support the programme categories `ROUTE_RESOLUTION_FAILURE`, `ROUTE_PREFLIGHT_FAILURE`, `PLAN_LOAD_FAILURE`, `INITIAL_POSITION_MISMATCH`, `MOVEMENT_DIVERGENCE`, `BLOCKED_TILE`, `INTERACTION_UNSUPPORTED`, `INTERACTION_TIMEOUT`, `TELEPORT_NOT_TRIGGERED`, `WRONG_TRANSITION_DESTINATION`, `WRONG_FLOOR_DELTA`, `SERVER_DISCONNECT`, `PERSISTENCE_FAILURE`, and `RELOG_FAILURE`.
- [x] Base classification only on retained deterministic artifacts and explicit existing failure markers/codes; do not guess the runtime actor or cause of a blocked tile.
- [x] Preserve exact first-failure evidence and route edge/transition context when available.
- [x] Distinguish route resolution from exact-map preflight failure using existing route/preflight evidence rather than a second static analyzer.
- [x] Treat successful route physical E2E as `status=success` with no failure category.
- [x] Fail closed to an explicit unclassified result when evidence is insufficient or contradictory instead of inventing a supported category.
- [ ] Integrate the classifier into the existing Universal E2E physical job with an `always()` post-processing step so retained artifacts include triage even when route preparation or physical execution fails.
- [x] Do not modify OTClient route execution or persistence code owned by open PR #615.
- [x] Add focused Python regression coverage for every required category plus success/unclassified behavior.
- [ ] Update `MODULE_CATALOG.md` only after its current overlap with open PR #615 is resolved; do not edit the shared path concurrently.
- [ ] Run focused validation plus required Universal Agent E2E proof on the exact final head.
- [ ] Apply `ci:final-gate` before the final checkpoint commit and make no post-final-head commits.
- [ ] Require exact-final-head required checks, clean review/comment/thread state, live-main overlap recheck and mergeability before squash merge with expected head SHA.
- [ ] After feature merge, complete exact active-to-archive lifecycle before declaring OTBM-E2E-006 complete.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20
head: d8f62d36da5173f3e7fe34f06624c97758def511
branch: feat/otbm-e2e-006-failure-triage
pr: 620
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
  - PR #620 is the active draft delivery PR for this task
  - open PR #615 explicitly excludes workflow, route execution and OTBM changes but modifies tools/e2e/client/agent_e2e_scenario.lua and docs/agents/MODULE_CATALOG.md
  - open PR #514 has no overlap with OTBM route E2E paths
  - existing route executor emits explicit route failure codes into the existing client error event
  - existing physical runner retains result.json, client-events.tsv and lifecycle/database evidence
  - existing route preparation retains route-preparation.json on success and route-*-preflight.json before raising on exact-map preflight failure
  - existing Universal workflow already has an always() artifact upload step after route preparation and physical execution
  - classifier format is canary-otbm-e2e-failure-triage-v1 schemaVersion 1 with deterministic success, failure, not-applicable and fail-closed unclassified states
  - focused sandbox unit run covered 25 cases and passed before publication of the implementation/test pair
  - CI run 29731915802 passed on head d8f62d36da5173f3e7fe34f06624c97758def511
  - initial ownership run 29731915649 failed only changed active task checkpoint validation because derived and first_failure fields were missing

derived:
  - route preparation invocation evidence plus absence of a passed preparation summary is sufficient for ROUTE_RESOLUTION_FAILURE only after exact preflight evidence has been checked first
  - MOVEMENT_TIMEOUT proves that the controlled client remained at the source until timeout and is classified as BLOCKED_TILE without claiming which actor or dynamic condition blocked movement
  - transition-specific categories require retained exact edge context; ambiguous INTERACTION_FAILED evidence remains unclassified instead of being promoted to handled or unsupported without proof
  - the existing first client error event plus preceding route edge marker provides deterministic first-failure ordering without modifying the currently shared OTClient scenario executor
unknown:
  - whether MODULE_CATALOG overlap with PR #615 will be resolved before implementation is otherwise ready
  - exact final integration commit and final-gate workflow conclusions until the always() triage hook is implemented and validated
blockers:
  - do not edit docs/agents/MODULE_CATALOG.md while open PR #615 owns that shared path
conflicts:
  - docs/agents/MODULE_CATALOG.md overlaps open PR #615; deferred until that PR merges or ownership is otherwise resolved
rejected_hypotheses:
  - modifying tools/e2e/client/agent_e2e_scenario.lua is rejected because open PR #615 currently owns that path and existing error events already expose deterministic route failure codes
  - a second E2E workflow or runner is rejected by programme architecture
  - log-only natural-language guessing is rejected; classification must prefer structured artifacts and explicit event codes
  - treating ambiguous INTERACTION_FAILED evidence as INTERACTION_UNSUPPORTED is rejected unless the retained detail explicitly proves an unsupported contract
changed_paths:
  - docs/agents/tasks/active/CAN-20260720-otbm-e2e-006-failure-triage.md
  - tools/e2e/otbm_route_failure_triage.py
  - tests/e2e/test_otbm_route_failure_triage.py
validation:
  - command: focused unittest contract for OTBM route failure triage
    result: PASS
    evidence: 25 focused cases passed in the pre-publication sandbox run, covering all required programme categories plus success, not-applicable and unclassified states.
  - command: CI on published classifier/test head d8f62d36da5173f3e7fe34f06624c97758def511
    result: PASS
    evidence: Workflow run 29731915802 completed successfully.
first_failure:
  marker: Agent Task Ownership / Validate changed active task checkpoints
  evidence: Workflow run 29731915649 rejected the initial task checkpoint because required derived and first_failure fields were absent; retained active-task-ownership artifact 8456622983 identified exactly those two missing fields.
next_action: Re-run ownership with the corrected checkpoint, finish the minimal always() Universal E2E triage hook, then validate the automatic retained artifact before touching MODULE_CATALOG.md.
```
