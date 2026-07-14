---
task_id: CAN-20260714-otbm-semantic-diff
program_id: ""
coordination_id: "OTS-OTBM-VALIDATION"
status: ready-for-review
agent: "GPT-5.6 Thinking"
branch: feat/otbm-semantic-diff
base_branch: main
created: 2026-07-14T09:10:00+02:00
updated: 2026-07-14T10:05:00+02:00
last_verified_commit: "ebd1767a6094ba68972fdcbdf814c0ce967267ec"
risk: medium
related_issue: ""
related_pr: "#311"
depends_on:
  - "merged and archived Unified OTBM World Index #219/#223"
  - "merged and archived Quest Map Validator #225/#236"
  - "merged and archived OTBM reachability validator #274/#277"
  - "merged and archived OTBM spawn/NPC validator #286/#290"
  - "merged and archived OTBM storage dependency graph #299/#309"
blocks:
  - "Phase 7 geometry and consistency audit"
  - "Phase 8 safe bounded OTBM patch writer"
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_semantic_diff.py
    - tools/ai-agent/otbm_semantic_diff_types.py
    - tools/ai-agent/otbm_semantic_diff_analysis.py
    - tools/ai-agent/otbm_semantic_diff_render.py
    - tools/ai-agent/otbm_semantic_diff_tool.py
    - tools/ai-agent/test_otbm_semantic_diff.py
    - docs/ai-agent/OTBM_SEMANTIC_DIFF.md
    - docs/ai-agent/OTBM_SEMANTIC_DIFF.schema.json
    - docs/agents/decisions/ADR-20260714-otbm-semantic-diff-evidence-boundary.md
    - .github/workflows/otbm-semantic-diff.yml
    - docs/agents/tasks/active/CAN-20260714-otbm-semantic-diff.md
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
    - tools/ai-agent/otbm_world_index_tool.py
    - tools/ai-agent/quest_map_validation.py
    - tools/ai-agent/quest_map_validation_tool.py
    - tools/ai-agent/otbm_script_resolution.py
    - tools/ai-agent/otbm_reachability.py
    - tools/ai-agent/otbm_reachability_types.py
    - tools/ai-agent/otbm_reachability_transition.py
    - tools/ai-agent/otbm_spawn_npc.py
    - tools/ai-agent/otbm_spawn_npc_validation.py
    - tools/ai-agent/otbm_storage_graph.py
    - tools/ai-agent/otbm_render_tool.py
    - tools/ai-agent/otbm_renderer.py
modules_touched:
  - Semantic OTBM Diff
reuses:
  - canary-otbm-world-index-v1
  - canary-otbm-world-query-v1
  - canary-otbm-reachability-v1
  - canary-quest-map-validation-v1
  - canary-otbm-spawn-npc-validation-v1
  - canary-otbm-storage-graph-v1
  - existing factual OTBM renderer
public_interfaces:
  - canary-otbm-semantic-diff-v1
  - canary-otbm-semantic-diff-render-v1
  - OTBM semantic diff CLI
cross_repo_tasks: []
---

# Goal

Deliver Phase 6 as a deterministic read-only semantic diff between two canonical World Index inputs, reusing the existing native scanner, Phase 3 walkability semantics and factual renderer without creating a second parser, pathfinder or renderer.

# Preflight

- Original branch base: `f4e5371906d3b4a33229db2dce6b25d44fb813f0`, after Phase 5 lifecycle merge #309.
- No existing Semantic OTBM Diff task, branch, implementation or open OTBM PR was found.
- Unrelated open PRs had no declared OTBM ownership overlap.
- `ACTIVE_WORK.md` is read-only and was not added to owned paths.
- Upstream `opentibiabr/*` is read-only.

# Fixed contract

- Report: `canary-otbm-semantic-diff-v1`.
- Factual render manifest: `canary-otbm-semantic-diff-render-v1`.
- Tile identity: exact `x,y,z`.
- Aligned item base: exact `(itemId,itemDepth,source)`.
- Exact item evidence retains action ID, unique ID, house-door ID and teleport destination.
- Pure exact-multiset reorder emits `stack-order-changed` without add/remove.
- Other stack edits use a deterministic minimum edit script with fixed `replace`, `remove`, `add` tie order.
- No fuzzy item matching, neighboring-position inference or gameplay-intent inference.
- Walkability calls existing Phase 3 `otbm_reachability_transition._classify_tile`; no copied engine.
- Correlation uses exact positions/literal mechanics only in explicitly supplied, format-validated Phase 2, script-resolution, Phase 3, Phase 4 and Phase 5 reports.
- Factual visual evidence calls `otbm_renderer.render_region` or emits exact `otbm_render_tool.py` commands. No new renderer or AI image generation.

# Final feature scope before ready state

Exactly 14 changed files were verified through the GitHub PR file list, branch comparison and patch review:

1. `.github/workflows/otbm-semantic-diff.yml`
2. `docs/agents/CHANGELOG.md`
3. `docs/agents/MODULE_CATALOG.md`
4. `docs/agents/decisions/ADR-20260714-otbm-semantic-diff-evidence-boundary.md`
5. `docs/agents/tasks/active/CAN-20260714-otbm-semantic-diff.md`
6. `docs/ai-agent/OTBM_SEMANTIC_DIFF.md`
7. `docs/ai-agent/OTBM_SEMANTIC_DIFF.schema.json`
8. `docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md`
9. `tools/ai-agent/otbm_semantic_diff.py`
10. `tools/ai-agent/otbm_semantic_diff_analysis.py`
11. `tools/ai-agent/otbm_semantic_diff_render.py`
12. `tools/ai-agent/otbm_semantic_diff_tool.py`
13. `tools/ai-agent/otbm_semantic_diff_types.py`
14. `tools/ai-agent/test_otbm_semantic_diff.py`

Confirmed absent from the feature diff:

- `docs/agents/ACTIVE_WORK.md`;
- `.otbm` and `.widx` files;
- `items.otb`, appearances binaries and client assets;
- generated JSON reports and render images;
- datapack, gameplay, map, OTClient and upstream repository changes.

# Delivered behavior

- Existing World Index reader validates binary structure.
- Index, manifest, source and scanner SHA-256/size provenance is verified.
- Incompatible World Index/scanner-build/OTBM/item versions fail closed.
- Full-index and inclusive bounded-region comparisons stream exact tile order.
- Tile kind, flags, house ID, ground, item stacks, AID, UID, house door and teleport changes are separate.
- Phase 3 strict/optimistic/blocked/conditional, blocker and unknown-appearance changes are preserved.
- Exact selected-scope totals remain global to the chosen scope while samples are bounded and explicitly truncated.
- Stable finding IDs are independent of optional correlation.
- Optional reports add conservative selected-scope evidence; missing correlation never proves global non-use.
- Render manifests pair factual before/after/context requests through the existing renderer.
- Paths are artifact-root confined; direct symlinks, accidental overwrite and oversized inputs/outputs are rejected.
- JSON output is atomic.
- Optional real maps are hash-verified only and remain unchanged.

# Focused tests

Thirty tests cover identical inputs; tile add/remove/flags/house/ground; item add/remove/reorder; AID/UID/house-door/teleport changes; strict and conditional walkability; unknown appearances; bounded scope; exact truncated totals; determinism; corrupt/incompatible provenance; overwrite/symlink safety; Phase 2–5 correlation; missing optional reports; existing renderer integration; and source-map immutability.

Local isolated checks without a checkout:

- Phase 6 Python compilation: passed.
- Schema JSON syntax: passed.

These are isolated-file checks, not a local repository test run.

# CI history and fixes

- Run `29314876746`, job `87026487592`: scanner compile succeeded; focused tests failed before diagnostics were visible.
- Run `29315020741`, artifact `8303572057`: fixture class field `build` shadowed the fixture-building method; render test used a `str` where its API declared `Path`. Fixed at `0705f8fa73e83ece14c83b3438648af1295256bd`.
- Run `29315132001`, job `87027296193`, artifact `8303618450`: 28/30 tests passed; two no-child synthetic maps exposed the existing fixture/index `maxItemDepth -1` versus binary `0` limitation, and the programmatic facade did not normalize string paths. Production path normalization was fixed at `2efb61c77c611f71f8cb736017044a4f623882e1`; the two walkability fixtures now retain the same neutral child item on both sides.
- Run `29315508600`, job `87028506652`: success. All 30 focused tests, native scanner compilation, synthetic map/index builds, repeated byte-identical semantic diff, Python compilation, schema syntax, representative `jsonschema`, forbidden-artifact removal and toolkit/report publication succeeded.
- Implementation head `f5d540b4d88955481909c76f9abcf7588e44559e`: OTBM Map Tools `29315508420`, Agent Task Ownership `29315508487` and repository CI `29315508700` succeeded.

# Synchronization and pre-ready verification

`main` advanced independently to `82348f9faca788a8cbb5c13feb75b4e06d8da9dc`. It was merged without force into the feature branch as `ebd1767a6094ba68972fdcbdf814c0ce967267ec`, preserving current-main changes and overlaying only the 14 verified Phase 6 paths.

Post-merge comparison: `behind_by: 0`; exact feature scope remained 14 files.

Head `ebd1767a6094ba68972fdcbdf814c0ce967267ec`:

- OTBM Semantic Diff run `29316022761`: success; job `87030142680` (`Validate semantic map evidence`): success.
- Agent Task Ownership run `29316022790`: success.
- AI Agent Tools run `29316022768`: success.
- OTBM Map Tools run `29316022769`: success.
- repository CI run `29316022958`: success.
- Required job `87030194820`: success.
- autofix.ci run `29316022795`: skipped because no autofix was required.

The successful synthetic workflow proves the tested contract only. It is not runtime/gameplay proof. A real two-map comparison was not run because only one historical private map provenance was available; no second map was fabricated or modified.

# Acceptance criteria

- [x] Reuse canonical World Index/native scanner without parsing OTBM independently.
- [x] Verify provenance and fail closed on corrupt/incompatible inputs.
- [x] Report deterministic tile, stack and mechanic changes with exact positions/indices.
- [x] Reuse Phase 3 walkability semantics without a second engine.
- [x] Support full and bounded inclusive 3D scopes.
- [x] Preserve exact totals, bounded samples, stable IDs and truncation state.
- [x] Provide conservative optional Phase 2–5/script correlation.
- [x] Integrate factual render evidence through the existing renderer.
- [x] Provide atomic output, overwrite/symlink/path/size safety.
- [x] Add schema, docs, ADR, 30 tests and dedicated workflow/artifacts.
- [x] Update MODULE_CATALOG, CHANGELOG and authoritative roadmap.
- [x] Keep OTBM, WIDX, appearances, assets, large generated reports and renders outside Git.
- [x] Confirm map source immutability.
- [x] Focused implementation workflow green.
- [x] Verify exact diff/files and absence of `ACTIVE_WORK.md`/forbidden artifacts.
- [ ] Verify full ready-state CI including Required.
- [ ] Confirm zero unresolved review threads, enable auto-merge and squash-merge.
- [ ] Complete separate lifecycle/archive PR and mark Phase 6 merged and archived.

# Explicit exclusions

No Harlow, `0,0,0` teleport, Bone Capsule, The Beginning, storage progression, NPC/spawn/AID/UID handler, geometry, gameplay or production-map repair. No Phase 7/8 and no OTClient change.

# Local checkout and DNS limitation

- Local checkout: unavailable.
- Command executed once: `git ls-remote https://github.com/blakinio/canary.git HEAD`.
- Exact error: `fatal: unable to access 'https://github.com/blakinio/canary.git/': Could not resolve host: github.com`.
- Clone/fetch/pull/ls-remote were not repeated.
- GitHub API, workflow jobs and downloaded workflow artifacts provide repository-level verification.
- No local repository test result is claimed.

# Work log

- 2026-07-14: fresh preflight, task/branch and draft PR #311.
- 2026-07-14: modular implementation, tests, schema, ADR, docs and workflow.
- 2026-07-14: workflow-driven fixture/API fixes recorded above.
- 2026-07-14: all 30 focused tests and the complete dedicated workflow became green.
- 2026-07-14: shared documentation updated; current `main` merged; exact 14-file scope and forbidden-path absence verified; pre-ready workflows and Required succeeded.

# Remaining work

1. Mark PR #311 Ready for review.
2. Verify all workflows triggered by ready state, including the concrete Required job.
3. Confirm zero unresolved review threads, enable auto-merge and complete squash merge.
4. Create and merge a separate documentation-only lifecycle/archive PR.

# Handoff

The immediate next action is to mark PR #311 Ready for review and verify its ready-state checks. Do not parse OTBM independently, duplicate Phase 3, edit `ACTIVE_WORK.md`, commit generated inputs, modify a map or repair gameplay findings.
