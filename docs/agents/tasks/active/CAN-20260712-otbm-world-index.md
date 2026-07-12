---
task_id: CAN-20260712-otbm-world-index
coordination_id: "OTS-OTBM-VALIDATION"
status: validating
agent: "GPT-5.6 Thinking"
branch: feat/otbm-world-index-implementation
base_branch: main
created: 2026-07-12T22:16:00+02:00
updated: 2026-07-12T23:31:00+02:00
last_verified_commit: "6f82901d16285f8d7b65f4fd68de8250d738e823"
risk: medium
related_issue: ""
related_pr: "#211"
depends_on:
  - "merged OTBM item audit"
  - "merged OTBM script-resolution audit #104"
  - "merged factual OTBM renderer and HD pipeline #154/#161"
  - "merged roadmap-only PR #190"
blocks:
  - "Quest Map Validator phase"
  - "teleport/pathfinding validation phase"
  - "OTBM semantic diff phase"
owned_paths:
  - tools/ai-agent/otbm_item_audit_scan.cpp
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
  - OTBM item audit native scanner
  - OTBM script-resolution audit input foundation
  - OTBM factual renderer region evidence
reuses:
  - tools/ai-agent/otbm_item_audit.py
  - tools/ai-agent/otbm_item_audit_scan.cpp
  - tools/ai-agent/otbm_script_resolution.py
  - tools/ai-agent/otbm_renderer.py
public_interfaces:
  - "OTSWIDX1 binary layout version 1"
  - "canary-otbm-world-index-v1 manifest"
  - "canary-otbm-world-query-v1 query result"
  - "OTBM world index CLI"
cross_repo_tasks: []
---

# Goal

Create a deterministic read-only world index that turns one full OTBM scan into a queryable local artifact for items, mechanics, positions, teleport destinations, tile occupancy and provenance, without rescanning or modifying the map for every downstream audit.

# Acceptance criteria

