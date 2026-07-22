---
task_id: CAN-20260722-otbm-qa-012-critical-access-integrity
program_id: CAN-PROGRAM-OTBM
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-012-critical-access-integrity-20260722
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "2f99d69428ed11f9da4698a1282d6f17c1e5d09f"
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

READY FOR FINAL GATE — bounded QA-012 current-state integrity composer, CLI, schemas, focused tests, documentation and required shared-doc entries are complete on draft PR #717. `ci:final-gate` was applied before this final checkpoint commit; no further branch commits are permitted after this checkpoint.

## Goal

Provide targeted static integrity checks for explicitly reviewed high-value landmarks, houses and spawn/NPC/boss access contexts without guessing semantic importance, intended public accessibility or runtime behavior.

## Delivered slice

- Adds reviewed target contract `canary-otbm-critical-access-targets-v1` and report `canary-otbm-critical-access-integrity-v1`.
- Critical-landmark targets reuse the existing exact Semantic Landmark resolver plus existing QA-011 Connectivity Resilience route IDs.
- House targets reuse exact canonical World Index `houseId`/`houseDoorId`/position evidence, existing Geometry Audit house findings and existing QA-011 route evidence; the reviewed route must terminate at the declared interior/access target and its proven baseline path must contain the exact reviewed door position.
- Spawn/NPC/boss targets reuse existing Spawn/NPC validation placement IDs, exact positions and existing QA-011 routes; boss targets require the canonical existing `rewardBossLiteral=true` evidence rather than name inference.
- Strict, optimistic and executable route evidence remain distinct; missing, truncated, stale, mismatched or ambiguous evidence fails closed.
- Public-access expectation may be explicitly reviewed but is never promoted to proof of public or runtime accessibility.
- v1 deliberately does not claim change-based entrance bypass/sever regressions without separately compatible before/after Semantic Diff evidence.
- CLI preserves stable input hashing, symlink rejection, distinct-input checks, output/input collision and hard-link rejection, create-new/no-clobber defaults and atomic overwrite.

## Explicit non-goals

- No OTBM parser/scanner, second World Index, pathfinder, geometry classifier, spawn/NPC scanner or landmark resolver.
- No inference of semantic criticality, house purpose, public accessibility, intended one-way behavior or runtime access.
- No Lua execution, door/storage/quest/database/runtime simulation or Physical E2E execution.
- No map/datapack mutation or repair recommendation.
- No change-based bypass/sever claim in v1 without a separately compatible Semantic Diff evidence contract.

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
updated_at: 2026-07-22T13:30:00+02:00
head: 2f99d69428ed11f9da4698a1282d6f17c1e5d09f
branch: feat/otbm-qa-012-critical-access-integrity-20260722
pr: 717
status: ready
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
  - Draft PR 717 was refreshed onto current main 5b4402958daa6584f90b848f385ad24a391b03a4 before feature implementation after one unrelated Universal E2E commit advanced the base.
  - Roadmap requires reviewed criticality metadata and forbids inferring semantic importance from item names or map appearance.
  - Semantic Landmark Registry provides exact reviewed anchors with source-map and World Index SHA-256 provenance.
  - Geometry Audit already emits exact house-disconnected-components and house-component-mixed-pz findings by houseId.
  - Spawn/NPC validation supplies stable placement IDs, exact positions/statuses, placementsTruncated and canonical rewardBossLiteral evidence plus World Index provenance.
  - World Index exposes exact tile, houseId and placement mechanic evidence including houseDoorId without reparsing OTBM.
  - QA-011 Connectivity Resilience supplies reviewed bounded route evidence; QA-012 consumes route IDs, goals and baseline paths without pathfinding.
  - An initial focused validation exposed an exact-field integration bug where the composer used spawnBossLiteral instead of the existing canonical rewardBossLiteral field; commit e25f32f484d8820a529bd5b73abfc05b78fdc4c5 corrected it and subsequent focused/full validation passed.
  - Pre-final head 2f99d69428ed11f9da4698a1282d6f17c1e5d09f passed CI run 29915417926, Agent Task Ownership 29915417736, OTBM Map Tools 29915417711 and AI Agent Tools 29915417815.
  - PR 717 changes exactly eleven declared implementation/test/docs/shared-doc/task paths.
  - Shared-doc patch audit proves MODULE_CATALOG.md has exactly one QA-012 row addition while preserving the concurrent #708 E2E row, and CHANGELOG.md has exactly one QA-012 Unreleased bullet addition.
  - Pre-final review audit found zero inline review threads and zero review submissions; PR 717 is mergeable and main remains 5b4402958daa6584f90b848f385ad24a391b03a4.
  - ci:final-gate was applied to PR 717 before this final checkpoint commit.
derived:
  - QA-012 is ready for exact-final-head validation; no implementation or documentation edits remain.
unknown:
  - A reviewed critical-access target registry for all real-world critical landmarks/houses/spawns is not guaranteed to exist; the delivered reusable contract is proven by deterministic fixtures while real target evaluation remains evidence-dependent.
conflicts: []
first_failure:
  marker: canonical-reward-boss-field-mismatch
  evidence: Initial OTBM Map Tools/AI Agent Tools validation on 32c2457a9e8b11867027fd87404d3996676b348f failed because boss-role correlation referenced non-existent spawnBossLiteral instead of existing rewardBossLiteral. The field was corrected, OTBM Map Tools became green on e25f32f484d8820a529bd5b73abfc05b78fdc4c5, and all four pre-final workflows passed on 2f99d69428ed11f9da4698a1282d6f17c1e5d09f.
rejected_hypotheses:
  - Inferring critical infrastructure from item names, sprite appearance or map proximity.
  - Recomputing reachability or geometry inside QA-012.
  - Treating static spawn placement access as proof of intended public accessibility.
  - Claiming bypass/sever regressions without compatible before/after Semantic Diff evidence.
  - Creating a second spawn-boss classifier instead of consuming canonical rewardBossLiteral evidence.
changed_paths:
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-012-critical-access-integrity.md
  - docs/ai-agent/OTBM_CRITICAL_ACCESS_INTEGRITY.md
  - docs/ai-agent/OTBM_CRITICAL_ACCESS_INTEGRITY.schema.json
  - docs/ai-agent/OTBM_CRITICAL_ACCESS_TARGETS.schema.json
  - tools/ai-agent/otbm_critical_access_integrity.py
  - tools/ai-agent/otbm_critical_access_integrity_tool.py
  - tools/ai-agent/test_otbm_critical_access_integrity.py
  - tools/ai-agent/test_otbm_critical_access_integrity_output_safety.py
  - tools/ai-agent/test_otbm_critical_access_integrity_schema.py
validation:
  - command: GitHub Actions CI run 29915417926
    result: PASS
    evidence: repository CI passed on pre-final head 2f99d69428ed11f9da4698a1282d6f17c1e5d09f.
  - command: GitHub Actions Agent Task Ownership run 29915417736
    result: PASS
    evidence: ownership validation passed on pre-final head.
  - command: GitHub Actions OTBM Map Tools run 29915417711
    result: PASS
    evidence: focused OTBM schema and test validation passed on pre-final head.
  - command: GitHub Actions AI Agent Tools run 29915417815
    result: PASS
    evidence: full AI-agent validation passed on pre-final head.
  - command: changed-path and shared-doc audit
    result: PASS
    evidence: exactly eleven declared changed paths; MODULE_CATALOG and CHANGELOG patches contain only intended QA-012 additions.
  - command: review and mergeability audit
    result: PASS
    evidence: zero review threads, zero review submissions, mergeable=true, current main unchanged from branch base.
blockers: []
next_action: Make no further commits. Verify all required workflows on the exact final checkpoint head, update PR evidence, mark ready, enable auto-merge, verify squash merge and complete active-to-archive lifecycle closure before starting QA-013.
```
