---
task_id: CAN-20260714-crystal-global-map-comparison
program_id: CAN-PROGRAM-CRYSTALSERVER-COMPARISON
coordination_id: REAL-TIBIA-MAP-AUDIT
status: active
agent: "GPT-5.6 Thinking"
branch: audit/crystal-global-map-comparison
base_branch: main
created: 2026-07-14T08:00:00+02:00
updated: 2026-07-14T08:00:00+02:00
last_verified_commit: "f4e5371906d3b4a33229db2dce6b25d44fb813f0"
risk: low
related_issue: ""
related_pr: ""
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - .github/workflows/real-tibia-crystal-map-audit.yml
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

Perform a deterministic, read-only comparison between the exact supplied OTServBR/Canary-lineage map baseline and the pinned CrystalServer `data-global` map, then publish small reviewable Markdown and JSON evidence for later bounded Targuna/Newhaven integration work.

# Acceptance criteria

- [ ] Pin the exact target Canary main SHA and CrystalServer SHA.
- [ ] Acquire both OTBM files only in CI or outside Git and verify SHA-256/size.
- [ ] Verify the target baseline hash is `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`.
- [ ] Build deterministic World Indexes for both maps using the existing scanner and tool.
- [ ] Compare global tile coordinates, tile metadata, item stacks and map mechanics without implementing a reusable semantic-diff module.
- [ ] Report exact counts, changed-coordinate bounds per floor and top changed 256x256 regions.
- [ ] Compare house, spawn, NPC and zone sidecar inventories and hashes.
- [ ] Identify Targuna/Newhaven evidence and unresolved dependencies without importing any content.
- [ ] Publish concise Markdown and machine-readable JSON reports.
- [ ] Remove the temporary audit workflow before merge.
- [ ] Keep `.otbm`, `.widx`, downloaded archives, client assets and large raw reports outside Git.
- [ ] Verify final CI, review state and autonomous merge gate.

# Confirmed context

- Writable repository: `blakinio/canary` only.
- CrystalServer is read-only and pinned to `fc0d53b9f9965463b6082c07e6d3d482294541a7`.
- The supplied baseline map exists outside Git with size `184,776,037` bytes and SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`.
- PR #311 owns the reusable Semantic OTBM Diff implementation. This task must not edit its paths, API or tests and must not create a competing module.
- A temporary PR-only workflow may perform a one-off exact snapshot audit, upload raw artifacts and print a bounded summary. It must be deleted before merge.
- No map-writing, item substitution, datapack mixing or direct full-map replacement is authorized.

# Existing work to reuse

| Existing work | Reuse | Boundary |
|---|---|---|
| Unified OTBM World Index | Build deterministic indexes and inspect exact tile/placement/mechanic records | Generated `.widx` remains outside Git. |
| Native OTBM scanner | Parse both exact OTBM snapshots | No second binary parser. |
| PR #311 Semantic OTBM Diff | Read-only coordination dependency | Do not duplicate reusable implementation; this task is one-off evidence only. |
| Real Tibia evidence registry | Provenance, source ranking and candidate intake rules | Follow all quarantine/hash/compatibility requirements. |
| CrystalServer comparison program | Pin external source and separate implementation evidence from parity proof | Crystal remains read-only. |

# Ownership and overlap check

- Open PRs inspected on 2026-07-14, including PR #311 (`feat(ai-agent): add semantic OTBM diff`).
- This task owns only a temporary workflow, two new reports and its task record.
- No shared paths and no edit to `ACTIVE_WORK.md`, the OTBM roadmap, module catalogue or Crystal comparison program.
- PR #311 remains the owner of reusable semantic-diff code and documentation.

# Plan

1. Add a bounded PR-only workflow that downloads the configured baseline map and checks out the pinned CrystalServer map with Git LFS.
2. Verify source hashes, compile the existing scanner and build both World Indexes.
3. Run an inline one-off comparison over exact index records and sidecar files; print a bounded JSON summary and upload raw audit artifacts.
4. Convert verified workflow evidence into committed Markdown/JSON reports.
5. Delete the temporary workflow, update this record, run final CI and merge.
6. Archive the task record in a separate lifecycle cleanup PR if required by repository convention.

# Current state

Branch created from current main. No map, index, report or workflow has been committed yet.

# Validation and CI

| Commit | Check | Result | Notes |
|---|---|---|---|
| pending | Agent Task Ownership | not-run | Run after PR creation. |
| pending | one-off map audit workflow | not-run | Must verify both hashes and produce bounded evidence. |
| pending | final repository CI | not-run | Run after temporary workflow removal and report commit. |

# Safety and rollback

- Runtime impact: none; reports only.
- Data impact: none; no map/datapack modification.
- External input: untrusted, pinned and read-only.
- Rollback: revert the documentation commits.
- Temporary workflow is not part of the final merged state.

# Remaining work

All audit and report work remains.

# Handoff

Read `docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md` and this task before touching external map candidates. Do not continue this task by implementing another reusable semantic-diff tool.

# Completion

- Final status: active
- PR:
- Final reviewed head:
- Merge commit:
- Archived at:
