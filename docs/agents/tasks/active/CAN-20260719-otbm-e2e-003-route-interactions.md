---
task_id: CAN-20260719-otbm-e2e-003-route-interactions
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-003
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-003-route-interactions
base_branch: main
created: 2026-07-19T09:53:00+02:00
updated: 2026-07-19T10:50:00+02:00
last_verified_commit: "9a5be3ebceae45a81d6502d28d0faa36d096e306"
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
updated_at: 2026-07-19T10:50:00+02:00
head: 9a5be3ebceae45a81d6502d28d0faa36d096e306
branch: feat/otbm-e2e-003-route-interactions
pr: 572
status: implementing
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
  - PR 572 is the same-repository PR for this task with base main and head feat/otbm-e2e-003-route-interactions
  - OTBM-E2E-001 route-plan export merged as PR #567 and publishes canary-otbm-e2e-route-plan-v1
  - PR #570 remains the separate lifecycle cleanup path for merged PR #567; this task does not manually archive that task
  - OTBM-E2E-002 merged independently as PR #571 with main merge commit da36fedefdf7071ad3def46e497140418c9b2f84
  - after PR #571 advanced main and made PR #572 non-mergeable, merge commit e8b73f45212594c36aa5f55d273656bd407ee0f0 synchronized this branch with main while preserving the six exclusive OTBM-E2E-003 files by exact blob identity
  - PR #572 is mergeable again against base da36fedefdf7071ad3def46e497140418c9b2f84
  - MODULE_CATALOG.md patch against current main contains exactly one added OTBM Route Interaction Registry row and preserves the merged Semantic Landmark Registry row
  - CHANGELOG.md patch against current main contains exactly one added canary-otbm-route-interactions-v1 Unreleased bullet and preserves the semantic-landmarks entry
  - changed-file inventory contains exactly eight files: the task record, three route-interaction docs/contracts, resolver, focused tests, MODULE_CATALOG.md and CHANGELOG.md
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
  - pre-sync implementation validation passed AI Agent Tools, CI, Agent Task Ownership and OTBM Map Tools on exact historical heads
  - pre-sync ci:final-gate on fa6d6a22e0a08c92128d6ad29dfba37ea7629449 passed AI Agent Tools, Agent Task Ownership, OTBM Map Tools and initial CI, but was superseded when PR #571 advanced main before branch protection completed the ready-for-review full CI matrix
  - ci:final-gate label remains applied to PR #572 for the post-sync exact-head validation
  - repository writes are restricted to blakinio/canary
  - no local Git checkout is available because the execution sandbox cannot resolve github.com; GitHub connector state is authoritative for repository writes and CI observation
  - no OTBM, WIDX, items.otb, client assets, generated route reports, Reachability pathfinder changes or tools/e2e changes are in scope
derived:
  - the v1 registry can be implemented independently of executable interaction-aware routing because OTBM-E2E-001B is a later consumer of the stable interaction contract
  - a successful interaction resolution is static evidence only and does not prove runtime gameplay state
unknown:
  - exact final checkpoint commit SHA and its post-sync final-gate workflow results are pending after this commit
conflicts: []
blockers: []
first_failure:
  marker: Agent Task Ownership rejected task status validating on historical final checkpoint 362889ec7707b65909d04c5201ca49327394285a
  evidence: corrected to implementing; exact subsequent head fa6d6a22e0a08c92128d6ad29dfba37ea7629449 passed changed-active-task checkpoint validation
rejected_hypotheses:
  - modify Reachability BFS or add a second pathfinder in this task
  - infer interaction semantics from sprite names, item names or optimistic walkability
  - treat unresolved or conflicting Script Resolution evidence as executable
  - add physical client execution under tools/e2e in this task
  - overwrite or drop OTBM-E2E-002 shared documentation while synchronizing main
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
  - command: initial live main, programme, route-plan contract and open-PR ownership preflight
    result: PASS
    evidence: PR #567 merged; OTBM-E2E-003 had no live owner at task start; OTBM-E2E-002 was owned independently
  - command: pre-sync AI Agent Tools, CI, Agent Task Ownership and OTBM Map Tools workflows
    result: PASS
    evidence: implementation and documentation heads passed focused tests, schema validation, ownership and repository CI before main advanced
  - command: synchronize PR #572 with main after PR #571 merge
    result: PASS
    evidence: merge commit e8b73f45212594c36aa5f55d273656bd407ee0f0 has feature head fa6d6a22e0a08c92128d6ad29dfba37ea7629449 and main da36fedefdf7071ad3def46e497140418c9b2f84 as parents; PR is mergeable again
  - command: MODULE_CATALOG.md changed-file patch review against current main
    result: PASS
    evidence: exactly one OTBM Route Interaction Registry row is added; no existing line changes remain
  - command: CHANGELOG.md changed-file patch review against current main
    result: PASS
    evidence: exactly one canary-otbm-route-interactions-v1 Unreleased bullet is added
  - command: ci:final-gate label
    result: PASS
    evidence: label remains applied to PR #572; post-sync exact-head workflows must complete before merge
next_action: Treat the commit created by this checkpoint update as the final feature-head mutation. Verify all ci:final-gate workflows and the branch-protection Required check on its exact SHA, then verify review threads, approvals and mergeability before squash merge. Do not add another commit after a green final gate.
```
