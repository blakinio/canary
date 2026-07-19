---
task_id: CAN-20260719-otbm-e2e-004-static-route-preflight
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-004
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-004-static-route-preflight
base_branch: main
created: 2026-07-19
updated: 2026-07-19
last_verified_commit: "f1f4a67c70909c93b1912f22e35f9350dc935d00"
risk: medium
related_issue: ""
related_pr: "594"
depends_on:
  - merged PR #567 canary-otbm-e2e-route-plan-v1
  - merged PR #571 canary-otbm-semantic-landmarks-v1
  - merged PR #572 canary-otbm-route-interactions-v1
  - merged PR #580 executable interaction-aware routing
  - merged PR #589 Universal follow_route execution
blocks:
  - OTBM-E2E-005 reference physical route integration
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260719-otbm-e2e-004-static-route-preflight.md
    - tools/ai-agent/otbm_route_preflight.py
    - tools/ai-agent/test_otbm_route_preflight.py
    - docs/ai-agent/OTBM_E2E_ROUTE_PREFLIGHT.md
    - docs/ai-agent/OTBM_E2E_ROUTE_PREFLIGHT.schema.json
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/otbm_reachability*.py
    - tools/ai-agent/otbm_world_index*.py
    - tools/ai-agent/otbm_semantic_landmarks.py
    - tools/ai-agent/otbm_route_interactions.py
    - tools/ai-agent/otbm_script_resolution*.py
    - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.schema.json
    - docs/ai-agent/OTBM_SEMANTIC_LANDMARKS.schema.json
    - docs/ai-agent/OTBM_ROUTE_INTERACTIONS.schema.json
modules_touched:
  - OTBM exact-map static route preflight
reuses:
  - canary-otbm-e2e-route-plan-v1
  - canary-otbm-semantic-landmarks-v1
  - canary-otbm-route-interactions-v1
  - existing Unified OTBM World Index evidence
  - existing Reachability movement and transition semantics
  - existing Script Resolution evidence states
public_interfaces:
  - canary-otbm-e2e-route-preflight-v1
cross_repo_tasks: []
---

# Goal

Implement `OTBM-E2E-004 — Exact-map static route preflight` as a deterministic fail-closed validator over existing OTBM route-plan and evidence contracts. The preflight must reject stale, incomplete or unsupported executable plans before an expensive physical Canary + controlled-OTClient run, without adding another parser, World Index, pathfinder, runner or workflow.

# Acceptance criteria

- [ ] Add versioned `canary-otbm-e2e-route-preflight-v1` result schema and public contract documentation.
- [ ] Validate route-plan format/version, executable status, completeness and continuous start-to-goal state sequence.
- [ ] Verify exact runtime map SHA-256 and World Index SHA-256 against route provenance.
- [ ] Verify every walk edge is adjacent under the declared cardinal/diagonal policy and enforce no-corner-cutting evidence for diagonals.
- [ ] Verify referenced World Index tiles still exist and match the route execution policy without silently crossing unknown conditional barriers.
- [ ] Re-resolve semantic landmark anchors when a landmark request is present and require exact start/goal/region agreement.
- [ ] Revalidate transition IDs, exact source/destination and expected item evidence.
- [ ] Revalidate required interaction selectors and fail closed for unsupported activation or blocked Script Resolution evidence.
- [ ] Emit deterministic first blocker plus bounded findings without claiming runtime gameplay proof.
- [ ] Add focused tests for success, provenance mismatch, stale landmark, invalid walk/diagonal, stale transition, blocked script resolution, unsupported activation and truncated/incomplete route.
- [ ] Do not modify `.otbm`, `.widx`, `items.otb`, client assets, `tools/e2e/**` or workflows.
- [ ] Apply `ci:final-gate` before the final checkpoint commit and pass exact-final-head required checks before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19
head: f1f4a67c70909c93b1912f22e35f9350dc935d00
branch: feat/otbm-e2e-004-static-route-preflight
pr: 594
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_route_preflight.py
  - tools/ai-agent/test_otbm_route_preflight.py
  - docs/ai-agent/OTBM_E2E_ROUTE_PREFLIGHT.md
  - docs/ai-agent/OTBM_E2E_ROUTE_PREFLIGHT.schema.json
proven:
  - live main at task start is a8ad5dcc0d1b5a2e399fc96d24d987fb633b7344
  - OTBM-E2E-001, OTBM-E2E-002, OTBM-E2E-003, OTBM-E2E-001B and E2E-ROUTE-001 are merged and lifecycle-archived
  - no open PR or branch matching OTBM-E2E-004 or static route preflight was found at task start
  - open PR #591 does not touch the planned exclusive tools/ai-agent or docs/ai-agent paths
  - PR #594 owns feat/otbm-e2e-004-static-route-preflight
  - programme requires OTBM-E2E-004 before OTBM-E2E-005
  - this package will remain a static evidence validator and will not add a second physical E2E runner/workflow or modify tools/e2e
  - no binary map/index/client asset will be committed
  - plain optimistic reachability remains insufficient for physical executability
  - unresolved/conflicting Script Resolution evidence must not be promoted to executable

derived:
  - the smallest dependency-safe 004 package is a reusable deterministic preflight module plus schema/docs/focused tests, leaving real Thais landmark binding and physical reference-route integration to OTBM-E2E-005
unknown:
  - exact reusable validation/helper APIs in the merged route-plan, landmark, interaction and World Index modules still need source inspection
conflicts: []
rejected_hypotheses:
  - implementing another OTBM parser, World Index or pathfinder is forbidden and unnecessary
  - integrating thais.temple -> thais.depot in this task is rejected because OTBM-E2E-005 owns the real reference route
  - modifying tools/e2e or workflows is rejected for this static reusable package unless later source evidence proves a mandatory contract gap
changed_paths:
  - docs/agents/tasks/active/CAN-20260719-otbm-e2e-004-static-route-preflight.md
blockers: []
first_failure: null
validation: []
next_action: Inspect the exact merged route-plan, landmark, interaction, Reachability and World Index APIs and implement the smallest fail-closed preflight validator.
```
