---
task_id: CAN-20260719-otbm-e2e-thais-landmark-binding
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-005-LANDMARKS
status: validating
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-thais-landmark-binding
base_branch: main
created: 2026-07-19T21:05:00+02:00
updated: 2026-07-19T22:00:00+02:00
last_verified_commit: "865644d3755af9949b3d54062ea5aca44dcae0b3"
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
    - tools/ai-agent/test_otbm_semantic_landmarks.py
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

- [x] Reconfirm the source map is exactly SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2` and size `184776037` bytes.
- [x] Build/reuse the canonical deterministic `OTSWIDX1` World Index from that exact map using the existing native scanner; do not create another parser or scanner.
- [x] Record the exact generated World Index SHA-256 and keep `.widx`, map and client assets outside Git.
- [x] Preserve exact town-metadata evidence that town `Thais` has id `8` and temple position `[32369,32241,7]` on the selected map.
- [x] Preserve exact-map evidence for the four nearby `ATTR_DEPOT_ID=8` depot lockers at `[32352,32225,7]`, `[32354,32225,7]`, `[32352,32231,7]`, and `[32354,32231,7]`.
- [x] Correlate `ATTR_DEPOT_ID` with current Canary `DepotLocker` runtime semantics without treating an unresolved script as handled.
- [x] Select `thais.depot` only from an exact strict-walkable route-destination tile reviewed against existing World Index/appearance/Reachability evidence adjacent to a confirmed depot locker; do not guess an adjacent coordinate.
- [x] Define one bounded common routing region containing the selected temple and depot anchors without exceeding the existing Reachability coordinate bound.
- [x] Update `OTBM_SEMANTIC_LANDMARKS.json` to `registryStatus=reviewed` with exact source-map and World Index SHA-256 provenance, evidence-reviewed anchors and deterministic IDs.
- [x] Validate the updated registry with the existing `otbm_semantic_landmarks.py` contract and exact expected provenance.
- [x] Update the committed-registry regression test from the superseded unbound-seed expectation to exact reviewed Thais provenance and anchor resolution.
- [x] Do not edit route planning, preflight, Universal E2E, workflow, OTClient, runtime map, OTBM, `.widx`, `items.otb` or client assets.
- [x] Keep the actual OTBM-E2E-005 physical scenario out of this PR; it remains the downstream consumer after this binding merges.
- [x] Update the module catalogue/changelog narrowly for the reviewed registry binding.
- [x] Apply/reuse `ci:final-gate` before the replacement final checkpoint commit and make no post-final-head commits.
- [ ] Require exact-final-head Ownership, CI and applicable OTBM validation checks plus a clean review blocker audit before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T22:00:00+02:00
head: 865644d3755af9949b3d54062ea5aca44dcae0b3
branch: feat/otbm-e2e-thais-landmark-binding
pr: 599
status: validating
context_routes:
  - agent-governance
  - otbm
owned_paths:
  - docs/agents/tasks/active/CAN-20260719-otbm-e2e-thais-landmark-binding.md
  - docs/ai-agent/OTBM_SEMANTIC_LANDMARKS.json
  - docs/ai-agent/OTBM_THAIS_LANDMARK_EVIDENCE.md
  - tools/ai-agent/test_otbm_semantic_landmarks.py
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - live main at task start is c353b89b5a7f783cf4ee22fe1ba91850de837a68
  - PR 599 owns branch feat/otbm-e2e-thais-landmark-binding and is ready for review
  - no open PR matched OTBM-E2E-005, semantic landmark or Thais ownership at task start
  - PR #571 semantic landmark registry, PR #589 follow_route and PR #594 exact-map route preflight are merged
  - exact local map SHA-256 is a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2 and its size is 184776037 bytes
  - current and historical official native scanner artifacts both rebuild byte-identical canonical World Index SHA-256 6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a with size 842280592 bytes
  - exact-map OTBM town metadata resolves Thais id 8 temple position to 32369,32241,7
  - existing repository OTBM scanning found depotId 8 lockers at 32352,32225,7; 32354,32225,7; 32352,32231,7; and 32354,32231,7
  - current Canary DepotLocker reads ATTR_DEPOT_ID as uint16 and use-item handling opens player->getDepotLocker(depot->getDepotId()) while recording the same lastDepotId
  - all 14 unique orthogonal locker-neighbor candidates were evaluated with current Reachability against the exact World Index and appearances evidence
  - deterministic minimum-strict-distance then lexicographic tie-break selects thais.depot route destination 32352,32226,7 adjacent to reviewed locker 32352,32225,7
  - final bounded region 32347,32216,7 through 32369,32241,7 contains 598 coordinates and produces confirmed strict/optimistic distance 66 with zero error findings, no path truncation and no transition IDs used
  - semantic landmark registry is reviewed with exact source-map/index provenance and resolves the temple/depot anchors inside the bounded region under the existing validator contract
  - first frozen head ff9502ac87719767e45fa8850fb41ce1050a338a failed AI Agent Tools because the committed-registry unit test still asserted the superseded unbound seed state
  - the regression test now validates exact committed map/index provenance plus deterministic Thais route-origin and route-destination resolution
  - ci:final-gate remains applied before this replacement final checkpoint commit
blockers:
  - exact-final-head Ownership, CI, OTBM Map Tools and AI Agent Tools are pending
  - final review blocker audit and expected-head squash merge remain pending
failed_approaches:
  - interpreted-Python bounded full-map scanning was too slow for the 184776037-byte map; the canonical native World Index scanner was reused instead of creating another parser
  - client minimap package inspection is only auxiliary visual evidence and was not used to establish strict walkability or executable route anchors
  - first final head ff9502ac87719767e45fa8850fb41ce1050a338a failed AI Agent Tools because the old committed-seed unit test was not updated with the registry state transition
next_actions:
  - make no commits after this replacement final checkpoint
  - require exact-final-head checks and confirm autofix does not mutate the frozen head
  - require clean review blocker audit and unchanged expected head before squash merge
validation:
  ownership: pending
  registry: passed
  world_index: passed
  reachability: passed
  ai_agent_tools: pending
  ci: pending
```
