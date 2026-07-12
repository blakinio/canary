---
task_id: CAN-20260712-otbm-world-index
coordination_id: "OTS-OTBM-VALIDATION"
status: active
agent: "GPT-5.6 Thinking"
branch: feat/otbm-world-index
base_branch: main
created: 2026-07-12T22:16:00+02:00
updated: 2026-07-12T22:16:00+02:00
last_verified_commit: "266cf3b1798f144a4b3b8ffbc26817df96c53c68"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - "merged OTBM item audit"
  - "merged OTBM script-resolution audit #104"
  - "merged factual OTBM renderer and HD pipeline #154/#161"
blocks:
  - "Quest Map Validator phase"
  - "teleport/pathfinding validation phase"
  - "OTBM semantic diff phase"
owned_paths:
  - tools/ai-agent/otbm_world_index.py
  - tools/ai-agent/otbm_world_index_tool.py
  - tools/ai-agent/test_otbm_world_index.py
  - docs/ai-agent/OTBM_WORLD_INDEX.md
  - docs/ai-agent/OTBM_WORLD_INDEX.schema.json
  - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
  - .github/workflows/otbm-world-index.yml
  - docs/agents/tasks/active/CAN-20260712-otbm-world-index.md
  - docs/agents/ACTIVE_WORK.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
modules_touched:
  - OTBM item audit
  - OTBM script-resolution audit
  - OTBM factual renderer
reuses:
  - tools/ai-agent/otbm_item_audit.py
  - tools/ai-agent/otbm_item_audit_scan.cpp
  - tools/ai-agent/otbm_script_resolution.py
  - tools/ai-agent/otbm_renderer.py
public_interfaces:
  - "canary-otbm-world-index-v1"
  - "OTBM world index CLI"
cross_repo_tasks: []
---

# Goal

Create a deterministic read-only world index that converts one OTBM scan plus appearances/items metadata into a queryable JSON contract for item IDs, map mechanics, positions, teleport destinations, tile occupancy and provenance, without rescanning or modifying the map for every downstream audit.

# Acceptance criteria

- [ ] Build `canary-otbm-world-index-v1` from the existing native OTBM scan output; do not create a second binary parser.
- [ ] Index positions by `itemId`, `actionId`, `uniqueId`, `houseDoorId`, and teleport source/destination.
- [ ] Preserve map SHA-256, scanner format/version, source report hashes and deterministic ordering.
- [ ] Provide CLI queries for position, region, item ID, action ID, unique ID and teleport destination.
- [ ] Bound in-memory/report growth and support summary-only/truncated position lists without losing counts.
- [ ] Add focused tests for determinism, duplicate mechanics, bounds, malformed input, path/hash provenance and query semantics.
- [ ] Add schema, documentation, dedicated CI and an umbrella roadmap for later quest/spawn/NPC/storage/diff/patch phases.
- [ ] Confirm no `.otbm`, `items.otb`, appearances binary, client asset, generated world index or active datapack is committed.
- [ ] Module catalogue, changelog, task record and PR body are current.
- [ ] Cross-repository impact is none for this phase.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- Current `main` at branch creation: `266cf3b1798f144a4b3b8ffbc26817df96c53c68`.
- Existing OTBM item audit already emits item usage, mechanic placements and map provenance; the new module must consume/extend that contract rather than duplicate OTBM parsing.
- Existing OTBM script-resolution audit #104 consumes `mechanicPlacements` and separates runtime evidence from review disposition.
- Existing renderer/HD pipeline can render bounded factual regions from real OTBM/client assets, but visual rendering remains optional and separate from index correctness.
- Repository policy forbids committing `.otbm`, `items.otb`, appearances binaries, sprite sheets and generated reports.
- Open PRs inspected at task start include #188, #187, #186, #185, #184, #169 and #157. None owns the new `otbm_world_index*` paths. Shared agent indexes may require current-main conflict resolution.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| OTBM item audit | native scan and item/mechanic placement contract | `tools/ai-agent/otbm_item_audit.py`, `otbm_item_audit_scan.cpp` | Already parses the binary map and records the identifiers required by downstream tools. |
| OTBM script resolution / #104 | registration/status vocabulary and placement linkage | `tools/ai-agent/otbm_script_resolution.py` | World index should be directly consumable by future quest/script correlation rather than inventing a competing representation. |
| Factual OTBM renderer / #154/#161 | bounded region rendering and asset provenance | `tools/ai-agent/otbm_renderer.py`, `otbm_hd.py` | Later visual reports can query exact regions from this index. |

# Ownership and overlap check

- Open PRs inspected: #188, #187, #186, #185, #184, #169, #157 and current search results.
- Active tasks inspected: `docs/agents/ACTIVE_WORK.md`; GitHub open PR state treated as authoritative because the index is stale.
- Overlaps: none in planned implementation paths; shared coordination documents are edited narrowly.
- Resolution: dedicated branch and draft PR; no runtime/datapack/map paths are owned or changed.

# Current state

Branch claimed. Architecture and implementation are starting with the smallest reusable foundation: the read-only unified world index.

# Plan

1. Inspect the exact native scan and item-audit schemas and identify the minimum compatible index contract.
2. Implement deterministic index building and query helpers without adding a new OTBM parser.
3. Add CLI, schema, tests and workflow.
4. Validate against synthetic fixtures and the supplied real OTBM outside Git.
5. Review CI, repair failures, update documentation, and merge this phase before starting the Quest Map Validator.

# Work log

## 2026-07-12T22:16:00+02:00

- Changed: created dedicated branch and claimed phase-one paths.
- Learned: current open work is concentrated in Cyclopedia, Store and tutorial quest fixes; no agent owns the proposed world-index implementation paths.
- Failed/blocked: local Git worktree state cannot be inspected through the connector; GitHub branch/base/open-PR state is used as the authoritative substitute and this limitation is recorded.
- Result: ready to publish the early draft PR and implement the index.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Deliver the full roadmap as sequential independently testable PRs | Combining index, pathfinding, quest semantics, writer and CI in one PR would be unsafe and unreviewable. | planned roadmap document |
| Reuse native item scan rather than write another OTBM parser | Prevents parser drift and honors module reuse rules. | none |
| Keep phase one strictly read-only | Map writing remains prohibited until format detection, backup, bounded patching and round-trip validation exist. | none |

# Files and interfaces

| Path/interface/config/schema | Purpose | Status |
|---|---|---|
| `tools/ai-agent/otbm_world_index.py` | deterministic index builder/query library | planned |
| `tools/ai-agent/otbm_world_index_tool.py` | CLI | planned |
| `canary-otbm-world-index-v1` | downstream JSON contract | planned |
| `docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md` | multi-phase delivery/safety plan | planned |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| | focused Python unit tests and `py_compile` | not-run | implementation pending |
| | real OTBM index smoke outside Git | not-run | supplied map/assets only; no generated artifacts committed |
| | GitHub required checks | not-run | draft PR pending |

Never write `passed` without verification.

# Failed approaches and dead ends

- None yet.

# Risks and compatibility

- Runtime: none; offline tooling only.
- Data/migration: none.
- Security: source paths and hashes must be reviewable; generated indexes remain artifacts.
- Backward compatibility: existing item-audit and script-resolution formats remain supported and unchanged.
- Cross-repo rollout: none for phase one.
- Rollback: revert the tooling PR; no map or production state changes.

# Remaining work

1. Publish the draft PR and implement the index contract.

# Handoff

## Start here

Read this task, `AGENTS.md`, the existing OTBM item audit and script-resolution modules, and `docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md` once created.

## Do not repeat

Do not add a second binary OTBM parser, modify the map, commit binary assets, or treat unresolved dynamic Lua as confirmed behavior.

## Required reads

- `AGENTS.md`
- `docs/agents/ACTIVE_WORK.md`
- `docs/agents/MODULE_CATALOG.md`
- `tools/ai-agent/otbm_item_audit.py`
- `tools/ai-agent/otbm_script_resolution.py`
- `docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md`

## Open questions

- Exact report-size default for position samples will be chosen from real-map cardinality measurements and documented.

# Completion

- Final status: active
- PR:
- Merge commit:
- Catalogue updated: pending
- Changelog updated: pending
- Archived at:
