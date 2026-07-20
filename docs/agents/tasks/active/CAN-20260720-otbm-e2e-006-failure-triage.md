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
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - .github/workflows/universal-agent-e2e.yml
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
- [x] Keep the existing Universal E2E workflow and physical runner unchanged; OTBM-E2E-006 programme scope requires deterministic classification from current artifacts, not a new workflow hook.
- [x] Do not modify OTClient route execution or persistence code owned by E2E gameplay tasks.
- [x] Add focused Python regression coverage for every required category plus success/not-applicable/unclassified behavior.
- [ ] Update `MODULE_CATALOG.md` after merged PR #615 completes active-to-archive lifecycle and releases its shared ownership of that path.
- [ ] Run focused validation plus required Universal Agent E2E proof on the exact final head.
- [ ] Apply `ci:final-gate` before the final checkpoint commit and make no post-final-head commits.
- [ ] Require exact-final-head required checks, clean review/comment/thread state, live-main overlap recheck and mergeability before squash merge with expected head SHA.
- [ ] After feature merge, complete exact active-to-archive lifecycle before declaring OTBM-E2E-006 complete.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20
head: 2d0190266fe99953da8b52eb5cfcc806e8d56c4f
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
  - docs/agents/MODULE_CATALOG.md
proven:
  - live main at task start is 060fe0fa018e55725c93daee5dd4cadec0a68162
  - OTBM-E2E-005 feature PR #600 and lifecycle PR #617 are merged and archived
  - the programme defines OTBM-E2E-006 only as first-failure classification from route plan plus current physical artifacts and prefers deterministic evidence over natural-language guessing
  - PR #620 is the active draft delivery PR for this task
  - classifier format is canary-otbm-e2e-failure-triage-v1 schemaVersion 1 with deterministic success, failure, not-applicable and fail-closed unclassified states
  - classifier consumes existing route preparation, preflight, route plan, client event, result and lifecycle artifacts without modifying their producers
  - focused sandbox unit run covered 25 cases and passed before publication of the implementation/test pair
  - CI run 29731915802 passed on published classifier/test head d8f62d36da5173f3e7fe34f06624c97758def511
  - initial ownership run 29731915649 failed only checkpoint schema validation because derived and first_failure were missing
  - corrected checkpoint ownership run 29732167372 passed on head 2d0190266fe99953da8b52eb5cfcc806e8d56c4f
  - corrected checkpoint CI run 29732167605 passed on head 2d0190266fe99953da8b52eb5cfcc806e8d56c4f
  - PR #615 merged as 9648e213792c21b59e7c8b7c5310609e6b554141 after this task branch started
  - PR #615 active task record still exists on main and still lists docs/agents/MODULE_CATALOG.md as shared ownership, so catalog editing remains deferred until lifecycle archive

derived:
  - route preparation invocation evidence plus absence of a passed preparation summary is sufficient for ROUTE_RESOLUTION_FAILURE only after exact preflight evidence has been checked first
  - MOVEMENT_TIMEOUT proves that the controlled client remained at the source until timeout and is classified as BLOCKED_TILE without claiming which actor or dynamic condition blocked movement
  - transition-specific categories require retained exact edge context; ambiguous INTERACTION_FAILED evidence remains unclassified instead of being promoted to handled or unsupported without proof
  - the existing first client error event plus preceding route edge marker provides deterministic first-failure ordering without modifying the shared OTClient scenario executor
  - adding an always() workflow hook is not required by the canonical OTBM-E2E-006 programme acceptance text and would unnecessarily widen shared integration scope; the bounded CLI classifier is the smaller compliant implementation
unknown:
  - exact PR #615 lifecycle archive PR/merge SHA and when its MODULE_CATALOG ownership will be released
  - exact final synchronized head and final-gate workflow conclusions until the catalog update and final checkpoint exist
blockers:
  - docs/agents/MODULE_CATALOG.md remains shared-owned by the still-active PR #615 task record until its lifecycle archive merges
conflicts:
  - docs/agents/MODULE_CATALOG.md overlaps the still-active CAN-20260720-e2e-gameplay-005-player-soul-persistence task; no edit will be made until that task is archived
rejected_hypotheses:
  - modifying tools/e2e/client/agent_e2e_scenario.lua is rejected because existing error events already expose deterministic route failure codes and the path belongs to gameplay persistence work
  - a second E2E workflow or runner is rejected by programme architecture
  - log-only natural-language guessing is rejected; classification must prefer structured artifacts and explicit event codes
  - treating ambiguous INTERACTION_FAILED evidence as INTERACTION_UNSUPPORTED is rejected unless retained detail explicitly proves an unsupported contract
  - adding a Universal workflow post-processing hook is rejected as unnecessary scope expansion because the programme requires a deterministic classifier over current artifacts, not automatic workflow mutation
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
  - command: Agent Task Ownership after checkpoint schema correction
    result: PASS
    evidence: Workflow run 29732167372 completed successfully on head 2d0190266fe99953da8b52eb5cfcc806e8d56c4f.
  - command: CI after checkpoint schema correction
    result: PASS
    evidence: Workflow run 29732167605 completed successfully on head 2d0190266fe99953da8b52eb5cfcc806e8d56c4f.
first_failure:
  marker: Agent Task Ownership / Validate changed active task checkpoints
  evidence: Workflow run 29731915649 rejected the initial task checkpoint because required derived and first_failure fields were absent; retained active-task-ownership artifact 8456622983 identified exactly those two missing fields.
next_action: Wait only on PR #615 lifecycle archive to release MODULE_CATALOG ownership; then synchronize the catalog entry, revalidate against current main, apply ci:final-gate, write the immutable final checkpoint, and complete PR/lifecycle closure.
```
