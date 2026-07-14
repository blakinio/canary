---
task_id: CAN-20260714-otbm-geometry-consistency-audit
program_id: ""
coordination_id: "OTS-OTBM-VALIDATION"
status: ready-for-review
agent: "GPT-5.6 Thinking"
branch: feat/otbm-geometry-consistency-audit-refresh
base_branch: main
created: 2026-07-14T10:35:00+02:00
updated: 2026-07-14T11:25:00+02:00
last_verified_commit: "d9a363f5e9bae46de8e96edcca06665de697ef88"
risk: medium
related_issue: ""
related_pr: "#322"
depends_on:
  - "merged and archived Unified OTBM World Index #219/#223"
  - "merged and archived OTBM reachability validator #274/#277"
  - "merged and archived Semantic OTBM Diff #311/#315"
  - "merged bounded Semantic OTBM Diff ordering fix #319"
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
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
    - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
  read_only:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/ACTIVE_WORK.md
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

- [x] Require one explicit inclusive 3D region bounded to at most 1,000,000 coordinates.
- [x] Reuse `canary-otbm-world-index-v1`; do not parse OTBM independently.
- [x] Reuse the Phase 3 appearance/tile classifier; do not create another walkability engine.
- [x] Detect tiles and item placements without confirmed ground.
- [x] Detect suspicious multiple confirmed ground placements without claiming every layered case is defective.
- [x] Detect bounded cardinal tile components and report small isolated/orphan candidates with scope-boundary uncertainty.
- [x] Detect disconnected components for one exact house ID and mixed PZ state inside one house component.
- [x] Use the verified OTBM protection-zone flag mask `0x0001`; preserve all other flags without invented meanings.
- [x] Detect confirmed unpassable appearances with no nonzero sprite-ID evidence as low-confidence invisible-blocker candidates.
- [x] Support reviewed wall/border adjacency rules through `canary-otbm-geometry-rules-v1`; emit no visual-style finding without a supplied rule.
- [x] Emit exact totals, bounded samples, stable finding IDs, confidence levels and explicit truncation.
- [x] Add deterministic factual render requests through the existing renderer only; no AI-generated imagery.
- [x] Add provenance/hash/version checks, path confinement, size limits, overwrite protection, symlink rejection and atomic JSON output.
- [x] Add schemas, documentation, ADR, 21 focused tests and dedicated CI/artifacts.
- [x] Keep `.otbm`, `.widx`, appearances binaries, assets, generated reports and renders outside Git.
- [x] Confirm no map, datapack, gameplay, protocol, database, item or OTClient change.
- [x] Restore the validated Phase 7 implementation onto a clean current-main branch.
- [x] Update catalogue, changelog and roadmap from current `main` without unrelated diffs.
- [x] Verify the exact 15-file scope, clean current-main comparison, draft-state CI, Required and zero unrelated/forbidden paths.
- [ ] Mark #322 ready, verify ready-state checks and zero review threads, then squash-merge.
- [ ] Archive this task separately before Phase 8 starts.

# Delivered contracts and behavior

- Report: `canary-otbm-geometry-audit-v1`.
- Reviewed adjacency rules: `canary-otbm-geometry-rules-v1`.
- Factual render requests: `canary-otbm-geometry-audit-render-v1`.
- Bounded World Index region iteration through existing area postings; the full world is not materialized or scanned tile-by-tile.
- Exact missing-floor, duplicate-ground, unknown-appearance, small component, house-component, verified-PZ and reviewed adjacency evidence.
- Low-confidence invisible-blocker candidates require direct `unpassable` evidence plus absence of any nonzero decoded sprite ID; pixels/runtime are not claimed.
- Finding IDs, totals, samples, confidence, scope-boundary uncertainty and truncation are deterministic for exact inputs.
- Inputs and outputs are artifact-root confined; direct symlinks, path escape, oversized input and accidental overwrite fail closed; JSON writes are atomic.
- Optional render-manifest output is confined through the same artifact-root resolver before writing.
- No wall or border rule is inferred from names, sprite appearance or proximity.

# Clean branch replacement

- Original draft #320 was created before shared-document advances from #318/#319 and validated the implementation.
- Its old merge-base caused GitHub to attribute preserved current-main catalogue lines to Phase 7.
- No force-push, history rewrite or partial synthetic merge was used.
- Replacement branch `feat/otbm-geometry-consistency-audit-refresh` was created directly from current main `b6a6b3d8e851409de448f4e621df909cb041d05a` after #319 merged.
- Validated implementation blobs were copied exactly, then current-main catalogue/changelog/roadmap were updated narrowly.
- Historical #320 was commented and closed without merge; #322 is the only active Phase 7 delivery PR.

# Confirmed context

