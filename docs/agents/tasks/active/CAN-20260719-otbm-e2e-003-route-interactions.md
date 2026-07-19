---
task_id: CAN-20260719-otbm-e2e-003-route-interactions
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-003
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-003-route-interactions
base_branch: main
created: 2026-07-19T09:53:00+02:00
updated: 2026-07-19T09:55:00+02:00
last_verified_commit: "60b4051409a944c578c4609fdc13b2991f58f41d"
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

- [ ] Add versioned `canary-otbm-route-interactions-v1` JSON Schema and reviewed empty/unbound registry seed.
- [ ] Add a deterministic Python standard-library validator/resolver.
- [ ] Support activation kinds `step-on`, `walk-direction`, `use-map-item`, and `use-inventory-on-map`.
- [ ] Support narrow selectors by stable transition ID or exact position plus mechanic identifiers.
- [ ] Reject ambiguous/duplicate selectors that could apply conflicting physical behavior to the same mechanic.
- [ ] Integrate Script Resolution evidence conservatively: unresolved, partially-resolved, referenced-only and conflicting required handler evidence must not become executable.
- [ ] Allow engine-handled teleport evidence to resolve to `step-on` when explicitly selected by reviewed transition evidence.
- [ ] Allow reviewed ladder-style transitions to resolve to `use-map-item` only with explicit interaction evidence.
- [ ] Keep unknown doors/barriers blocked rather than assuming they are open or usable.
- [ ] Add focused deterministic tests for accepted activations, selector matching, stale/unsupported evidence and fail-closed script statuses.
- [ ] Update catalogue/changelog only for the delivered reusable interface.
- [ ] Apply `ci:final-gate` before final checkpoint commit.
- [ ] Verify exact-final-head required checks and review/merge blockers before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T09:55:00+02:00
head: 60b4051409a944c578c4609fdc13b2991f58f41d
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
  - draft PR 572 is the early same-repository PR for this task with base main and head feat/otbm-e2e-003-route-interactions
  - OTBM-E2E-001 route-plan export merged as PR #567 and publishes canary-otbm-e2e-route-plan-v1
  - PR #571 owns OTBM-E2E-002 semantic-landmark exclusive paths; this task does not overlap those exclusive paths
  - no open PR or repository task matching OTBM-E2E-003 was found at task start
  - programme requires a separate interaction registry and forbids treating optimistic reachability as physical executability
  - Script Resolution preserves unresolved, partially-resolved, referenced-only and conflicting states; unresolved does not mean handled
  - repository writes are restricted to blakinio/canary
  - no local Git checkout is available because the execution sandbox cannot resolve github.com; GitHub connector state is authoritative for repository writes and CI observation
  - no OTBM, WIDX, items.otb, client assets, generated route reports, Reachability pathfinder changes or tools/e2e changes are in scope
derived:
  - the v1 registry can be implemented independently of executable interaction-aware routing because OTBM-E2E-001B is a later consumer of the stable interaction contract
unknown:
  - exact final resolver data model and CLI shape remain to be implemented and validated in CI
conflicts: []
blockers: []
first_failure:
  marker: none
  evidence: no validation failure observed yet
rejected_hypotheses:
  - modify Reachability BFS or add a second pathfinder in this task
  - infer interaction semantics from sprite names, item names or optimistic walkability
  - treat unresolved or conflicting Script Resolution evidence as executable
  - add physical client execution under tools/e2e in this task
changed_paths:
  - docs/agents/tasks/active/CAN-20260719-otbm-e2e-003-route-interactions.md
validation:
  - command: live main, programme, route-plan contract and open-PR ownership preflight
    result: PASS
    evidence: main f962d7b606e29965fe091ea79ba154c27b22fe34; PR #567 merged; PR #571 owns only semantic-landmark exclusive paths; no OTBM-E2E-003 owner found
next_action: Implement the versioned registry schema, deterministic resolver, Script Resolution gating rules and focused tests without changing Reachability or tools/e2e.
```
