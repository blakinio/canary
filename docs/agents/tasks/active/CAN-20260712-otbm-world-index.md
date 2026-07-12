---
task_id: CAN-20260712-otbm-world-index
coordination_id: "OTS-OTBM-VALIDATION"
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/otbm-world-index-v2
base_branch: main
created: 2026-07-12T22:16:00+02:00
updated: 2026-07-13T00:06:00+02:00
last_verified_commit: "cdc78e55153a3833b37bb6754bcaf63cb8cd1443"
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

- [x] Extend the existing scanner instead of creating a second OTBM parser.
- [x] Index tiles and placements by item ID, AID, UID, house-door ID, teleport destination, exact position and region.
- [x] Preserve hashes, OTBM versions, deterministic ordering and exact counts.
- [x] Preserve the legacy item-audit JSON invocation.
- [x] Bound list output with pagination and exact totals.
- [x] Add focused tests, schema, documentation and dedicated CI.
- [x] Validate against the supplied real map outside Git.
- [x] Keep maps, assets and generated `.widx` artifacts outside Git.
- [x] Update catalogue, changelog and task documentation.
- [x] Confirm no runtime, DB, protocol, datapack or cross-repository change.
- [x] Current-head GitHub checks passed.
- [x] Final changed-file list and review threads are clear.
- [x] Autonomous merge gate satisfied.

# Confirmed context

- PR #190 delivered only the roadmap.
- Conflicted implementation PR #211 was closed and superseded by clean current-main PR #219.
- Coordination policy #214 requires normal task branches to leave `ACTIVE_WORK.md` unchanged; this task file and the live PR are authoritative.
- Real-map source: `/mnt/data/otservbr(4).otbm`, SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`.
- GitHub reports PR #219 mergeable and there are no review threads.

# Existing work reused

| Module | Reuse |
|---|---|
| OTBM item audit | canonical native OTBM traversal and mechanic parsing |
| OTBM script resolution #104 | downstream AID/UID/item/position correlation |
| Factual renderer #154/#161 | Cobra region count cross-check |

# Implemented behavior

- Native mode: `otbm_item_audit_scan --world-index MAP OUTPUT.widx`.
- Fixed little-endian `OTSWIDX1` sections for item directory, canonical areas, area postings, tiles, placements, mechanics and item postings.
- Repeated raw tile-area nodes merge by canonical 256×256×floor key; duplicate exact tile positions fail.
- Python memory-maps and validates the binary before queries.
- CLI supports summary, item, action, unique, house door, teleport destination, exact position and inclusive 3D region.
- Output publication is atomic; symlink targets and accidental overwrite are rejected.
- Legacy `scanner MAP OUTPUT.json` remains unchanged.

# Work log

## 2026-07-12T22:16:00+02:00

- Claimed the phase and confirmed no overlapping implementation.

## 2026-07-12T23:31:00+02:00

- Implemented scanner mode, binary index, mmap reader, CLI, tests, docs and workflow.
- Rejected NDJSON/SQLite after a real-map run exceeded five minutes.
- Reduced 1,175,983 raw tile-area nodes to 1,171 canonical query areas plus postings.

## 2026-07-13T00:06:00+02:00

- Replaced conflicted PR #211 with current-main PR #219.
- Reviewed all 11 changed paths; no forbidden map/asset/generated files are present.
- Current head `cdc78e55153a3833b37bb6754bcaf63cb8cd1443` passed OTBM World Index, OTBM Map Tools, AI Agent Tools and CI.

# Decisions

| Decision | Reason |
|---|---|
| Separate roadmap phases | Quest semantics, pathfinding, spawns and writing have different risks. |
| Extend the existing scanner | Prevents binary parser drift. |
| Use deterministic binary postings | JSON/SQLite was too slow at real-world scale; mmap supports bounded random access. |
| Keep phase one read-only | Safe writer prerequisites remain unsatisfied. |
| Replace #211 instead of force-refreshing | Avoids overwriting concurrent shared documentation and respects #214. |

# Validation and CI

| Source | Check | Result |
|---|---|---|
| local | native compile with `-Wall -Wextra -Wpedantic -Werror` | passed |
| local | `python -m unittest -v test_otbm_world_index.py` | 10 tests passed in 3.015 s |
| local | `python -m py_compile ...` | passed |
| real map | full build plus item/mechanic/position/region queries | passed |
| PR #219 head `cdc78e...` | OTBM World Index run `29210650773` | success |
| PR #219 head `cdc78e...` | OTBM Map Tools run `29210650833` | success |
| PR #219 head `cdc78e...` | AI Agent Tools run `29210650772` | success |
| PR #219 head `cdc78e...` | CI run `29210650805` | success |

## Real-map evidence

```text
source size: 184,776,037 bytes
index size: 842,280,592 bytes
build time: 32.72 s
peak RSS: 419,140 KiB
tiles: 17,972,761
placements: 23,359,571
used item IDs: 23,852
mechanics: 9,339
canonical areas: 1,171
raw area nodes: 1,175,983
unknown attribute tails: 0
maximum item depth: 2
Cobra bounds: 33377,32631,7 -> 33417,32671,7
Cobra tiles: 1,681
Cobra placements: 2,627
```

# Failed approaches

- NDJSON/SQLite exceeded five minutes.
- One directory entry per raw area node made validation unnecessarily expensive.
- PR #211 became conflicted through unrelated shared-document churn.

# Risks and compatibility

- Offline read-only tool; no runtime or migration.
- Generated `.widx` is a large cache and must remain outside Git/client distribution.
- Existing scanner CLI and JSON report remain compatible.
- Rollback is a PR revert with no persistent cleanup.

# Remaining work

1. Mark PR #219 ready and squash-merge.
2. Archive this task in a documentation-only follow-up.
3. Start Quest Map Validator as the next independent phase.

# Handoff

Read PR #219 and `docs/ai-agent/OTBM_WORLD_INDEX.md`. Do not revive #211, edit `ACTIVE_WORK.md`, create another OTBM parser, commit `.widx`, or add map writing.

# Completion

- Final status: ready
- PR: #219
- Merge commit:
- Catalogue updated: yes
- Changelog updated: yes
- Archived at:
