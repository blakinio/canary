---
task_id: CAN-20260714-otbm-semantic-diff
program_id: ""
coordination_id: "OTS-OTBM-VALIDATION"
status: active
agent: "GPT-5.6 Thinking"
branch: feat/otbm-semantic-diff
base_branch: main
created: 2026-07-14T09:10:00+02:00
updated: 2026-07-14T09:10:00+02:00
last_verified_commit: "f4e5371906d3b4a33229db2dce6b25d44fb813f0"
risk: medium
related_issue: ""
related_pr: "pending"
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
  - OTBM semantic diff CLI
cross_repo_tasks: []
---

# Goal

Deliver Phase 6 as a deterministic read-only semantic diff between two canonical World Index inputs, reusing the existing native scanner, Phase 3 walkability semantics and factual renderer without creating a second parser, pathfinder or renderer.

# Fresh preflight

- Current `main`: `f4e5371906d3b4a33229db2dce6b25d44fb813f0`.
- Phase 5 lifecycle PR #309: squash-merged and archived before this branch was created.
- Open PR search: no OTBM or semantic-diff PR exists; current open PRs concern multichannel DB handoff, E2E, Forge, Wheel staging and a paused Cyclopedia experiment.
- Branch search: no existing semantic-diff branch found.
- Repository search: no existing `otbm_semantic_diff` implementation found.
- Roadmap: Phase 5 is `merged and archived`; Phase 6 is `not started` at branch creation.
- `ACTIVE_WORK.md`: read-only and not edited.
- Upstream `opentibiabr/*`: read-only; no writes planned.

# Contract under design

Preferred report contract: `canary-otbm-semantic-diff-v1`.

Required evidence layers remain distinct:

- structural;
- static;
- semantic;
- correlated;
- regression;
- runtime;
- gameplay;
- factual visual evidence.

A lower evidence layer does not prove a higher one. The diff may classify changed evidence but does not repair maps, gameplay, scripts, quests, spawns, NPCs or storage progression.

# Acceptance criteria

- [ ] Compare two compatible canonical World Index inputs without parsing OTBM independently.
- [ ] Verify source-map/index/scanner provenance and SHA-256, fail closed on incompatible or corrupt inputs.
- [ ] Report deterministic tile additions/removals, tile flags, house IDs and ground changes with exact positions/floors.
- [ ] Report deterministic item additions/removals/replacements, stack-order changes and exact before/after stack indices.
- [ ] Report AID, UID, house-door and teleport source/destination mechanic changes separately.
- [ ] Reuse Phase 3 public walkability semantics; do not duplicate its engine.
- [ ] Support full comparison and optional inclusive bounded 3D regions.
- [ ] Preserve exact total counts with bounded samples and explicit truncation.
- [ ] Provide stable finding IDs, deterministic ordering and exact before/after provenance.
- [ ] Provide conservative optional Phase 2/3/4/5 correlation without expanding selected scope.
- [ ] Integrate factual before/after/context render commands/manifests through the existing renderer API.
- [ ] Add atomic output, explicit overwrite, symlink rejection, path confinement and input/output size limits.
- [ ] Add schema, documentation, ADR, focused tests and dedicated CI/artifacts.
- [ ] Keep `.otbm`, `.widx`, client assets, appearances and generated renders/reports outside Git.
- [ ] Confirm source maps remain unchanged.
- [ ] Update module catalogue, changelog, roadmap, task and PR body.
- [ ] Verify exact changed files/diff, zero `ACTIVE_WORK.md`, zero forbidden binaries/assets.
- [ ] Pass ready-state CI including `Required`, resolve review threads, auto-merge and squash-merge.
- [ ] Archive this task in a separate lifecycle PR and mark Phase 6 merged/archived.

# Explicit exclusions

- No new OTBM parser, World Index, script resolver, pathfinder or map renderer.
- No dynamic Lua execution or guessing dynamic expressions.
- No promotion of `unresolved` to handled without direct evidence.
- No Harlow, `0,0,0` teleport, Bone Capsule, The Beginning, storage, NPC, spawn, AID/UID or map-geometry repair.
- No map modification or production gameplay change.
- No Phase 7 or Phase 8 implementation.
- No OTClient change.

# Local checkout and DNS limitation

- Local checkout: unavailable.
- Command previously executed once: `git ls-remote https://github.com/blakinio/canary.git HEAD`.
- Exact result: `fatal: unable to access 'https://github.com/blakinio/canary.git/': Could not resolve host: github.com`.
- Clone/fetch/pull/ls-remote will not be repeated after this confirmed DNS failure.
- GitHub API will be used for repository, branch, file, PR, workflow, job, review and commit operations.
- No local repository test result is claimed unless a checkout later becomes available independently.

# Work log

- 2026-07-14 09:10 CEST: completed fresh post-Phase-5 preflight, created branch from current `main`, claimed the Phase 6 paths and recorded the evidence boundary.

# Remaining work

1. Read the canonical World Index, Phase 3 reachability, renderer and prior modular Phase patterns in detail.
2. Fix the exact input/report API and data model in the ADR and task.
3. Open a draft PR early.
4. Implement the smallest complete modular diff, tests, schema, docs and workflow.

# Handoff

No implementation exists yet. The next safe action is to inspect the World Index reader/query API and Phase 3 public walkability API, then record the chosen reuse boundary before creating source modules. Do not parse `.otbm`, duplicate walkability logic or edit `ACTIVE_WORK.md`.
