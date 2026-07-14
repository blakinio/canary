---
task_id: CAN-20260714-otbm-bounded-attribute-patcher
program_id: ""
coordination_id: "OTS-OTBM-VALIDATION"
status: active
agent: "GPT-5.6 Thinking"
branch: feat/otbm-bounded-attribute-patcher
base_branch: main
created: 2026-07-14T12:00:00+02:00
updated: 2026-07-14T13:30:00+02:00
last_verified_commit: "3a390c9d892c5b737d32711a71dbdf7fff1f06fe"
risk: high
related_issue: ""
related_pr: "#325"
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

- [x] Extend the existing native scanner rather than adding a second OTBM parser.
- [x] Add `canary-otbm-patch-anchors-v1` with exact source hash/size/OTBM version and supported attribute byte spans.
- [x] Identify every target by exact `x,y,z`, tile-local placement index, item ID, item depth, attribute kind and expected value.
- [x] Require an explicit inclusive region capped at 1,000,000 coordinates and reject operations outside it.
- [x] Require exact source SHA-256/size and compatible OTBM/items versions in the plan.
- [x] Reject missing, duplicate, ambiguous or dynamically unsupported targets.
- [x] Preserve file length and OTBM escaping width; fail closed when replacement bytes would change encoded width.
- [x] Write only to a distinct output path below an explicit artifact root; never modify source in place.
- [x] Refuse symlink/path escape/overwrite by default and publish atomically/no-overwrite.
- [x] Prove byte equality outside the exact planned encoded spans and report every changed physical offset.
- [x] Fully reparse the patched copy with the existing scanner and regenerate canonical World Index evidence.
- [x] Run bounded Semantic OTBM Diff and require that only the planned mechanic changes appear.
- [x] Emit rollback instructions that retain the untouched source and identify the patched copy by hash.
- [x] Emit factual render requests through the existing renderer only; no AI-generated imagery.
- [x] Add schemas, ADR, documentation, focused synthetic round-trip/tamper/escape-width tests and dedicated CI artifacts.
- [x] Keep source/target `.otbm`, `.widx`, appearances, client assets, generated reports and renders outside Git.
- [x] Confirm no active datapack, gameplay, item definition, protocol, database or OTClient change.
- [ ] Update catalogue/changelog/roadmap in the separate lifecycle PR after current shared owner #331 releases those paths.
- [ ] Review exact final diff, all required current-head checks and zero review threads.
- [ ] Squash-merge and archive separately.

# Delivered implementation

- Existing `otbm_item_audit_scan.cpp` now exposes `--patch-anchors` without changing the legacy JSON or World Index modes.
- Every supported payload byte includes its physical offset, decoded value and encoded width.
- Tile-local placement indices preserve source placement order and disambiguate duplicate item IDs.
- Strict plan/result schemas and runtime validation reject unknown fields, oversized regions, duplicate operations and stale source pins.
- The Python layer validates scanner evidence; it does not parse the OTBM tree independently.
- Patching is copy-only, streaming and restricted to scanner-proven payload bytes.
- OTBM marker escape-width changes and non-canonical source spans are rejected.
- Source/output global byte comparison rejects every unplanned physical change.
- Post-write validation performs anchor reparse, legacy full scan, before/after World Index and bounded Semantic Diff.
- Output, evidence and result use confined no-overwrite publication; any late failure removes partial artifacts.
- Result evidence includes hashes, physical offsets, rollback instructions and a non-executing real-assets render request.
- Dedicated tests construct only a small synthetic OTBM; no real or user-supplied map is patched by CI.

# Safety invariants

- Source map remains byte-for-byte untouched.
- Output path differs from source and resides below `artifact_root`.
- Plan pins source SHA-256, byte size, OTBM version, items major/minor and one bounded region.
- Every operation pins exact target identity and expected old value.
- Only scanner-proven payload bytes may change.
- Logical replacement bytes retain the same physical OTBM escape width byte-by-byte.
- Changed physical offsets are pairwise disjoint.
- Output byte size equals source byte size.
- Direct comparison proves equality outside declared spans.
- Full scanner parse and World Index build succeed after mutation.
- Semantic validation finds exactly the planned mechanic changes and no tile/placement count changes.
- No generated binary, map, index, report or render is committed.

# Confirmed context

- Task-start `main`: `9b04ab3ef3dfbc9440274d63e15e6102c5501d85`, after Phase 7 lifecycle merge #323.
- Feature branch was merged forward without conflicts to current `main` `3a390c9d892c5b737d32711a71dbdf7fff1f06fe` on 2026-07-14.
- PR #325 owns the scanner and new Phase 8 paths; no other open PR owns those implementation paths.
- Shared catalogue/changelog/roadmap remain read-only because open PR #331 currently declares shared registry/catalogue/changelog integration.
- Upstream `opentibiabr/*` and Remere's Map Editor remain read-only evidence sources.
- User-supplied `/mnt/data/otservbr(4).otbm` and `/mnt/data/assets(1).zip` remain external evidence only. No real-map patch has been executed.
- Local checkout execution is unavailable after recorded DNS failures; repository validation is GitHub Actions evidence only.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Patch existing fixed-width attributes only | Preserves node structure and confines mutation to scanner-proven payloads. | `ADR-20260714-otbm-fixed-width-patch-boundary.md` |
| Preserve encoded width per logical byte | OTBM escaping can otherwise change file length and invalidate offsets/tree structure. | same ADR |
| Require tile-local placement index plus redundant identity | Disambiguates duplicate item IDs on one tile without inferred intent. | same ADR |
| Prove outside-span byte equality | Stronger than relying only on semantic reports. | same ADR |
| Source map is never an output | Makes rollback immediate and prevents in-place corruption. | same ADR |
| Publish output/evidence/result no-overwrite | Prevents destination races from replacing reviewed artifacts. | implementation hardening |

# Validation and CI

| Commit | Check | Result | Evidence |
|---|---|---|---|
| `8895ce2b785fff6dcd303736283080f23ee73423` | repository OTBM workflows including synthetic full round trip | success | OTBM Map Tools run `29328519105`; CI run `29328519126` |
| `db213fb7055f054b99dfeb3125953be165b61994` | dedicated schema, Werror scanner, Python compile and focused patch tests | success | OTBM Bounded Patch run `29328671997`, job `87071048163` |
| `aaf2818172ff2cbd7f693275dc88ef192e20ea9f` | deterministic publication hardening and new late-failure cleanup test | success | one-shot job `87072103215` before self-deletion |
| `bc57e7a295c6a332aa2c48293a3fd44745ac0d61` | conflict-intolerant merge from current main | success | one-shot sync job `87072495453` before self-deletion |
| pending current direct head | all required final checks | pending | final merge gate |

# Risks and compatibility

- Risk remains high because binary map mutation is introduced, even though the first scope is fixed-width and copy-only.
- Runtime impact: none; offline tooling only.
- Data migration: none; no active map is modified.
- Compatibility: existing scanner JSON and World Index modes remain in place and are exercised by repository tests.
- Rollback: delete the patched external copy and retain the pinned untouched source; repository rollback is a squash revert.
- The tool proves structural and semantic confinement, not gameplay intent. A reviewed plan remains mandatory.

# Remaining work

1. Review the exact 11-file final diff on the synchronized branch.
2. Require successful current-head OTBM Bounded Patch, OTBM tool suites, ownership and repository Required checks.
3. Confirm zero blocking comments/reviews/threads.
4. Mark PR #325 ready and squash-merge with the exact reviewed head.
5. Open a separate lifecycle PR to archive this task and update shared documentation when #331 releases it.

# Handoff

## Start here

Read this task, `OTBM_BOUNDED_PATCH.md`, the fixed-width ADR, scanner source, plan/result schemas and existing World Index/Semantic Diff contracts.

## Do not repeat

Do not create another OTBM parser, add/remove attributes, serialize the whole map, modify the uploaded source map, weaken escape handling, skip full reparse/diff validation or treat a clean semantic diff as player-intent proof.

## Open questions

- None for the initial fixed-width existing-attribute scope. Broader operations require a later explicit safety review and ADR.

# Completion

- Final status: active; implementation complete, final merge gate pending
- PR: #325
- Final feature head: pending final direct-head CI
- Merge commit:
- Cleanup PR:
- Archived at:
