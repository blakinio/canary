# Semantic OTBM Diff

## Purpose

Phase 6 compares two deterministic `canary-otbm-world-index-v1` inputs and emits `canary-otbm-semantic-diff-v1`. It is read-only. It does not parse OTBM, execute Lua, infer gameplay intent or modify either map.

The canonical data path is:

1. build each `.widx` with the existing native `otbm_item_audit_scan.cpp` scanner and `otbm_world_index.py`;
2. verify each index against its World Index manifest and optional real source map;
3. stream both sorted index tile sets and compare exact positions, tile metadata and item-stack evidence;
4. use the existing Phase 3 `_classify_tile` implementation for ground/blocker/walkability semantics when an appearances catalogue is supplied;
5. optionally attach exact selected-scope evidence from Phase 2, script resolution, Phase 3, Phase 4 and Phase 5 reports;
6. optionally build or execute factual before/after/context render requests through `otbm_renderer.render_region`.

No `.otbm`, `.widx`, client assets, appearances binary, large report or PNG belongs in Git.

## Entry points

- facade: `tools/ai-agent/otbm_semantic_diff.py`;
- comparison: `tools/ai-agent/otbm_semantic_diff_analysis.py`;
- shared types/limits/stable IDs: `tools/ai-agent/otbm_semantic_diff_types.py`;
- factual render manifest: `tools/ai-agent/otbm_semantic_diff_render.py`;
- CLI: `tools/ai-agent/otbm_semantic_diff_tool.py`;
- schema: `docs/ai-agent/OTBM_SEMANTIC_DIFF.schema.json`.

## Build the two canonical indexes

```bash
c++ -O2 -std=c++20 -Wall -Wextra -Wpedantic -Werror \
  tools/ai-agent/otbm_item_audit_scan.cpp \
  -o artifacts/otbm_item_audit_scan

PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_world_index_tool.py build artifacts/before.otbm \
  --scanner artifacts/otbm_item_audit_scan \
  --output artifacts/before.widx \
  --manifest artifacts/before.widx.json

PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_world_index_tool.py build artifacts/after.otbm \
  --scanner artifacts/otbm_item_audit_scan \
  --output artifacts/after.widx \
  --manifest artifacts/after.widx.json
```

## Full-index comparison

All paths are confined below `--artifact-root`. Direct symlink inputs and outputs are rejected.

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_semantic_diff_tool.py diff \
  --artifact-root artifacts \
  --before-index before.widx \
  --before-manifest before.widx.json \
  --after-index after.widx \
  --after-manifest after.widx.json \
  --appearances appearances.json \
  --before-map before.otbm \
  --after-map after.otbm \
  --output OTBM_SEMANTIC_DIFF.json
```

`--before-map` and `--after-map` are optional. When supplied, they are only hashed and compared to the World Index provenance; they are never parsed or modified by Phase 6.

## Inclusive bounded region

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_semantic_diff_tool.py diff \
  --artifact-root artifacts \
  --before-index before.widx \
  --before-manifest before.widx.json \
  --after-index after.widx \
  --after-manifest after.widx.json \
  --appearances appearances.json \
  --from 33200,31800,7 \
  --to 33250,31850,8 \
  --sample-limit 500 \
  --output OTBM_SEMANTIC_DIFF.json
```

Counts are exact for the selected full-index or bounded-region scope. `sampleLimit` bounds only returned findings and correlation samples. `summary.findings.total`, all per-kind/classification/evidence counts, tile counts and placement counts remain exact. `summary.findings.truncated` is explicit.

## Tile diff contract

At each exact `x,y,z`, Phase 6 reports:

- `tile-added` and `tile-removed`;
- `tile-kind-changed`;
- `tile-flags-changed`;
- `house-id-changed`;
- `ground-added`, `ground-removed` and `ground-changed` when Phase 3 appearance evidence is available.

Before/after tile evidence preserves exact position, floor, kind, house ID, flags, placement count and Phase 3 walkability state.

## Item-stack diff contract

A normalized item placement consists only of indexed semantic fields:

- item ID;
- source (`inline` or `node`);
- nested item depth;
- action ID;
- unique ID;
- house-door ID;
- teleport destination.

Index-build ordinals and tile indexes are provenance-local and are not treated as cross-index identity.

The stack algorithm is explicit and deterministic:

1. identical normalized sequences are unchanged;
2. if the exact normalized multisets are equal but sequence order differs, emit one `stack-order-changed` and suppress add/remove findings;
3. otherwise compute a minimum edit script over exact item base `(itemId,itemDepth,source)` with fixed tie order `replace`, `remove`, `add`;
4. exactly aligned base items emit separate mechanic changes;
5. unmatched operations report exact before/after stack indices.

This is not fuzzy or name-based matching. No item is paired by distance, sprite, neighboring tiles or guessed gameplay meaning.

## Mechanics diff

Mechanic changes are distinct from item replacement:

- `action-id-changed`;
- `unique-id-changed`;
- `house-door-id-changed`;
- `teleport-source-added` / `teleport-source-removed`;
- `teleport-destination-changed`;
- generic `mechanic-added` / `mechanic-removed` with the exact mechanic type.

A tile add/remove is also position-registration evidence. It is not described as a gameplay defect.

## Walkability diff

Phase 6 does not implement another walkability engine. It calls the Phase 3 classifier from `otbm_reachability_transition.py` with the same `AppearanceSemantics` loaded by Phase 3.

Reported transitions include:

- `strict-walkable-to-blocked`;
- `blocked-to-strict-walkable`;
- `optimistic-walkable-to-blocked`;
- `strict-to-conditional`;
- `conditional-to-strict`;
- ground added/removed/changed;
- static blocker added/removed;
- conditional blocker added/removed;
- unknown appearance added/removed.

`walkability-regression` and `walkability-improvement` are semantic classifications under the Phase 3 model. They are not runtime or gameplay proof. Unknown appearances remain explicit.

Without `--appearances`, structural/static tile, stack and mechanics comparison remains available, while walkability/ground findings are not produced.

## Conservative correlation

Optional inputs:

```text
--quest-validation canary-quest-map-validation-v1
--script-resolution canary-otbm-script-resolution-v1
--reachability canary-otbm-reachability-v1
--spawn-npc canary-otbm-spawn-npc-evidence-v1 or canary-otbm-spawn-npc-validation-v1
--storage-graph canary-otbm-storage-graph-v1
```

Correlation walks bounded JSON inputs and indexes only exact positions and literal mechanic values. Attached evidence retains report role, format, JSON path and a bounded field subset. It can add `handler-affected`, `quest-evidence-affected`, `spawn-npc-evidence-affected`, `storage-evidence-affected`, `unresolved` or `conflicting` classifications.

Important limits:

- correlation is only for the supplied report scope;
- absence from a supplied report does not mean global absence or non-use;
- no selected scope is promoted to the full world;
- no handler, route, actor, storage operation or quest state is executed;
- `unresolved` is never promoted to handled.

## Stable finding IDs and ordering

Finding IDs are SHA-256-derived from the exact change kind, position, before/after values and core details. Optional correlation does not change an underlying finding ID. Samples are ordered by position, kind and ID. JSON output uses sorted keys and is deterministic for identical inputs and options.

## Input compatibility and failure behavior

The diff fails closed when:

- either binary index has invalid magic, version, layout, offsets, postings or records;
- an index SHA-256/size differs from its manifest;
- source size, OTBM header, logical summary or binary record metadata differs from the index;
- source/scanner hashes are missing or malformed;
- scanner build formats differ;
- OTBM version or item major/minor versions differ;
- the same source hash and scanner hash produce different index bytes;
- a supplied real map does not match manifest source hash/size;
- a correlation report format is unsupported;
- any input escapes `artifactRoot`, is a direct symlink or exceeds its size limit;
- output exists without `--overwrite`, is a symlink, escapes the root or exceeds 64 MiB.

The report is written atomically with `fsync` and `os.replace`.

## Factual visual evidence

Build a deterministic manifest without requiring CI assets:

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_semantic_diff_tool.py render \
  --artifact-root artifacts \
  --before-map before.otbm \
  --after-map after.otbm \
  --assets client-assets \
  --from 33200,31800,7 \
  --to 33220,31820,7 \
  --output-directory renders \
  --manifest OTBM_SEMANTIC_DIFF_RENDER.json
```

Add `--execute` to call the existing `otbm_renderer.render_region` API. Per floor, the manifest contains exact before, after, before-context and after-context requests. Executed PNGs are staged through temporary paths, then atomically moved. Their SHA-256 values and the existing renderer reports are recorded. Source maps are hashed again after rendering.

No AI image generation, styling, invented sprite or synthetic visual repair is used. No overlay image is generated; `diffManifest` deterministically pairs the factual render IDs. Missing private assets in CI result in manifest/toolkit validation, not a fake render.

## Test coverage

```bash
PYTHONPATH=tools/ai-agent \
python -m unittest -v tools/ai-agent/test_otbm_semantic_diff.py
```

The focused suite compiles the existing native scanner and builds two synthetic canonical indexes. It covers identical inputs, tile/item/mechanic changes, pure reorder, Phase 3 walkability transitions, bounded scope, exact truncated counts, determinism, corrupt/mismatched provenance, overwrite/symlink safety, Phase 2–5 correlation, renderer API integration and source-map immutability.

## Evidence levels

The report keeps these layers separate:

- `structural`: exact index presence/order;
- `static`: exact tile attributes;
- `semantic`: item/mechanic/Phase 3 state meaning;
- `correlated`: exact supplied-report linkage;
- `regression`: a Phase 3 walkability transition;
- `runtime`: not claimed by this tool;
- `gameplay`: not claimed by this tool;
- `factual-visual-evidence`: only an executed existing-renderer artifact.

Lower levels never prove higher levels.
