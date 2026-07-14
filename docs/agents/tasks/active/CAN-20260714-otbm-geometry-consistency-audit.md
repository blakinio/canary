---
task_id: CAN-20260714-otbm-geometry-consistency-audit
program_id: ""
coordination_id: "OTS-OTBM-VALIDATION"
status: active
agent: "GPT-5.6 Thinking"
branch: feat/otbm-geometry-consistency-audit
base_branch: main
created: 2026-07-14T10:35:00+02:00
updated: 2026-07-14T11:05:00+02:00
last_verified_commit: "39aa6c5940ddd21f9935172dfde32f979942ea1d"
risk: medium
related_issue: ""
related_pr: "#320"
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
  shared:
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/ACTIVE_WORK.md
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
- [x] Register the reusable module in `MODULE_CATALOG.md` after #318 released ownership.
- [ ] Update changelog after #319 releases ownership and update the authoritative roadmap.
- [ ] Verify final changed-file scope, synchronized current-main state, current-head CI, Required and zero review threads.
- [ ] Squash-merge and archive this task separately.

# Delivered contracts and behavior

- Report: `canary-otbm-geometry-audit-v1`.
- Reviewed adjacency rules: `canary-otbm-geometry-rules-v1`.
- Factual render requests: `canary-otbm-geometry-audit-render-v1`.
- Bounded World Index region iteration through existing area postings; the full world is not materialized or scanned tile-by-tile.
- Exact missing-floor, duplicate-ground, unknown-appearance, small component, house-component, verified-PZ and reviewed adjacency evidence.
- Low-confidence invisible-blocker candidates require direct `unpassable` evidence plus absence of any nonzero decoded sprite ID; pixels/runtime are not claimed.
- Finding IDs, totals, samples, confidence, scope-boundary uncertainty and truncation are deterministic for exact inputs.
- Inputs and outputs are artifact-root confined; direct symlinks, path escape, oversized input and accidental overwrite fail closed; JSON writes are atomic.
- Optional render-manifest output is now confined through the same artifact-root resolver before writing.
- No wall or border rule is inferred from names, sprite appearance or proximity.

# Confirmed context

- Original task base: `main` `e71630db609e03417ac61725fc5695dbe04d92b6`, after Phase 6 lifecycle merge #315.
- Current `main` includes Real Tibia parity governance #318 at `8dd09bddbc7a492660472e29ef576578691f3d91`; the catalogue update in this branch preserves that current-main content.
- Phase 7 is the next roadmap phase; Phase 8 remains blocked by this geometry gate.
- Open PR #319 exclusively owns the bounded Semantic Diff iterator fix and `CHANGELOG.md`; this task does not edit its source/test/task paths or changelog while it remains open.
- Open PR #316 is a separate bounded Targuna donor-evidence audit with no Phase 7 implementation ownership.
- Current Remere's Map Editor source defines `TILESTATE_PROTECTIONZONE = 0x0001`; no other tile-flag meaning is assumed.
- Local Git remains unavailable after the previously recorded one-time DNS failure. Repository operations and validation use GitHub API and GitHub Actions; no local checkout result is claimed.

# Existing work reused

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Unified OTBM World Index | Exact bounded tile/item/house/flag/mechanic evidence and area postings | `tools/ai-agent/otbm_world_index.py` | Avoids a second OTBM parser and whole-world iteration. |
| Reachability tile classifier | Ground, blocker, unknown-appearance and strict/optimistic semantics | `tools/ai-agent/otbm_reachability_transition.py` | Keeps one appearance/walkability policy. |
| Appearances index | Object flags and sprite-ID metadata | `tools/ai-agent/otbm_appearances.py` | Supports factual ground/blocker/sprite evidence. |
| Factual OTBM renderer | Real map/client-asset render path | `tools/ai-agent/otbm_renderer.py`, `otbm_render_tool.py` | No competing renderer or AI imagery. |
| Semantic OTBM Diff #311/#319 | Independent comparison contract only | `tools/ai-agent/otbm_semantic_diff*.py` | Phase 7 audits one selected map region and does not overlap the active ordering repair. |

# Ownership and overlap