- Phase 7 is the next roadmap phase; Phase 8 remains blocked by this geometry gate.
- PR #319 merged the bounded Semantic Diff area-ordering repair and released `CHANGELOG.md`.
- PR #316 remains a separate bounded Targuna donor-evidence audit with no Phase 7 implementation ownership.
- Current Remere's Map Editor source defines `TILESTATE_PROTECTIONZONE = 0x0001`; no other tile-flag meaning is assumed.
- Local Git remains unavailable after the previously recorded one-time DNS failure. Repository operations and validation use GitHub API and GitHub Actions; no local checkout result is claimed.

# Existing work reused

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Unified OTBM World Index | Exact bounded tile/item/house/flag/mechanic evidence and area postings | `tools/ai-agent/otbm_world_index.py` | Avoids a second OTBM parser and whole-world iteration. |
| Reachability tile classifier | Ground, blocker, unknown-appearance and strict/optimistic semantics | `tools/ai-agent/otbm_reachability_transition.py` | Keeps one appearance/walkability policy. |
| Appearances index | Object flags and sprite-ID metadata | `tools/ai-agent/otbm_appearances.py` | Supports factual ground/blocker/sprite evidence. |
| Factual OTBM renderer | Real map/client-asset render path | `tools/ai-agent/otbm_renderer.py`, `otbm_render_tool.py` | No competing renderer or AI imagery. |
| Semantic OTBM Diff #311/#319 | Independent comparison contract and corrected bounded area ordering | `tools/ai-agent/otbm_semantic_diff*.py` | Phase 7 uses World Index region iteration but does not overlap Semantic Diff implementation. |

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Region is mandatory and capped at 1,000,000 coordinates. | Component analysis must remain bounded and reviewable; full-world materialization is unsafe. | `ADR-20260714-otbm-geometry-evidence-boundary.md` |
| PZ mask is exactly `0x0001`. | Verified in current read-only Remere's Map Editor `source/tile.h`; other raw flags remain uninterpreted. | same ADR |
| Wall/border checks require explicit adjacency rules. | Item names, sprites and visual memory do not prove intended edge connectivity. | same ADR |
| Invisible blocker is only a low-confidence candidate when unpassable evidence exists but no nonzero sprite ID exists. | Direct metadata evidence is not pixel/runtime proof. | same ADR |
| Small/disconnected components are review candidates, not automatic gameplay defects. | Teleports, scripts and out-of-scope map areas can provide runtime connectivity. | same ADR |

# Validation history

## Failure and repair on superseded draft

- Initial dedicated run `29319415323`, job `87040890744`, failed during focused tests before compilation/schema steps.
- Diagnostic artifact `8305301685` proved the only cause was the existing synthetic-fixture edge: maps with no node-item reported scanner `maxItemDepth=-1`, while the binary index represents `0`.
- Test fixtures were repaired with one neutral known nested item. No production contract or fail-closed validation was weakened.
- Superseded implementation head `69658ddabf74b4202ef7ee896e2262c67d7224a8` then passed the dedicated workflow, all 21 tests, ownership, map tools, AI tools and repository Required.

## Clean replacement draft-state validation

Head `d9a363f5e9bae46de8e96edcca06665de697ef88`:

- OTBM Geometry Audit run `29321325585`: success.
- `Validate bounded geometry evidence` job `87047089681`: success.
- All 21 focused tests: success.
- Python compilation: success.
- Both schema syntax checks and representative `jsonschema`: success.
- Synthetic map/index/report, reviewed-rules validation and forbidden generated-artifact check: success.
- Toolkit/report artifact publication: success.
- Agent Task Ownership run `29321325508`: success.
- OTBM Map Tools run `29321325546`: success.
- AI Agent Tools run `29321325460`: success.
- repository CI run `29321325680`: success.
- Required job `87047140975`: success.
- Branch comparison: exactly 15 expected paths, ahead and behind by 0 at verification.

The current task-record readiness commit must pass its own final checks before merge.

# Risks and compatibility

- Runtime: none; offline read-only tooling.
- Data/migration: none; source map and external binaries remain unchanged.
- Security: artifact-root confinement, bounded inputs, no Lua execution and no shell-derived map semantics.
- Backward compatibility: consumes existing versioned World Index/appearances contracts without changing them.
- Cross-repo rollout: none; upstream repositories remain read-only.
- Rollback: revert the eventual squash merge; no persistence or map cleanup.

# Remaining work

1. Verify checks on this final task-record head.
2. Review exact diff and zero review threads.
3. Mark #322 ready, verify ready-state Required and squash-merge with expected-head guard.
4. Archive Phase 7 in a separate lifecycle PR before Phase 8 starts.

# Completion

- Final status: ready-for-review
- PR: #322
- Final feature head: pending final readiness checks
- Merge commit:
- Program record updated: not applicable
- Catalogue updated: active delivery row
- Changelog updated: Unreleased Phase 7 entry
- Archived at:
