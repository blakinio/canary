---
task_id: CAN-20260722-otbm-qa-011-connectivity-resilience
program_id: CAN-PROGRAM-OTBM
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-011-connectivity-resilience-20260722
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "4bd646ab8ae0727123ad7589bac659f13ca7fb31"
risk: medium
related_issue: ""
related_pr: "713"
depends_on:
  - CAN-20260722-otbm-qa-010-quest-state-reachability complete
  - OTBM teleport and reachability validator merged
  - OTBM Route Interaction Registry available
blocks:
  - OTBM-QA-012 critical infrastructure, house and spawn access integrity
  - OTBM-QA-017 deterministic change risk
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_connectivity_resilience.py
    - tools/ai-agent/otbm_connectivity_resilience_tool.py
    - tools/ai-agent/test_otbm_connectivity_resilience.py
    - tools/ai-agent/test_otbm_connectivity_resilience_output_safety.py
    - tools/ai-agent/test_otbm_connectivity_resilience_schema.py
    - docs/ai-agent/OTBM_CONNECTIVITY_RESILIENCE.md
    - docs/ai-agent/OTBM_CONNECTIVITY_RESILIENCE_MANIFEST.schema.json
    - docs/ai-agent/OTBM_CONNECTIVITY_RESILIENCE.schema.json
    - docs/agents/tasks/active/CAN-20260722-otbm-qa-011-connectivity-resilience.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/otbm_reachability.py
    - tools/ai-agent/otbm_reachability_analysis.py
    - tools/ai-agent/otbm_reachability_graph.py
    - tools/ai-agent/otbm_reachability_transition.py
    - tools/ai-agent/otbm_reachability_types.py
    - docs/ai-agent/OTBM_REACHABILITY.md
    - docs/ai-agent/OTBM_REACHABILITY.schema.json
    - tools/ai-agent/otbm_route_interactions.py
    - docs/ai-agent/OTBM_ROUTE_INTERACTIONS.md
modules_touched:
  - otbm-connectivity-resilience
reuses:
  - OTBM Reachability graph/BFS
  - OTBM reviewed transition model
  - OTBM Route Interaction Registry when executable routing evidence is supplied
public_interfaces:
  - canary-otbm-connectivity-resilience-manifest-v1
  - canary-otbm-connectivity-resilience-v1
cross_repo_tasks: []
---

# CAN-20260722 — OTBM-QA-011 Connectivity Resilience, Route Fragility, Entrapment and Teleport Networks

## Status

IMPLEMENTING — QA-010 feature and lifecycle are complete; draft PR #713 owns the bounded QA-011 scope. `main` advanced by two unrelated OAM-035 documentation/lifecycle commits after branch creation; live compare shows no overlap with QA-011 owned paths.

## Goal

Analyze reviewed world-connectivity robustness by reusing the canonical OTBM Reachability graph/BFS and reviewed transition model, without creating another pathfinder or claiming runtime entrapment/gameplay behavior.

## Bounded slice

- Accept explicit reviewed route start/goal pairs and entry/exit target sets inside one explicit bounded region.
- Reuse canonical Reachability tile semantics, transition validation, graph edges and `_bfs` for baseline and edge-removal perturbation runs.
- Identify route edges on a proven canonical predecessor path whose single removal disconnects that reviewed route.
- Prove one alternative edge-disjoint route when canonical BFS still reaches the goal after removing every edge from the first proven route.
- Distinguish strict, optimistic and optionally executable evidence modes without promoting unresolved transitions.
- Identify selected entry points with no proven exit path as static entrapment candidates.
- Summarize reviewed transition/teleport topology including one-way edges, dead ends and cycles using canonical transition evidence.
- Preserve static-only caveats when runtime state/scripts/mechanics outside selected evidence may resolve a finding.

## Explicit non-goals

- No second pathfinder, route planner, World Index, OTBM parser/scanner or transition resolver.
- No inference of stairs/holes/ladders/teleport destinations from names, sprites, proximity or chat history.
- No Lua execution, runtime door/storage/quest state simulation or Physical E2E execution.
- No global world connectivity or entrapment claim from bounded reviewed evidence.
- No map/datapack mutation or repair recommendation.

## Acceptance criteria

