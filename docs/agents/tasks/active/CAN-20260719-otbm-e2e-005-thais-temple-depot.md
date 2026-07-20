---
task_id: CAN-20260719-otbm-e2e-005-thais-temple-depot
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-005
status: ready
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-005-thais-temple-depot
base_branch: main
created: 2026-07-19
updated: 2026-07-19
last_verified_commit: "2c448205d864f6388b8be932ecbb1a9e6dcaffe0"
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
  - merged PR #599 reviewed Thais semantic landmark binding
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

Deliver `OTBM-E2E-005 — Reference physical route: thais.temple -> thais.depot` as the first exact-map semantic landmark-to-landmark physical route proof. The scenario reuses the merged OTBM evidence/planning/preflight contracts and the existing Universal Physical E2E lifecycle, physically reaches the exact reviewed depot destination anchor with controlled OTClient `follow_route`, and preserves safe logout, persistence, relog and second safe logout evidence.

# Acceptance criteria

- [x] Consume semantic landmark IDs `thais.temple` and `thais.depot` from the reviewed exact-map registry; do not hard-code guessed landmark coordinates.
- [x] Require PR #599 landmark binding to be merged and update this branch from the resulting current `main` before final route generation.
- [x] Build/reuse the exact canonical World Index for source map SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2` without committing `.widx` or the source map.
- [x] Generate the complete route with existing Reachability/exporter only; do not implement another parser, World Index, BFS/A*/Dijkstra/pathfinder or renderer.
- [x] Resolve only interactions actually required by the generated path; the selected same-floor path uses no transition IDs and invents no interaction evidence.
- [x] Pass `canary-otbm-e2e-route-preflight-v1` against the exact runtime map, exact World Index, appearances and reviewed semantic registry.
- [x] Add feature-owned deterministic route request/fixture/assertion data plus only the proven minimal shared bridge required to materialize the canonical route artifact before the unchanged physical executor consumes it.
- [x] Do not create a second E2E runner, workflow or physical-client lifecycle.
- [x] Make the canonical runner own/materialize `route-<logical-id>.json` without committing generated route reports.
- [x] Keep generated `.widx` temporary and outside the uploaded Universal E2E evidence payload; retain only bounded route/preflight/provenance evidence.
- [x] Execute the existing `follow_route` action through a real controlled OTClient and assert the exact reviewed depot destination anchor.
- [x] Preserve route-plan provenance and runtime map hash in retained physical evidence.
- [x] Pass safe first logout, persistence sentinel, relog and second safe logout.
- [x] Keep the scenario reproducible on the reviewed exact map snapshot.
- [x] Run focused validation plus required Universal Agent E2E physical proof.
- [x] Apply `ci:final-gate` before the final checkpoint commit and make no post-final-head commits.
- [ ] Require exact-final-head required checks, clean review/comment/thread state, live-main overlap recheck and mergeability before squash merge with expected head SHA.
- [ ] After feature merge, complete exact active-to-archive lifecycle before declaring this task complete.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19
head: 469428bbaad0eee3fb88a9472a7e7d389e8d9539
branch: feat/otbm-e2e-005-thais-temple-depot
pr: 600
status: ready
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
  - PR #599 merged the reviewed Thais semantic landmark binding as 7b659fc3ad2de16374adf5450e97a731406f92e6 before final route generation
  - source map /mnt/data/otservbr(4).otbm has size 184776037 bytes and SHA-256 a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
  - exact native OTBM scanner source blob dbc778b51f91f5a95203bb491ef772bfd3ab1e24 rebuilt the canonical World Index with 17972761 tiles, 23359571 placements, 9339 mechanic placements, 1171 indexed tile areas and zero unknown attribute tails
  - generated exact World Index SHA-256 is 6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a and remains temporary and outside Git and retained Universal evidence
  - reviewed semantic registry resolves thais.temple route-origin to 32369,32241,7 and thais.depot route-destination to 32352,32226,7 inside region 32347,32216,7 through 32369,32241,7
  - reviewed landmark evidence established a four-direction strict baseline route distance 66 with no transition IDs before runtime execution
  - the implemented bridge composes existing World Index, semantic landmark, Reachability route export and exact-map preflight APIs while leaving run_agent_e2e.py, run_physical_e2e.sh, route_plan_execution.py and both controlled-client Lua executors unchanged
  - generated World Index state remains temporary while route plan, request, World Index manifest, static preflight and route-preparation summary are retained as bounded evidence
  - initial Universal physical run 29702291544 proved exact route preparation and preflight but the first four-direction WEST movement edge from 32369,32241,7 to 32368,32241,7 was not observed within the runtime timeout
  - the existing canonical diagonal Reachability option produced a 59-edge executable route from 32369,32241,7 to 32352,32226,7 with plan SHA-256 0736a819ef656f9040ea14c51f1ab474beabe9e4da50435e1eb9e7fd0c28974b and no transition IDs
  - successful pre-sync Universal physical run 29703752964 confirmed the diagonal route end to end without weakening the exact destination or persistence assertions
  - feature changes were cleanly replayed onto main 183d7224cb5de57585294d72631f37783b93dc89 through technical PR #609, producing validated implementation parent 469428bbaad0eee3fb88a9472a7e7d389e8d9539 with exactly the six OTBM-E2E-005 changed paths
  - synchronized Agent Task Ownership run 29704821358 passed on implementation parent 469428bbaad0eee3fb88a9472a7e7d389e8d9539
  - synchronized CI run 29704821457 passed on implementation parent 469428bbaad0eee3fb88a9472a7e7d389e8d9539
  - synchronized Universal Agent E2E run 29704821423 passed Resolve scenario, exact Canary build, controlled OTClient build, Physical client movement/physical-thais-temple-depot and Required physical E2E
  - synchronized Universal artifact 8447816376 digest sha256:131faa08eaaccdacda62788b2e173b0f9ecc422a62ecd4769e874e4d136aeb40 retains exact-map route/preflight/provenance and physical lifecycle evidence
  - synchronized route preparation status is passed with runtime map SHA-256 a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2, World Index SHA-256 6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a, World Index retained false, distance 59 and preflight status passed
  - synchronized route preflight status is passed with ok true, zero findings, exact semantic origin 32369,32241,7 and exact semantic destination 32352,32226,7
  - synchronized physical evidence records route_plans=1, route_temple-to-depot=success, step_temple-to-depot=success and step_temple-to-depot_detail=32352,32226,7
  - synchronized physical evidence records safe first logout, confirmed first persistence, successful second login, persistence_check_level=success with detail 500, safe second logout and e2e=success
  - synchronized result records two server logins, two packet records, zero client exit code, no fatal runtime log hits and all scenario SQL assertions passed
  - after synchronized proof, live main advanced from 183d7224cb5de57585294d72631f37783b93dc89 to 2c448205d864f6388b8be932ecbb1a9e6dcaffe0 only through two disjoint OAM-021 documentation additions; fresh compare found no overlap with OTBM-E2E-005 or its runtime dependencies
  - ci:final-gate was applied to PR #600 before this final checkpoint commit
  - no .otbm, .widx, appearances asset or generated route report is committed by this task
  - OTBM-E2E-006 has not been started and remains blocked until OTBM-E2E-005 feature merge and exact active-to-archive lifecycle complete

derived:
  - static exact-map Reachability intentionally cannot prove dynamic runtime occupancy; the runtime-rejected initial four-direction WEST edge therefore does not invalidate the reviewed map/WIDX walkability evidence
  - reusing the existing diagonal Reachability mode is the narrowest canonical correction because it changes only route generation options, keeps exact reviewed semantic endpoints and preflight provenance, introduces no new pathfinder and requires no transition interactions
  - the two post-proof OAM-021 documentation commits on main are disjoint from the feature and do not invalidate the synchronized exact-map or controlled-client runtime proof
unknown:
  - exact final checkpoint commit SHA and its exact-final-head workflow conclusions are not knowable until this commit exists and must be verified before merge
  - exact runtime actor or transient condition that rejected the original WEST edge is not proven and is not asserted
  - final PR #600 squash merge SHA is unknown until merge
  - exact active-to-archive lifecycle PR and merge SHA are unknown until post-feature lifecycle cleanup
blockers: []
first_failure:
  marker: Agent Task Ownership / Validate changed active task checkpoints
  evidence: Workflow run 29701205563 on head 0a8588d55222b51744f805e758ac76ed8345b6a1 rejected the initial checkpoint validation shape; the validator was not weakened and the task record was corrected before implementation validation continued.
conflicts: []
rejected_hypotheses:
  - guessed Tibia coordinates are rejected; exact anchors come from reviewed exact-map evidence
  - a second OTBM parser, World Index, pathfinder, renderer, E2E runner or workflow is rejected
  - committing the generated .otbm, .widx, appearances asset or route report is rejected
  - editing PR #599 landmark-registry paths from this branch is rejected because that task owned them exclusively until merge
  - storing the generated 842280592-byte World Index under the uploaded artifact directory is rejected; it is temporary build/preflight state only
  - treating the first runtime WEST-edge timeout as proof that g_game.walk or the whole login session is broken is rejected because the maintained physical movement scenario had already runtime-proven movement from the same temple start and the diagonal canonical route later passed end to end
  - claiming a specific NPC or creature blocked the original WEST edge is rejected because retained evidence proves only the movement timeout, not the identity of a dynamic blocker
changed_paths:
  - .github/workflows/universal-agent-e2e.yml
  - docs/agents/tasks/active/CAN-20260719-otbm-e2e-005-thais-temple-depot.md
  - tests/e2e/routes/thais-temple-depot.json
  - tests/e2e/scenarios/movement/physical-thais-temple-depot.json
  - tests/e2e/test_prepare_otbm_route.py
  - tools/e2e/prepare_otbm_route.py
validation:
  - command: Agent Task Ownership on synchronized implementation parent 469428bbaad0eee3fb88a9472a7e7d389e8d9539
    result: PASS
    evidence: Workflow run 29704821358 completed successfully after clean replay onto main 183d7224cb5de57585294d72631f37783b93dc89.
  - command: CI on synchronized implementation parent 469428bbaad0eee3fb88a9472a7e7d389e8d9539
    result: PASS
    evidence: Workflow run 29704821457 completed successfully.
  - command: Universal Agent E2E synchronized exact-map physical proof
    result: PASS
    evidence: Workflow run 29704821423 completed Physical client / movement/physical-thais-temple-depot and Required physical E2E successfully and uploaded artifact 8447816376 with digest sha256:131faa08eaaccdacda62788b2e173b0f9ecc422a62ecd4769e874e4d136aeb40.
  - command: canary-otbm-e2e-route-preflight-v1 in synchronized Universal evidence
    result: PASS
    evidence: route-thais-temple-depot-preflight.json reports status passed, ok true, zero findings and plan SHA-256 0736a819ef656f9040ea14c51f1ab474beabe9e4da50435e1eb9e7fd0c28974b against the exact runtime map and World Index hashes.
  - command: controlled OTClient follow_route exact destination assertion
    result: PASS
    evidence: synchronized client evidence reports route_temple-to-depot=success and step_temple-to-depot_detail=32352,32226,7 after all 59 route edges.
  - command: Universal two-session persistence lifecycle
    result: PASS
    evidence: synchronized result records safe logout, confirmed persistence, successful relog, level 500 persistence check, second safe logout, two server logins, two packet records and all SQL assertions passed.
  - command: fresh live-main overlap audit after synchronized proof
    result: PASS
    evidence: compare 183d7224cb5de57585294d72631f37783b93dc89..2c448205d864f6388b8be932ecbb1a9e6dcaffe0 contains only docs/agents/OTERYN_OAM_021_MARKET_REVALIDATION.md and docs/agents/tasks/archive/CAN-20260719-oteryn-market-revalidation.md.
next_action: Treat this checkpoint commit as the immutable final feature head; require exact-final-head Agent Task Ownership, CI and Universal Agent E2E, then perform clean comment/review/thread and live-main overlap audit, mark PR #600 ready, squash merge with expected head SHA, verify main, and complete the exact active-to-archive lifecycle before unblocking OTBM-E2E-006.
```
