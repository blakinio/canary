---
task_id: CAN-20260719-otbm-e2e-003-route-interactions
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-003
status: validating
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-003-route-interactions
base_branch: main
created: 2026-07-19T09:53:00+02:00
updated: 2026-07-19T10:20:00+02:00
last_verified_commit: "6f6a98e992079dd127bea442492c71216e2fb7de"
risk: medium
related_issue: ""
related_pr: "572"
depends_on:
  - CAN-PROGRAM-OTBM-E2E-ROUTING merged planning programme PR #562
  - OTBM-E2E-001 route-plan contract merged as PR #567
blocks:
  - OTBM-E2E-001B
  - E2E-ROUTE-001 full interaction support
  - OTBM-E2E-004
  - OTBM-E2E-005
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260719-otbm-e2e-003-route-interactions.md
    - docs/ai-agent/OTBM_ROUTE_INTERACTIONS.schema.json
    - docs/ai-agent/OTBM_ROUTE_INTERACTIONS.json
    - docs/ai-agent/OTBM_ROUTE_INTERACTIONS.md
    - tools/ai-agent/otbm_route_interactions.py
    - tools/ai-agent/test_otbm_route_interactions.py
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
    - docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md
    - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.md
    - docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md
    - docs/ai-agent/OTBM_SCRIPT_RESOLUTION_REPORT.schema.json
    - docs/ai-agent/OTBM_TRANSITIONS.schema.json
    - tools/ai-agent/otbm_reachability*.py
    - tools/e2e/**
modules_touched:
  - OTBM Route Interaction Registry
reuses:
  - canary-otbm-e2e-route-plan-v1 transition IDs and exact edge evidence
  - canary-otbm-script-resolution-v1 placement/runtime statuses
  - existing OTBM transition vocabulary
public_interfaces:
  - canary-otbm-route-interactions-v1
cross_repo_tasks: []
---

# Goal

Implement `OTBM-E2E-003 — Route interaction semantics` as a deterministic reviewed registry that maps exact OTBM mechanic/transition evidence to supported physical activation semantics without changing Reachability or Universal E2E execution.

# Acceptance criteria

- [x] Add versioned `canary-otbm-route-interactions-v1` JSON Schema and reviewed empty/unbound registry seed.
- [x] Add a deterministic Python standard-library validator/resolver.
- [x] Support activation kinds `step-on`, `walk-direction`, `use-map-item`, and `use-inventory-on-map`.
- [x] Support narrow selectors by stable transition ID or exact position plus mechanic identifiers.
- [x] Reject ambiguous/duplicate selectors that could apply conflicting physical behavior to the same mechanic.
- [x] Integrate Script Resolution evidence conservatively: unresolved, partially-resolved, referenced-only and conflicting required handler evidence must not become executable.
- [x] Allow engine-handled teleport evidence to resolve to `step-on` when explicitly selected by reviewed transition evidence.
- [x] Allow reviewed ladder-style transitions to resolve to `use-map-item` only with explicit interaction evidence.
- [x] Keep unknown doors/barriers blocked rather than assuming they are open or usable.
- [x] Add focused deterministic tests for accepted activations, selector matching, stale/unsupported evidence and fail-closed script statuses.
- [x] Update catalogue/changelog only for the delivered reusable interface.
- [x] Apply `ci:final-gate` before final checkpoint commit.
- [ ] Verify exact-final-head required checks and review/merge blockers before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T10:20:00+02:00
head: 6f6a98e992079dd127bea442492c71216e2fb7de
branch: feat/otbm-e2e-003-route-interactions
pr: 572
status: validating
context_routes:
  - agent-governance
  - otbm
owned_paths:
  - docs/agents/tasks/active/CAN-20260719-otbm-e2e-003-route-interactions.md
  - docs/ai-agent/OTBM_ROUTE_INTERACTIONS.schema.json
  - docs/ai-agent/OTBM_ROUTE_INTERACTIONS.json
  - docs/ai-agent/OTBM_ROUTE_INTERACTIONS.md
  - tools/ai-agent/otbm_route_interactions.py
  - tools/ai-agent/test_otbm_route_interactions.py
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - task branch was created from live main at f962d7b606e29965fe091ea79ba154c27b22fe34
  - draft PR 572 is the early same-repository PR for this task with base main and head feat/otbm-e2e-003-route-interactions
  - OTBM-E2E-001 route-plan export merged as PR #567 and publishes canary-otbm-e2e-route-plan-v1
  - PR #570 remains the separate open automated lifecycle cleanup for merged PR #567; this task does not manually archive that task
  - PR #571 remains the separate draft owner of OTBM-E2E-002 semantic-landmark exclusive paths; this task does not overlap those exclusive paths
  - live main remains f962d7b606e29965fe091ea79ba154c27b22fe34 through this checkpoint
  - no open PR or repository task matching OTBM-E2E-003 was found at task start
  - programme requires a separate interaction registry and forbids treating optimistic reachability as physical executability
  - Script Resolution preserves unresolved, partially-resolved, referenced-only and conflicting states; unresolved does not mean handled
  - canary-otbm-route-interactions-v1 schema and an empty unbound seed are implemented
  - deterministic standard-library resolver supports step-on, walk-direction, use-map-item and use-inventory-on-map activation contracts
  - selectors are bounded to stable transition IDs or exact positions plus itemId/actionId/uniqueId/houseDoorId evidence
  - exact duplicate selectors are rejected and overlapping matching selectors fail closed as ambiguous
  - handler-gated entries accept only explicit handled Script Resolution statuses; partially-resolved, referenced-only, unresolved and conflicting cannot be whitelisted and remain blocked
  - reviewed transition-manifest and Script Resolution evidence can be SHA-256 pinned and exact caller expectations fail closed on stale evidence
  - engine teleport step-on and reviewed ladder use-map-item semantics are covered without modifying Reachability or Universal E2E
  - unknown doors and barriers resolve to interaction-not-reviewed rather than assumed usable
  - MODULE_CATALOG.md PR patch is limited to Last reviewed 2026-07-19 plus one OTBM Route Interaction Registry row
  - CHANGELOG.md PR patch is limited to one Unreleased bullet for canary-otbm-route-interactions-v1
  - changed-file inventory contains exactly the task record, three route-interaction docs/contracts, resolver, focused tests, MODULE_CATALOG.md and CHANGELOG.md
  - AI Agent Tools run 29679036887 passed including Run unit tests on implementation head e15bdc8ad9ad14fb448bcfeaf4b90f43be193832
  - CI run 29679429456, Agent Task Ownership run 29679429392 and OTBM Map Tools run 29679429347 passed on documentation-complete head 6f6a98e992079dd127bea442492c71216e2fb7de
  - OTBM Map Tools run 29679429347 passed Validate OTBM schema JSON and Run focused OTBM tests
  - ci:final-gate label was applied to PR 572 before this final checkpoint commit
  - repository writes are restricted to blakinio/canary
  - no local Git checkout is available because the execution sandbox cannot resolve github.com; GitHub connector state is authoritative for repository writes and CI observation
  - no OTBM, WIDX, items.otb, client assets, generated route reports, Reachability pathfinder changes or tools/e2e changes are in scope
derived:
  - the v1 registry can be implemented independently of executable interaction-aware routing because OTBM-E2E-001B is a later consumer of the stable interaction contract
  - a successful interaction resolution is static evidence only and does not prove runtime gameplay state
unknown:
  - exact final checkpoint commit SHA and its final-gate workflow results are pending after this commit
conflicts: []
blockers: []
first_failure:
  marker: docs/agents/MODULE_CATALOG.md temporary tail truncation during connector-only full-file replacement
  evidence: repaired immediately; final PR patch proves only the intended review-date change and one registry row remain
rejected_hypotheses:
  - modify Reachability BFS or add a second pathfinder in this task
  - infer interaction semantics from sprite names, item names or optimistic walkability
  - treat unresolved or conflicting Script Resolution evidence as executable
  - add physical client execution under tools/e2e in this task
changed_paths:
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260719-otbm-e2e-003-route-interactions.md
  - docs/ai-agent/OTBM_ROUTE_INTERACTIONS.json
  - docs/ai-agent/OTBM_ROUTE_INTERACTIONS.md
  - docs/ai-agent/OTBM_ROUTE_INTERACTIONS.schema.json
  - tools/ai-agent/otbm_route_interactions.py
  - tools/ai-agent/test_otbm_route_interactions.py
validation:
  - command: live main, programme, route-plan contract and open-PR ownership preflight
    result: PASS
    evidence: main f962d7b606e29965fe091ea79ba154c27b22fe34; PR #567 merged; PR #571 owns only semantic-landmark exclusive paths; no OTBM-E2E-003 owner found
  - command: AI Agent Tools workflow on e15bdc8ad9ad14fb448bcfeaf4b90f43be193832
    result: PASS
    evidence: run 29679036887 completed successfully; Run unit tests and all generation/validation steps passed
  - command: MODULE_CATALOG.md changed-file patch review
    result: PASS
    evidence: only Last reviewed date and one OTBM Route Interaction Registry row differ from main
  - command: CHANGELOG.md changed-file patch review
    result: PASS
    evidence: only one canary-otbm-route-interactions-v1 Unreleased bullet differs from main
  - command: CI workflow on 6f6a98e992079dd127bea442492c71216e2fb7de
    result: PASS
    evidence: run 29679429456 completed successfully
  - command: Agent Task Ownership workflow on 6f6a98e992079dd127bea442492c71216e2fb7de
    result: PASS
    evidence: run 29679429392 completed successfully
  - command: OTBM Map Tools workflow on 6f6a98e992079dd127bea442492c71216e2fb7de
    result: PASS
    evidence: run 29679429347 completed successfully including schema JSON validation and focused OTBM tests
  - command: ci:final-gate label application
    result: PASS
    evidence: label applied to PR 572 before final checkpoint commit
next_action: Treat this commit as the final feature-head mutation. Verify all ci:final-gate workflows on its exact SHA, then verify review threads, approvals, mergeability and branch protection before squash merge. Do not add another commit after a green final gate.
```
