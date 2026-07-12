---
task_id: CAN-20260712-otbm-world-index
coordination_id: "OTS-OTBM-VALIDATION"
status: validating
agent: "GPT-5.6 Thinking"
branch: feat/otbm-world-index-v2
base_branch: main
created: 2026-07-12T22:16:00+02:00
updated: 2026-07-13T00:02:00+02:00
last_verified_commit: "f0f7395dd8088ce05601adedf0806abc678485cc"
risk: medium
related_issue: ""
related_pr: "#219"
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
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
modules_touched:
  - OTBM item audit native scanner
  - OTBM script-resolution input foundation
  - factual OTBM renderer evidence
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

Create a deterministic read-only full-world OTBM index so agents can query items, mechanics, positions, regions and teleport destinations without rescanning or modifying the map.

# Acceptance criteria

- [x] Extend the existing native scanner instead of creating a second OTBM parser.
- [x] Index tiles and placements by item ID, AID, UID, house-door ID, teleport destination, exact position and region.
- [x] Preserve map/scanner/index hashes, OTBM versions, deterministic ordering and exact counts.
- [x] Bound list output with pagination while retaining exact total counts.
- [x] Preserve the legacy scanner JSON invocation.
- [x] Add focused tests, schema, documentation and dedicated CI.
- [x] Validate against the supplied real map outside Git.
- [x] Keep maps, assets and generated `.widx` artifacts outside Git.
- [x] Update catalogue/changelog/task documentation.
- [x] Confirm no cross-repository behavior change.
- [ ] Current-head GitHub checks pass and final diff/reviews are clear.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- PR #190 delivered only the roadmap.
- PR #211 delivered the first implementation branch but became conflicted after unrelated shared-document changes; it is closed and superseded by PR #219.
- PR #219 started from current `main`, does not edit `ACTIVE_WORK.md`, and GitHub currently reports it mergeable.
- Source map: `/mnt/data/otservbr(4).otbm`, SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`.
- No runtime, datapack, DB, protocol, map or OTClient behavior is changed.

# Existing work to reuse

| Module/task/PR | Reuse | Why it fits |
|---|---|---|
| OTBM item audit | canonical native OTBM traversal and mechanic parsing | The new `--world-index` mode shares one parser and keeps legacy output. |
| OTBM script resolution #104 | downstream AID/UID/item/position correlation | Phase 2 can consume indexed evidence without rescanning. |
| Factual renderer #154/#161 | bounded visual evidence | Cobra counts cross-check the world-index region result. |

# Ownership and overlap check

- Open PRs and active task files were inspected before implementation and replacement.
- No other task owns `otbm_world_index*` or the scanner's new mode.
- Per coordination policy #214, `ACTIVE_WORK.md` remains unchanged; this task file and live PR are authoritative.

# Current state

Code, docs, schema, workflow and local/real-map validation are complete on PR #219. Current-head CI and final merge review remain.

# Implemented behavior

- Native scanner mode: `otbm_item_audit_scan --world-index MAP OUTPUT.widx`.
- Fixed little-endian v1 sections for item directory, unique areas, area postings, tiles, placements, mechanics and item postings.
- Repeated raw tile-area nodes are merged by canonical 256×256×floor key; duplicate exact tile positions fail the build.
- Python reader memory-maps and validates section ranges/record sizes before querying.
- Build wrapper records source/scanner/index hashes and publishes the output atomically.
- Query CLI supports summary, item, action, unique, house door, teleport destination, exact position and inclusive 3D region.
- Generated index and manifest remain local/workflow artifacts.

# Work log

## 2026-07-12T22:16:00+02:00

- Claimed the roadmap and confirmed no overlapping implementation.

## 2026-07-12T23:31:00+02:00

- Implemented the binary index, memory-mapped reader, CLI, tests, docs and workflow.
- Abandoned NDJSON/SQLite after a real-map run exceeded five minutes.
- Replaced a raw 1,175,983-entry area directory with 1,171 unique query areas and postings.

## 2026-07-13T00:02:00+02:00

- Replaced conflicted PR #211 with current-main PR #219.
- Reused reviewed Git blobs directly, preserved current shared coordination policy and closed #211 as superseded.

# Decisions

| Decision | Reason/evidence |
|---|---|
| Separate roadmap phases into independent PRs | Quest semantics, pathfinding, spawns and writing have different risks. |
| Extend the existing scanner | Avoids binary-parser drift. |
| Use an uncompressed deterministic postings index | Real-map JSON/SQLite generation was too slow; mmap enables bounded random access. |
| Keep phase one read-only | Safe writer prerequisites are not yet satisfied. |
| Replace rather than force-refresh PR #211 | Prevents overwriting concurrent shared documentation and respects policy #214. |

# Files and interfaces

| Path/interface | Purpose | Status |
|---|---|---|
| `tools/ai-agent/otbm_item_audit_scan.cpp` | legacy scan plus native index generation | implemented |
| `tools/ai-agent/otbm_world_index.py` | validator, builder wrapper and query library | implemented |
| `tools/ai-agent/otbm_world_index_tool.py` | CLI | implemented |
| `tools/ai-agent/test_otbm_world_index.py` | focused regression tests | implemented |
| `OTSWIDX1` | deterministic binary format v1 | implemented |
| `canary-otbm-world-index-v1` | JSON provenance/summary manifest | implemented |

# Validation and CI

| Source | Command/check | Result | Evidence |
|---|---|---|---|
| local source | `c++ -O2 -std=c++20 -Wall -Wextra -Wpedantic -Werror ...` | passed | native scanner compiled cleanly. |
| local source | `PYTHONPATH=. python -m unittest -v test_otbm_world_index.py` | passed | 10 tests in 3.015s. |
| local source | `python -m py_compile ...` | passed | no syntax errors. |
| supplied real map | build plus item/mechanic/position/region queries | passed | counts below. |
| PR #219 head | OTBM World Index | passed | current dedicated run verified; remaining repository checks pending. |

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

- NDJSON/SQLite exceeded five minutes on the real map.
- One directory record per raw area node made validation unnecessarily expensive.
- PR #211 was not force-refreshed because it conflicted through unrelated shared-document churn.

# Risks and compatibility

- Runtime/data migration: none; offline read-only tooling.
- Security: output symlinks are rejected, publication is atomic, source binaries stay outside Git.
- Performance: `.widx` is a large generated cache and must not be shipped as a client asset.
- Backward compatibility: legacy scanner invocation and JSON format remain unchanged.
- Cross-repo rollout: none.
- Rollback: revert PR #219; no persistent cleanup.

# Remaining work

1. Observe current-head repository checks.
2. Review complete changed-file list and review threads.
3. Mark ready and squash-merge.
4. Archive the task and start Quest Map Validator separately.

# Handoff

## Start here

Read PR #219, this task and `docs/ai-agent/OTBM_WORLD_INDEX.md`, then inspect current-head checks.

## Do not repeat

Do not revive #211, edit `ACTIVE_WORK.md`, create another OTBM parser, commit `.widx`, or add map writing.

## Required reads

- `AGENTS.md`
- `docs/agents/tasks/active/CAN-20260712-otbm-world-index.md`
- `docs/agents/MODULE_CATALOG.md`
- `docs/ai-agent/OTBM_WORLD_INDEX.md`
- `docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md`

# Completion

- Final status: validating
- PR: #219
- Merge commit:
- Catalogue updated: yes
- Changelog updated: yes
- Archived at:
