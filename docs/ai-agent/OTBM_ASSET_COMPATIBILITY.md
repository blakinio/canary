# OTBM Asset and Appearance Compatibility Audit

`otbm_asset_compatibility_tool.py` emits deterministic `canary-otbm-asset-compatibility-v1` evidence for the exact item IDs used by one canonical OTBM World Index.

## Reuse boundary

The audit does not parse OTBM, protobuf appearances, client catalogs or sprite containers. It consumes:

- the existing binary Unified OTBM World Index plus its `canary-otbm-world-index-v1` manifest;
- an existing `canary-appearances-index-v1` produced by `otbm_appearances.py`;
- an existing `canary-client-assets-index-v1` produced by `otbm_assets.py`;
- optionally, one exact baseline `canary-appearances-index-v1` for semantic-delta evidence.

The manifest `canary-otbm-asset-compatibility-manifest-v1` pins the source-map SHA-256, World Index SHA-256, current appearances-index SHA-256 and client-asset-index SHA-256. When a baseline appearances index is supplied, its SHA-256 must also be pinned. Mismatched or missing provenance fails closed.

## Findings

For item IDs actually present in the exact World Index, the audit reports:

- `missing-object-appearance` when no canonical object appearance record exists;
- `uncovered-sprite-id` when a used appearance references a sprite outside all indexed client-asset ranges;
- `missing-sprite-asset-file` when the matching indexed sprite range exists but its asset file is missing;
- `zero-sprite-reference` for explicit sprite ID 0 references;
- `appearance-semantics-changed` when an optional exact baseline proves a change in canonical flags used by OTBM walkability/interaction classification: ground/bank, unpassable, avoid, usable, multiUse or forceUse.

Appearance deltas for item IDs not used by the selected World Index are intentionally excluded from the map-compatibility result.

## Proof boundary

A clean static report proves only compatibility of the selected exact evidence set. It does not prove that a client can render every scene at runtime or that a gameplay route remains physically correct. Conversely, missing/stale/truncated upstream evidence is never converted into a passing claim.

The tool never rewrites `items.otb`, appearances, client assets or `.otbm` maps and never becomes a second renderer or parser.

## CLI

```sh
python tools/ai-agent/otbm_asset_compatibility_tool.py \
  --manifest qa014-manifest.json \
  --world-index world.widx \
  --world-manifest world.widx.json \
  --appearances appearances-index.json \
  --asset-index client-assets-index.json \
  --output asset-compatibility.json
```

Add `--baseline-appearances previous-appearances-index.json` only when `baselineAppearancesSha256` is pinned in the manifest. Output defaults to create-new/no-clobber; `--overwrite` uses atomic replacement. Symlink outputs and input/output aliasing are rejected.
