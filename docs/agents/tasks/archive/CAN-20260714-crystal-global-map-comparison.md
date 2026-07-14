---
task_id: CAN-20260714-crystal-global-map-comparison
program_id: CAN-PROGRAM-CRYSTALSERVER-COMPARISON
coordination_id: REAL-TIBIA-MAP-AUDIT
status: merged
agent: "GPT-5.6 Thinking"
branch: audit/crystal-global-map-comparison
base_branch: main
created: 2026-07-14T08:00:00+02:00
updated: 2026-07-14T10:05:00+02:00
last_verified_commit: "7a825e7ba25e359f30c3f51627a658d729ca7ac7"
risk: low
related_issue: ""
related_pr: "#313"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/ai-agent/REAL_TIBIA_CRYSTAL_MAP_AUDIT.md
    - docs/ai-agent/REAL_TIBIA_CRYSTAL_MAP_AUDIT.json
    - docs/agents/tasks/active/CAN-20260714-crystal-global-map-comparison.md
  shared: []
  read_only:
    - AGENTS.md
    - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
    - docs/ai-agent/OTBM_WORLD_INDEX.md
    - docs/ai-agent/OTBM_HD_PIPELINE.md
    - docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md
    - tools/ai-agent/otbm_item_audit_scan.cpp
    - tools/ai-agent/otbm_world_index.py
    - tools/ai-agent/otbm_world_index_tool.py
modules_touched:
  - read-only external map evidence audit
reuses:
  - Unified OTBM World Index
  - existing native OTBM scanner
  - existing CrystalServer comparison program
public_interfaces: []
cross_repo_tasks:
  - repository: zimbadev/crystalserver
    mode: read-only
    ref: fc0d53b9f9965463b6082c07e6d3d482294541a7
---

# Goal

Perform a deterministic, read-only comparison between the exact supplied OTServBR/Canary-lineage map baseline and the pinned CrystalServer `data-global` map, then publish small reviewable Markdown and JSON evidence for bounded Targuna/Newhaven integration work.

# Acceptance criteria

- [x] Pin the exact target Canary base SHA and CrystalServer SHA.
- [x] Acquire both OTBM files only in CI/outside Git and verify SHA-256 and size.
- [x] Verify the baseline hash `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`.
- [x] Build deterministic World Indexes for both maps using the existing scanner/tool.
- [x] Compare global tile coordinates, metadata, item stacks and mechanics without adding a reusable diff module.
- [x] Report exact counts, per-floor changed bounds and top changed 256x256 regions.
- [x] Compare house, monster/spawn, NPC and zone sidecar inventories/hashes.
- [x] Identify Targuna/Newhaven evidence and unresolved dependencies without importing content.
- [x] Publish concise Markdown and machine-readable JSON reports.
- [x] Remove every temporary workflow and audit script before merge.
- [x] Keep `.otbm`, `.widx`, archives, client assets and large raw reports outside Git.
- [x] Verify final-head CI, review state and autonomous merge gate.

# Exact source provenance

| Source | Stored form | Size | SHA-256 |
|---|---|---:|---|
| Canary baseline | plain OTBM | 184,776,037 | `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2` |
| Crystal repository blob | gzip despite `.otbm` extension | 52,836,960 | `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034` |
| Crystal logical OTBM | decompressed | 186,660,172 | `4b2099f38df05d4be68d1ba1265754e9fd6da09742025d92644fa4b1a12eb120` |

- Canary comparison base: `bd5c7bee5a0524dedcd786ef52152f475dd424a6`.
- CrystalServer pin: `fc0d53b9f9965463b6082c07e6d3d482294541a7`.
- Both logical OTBMs use version 4, item major/minor 4/4, dimensions 35143x34812, maximum item depth 2 and zero unknown attribute tails.

# Delivered findings

The exact merge-scan covered 19,099,041 coordinates present in either snapshot:

- shared coordinates: 17,871,388;
- identical shared coordinates: 17,214,872;
- changed shared coordinates: 656,516;
- Canary-only tiles: 101,373;
- Crystal-only tiles: 1,126,280;
- shared item-stack changes: 639,821;
- shared metadata changes: 19,531;
- shared mechanic changes: 382;
- any changed coordinate: 1,884,169, or 9.87% of the coordinate union.

Crystal has 18,997,668 tiles and 24,504,223 placements versus 17,972,761 tiles and 23,359,571 placements in the baseline. It has 9,323 mechanic placements versus 9,339 in the baseline.

The evidence rejects complete-map replacement. Differences are global and one-sided bounds reach coordinates near 1000/1000, far outside the principal global-map cluster. Crystal is a donor for bounded newer regions, not a clean successor snapshot.

# Targuna and Newhaven evidence

- Crystal adds house 3701 `Targuna Cottage 1` at `31962,31911,7`.
- Crystal adds house 3702 `Targuna Cottage 2` at `31940,31890,7`.
- No houses are removed; shared house IDs 2819, 3205, 3654 and 3660 differ.
- Crystal contains 15 Targuna quest scripts absent from Canary.
- Crystal contains seven Newhaven quest scripts absent from Canary.
- NPC sidecar count is 1043 in Crystal versus 1007 in Canary.
- Zone sidecars are byte-identical by SHA-256.
- Monster/spawn sidecars have different Git blob SHAs and require separate semantic runtime resolution.

# Reports

- `docs/ai-agent/REAL_TIBIA_CRYSTAL_MAP_AUDIT.md`
- `docs/ai-agent/REAL_TIBIA_CRYSTAL_MAP_AUDIT.json`

The JSON records exact source/index hashes, OTBM summaries, comparison counts, per-floor changed bounds, top changed regions, houses, sidecar identifiers and Targuna/Newhaven file inventories.

# Existing work reused

| Existing work | Reuse | Boundary |
|---|---|---|
| Unified OTBM World Index | Deterministic indexes and exact records | Generated `.widx` stayed outside Git. |
| Native OTBM scanner | Parsed both logical OTBM snapshots | No second binary parser. |
| PR #311 Semantic OTBM Diff | Coordination dependency | No competing reusable module/API/tests. |
| Real Tibia evidence registry | Provenance, source ranking and intake rules | External inputs remained pinned/read-only. |
| CrystalServer comparison program | Separates implementation evidence from parity proof | Crystal remained read-only. |

# Work log

## Initial setup

- Created branch and draft PR #313.
- Added a temporary PR-only audit workflow using the existing scanner and World Index.
- First run failed before indexing because it imposed an unjustified `>100 MB` Crystal blob-size assumption.

## Source-format diagnosis

- Verified baseline download, size and hash.
- Verified Crystal Git LFS checkout.
- Captured Crystal stored blob as 52,836,960 bytes with gzip magic `1f8b`.
- The native scanner correctly rejected compressed bytes with `Missing OTBM root node`.
- Added explicit gzip decompression while preserving stored and logical hashes separately.

## Successful exact audit

- Workflow run `29315216124` succeeded on head `f6d9cc5c62170864e494806bdbf57aefa5b465cd`.
- Baseline index: 842,280,592 bytes, SHA-256 `6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a`.
- Crystal index: 887,242,734 bytes, SHA-256 `c2bc741ad023f9bd7cad64a7b3b60adb1143243c8def37d2f3ab64e07d6b9ed3`.
- Exact coordinate comparison completed in 88.71 seconds with about 1.58 GB peak RSS.
- Bounded evidence artifact `8303695620` was retained for 14 days.

## Publication and cleanup

- Added Markdown and compact machine-readable JSON reports.
- Added verified monster sidecar Git blob identifiers.
- Removed every temporary audit workflow and script.
- Final PR diff contained only the two reports and the task record.
- No binary map, index, archive, client asset or large generated artifact remained.

## Merge

- Final reviewed head: `7a825e7ba25e359f30c3f51627a658d729ca7ac7`.
- No requested changes and no unresolved review threads.
- PR #313 was squash-merged as `6bc54ad4796dbc04c3334e8596d3a229146781ce`.

# Validation and CI

| Commit/run | Check | Result | Notes |
|---|---|---|---|
| `f6d9cc5c62170864e494806bdbf57aefa5b465cd` / run `29315216124` | exact two-map audit | passed | Source verification, decompression, both indexes, coordinate comparison and artifact upload succeeded. |
| `7a825e7ba25e359f30c3f51627a658d729ca7ac7` / run `29315907343` | Agent Task Ownership | passed | Final owned paths were valid and non-overlapping. |
| `7a825e7ba25e359f30c3f51627a658d729ca7ac7` / run `29315907339` | AI Agent Tools | passed | Agent documentation/tooling validation succeeded. |
| `7a825e7ba25e359f30c3f51627a658d729ca7ac7` / run `29315995982` | ready-state CI | passed | Fast Checks, Lua Tests, Linux Release and aggregate `Required` succeeded. |
| PR #313 | reviews and threads | passed | No reviews requesting changes and zero unresolved threads. |

# Safety and rollback

- Runtime impact: none; reports only.
- Data impact: none; no map/datapack modification.
- External input: pinned, read-only and kept outside Git.
- Rollback: revert merge commit `6bc54ad4796dbc04c3334e8596d3a229146781ce`.

# Remaining work

None for this global comparison task. Future work must be separate and bounded:

1. isolate Targuna coordinates and dependencies;
2. resolve Targuna NPCs, spawns, scripts, storages, transitions, items and assets;
3. repeat independently for Newhaven;
4. prepare a region patch plan without writing an OTBM until map-writing safety is explicitly authorized.

# Handoff

Read `docs/ai-agent/REAL_TIBIA_CRYSTAL_MAP_AUDIT.md` and its JSON companion. The next work is bounded donor isolation and dependency resolution, not another global comparison and not a whole-map replacement.

# Completion

- Final status: merged
- PR: #313
- Final reviewed head: `7a825e7ba25e359f30c3f51627a658d729ca7ac7`
- Merge commit: `6bc54ad4796dbc04c3334e8596d3a229146781ce`
- Program record updated: not required; no active queue mutation was authorized
- Module catalogue updated: not required; no reusable interface was added
- Changelog updated: not required; no runtime behavior changed
- Archived at: `docs/agents/tasks/archive/CAN-20260714-crystal-global-map-comparison.md`
