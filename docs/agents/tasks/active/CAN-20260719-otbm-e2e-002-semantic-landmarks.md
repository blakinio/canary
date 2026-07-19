---
task_id: CAN-20260719-otbm-e2e-002-semantic-landmarks
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-002
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-002-semantic-landmarks
base_branch: main
created: 2026-07-19T09:00:00+02:00
updated: 2026-07-19T10:12:00+02:00
last_verified_commit: "cd3ffac5f715f4d17a5d0affc8fb66e3d42b7dd1"
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
  read_only:
    - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
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
  - existing Reachability MAX_REGION_COORDINATES bound
public_interfaces:
  - canary-otbm-semantic-landmarks-v1
cross_repo_tasks: []
---

# Goal

Implement `OTBM-E2E-002 — Semantic Landmark Registry` as a deterministic reviewed-name-to-exact-anchor contract for the OTBM-aware Universal Physical E2E routing programme. The registry must resolve semantic landmark IDs only from explicit reviewed entries, preserve exact map/index provenance, validate inclusive 3D routing regions and fail closed for stale or ambiguous evidence.

# Acceptance criteria

- [x] Add versioned `canary-otbm-semantic-landmarks-v1` JSON Schema.
- [x] Add a deterministic validator/resolver using Python standard library only.
- [x] Validate unique region IDs, landmark IDs and per-landmark anchor IDs.
- [x] Validate inclusive 3D routing bounds and require every anchor to lie inside its declared region.
- [x] Enforce the existing Reachability `MAX_REGION_COORDINATES` bound for every reviewed routing region.
- [x] Support reviewed anchor roles including `route-origin`, `route-destination`, `entrance`, `exit`, and `interaction`.
- [x] Require explicit map SHA-256 and World Index SHA-256 provenance and reject caller-supplied stale evidence.
- [x] Resolve exact landmark/anchor IDs deterministically; never guess from names, sprites, minimap text or item metadata.
- [x] Add a bounded fail-closed unbound registry seed; do not invent claims for unverified real-map landmarks.
- [x] Add focused tests for deterministic resolution, duplicate IDs, invalid bounds, Reachability region bounds, out-of-bounds anchors, stale provenance and unknown landmark/anchor IDs.
- [x] Update catalogue/changelog for the delivered reusable interface.
- [x] Apply `ci:final-gate` before final checkpoint commit.
- [ ] Verify exact-final-head required checks and review/merge blockers before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T10:12:00+02:00
head: cd3ffac5f715f4d17a5d0affc8fb66e3d42b7dd1
branch: feat/otbm-e2e-002-semantic-landmarks
pr: 571
status: validating
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
proven:
  - task branch was created from live main at f962d7b606e29965fe091ea79ba154c27b22fe34
  - draft PR 571 is the early same-repository PR for this task with base main and head feat/otbm-e2e-002-semantic-landmarks
  - OTBM-E2E-001 route-plan export merged as PR #567 before this task started
  - merged planning programme defines OTBM-E2E-002 as a separate landmark registry contract and permits it independently of E2E runner changes
  - no open PR matching OTBM-E2E-002 or semantic landmark registry ownership was found at task start
  - World Index manifest provenance uses source.sha256 for the exact OTBM map and index.sha256 for the exact WIDX artifact
  - AI Agent Tools discovers every tools/ai-agent/test_*.py file through Python unittest discovery
  - registry implementation uses no third-party dependency, does not parse OTBM and does not add a pathfinder
  - committed registry seed is unbound with provenance null and no regions or landmarks, so no real-map coordinates are invented
  - reviewed registries require exact source-map and World Index SHA-256 values before resolution
  - review against OTBM_E2E_ROUTE_INTEGRATION found that semantic routing regions must respect the existing Reachability coordinate-volume bound
  - semantic landmark validation now reuses MAX_REGION_COORDINATES from otbm_reachability_types and rejects reviewed regions above 1000000 inclusive coordinates
  - focused regression proves exactly 1000000 region coordinates are accepted and 1001000 are rejected fail-closed
  - CI run 29679368864, Agent Task Ownership run 29679368761, OTBM Map Tools run 29679368824 and AI Agent Tools run 29679368747 passed on implementation head cd3ffac5f715f4d17a5d0affc8fb66e3d42b7dd1
  - MODULE_CATALOG diff contains only review-date update, merged status for PR 567 and the reusable semantic-landmark row
  - CHANGELOG diff contains exactly one semantic-landmark behavior entry
  - ci:final-gate label is present on PR 571 before this checkpoint commit
  - repository writes are restricted to blakinio/canary
  - changed-file list contains only the seven declared task/shared paths and no OTBM, WIDX, items.otb, client assets, tools/e2e paths or generated route reports
