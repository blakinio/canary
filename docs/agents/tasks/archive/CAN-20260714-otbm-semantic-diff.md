---
task_id: CAN-20260714-otbm-semantic-diff
program_id: ""
coordination_id: "OTS-OTBM-VALIDATION"
status: completed
agent: "GPT-5.6 Thinking"
branch: feat/otbm-semantic-diff
base_branch: main
created: 2026-07-14T09:10:00+02:00
updated: 2026-07-14T10:17:03+02:00
completed: 2026-07-14T10:17:03+02:00
last_verified_commit: "5ae3141d6809b7a046b95922b304f905f7c636b2"
risk: medium
related_issue: ""
related_pr: "#311 / lifecycle PR pending"
depends_on:
  - "merged and archived Unified OTBM World Index #219/#223"
  - "merged and archived Quest Map Validator #225/#236"
  - "merged and archived OTBM reachability validator #274/#277"
  - "merged and archived OTBM spawn/NPC validator #286/#290"
  - "merged and archived OTBM storage dependency graph #299/#309"
blocks: []
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
    - docs/agents/tasks/archive/CAN-20260714-otbm-semantic-diff.md
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

# Completion state

Phase 6 feature PR #311 was squash-merged into `main`.

- Historical feature branch: `feat/otbm-semantic-diff` (do not continue).
- Final feature head: `5ae3141d6809b7a046b95922b304f905f7c636b2`.
- Squash merge: `4ab2dd2d72e3f55badfd45d76dd9f59d65c22f5a`.
- Feature merged at: `2026-07-14T08:17:03Z` (`2026-07-14T10:17:03+02:00`).
- Feature review threads: zero.
- Auto-merge: enabled after the final Required check succeeded; GitHub completed the squash merge.
- Rollback: revert `4ab2dd2d72e3f55badfd45d76dd9f59d65c22f5a`; no map, persistence, asset or generated-artifact cleanup is required.
- Lifecycle branch: `docs/archive-otbm-semantic-diff`.
- Lifecycle cleanup PR: pending creation; update this record before merge.

# Delivered contracts and evidence boundary

- Report: `canary-otbm-semantic-diff-v1`.
- Factual render manifest: `canary-otbm-semantic-diff-render-v1`.
- Tile identity is exact `x,y,z`.
- Aligned item base is exact `(itemId,itemDepth,source)`.
- Pure exact-multiset reorder emits `stack-order-changed` without false add/remove.
- Other stack edits use a deterministic minimum edit script with fixed `replace`, `remove`, `add` tie order.
- AID, UID, house-door, teleport source and teleport destination changes remain separate findings.
- Full-index and inclusive bounded 3D scopes preserve exact selected-scope totals while samples are bounded and explicitly truncated.
- Optional Phase 2, script-resolution, Phase 3, Phase 4 and Phase 5 correlation uses exact positions/literal mechanics only and never promotes selected scope to global proof.
- Walkability calls the existing Phase 3 `otbm_reachability_transition._classify_tile` implementation.
- Factual visual evidence calls `otbm_renderer.render_region` or emits exact `otbm_render_tool.py` commands.
- No second OTBM parser, World Index, script resolver, pathfinder or renderer was created.
- No dynamic Lua was executed; unresolved evidence was not promoted to handled.
- No map, datapack, gameplay, OTClient or upstream repository was modified.

# Final changed files in PR #311

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

Confirmed absent from the feature diff: `docs/agents/ACTIVE_WORK.md`, `.otbm`, `.widx`, `items.otb`, appearances binaries, client assets, generated reports/renders, map/datapack/gameplay/OTClient changes and upstream writes.

# Validation

## Local isolated checks

Local repository checkout was unavailable. The following isolated file checks were executed before publication:

- Phase 6 Python compilation: passed.
- `OTBM_SEMANTIC_DIFF.schema.json` JSON syntax: passed.

These are not a local repository test run.

## Workflow-driven fixes

- Run `29314876746`, job `87026487592`: initial focused-test failure after native scanner compilation.
- Run `29315020741`, artifact `8303572057`: diagnosed a test fixture field shadowing its builder method and one incorrect test path type.
- Run `29315132001`, job `87027296193`, artifact `8303618450`: 28/30 tests passed; fixed programmatic path normalization and retained a neutral child item in two synthetic walkability fixtures to avoid an existing no-child fixture/index representation edge.
- Run `29315508600`, job `87028506652`: all 30 focused tests and the complete dedicated workflow passed.

## Final ready-state feature-head workflows

Head `5ae3141d6809b7a046b95922b304f905f7c636b2`:

- OTBM Semantic Diff run `29316215755`; job `87030733453` (`Validate semantic map evidence`): success.
- OTBM Map Tools run `29316215784`: success.
- Agent Task Ownership run `29316215791`; job `87030730336`: success.
- autofix.ci run `29316215749`: success/no autofix changes.
- AI Agent Tools run `29316215787`: success.
- repository CI run `29316215995`: success.
- Fast Checks job `87030777614`: success.
- Lua Tests job `87030777654`: success.
- Linux Release job `87031009052`: success.
- Required job `87032170628`: success.
- Review threads: zero.

Green CI proves only the checks executed for this commit. It is not runtime or gameplay proof.

# Real-map validation

Real two-map comparison: not run. Only one historical private-map provenance was available, so no second map was invented or modified. Historical private map SHA-256 retained for provenance only:

`a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`

No private map, WIDX, appearances binary, client asset, generated report or render was committed.

# Local checkout and DNS limitation

- Local checkout: unavailable.
- Command executed once: `git ls-remote https://github.com/blakinio/canary.git HEAD`.
- Exact error: `fatal: unable to access 'https://github.com/blakinio/canary.git/': Could not resolve host: github.com`.
- Clone/fetch/pull/ls-remote were not repeated.
- Repository, PR, commit, workflow, job, artifact and review-thread verification used GitHub API.
- No local repository test result is claimed.

# Acceptance criteria

- [x] Reuse canonical World Index/native scanner without independently parsing OTBM.
- [x] Verify provenance and fail closed on corrupt/incompatible inputs.
- [x] Report deterministic tile, stack, mechanic and Phase 3 walkability changes.
- [x] Support full and bounded inclusive 3D scopes.
- [x] Preserve exact totals, bounded samples, stable IDs and explicit truncation.
- [x] Provide conservative optional correlation.
- [x] Integrate factual visual evidence through the existing renderer.
- [x] Provide path/size/overwrite/symlink/atomic-output safety.
- [x] Add schema, documentation, ADR, 30 focused tests and dedicated workflow/artifacts.
- [x] Update MODULE_CATALOG, CHANGELOG and authoritative roadmap.
- [x] Keep forbidden map/index/asset/render artifacts outside Git.
- [x] Confirm source-map immutability.
- [x] Verify the exact 14-file feature diff.
- [x] Pass final ready-state CI and Required.
- [x] Confirm zero review threads, enable auto-merge and squash-merge PR #311.
- [x] Move this record from `tasks/active` to `tasks/archive` in a separate lifecycle branch.

# Work log

- 2026-07-14: completed fresh preflight, task/branch creation and draft PR #311.
- 2026-07-14: delivered modular implementation, tests, schema, ADR, documentation and workflow.
- 2026-07-14: diagnosed and fixed workflow-discovered fixture/API issues without weakening the production evidence boundary.
- 2026-07-14: synchronized with advancing `main`, preserved the exact 14-file scope and verified all final checks.
- 2026-07-14: enabled auto-merge after Required and completed squash merge `4ab2dd2d72e3f55badfd45d76dd9f59d65c22f5a`.
- 2026-07-14: created the separate lifecycle branch and moved the task record to archive.

# Handoff

Phase 6 implementation is complete. Do not reopen #311 or continue `feat/otbm-semantic-diff`. Do not create another parser, World Index, resolver, pathfinder or renderer. Phase 7 is the exact next planned programme phase, but it must not start until this lifecycle PR is merged and a fresh main/open-PR/active-task/ownership preflight is complete.
