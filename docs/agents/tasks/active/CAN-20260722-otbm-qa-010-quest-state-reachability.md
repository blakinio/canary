---
task_id: CAN-20260722-otbm-qa-010-quest-state-reachability
program_id: CAN-PROGRAM-OTBM
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-010-quest-state-reachability-20260722
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "7bdfc5f276663393e6115d02de748026df7e8439"
risk: medium
related_issue: ""
related_pr: "709"
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

IMPLEMENTING — bounded QA-010 implementation is present in draft PR #709; shared catalogue/changelog and final validation remain.

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
updated_at: 2026-07-22T09:36:00+02:00
head: 7bdfc5f276663393e6115d02de748026df7e8439
branch: feat/otbm-qa-010-quest-state-reachability-20260722
pr: 709
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
  - Current main was identical to 6a87373e84073a84ccdbdb64f7d61b2747f40764 at QA-010 preflight.
  - No open QA-010 or quest-state-reachability PR was found during the fresh overlap preflight.
  - The canonical Storage Dependency Graph emits only conservative exact same-key transitions and preserves dynamic, inequality and else cases as non-transition evidence.
  - The canonical Route Interaction Registry is reused through resolve_interaction; unresolved, conflicting or ambiguous evidence is not traversable.
  - Draft PR 709 contains the bounded core, CLI, manifest/report schemas, documentation and focused semantic, schema and output-safety tests.
  - Repository CI run 29900217346 passed on head 7bdfc5f276663393e6115d02de748026df7e8439.
derived:
  - QA-010 remains a deterministic composition layer and does not reconstruct storage parsing, map scanning, Script Resolution or pathfinding.
unknown:
  - No committed reviewed interaction registry is guaranteed for any concrete quest scope; generic fixture tests can prove the composition contract while real target evaluation remains evidence-dependent.
conflicts: []
first_failure:
  marker: Agent Task Ownership run 29900217186 / Validate changed active task checkpoints
  evidence: The active task was opened in PR 709 while frontmatter related_pr remained empty and checkpoint pr remained none; lifecycle validation requires both to match the current PR.
rejected_hypotheses:
  - Inferring transition order from Lua or source proximity was rejected by the Storage Graph evidence boundary.
  - Treating missing selected-scope producers as global impossibility was rejected by the roadmap safety boundary.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-010-quest-state-reachability.md
  - tools/ai-agent/otbm_quest_state_reachability.py
  - tools/ai-agent/otbm_quest_state_reachability_tool.py
  - tools/ai-agent/test_otbm_quest_state_reachability.py
  - tools/ai-agent/test_otbm_quest_state_reachability_output_safety.py
  - tools/ai-agent/test_otbm_quest_state_reachability_schema.py
  - docs/ai-agent/OTBM_QUEST_STATE_REACHABILITY.md
  - docs/ai-agent/OTBM_QUEST_STATE_REACHABILITY_MANIFEST.schema.json
  - docs/ai-agent/OTBM_QUEST_STATE_REACHABILITY.schema.json
validation:
  - command: post-QA-009 live main and overlap preflight
    result: PASS
    evidence: main 6a87373e84073a84ccdbdb64f7d61b2747f40764; no competing QA-010 PR or task found.
  - command: GitHub Actions CI run 29900217346
    result: PASS
    evidence: repository CI passed on implementation head 7bdfc5f276663393e6115d02de748026df7e8439.
  - command: GitHub Actions Agent Task Ownership run 29900217186
    result: FAIL
    evidence: lifecycle metadata mismatch for current PR 709; related_pr and checkpoint pr are corrected in the next task-record commit.
blockers: []
next_action: Update shared MODULE_CATALOG and CHANGELOG entries, verify focused OTBM and AI Agent workflows, then prepare one final checkpoint commit under ci:final-gate.
```
