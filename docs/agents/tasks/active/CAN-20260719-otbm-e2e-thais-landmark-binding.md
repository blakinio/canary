---
task_id: CAN-20260719-otbm-e2e-thais-landmark-binding
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-005-LANDMARKS
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-thais-landmark-binding
base_branch: main
created: 2026-07-19T21:05:00+02:00
updated: 2026-07-19T21:06:00+02:00
last_verified_commit: "59bdf3221ec4b5325d9b5f9961cf3d20a69cbbe8"
risk: medium
related_issue: ""
related_pr: "599"
depends_on:
  - merged PR #571 semantic landmark registry contract
  - merged PR #594 exact-map static route preflight
  - merged Unified OTBM World Index and Reachability stack
blocks:
  - OTBM-E2E-005 reference physical route thais.temple -> thais.depot
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260719-otbm-e2e-thais-landmark-binding.md
    - docs/ai-agent/OTBM_SEMANTIC_LANDMARKS.json
    - docs/ai-agent/OTBM_THAIS_LANDMARK_EVIDENCE.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
    - docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md
    - docs/ai-agent/OTBM_SEMANTIC_LANDMARKS.schema.json
    - tools/ai-agent/otbm_semantic_landmarks.py
    - tools/ai-agent/otbm_item_audit_scan.cpp
    - tools/ai-agent/otbm_world_index.py
    - tools/ai-agent/otbm_world_index_tool.py
    - tools/ai-agent/otbm_reachability.py
    - tools/ai-agent/otbm_reachability_types.py
    - tools/e2e/**
    - tests/e2e/**
    - .github/workflows/**
modules_touched:
  - OTBM Semantic Landmark Registry
reuses:
  - Unified OTBM World Index
  - OTBM Reachability strict walkability and route planning
  - canary-otbm-semantic-landmarks-v1 validator/resolver
  - exact-map static route preflight
public_interfaces:
  - reviewed thais.temple and thais.depot entries in canary-otbm-semantic-landmarks-v1
cross_repo_tasks: []
---

# Goal

Bind the existing semantic landmark registry to evidence-reviewed `thais.temple` and `thais.depot` anchors for the exact user-supplied Canary/OTServBR map snapshot, without starting the physical OTBM-E2E-005 scenario itself.

This is a bounded evidence prerequisite. It must turn the currently `unbound` registry into a `reviewed` registry only after the exact source-map and canonical World Index SHA-256 values are known and both route anchors are proven from the exact map. The depot destination must be a strict-walkable route destination near an exact reviewed Thais depot locker; the locker tile itself must not be assumed walkable.

# Acceptance criteria

- [ ] Reconfirm the source map is exactly SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2` and size `184776037` bytes.
- [ ] Build/reuse the canonical deterministic `OTSWIDX1` World Index from that exact map using the existing native scanner; do not create another parser or scanner.
- [ ] Record the exact generated World Index SHA-256 and keep `.widx`, map and client assets outside Git.
- [ ] Preserve exact town-metadata evidence that town `Thais` has id `8` and temple position `[32369,32241,7]` on the selected map.
- [ ] Preserve exact-map evidence for the four nearby `ATTR_DEPOT_ID=8` depot lockers at `[32352,32225,7]`, `[32354,32225,7]`, `[32352,32231,7]`, and `[32354,32231,7]`.
- [ ] Correlate `ATTR_DEPOT_ID` with current Canary `DepotLocker` runtime semantics without treating an unresolved script as handled.
- [ ] Select `thais.depot` only from an exact strict-walkable route-destination tile reviewed against existing World Index/appearance/Reachability evidence adjacent to a confirmed depot locker; do not guess an adjacent coordinate.
- [ ] Define one bounded common routing region containing the selected temple and depot anchors without exceeding the existing Reachability coordinate bound.
- [ ] Update `OTBM_SEMANTIC_LANDMARKS.json` to `registryStatus=reviewed` with exact source-map and World Index SHA-256 provenance, evidence-reviewed anchors and deterministic IDs.
- [ ] Validate the updated registry with the existing `otbm_semantic_landmarks.py` contract and exact expected provenance.
- [ ] Do not edit route planning, preflight, Universal E2E, workflow, OTClient, runtime map, OTBM, `.widx`, `items.otb` or client assets.
- [ ] Keep the actual OTBM-E2E-005 physical scenario out of this PR; it remains the downstream consumer after this binding merges.
- [ ] Update the module catalogue/changelog narrowly for the reviewed registry binding.
- [ ] Apply `ci:final-gate` before the final checkpoint commit and make no post-final-head commits.
- [ ] Require exact-final-head Ownership, CI and applicable OTBM validation checks plus a clean review blocker audit before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T21:06:00+02:00
head: 59bdf3221ec4b5325d9b5f9961cf3d20a69cbbe8
branch: feat/otbm-e2e-thais-landmark-binding
pr: 599
status: implementing
context_routes:
  - agent-governance
  - otbm
owned_paths:
  - docs/agents/tasks/active/CAN-20260719-otbm-e2e-thais-landmark-binding.md
  - docs/ai-agent/OTBM_SEMANTIC_LANDMARKS.json
  - docs/ai-agent/OTBM_THAIS_LANDMARK_EVIDENCE.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - live main at task start is c353b89b5a7f783cf4ee22fe1ba91850de837a68
  - draft PR 599 owns branch feat/otbm-e2e-thais-landmark-binding
  - no open PR matched OTBM-E2E-005, semantic landmark or Thais ownership at task start
  - PR #571 semantic landmark registry, PR #589 follow_route and PR #594 exact-map route preflight are merged
  - committed semantic landmark registry is intentionally unbound and empty before this task
  - exact local map SHA-256 is a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2 and its size is 184776037 bytes
  - exact-map OTBM town metadata resolves Thais id 8 temple position to 32369,32241,7
  - existing repository OTBM scanning found depotId 8 lockers at 32352,32225,7; 32354,32225,7; 32352,32231,7; and 32354,32231,7
  - current Canary DepotLocker reads ATTR_DEPOT_ID as uint16 and use-item handling opens player->getDepotLocker(depot->getDepotId()) while recording the same lastDepotId
blockers:
  - exact canonical World Index SHA-256 for the selected map has not yet been regenerated or recovered in this session
  - no strict-walkable thais.depot route-destination anchor has yet been proven with the existing Reachability/appearance evidence
failed_approaches:
  - interpreted-Python bounded full-map scanning was too slow for the 184776037-byte map; do not replace the canonical native World Index scanner with a new parser
  - client minimap package inspection is only auxiliary visual evidence and cannot establish strict walkability or executable route anchors
next_actions:
  - obtain the exact canonical World Index for the pinned map with the merged native scanner and record its SHA-256
  - query/review the depot locker neighborhood with the existing World Index and Reachability inputs to select a strict-walkable destination anchor
  - write the small durable landmark evidence document, bind the registry and validate exact provenance
validation:
  ownership: pending
  registry: pending
  world_index: pending
  reachability: pending
  ci: pending
```
