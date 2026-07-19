---
task_id: CAN-20260719-otbm-e2e-005-thais-temple-depot
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-005
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-005-thais-temple-depot
base_branch: main
created: 2026-07-19
updated: 2026-07-19
last_verified_commit: "c353b89b5a7f783cf4ee22fe1ba91850de837a68"
risk: high
related_issue: ""
related_pr: "600"
depends_on:
  - merged PR #567 canary-otbm-e2e-route-plan-v1
  - merged PR #571 canary-otbm-semantic-landmarks-v1 infrastructure
  - merged PR #572 canary-otbm-route-interactions-v1 infrastructure
  - merged PR #580 executable interaction-aware Reachability
  - merged PR #589 Universal follow_route execution
  - merged PR #594 exact-map static route preflight
  - PR #599 reviewed Thais semantic landmark binding must merge before final route generation and physical proof
blocks:
  - OTBM-E2E-006 and later second-stage routing enhancements
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260719-otbm-e2e-005-thais-temple-depot.md
    - tools/e2e/prepare_otbm_route.py
    - tests/e2e/test_prepare_otbm_route.py
    - tests/e2e/routes/thais-temple-depot.json
    - tests/e2e/scenarios/movement/physical-thais-temple-depot.json
  shared:
    - .github/workflows/universal-agent-e2e.yml
  read_only:
    - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
    - docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md
    - docs/ai-agent/OTBM_WORLD_INDEX.md
    - docs/ai-agent/OTBM_REACHABILITY.md
    - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.md
    - docs/ai-agent/OTBM_SEMANTIC_LANDMARKS.schema.json
    - docs/ai-agent/OTBM_SEMANTIC_LANDMARKS.json
    - docs/ai-agent/OTBM_ROUTE_INTERACTIONS.md
    - docs/ai-agent/OTBM_ROUTE_INTERACTIONS.json
    - docs/ai-agent/OTBM_E2E_ROUTE_PREFLIGHT.md
    - tools/ai-agent/otbm_reachability*.py
    - tools/ai-agent/otbm_world_index*.py
    - tools/ai-agent/otbm_semantic_landmarks.py
    - tools/ai-agent/otbm_route_interactions.py
    - tools/ai-agent/otbm_route_preflight.py
    - tools/ai-agent/otbm_item_audit_scan.cpp
    - tools/e2e/route_plan_execution.py
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/client/agent_e2e_route.lua
    - tools/e2e/client/agent_e2e_scenario.lua
modules_touched:
  - OTBM reference physical route integration
  - Universal E2E route-artifact preparation bridge
reuses:
  - canary-otbm-e2e-route-plan-v1
  - canary-otbm-semantic-landmarks-v1
  - canary-otbm-route-interactions-v1
  - canary-otbm-e2e-route-preflight-v1
  - Unified OTBM World Index
  - canonical Reachability BFS route export
  - Universal follow_route exact-position executor
  - Universal Agent E2E two-session lifecycle
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Deliver `OTBM-E2E-005 — Reference physical route: thais.temple -> thais.depot` as the first exact-map semantic landmark-to-landmark physical route proof. The scenario must reuse the merged OTBM evidence/planning/preflight contracts and the existing Universal Physical E2E lifecycle, physically reach the exact reviewed depot destination anchor with controlled OTClient `follow_route`, and preserve safe logout, persistence, relog and second safe logout evidence.

# Acceptance criteria

- [ ] Consume semantic landmark IDs `thais.temple` and `thais.depot` from the reviewed exact-map registry; do not hard-code guessed landmark coordinates.
- [ ] Require PR #599 landmark binding to be merged and update this branch from the resulting current `main` before final route generation.
- [ ] Build/reuse the exact canonical World Index for source map SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2` without committing `.widx` or the source map.
- [ ] Generate the complete route with existing Reachability/exporter only; do not implement another parser, World Index, BFS/A*/Dijkstra/pathfinder or renderer.
- [ ] Resolve only interactions actually required by the generated path; a strict same-floor path with no required interaction must not invent one.
- [ ] Pass `canary-otbm-e2e-route-preflight-v1` against the exact runtime map, exact World Index, appearances and reviewed semantic registry.
- [ ] Add feature-owned deterministic route request/fixture/assertion data plus only the proven minimal shared bridge required to materialize the canonical route artifact before the unchanged physical executor consumes it.
- [ ] Do not create a second E2E runner, workflow or physical-client lifecycle.
- [ ] Make the canonical runner own/materialize `route-<logical-id>.json` without committing generated route reports.
- [ ] Keep generated `.widx` temporary and outside the uploaded Universal E2E evidence payload; retain only bounded route/preflight/provenance evidence.
- [ ] Execute the existing `follow_route` action through a real controlled OTClient and assert the exact reviewed depot destination anchor.
- [ ] Preserve route-plan provenance and runtime map hash in retained physical evidence.
- [ ] Pass safe first logout, persistence sentinel, relog and second safe logout.
- [ ] Keep the scenario reproducible on the reviewed exact map snapshot.
- [ ] Run focused validation plus required Universal Agent E2E physical proof.
- [ ] Apply `ci:final-gate` before the final checkpoint commit and make no post-final-head commits.
- [ ] Require exact-final-head required checks, clean review/comment/thread state, live-main overlap recheck and mergeability before squash merge with expected head SHA.
- [ ] After feature merge, complete exact active-to-archive lifecycle before declaring programme v1 complete.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19
head: ac6b5cab7923b27b45e9a42865fa5350f4083776
branch: feat/otbm-e2e-005-thais-temple-depot
pr: 600
status: implementing
context_routes:
  - agent-governance
  - otbm
  - e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260719-otbm-e2e-005-thais-temple-depot.md
  - tools/e2e/prepare_otbm_route.py
  - tests/e2e/test_prepare_otbm_route.py
  - tests/e2e/routes/thais-temple-depot.json
  - tests/e2e/scenarios/movement/physical-thais-temple-depot.json
  - .github/workflows/universal-agent-e2e.yml
proven:
  - live main at task start is c353b89b5a7f783cf4ee22fe1ba91850de837a68
  - no actual OTBM-E2E-005 task, branch or PR existed before this task branch was created
  - draft PR #600 owns feat/otbm-e2e-005-thais-temple-depot
  - open PR #599 is a disjoint landmark-binding prerequisite and explicitly excludes the actual OTBM-E2E-005 physical scenario
  - source map /mnt/data/otservbr(4).otbm is available with size 184776037 bytes and SHA-256 a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
  - exact current native OTBM scanner source blob dbc778b51f91f5a95203bb491ef772bfd3ab1e24 rebuilt the canonical World Index with 17972761 tiles, 23359571 placements, 9339 mechanic placements, 1171 indexed tile areas and zero unknown attribute tails
  - generated exact World Index SHA-256 is 6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a and remains outside Git
  - exact OTBM town evidence resolves town id 8 name Thais temple position 32369,32241,7
  - exact map evidence correlates four nearby depotId 8 lockers with Thais
  - PR #599 independently reviewed and selected route-destination anchor 32352,32226,7 using minimum strict Reachability distance plus deterministic lexicographic tie-break
  - PR #599 final bounded static route report records region 32347,32216,7 through 32369,32241,7, confirmed strict distance 66 and no transition IDs used
  - existing follow_route requires canonical runner-owned route-<logical-id>.json in the artifact directory and validates route hash, provenance, executability and exact final destination
  - E2E-ROUTE-001 explicitly scoped route production out and only implemented validated canonical artifact consumption
  - the implemented minimal bridge keeps run_agent_e2e.py, run_physical_e2e.sh and both controlled-client Lua executors unchanged
  - the Universal workflow now performs metadata-only scenario resolution, prepares exact-map route evidence only when follow_route is present, then delegates to the unchanged canonical physical lifecycle
  - generated World Index state remains temporary while route-plan, request, World Index manifest, static preflight and route-preparation summary are retained as bounded evidence
  - no other live open PR owns the modified Universal E2E workflow at the latest overlap preflight
derived:
  - the narrowest missing integration contract is route-artifact preparation between metadata-only scenario selection and the existing physical lifecycle; it can be supplied by composing existing World Index, semantic landmark, Reachability and preflight APIs without changing the runner, physical shell lifecycle or controlled-client executors
  - the reviewed Thais reference path is strict same-floor and uses no transition IDs, so OTBM-E2E-005 must not invent interaction evidence for this route
unknown:
  - final merged head and squash SHA of prerequisite PR #599
  - exact physical-client outcome and retained route/preflight evidence on the eventual exact-final 005 head
blockers:
  - PR #599 is not yet merged; final 005 implementation must consume its reviewed registry from current main rather than duplicate or race its owned paths
first_failure:
  marker: Agent Task Ownership / Validate changed active task checkpoints
  evidence: Workflow run 29701205563 on head 0a8588d55222b51744f805e758ac76ed8345b6a1 rejected the checkpoint because validation was encoded as a mapping of scalar pending values instead of the required list of validation-entry mappings; implementation-focused ownership unit tests had already passed and the validator was not weakened.
conflicts: []
rejected_hypotheses:
  - guessed Tibia coordinates are rejected; exact anchors come from reviewed exact-map evidence
  - a second OTBM parser, World Index, pathfinder, renderer, E2E runner or workflow is rejected
  - committing the generated .otbm, .widx, appearances asset or route report is rejected
  - editing PR #599 landmark-registry paths from this branch is rejected because that active task owns them exclusively
  - storing the 842280592-byte generated World Index under the uploaded artifact directory is rejected; it is temporary build/preflight state only
changed_paths:
  - .github/workflows/universal-agent-e2e.yml
  - docs/agents/tasks/active/CAN-20260719-otbm-e2e-005-thais-temple-depot.md
  - tests/e2e/routes/thais-temple-depot.json
  - tests/e2e/scenarios/movement/physical-thais-temple-depot.json
  - tests/e2e/test_prepare_otbm_route.py
  - tools/e2e/prepare_otbm_route.py
validation:
  - command: Agent Task Ownership on head 0a8588d55222b51744f805e758ac76ed8345b6a1
    result: FAIL
    evidence: Workflow run 29701205563 failed at Validate changed active task checkpoints with invalid validation entry; artifact CHANGED_TASK_VALIDATION.txt points to the task checkpoint schema and the validator remains unchanged.
  - command: focused implementation unit tests in Agent Task Ownership on head 0a8588d55222b51744f805e758ac76ed8345b6a1
    result: PASS
    evidence: Workflow run 29701205563 completed Run focused unit tests successfully before checkpoint validation failed.
  - command: Agent Task Ownership on head ac6b5cab7923b27b45e9a42865fa5350f4083776
    result: FAIL
    evidence: Workflow run 29701324330 required the derived and unknown checkpoint fields; the task record was corrected without weakening the validator.
next_action: Require the corrected ownership checkpoint to pass, monitor prerequisite PR #599 to merge, update this branch from the resulting main, then run exact-map static route preparation and the real controlled-OTClient Universal Physical E2E proof before final-gate freeze.
```
