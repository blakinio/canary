---
task_id: CAN-20260714-otbm-bounded-attribute-patcher
program_id: ""
coordination_id: "OTS-OTBM-VALIDATION"
status: archived
agent: "GPT-5.6 Thinking"
branch: feat/otbm-bounded-attribute-patcher
base_branch: main
created: 2026-07-14T12:00:00+02:00
updated: 2026-07-14T14:50:00+02:00
last_verified_commit: "9350f2fb7420f9af2ecf79ea7085ca4e094a3891"
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
    - docs/agents/tasks/archived/CAN-20260714-otbm-bounded-attribute-patcher.md
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

Deliver the first Phase 8 write-capable OTBM safety surface: deterministic, manifest-driven mutation of an **already existing fixed-width mechanic attribute only** on a distinct OTBM copy, with exact expected state, source hash/version pinning, bounded region, byte-level confinement proof, full reparse, canonical World Index/Semantic Diff validation and factual render instructions.

# Delivered operations

Only existing item-node attributes are eligible:

1. `set-action-id` — existing `ATTR_ACTION_ID`, unsigned 16-bit;
2. `set-unique-id` — existing `ATTR_UNIQUE_ID`, unsigned 16-bit;
3. `set-house-door-id` — existing `ATTR_HOUSEDOOR_ID`, unsigned 8-bit;
4. `set-teleport-destination` — existing `ATTR_TELE_DEST`, exact `x,y,z` encoded as 16/16/8 bits.

No attribute, item, tile or node can be inserted or removed. Item IDs, counts, stack order, tile kind/flags/house ID, ground, geometry, text and complete-map serialization remain out of scope.

# Completion criteria

- [x] Reuse and extend the existing native scanner instead of creating a second OTBM parser.
- [x] Add `--patch-anchors` and `canary-otbm-patch-anchors-v1` with exact physical payload offsets, decoded bytes and encoded widths.
- [x] Identify each target by exact `x,y,z`, tile-local placement index, item ID, item depth, attribute kind and expected old value.
- [x] Pin source SHA-256, byte size, OTBM/items versions and an inclusive region capped at 1,000,000 coordinates.
- [x] Reject more than 10,000 operations before entry parsing and cap operation IDs at 200 characters.
- [x] Reject missing, duplicate, ambiguous, stale or unsupported targets.
- [x] Preserve file length and OTBM escape width; reject escape-prefix or non-canonical span changes.
- [x] Write only to a new confined output path; reject in-place mutation, overwrite, path escape and lexical/resolved/broken symlink traversal.
- [x] Prove equality outside exact scanner-proven payload offsets and report every changed physical payload offset.
- [x] Fully reparse the copy and build before/after canonical World Index evidence.
- [x] Require bounded Semantic OTBM Diff to contain exactly the planned mechanic changes and no tile/placement count changes.
- [x] Publish output, evidence and result through no-overwrite operations and remove partial artifacts after late failure.
- [x] Emit rollback instructions retaining the untouched source and a non-executing factual render request using real assets only.
- [x] Add strict plan/result schemas, ADR, documentation, focused synthetic tests and dedicated CI.
- [x] Keep `.otbm`, `.widx`, appearances, assets, generated reports and renders outside Git.
- [x] Confirm no active map, datapack, gameplay, item definition, protocol, database or OTClient change.
- [x] Review the exact 11-file feature diff, successful final-head checks and zero review threads.
- [x] Squash-merge feature PR #325 and archive in separate lifecycle PR #333.
- [x] Defer catalogue/changelog/roadmap integration while draft PR #331 owns those shared paths; handle it in a later dedicated integration change.

# Delivered implementation

- `otbm_item_audit_scan.cpp` now exposes `--patch-anchors` while retaining legacy JSON and World Index modes.
- Every supported logical payload byte carries physical offset, decoded value and encoded width.
- Tile-local placement indices preserve source order and disambiguate duplicate item IDs.
- Python validates native scanner evidence and does not independently parse the OTBM tree.
- Patching is copy-only and streaming, restricted to exact scanner-proven payload locations.
- Direct source/output comparison rejects every unplanned physical difference.
- Post-write validation performs anchor reparse, legacy full scan, before/after World Index and exact bounded Semantic Diff.
- Destination parents are created only after overlap validation; arbitrary output names cannot collide with internal evidence filenames.
- Output, evidence and result use confined no-overwrite publication; late failures remove partial artifacts.
- Result evidence includes hashes, changed payload offsets, rollback instructions and a real-assets render request.
- Tests construct only a tiny synthetic OTBM; no production or user-supplied map is patched by CI.

# Safety invariants

- Source map remains byte-for-byte untouched.
- Output differs from source and is confined below `artifact_root` without symlink traversal.
- Every plan pins source identity, format versions, bounded region, exact target identity and expected old value.
- Only scanner-proven logical payload locations may change; OTBM escape framing is immutable.
- Replacement bytes retain identical physical encoded widths.
- Changed payload offsets are pairwise disjoint.
- Output byte size equals source byte size.
- Full scanner parse and World Index build succeed after mutation.
- Semantic validation proves exactly the planned mechanic changes.
- Structural and semantic confinement does not replace reviewed gameplay intent.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Patch existing fixed-width attributes only | Preserves node structure and confines mutation to scanner-proven payloads. | `ADR-20260714-otbm-fixed-width-patch-boundary.md` |
| Preserve encoded width per logical byte | OTBM escaping can otherwise shift the node stream. | same ADR |
| Require tile-local placement index plus redundant identity | Disambiguates duplicate items without inferred intent. | same ADR |
| Prove outside-payload byte equality | Escape prefix is framing and cannot be an allowed changed byte. | implementation hardening |
| Source map is never an output | Makes rollback immediate and prevents in-place corruption. | same ADR |
| Publish output/evidence/result no-overwrite | Prevents destination races and accidental replacement. | implementation hardening |
| Reject lexical/resolved/broken symlink ancestry | Prevents confined-looking paths from being redirected. | implementation hardening |
| Parse no more than 10,000 operations | Bounds plan allocation and validation cost before entry parsing. | implementation hardening |

# Validation and CI

| Commit | Check | Result | Evidence |
|---|---|---|---|
| `8895ce2b785fff6dcd303736283080f23ee73423` | repository OTBM workflows including synthetic full round trip | success | OTBM Map Tools `29328246908`; CI `29328247215`; bounded patch `29328246853` |
| `db213fb7055f054b99dfeb3125953be165b61994` | schemas, Werror scanner, Python compile and focused tests | success | run `29328671997`, job `87071048163` |
| `aaf2818172ff2cbd7f693275dc88ef192e20ea9f` | publication hardening and late-result cleanup test | success | job `87072103215` |
| `dcae5ce0ac4a09fc484a47ee442fc33610dd269e` | payload-only allowlist and symlink-parent tests | success | run `29329458294`, job `87073625155` |
| `f20f81952ca5e25ab809da6eab7bd71e3efc87ae` | deferred destination publication and collision tests | success | run `29329940427`, job `87075200703` |
| `6c6b788484bed8268d4db3714d6c8a33af84199a` | pre-parse plan limits and broken-symlink test | success | run `29330123167`, job `87075797473` |
| `132fa913bbd1607928d9bd70a080c6b27f5ce669` | complete final-head merge gate | success | OTBM Bounded Patch `29331044093`; CI `29331044300`; all OTBM/agent workflows successful |

# Merge record

- Feature PR: #325
- Final feature head: `132fa913bbd1607928d9bd70a080c6b27f5ce669`
- Squash merge commit: `9350f2fb7420f9af2ecf79ea7085ca4e094a3891`
- Merged at: 2026-07-14T12:37:50Z
- Lifecycle PR: #333
- Archived at: 2026-07-14T14:50:00+02:00
- Runtime impact: none; offline tooling only.
- Data migration: none; no active map was modified.
- Repository rollback: revert the squash merge.
- External patched-map rollback: delete the patched copy and retain the pinned untouched source.

# Deferred integration

Shared `MODULE_CATALOG.md`, `CHANGELOG.md` and `OTS_OTBM_TOOLING_ROADMAP.md` remain intentionally unchanged because draft PR #331 currently owns those paths. A later dedicated integration change must add Phase 8 entries after that ownership is released.

# Final status

Archived. Phase 8 implementation is merged and feature path ownership is released. No feature implementation work remains.
