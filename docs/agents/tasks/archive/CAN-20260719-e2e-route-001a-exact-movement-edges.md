---
task_id: CAN-20260719-e2e-route-001a-exact-movement-edges
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-ROUTE-001A
status: completed
agent: "GPT-5.5 Thinking"
branch: feat/e2e-route-001a-exact-movement-edges
base_branch: main
created: 2026-07-19T10:20:00+02:00
updated: 2026-07-19T10:20:24Z
last_verified_commit: "c2e27060165b91c1de6a5f40571060e480cdcb06"
risk: medium
related_issue: ""
related_pr: "573"
depends_on:
  - CAN-PROGRAM-E2E-PLATFORM existing Universal Physical E2E action-plan lifecycle
  - CAN-PROGRAM-OTBM-E2E-ROUTING merged planning programme PR #562
  - OTBM-E2E-001 route-plan contract merged as PR #567
blocks:
  - E2E-ROUTE-001 movement-only follow_route consumption
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260719-e2e-route-001a-exact-movement-edges.md
    - tests/e2e/test_exact_movement_edges.py
    - tests/e2e/scenarios/movement/physical-movement.json
  shared:
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/client/agent_e2e_scenario.lua
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
    - docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md
    - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.md
    - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.schema.json
    - tools/ai-agent/otbm_reachability*.py
    - docs/ai-agent/OTBM_SEMANTIC_LANDMARKS*
    - tools/ai-agent/otbm_semantic_landmarks.py
    - docs/ai-agent/OTBM_ROUTE_INTERACTIONS*
    - tools/ai-agent/otbm_route_interactions.py
modules_touched:
  - Universal OTS E2E automation
reuses:
  - existing scenario.steps validation and scenario-plan.lua generation
  - existing controlled OTClient generic gameplay driver
  - existing two-session safe logout persistence relog lifecycle
  - canary-otbm-e2e-route-plan-v1 exact movement edge semantics
  - physically proven movement fixture coordinates from merged PR #481
public_interfaces:
  - walk_edge exact-position-synchronized physical movement primitive
cross_repo_tasks: []
completed: 2026-07-19T10:20:24Z
---

# Goal

Implement `E2E-ROUTE-001A — exact movement-edge execution primitive` as the dependency-safe first slice of Universal `follow_route`: a generic physical action that executes one exact same-floor adjacent movement edge by asserting the controlled client's current position equals the declared source, deriving the movement direction from the exact coordinate delta, sending exactly one movement request, and waiting for the exact destination before succeeding.

This task does not claim full `E2E-ROUTE-001` completion. It deliberately excludes semantic landmarks, route interaction semantics, conditional barriers, transition execution, route artifact plumbing, static route preflight and pathfinding.

# Acceptance criteria

- [x] Add a strict bounded `walk_edge` action to the existing `scenario.steps` contract.
- [x] Require exact `from_x/from_y/from_z` and `to_x/to_y/to_z` OTBM-range integer coordinates.
- [x] Require one adjacent same-floor edge only; reject zero-length, multi-tile and floor-changing edges.
- [x] Derive one of the existing eight movement directions from coordinate delta; do not accept a caller-supplied direction as source of truth.
- [x] At runtime fail closed when current player position is not the declared source before movement.
- [x] Send exactly one `g_game.walk(...)` request and wait with a bounded timeout for exact destination equality before completing the step.
- [x] Preserve existing blind bounded `walk` behavior for backward compatibility while documenting that route execution must use `walk_edge`.
- [x] Emit deterministic existing step start/success markers and destination detail; preserve first-failure diagnostics.
- [x] Add focused tests for coordinate bounds, adjacency, direction derivation, unknown fields, deterministic rendering and runtime source-position/destination synchronization contract.
- [x] Preserve persistence checks and the canonical two-session lifecycle unchanged.
- [x] Reuse the previously physically proven movement fixture coordinates and select that scenario for a new real-client proof.
- [x] Do not modify OTBM-E2E-002 or OTBM-E2E-003 owned paths or claim their work.
- [x] Update reusable interface documentation/catalogue/changelog.
- [x] Apply `ci:final-gate` before final checkpoint commit.
- [ ] Verify exact-final-head required checks and review/merge blockers before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T10:55:00+02:00
head: 672840aa41ca7c7bedf3639f207f857785a0dbe7
branch: feat/e2e-route-001a-exact-movement-edges
pr: 573
status: validating
context_routes:
  - agent-governance
  - universal-e2e
  - otbm
owned_paths:
  - docs/agents/tasks/active/CAN-20260719-e2e-route-001a-exact-movement-edges.md
  - tests/e2e/test_exact_movement_edges.py
  - tests/e2e/scenarios/movement/physical-movement.json
  - tools/e2e/run_agent_e2e.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - live main advanced to da36fedefdf7071ad3def46e497140418c9b2f84 when the separately owned OTBM-E2E-002 PR 571 was merged
  - branch synchronization merge commit 20226ad0643668bc8bd8fdd7e68981e425f8fa87 preserves merged OTBM-E2E-002 while reapplying only this task's non-conflicting E2E files
  - OTBM-E2E-003 remains separately owned by draft PR 572 and this task does not modify its owned paths
  - no open PR or branch matching E2E-ROUTE-001A or walk_edge was found before task creation
  - existing Universal E2E bounded walk behavior remains present and unchanged
  - walk_edge validation accepts only one adjacent same-floor coordinate edge and derives direction from its delta
  - runtime walk_edge asserts exact source position sends one g_game.walk request and waits for exact destination with bounded timeout and route-drift failure
  - merged PR 481 physically proved the deterministic fixture starts at 32369,32241,7 and one east movement reaches 32370,32241,7
  - the physical-movement scenario uses those exact previously proven coordinates with walk_edge so Universal Agent E2E can re-prove the new primitive through the controlled real client
  - MODULE_CATALOG diff is limited to the intended Universal E2E row after detecting and reverting an accidental unrelated wording change
  - CHANGELOG diff contains one intended walk_edge behavior entry while preserving the merged semantic-landmark entry from OTBM-E2E-002
  - ci:final-gate was applied to PR 573 before this final checkpoint commit
  - repository writes are restricted to blakinio/canary
  - no OTBM WIDX items.otb client assets maps or generated route reports are in scope
derived:
  - an exact single-edge primitive is a dependency-safe reusable foundation for later route-plan consumption without depending on landmark or interaction registries
  - preserving the existing walk action avoids breaking existing feature scenarios while walk_edge can become the route-execution movement primitive
  - changing exactly the existing movement scenario makes the current PR eligible for deterministic same-repository scenario auto-selection and physical proof
unknown:
  - exact-final-head CI conclusion
  - exact-final-head Agent Task Ownership conclusion
  - exact-final-head Universal Agent E2E physical conclusion and artifact markers
  - exact-final-head review and mergeability state
conflicts: []
blockers: []
first_failure:
  marker: agent-task-ownership-checkpoint
  evidence: Agent Task Ownership run 29680262277 failed because CHANGED_TASK_VALIDATION.txt reported missing checkpoint field blockers; no ownership overlap was reported and the checkpoint contract was corrected before final gate
rejected_hypotheses:
  - implement full follow_route before route artifact ownership and interaction dependencies are ready
  - modify or claim OTBM-E2E-002
  - modify OTBM-E2E-003
  - add pathfinding to Universal E2E
  - replace the existing walk action and break backward compatibility
  - invent new movement coordinates instead of reusing PR 481 physical evidence
changed_paths:
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260719-e2e-route-001a-exact-movement-edges.md
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - tests/e2e/scenarios/movement/physical-movement.json
  - tests/e2e/test_exact_movement_edges.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tools/e2e/run_agent_e2e.py
validation:
  - command: live main plus targeted open PR and branch ownership preflight
    result: PASS
    evidence: PR 572 owns OTBM-E2E-003; no E2E-ROUTE-001A or walk_edge owner was found before task creation
  - command: PR 481 prior physical movement evidence review
    result: PASS
    evidence: controlled OTClient artifacts previously proved initial_position 32369,32241,7 and one east step destination 32370,32241,7 with canonical persistence relog success
  - command: Agent Task Ownership run 29680262277 artifact inspection
    result: FAIL
    evidence: CHANGED_TASK_VALIDATION.txt reported only missing checkpoint field blockers; task record corrected before final gate
  - command: PR 573 shared-document diff review after merging main da36fedefdf7071ad3def46e497140418c9b2f84
    result: PASS
    evidence: MODULE_CATALOG contains only the intended Universal E2E row change and CHANGELOG contains only the intended walk_edge entry relative to current main
next_action: Verify all required workflows and physical movement markers on the exact final PR head, confirm no review blockers and clean mergeability, then squash merge PR 573 without any further commits.
```

## Automated lifecycle completion

- Feature PR: #573.
- Feature head: `2daf83730bb8acac3f49e7748deaf68d3eaa66f1`.
- Merge commit: `c2e27060165b91c1de6a5f40571060e480cdcb06`.
- Merged at: `2026-07-19T10:20:24Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
