---
task_id: CAN-20260722-otbm-qa-010-quest-state-reachability
program_id: CAN-PROGRAM-OTBM
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-010-quest-state-reachability-20260722
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "6a87373e84073a84ccdbdb64f7d61b2747f40764"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260721-otbm-qa-009-content-completeness complete
  - CAN-20260713-otbm-storage-dependency-graph complete
  - CAN-20260719-otbm-e2e-003-route-interactions complete
blocks:
  - OTBM-QA-011 connectivity resilience and route fragility
  - OTBM-QA-017 deterministic change risk
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_quest_state_reachability.py
    - tools/ai-agent/otbm_quest_state_reachability_tool.py
    - tools/ai-agent/test_otbm_quest_state_reachability.py
    - tools/ai-agent/test_otbm_quest_state_reachability_output_safety.py
    - tools/ai-agent/test_otbm_quest_state_reachability_schema.py
    - docs/ai-agent/OTBM_QUEST_STATE_REACHABILITY.md
    - docs/ai-agent/OTBM_QUEST_STATE_REACHABILITY_MANIFEST.schema.json
    - docs/ai-agent/OTBM_QUEST_STATE_REACHABILITY.schema.json
    - docs/agents/tasks/active/CAN-20260722-otbm-qa-010-quest-state-reachability.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/otbm_storage_graph.py
    - tools/ai-agent/otbm_storage_graph_analysis.py
    - tools/ai-agent/otbm_storage_graph_types.py
    - docs/ai-agent/OTBM_STORAGE_GRAPH.md
    - docs/ai-agent/OTBM_STORAGE_GRAPH.schema.json
    - tools/ai-agent/otbm_route_interactions.py
    - docs/ai-agent/OTBM_ROUTE_INTERACTIONS.md
    - docs/ai-agent/OTBM_ROUTE_INTERACTIONS.schema.json
modules_touched:
  - otbm-quest-state-reachability
reuses:
  - OTBM storage dependency graph
  - OTBM Route Interaction Registry
public_interfaces:
  - canary-otbm-quest-state-reachability-manifest-v1
  - canary-otbm-quest-state-reachability-v1
cross_repo_tasks: []
---

# CAN-20260722 — OTBM-QA-010 Quest State Reachability

## Status

IMPLEMENTING — fresh post-QA-009 preflight completed; bounded QA-010 feature branch established from exact current `main`.

## Goal

Derive a conservative static state-reachability view for explicitly selected quest/mechanic scopes by composing exact transitions already proven by `canary-otbm-storage-graph-v1` with explicit map/mechanic context and reviewed interaction resolution, without executing Lua or inferring new transition semantics.

## Bounded slice

- Add a reviewed manifest that selects exact storage transition IDs, initial states and desired states.
- Traverse only exact storage transitions already emitted by the canonical Storage Dependency Graph.
- Require every selected transition to match its exact namespace/key and literal predecessor/result semantics.
- Allow a selected transition to declare exact expected map-context evidence and/or one reviewed Route Interaction query.
- Reuse the existing Route Interaction Registry resolver for interaction gating; blocked/ambiguous/unresolved interaction evidence blocks that transition.
- Classify states and goals deterministically as reachable, unreachable-in-selected-scope, external-or-unproven or blocked-by-evidence.
- Preserve predecessor chains that explain every reachable selected state.
- Emit static evidence only; runtime quest completion remains explicitly unproven.

## Explicit non-goals

- No new OTBM parser/scanner, World Index, Script Resolution engine, Storage Dependency Graph, pathfinder or route planner.
- No Lua execution, callback-order inference, inequality expansion, `else` inference or source-proximity transition inference.
- No inference that missing selected-scope producers are globally impossible.
- No map mutation, repair recommendation, Physical E2E execution or gameplay certification.

## Acceptance criteria

- Input Storage Graph must be complete, exact-format v1 evidence; incomplete/truncated core transition evidence fails closed.
- Manifest transition references must resolve to exact existing Storage Graph transition IDs.
- Only exact `==` prerequisite transitions with literal/delete/exact-delta results already proven by Storage Graph are traversed.
- Dynamic storage keys/values and unresolved expressions never become reachable transitions.
- Exact expected map context must match selected transition evidence; absence or mismatch blocks the transition.
- Interaction-gated transitions must resolve through the existing Route Interaction Registry and preserve its fail-closed statuses.
- A missing predecessor in selected scope is reported as `external-or-unproven` unless the selected manifest explicitly establishes an initial state.
- Potentially unreachable selected goals remain static findings, never runtime impossibility claims.
- Output is deterministic, create-new/no-clobber and rejects symlink/input-output collisions.
- Focused semantic, schema and output-safety tests plus relevant OTBM/AI Agent workflows pass.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T09:20:00+02:00
head: 6a87373e84073a84ccdbdb64f7d61b2747f40764
branch: feat/otbm-qa-010-quest-state-reachability-20260722
pr: none
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_quest_state_reachability.py
  - tools/ai-agent/otbm_quest_state_reachability_tool.py
  - tools/ai-agent/test_otbm_quest_state_reachability.py
  - tools/ai-agent/test_otbm_quest_state_reachability_output_safety.py
  - tools/ai-agent/test_otbm_quest_state_reachability_schema.py
  - docs/ai-agent/OTBM_QUEST_STATE_REACHABILITY.md
  - docs/ai-agent/OTBM_QUEST_STATE_REACHABILITY_MANIFEST.schema.json
  - docs/ai-agent/OTBM_QUEST_STATE_REACHABILITY.schema.json
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-010-quest-state-reachability.md
proven:
  - QA-009 feature and lifecycle are complete; PR 704 merged as 6a87373e84073a84ccdbdb64f7d61b2747f40764.
  - Current main is identical to 6a87373e84073a84ccdbdb64f7d61b2747f40764 at QA-010 preflight.
  - No open QA-010 or quest-state-reachability PR was found during the fresh overlap preflight.
  - The canonical Storage Dependency Graph emits only conservative exact same-key transitions and preserves dynamic/inequality/else cases as non-transition evidence.
  - The canonical Route Interaction Registry is the existing fail-closed reviewed interaction resolver; unresolved/conflicting/ambiguous evidence is not executable.
derived:
  - QA-010 can remain a deterministic composition layer and must not reconstruct storage parsing, map scanning, Script Resolution or pathfinding.
unknown:
  - No committed reviewed interaction registry is guaranteed for any concrete quest scope; fixture-based focused tests may prove the generic composition contract while real target evaluation remains evidence-dependent.
conflicts: []
first_failure:
  marker: none
  evidence: No ownership or overlap blocker was found before bounded implementation.
rejected_hypotheses:
  - Inferring transition order from Lua/source proximity: rejected by Storage Graph evidence boundary.
  - Treating missing selected-scope producers as global impossibility: rejected by roadmap safety boundary.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-010-quest-state-reachability.md
validation:
  - command: post-QA-009 live main/PR/overlap preflight
    result: PASS
    evidence: main 6a87373e84073a84ccdbdb64f7d61b2747f40764; no competing QA-010 PR/task found.
blockers: []
next_action: Open the early draft PR, then implement the smallest deterministic manifest/report composition over exact Storage Graph transitions and existing Route Interaction resolution with focused tests.
```
