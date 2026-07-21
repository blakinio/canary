---
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
name: OTBM-aware Universal Physical E2E routing
status: completed
owner: unassigned
created: 2026-07-18T23:05:00+02:00
updated: 2026-07-21T07:10:00+02:00
completed: 2026-07-21T07:10:00+02:00
coordination_id: OTBM-E2E-ROUTE-V1
primary_paths:
  - tools/ai-agent/otbm_reachability*
  - docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md
  - docs/ai-agent/OTBM_*ROUTE*
  - docs/ai-agent/OTBM_*LANDMARK*
  - tools/e2e/run_agent_e2e.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tests/e2e/**
related_programs:
  - CAN-PROGRAM-OTBM
  - CAN-PROGRAM-E2E-PLATFORM
cross_repo_contracts:
  - OTS-E2E-CANARY-OTCLIENT
---

# Mission

Connect the completed static OTBM evidence stack to the existing Universal Physical E2E lifecycle so semantic route intents such as `thais.temple -> thais.depot` execute deterministically on exact reviewed map evidence.

```text
semantic landmark request
  -> exact evidence-backed coordinates and bounded routing region
  -> existing OTBM World Index
  -> existing Reachability graph/BFS
  -> edge-aware executable route plan
  -> exact-map static route preflight
  -> existing Universal Physical E2E
  -> controlled real OTClient follows planned positions/interactions
  -> runtime evidence and deterministic failure classification
```

The programme reused the canonical OTBM evidence stack, World Index, Reachability BFS and Universal Physical E2E lifecycle. It did not create a second parser, index, pathfinder, renderer, physical runner or workflow.

# Completion

**Completed.** Live repository evidence confirms every required v1 package and every approved second-stage package through OTBM-E2E-009 is merged and lifecycle-archived. The roadmap defines no OTBM-E2E-010.

## Delivered packages

| Package | Feature PR | Lifecycle PR | Result |
|---|---:|---:|---|
| OTBM-E2E-001 route-plan export | #567 | #570 | merged and archived |
| OTBM-E2E-002 semantic landmarks | #571 | #574 | merged and archived |
| OTBM-E2E-003 route interactions | #572 | #579 | merged and archived |
| OTBM-E2E-001B executable interaction-aware routing | #580 | #587 | merged and archived |
| E2E-ROUTE-001 Universal `follow_route` | #589 | #592 | merged and archived |
| OTBM-E2E-004 exact-map preflight | #594 | #596 | merged and archived |
| reviewed Thais landmark prerequisite | #599 | repository lifecycle | merged before reference proof |
| OTBM-E2E-005 `thais.temple -> thais.depot` physical proof | #600 | #617 | merged and archived |
| OTBM-E2E-006 automatic failure triage | #628 | #638 | merged and archived |
| OTBM-E2E-007 mechanic/Physical E2E coverage matrix | #639 | #640 | merged and archived |
| OTBM-E2E-008 Semantic Diff impacted selection | #643 | #645 | merged and archived |
| OTBM-E2E-009 candidate-map physical validation | #646 | #652 | merged and archived |

OTBM-E2E-009 feature PR #646 merged as `4aea1e43d4116976f11ee34e498b2e63155d7741`; lifecycle PR #652 merged as `5a3b079496974dbc10934266c229613fe5ab3da5`.

# Delivered contracts and boundaries

- `canary-otbm-e2e-route-plan-v1`;
- `canary-otbm-semantic-landmarks-v1`;
- `canary-otbm-route-interactions-v1`;
- executable interaction-aware routing reusing existing Reachability BFS;
- Universal Physical E2E `follow_route` with exact-position synchronization;
- `canary-otbm-e2e-route-preflight-v1`;
- deterministic OTBM-aware Physical E2E failure triage;
- `canary-otbm-e2e-coverage-targets-v1`;
- `canary-otbm-e2e-coverage-matrix-v1`;
- `canary-otbm-e2e-impacted-selection-v1`;
- `canary-otbm-candidate-physical-validation-v1`.

Generated maps, `.widx` indexes, route reports and client assets remain outside Git.

# Preserved invariants

- Exact map/index/landmark/interaction/route/runtime provenance is required where applicable.
- `unresolved`, `partially-resolved`, `referenced-only` and `conflicting` Script Resolution evidence is never promoted to handled without proof.
- Plain optimistic walkability is not physical executability.
- Unknown appearances, unsupported interactions and stale evidence fail closed.
- Static route success is not gameplay correctness; physical proof remains separate.
- Candidate-map validation keeps source/production and candidate maps distinct and never deploys or overwrites the source map.
- Semantic Diff may suppress only scenarios whose non-impact is exactly proven.

# Explicit non-goals

This completed programme does not add a new OTBM parser, second World Index, independent pathfinding engine, replacement Reachability algorithm, second E2E runner/workflow, production map writes/deployment, committed OTBM/WIDX/client assets, sprite/name-based mechanic guessing, automatic landmark guessing, automatic promotion of unresolved Script Resolution, dynamic Lua execution by static planning, combat-aware replanning, live occupancy routing, cross-region world-scale semantic routing, or claims of gameplay correctness from static success alone.

# Final completion disposition

All original v1 completion conditions are satisfied: route-plan v1, semantic landmarks, interaction semantics, interaction-aware Reachability, Universal `follow_route`, exact-map preflight and the real controlled-OTClient Thais temple-to-depot proof are delivered; the physical proof includes exact destination plus canonical logout/persistence/relog; no required v1 task remains active; and this record preserves the delivered contracts and non-goals.

The second-stage programme is also complete through OTBM-E2E-009: deterministic failure triage, mechanic coverage correlation, Semantic Diff impacted selection and isolated candidate-map physical validation are merged and archived.

# Programme closure

The dependency-safe roadmap ends at OTBM-E2E-009. Any future OTBM E2E extension must start from new live repository evidence as a separately approved programme/task. Do not invent OTBM-E2E-010 as a continuation of this completed programme.

Continue to reuse the canonical OTBM World Index, Reachability, Script Resolution, reviewed transition evidence, Semantic OTBM Diff and Universal Physical E2E infrastructure.