- All path/connectivity calculations call the existing canonical Reachability `_bfs`; movement and transition topology reuse `_movement_neighbors` and `_transition_edges` semantics.
- Only exact reviewed route/entry/exit coordinates inside explicit bounds are analyzed.
- Edge-removal fragility reports only edges from a complete canonical predecessor route and proves disconnection by rerunning canonical BFS with exactly that edge excluded.
- Alternative-route evidence is reported only when a second canonical path exists after excluding every edge from the first path.
- Conditional/optimistic or unresolved transition evidence stays distinct from strict proof; executable mode requires existing interaction-aware evidence.
- Static entrapment means no selected exit is proven in the analyzed evidence mode, not runtime impossibility.
- Transition/teleport one-way, dead-end and cycle findings preserve reviewed uncertainty and do not classify intentional one-way edges as defects without evidence.
- Output is deterministic, provenance-pinned, create-new/no-clobber and rejects symlink/input-output collisions.
- Focused semantic, schema and output-safety tests plus relevant OTBM/AI Agent workflows pass.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T10:52:00+02:00
head: 4bd646ab8ae0727123ad7589bac659f13ca7fb31
branch: feat/otbm-qa-011-connectivity-resilience-20260722
pr: 713
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_connectivity_resilience.py
  - tools/ai-agent/otbm_connectivity_resilience_tool.py
  - tools/ai-agent/test_otbm_connectivity_resilience.py
  - tools/ai-agent/test_otbm_connectivity_resilience_output_safety.py
  - tools/ai-agent/test_otbm_connectivity_resilience_schema.py
  - docs/ai-agent/OTBM_CONNECTIVITY_RESILIENCE.md
  - docs/ai-agent/OTBM_CONNECTIVITY_RESILIENCE_MANIFEST.schema.json
  - docs/ai-agent/OTBM_CONNECTIVITY_RESILIENCE.schema.json
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-011-connectivity-resilience.md
proven:
  - QA-010 feature PR 709 and lifecycle PR 710 are merged and complete; lifecycle merge is 7b993dc48c6e0be5ddeb63f0f487bef5e774040e.
  - No existing QA-011 task record and no open connectivity-resilience, route-fragility, entrapment or teleport-network PR existed at the initial fresh preflight.
  - Roadmap requires all QA-011 path/connectivity calculations to reuse the existing Reachability graph/BFS and reviewed transition model.
  - Canonical Reachability exposes _bfs, _movement_neighbors, _transition_edges, _reconstruct_route and _tarjan_cycles; QA-011 composes those functions rather than implementing a second pathfinder.
  - After branch creation, main advanced to 1328fb42b03056a0f2571831a1a1eb7a5416f73a through OAM-035 documentation/lifecycle commits only.
  - Compare 7b993dc48c6e0be5ddeb63f0f487bef5e774040e..1328fb42b03056a0f2571831a1a1eb7a5416f73a changes only OAM-035 documentation and its active/archive task records; none overlap QA-011 owned paths.
  - PR 713 currently differs from live main only by the QA-011 active task record despite being two unrelated commits behind.
derived:
  - QA-011 can proceed without integrating the unrelated OAM-035 commits; final mergeability must still be rechecked against live main before readiness.
unknown:
  - No reviewed target manifest for concrete real-world route/entry/exit pairs is guaranteed to be committed; generic fixture tests can prove the reusable contract while real target evaluation remains evidence-dependent.
conflicts: []
first_failure:
  marker: none
  evidence: No ownership or overlapping-path blocker remains after reconciling the live-main advance.
rejected_hypotheses:
  - Building a second BFS/pathfinder was rejected by the roadmap reuse boundary.
  - Treating bounded static no-exit evidence as runtime entrapment was rejected by the roadmap caveat.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-011-connectivity-resilience.md
validation:
  - command: post-QA-010 live main and overlap preflight
    result: PASS
    evidence: no competing QA-011 PR/task found before branch creation.
  - command: live compare 7b993dc4..1328fb42
    result: PASS
    evidence: only unrelated OAM-035 documentation/lifecycle paths changed on main; no QA-011 ownership overlap.
blockers: []
next_action: Implement the bounded reviewed-route perturbation and entrapment/topology composition over canonical Reachability graph/BFS with focused tests, then recheck live-main mergeability before final validation.
```
