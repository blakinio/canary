---
task_id: CAN-20260718-otbm-e2e-route-integration-program
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-ROUTE-V1
status: implementing
agent: "GPT-5.5 Thinking"
branch: docs/otbm-e2e-route-integration-program-20260718
base_branch: main
created: 2026-07-18T22:55:00+02:00
updated: 2026-07-18T23:22:00+02:00
last_verified_commit: "00b1b4ec2f63b5a938e0acb0dd3f72f91a174f8c"
risk: medium
related_issue: ""
related_pr: "562"
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

- [x] Record the existing reusable OTBM and E2E components and their exact responsibility boundaries.
- [x] Define the minimal `canary-otbm-e2e-route-plan-v1` contract with edge-aware movement and transition semantics.
- [x] Define the semantic landmark and route-interaction registry responsibilities without guessing coordinates or runtime mechanics.
- [x] Define how `walk`, `door/use`, `teleport`, `stairs/ladder/hole/rope/floor-change` map to physical client execution.
- [x] Define fail-closed route-preflight rules including exact provenance and a prohibition on truncated executable routes.
- [x] Define the ordered implementation work packages with owned paths, dependencies, deliverables and acceptance gates so multiple agents can start safely in sequence.
- [x] Define the first end-to-end reference scenario `thais.temple -> thais.depot` without inventing unverified Thais coordinates.
- [x] Preserve explicit non-goals: no new parser, no second World Index, no independent pathfinder, no parallel E2E orchestrator, no AI map imagery, no committed OTBM/assets, no guessed dynamic Lua behavior.
- [x] Keep implementation paths read-only in this planning PR.
- [x] Open draft PR #562 containing only this task record and the two durable planning documents.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T23:22:00+02:00
head: 00b1b4ec2f63b5a938e0acb0dd3f72f91a174f8c
branch: docs/otbm-e2e-route-integration-program-20260718
pr: 562
status: validating
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
  - The declarative physical action layer currently supports bounded direction/count walk commands but not a route-plan follower, exact-position step synchronization, generic map-item use or inventory-item-on-map use.
  - Current open Canary PRs observed during planning own security, OAM and MyAAC scopes; no planned exclusive document path overlap was identified.
  - Draft PR 562 targets blakinio/canary:main and changed-file scope is exactly the task record plus two new durable planning documents.
  - The durable programme defines OTBM-E2E-001, OTBM-E2E-002, OTBM-E2E-003, optional split OTBM-E2E-001B, E2E-ROUTE-001, OTBM-E2E-004 and OTBM-E2E-005 with dependency ordering and acceptance gates.
  - ci:final-gate was applied before the final checkpoint sequence and remains applied for this corrected exact head.
derived:
  - The smallest architecture is a bridge layer that exports the existing Reachability predecessor graph into an edge-aware executable route plan and lets the existing Universal E2E runner execute that plan.
  - Semantic place names and physical interaction activation semantics should be separate evidence-backed registries because neither is safely inferable from raw map geometry alone.
  - Plain optimistic Reachability cannot equal physical executability; interaction-aware routing must reuse the same BFS with an executable predicate that admits only explicitly resolved conditional crossings.
unknown:
  - Exact evidence-backed coordinates/anchors for `thais.temple` and `thais.depot` on the runtime-selected map snapshot.
  - Exact final generic OTClient APIs for map-item use and inventory-item-on-map use; implementation agents must verify maintained-client APIs before coding.
conflicts: []
blockers: []
first_failure:
  marker: agent-task-ownership-checkpoint-schema
  evidence: Agent Task Ownership run 29661161207 on head 00b1b4ec2f63b5a938e0acb0dd3f72f91a174f8c required checkpoint fields blockers and rejected_hypotheses; both are added in this correction.
rejected_hypotheses:
  - Build a new OTBM parser for E2E routing.
  - Build an independent E2E pathfinder instead of reusing Reachability BFS.
  - Treat optimistic Reachability as equivalent to physical executability.
  - Put semantic landmark names and physical activation semantics into one guessed registry.
  - Encode long physical routes as blind direction/count timing sequences.
changed_paths:
  - docs/agents/tasks/active/CAN-20260718-otbm-e2e-route-integration-program.md
  - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
  - docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md
validation:
  - command: repository instruction and routed-context review
    result: PASS
    evidence: AGENTS.md, REPOSITORY_MAP.md, CONTEXT_ROUTING.md, E2E_AUTOMATION_PROGRAM.md, OTBM World Index/Reachability/Script Resolution contracts and Physical Gameplay Action Plans reviewed.
  - command: architecture reuse review
    result: PASS
    evidence: programme explicitly reuses existing Reachability _bfs/predecessor graph and Universal E2E lifecycle and forbids parallel parser/pathfinder/orchestrator implementations.
  - command: planning scope review
    result: PASS
    evidence: PR 562 changed-file list is exactly the active task plus two new durable docs; implementation paths remain read-only.
  - command: Agent Task Ownership on head 00b1b4ec2f63b5a938e0acb0dd3f72f91a174f8c
    result: FAIL
    evidence: missing required checkpoint fields blockers and rejected_hypotheses; corrected in this task-record-only commit.
  - command: final-gate preparation
    result: PASS
    evidence: ci:final-gate remains applied; this correction creates a new exact final head and no further content commits are planned.
next_action: Require exact-final-head Agent Task Ownership, CI, AI Agent Tools and OTBM Map Tools success for PR 562. Then mark ready and squash-merge if review-clean; allow lifecycle automation to archive this planning task. Start OTBM-E2E-001 and optionally OTBM-E2E-002 only from fresh current-main branches after this programme is merged.
```
