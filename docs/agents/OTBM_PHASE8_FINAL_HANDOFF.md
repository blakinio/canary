# OTBM Phase 8 Final Handoff

## Status

Phase 8 is complete, merged, validated, and archived. This file is a durable handoff for future agents so the work does not need to be reconstructed from chat history.

Repository: `blakinio/canary`

Current implementation status:

- Phase 7 geometry consistency audit delivered and archived.
- Phase 8 bounded existing-attribute OTBM patcher delivered and archived.
- No production map, user-provided map, `.otbm`, `.widx`, client asset, generated report, or render was committed by this work.
- No real or user-provided map was patched during implementation or CI.
- Upstream `opentibiabr/*` repositories remained read-only evidence sources.

## Phase 7 durable state

Geometry consistency audit:

- feature PR: #322
- feature merge: `0d1eb94c8e8e3033d95fd73f56711b830624540f`
- lifecycle PR: #323
- lifecycle merge: `9b04ab3ef3dfbc9440274d63e15e6102c5501d85`

Delivered behavior includes exact ground/house/PZ consistency checks, conservative orphan and invisible-blocker candidates, render-request evidence, and deterministic tests built on the existing OTBM analysis pipeline.

## Phase 8 durable state

Bounded OTBM existing-attribute patcher:

- feature PR: #325
- final reviewed feature head: `132fa913bbd1607928d9bd70a080c6b27f5ce669`
- feature squash merge: `9350f2fb7420f9af2ecf79ea7085ca4e094a3891`
- lifecycle PR: #333
- lifecycle squash merge: `85c706ce79baa63e9cd4d8d2622b026c6a4826a7`
- archived task: `docs/agents/tasks/archived/CAN-20260714-otbm-bounded-attribute-patcher.md`

Public contracts introduced:

- `canary-otbm-patch-anchors-v1`
- `canary-otbm-bounded-patch-plan-v1`
- `canary-otbm-bounded-patch-result-v1`

Primary implementation paths:

- `tools/ai-agent/otbm_item_audit_scan.cpp`
- `tools/ai-agent/otbm_bounded_patch.py`
- `tools/ai-agent/otbm_bounded_patch_types.py`
- `tools/ai-agent/otbm_bounded_patch_tool.py`
- `tools/ai-agent/test_otbm_bounded_patch.py`
- `docs/ai-agent/OTBM_BOUNDED_PATCH.md`
- `docs/ai-agent/OTBM_BOUNDED_PATCH_PLAN.schema.json`
- `docs/ai-agent/OTBM_BOUNDED_PATCH_RESULT.schema.json`
- `docs/agents/decisions/ADR-20260714-otbm-fixed-width-patch-boundary.md`
- `.github/workflows/otbm-bounded-patch.yml`

## Supported Phase 8 mutations

Only already-existing fixed-width item attributes are eligible:

1. existing action ID;
2. existing unique ID;
3. existing house-door ID;
4. existing teleport destination.

The patcher does not insert or remove attributes, items, tiles, or nodes. It does not change item IDs, counts, stack order, tile type, ground, geometry, house ID, tile flags, text, or arbitrary visual content.

## Safety invariants

Every patch plan must pin the source SHA-256, byte size, OTBM/items versions, bounded region, exact position, tile-local placement index, item ID, item depth, attribute kind, expected old value, and replacement.

The implementation:

- reuses the existing native OTBM scanner rather than introducing a second parser;
- writes only to a distinct copy below an explicit artifact root;
- rejects in-place writes, overwrites, path escape, symlink traversal, and broken-symlink ancestry;
- changes only scanner-proven payload bytes;
- preserves file length and OTBM physical escape width;
- treats escape framing as immutable;
- proves byte equality outside declared payload offsets;
- performs a full scanner reparse after mutation;
- regenerates canonical before/after World Index evidence;
- requires bounded Semantic OTBM Diff to contain exactly the planned mechanic changes;
- emits rollback evidence that keeps the original source untouched;
- emits factual render requests through the existing real-assets renderer only;
- never uses AI-generated imagery as map evidence.

A clean structural and semantic validation proves confinement of the mutation. It does not prove player intent or gameplay correctness; every patch plan still requires review.

## Validation evidence

Final feature head `132fa913bbd1607928d9bd70a080c6b27f5ce669` passed the complete repository gate, including:

- OTBM Bounded Patch run `29331044093`;
- repository CI run `29331044300`;
- OTBM Map Tools;
- OTBM World Index;
- OTBM Semantic Diff;
- OTBM Geometry Audit;
- OTBM Reachability;
- Quest Map Validator;
- AI Agent Tools;
- Agent Task Ownership;
- Fast Checks;
- Lua Tests;
- Linux Release;
- required branch-protection gate.

Lifecycle PR #333 also passed Agent Task Ownership and ready-state repository CI, including Linux Release and `Required`, before squash merge.

## What not to redo

Do not:

- build another OTBM parser or complete-map serializer for this use case;
- create a second renderer for map evidence;
- treat unresolved script resolution as handled without evidence;
- modify the source map in place;
- weaken escape-width checks or outside-span equality proof;
- broaden Phase 8 into item/tile insertion, deletion, stack editing, or geometry changes without a new ADR and bounded task;
- commit source/target maps, `.widx` files, appearances, client assets, generated reports, or renders.

## Current continuation point

The bounded writer itself has no remaining implementation work.

PR #331, which previously owned shared catalogue/changelog/roadmap paths, is now merged. Before any future shared documentation integration, inspect current `main` and active ownership first; do not assume those documents still lack Phase 8 entries.

For the next real-map repair task:

1. run the existing item/mechanic audit and script resolution first;
2. prove the exact target and expected old state;
3. prepare a reviewed bounded patch plan;
4. patch a new copy only;
5. require full reparse, World Index, Semantic Diff, byte-confinement evidence, rollback instructions, and factual renderer evidence where useful;
6. never treat structural success as proof of gameplay intent.

## Next action

No action is required for Phase 8 itself. Future work should start as a new bounded task and PR against current `main`, reusing the merged Phase 8 contracts and tooling.
