# OTBM Bounded Raw Tile Type Conversion Materializer

## Purpose

`otbm_tile_type_conversion_materializer_tool.py` converts an already-existing complete raw `OTBM_TILE` subtree to `OTBM_HOUSETILE`, or an already-existing complete raw `OTBM_HOUSETILE` subtree to `OTBM_TILE`, by replacing the complete reviewed current subtree with a complete reviewed donor subtree at the exact same absolute position.

The tool is deliberately not a generic tile editor. It does not patch a node-type byte, synthesize a house ID, serialize individual attributes, or reconstruct an OTBM node. The complete donor raw subtree is the target representation.

Public contracts:

- `canary-otbm-tile-type-conversion-approval-v1`
- `canary-otbm-tile-type-conversion-result-v1`

The architecture boundary is recorded in `docs/agents/decisions/ADR-20260717-otbm-raw-tile-type-conversion-boundary.md`.

## Why complete-subtree replacement is required

`OTBM_TILE` and `OTBM_HOUSETILE` do not have interchangeable raw property layouts. A house tile carries house metadata that an ordinary tile does not. Therefore changing only the node type, or inventing missing house metadata, would be unsafe.

This materializer instead reuses the existing complete raw-tile replacement writer. The approved donor subtree already contains the exact target node type, house metadata when applicable, inline ground, child items and attributes.

## Required workflow

1. Build canonical current and donor World Index files and manifests with the existing native scanner.
2. Produce existing `canary-otbm-tile-spans-v1` evidence for both maps.
3. Review the exact position and canonical parent `TILE_AREA` for every conversion.
4. Create a separate `canary-otbm-tile-type-conversion-approval-v1` document that pins both maps, World Indexes and manifests plus exact current/donor raw and canonical tile state.
5. Require each selected current and donor tile to exist exactly once at the same absolute position and under the same canonical parent `TILE_AREA`.
6. Require the node types to differ: `5 → 14` or `14 → 5` only.
7. Run the materializer and consume only a create-new output after all post-write verification succeeds.

An approval is input-specific and state-specific. Any source map, index, manifest, selected raw subtree or selected canonical tile change invalidates the approval.

## CLI

```sh
python tools/ai-agent/otbm_tile_type_conversion_materializer_tool.py \
  --artifact-root artifacts/otbm-tile-type-conversion \
  --current-map /path/to/current.otbm \
  --donor-map /path/to/donor.otbm \
  --scanner artifacts/otbm_area_materializer_scan \
  --approval conversion-approval.json \
  --current-index current.widx \
  --current-manifest current.widx.json \
  --donor-index donor.widx \
  --donor-manifest donor.widx.json \
  --output-map output/converted.otbm \
  --evidence-dir output/conversion-evidence
```

Approval, indexes, manifests, output and evidence are confined below `--artifact-root`. Current/donor maps and the scanner may be external regular files. The existing materializer safety helpers reject unsafe symlink/path behavior. Output and evidence use create-new semantics.

## Structural safety gates

Before publication, v1 requires:

- exact approval provenance pins for both maps, World Index files and manifests;
- green canonical World Index v1 manifests that pin the supplied maps and indexes;
- compatible OTBM version, dimensions, items major and items minor;
- zero unknown attribute tails;
- at least one and no more than 4096 selected positions;
- every selected position present exactly once in current and donor raw tile-span reports;
- the same absolute position and canonical 256-aligned parent `TILE_AREA` on both sides;
- current and donor node types limited to `OTBM_TILE` (`5`) and `OTBM_HOUSETILE` (`14`);
- current and donor node types must be different;
- exact approval matches for current/donor raw SHA-256, raw byte length, node type and canonical World Index tile SHA-256;
- create-new output/evidence paths with artifact-root confinement.

## Raw confinement proof

For every selected position, the existing complete raw-tile replacement writer copies the donor subtree byte-for-byte over the selected complete current subtree.

The output is accepted only when:

- the concatenation of all non-selected current bytes is byte-for-byte identical to the output after excluding converted output spans; and
- every selected output raw subtree has the exact SHA-256 of the selected donor subtree.

No house metadata is synthesized. For `TILE → HOUSETILE`, the donor subtree supplies the reviewed house ID and all raw properties. For `HOUSETILE → TILE`, the donor subtree supplies the complete ordinary-tile representation.

## Mandatory post-write verification

The temporary candidate is not published until it passes:

1. native scanner reparse;
2. normalized output tile-span validation;
3. selected output raw-subtree equality with donor, including parent area and target node type;
4. canonical output World Index rebuild;
5. selected canonical output tile equality with donor;
6. bounded Semantic OTBM Diff from current to output over the minimal selected-position bounding box;
7. current map, donor map and scanner pre/post stat and SHA-256 checks.

Evidence includes the conversion result, current/donor/output tile-span reports, rebuilt output World Index/manifest and Semantic Diff. These are runtime artifacts and must not be committed.

## What v1 does not do

v1 does not support:

- coordinate translation;
- `TILE_AREA` creation, deletion or movement;
- tile insertion or deletion;
- independent item insertion, deletion or stack reordering;
- in-place node-type byte editing;
- synthesized or automatically allocated house IDs;
- generic OTBM node serialization;
- a complete-map writer;
- in-place map writes;
- automatic approval generation;
- gameplay, house-runtime, reachability, player-intent or physical-client E2E proof.

Those remain separate bounded tasks only when required by an approved project/program boundary.
