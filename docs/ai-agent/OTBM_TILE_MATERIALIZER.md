# OTBM Bounded Raw Tile Materializer

## Purpose

The bounded raw tile materializer is the next structural OTBM write boundary after complete `TILE_AREA` materialization. It replaces one or more already-existing complete raw `OTBM_TILE` or `OTBM_HOUSETILE` subtrees with reviewed donor subtrees at the exact same absolute positions.

It is intentionally not a general tile editor. v1 does not insert or delete tiles, translate coordinates, convert ordinary tiles to house tiles, edit individual stack entries, or serialize arbitrary OTBM nodes.

Public contracts:

- `canary-otbm-tile-spans-v1`
- `canary-otbm-tile-materialization-approval-v1`
- `canary-otbm-tile-materialization-result-v1`

The architecture boundary is recorded in `docs/agents/decisions/ADR-20260717-otbm-raw-tile-replacement-boundary.md`.

## Required workflow

1. Build canonical current and donor World Index files and manifests with the existing extended native scanner.
2. Produce `canary-otbm-tile-spans-v1` evidence for both maps with the scanner's `--tile-spans` mode.
3. Review the exact selected positions and create a separate `canary-otbm-tile-materialization-approval-v1` document.
4. The approval must pin the current and donor map, World Index, and manifest SHA-256/size plus every selected position, canonical parent `TILE_AREA` key, expected raw tile hash/length/node type, and expected canonical World Index tile hash on both sides.
5. Run the materializer against those exact inputs.
6. Consume only a generated output copy after the tool reports `ok: true` and all post-write verification completes.

An approval is input-specific and state-specific. If either map, index, manifest, selected raw tile, or selected canonical tile changes, the materializer fails closed and the change must be reviewed again.

## Native scanner reuse

Compile the existing wrapper rather than introducing another parser:

```sh
c++ -O2 -std=c++20 -Wall -Wextra -Wpedantic -Werror \
  tools/ai-agent/otbm_area_materializer_scan.cpp \
  -o artifacts/otbm_area_materializer_scan
```

The wrapper includes the existing `otbm_item_audit_scan.cpp` translation unit. Existing scanner modes are delegated unchanged. `--tile-spans` first requires the canonical scanner to accept the full map, then records physical spans only for direct `OTBM_TILE` and `OTBM_HOUSETILE` children of a `TILE_AREA`.

The normalized span evidence records absolute position, canonical parent area key, node type, exact physical offsets, byte length, and SHA-256 for each raw tile subtree.

## CLI

```sh
python tools/ai-agent/otbm_tile_materializer_tool.py \
  --artifact-root artifacts/otbm-tile-materialization \
  --current-map /path/to/current.otbm \
  --donor-map /path/to/donor.otbm \
  --scanner artifacts/otbm_area_materializer_scan \
  --approval tile-approval.json \
  --current-index current.widx \
  --current-manifest current.widx.json \
  --donor-index donor.widx \
  --donor-manifest donor.widx.json \
  --output-map output/materialized.otbm \
  --evidence-dir output/materialization-evidence
```

Approval, indexes, manifests, output, and evidence are confined below `--artifact-root`. Current/donor maps and the scanner may be external regular files, but symlinks are rejected by the reused materializer path-safety helpers. Output and evidence must be new paths.

## Structural safety gates

Before publication, v1 requires all of the following:

- exact approval provenance pins for both source maps, World Index files, and manifests;
- green World Index v1 manifests that independently pin the supplied maps and indexes;
- compatible current/donor OTBM version, dimensions, items major, and items minor;
- zero unknown attribute tails;
- at least one and no more than 4096 selected positions;
- every selected position appears exactly once in both raw span reports;
- every selected position resolves to its canonical 256-aligned parent `TILE_AREA` key on both sides;
- current and donor use the same tile node type at every selected position;
- exact approval matches for current/donor raw tile SHA-256, raw byte length, node type, and canonical World Index tile SHA-256;
- create-new output/evidence paths with artifact-root confinement and overwrite/symlink rejection.

## Raw replacement proof

For every selected position, the complete donor raw tile subtree is copied byte-for-byte in place of the complete current raw tile subtree.

The implementation hashes the concatenation of all non-selected current bytes and compares it with the output after excluding selected output tile spans. Both retained streams must have identical byte count and SHA-256.

Every selected output raw tile subtree must also have the exact donor raw subtree SHA-256. Because v1 is replacement-only, result evidence always reports zero tile insertions and zero tile deletions.

## Mandatory post-write verification

The temporary candidate is not published until it passes:

1. the native scanner again;
2. normalized output tile-span validation;
3. selected output raw-subtree equality with donor, including parent area and node type;
4. canonical output World Index rebuild;
5. canonical selected-tile World Index equality with donor;
6. bounded Semantic OTBM Diff from current to output over the minimal selected-position bounding box;
7. current map, donor map, and scanner pre/post stat and SHA-256 checks.

Only after those gates pass are the output map and evidence directory published with create-new semantics.

Evidence includes:

- `materialization-result.json`
- `current-tile-spans.json`
- `donor-tile-spans.json`
- `output-tile-spans.json`
- `output.widx`
- `output.widx.json`
- `semantic-diff.json`

These are runtime artifacts and must not be committed.

## What v1 does not do

v1 does not support:

- tile insertion or deletion;
- non-zero x/y/z translation;
- teleport rewriting caused by translation;
- ordinary-tile/house-tile type conversion;
- independent item insertion, deletion, or stack reordering;
- generic OTBM node serialization;
- a complete-map writer;
- in-place map writes;
- automatic approval generation;
- direct execution as a new repair/materialization pipeline mode;
- gameplay, player-intent, reachability, script-runtime, or physical-client E2E proof.

Those require separate bounded work and, where the structural contract changes, a new ADR.
