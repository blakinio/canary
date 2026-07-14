# OTBM geometry and consistency audit

Phase 7 provides a deterministic, bounded, read-only audit over the canonical World Index and appearances evidence. It does not parse or modify OTBM, execute Lua, infer gameplay intent or create a second walkability engine or renderer.

## Contracts

- report: `canary-otbm-geometry-audit-v1`;
- reviewed adjacency rules: `canary-otbm-geometry-rules-v1`;
- factual render request manifest: `canary-otbm-geometry-audit-render-v1`;
- schemas: `OTBM_GEOMETRY_AUDIT.schema.json` and `OTBM_GEOMETRY_RULES.schema.json`.

Entrypoints:

- facade: `tools/ai-agent/otbm_geometry_audit.py`;
- CLI: `tools/ai-agent/otbm_geometry_audit_tool.py`;
- analysis: `tools/ai-agent/otbm_geometry_audit_analysis.py`;
- render requests: `tools/ai-agent/otbm_geometry_audit_render.py`.

## Required inputs

1. one `canary-otbm-world-index-v1` binary;
2. its exact manifest, including matching binary size, SHA-256, OTBM metadata and summary;
3. one `canary-appearances-index-v1` JSON document or compatible appearances binary;
4. one explicit inclusive 3D region containing at most 1,000,000 coordinates.

Every input path is confined below `--artifact-root`. Direct symlinks, path escapes and oversized inputs fail closed. The source map is not required for analysis.

## Evidence classes

### High-confidence structural evidence

- `item-without-floor`: indexed tile/item evidence with no confirmed ground appearance;
- invalid house tile without a positive house ID;
- disconnected components for one exact house ID when the selected boundary does not limit the conclusion;
- manifest-backed wall/border adjacency mismatches when the reviewed rule itself claims the neighbor is required.

### Review warnings

- `multiple-ground-items`: more than one placement has confirmed ground appearance; layered ground can be intentional;
- `orphan-tile-component`: a small cardinal component inside the selected scope; scripts, reviewed floor transitions or runtime teleportation may connect it;
- `house-component-mixed-pz`: one cardinal house component mixes PZ and non-PZ raw tile flags;
- `isolated-pz-tile` and `pz-enclosed-gap`: exact raw-flag geometry that still requires gameplay review;
- `unknown-appearance`: an item ID is absent from the supplied appearances catalogue.

### Low-confidence invisible-blocker candidate

`invisible-blocker-candidate` requires direct `unpassable` appearance evidence and no nonzero sprite ID in any decoded frame group. It does **not** prove transparent pixels, runtime invisibility or a defect. Sprite pixels are not inspected by this finding.

## Protection-zone flag

The raw OTBM tile flag is preserved by the native scanner. The audit interprets only protection-zone bit `0x0001`, verified against current read-only Remere's Map Editor `source/tile.h` (`TILESTATE_PROTECTIONZONE`). All other raw flag bits remain uninterpreted.

## Wall and border rules

Names, sprite shape and visual memory do not prove intended wall/border connectivity. Therefore no wall or border finding is emitted without an explicit reviewed rule manifest.

Example:

```json
{
  "format": "canary-otbm-geometry-rules-v1",
  "schemaVersion": 1,
  "adjacencyRules": [
    {
      "id": "stone-wall-east",
      "category": "wall",
      "sourceItemIds": [400],
      "direction": "east",
      "requiredNeighborItemIds": [401, 402],
      "severity": "warning",
      "confidence": "high",
      "message": "Reviewed stone-wall segment requires an east continuation"
    }
  ]
}
```

A rule means only what it states: when one source item occurs, the adjacent tile in the declared cardinal direction must contain at least one required item ID. The tool does not derive reciprocal edges or invent endpoints.

## CLI

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_geometry_audit_tool.py \
  --artifact-root artifacts/geometry \
  --index world.widx \
  --manifest world.widx.json \
  --appearances appearances.json \
  --from 32000,32000,7 \
  --to 32100,32100,7 \
  --rules reviewed-rules.json \
  --orphan-max-tiles 8 \
  --sample-limit 500 \
  --output OTBM_GEOMETRY_AUDIT.json
```

The command returns `1` when high-severity error findings exist and `2` for invalid input or contract failure. Warnings do not make `ok` false.

## Factual render requests

The optional render manifest records exact `otbm_render_tool.py` argument arrays around sampled findings. It does not render by itself and does not modify the map. Execution requires the real OTBM and compatible client assets outside Git.

```bash
  --render-manifest OTBM_GEOMETRY_RENDERS.json \
  --map /external/map.otbm \
  --assets /external/client-assets \
  --render-output-dir /external/renders
```

No AI-generated, stylized or invented map imagery is accepted as evidence.

## Scope and completeness

`complete: true` means all indexed tiles inside the selected inclusive region were evaluated under the stated contracts and sample limits. It does not mean the selected region is the whole world, that runtime routes were executed, or that every warning is a gameplay defect.

Exact finding totals remain available even when `findings` samples are truncated. Components touching the selected boundary are marked explicitly and use lower confidence.

## Safety

- source OTBM and World Index are never modified;
- generated reports, indexes, binaries, assets and renders stay outside Git;
- output is atomic;
- overwrite requires `--overwrite`;
- dynamic Lua and callback order are not evaluated;
- no map repair or Phase 8 operation is authorized by this report.
