---
task_id: CAN-20260713-otbm-reachability-validator
program_id: ""
coordination_id: "OTS-OTBM-VALIDATION"
status: active
agent: "GPT-5.6 Thinking"
branch: feat/otbm-reachability-validator
base_branch: main
created: 2026-07-13T18:43:00+02:00
updated: 2026-07-13T19:05:00+02:00
last_verified_commit: "afd5b2eeac2ae2137ea52cf3ce0cd19035eb9360"
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

Deliver Phase 3 of the OTBM tooling roadmap: a deterministic read-only validator for bounded teleport/floor-transition correctness and conservative player reachability without creating another OTBM parser or modifying any map.

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
- [ ] Update catalogue, changelog and roadmap.
- [x] Confirm no `.otbm`, `.widx`, `items.otb`, appearances binary, client asset, generated report/render, gameplay, protocol or production configuration is committed.
- [ ] Current-head required GitHub checks pass and autonomous merge gate is satisfied.

# Confirmed context

- Write target is exactly `blakinio/canary`; upstream repositories are read-only.
- Branch was created from `main` commit `444aa8ae13edc01c6e77b03139a43d386b437308`.
- Local Git access was attempted once with `git ls-remote https://github.com/blakinio/canary.git HEAD` and failed with `Could not resolve host: github.com`; GitHub API is the repository mutation path and no local checkout result is claimed.
- Open PR search for OTBM/reachability/teleport/stairs/pathfinding ownership returned no overlap. Adjacent open work is Forge, achievements, Wheel and E2E; none owns the claimed paths.
- `ACTIVE_WORK.md` is stale and read-only for this task.
- Phases 1 and 2 were merged before this branch; Phase 3 implementation is isolated in draft PR #274.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Unified OTBM World Index #219 | memory-mapped exact tile/placement/mechanic/region queries | `tools/ai-agent/otbm_world_index.py` | Avoids rescanning and avoids a competing OTBM parser. |
| Appearances catalogue | object ground/unpassable/avoid/usable flags | `tools/ai-agent/otbm_appearances.py` | Supplies conservative geometry semantics from actual client metadata. |
| Script resolution #104 | placement runtime status | `OTBM_SCRIPT_RESOLUTION_REPORT.schema.json` | Distinguishes engine/direct handling, unresolved registrations and conflicts. |
| Factual renderer | review-only visual context | `tools/ai-agent/otbm_renderer.py` | Users can render exact reported bounds without AI-generated map imagery. |

# Ownership and overlap check

- Program record: `docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md` is the authoritative programme handoff.
- Open PRs inspected: current user-owned open PR list plus targeted OTBM/reachability search; no matching ownership.
- Active tasks inspected: stale `ACTIVE_WORK.md`, targeted repository search and live PRs.
- Ownership checker result: pending GitHub Agent Task Ownership workflow.
- Exclusive claims: new reachability modules, CLI, tests, schemas, workflow, ADR and this task.
- Shared claims: narrow catalogue/changelog/roadmap entries.
- Read-only dependencies: World Index, appearances, script resolution, renderer and existing contracts.
- Overlaps: none confirmed.

# Current state

Implementation, CLI, tests, schemas, documentation, workflow and ADR are published on draft PR #274. The module is split by responsibility only to keep the reusable contracts reviewable; `otbm_reachability.py` remains the public facade.

# Plan

1. Update module catalogue, changelog and programme roadmap.
2. Inspect the complete PR diff and current-head workflows.
3. Repair any formatter, ownership, schema or integration failure.
4. Mark ready and merge only after every required gate succeeds.
5. Archive this task in a separate lifecycle PR.

# Work log

## 2026-07-13T18:43:00+02:00

- Created `feat/otbm-reachability-validator`, claimed exact paths and opened draft PR #274.
- Confirmed that World Index already exposes tile stacks and teleport destinations, while appearances expose `bank`, `unpassable`, `avoid`, `usable`, `multiUse` and `forceUse`.
- Rejected parser duplication and automatic stair/ladder inference.

## 2026-07-13T19:05:00+02:00

- Published strict/optimistic tile classification, teleport and reviewed transition validation, bounded BFS, no-corner-cut diagonals, route/mechanic reachability, one-way/dead-end/cycle findings and provenance-safe output.
- Added `canary-otbm-reachability-v1` and `canary-otbm-transition-manifest-v1` schemas.
- Added 16 focused tests, including a synthetic map built by the real World Index scanner when CI supplies it.
- Added dedicated CI and local toolkit artifact packaging without map/client binaries.
- Local isolated result: 16 tests passed with the scanner integration test skipped because no scanner path was available; Python compilation and schema syntax passed. This is not current-main CI evidence.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Require reviewed manifests for stairs/holes/ladders | Appearance flags do not prove destination offsets or direction. | `ADR-20260713-otbm-reachability-evidence-boundary.md` |
| Emit strict and optimistic reachability | Runtime door/quest/dynamic/unknown state must remain visible instead of guessed. | same ADR |
| Default to four-direction movement | Avoids claiming diagonal semantics; optional diagonals never cut corners. | same ADR |
| Keep a public facade plus focused internal modules | Preserves one stable import surface while keeping evidence, graph and analysis responsibilities reviewable. | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `tools/ai-agent/otbm_reachability.py` | exclusive | public facade, input provenance, atomic output | implemented |
| `tools/ai-agent/otbm_reachability_types.py` | exclusive | contracts, loaders and shared evidence types | implemented |
| `tools/ai-agent/otbm_reachability_transition.py` | exclusive | tile/transition validation | implemented |
| `tools/ai-agent/otbm_reachability_graph.py` | exclusive | bounded BFS and transition-cycle analysis | implemented |
| `tools/ai-agent/otbm_reachability_analysis.py` | exclusive | report orchestration | implemented |
| `tools/ai-agent/otbm_reachability_tool.py` | exclusive | CLI | implemented |
| `canary-otbm-reachability-v1` | exclusive | machine-readable output | implemented |
| `canary-otbm-transition-manifest-v1` | exclusive | reviewed floor-transition evidence | implemented |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| isolated local files | `python -m unittest -v test_otbm_reachability.py` | passed | 16 tests; scanner integration skipped because no scanner path was supplied |
| isolated local files | `python -m py_compile otbm_reachability*.py test_otbm_reachability.py` | passed | no repository checkout claim |
| isolated local files | JSON syntax and `jsonschema` sample validation | passed | report and transition sample validated |
| current PR head | OTBM Reachability / ownership / AI tools / repository CI | not-run | final documentation head not published yet |

Never treat the isolated local result as full current-main or real private-map proof.

# Failed approaches and dead ends

- Local Git DNS failed once; clone/fetch was not repeatedly retried.
- Automatic stairs/ladder inference from item names, sprites or visual memory was rejected.
- A single passable/blocked graph was rejected because it would hide runtime uncertainty or create false failures.

# Risks and compatibility

- Runtime: none; offline read-only tooling.
- Data/migration: none.
- Security: input hashes, bounded memory/output, atomic writes and symlink rejection.
- Backward compatibility: existing World Index, Quest Map Validator, script-resolution and renderer contracts remain unchanged.
- Cross-repo rollout: none; no OTClient protocol/client-code change.
- Rollback: squash-revert the tooling PR; no map or production state changes.

# Remaining work

1. Finish shared documentation and current-head CI review.

# Handoff

## Start here

Continue only PR #274 and `feat/otbm-reachability-validator` until it merges.

## Do not repeat

Do not create a new OTBM parser, infer floor transitions from imagery, execute dynamic Lua, modify the map, commit binary assets or edit `ACTIVE_WORK.md`.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md`
- `docs/ai-agent/OTBM_REACHABILITY.md`
- `docs/agents/decisions/ADR-20260713-otbm-reachability-evidence-boundary.md`

## Open questions

- A real-map smoke requires a local `.widx` plus compatible appearances catalogue. Absence of these artifacts must remain an explicit evidence limitation; they must not be committed.

# Completion

- Final status: active
- PR: #274
- Merge commit:
- Program record updated: pending
- Catalogue updated: pending
- Changelog updated: pending
- Archived at:
