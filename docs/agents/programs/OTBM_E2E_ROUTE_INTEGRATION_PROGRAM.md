---
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
name: OTBM-aware Universal Physical E2E routing
status: completed
owner: unassigned
created: 2026-07-18T23:05:00+02:00
updated: 2026-07-21T06:35:00+02:00
completed: 2026-07-21T06:35:00+02:00
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

Connect the completed static OTBM evidence stack to the existing Universal Physical E2E lifecycle so an agent can express a semantic route intent such as `thais.temple -> thais.depot` and obtain deterministic, evidence-backed physical execution on the exact reviewed map snapshot.

The delivered pipeline is:

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

The programme deliberately reused the existing OTBM parser/evidence stack, World Index, Reachability BFS and Universal Physical E2E lifecycle. It did not create a second parser, index, pathfinder, renderer, physical runner or workflow.

# Completion status

**Completed.** Live repository evidence verified that every required v1 package and every approved second-stage package through OTBM-E2E-009 is merged and lifecycle-archived. No OTBM-E2E-010 package exists in this programme.

## Delivered v1 packages

| Package | Feature PR | Lifecycle PR | Result |
|---|---:|---:|---|
| OTBM-E2E-001 — Reachability executable route export | #567 | #570 | merged and archived |
| OTBM-E2E-002 — Semantic Landmark Registry | #571 | #574 | merged and archived |
| OTBM-E2E-003 — Route interaction semantics | #572 | #579 | merged and archived |
| OTBM-E2E-001B — Executable interaction-aware routing | #580 | #587 | merged and archived |
| E2E-ROUTE-001 — Universal `follow_route` execution | #589 | #592 | merged and archived |
| OTBM-E2E-004 — Exact-map static route preflight | #594 | #596 | merged and archived |
| Reviewed Thais landmark evidence prerequisite | #599 | lifecycle recorded by repository task lifecycle | merged before reference-route proof |
| OTBM-E2E-005 — `thais.temple -> thais.depot` physical proof | #600 | #617 | merged and archived |

The OTBM-E2E-005 physical proof uses reviewed semantic landmark IDs, exact map/World Index provenance, the canonical Reachability route export, exact-map preflight, Universal `follow_route`, controlled OTClient execution and the canonical logout/persistence/relog sentinel.

## Delivered second-stage packages

| Package | Feature PR | Lifecycle PR | Result |
|---|---:|---:|---|
| OTBM-E2E-006 — Automatic E2E failure triage | #628 | #638 | merged and archived |
| OTBM-E2E-007 — OTBM mechanic to Physical E2E coverage matrix | #639 | #640 | merged and archived |
| OTBM-E2E-008 — Semantic Diff impacted E2E selection | #643 | #645 | merged and archived |
| OTBM-E2E-009 — Candidate-map physical validation | #646 | #652 | merged and archived |

OTBM-E2E-009 feature PR #646 was squash-merged as `4aea1e43d4116976f11ee34e498b2e63155d7741`. Its final lifecycle PR #652 was merged as `5a3b079496974dbc10934266c229613fe5ab3da5`.

# Delivered public contracts and reusable boundaries

The programme delivered or established the following durable interfaces and boundaries:

- `canary-otbm-e2e-route-plan-v1` — complete executable edge-aware route plans derived from the existing Reachability predecessor graph;
- `canary-otbm-semantic-landmarks-v1` — reviewed semantic landmark and anchor resolution with exact map/index provenance;
- `canary-otbm-route-interactions-v1` — reviewed physical activation semantics for exact mechanic/transition selectors;
- executable interaction-aware routing that continues to reuse the existing Reachability BFS rather than introducing another pathfinder;
- Universal Physical E2E `follow_route` execution with exact-position synchronization and supported interaction execution;
- `canary-otbm-e2e-route-preflight-v1` — fail-closed exact-map route-plan validation before expensive physical execution;
- deterministic OTBM-aware Physical E2E failure triage over retained route/runtime evidence;
- `canary-otbm-e2e-coverage-targets-v1` and `canary-otbm-e2e-coverage-matrix-v1` — reviewed exact-target coverage correlation without promoting unresolved evidence;
- `canary-otbm-e2e-impacted-selection-v1` — Semantic OTBM Diff-driven impacted scenario selection;
- `canary-otbm-candidate-physical-validation-v1` — candidate-map validation that reuses approved materialization, static validation, Semantic Diff, impacted selection and the existing Universal Physical E2E lifecycle.

Generated maps, `.widx` indexes, route reports and client assets remain outside Git.

# Evidence and safety invariants preserved

- Exact map, World Index, landmark, interaction, route and runtime provenance is required where applicable.
- `unresolved`, `partially-resolved`, `referenced-only` and `conflicting` Script Resolution evidence is never promoted to handled without proof.
- Plain optimistic walkability is not treated as physical executability.
- Unknown appearances, unsupported interactions and stale evidence fail closed.
- Static route success is not claimed as gameplay correctness; physical proof remains a distinct evidence layer.
- Candidate-map validation keeps source/production and candidate maps distinct and never deploys or overwrites the production/source map.
- Semantic Diff selection may suppress only scenarios whose non-impact is exactly proven; unrelated/general gameplay coverage is not silently skipped.

# Explicit non-goals retained

The following remain outside this completed programme:

- a new OTBM parser;
- a second World Index;
- an independent route/pathfinding engine;
- replacing Reachability BFS merely for E2E;
- a second E2E runner or workflow;
- production map writes or deployment;
- committed OTBM/WIDX/client assets;
- inference of stairs, ladders, holes or other mechanics from sprite/name guesses;
- automatic guessing of semantic landmarks;
- automatic promotion of unresolved Script Resolution evidence;
- dynamic Lua execution by the static route planner;
- combat-aware dynamic replanning in v1;
- live creature/player/movable-item occupancy routing in v1;
- cross-region world-scale semantic routing in v1;
- claiming gameplay correctness from static route success alone.

# v1 completion definition — final disposition

All original completion conditions are satisfied:

1. route-plan v1 is merged and archived;
2. semantic landmark registry/resolver is merged and archived;
3. route interaction semantics are merged and archived;
4. the existing Reachability graph produces executable interaction-aware routes without a second pathfinder;
5. Universal Physical E2E executes `follow_route` with exact-position synchronization;
6. exact-map static preflight is merged and archived;
7. `thais.temple -> thais.depot` passed through a real controlled OTClient on an exact reviewed map snapshot;
8. physical evidence proved the exact destination plus canonical logout/persistence/relog;
9. no required v1 task remains active or has an open unmerged feature/lifecycle PR;
10. this durable completion record preserves the delivered contracts and non-goals.

# Programme closure

The dependency-safe roadmap ends at OTBM-E2E-009. Future work must start from new live repository evidence and a separately approved programme/task; agents must not invent OTBM-E2E-010 as a continuation of this completed programme.

For maintenance or extensions, continue to reuse the canonical OTBM World Index, Reachability, Script Resolution, reviewed transition evidence, Semantic OTBM Diff and Universal Physical E2E infrastructure described above.