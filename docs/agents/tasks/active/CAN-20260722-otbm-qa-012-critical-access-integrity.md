---
task_id: CAN-20260722-otbm-qa-012-critical-access-integrity
program_id: CAN-PROGRAM-OTBM
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-012-critical-access-integrity-20260722
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "5b4402958daa6584f90b848f385ad24a391b03a4"
risk: medium
related_issue: ""
related_pr: "717"
depends_on:
  - CAN-20260722-otbm-qa-011-connectivity-resilience complete
  - OTBM Semantic Landmark Registry available
  - OTBM geometry and consistency audit available
  - OTBM spawn, boss and NPC validator available
  - Unified OTBM World Index available
blocks:
  - OTBM-QA-013 identifier, selector and collision integrity
  - OTBM-QA-017 deterministic change risk
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_critical_access_integrity.py
    - tools/ai-agent/otbm_critical_access_integrity_tool.py
    - tools/ai-agent/test_otbm_critical_access_integrity.py
    - tools/ai-agent/test_otbm_critical_access_integrity_output_safety.py
    - tools/ai-agent/test_otbm_critical_access_integrity_schema.py
    - docs/ai-agent/OTBM_CRITICAL_ACCESS_INTEGRITY.md
    - docs/ai-agent/OTBM_CRITICAL_ACCESS_TARGETS.schema.json
    - docs/ai-agent/OTBM_CRITICAL_ACCESS_INTEGRITY.schema.json
    - docs/agents/tasks/active/CAN-20260722-otbm-qa-012-critical-access-integrity.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/otbm_world_index.py
    - tools/ai-agent/otbm_semantic_landmarks.py
    - tools/ai-agent/otbm_connectivity_resilience.py
    - tools/ai-agent/otbm_geometry_audit.py
    - tools/ai-agent/otbm_spawn_npc.py
    - docs/ai-agent/OTBM_SEMANTIC_LANDMARKS.schema.json
    - docs/ai-agent/OTBM_CONNECTIVITY_RESILIENCE.schema.json
    - docs/ai-agent/OTBM_GEOMETRY_AUDIT.schema.json
    - docs/ai-agent/OTBM_SPAWN_NPC_VALIDATION.schema.json
modules_touched:
  - otbm-critical-access-integrity
reuses:
  - Unified OTBM World Index exact tile/mechanic evidence
  - OTBM Semantic Landmark Registry
  - OTBM Connectivity Resilience report
  - OTBM geometry and consistency audit
  - OTBM spawn, boss and NPC validation
public_interfaces:
  - canary-otbm-critical-access-targets-v1
  - canary-otbm-critical-access-integrity-v1
cross_repo_tasks: []
---

# CAN-20260722 — OTBM-QA-012 Critical Infrastructure, House and Spawn Access Integrity

## Status

IMPLEMENTING — QA-011 feature and lifecycle are complete; fresh QA-012 overlap preflight passed and the draft branch was refreshed onto current `main` `5b4402958daa6584f90b848f385ad24a391b03a4` after one unrelated E2E commit advanced the base.

## Goal

Provide targeted static integrity checks for explicitly reviewed high-value landmarks, houses and spawn/NPC/boss access contexts without guessing semantic importance, intended public accessibility or runtime behavior.

## Bounded slice

- Add a reviewed target manifest that declares semantic criticality and exact evidence references; criticality is never inferred from item names, map appearance or proximity.
- Critical-landmark targets reuse exact Semantic Landmark anchors and an existing QA-011 Connectivity Resilience route ID.
- House targets reuse exact World Index tile/placement evidence for declared `houseId`, `houseDoorId` and door position; correlate existing Geometry Audit findings by exact `houseId`; require a reviewed QA-011 access route whose proven path includes the declared house-door position and terminates at the declared interior/access target.
- Spawn/NPC/boss targets reuse existing Spawn/NPC validation placement IDs and exact positions plus a reviewed QA-011 route whose declared goal matches the placement/access target.
- Preserve strict, optimistic and executable route evidence separately; absence of a proven reviewed route means unresolved/unreachable in the selected evidence context, not global or runtime inaccessibility.
- Fail closed on stale/mismatched source-map or World Index provenance, truncated evidence required for exact target resolution, duplicate/ambiguous selectors and missing referenced IDs.

## Explicit non-goals

- No OTBM parser/scanner, second World Index, pathfinder, geometry classifier, spawn/NPC scanner or landmark resolver.
- No inference of semantic criticality, house purpose, public accessibility, intended one-way behavior or runtime access.
- No Lua execution, door/storage/quest/database/runtime simulation or Physical E2E execution.
- No map/datapack mutation or repair recommendation.
- No change-based bypass/sever claim in v1 without a separately compatible Semantic Diff evidence contract; current-state access integrity is the bounded first slice.

## Acceptance criteria

- All landmark resolution uses the existing reviewed Semantic Landmark Registry contract and exact map/index SHA-256 provenance.
- All route evidence is consumed from existing `canary-otbm-connectivity-resilience-v1`; QA-012 performs no pathfinding.
- Exact house-door evidence is read from the existing World Index and correlated only to explicit reviewed `houseId`/`houseDoorId`/position targets.
- House component/PZ findings are consumed from `canary-otbm-geometry-audit-v1`; no geometry is recomputed.
- Spawn/NPC/boss placement status is consumed from `canary-otbm-spawn-npc-validation-v1`; no source/datapack scan is repeated.
- Truncated or incompatible required evidence fails closed rather than being treated as absence or success.
- Output remains static evidence and explicitly states that intended public accessibility and runtime reachability are not proven.
- Output is deterministic, provenance-pinned, create-new/no-clobber and rejects symlink/input-output collisions.
- Focused semantic, schema and output-safety tests plus relevant OTBM/AI Agent workflows pass.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T13:02:00+02:00
head: 5b4402958daa6584f90b848f385ad24a391b03a4
branch: feat/otbm-qa-012-critical-access-integrity-20260722
pr: 717
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_critical_access_integrity.py
  - tools/ai-agent/otbm_critical_access_integrity_tool.py
  - tools/ai-agent/test_otbm_critical_access_integrity.py
  - tools/ai-agent/test_otbm_critical_access_integrity_output_safety.py
  - tools/ai-agent/test_otbm_critical_access_integrity_schema.py
  - docs/ai-agent/OTBM_CRITICAL_ACCESS_INTEGRITY.md
  - docs/ai-agent/OTBM_CRITICAL_ACCESS_TARGETS.schema.json
  - docs/ai-agent/OTBM_CRITICAL_ACCESS_INTEGRITY.schema.json
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-012-critical-access-integrity.md
proven:
  - QA-011 feature PR 713 and lifecycle PR 716 are merged and complete; lifecycle merge is a73b20df63eb40c18a4b01a52d22fcd6ea8eb7d4.
  - Fresh QA-012 searches found no existing QA-012 task and no open critical-infrastructure/house-integrity/spawn-access PR.
  - Roadmap requires reviewed criticality metadata and forbids inferring semantic importance from item names or map appearance.
  - Semantic Landmark Registry provides exact reviewed anchors with source-map and World Index SHA-256 provenance.
  - Geometry Audit already emits exact house-disconnected-components and house-component-mixed-pz findings by houseId.
  - Spawn/NPC validation already supplies bounded exact placement/map-walkability evidence and explicitly does not prove intended public accessibility.
  - World Index exposes exact tile, houseId and placement mechanic evidence including houseDoorId without reparsing OTBM.
  - QA-011 Connectivity Resilience provides reviewed bounded route evidence without requiring QA-012 to pathfind.
  - Main advanced from a73b20df63eb40c18a4b01a52d22fcd6ea8eb7d4 to 5b4402958daa6584f90b848f385ad24a391b03a4 through one unrelated Universal E2E commit; its only shared-path overlap is MODULE_CATALOG.md, which will be reread from current main before the QA-012 shared-doc edit.
derived:
  - QA-012 can be implemented as a fail-closed evidence composer over existing IDs and provenance rather than a new scanner or route engine.
unknown:
  - A reviewed critical-access target registry for all real-world critical landmarks/houses/spawns is not guaranteed to exist; generic deterministic fixtures can prove the reusable contract while real target evaluation remains evidence-dependent.
conflicts: []
first_failure:
  marker: live-main-advance
  evidence: Draft PR 717 initially opened after main advanced one unrelated commit; the branch was safely refreshed to 5b4402958daa6584f90b848f385ad24a391b03a4 before feature implementation because only the task bootstrap commit existed.
rejected_hypotheses:
  - Inferring critical infrastructure from item names, sprite appearance or map proximity.
  - Recomputing reachability or geometry inside QA-012.
  - Treating static spawn placement access as proof of intended public accessibility.
  - Claiming bypass/sever regressions without compatible before/after Semantic Diff evidence.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-012-critical-access-integrity.md
validation:
  - command: post-QA-011 live main and overlap preflight
    result: PASS
    evidence: no competing QA-012 task/PR; branch refreshed onto current main 5b4402958daa6584f90b848f385ad24a391b03a4 before implementation.
blockers: []
next_action: Implement the smallest deterministic evidence-composition contract over existing Landmark, Connectivity, Geometry, Spawn/NPC and World Index evidence with focused tests; reread shared docs from current main before editing them.
```
