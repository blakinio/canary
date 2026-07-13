---
task_id: CAN-20260713-otbm-reachability-validator
program_id: ""
coordination_id: "OTS-OTBM-VALIDATION"
status: ready_for_review_pending_ci
agent: "GPT-5.6 Thinking"
branch: feat/otbm-reachability-validator
base_branch: main
created: 2026-07-13T18:43:00+02:00
updated: 2026-07-13T19:22:00+02:00
last_verified_commit: "c185482e50e18160531d5fee697eb3c4522c2c7d"
risk: medium
related_issue: ""
related_pr: "#274"
depends_on:
  - "merged Unified OTBM World Index #219/#223"
  - "merged Quest Map Validator #225/#236"
  - "merged OTBM script-resolution audit #104"
  - "merged factual renderer/appearance catalogue tooling"
blocks:
  - "OTBM spawn/NPC validation phase"
  - "OTBM storage graph phase"
  - "OTBM semantic diff and geometry phases"
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_reachability.py
    - tools/ai-agent/otbm_reachability_types.py
    - tools/ai-agent/otbm_reachability_transition.py
    - tools/ai-agent/otbm_reachability_graph.py
    - tools/ai-agent/otbm_reachability_analysis.py
    - tools/ai-agent/otbm_reachability_tool.py
    - tools/ai-agent/test_otbm_reachability.py
    - docs/ai-agent/OTBM_REACHABILITY.md
    - docs/ai-agent/OTBM_REACHABILITY.schema.json
    - docs/ai-agent/OTBM_TRANSITIONS.schema.json
    - .github/workflows/otbm-reachability.yml
    - docs/agents/decisions/ADR-20260713-otbm-reachability-evidence-boundary.md
    - docs/agents/tasks/active/CAN-20260713-otbm-reachability-validator.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
    - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
  read_only:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/ACTIVE_WORK.md
    - tools/ai-agent/otbm_world_index.py
    - tools/ai-agent/otbm_world_index_tool.py
    - tools/ai-agent/otbm_appearances.py
    - tools/ai-agent/otbm_script_resolution.py
    - tools/ai-agent/otbm_renderer.py
    - docs/ai-agent/OTBM_WORLD_INDEX.md
    - docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md
    - docs/ai-agent/QUEST_MAP_VALIDATION.md
modules_touched:
  - OTBM reachability validator
reuses:
  - Unified OTBM World Index
  - appearances catalogue parser
  - OTBM script-resolution report
  - factual OTBM renderer contract
public_interfaces:
  - canary-otbm-reachability-v1
  - canary-otbm-transition-manifest-v1
  - OTBM reachability CLI
cross_repo_tasks: []
---

# Goal

Deliver Phase 3 of the OTBM tooling roadmap: deterministic read-only validation for bounded teleport/floor-transition correctness and conservative player reachability without creating another OTBM parser or modifying any map.

# Acceptance criteria

- [x] Analyze only explicit bounded regions and explicit origins/start-goal routes.
- [x] Reuse `WorldIndex` for tiles, placements, mechanics, teleports and exact coordinates.
- [x] Reuse object appearance flags for confirmed ground, unpassable, avoid and interactive-state evidence.
- [x] Validate every indexed teleport source/destination in the selected region.
- [x] Accept reviewed stairs/ladder/hole/rope/floor-change edges through a versioned transition manifest; never infer them from visual memory or item-name guesses.
- [x] Correlate optional script-resolution placement status and preserve conflicting/unresolved evidence.
- [x] Produce strict and optimistic reachability, with door/quest/dynamic/unknown uncertainty separated from confirmed geometry.
- [x] Detect unreachable routes/mechanics, one-way transitions, destination dead ends and transition cycles.
- [x] Prevent diagonal corner cutting when optional diagonal movement is enabled.
- [x] Bound region size, route starts, routes, transitions, samples and path output.
- [x] Write reports atomically and reject symlink outputs and provenance mismatches.
- [x] Add focused tests, schemas, documentation, dedicated CI and a durable evidence-boundary ADR.
- [x] Update catalogue, changelog and authoritative roadmap.
- [x] Confirm no `.otbm`, `.widx`, `items.otb`, appearances binary, client asset, generated report/render, gameplay, protocol or production configuration is committed.
- [ ] Final ready-head workflows and autonomous merge gate pass.
- [ ] Merge and archive this task in a separate lifecycle PR.

# Confirmed context

- Write target is exactly `blakinio/canary`; upstream repositories are read-only.
- Branch was created from `main` commit `444aa8ae13edc01c6e77b03139a43d386b437308`.
- Local Git access was attempted once with `git ls-remote https://github.com/blakinio/canary.git HEAD` and failed with `Could not resolve host: github.com`; GitHub API is the repository mutation path and no local checkout result is claimed.
- Open PR search for OTBM/reachability/teleport/stairs/pathfinding ownership returned no overlap. Adjacent work is Forge, achievements, Wheel and E2E; none owns the claimed paths.
- `ACTIVE_WORK.md` is stale and read-only for this task.
- Phases 1 and 2 were merged before this branch; Phase 3 is isolated in PR #274.

# Architecture and reuse

| Dependency | Reuse | Reason |
|---|---|---|
| Unified OTBM World Index #219 | exact memory-mapped tile/placement/mechanic/region queries | prevents rescanning and parser duplication |
| appearances catalogue parser | actual ground/unpassable/avoid/interaction flags | supplies conservative geometry evidence |
| script-resolution #104 | placement runtime status | preserves unresolved and conflicts |
| factual renderer | separate bounded visual review | prevents AI-generated map evidence |

The implementation provides one public facade, `otbm_reachability.py`, with focused internal modules for evidence types, transition validation, graph traversal and report orchestration.

# Delivered behavior

- `canary-otbm-reachability-v1` report and JSON Schema;
- `canary-otbm-transition-manifest-v1` reviewed floor-transition contract and JSON Schema;
- strict graph: confirmed ground, no static/conditional blocker, no unknown appearance;
- optimistic graph: confirmed ground and no static blocker while conditional/unknown state remains explicit;
- four-direction movement by default;
- optional diagonal movement without corner cutting;
- automatic indexed teleport validation;
- explicit reviewed stairs/ladder/hole/rope/floor-change edges;
- optional script-resolution correlation;
- route and map-mechanic reachability;
- one-way, dead-end and transition-cycle findings;
- deterministic bounded path samples and exact totals;
- atomic output, overwrite protection, symlink rejection and provenance hashes;
- dedicated workflow and local toolkit artifact without map/client binaries.

# Evidence and safety boundary

- Dynamic Lua is never executed.
- Non-teleport floor offsets are never inferred from item names, sprites or visual memory.
- Conditional/optimistic reachability is not gameplay proof.
- The validator does not model creatures, players, movable blockers, live storage/account/database state or physical-client behavior.
- No map, WIDX, appearances binary, client asset, generated report/render or upstream repository is modified or committed.

# Validation and CI

## Isolated local files

- `python -m unittest -v test_otbm_reachability.py`: 16 tests passed; the real-scanner integration test was skipped because no scanner path was supplied.
- `python -m py_compile otbm_reachability*.py test_otbm_reachability.py`: passed.
- report/transition JSON syntax and representative `jsonschema` validation: passed.

These are isolated-file checks, not current-main/full-repository or private-map proof.

## Reviewed implementation head

Head `2fb1fe195a13e830709c0ae028a7f9d8280ff7db`:

- OTBM Reachability run `29269281476`: success.
  - job `86882600269` succeeded;
  - native scanner compiled with warnings as errors;
  - focused tests including real World Index fixture integration succeeded;
  - Python compilation, schema syntax and toolkit upload succeeded.
- Agent Task Ownership run `29269281465`: success; job `86882600120` succeeded.
- AI Agent Tools run `29269281509`: success; job `86882600789` succeeded.
- OTBM Map Tools run `29269281596`: success; job `86882600654` succeeded.
- repository CI run `29269281801`: success.
  - Detect Build Scope job `86882601595`: success;
  - Required job `86882669487`: success;
  - C++/Lua platform jobs were skipped by path scope, so no runtime/gameplay claim is made.
- review threads: zero at inspection.
- changed-file list: exactly 15 text/source/workflow/schema/documentation paths; no map/index/asset/generated artifact.

## Ready-head gate

The catalogue, changelog and authoritative roadmap were subsequently updated. Fresh workflows on the final ready head remain required before merge.

# Decisions

| Decision | Reason | ADR |
|---|---|---|
| reviewed manifests for stairs/holes/ladders | appearance flags do not prove destination offset/direction | `ADR-20260713-otbm-reachability-evidence-boundary.md` |
| strict and optimistic graphs | runtime door/quest/dynamic/unknown state must remain visible | same ADR |
| four-direction default, corner-safe diagonals | avoids guessing client movement semantics | same ADR |
| read-only consumer of World Index | preserves one canonical OTBM parser/cache | same ADR |

# Failed approaches and corrections

- Local Git DNS failed once; clone/fetch was not repeatedly retried.
- Automatic stairs/ladder inference from item names, sprites or visual memory was rejected.
- A single passable/blocked graph was rejected because it would hide runtime uncertainty or create false failures.
- A local attempt to rebuild the full private-map WIDX exceeded the available execution window and was aborted; no partial file was used as evidence. The earlier verified map provenance remains documented, while Phase 3 correctness is supported by the dedicated real-scanner fixture integration in CI.

# Risks and compatibility

- Runtime: none; offline read-only tooling.
- Data/migration: none.
- Backward compatibility: World Index, Quest Map Validator, script-resolution and renderer contracts are unchanged.
- Cross-repository rollout: none; no OTClient protocol/client-code change.
- Rollback: squash-revert PR #274; no map or production state cleanup.

# Remaining work

1. Mark PR #274 Ready for review.
2. Inspect every fresh final-head workflow/job, reviews, mergeability and exact changed files.
3. Squash-merge after the autonomous gate passes.
4. Move this record to `docs/agents/tasks/archive/` in a separate documentation-only lifecycle PR and pin the final merge SHA in the roadmap.

# Handoff

Continue only PR #274 and branch `feat/otbm-reachability-validator` until merge. Do not start Phase 4, create another OTBM parser/pathfinder, modify the map, commit binary artifacts or edit `ACTIVE_WORK.md`.

# Completion

- Final status: ready_for_review_pending_ci
- PR: #274
- Merge commit:
- Programme record updated: yes
- Catalogue updated: yes
- Changelog updated: yes
- Archived at: pending lifecycle PR
