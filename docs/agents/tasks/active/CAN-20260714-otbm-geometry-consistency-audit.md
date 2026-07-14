---
task_id: CAN-20260714-otbm-geometry-consistency-audit
program_id: ""
coordination_id: "OTS-OTBM-VALIDATION"
status: active
agent: "GPT-5.6 Thinking"
branch: feat/otbm-geometry-consistency-audit
base_branch: main
created: 2026-07-14T10:35:00+02:00
updated: 2026-07-14T10:35:00+02:00
last_verified_commit: "e71630db609e03417ac61725fc5695dbe04d92b6"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - "merged and archived Unified OTBM World Index #219/#223"
  - "merged and archived OTBM reachability validator #274/#277"
  - "merged and archived Semantic OTBM Diff #311/#315"
blocks:
  - "Phase 8 safe bounded OTBM patch writer"
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_geometry_audit.py
    - tools/ai-agent/otbm_geometry_audit_types.py
    - tools/ai-agent/otbm_geometry_audit_analysis.py
    - tools/ai-agent/otbm_geometry_audit_render.py
    - tools/ai-agent/otbm_geometry_audit_tool.py
    - tools/ai-agent/test_otbm_geometry_audit.py
    - docs/ai-agent/OTBM_GEOMETRY_AUDIT.md
    - docs/ai-agent/OTBM_GEOMETRY_AUDIT.schema.json
    - docs/ai-agent/OTBM_GEOMETRY_RULES.schema.json
    - docs/agents/decisions/ADR-20260714-otbm-geometry-evidence-boundary.md
    - .github/workflows/otbm-geometry-audit.yml
    - docs/agents/tasks/active/CAN-20260714-otbm-geometry-consistency-audit.md
  shared: []
  read_only:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
    - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
    - tools/ai-agent/otbm_item_audit_scan.cpp
    - tools/ai-agent/otbm_world_index.py
    - tools/ai-agent/otbm_reachability_transition.py
    - tools/ai-agent/otbm_reachability_types.py
    - tools/ai-agent/otbm_semantic_diff_analysis.py
    - tools/ai-agent/test_otbm_semantic_diff.py
modules_touched:
  - OTBM geometry and consistency audit
reuses:
  - canary-otbm-world-index-v1
  - canary-appearances-index-v1
  - Phase 3 tile classifier
  - existing factual OTBM renderer
public_interfaces:
  - canary-otbm-geometry-audit-v1
  - canary-otbm-geometry-rules-v1
  - canary-otbm-geometry-audit-render-v1
  - OTBM geometry audit CLI
cross_repo_tasks: []
---

# Goal

Deliver Phase 7 as a deterministic, bounded, read-only geometry and consistency audit over the canonical World Index and appearances evidence, with exact positions, explicit confidence/evidence boundaries and factual render requests through the existing renderer.

# Acceptance criteria

- [ ] Require one explicit inclusive 3D region bounded to at most 1,000,000 coordinates.
- [ ] Reuse `canary-otbm-world-index-v1`; do not parse OTBM independently.
- [ ] Reuse the Phase 3 appearance/tile classifier; do not create another walkability engine.
- [ ] Detect tiles and item placements without confirmed ground.
- [ ] Detect suspicious multiple confirmed ground placements without claiming every layered case is defective.
- [ ] Detect bounded cardinal tile components and report small isolated/orphan candidates with scope-boundary uncertainty.
- [ ] Detect disconnected components for one exact house ID and mixed PZ state inside one house component.
- [ ] Use the verified OTBM protection-zone flag mask `0x0001`; preserve all other flags without invented meanings.
- [ ] Detect confirmed unpassable appearances with no nonzero sprite-ID evidence as low-confidence invisible-blocker candidates.
- [ ] Support reviewed wall/border adjacency rules through `canary-otbm-geometry-rules-v1`; emit no visual-style finding without a supplied rule.
- [ ] Emit exact totals, bounded samples, stable finding IDs, confidence levels and explicit truncation.
- [ ] Add deterministic factual render requests through the existing renderer only; no AI-generated imagery.
- [ ] Add provenance/hash/version checks, path confinement, size limits, overwrite protection, symlink rejection and atomic JSON output.
- [ ] Add schemas, documentation, ADR, focused tests and dedicated CI/artifacts.
- [ ] Keep `.otbm`, `.widx`, appearances binaries, assets, generated reports and renders outside Git.
- [ ] Confirm no map, datapack, gameplay, protocol, database, item or OTClient change.
- [ ] Update catalogue/changelog/roadmap only after current shared-path owners #318/#319 are resolved.
- [ ] Verify final changed-file scope, current-head CI, Required and zero review threads.
- [ ] Squash-merge and archive this task separately.

# Confirmed context