- [x] Extend the existing native OTBM scanner; do not create a second binary parser.
- [x] Index every tile/item placement and positions by `itemId`, `actionId`, `uniqueId`, `houseDoorId`, and teleport destination.
- [x] Preserve map/scanner/index SHA-256, OTBM versions, deterministic ordering and exact counts.
- [x] Provide CLI queries for summary, position, region, item ID, action ID, unique ID, house door and teleport destination.
- [x] Bound query output with pagination while preserving exact total counts.
- [x] Add focused tests for determinism, repeated area nodes, duplicates, bounds, corrupt input, provenance, overwrite and symlink safety.
- [x] Add schema, documentation, dedicated CI and the staged roadmap.
- [x] Validate against the supplied real OTBM outside Git.
- [x] Confirm no `.otbm`, `items.otb`, appearance/client asset or generated `.widx` is committed.
- [x] Cross-repository impact is none for this phase.
- [ ] Refresh against current `main`, complete current-head GitHub checks and review the final changed-file list.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- Roadmap-only PR #190 merged without the implementation; actual code is in PR #211.
- Implementation branch started from `main` commit `366b3d4e6bba4cb8d3dee09a8c5a0181cc3d7423`; `main` advanced during work and requires a final refresh.
- The source map used for the real smoke is `/mnt/data/otservbr(4).otbm`, SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`.
- Existing native legacy scan mode remains available as `scanner MAP OUTPUT.json`.
- No map, assets, datapack, runtime, DB, protocol or OTClient behavior is changed.

# Existing work reused

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| OTBM item audit | one canonical binary parser and mechanic vocabulary | `tools/ai-agent/otbm_item_audit_scan.cpp` | New `--world-index` mode shares the same parser and preserves legacy output. |
| OTBM script resolution / #104 | future handler correlation | `tools/ai-agent/otbm_script_resolution.py` | Indexed AID/UID/item/position evidence is the input foundation for the next quest phase. |
| Factual renderer / #154/#161 | bounded region evidence | `tools/ai-agent/otbm_renderer.py`, `otbm_hd.py` | Real Cobra region counts were cross-checked against prior factual renders. |

# Ownership and overlap check

- Open PRs were inspected before branch creation and again before PR #211; none owns `otbm_world_index*` or changes the world-index mode of the native scanner.
- Shared coordination files are edited narrowly.
- No active map, datapack or asset paths are owned by this task.

# Current state

Implementation, local synthetic validation, real-map smoke, schema, documentation and dedicated workflow are complete. PR #211 is draft while its branch is refreshed to current `main` and current-head workflows finish.

# Implemented behavior

- The native scanner accepts `--world-index MAP OUTPUT.widx` and performs two deterministic passes over one in-memory OTBM source.
- Binary v1 uses fixed little-endian records for an item directory, unique-area directory, area postings, tiles, placements, mechanics and item postings.
- Repeated raw tile-area nodes with the same 256×256×floor key are merged; duplicate exact tile positions are rejected.
- Python opens `.widx` with `mmap`, validates all section offsets/record sizes, and exposes bounded query helpers.
- Build wrapper verifies source stability, map/scanner/index hashes, scanner JSON vs binary counts and atomic output publication.
- Queries return stable placement ordinals, exact position, item depth/source and mechanic attributes.
- Pagination is capped at 10,000 results per page.

# Work log

## 2026-07-12T22:16:00+02:00

- Changed: claimed the roadmap and phase-one paths.
- Learned: no overlapping implementation existed.
- Failed/blocked: connector-only repository access prevented local Git worktree inspection; GitHub state remained authoritative.
- Result: roadmap PR #190 published.

## 2026-07-12T23:31:00+02:00

- Changed: implemented native binary generation, memory-mapped Python reader, CLI, ten focused tests, schema, docs and CI in PR #211.
- Learned: the real world contains 17,972,761 tiles and 23,359,571 placements; emitting a giant JSON/SQLite import is the wrong hot-path representation. A deterministic binary postings index builds in 32.72 seconds and supports direct queries.
- Failed/blocked: an initial NDJSON/SQLite prototype exceeded five minutes; an initial directory containing 1,175,983 raw area records made reader validation unnecessarily expensive. Both were discarded. The final format merges those nodes into 1,171 unique query areas with area postings.
- Result: real source indexed successfully with zero unknown attribute tails; Cobra query returned 1,681 tiles and 2,627 placements.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Deliver roadmap phases as separate PRs | Quest semantics, pathfinding and patch writing have different risks and evidence requirements. | roadmap document |
| Extend `otbm_item_audit_scan.cpp` | Prevents parser drift and preserves one canonical OTBM traversal. | documented in `OTBM_WORLD_INDEX.md` |
| Use deterministic uncompressed binary postings plus JSON manifest | Real map scale made JSON/SQLite generation too slow and memory-heavy; mmap supports bounded random queries. | documented in `OTBM_WORLD_INDEX.md` |
| Merge repeated raw tile-area nodes by canonical area key | Real map has 1,175,983 raw nodes but only 1,171 unique 256×256×floor query areas. | documented in format section |
| Keep the feature read-only | Writer prerequisites remain unsatisfied and outside phase one. | roadmap phase 8 |

# Files and interfaces

| Path/interface/config/schema | Purpose | Status |
|---|---|---|
| `tools/ai-agent/otbm_item_audit_scan.cpp` | legacy scan plus native world-index generation | implemented |
| `tools/ai-agent/otbm_world_index.py` | binary validator, build wrapper and query library | implemented |
| `tools/ai-agent/otbm_world_index_tool.py` | build/query CLI | implemented |
| `tools/ai-agent/test_otbm_world_index.py` | focused synthetic regression suite | implemented |
| `docs/ai-agent/OTBM_WORLD_INDEX.md` | format, usage, safety and real evidence | implemented |
| `docs/ai-agent/OTBM_WORLD_INDEX.schema.json` | JSON manifest schema | implemented |
| `.github/workflows/otbm-world-index.yml` | dedicated build/test/compile/schema check | implemented |

# Validation and CI

| Commit/source | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| local implementation | `c++ -O2 -std=c++20 -Wall -Wextra -Wpedantic -Werror ...` | passed | native scanner compiled with warnings as errors. |
| local implementation | `PYTHONPATH=. python -m unittest -v test_otbm_world_index.py` | passed | 10 tests in 3.015s. |
| local implementation | `python -m py_compile otbm_world_index.py otbm_world_index_tool.py test_otbm_world_index.py` | passed | no syntax errors. |
| supplied real map | build and bounded query smoke | passed | 32.72 s; peak RSS 419,140 KiB; 842,280,592-byte index; exact counts below. |
| PR #211 current head | AI Agent Tools / OTBM Map Tools / CI / dedicated workflow | pending | inspect current-head runs after shared docs and base refresh. |

## Real-map evidence

```text
map SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
source size: 184,776,037 bytes
index size: 842,280,592 bytes
build wall time: 32.72 s
peak RSS: 419,140 KiB
tiles: 17,972,761
placements: 23,359,571
used item IDs: 23,852
mechanic placements: 9,339
unique areas: 1,171
raw area nodes: 1,175,983
unknown attribute tails: 0
maximum item depth: 2
Cobra bounds: 33377,32631,7 -> 33417,32671,7
Cobra tiles: 1,681
Cobra placements: 2,627
```

# Failed approaches and dead ends

- NDJSON plus SQLite was abandoned after exceeding five minutes on the real map; it did not meet the intended reusable-agent latency.
- Storing one directory record per raw tile-area node produced 1,175,983 Python validation iterations. The final format stores one canonical area entry plus tile postings.
- A temporary connector bootstrap commit was used only to materialize the validated local sources because shell GitHub access was unavailable; all payload/workflow bootstrap files were deleted automatically, leaving only the four intended implementation files.

# Risks and compatibility

- Runtime: none; offline tool only.
- Data/migration: none.
- Security: output paths reject symlinks; publication is atomic; plaintext source map content is not copied into Git.
- Performance: full indexes are large generated caches; they must not be committed or distributed as client assets.
- Backward compatibility: the original native scanner invocation and JSON format remain unchanged.
- Cross-repo rollout: none.
- Rollback: revert PR #211; no map or persistent state cleanup.

# Remaining work

1. Refresh PR #211 to current `main` without losing implementation commits.
2. Update shared catalogue/changelog/index and inspect the complete diff.
3. Observe current-head workflows, fix actual failures, mark ready and squash-merge.
4. Archive this task and start the Quest Map Validator as a separate branch/PR.

# Handoff

## Start here

Read PR #211, this task and `docs/ai-agent/OTBM_WORLD_INDEX.md`; inspect current head, base divergence, changed files and workflow logs.

## Do not repeat

Do not reintroduce NDJSON/SQLite as the full-world hot path, create another OTBM parser, commit generated `.widx`, or add map writing to this PR.

## Required reads

- `AGENTS.md`
- `docs/agents/ACTIVE_WORK.md`
- `docs/agents/MODULE_CATALOG.md`
- `docs/ai-agent/OTBM_WORLD_INDEX.md`
- `docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md`
- `tools/ai-agent/otbm_item_audit_scan.cpp`
- `tools/ai-agent/otbm_world_index.py`

## Open questions

- None for phase one; later phases decide appearance/walkability joins and quest evidence schema.

# Completion

- Final status: validating
- PR: #211
- Merge commit:
- Catalogue updated: pending
- Changelog updated: pending
- Archived at:
