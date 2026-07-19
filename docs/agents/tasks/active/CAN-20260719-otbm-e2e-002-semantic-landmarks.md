---
task_id: CAN-20260719-otbm-e2e-002-semantic-landmarks
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-002
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-002-semantic-landmarks
base_branch: main
created: 2026-07-19T09:00:00+02:00
updated: 2026-07-19T09:38:12+02:00
last_verified_commit: "28dba1881aa217631d6caa8b64cf25757e4e462d"
risk: medium
related_issue: ""
related_pr: "571"
depends_on:
  - CAN-PROGRAM-OTBM-E2E-ROUTING merged planning programme PR #562
blocks:
  - OTBM-E2E-004
  - OTBM-E2E-005
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260719-otbm-e2e-002-semantic-landmarks.md
    - docs/ai-agent/OTBM_SEMANTIC_LANDMARKS.schema.json
    - docs/ai-agent/OTBM_SEMANTIC_LANDMARKS.json
    - tools/ai-agent/otbm_semantic_landmarks.py
    - tools/ai-agent/test_otbm_semantic_landmarks.py
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
    - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
  read_only:
    - docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md
    - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.md
    - docs/ai-agent/OTBM_WORLD_INDEX.md
    - tools/ai-agent/otbm_world_index.py
modules_touched:
  - OTBM Semantic Landmark Registry
reuses:
  - Unified OTBM World Index provenance contracts
  - exact x,y,z position model
  - OTBM-E2E route integration architecture
public_interfaces:
  - canary-otbm-semantic-landmarks-v1
cross_repo_tasks: []
---

# Goal

Implement `OTBM-E2E-002 — Semantic Landmark Registry` as a deterministic reviewed-name-to-exact-anchor contract for the OTBM-aware Universal Physical E2E routing programme. The registry must resolve semantic landmark IDs only from explicit reviewed entries, preserve exact map/index provenance, validate inclusive 3D routing regions and fail closed for stale or ambiguous evidence.

# Acceptance criteria

- [ ] Add versioned `canary-otbm-semantic-landmarks-v1` JSON Schema.
- [ ] Add a deterministic validator/resolver using Python standard library only.
- [ ] Validate unique region IDs, landmark IDs and per-landmark anchor IDs.
- [ ] Validate inclusive 3D routing bounds and require every anchor to lie inside its declared region.
- [ ] Support reviewed anchor roles including `route-origin`, `route-destination`, `entrance`, `exit`, and `interaction`.
- [ ] Require explicit map SHA-256 and World Index SHA-256 provenance and reject caller-supplied stale evidence.
- [ ] Resolve exact landmark/anchor IDs deterministically; never guess from names, sprites, minimap text or item metadata.
- [ ] Add a bounded reviewed registry file with schema-valid fixture/example entries only; do not invent claims for unverified real-map landmarks.
- [ ] Add focused tests for deterministic resolution, duplicate IDs, invalid bounds, out-of-bounds anchors, stale provenance and unknown landmark/anchor IDs.
- [ ] Update catalogue/changelog/program record for the delivered reusable interface.
- [ ] Apply `ci:final-gate` before final checkpoint commit.
- [ ] Verify exact-final-head required checks and review/merge blockers before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T09:38:12+02:00
head: 28dba1881aa217631d6caa8b64cf25757e4e462d
branch: feat/otbm-e2e-002-semantic-landmarks
pr: 571
status: implementing
context_routes:
  - agent-governance
  - otbm
owned_paths:
  - docs/agents/tasks/active/CAN-20260719-otbm-e2e-002-semantic-landmarks.md
  - docs/ai-agent/OTBM_SEMANTIC_LANDMARKS.schema.json
  - docs/ai-agent/OTBM_SEMANTIC_LANDMARKS.json
  - tools/ai-agent/otbm_semantic_landmarks.py
  - tools/ai-agent/test_otbm_semantic_landmarks.py
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
  - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
proven:
  - task branch was created from live main at f962d7b606e29965fe091ea79ba154c27b22fe34
  - draft PR 571 is the early same-repository PR for this task with base main and head feat/otbm-e2e-002-semantic-landmarks
  - OTBM-E2E-001 route-plan export merged as PR #567 before this task started
  - merged planning programme defines OTBM-E2E-002 as a separate landmark registry contract and permits it independently of E2E runner changes
  - no open PR matching OTBM-E2E-002 or semantic landmark registry ownership was found at task start
  - repository writes are restricted to blakinio/canary
  - no OTBM, WIDX, items.otb, client assets or generated route reports are in scope
  - real landmark coordinates must not be invented; initial registry content will remain explicitly non-authoritative example/fixture data unless exact map evidence is separately proven
unknown:
  - exact reusable validator patterns and World Index provenance field naming still need targeted source inspection
conflicts: []
blockers: []
first_failure: {}
rejected_hypotheses:
  - infer Thais landmark coordinates from memory or map labels
  - parse OTBM again inside the landmark registry
  - add semantic landmark resolution to the Universal E2E runner directly
changed_paths:
  - docs/agents/tasks/active/CAN-20260719-otbm-e2e-002-semantic-landmarks.md
validation:
  - command: live main, programme and open-PR ownership preflight
    result: PASS
    evidence: main f962d7b606e29965fe091ea79ba154c27b22fe34; PR #567 merged; no open OTBM-E2E-002 owner found
next_action: Inspect reusable validation/provenance patterns, then implement and test the smallest complete semantic-landmark contract without inventing real-map coordinates.
```