- Current task base is `main` `e71630db609e03417ac61725fc5695dbe04d92b6`, after Phase 6 lifecycle merge #315.
- Phase 7 is the exact next roadmap phase; Phase 8 remains blocked by this geometry gate.
- Current open OTBM PR #319 exclusively owns the bounded Semantic Diff iterator fix and its tests/changelog; this task does not edit those paths.
- Current open Targuna PR #316 is a separate donor-evidence audit and owns only its audit paths/reports.
- Current governance PR #318 has shared ownership of `MODULE_CATALOG.md` and `CHANGELOG.md`; both remain read-only here until its lifecycle is resolved.
- The native scanner/World Index already preserve exact tile position, kind, house ID, raw flags, placements and mechanic attributes.
- Current Remere's Map Editor source defines `TILESTATE_PROTECTIONZONE = 0x0001`; no other tile-flag meaning is assumed without direct source evidence.
- Local Git is unavailable after the previously recorded one-time DNS failure. Repository operations and validation use GitHub API and GitHub Actions; no local checkout result will be claimed.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Unified OTBM World Index | Exact bounded tile/item/house/flag/mechanic evidence | `tools/ai-agent/otbm_world_index.py` | Avoids a second OTBM parser. |
| Reachability tile classifier | Ground, blocker, unknown-appearance and strict/optimistic semantics | `tools/ai-agent/otbm_reachability_transition.py` | Keeps one appearance/walkability policy. |
| Appearances index | Object flags and sprite-ID metadata | `tools/ai-agent/otbm_appearances.py` | Supports factual ground/blocker/sprite evidence. |
| Factual OTBM renderer | Real map/client-asset render path | `tools/ai-agent/otbm_renderer.py`, `otbm_render_tool.py` | No competing renderer or AI imagery. |
| Semantic OTBM Diff #311/#319 | Optional future comparison context only | `tools/ai-agent/otbm_semantic_diff*.py` | This task audits one selected map region and does not overlap the active bounded-order fix. |

# Ownership and overlap check

- Open OTBM PRs inspected: #316 and #319.
- Shared documentation owner inspected: #318.
- Exclusive claims: only new Phase 7 modules, tests, schemas, docs, ADR, workflow and this task.
- Shared claims: none during implementation bootstrap.
- Read-only dependencies: existing scanner/index/reachability/semantic-diff modules and shared documentation.
- Overlap resolution: do not edit #318/#319 paths; add shared catalogue/changelog/roadmap updates only after fresh ownership validation.
- Local ownership checker: unavailable without checkout; GitHub task files, PR changed-file lists and live branch state were inspected directly.

# Current state

Phase 7 task and branch claimed. No implementation, generated artifact or map change exists yet.

# Plan

1. Fix the versioned report, rules-manifest and render-manifest contracts.
2. Implement bounded evidence loading, geometry analyses and deterministic output.
3. Add focused synthetic OTBM/index/appearance tests and permanent dedicated CI.
4. Open a draft PR early, then iterate from workflow evidence until green.
5. Recheck shared ownership, update durable indexes, review exact diff, mark ready and merge.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Region is mandatory and capped at 1,000,000 coordinates. | Component analysis must remain bounded and reviewable; full-world materialization is unsafe. | planned |
| PZ mask is exactly `0x0001`. | Verified in current read-only Remere's Map Editor `source/tile.h`; other raw flags remain uninterpreted. | planned |
| Wall/border checks require explicit adjacency rules. | Item names, sprites and visual memory do not prove intended edge connectivity. | planned |
| Invisible blocker is only a low-confidence candidate when unpassable evidence exists but no nonzero sprite ID exists. | This is direct metadata evidence, not pixel/runtime proof. | planned |
| Small/disconnected components are review candidates, not automatic gameplay defects. | Teleports, scripts and out-of-scope map areas can provide runtime connectivity. | planned |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| pending | focused Phase 7 tests | not-run | Must use synthetic OTBM through the existing native scanner/World Index. |
| pending | Python compilation and schema validation | not-run | Dedicated workflow. |
| pending | repository CI / Required | not-run | Current final head only. |

# Risks and compatibility

- Runtime: none; offline read-only tooling.
- Data/migration: none; source map and external binaries remain unchanged.
- Security: artifact-root confinement, bounded inputs, no Lua execution, no shell-derived map semantics.
- Backward compatibility: consumes existing versioned reports/indexes without changing them.
- Cross-repo rollout: none; upstream repositories remain read-only.
- Rollback: revert the eventual squash merge; no persistence or map cleanup.

# Remaining work

1. Implement and validate the fixed contracts.

# Handoff

## Start here

Read this task, `docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md`, Phase 1/3/6 docs and the active #316/#319 task records.

## Do not repeat

Do not parse or write OTBM, duplicate walkability, infer wall/border meaning from names/sprites, guess tile flags, modify the private map or use AI image generation.

## Open questions

- Shared catalogue/changelog/roadmap updates wait for current owners #318/#319 to merge or release those paths.

# Completion

- Final status: active
- PR:
- Merge commit:
- Program record updated: not applicable
- Catalogue updated: pending ownership release
- Changelog updated: pending ownership release
- Archived at:
