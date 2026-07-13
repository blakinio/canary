---
task_id: CAN-20260713-otbm-phase3-reachability
coordination_id: "OTS-OTBM-VALIDATION"
status: active
agent: "GPT-5.6 Thinking"
branch: feat/otbm-phase3-reachability
base_branch: main
created: 2026-07-13T19:45:00+02:00
updated: 2026-07-13T19:45:00+02:00
last_verified_commit: "ad9ea2dd62cd72054edb1be81a0f31d6849de69c"
risk: medium
related_issue: ""
related_pr: "pending"
depends_on:
  - "merged Unified OTBM World Index #219/#223"
  - "merged Quest Map Validator #225/#236"
  - "merged factual appearance parser and renderer"
blocks:
  - "Phase 4 spawn/NPC validation"
  - "Phase 6 semantic map diff reachability impact"
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_reachability.py
    - tools/ai-agent/otbm_reachability_tool.py
    - tools/ai-agent/test_otbm_reachability.py
    - docs/ai-agent/OTBM_REACHABILITY.md
    - docs/ai-agent/OTBM_REACHABILITY.schema.json
    - .github/workflows/otbm-reachability.yml
    - docs/agents/tasks/active/CAN-20260713-otbm-phase3-reachability.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
    - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
  read_only:
    - tools/ai-agent/otbm_world_index.py
    - tools/ai-agent/otbm_world_index_tool.py
    - tools/ai-agent/otbm_appearances.py
    - tools/ai-agent/otbm_script_resolution.py
    - tools/ai-agent/quest_map_validation.py
    - tools/ai-agent/otbm_renderer.py
modules_touched:
  - OTBM World Index
  - OTBM appearances index
  - OTBM Phase 3 reachability validator
reuses:
  - tools/ai-agent/otbm_world_index.py
  - tools/ai-agent/otbm_appearances.py
  - existing factual renderer for review context only
public_interfaces:
  - canary-otbm-reachability-v1
  - canary-otbm-movement-catalog-v1
cross_repo_tasks: []
---

# Goal

Implement Phase 3 of the OTBM tooling programme as a deterministic, read-only validator for teleport destinations, bounded tile walkability evidence and explicit start/goal reachability. Reuse the existing World Index and appearance flags; do not create another OTBM parser or modify maps.

# Acceptance criteria

- [ ] Consume an existing `.widx` World Index and an appearances index/appearance catalogue.
- [ ] Classify tile movement evidence as walkable, blocked, conditional or unresolved.
- [ ] Validate every indexed teleport destination for tile existence, floor evidence and conservative walkability.
- [ ] Detect zero/self destinations, exact reverse pairs, one-way transitions and destination dead ends.
- [ ] Support explicitly bounded start/goal route checks with four-direction movement and indexed teleports.
- [ ] Distinguish confirmed reachability, unresolved conditional reachability and confirmed unreachable results.
- [ ] Support reviewed relative transitions for stairs, ladders, holes and floor changes through a versioned movement catalogue; never guess item roles.
- [ ] Enforce bounds, node limits, output limits, atomic writes and symlink rejection.
- [ ] Add schema, focused tests, documentation and dedicated CI.
- [ ] Run a real-map smoke against `/mnt/data/otservbr(4).otbm` and compatible client appearances without committing binary/generated artifacts.
- [ ] Update module catalogue, changelog and programme roadmap.
- [ ] Inspect final changed files, CI and review threads before squash merge.

# Scope and evidence boundaries

- Read-only source map/index operation.
- Appearance `unpassable` is movement evidence, not full server runtime proof.
- Doors, scripted blockers, quest state and dynamic item movement are reported as conditional/unresolved.
- Absence of a reviewed stairs/ladder/hole rule is not treated as a broken transition.
- No dynamic Lua execution.
- No OTBM, WIDX, client asset, appearance binary, generated report or render is committed.
- No upstream repository mutation.

# Ownership and overlap check

- Open PR search for OTBM/teleport/stairs/reachability/pathfinding returned no owner of these paths.
- Adjacent PR #245 is universal physical-client E2E and does not own OTBM tooling paths.
- Existing Phase 1/2 branches are historical and must not be reused.

# Plan

1. Add a reusable movement-evidence library over World Index placement/tile APIs.
2. Add teleport audit and bounded dual-graph route analysis.
3. Add reviewed movement-catalog support for relative cross-floor transitions.
4. Add CLI, schema, tests, workflow and documentation.
5. Validate on synthetic fixtures and the supplied real map/assets outside Git.
6. Update shared documentation, inspect CI and merge.

# Work log

## 2026-07-13T19:45:00+02:00

- Read current `AGENTS.md`, authoritative OTBM roadmap, World Index and appearances contracts.
- Verified current main `ad9ea2dd62cd72054edb1be81a0f31d6849de69c` at branch creation.
- Local clone attempt failed once with `Could not resolve host: github.com`; GitHub API will be used for repository writes and CI evidence. No local checkout result will be claimed.
- Claimed Phase 3 paths on `feat/otbm-phase3-reachability`.

# Validation

| Head | Check | Result | Evidence |
|---|---|---|---|
| | focused unit tests | not-run | implementation pending |
| | Python byte compilation | not-run | implementation pending |
| | real-map smoke | not-run | local supplied artifacts only |
| | GitHub Actions | not-run | draft PR pending |

# Remaining work

Implementation, validation, documentation and merge are pending.
