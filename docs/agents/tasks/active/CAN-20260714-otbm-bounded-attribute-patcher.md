---
task_id: CAN-20260714-otbm-bounded-attribute-patcher
program_id: ""
coordination_id: "OTS-OTBM-VALIDATION"
status: active
agent: "GPT-5.6 Thinking"
branch: feat/otbm-bounded-attribute-patcher
base_branch: main
created: 2026-07-14T12:00:00+02:00
updated: 2026-07-14T12:00:00+02:00
last_verified_commit: "9b04ab3ef3dfbc9440274d63e15e6102c5501d85"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - "merged and archived Unified OTBM World Index #219/#223"
  - "merged and archived Semantic OTBM Diff #311/#315"
  - "merged bounded Semantic OTBM Diff ordering fix #319"
  - "merged and archived OTBM geometry audit #322/#323"
blocks:
  - "any broader tile/item-stack OTBM writer"
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_item_audit_scan.cpp
    - tools/ai-agent/otbm_bounded_patch.py
    - tools/ai-agent/otbm_bounded_patch_types.py
    - tools/ai-agent/otbm_bounded_patch_tool.py
    - tools/ai-agent/test_otbm_bounded_patch.py
    - docs/ai-agent/OTBM_BOUNDED_PATCH.md
    - docs/ai-agent/OTBM_BOUNDED_PATCH_PLAN.schema.json
    - docs/ai-agent/OTBM_BOUNDED_PATCH_RESULT.schema.json
    - docs/agents/decisions/ADR-20260714-otbm-fixed-width-patch-boundary.md
    - .github/workflows/otbm-bounded-patch.yml
    - docs/agents/tasks/active/CAN-20260714-otbm-bounded-attribute-patcher.md
  shared: []
  read_only:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
    - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
    - tools/ai-agent/otbm_world_index.py
    - tools/ai-agent/otbm_semantic_diff.py
    - tools/ai-agent/otbm_semantic_diff_analysis.py
    - tools/ai-agent/otbm_semantic_diff_tool.py
    - tools/ai-agent/otbm_renderer.py
    - tools/ai-agent/otbm_render_tool.py
modules_touched:
  - native OTBM scanner patch-anchor surface
  - safe bounded OTBM existing-attribute patcher
reuses:
  - existing native OTBM parser/scanner
  - canary-otbm-world-index-v1
  - canary-otbm-semantic-diff-v1
  - existing factual OTBM renderer
public_interfaces:
  - canary-otbm-patch-anchors-v1
  - canary-otbm-bounded-patch-plan-v1
  - canary-otbm-bounded-patch-result-v1
  - OTBM bounded patch CLI
cross_repo_tasks: []
---

# Goal

Deliver the first Phase 8 safety surface: deterministic, manifest-driven mutation of an **existing fixed-width mechanic attribute only** on a new OTBM copy, with exact expected state, source hash/version, bounded region, byte-level outside-change equality proof, full reparse, canonical World Index/Semantic Diff validation and factual render instructions.

# Initial supported operations

Only existing item-node attributes are eligible:

1. `set-action-id` — existing `ATTR_ACTION_ID`, unsigned 16-bit;
2. `set-unique-id` — existing `ATTR_UNIQUE_ID`, unsigned 16-bit;
3. `set-house-door-id` — existing `ATTR_HOUSEDOOR_ID`, unsigned 8-bit;
4. `set-teleport-destination` — existing `ATTR_TELE_DEST`, exact `x,y,z` encoded as 16/16/8 bits.

No attribute may be inserted or removed. Item IDs, counts, stack order, tile kind/flags/house ID, text, node structure and file length are out of scope.

# Acceptance criteria

- [ ] Extend the existing native scanner rather than adding a second OTBM parser.
- [ ] Add `canary-otbm-patch-anchors-v1` with exact source hash/size/OTBM version and supported attribute byte spans.
- [ ] Identify every target by exact `x,y,z`, tile-local placement index, item ID, item depth, attribute kind and expected value.
- [ ] Require an explicit inclusive region capped at 1,000,000 coordinates and reject operations outside it.
- [ ] Require exact source SHA-256/size and compatible OTBM/items versions in the plan.
- [ ] Reject missing, duplicate, ambiguous or dynamically unsupported targets.
- [ ] Preserve file length and OTBM escaping width; fail closed when replacement bytes would change encoded width.
- [ ] Write only to a distinct output path below an explicit artifact root; never modify source in place.
- [ ] Refuse symlink/path escape/overwrite by default and write atomically.
- [ ] Prove byte equality outside the exact planned encoded spans and report every changed physical offset.
- [ ] Fully reparse the patched copy with the existing scanner and regenerate canonical World Index evidence.
- [ ] Run bounded Semantic OTBM Diff and require that only the planned mechanic changes appear.
- [ ] Emit rollback instructions that retain the untouched source and identify the patched copy by hash.
- [ ] Emit factual render requests through the existing renderer only; no AI-generated imagery.
- [ ] Add schemas, ADR, documentation, focused synthetic round-trip/tamper/escape-width tests and dedicated CI artifacts.
- [ ] Keep source/target `.otbm`, `.widx`, appearances, client assets, generated reports and renders outside Git.
- [ ] Confirm no active datapack, gameplay, item definition, protocol, database or OTClient change.
- [ ] Update catalogue/changelog/roadmap only after shared owners #317/#324 release those paths.
- [ ] Review exact final diff, current-main synchronization, all required current-head checks and zero review threads.
- [ ] Squash-merge and archive separately.

