---
task_id: CAN-20260719-otbm-e2e-004-static-route-preflight
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-004
status: completed
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-004-static-route-preflight
base_branch: main
created: 2026-07-19
updated: 2026-07-19T16:26:36Z
last_verified_commit: "3d9f8590e1705b4d181471801dd79e8a844b81f1"
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
completed: 2026-07-19T16:26:36Z
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
head: 0dc6078f3e39fdc4d21208ba8955a009cdf55537
branch: feat/otbm-e2e-004-static-route-preflight
pr: 594
status: ready
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
  - live main at task start was a8ad5dcc0d1b5a2e399fc96d24d987fb633b7344
  - OTBM-E2E-001, OTBM-E2E-002, OTBM-E2E-003, OTBM-E2E-001B and E2E-ROUTE-001 were merged and lifecycle-archived before this package started
  - no open PR or branch matching OTBM-E2E-004 or static route preflight was found at task start
  - PR #594 owns feat/otbm-e2e-004-static-route-preflight
  - programme requires OTBM-E2E-004 before OTBM-E2E-005
  - implementation reuses export_route_plan_index_path so current exact-map verification reruns the existing Reachability classification and canonical _bfs rather than adding another pathfinder
  - implementation reuses the existing semantic landmark resolver and current route-interaction activation/script-status contracts
  - runtime map, World Index, appearances and every referenced optional evidence input are SHA-256 matched fail-closed before canonical regeneration
  - route-plan hash, executable status, path completeness, continuity, movement adjacency, diagonal policy, transition evidence and supported activation semantics are validated before physical execution
  - path integration tests prove preflight_index_paths calls export_route_plan_index_path with exact bounds/origin/destination/options and blocks a runtime-map versus World-Index-manifest mismatch before canonical export
  - no binary map/index/client asset, tools/e2e file or workflow is modified
  - plain optimistic reachability remains insufficient for physical executability
  - unresolved/conflicting Script Resolution evidence is not promoted to executable
  - main advanced with merged PR #591 to d4f8bb3aa3a6ca31b54f324797078360da28f8f8; the MODULE_CATALOG content on PR #594 preserves that merged player_balance row while adding the separate OTBM preflight row
  - PR #594 is mergeable against current main and no comment or review blocker exists
  - MODULE_CATALOG maintenance contract is satisfied in this PR; CHANGELOG remains unchanged because the reusable public contract is documented in its dedicated docs/schema and catalogue entry
  - ci:final-gate was applied to PR #594 before this final checkpoint commit
  - pre-final head 0dc6078f3e39fdc4d21208ba8955a009cdf55537 passed Agent Task Ownership, CI/Required, OTBM Map Tools and AI Agent Tools
  - AI Agent Tools and OTBM Map Tools discovered and passed both focused preflight test modules and the new result schema validation

derived:
  - exact canonical route regeneration is the narrowest way to re-check tile classification, diagonal corner constraints, transitions and interaction-aware executable policy without duplicating the existing parser, World Index, classifier or BFS
  - real Thais landmark binding and physical reference-route execution remain OTBM-E2E-005 scope
  - the stale merge-base visibly includes the already-merged #591 catalogue row in GitHub review diff, but current branch catalogue content equals current main for that row and PR #594 is mergeable; no #591 implementation path is owned or modified by this package
unknown:
  - exact-final-head final-gate results on the commit created by this checkpoint update
conflicts: []
rejected_hypotheses:
  - implementing another OTBM parser, World Index or pathfinder is forbidden and unnecessary
  - integrating thais.temple -> thais.depot in this task is rejected because OTBM-E2E-005 owns the real reference route
  - modifying tools/e2e or workflows is rejected because the static preflight composes existing OTBM evidence APIs without changing the physical runner
changed_paths:
  - docs/agents/MODULE_CATALOG.md
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
  - command: Agent Task Ownership on pre-final head 0dc6078f3e39fdc4d21208ba8955a009cdf55537
    result: PASS
    evidence: Workflow run 29694190963 completed successfully.
  - command: CI / Required on pre-final head 0dc6078f3e39fdc4d21208ba8955a009cdf55537
    result: PASS
    evidence: Workflow run 29694191105 completed successfully with Required green.
  - command: OTBM Map Tools on pre-final head 0dc6078f3e39fdc4d21208ba8955a009cdf55537
    result: PASS
    evidence: Workflow run 29694190977 completed successfully, including OTBM schema validation and focused OTBM tests.
  - command: AI Agent Tools on pre-final head 0dc6078f3e39fdc4d21208ba8955a009cdf55537
    result: PASS
    evidence: Workflow run 29694190967 completed successfully, including unit-test discovery and execution of the route-preflight suites.
next_action: Freeze the commit created by this final checkpoint update. Require exact-final-head Agent Task Ownership, AI Agent Tools, OTBM Map Tools and full ci:final-gate CI/Required to pass with no further commit; recheck live main overlap and review blockers, then squash merge PR #594 using the exact validated head SHA. After merge, complete the active-to-archive lifecycle before starting OTBM-E2E-005.
```

## Automated lifecycle completion

- Feature PR: #594.
- Feature head: `ed370974638a55dc4730f0adcc5fc6ec09f4ff9c`.
- Merge commit: `3d9f8590e1705b4d181471801dd79e8a844b81f1`.
- Merged at: `2026-07-19T16:26:36Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