- Open OTBM PRs inspected: #316 and #319.
- Governance PR #318 merged and released `MODULE_CATALOG.md`; its current-main entries were preserved exactly before adding the Phase 7 row.
- Exclusive claims remain limited to new Phase 7 modules, tests, schemas, docs, ADR, workflow and task record.
- Shared claim currently contains only `MODULE_CATALOG.md`.
- `CHANGELOG.md` remains read-only while #319 is open.
- `ACTIVE_WORK.md`, existing World Index/reachability/Semantic Diff modules and upstream repositories remain read-only.
- Local ownership checker is unavailable without checkout; live task records, PR file lists and GitHub branch state were inspected directly. GitHub Agent Task Ownership is green on validated implementation heads.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Region is mandatory and capped at 1,000,000 coordinates. | Component analysis must remain bounded and reviewable; full-world materialization is unsafe. | `ADR-20260714-otbm-geometry-evidence-boundary.md` |
| PZ mask is exactly `0x0001`. | Verified in current read-only Remere's Map Editor `source/tile.h`; other raw flags remain uninterpreted. | same ADR |
| Wall/border checks require explicit adjacency rules. | Item names, sprites and visual memory do not prove intended edge connectivity. | same ADR |
| Invisible blocker is only a low-confidence candidate when unpassable evidence exists but no nonzero sprite ID exists. | Direct metadata evidence is not pixel/runtime proof. | same ADR |
| Small/disconnected components are review candidates, not automatic gameplay defects. | Teleports, scripts and out-of-scope map areas can provide runtime connectivity. | same ADR |

# Validation and CI

## Failure history and repair

- Initial dedicated run `29319415323`, job `87040890744`, failed during focused tests before compilation/schema steps.
- Diagnostic workflow commit retained full test output in artifact `8305301685`, digest `sha256:765e9eb0ff0965f54990ff64abbaf5db5d6e479c2e6a185be902c8b95f7aa790`.
- The only cause was the existing synthetic-fixture edge: maps with no node-item reported scanner `maxItemDepth=-1`, while the binary index represents `0`.
- Test fixtures were repaired with one neutral known nested item. No production contract or fail-closed validation was weakened.

## Validated implementation head

Head `69658ddabf74b4202ef7ee896e2262c67d7224a8`:

- OTBM Geometry Audit run `29319667799`: success.
- `Validate bounded geometry evidence` job `87041720844`: success.
- All 21 focused tests: success.
- Python compilation: success.
- Both schema syntax checks and representative `jsonschema` validation: success.
- Representative synthetic map/index/report and reviewed rules: success.
- Forbidden generated `.otbm`, `.widx`, `.png` and appearances binary publication check: success.
- Toolkit/report artifact publication: success.
- Agent Task Ownership `29319667792`: success.
- OTBM Map Tools `29319667803`: success.
- AI Agent Tools `29319667808`: success.
- repository CI `29319667975`: success; Required job `87041773144`: success.

Subsequent heads add only artifact-root confinement for the render-manifest output, bounded area-posting iteration, current-main-preserving catalogue registration and this handoff update. Their current-head workflows must pass before readiness.

# Risks and compatibility

- Runtime: none; offline read-only tooling.
- Data/migration: none; source map and external binaries remain unchanged.
- Security: artifact-root confinement, bounded inputs, no Lua execution and no shell-derived map semantics.
- Backward compatibility: consumes existing versioned World Index/appearances contracts without changing them.
- Cross-repo rollout: none; upstream repositories remain read-only.
- Rollback: revert the eventual squash merge; no persistence or map cleanup.

# Remaining work

1. Let current-head workflows complete and repair only evidence-backed failures.
2. Wait for #319 to release `CHANGELOG.md`, then add the narrow Phase 7 changelog entry.
3. Update the authoritative roadmap from current `main` without overwriting concurrent content.
4. Verify final scope/diff, synchronize with current main, mark ready, pass ready-state Required and squash-merge.
5. Archive Phase 7 in a separate lifecycle PR before Phase 8 starts.

# Handoff

## Start here

Read this task, `docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md`, `OTBM_GEOMETRY_AUDIT.md`, the ADR and active #316/#319 task records.

## Do not repeat

Do not parse or write OTBM, duplicate walkability, infer wall/border meaning from names/sprites, guess unverified tile flags, modify private maps or use AI image generation. Do not reintroduce whole-world tile iteration for bounded geometry analysis.

## Open question

- Only the timing of shared changelog/roadmap finalization remains; no geometry contract is unresolved.

# Completion

- Final status: active
- PR: #320
- Merge commit:
- Program record updated: not applicable
- Catalogue updated: active delivery row on feature branch
- Changelog updated: pending #319 ownership release
- Archived at:
