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
last_verified_commit: "5e9930815d317b91f4f688cc91f1b79888ed51f6"
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
    - tools/ai-agent/test_otbm_route_preflight_paths.py
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

- [x] Add versioned `canary-otbm-e2e-route-preflight-v1` result schema and public contract documentation.
- [x] Validate route-plan format/version, executable status, completeness and continuous start-to-goal state sequence.
- [x] Verify exact runtime map SHA-256 and World Index SHA-256 against route provenance.
- [x] Verify every walk edge is adjacent under the declared cardinal/diagonal policy and enforce no-corner-cutting evidence for diagonals.
- [x] Verify referenced World Index tiles still exist and match the route execution policy without silently crossing unknown conditional barriers through canonical Reachability regeneration.
- [x] Re-resolve semantic landmark anchors when a landmark request is present and require exact start/goal/region agreement.
- [x] Revalidate transition IDs, exact source/destination and expected item evidence through canonical route regeneration and transition-state comparison.
- [x] Revalidate required interaction selectors and fail closed for unsupported activation or blocked Script Resolution evidence.
- [x] Emit deterministic first blocker plus bounded findings without claiming runtime gameplay proof.
- [x] Add focused tests for success, provenance mismatch, stale landmark, invalid walk/diagonal, stale transition, blocked script resolution, unsupported activation, truncated/incomplete route and canonical exporter path integration.
- [x] Do not modify `.otbm`, `.widx`, `items.otb`, client assets, `tools/e2e/**` or workflows.
- [ ] Apply `ci:final-gate` before the final checkpoint commit and pass exact-final-head required checks before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19
head: 5e9930815d317b91f4f688cc91f1b79888ed51f6
branch: feat/otbm-e2e-004-static-route-preflight
pr: 594
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_route_preflight.py
  - tools/ai-agent/test_otbm_route_preflight.py
  - tools/ai-agent/test_otbm_route_preflight_paths.py
  - docs/ai-agent/OTBM_E2E_ROUTE_PREFLIGHT.md
  - docs/ai-agent/OTBM_E2E_ROUTE_PREFLIGHT.schema.json
proven:
  - live main at task start is a8ad5dcc0d1b5a2e399fc96d24d987fb633b7344
  - OTBM-E2E-001, OTBM-E2E-002, OTBM-E2E-003, OTBM-E2E-001B and E2E-ROUTE-001 are merged and lifecycle-archived
  - no open PR or branch matching OTBM-E2E-004 or static route preflight was found at task start
  - open PR #591 does not touch the exclusive tools/ai-agent or docs/ai-agent paths owned by PR #594
  - PR #594 owns feat/otbm-e2e-004-static-route-preflight
  - programme requires OTBM-E2E-004 before OTBM-E2E-005
  - implementation reuses export_route_plan_index_path so current exact-map verification reruns the existing Reachability classification and canonical _bfs rather than adding another pathfinder
  - implementation reuses the existing semantic landmark resolver and current route-interaction activation/script-status contracts
  - runtime map, World Index, appearances and every referenced optional evidence input are SHA-256 matched fail-closed before canonical regeneration
  - route-plan hash, executable status, path completeness, continuity, movement adjacency, diagonal policy, transition evidence and supported activation semantics are validated before physical execution
  - no binary map/index/client asset, tools/e2e file or workflow is modified
  - plain optimistic reachability remains insufficient for physical executability
  - unresolved/conflicting Script Resolution evidence is not promoted to executable
  - head 5e9930815d317b91f4f688cc91f1b79888ed51f6 passed AI Agent Tools, OTBM Map Tools and main CI
  - AI Agent Tools test discovery executed the focused test_otbm_route_preflight.py suite successfully
  - corrected task checkpoint passed Agent Task Ownership on head c332f5bd7cd66107f42fa563f71b79357bda1c3c

derived:
  - exact canonical route regeneration is the narrowest way to re-check tile classification, diagonal corner constraints, transitions and interaction-aware executable policy without duplicating the existing parser, World Index, classifier or BFS
  - real Thais landmark binding and physical reference-route execution remain OTBM-E2E-005 scope
unknown:
  - result of the newly added canonical-exporter path integration tests
  - final MODULE_CATALOG and CHANGELOG shared-document reconciliation
  - exact-final-head final-gate results
conflicts: []
rejected_hypotheses:
  - implementing another OTBM parser, World Index or pathfinder is forbidden and unnecessary
  - integrating thais.temple -> thais.depot in this task is rejected because OTBM-E2E-005 owns the real reference route
  - modifying tools/e2e or workflows is rejected because the static preflight can compose existing OTBM evidence APIs without changing the physical runner
changed_paths:
  - docs/agents/tasks/active/CAN-20260719-otbm-e2e-004-static-route-preflight.md
  - docs/ai-agent/OTBM_E2E_ROUTE_PREFLIGHT.md
  - docs/ai-agent/OTBM_E2E_ROUTE_PREFLIGHT.schema.json
  - tools/ai-agent/otbm_route_preflight.py
  - tools/ai-agent/test_otbm_route_preflight.py
  - tools/ai-agent/test_otbm_route_preflight_paths.py
blockers: []
first_failure:
  marker: Agent Task Ownership / Validate changed active task checkpoints
  evidence: Run 29693397731 failed because first_failure was null instead of the required YAML mapping; the task record was corrected without weakening the validator and ownership then passed.
validation:
  - command: AI Agent Tools on head 5e9930815d317b91f4f688cc91f1b79888ed51f6
    result: PASS
    evidence: Workflow run 29693397722 completed successfully, including the discovered focused Python route-preflight tests.
  - command: OTBM Map Tools on head 5e9930815d317b91f4f688cc91f1b79888ed51f6
    result: PASS
    evidence: Workflow run 29693397745 completed successfully.
  - command: CI on head 5e9930815d317b91f4f688cc91f1b79888ed51f6
    result: PASS
    evidence: Workflow run 29693397828 completed successfully.
  - command: Agent Task Ownership on head 5e9930815d317b91f4f688cc91f1b79888ed51f6
    result: FAIL
    evidence: Workflow run 29693397731 rejected only the null first_failure checkpoint field; implementation/tool tests were already green.
  - command: Agent Task Ownership on head c332f5bd7cd66107f42fa563f71b79357bda1c3c
    result: PASS
    evidence: Workflow run 29693593019 completed successfully after correcting the checkpoint schema.
next_action: Require the canonical-exporter path integration tests to pass in existing AI Agent Tools/OTBM Map Tools, reconcile shared MODULE_CATALOG and CHANGELOG without overwriting concurrent PR #591 content, apply ci:final-gate, make one final checkpoint commit, freeze that exact head and require all final gates before squash merge.
```