derived:
  - OTBM-E2E-002 can merge independently of route interaction semantics because it only defines reviewed route anchors and regions, while execution remains blocked on later packages
  - importing the existing Reachability bound avoids a duplicated numeric routing limit drifting between the landmark and Reachability contracts
unknown:
  - exact final-head workflow conclusions are pending after this checkpoint commit
conflicts: []
blockers: []
first_failure:
  marker: agent-task-ownership-checkpoint-schema
  evidence: runs 29678546429 and 29678595943 failed only changed-task checkpoint validation; first an empty first_failure mapping was invalid, then the required derived field was missing; implementation unit tests were green
rejected_hypotheses:
  - infer Thais landmark coordinates from memory or map labels
  - parse OTBM again inside the landmark registry
  - add semantic landmark resolution to the Universal E2E runner directly
  - allow semantic routing regions larger than the existing Reachability MAX_REGION_COORDINATES bound
changed_paths:
  - docs/agents/tasks/active/CAN-20260719-otbm-e2e-002-semantic-landmarks.md
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/ai-agent/OTBM_SEMANTIC_LANDMARKS.schema.json
  - docs/ai-agent/OTBM_SEMANTIC_LANDMARKS.json
  - tools/ai-agent/otbm_semantic_landmarks.py
  - tools/ai-agent/test_otbm_semantic_landmarks.py
validation:
  - command: live main, programme and open-PR ownership preflight
    result: PASS
    evidence: main f962d7b606e29965fe091ea79ba154c27b22fe34; PR 567 merged; no open OTBM-E2E-002 owner found at task start
  - command: AI Agent Tools run 29678546469 on ec7eb905b1f22e1c253fbe6ca8592376d27fc375
    result: PASS
    evidence: unittest discovery including test_otbm_semantic_landmarks.py and all downstream AI-agent validation steps completed successfully
  - command: CI, OTBM Map Tools and AI Agent Tools on bdc6bcb20b4a246b783fe48153a452b1b1f43d50
    result: PASS
    evidence: CI run 29678596022, OTBM Map Tools run 29678595946 and AI Agent Tools run 29678595934 completed successfully
  - command: Agent Task Ownership run 29678889674 on 740832cfc41849b412a24ed2fe27ddcf56a3f7e7
    result: PASS
    evidence: repaired checkpoint schema validated successfully
  - command: PR 571 shared-document patch review
    result: PASS
    evidence: MODULE_CATALOG has only intended status/catalogue edits and CHANGELOG has one intended new bullet
  - command: contract review against OTBM_E2E_ROUTE_INTEGRATION region rules and otbm_reachability_types.MAX_REGION_COORDINATES
    result: PASS
    evidence: implementation now imports the existing 1000000-coordinate Reachability bound and fails closed above it
  - command: CI, Agent Task Ownership, OTBM Map Tools and AI Agent Tools on cd3ffac5f715f4d17a5d0affc8fb66e3d42b7dd1
    result: PASS
    evidence: runs 29679368864, 29679368761, 29679368824 and 29679368747 completed successfully; focused OTBM and full AI-agent unit discovery include the new region-bound regression
next_action: Verify every required workflow on the exact checkpoint head; if all are successful and PR 571 is mergeable with no unresolved review blocker, mark ready and squash-merge without any post-green commit.
```