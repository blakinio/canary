---
task_id: CAN-20260718-otbm-e2e-route-integration-program
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-ROUTE-V1
status: implementing
agent: "GPT-5.5 Thinking"
branch: docs/otbm-e2e-route-integration-program-20260718
base_branch: main
created: 2026-07-18T22:55:00+02:00
updated: 2026-07-18T22:55:00+02:00
last_verified_commit: ""
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - "CAN-PROGRAM-OTBM completed bounded tooling programme"
  - "CAN-PROGRAM-E2E-PLATFORM Universal Physical E2E"
blocks:
  - "OTBM-E2E-001 Reachability executable route export"
  - "OTBM-E2E-002 Semantic Landmark Registry"
  - "OTBM-E2E-003 Route interaction semantics"
  - "E2E-ROUTE-001 Universal follow_route execution"
  - "OTBM-E2E-004 Static route preflight"
  - "OTBM-E2E-005 first landmark-to-landmark physical route scenario"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260718-otbm-e2e-route-integration-program.md
    - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
    - docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md
  shared: []
  read_only:
    - tools/ai-agent/otbm_world_index*
    - tools/ai-agent/otbm_reachability*
    - tools/ai-agent/otbm_script_resolution*
    - docs/ai-agent/OTBM_WORLD_INDEX.md
    - docs/ai-agent/OTBM_REACHABILITY.md
    - docs/ai-agent/OTBM_REACHABILITY.schema.json
    - docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
    - tools/e2e/**
    - tests/e2e/**
    - .github/workflows/**
modules_touched:
  - OTBM to Universal Physical E2E route integration planning
reuses:
  - Unified OTBM World Index
  - OTBM Reachability BFS and predecessor graph
  - OTBM Script Resolution
  - reviewed OTBM transition manifest
  - Universal OTS E2E physical lifecycle
  - declarative physical gameplay action plans
public_interfaces:
  - proposed canary-otbm-e2e-route-plan-v1
  - proposed canary-otbm-semantic-landmarks-v1
  - proposed canary-otbm-route-interactions-v1
cross_repo_tasks: []
---

# Goal

Publish the concrete architecture and ordered implementation programme that connects the completed static OTBM evidence stack to Universal Physical E2E so a future agent can request a semantic route such as `thais.temple -> thais.depot`, resolve evidence-backed anchors, reuse the existing Reachability graph/pathfinder, produce an executable route plan, preflight it against the exact map/index/provenance, and execute it through the controlled real OTClient without blind hand-authored directional sequences.

This task is planning/documentation only. It must not implement a second OTBM parser, World Index, pathfinder, E2E runner or workflow.

# Routes

- `agent-governance`
- `otbm`
- `universal-e2e`

# Acceptance criteria

- [ ] Record the existing reusable OTBM and E2E components and their exact responsibility boundaries.
- [ ] Define the minimal `canary-otbm-e2e-route-plan-v1` contract with edge-aware movement and transition semantics.
- [ ] Define the semantic landmark and route-interaction registry responsibilities without guessing coordinates or runtime mechanics.
- [ ] Define how `walk`, `door/use`, `teleport`, `stairs/ladder/hole/rope/floor-change` map to physical client execution.
- [ ] Define fail-closed route-preflight rules including exact provenance and `pathTruncated == false`.
- [ ] Define the ordered implementation work packages with owned paths, dependencies, deliverables and acceptance gates so multiple agents can start safely in sequence.
- [ ] Define the first end-to-end reference scenario `thais.temple -> thais.depot` without inventing unverified Thais coordinates.
- [ ] Preserve explicit non-goals: no new parser, no second World Index, no independent pathfinder, no parallel E2E orchestrator, no AI map imagery, no committed OTBM/assets, no guessed dynamic Lua behavior.
- [ ] Keep implementation paths read-only in this planning PR.
- [ ] Open a draft PR containing only this task record and the two durable planning documents.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T22:55:00+02:00
branch: docs/otbm-e2e-route-integration-program-20260718
pr: null
status: implementing
context_routes:
  - agent-governance
  - otbm
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260718-otbm-e2e-route-integration-program.md
  - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
  - docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md
proven:
  - Unified World Index is the canonical deterministic map evidence cache and already exposes exact tiles, item stacks, AID, UID, houseDoorId and teleport destinations.
  - Reachability already reuses World Index plus appearances, builds same-floor movement and transition edges, runs BFS, stores predecessor plus transition ID, and reconstructs an ordered coordinate path.
  - Reachability public route reports can truncate paths and expose transition IDs only as a separate list, so the existing report contract is not yet a sufficient executable E2E route contract.
  - Script Resolution is the canonical static runtime-handler correlation layer and preserves unresolved/conflicting evidence instead of guessing.
  - Universal Physical E2E already owns disposable MariaDB, exact Canary, pinned controlled OTClient, physical login/logout/relog, evidence and cleanup.
  - The declarative physical action layer currently supports bounded blind directional walk commands but not a route-plan follower, exact-position step synchronization, generic map-item use or inventory-item-on-map use.
  - Current open Canary PRs observed during planning own security, OAM and MyAAC scopes; no planned exclusive document path overlap was identified.
derived:
  - The smallest architecture is a bridge layer that exports the existing Reachability predecessor graph into an edge-aware executable route plan and lets the existing Universal E2E runner execute that plan.
  - Semantic place names and physical interaction activation semantics should be separate evidence-backed registries because neither is safely inferable from raw map geometry alone.
unknown:
  - Exact evidence-backed coordinates/anchors for `thais.temple` and `thais.depot` on the runtime-selected map snapshot.
  - Exact final generic OTClient APIs for map-item use and inventory-item-on-map use; implementation agents must verify maintained-client APIs before coding.
conflicts: []
first_failure:
  marker: none
  evidence: Planning preflight found no exclusive-path overlap for the three new documentation files.
changed_paths:
  - docs/agents/tasks/active/CAN-20260718-otbm-e2e-route-integration-program.md
validation:
  - command: repository instruction and routed-context review
    result: PASS
    evidence: AGENTS.md, REPOSITORY_MAP.md, CONTEXT_ROUTING.md, E2E_AUTOMATION_PROGRAM.md, OTBM World Index/Reachability/Script Resolution contracts and Physical Gameplay Action Plans reviewed.
next_action: Create the draft planning PR, then add the durable programme record and technical architecture/contract document without modifying implementation paths.
```