# Safety invariants

- Source map remains byte-for-byte untouched.
- Output path must differ from source and reside under `artifact_root`.
- Plan pins source SHA-256, byte size, OTBM version, items major/minor and one bounded region.
- Every operation pins exact target identity and expected old value.
- Only scanner-proven payload bytes may change.
- Logical replacement bytes must retain the same physical OTBM escape width byte-by-byte.
- Changed physical offsets are pairwise disjoint.
- Output byte size equals source byte size.
- A direct byte comparison proves equality outside declared spans.
- Full scanner parse and World Index build must succeed after mutation.
- Semantic validation must not infer intent and must find no unplanned change.
- No generated binary or report is committed.

# Confirmed context

- Task-start `main`: `9b04ab3ef3dfbc9440274d63e15e6102c5501d85`, after Phase 7 lifecycle merge #323.
- Roadmap marks Phase 8 not started and explicitly requires a fresh bounded task.
- No existing Phase 8 task, branch, PR or reusable map writer was found.
- The native scanner already parses item mechanics and OTBM escape encoding; this task extends it with byte-span evidence instead of creating another parser.
- Current open PR #316 is a donor-map audit and owns no scanner/writer path.
- Current open #317 and #324 own shared catalogue/changelog documentation only; those paths remain read-only here until released.
- Upstream `opentibiabr/*` and Remere's Map Editor remain read-only evidence sources.
- User-supplied `/mnt/data/otservbr(4).otbm` and `/mnt/data/assets(1).zip` are external evidence only. The source map will not be modified; no real-map patch will run until the implementation and safety workflow are complete.
- Local Git/network checkout remains unavailable after the recorded DNS failures; GitHub API/Actions provide repository validation and no local repository pass will be claimed.

# Existing work to reuse

| Module/task/PR | Reuse | Why it fits |
|---|---|---|
| Native OTBM scanner | Existing structural parse and escape decoding | Extend `PropertyReader` with physical spans; do not parse OTBM in Python. |
| World Index | Exact tile-local placement ordering and mechanic values | Verify plan target identity and regenerate target evidence. |
| Semantic OTBM Diff | Exact mechanic-change validation | Require bounded output changes to match the plan. |
| Geometry audit | Region bounds and external-artifact safety patterns | Reuse bounded/path/provenance conventions, not its findings. |
| Factual renderer | Real OTBM/client-asset render path | Emit commands/manifests only; no competing renderer. |

# Ownership and overlap

- Exclusive existing path: `tools/ai-agent/otbm_item_audit_scan.cpp`; no open PR declares it.
- Exclusive new paths: patcher modules/tests/schemas/docs/workflow/ADR/task.
- Shared paths: none during implementation bootstrap.
- Read-only shared documentation: catalogue, changelog and roadmap while #317/#324 are open.
- `ACTIVE_WORK.md` remains unchanged.
- No upstream write or cross-repository rollout.

# Plan

1. Add scanner patch-anchor output with physical encoded spans and exact target identities.
2. Fix plan/result schemas and a fail-closed Python orchestrator.
3. Add synthetic OTBM tests for successful existing-attribute replacements and every safety rejection.
4. Add full reparse, World Index, Semantic Diff, outside-span equality and artifact workflow.
5. Open draft PR early and iterate from workflow evidence.
6. Refresh shared docs after owners release them; verify exact diff and merge gate.
7. Archive Phase 8 separately.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Patch existing fixed-width attributes only | Preserves node structure and confines mutation to scanner-proven payloads. | planned |
| Preserve encoded width per logical byte | OTBM escaping can otherwise change file length and invalidate offsets/tree structure. | planned |
| Require tile-local placement index plus redundant identity | Disambiguates duplicate item IDs on one tile without relying on inferred intent. | planned |
| Prove outside-span byte equality | Stronger than relying only on semantic reports. | planned |
| Source map is never an output | Makes rollback immediate and prevents in-place corruption. | planned |

# Validation and CI

| Commit | Check | Result | Evidence |
|---|---|---|---|
| pending | scanner compile with warnings as errors | not-run | dedicated workflow |
| pending | focused patcher tests | not-run | dedicated workflow |
| pending | full parse/index/diff round trip | not-run | dedicated workflow |
| pending | repository Required | not-run | final current head |

# Risks and compatibility

- Risk: high because binary map mutation is introduced, even though the first scope is fixed-width and copy-only.
- Runtime: none; offline tooling only.
- Data migration: none; no active map is modified.
- Compatibility: existing scanner JSON and World Index modes must remain byte/contract compatible.
- Rollback: delete the patched copy and retain the pinned untouched source; repository rollback is a squash revert.

# Remaining work

1. Implement scanner anchor evidence and focused tests.

# Handoff

## Start here

Read this task, the Phase 8 roadmap section, scanner source, World Index/Semantic Diff contracts and the fixed-width ADR when added.

## Do not repeat

Do not create another OTBM parser, add/remove attributes, serialize the whole map, modify the uploaded source map, weaken escape handling, skip full reparse/diff validation or treat a clean semantic diff as player-intent proof.

## Open questions

- None for the initial fixed-width existing-attribute scope. Broader operations require a later explicit safety review.

# Completion

- Final status: active
- PR:
- Final feature head:
- Merge commit:
- Cleanup PR:
- Archived at:
