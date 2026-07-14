---
task_id: CAN-20260714-otbm-semantic-diff
program_id: ""
coordination_id: "OTS-OTBM-VALIDATION"
status: active
agent: "GPT-5.6 Thinking"
branch: feat/otbm-semantic-diff
base_branch: main
created: 2026-07-14T09:10:00+02:00
updated: 2026-07-14T09:39:00+02:00
last_verified_commit: "0705f8fa73e83ece14c83b3438648af1295256bd"
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

# Fresh preflight

- Branch base `main`: `f4e5371906d3b4a33229db2dce6b25d44fb813f0`.
- Phase 5 lifecycle PR #309 was squash-merged and archived before this branch was created.
- No open OTBM/Semantic Diff PR, active semantic-diff task, semantic-diff branch or existing `otbm_semantic_diff` implementation was found.
- Current unrelated open PRs had no declared OTBM ownership overlap.
- `ACTIVE_WORK.md` remains read-only and is not in owned paths.
- Upstream `opentibiabr/*` remains read-only.

# Fixed contract

Report contract: `canary-otbm-semantic-diff-v1`.

Render-manifest contract: `canary-otbm-semantic-diff-render-v1`.

Cross-index identities:

- tile: exact `x,y,z`;
- item base for aligned mechanic comparison: exact `(itemId,itemDepth,source)`;
- exact item evidence: item base plus literal action ID, unique ID, house-door ID and teleport destination.

Pure exact-multiset reorder is one `stack-order-changed` finding with no false add/remove. Other stack changes use a deterministic minimum edit script with fixed tie order `replace`, `remove`, `add`. No fuzzy item matching is performed.

Walkability calls the existing Phase 3 `otbm_reachability_transition._classify_tile` implementation. Phase 6 does not copy or reinterpret Phase 3 ground/static/conditional/unknown/strict/optimistic rules.

Optional correlation indexes only exact positions and literal mechanics in explicitly supplied format-validated Phase 2, script-resolution, Phase 3, Phase 4 and Phase 5 reports. Correlation remains selected-scope evidence.

Factual visual evidence calls `otbm_renderer.render_region` or emits exact `otbm_render_tool.py` commands. No renderer, AI image, styled sprite or synthetic overlay is created.

# Implemented files

- `.github/workflows/otbm-semantic-diff.yml`
- `docs/agents/decisions/ADR-20260714-otbm-semantic-diff-evidence-boundary.md`
- `docs/agents/tasks/active/CAN-20260714-otbm-semantic-diff.md`
- `docs/ai-agent/OTBM_SEMANTIC_DIFF.md`
- `docs/ai-agent/OTBM_SEMANTIC_DIFF.schema.json`
- `tools/ai-agent/otbm_semantic_diff.py`
- `tools/ai-agent/otbm_semantic_diff_analysis.py`
- `tools/ai-agent/otbm_semantic_diff_render.py`
- `tools/ai-agent/otbm_semantic_diff_tool.py`
- `tools/ai-agent/otbm_semantic_diff_types.py`
- `tools/ai-agent/test_otbm_semantic_diff.py`

Shared documentation remains to be updated after the focused workflow is green.

# Implemented behavior

- binary World Index validation through the existing reader;
- manifest/index/source/scanner SHA-256 and size validation;
- OTBM/index/scanner-build compatibility checks;
- streaming full-index or inclusive bounded-region merge;
- exact tile kind, flags, house ID and ground evidence;
- item added/removed/replaced, exact reorder and stack indices;
- separate AID, UID, house-door, teleport source/destination findings;
- Phase 3 walkability regression/improvement classifications;
- exact global selected-scope totals with bounded samples and explicit truncation;
- stable IDs independent of optional correlation;
- conservative optional correlation;
- factual before/after/context render manifest through the existing renderer;
- artifact-root confinement, direct symlink rejection, explicit overwrite, size limits and atomic JSON writes;
- optional real-map hash verification only; map bytes remain unchanged.

# Focused tests

Thirty tests cover:

1. identical indexes;
2. tile added;
3. tile removed;
4. tile flags;
5. house ID;
6. ground;
7. item added;
8. item removed;
9. exact stack reorder without false add/remove;
10. action ID;
11. unique ID;
12. house-door ID;
13. teleport destination;
14. strict walkability regression;
15. conditional walkability;
16. unknown appearances retained;
17. bounded-region exclusion;
18. exact totals under truncation;
19. deterministic output;
20. corrupt index fail-closed;
21. mismatched provenance fail-closed;
22. overwrite protection;
23. symlink output rejection;
24–27. optional Phase 2–5 correlation;
28. missing optional reports;
29. existing renderer API/command manifest;
30. source-map immutability.

Local isolated checks available without a repository checkout:

- `python -m py_compile` for the six Phase 6 Python files: passed before publication.
- `python -m json.tool docs/ai-agent/OTBM_SEMANTIC_DIFF.schema.json`: passed before publication.

These are isolated file checks, not a local repository test run.

# CI history and fixes

Initial Phase 6 run:

- workflow run `29314876746`;
- job `87026487592` (`Validate semantic map evidence`);
- scanner compilation: success;
- focused tests: failure.

A diagnostic-log artifact was added because the original downloaded job log was truncated before the traceback.

Diagnostic run:

- workflow run `29315020741`;
- artifact `otbm-semantic-diff-focused-tests`, artifact ID `8303572057`;
- exact failure: the class-level `TemporaryDirectory` used the same `build` name as the fixture-building method, so 29 tests attempted to call a `TemporaryDirectory`; the render-manifest test supplied strings where the API declares `Path`.
- fix at `0705f8fa73e83ece14c83b3438648af1295256bd`: rename the class resource to `compiler_temp` and pass `Path` values to the render API.

No production contract changed for this fixture fix.

# Acceptance criteria

- [x] Compare two compatible canonical World Index inputs without parsing OTBM independently.
- [x] Verify source-map/index/scanner provenance and SHA-256 and fail closed on incompatible/corrupt inputs.
- [x] Report deterministic tile, item-stack and separate mechanic changes with exact positions/indices.
- [x] Reuse the exact Phase 3 walkability implementation without duplicating its engine.
- [x] Support full comparison and optional inclusive bounded 3D regions.
- [x] Preserve exact totals with bounded samples, stable IDs and explicit truncation.
- [x] Provide conservative optional Phase 2/3/4/5 and script-resolution correlation.
- [x] Integrate factual before/after/context evidence through the existing renderer API.
- [x] Add atomic output, explicit overwrite, symlink rejection, path confinement and size limits.
- [x] Add schema, documentation, ADR, 30 focused tests and dedicated CI/artifacts.
- [x] Keep `.otbm`, `.widx`, assets, appearances and generated renders/reports outside Git.
- [x] Confirm source maps remain unchanged by tests and policy.
- [ ] Focused workflow green after the fixture fix.
- [ ] Update MODULE_CATALOG, CHANGELOG, roadmap, task and PR body.
- [ ] Verify exact diff/files and absence of `ACTIVE_WORK.md`/forbidden artifacts.
- [ ] Ready-state CI including Required, zero review threads, auto-merge and squash merge.
- [ ] Separate lifecycle/archive PR and Phase 6 `merged and archived` roadmap state.

# Explicit exclusions

No Harlow, `0,0,0` teleport, Bone Capsule, The Beginning, storage progression, NPC/spawn/AID/UID handler, geometry, gameplay or production-map repair. No Phase 7/8. No OTClient change.

# Local checkout and DNS limitation

- Local checkout: unavailable.
- Command executed once: `git ls-remote https://github.com/blakinio/canary.git HEAD`.
- Exact result: `fatal: unable to access 'https://github.com/blakinio/canary.git/': Could not resolve host: github.com`.
- Clone/fetch/pull/ls-remote were not repeated.
- GitHub API and workflow artifacts are used for repository-level verification.
- No local repository test result is claimed.

# Work log

- 2026-07-14 09:10 CEST: fresh preflight, branch/task creation and draft PR #311.
- 2026-07-14 09:12–09:32 CEST: fixed contracts, modular implementation, tests, schema, ADR, documentation and workflow published.
- 2026-07-14 09:34 CEST: first workflow failure isolated to test harness lifecycle; diagnostic artifact added.
- 2026-07-14 09:39 CEST: fixture-name and render-argument fixes published at `0705f8fa73e83ece14c83b3438648af1295256bd`.

# Remaining work

1. Verify the post-fix focused workflow and inspect its artifact/logs if needed.
2. Update shared documentation and PR body.
3. Run exact diff/file/forbidden-path review.
4. Mark Ready, verify ready-state CI/Required/review threads, enable auto-merge and merge.
5. Create and merge the separate lifecycle/archive PR.

# Handoff

Current implementation head: `0705f8fa73e83ece14c83b3438648af1295256bd`. The immediate next action is to inspect the `OTBM Semantic Diff` run for this head. Do not parse OTBM independently, duplicate Phase 3, edit `ACTIVE_WORK.md`, commit generated inputs or repair gameplay/map findings.
