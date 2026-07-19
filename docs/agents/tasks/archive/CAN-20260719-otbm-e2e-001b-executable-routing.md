---
task_id: CAN-20260719-otbm-e2e-001b-executable-routing
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-001B
status: completed
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-001b-executable-routing
base_branch: main
created: 2026-07-19T11:58:00+02:00
updated: 2026-07-19T11:44:37Z
last_verified_commit: "c9a5680c06c60ca6dd0e32ed067d4ab99a765fc4"
risk: medium
related_issue: ""
related_pr: "580"
depends_on:
  - OTBM-E2E-001 route-plan contract merged as PR #567
  - OTBM-E2E-003 route interaction registry merged as PR #572
blocks:
  - robust door/use routing in OTBM-E2E-005
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260719-otbm-e2e-001b-executable-routing.md
    - tools/ai-agent/otbm_reachability_graph.py
    - tools/ai-agent/otbm_reachability_analysis.py
    - tools/ai-agent/otbm_reachability.py
    - tools/ai-agent/otbm_reachability_tool.py
    - tools/ai-agent/test_otbm_reachability_executable.py
    - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.md
    - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.schema.json
    - .github/workflows/otbm-reachability.yml
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
    - docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md
    - docs/ai-agent/OTBM_ROUTE_INTERACTIONS.md
    - docs/ai-agent/OTBM_ROUTE_INTERACTIONS.schema.json
    - docs/ai-agent/OTBM_ROUTE_INTERACTIONS.json
    - tools/ai-agent/otbm_route_interactions.py
    - tools/e2e/**
modules_touched:
  - OTBM Reachability
  - OTBM E2E Route Plan
reuses:
  - existing otbm_reachability_graph.py::_bfs traversal and predecessor map
  - existing strict and optimistic tile classification
  - existing validated transition states and transition IDs
  - canary-otbm-route-interactions-v1 resolver and provenance gate
public_interfaces:
  - canary-otbm-e2e-route-plan-v1 executable routing mode
cross_repo_tasks: []
completed: 2026-07-19T11:44:37Z
---

# Goal

Implement `OTBM-E2E-001B — Executable interaction-aware routing mode` by rerunning the existing Reachability `_bfs()` with a fail-closed executable edge policy. Strictly walkable edges remain usable; conditional crossings are usable only when their exact reviewed interaction resolves as executable. Plain optimistic/unknown reachability must never become physical executability.

# Acceptance criteria

- [x] Reuse the existing `_bfs()` traversal; do not add another pathfinder.
- [x] Preserve existing strict and optimistic Reachability report behavior when executable interaction routing is not requested.
- [x] Add an executable movement/edge policy equivalent to strict walkability OR an exact conditional crossing with supported reviewed interaction evidence.
- [x] Keep unknown appearances, unresolved quest/dynamic state, conflicting Script Resolution and unsupported interactions blocked.
- [x] Require reviewed interaction semantics for transition edges used by an executable route.
- [x] Emit exact resolved interaction evidence on the route-plan edge where the conditional crossing/transition is used.
- [x] Pin the exact interaction-registry SHA-256 in route-plan provenance when it influences executability.
- [x] Provide the programme fixture: strict route unavailable, optimistic route can cross an unknown barrier or a reviewed door, executable BFS selects only a fully reviewed path, and removing interaction evidence makes the route non-executable.
- [x] Keep existing route-plan deterministic/full-path fail-closed behavior.
- [x] Update the route-plan schema/docs plus catalogue/changelog for the changed reusable interface.
- [x] Apply `ci:final-gate` before the final checkpoint commit; merge remains contingent on green exact-final-head required checks.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T12:36:00+02:00
head: 6d5a555b3016aba1da512dddfd238fc45b57c539
branch: feat/otbm-e2e-001b-executable-routing
pr: 580
status: implementing
context_routes:
  - agent-governance
  - otbm
owned_paths:
  - docs/agents/tasks/active/CAN-20260719-otbm-e2e-001b-executable-routing.md
  - tools/ai-agent/otbm_reachability_graph.py
  - tools/ai-agent/otbm_reachability_analysis.py
  - tools/ai-agent/otbm_reachability.py
  - tools/ai-agent/otbm_reachability_tool.py
  - tools/ai-agent/test_otbm_reachability_executable.py
  - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.md
  - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.schema.json
  - .github/workflows/otbm-reachability.yml
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - OTBM-E2E-001 merged as PR #567 and publishes canary-otbm-e2e-route-plan-v1 from the existing Reachability BFS/predecessor graph
  - OTBM-E2E-003 merged as PR #572 and publishes canary-otbm-route-interactions-v1 with deterministic fail-closed resolution
  - programme requires executable routing to reuse the same existing _bfs() and forbids treating plain optimistic walkability as executable
  - PR #580 is the same-repository draft PR for this task with base main and head feat/otbm-e2e-001b-executable-routing
  - _bfs() remains the only traversal and now accepts an optional movement-edge predicate without changing default strict/optimistic behavior
  - validated transition edges accept an optional directional executable predicate while preserving existing strict/optimistic eligibility
  - interaction-aware routing builds a narrower executable edge set and reruns the same _bfs() rather than introducing another pathfinder
  - unknown appearances are rejected before registry lookup and therefore cannot be promoted by a reviewed selector
  - exact conditional blocker placements must all resolve executable; AID/UID barriers additionally require an explicit safe Script Resolution status
  - transition edges require exact reviewed transition-ID semantics and fail closed on unresolved dynamic/script uncertainty
  - executable route-plan edges retain exact interaction-resolution evidence and interaction-registry provenance
  - focused fixtures cover a shorter unsafe optimistic path versus a longer reviewed-door path, missing door evidence, unknown appearance fail-closed behavior, reviewed/unreviewed teleports, unresolved AID state and determinism
  - route-plan CLI accepts optional --interactions and validates the reviewed registry against exact source-map and World Index provenance before executable routing
  - route-plan schema/docs describe executable routing mode, executableDistance and edge-level interaction evidence
  - existing OTBM Reachability workflow executes and compiles test_otbm_reachability*.py, validates route-plan schema syntax and packages the route-interaction runtime dependency instead of leaving the new fixtures unexecuted
  - exact implementation head 440a9e2ee1373baa30520c1cf9f2d1bc51cbed2a passed OTBM Reachability run 90, CI run 3670, AI Agent Tools run 1135, OTBM Map Tools run 689, OTBM Semantic Diff run 105, OTBM Geometry Audit run 95 and OTBM Spawn and NPC Validation run 70
  - Agent Task Ownership run 2529 failed only because checkpoint first_failure was null instead of the required YAML mapping; the checkpoint shape was corrected to an empty mapping in commit daae7f8b87b7cea82d9bf796330bd404da2fd87b
  - branch was synchronized with live main c2e27060165b91c1de6a5f40571060e480cdcb06 through GitHub's conflict-free PR merge commit and PR base metadata was refreshed; compare reports behind_by 0
  - PR #580 changed-file scope is exactly eleven task/Reachability/route-plan/workflow/catalogue/changelog files and contains no tools/e2e, OTBM, WIDX, items.otb or asset paths
  - MODULE_CATALOG diff is limited to the OTBM Reachability row and CHANGELOG diff replaces only the stale route-plan bullet
  - ci:final-gate was applied before this final checkpoint commit
  - no open PR was found claiming OTBM-E2E-001B or otbm_reachability paths at task start
  - repository writes are restricted to blakinio/canary
  - lifecycle cleanup PR #579 for merged PR #572 is separate; auto-merge is enabled and this task does not manually archive that record
  - no OTBM, WIDX, items.otb, client assets or tools/e2e changes are in scope
derived: []
unknown:
  - exact-final-head required workflow conclusions after this checkpoint-format correction
  - final review-thread state and branch-protection Required conclusion immediately before merge
conflicts: []
blockers: []
first_failure:
  marker: Agent Task Ownership run 2535 rejected inline empty first_failure mapping
  evidence: checkpoint validator requires non-empty first_failure.marker and first_failure.evidence mapping fields
rejected_hypotheses:
  - add another BFS/A*/Dijkstra implementation
  - treat optimistic unknown appearances as executable
  - infer door or transition behavior from sprite/item names
  - modify Universal Physical E2E execution in this work package
changed_paths:
  - .github/workflows/otbm-reachability.yml
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260719-otbm-e2e-001b-executable-routing.md
  - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.md
  - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.schema.json
  - tools/ai-agent/otbm_reachability.py
  - tools/ai-agent/otbm_reachability_analysis.py
  - tools/ai-agent/otbm_reachability_graph.py
  - tools/ai-agent/otbm_reachability_tool.py
  - tools/ai-agent/test_otbm_reachability_executable.py
validation:
  - command: live programme/dependency/ownership preflight
    result: PASS
    evidence: PR #567 and PR #572 are merged; no open overlapping OTBM-E2E-001B/reachability PR found
  - command: changed-file scope review on PR #580
    result: PASS
    evidence: exactly eleven task/Reachability/route-plan/workflow/catalogue/changelog files; no tools/e2e, OTBM, WIDX, items.otb or asset paths
  - command: OTBM Reachability workflow coverage review
    result: PASS
    evidence: existing workflow was extended in place to execute the new focused fixture file, validate route-plan schema syntax and package otbm_route_interactions.py; no second workflow was created
  - command: exact implementation-head focused workflows on 440a9e2ee1373baa30520c1cf9f2d1bc51cbed2a
    result: PASS
    evidence: OTBM Reachability 90, CI 3670, AI Agent Tools 1135, OTBM Map Tools 689, OTBM Semantic Diff 105, OTBM Geometry Audit 95 and OTBM Spawn and NPC Validation 70 all succeeded
  - command: Agent Task Ownership 2535 diagnostic artifact and checkpoint parser contract
    result: FAIL
    evidence: inline first_failure empty mapping is rejected; validator requires first_failure.marker and first_failure.evidence, corrected in commit e36552ff176e1cf578407efca02269dee2b259cb
  - command: compare main...feat/otbm-e2e-001b-executable-routing before final checkpoint
    result: PASS
    evidence: live main c2e27060165b91c1de6a5f40571060e480cdcb06 is the merge base and branch is behind_by 0
  - command: shared-document PR patch review
    result: PASS
    evidence: MODULE_CATALOG changes only the Reachability row; CHANGELOG changes only the route-plan bullet
next_action: Verify exact-final-head workflows including stable Required, confirm no unresolved review threads and unchanged mergeability/head, then squash-merge PR #580 with expected_head_sha.
```

## Automated lifecycle completion

- Feature PR: #580.
- Feature head: `ebf36b85bef344b54e509bb181980f28f8c81c85`.
- Merge commit: `c9a5680c06c60ca6dd0e32ed067d4ab99a765fc4`.
- Merged at: `2026-07-19T11:44:37Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
