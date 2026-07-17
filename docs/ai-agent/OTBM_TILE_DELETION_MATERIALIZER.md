# OTBM bounded raw tile deletion materializer

`tools/ai-agent/otbm_tile_deletion_materializer_tool.py` deletes one or more separately approved complete raw tile subtrees from a distinct copy of a current OTBM map.

This is a structural-confinement tool, not a gameplay editor.

## Hard boundary

A selected tile may be deleted only when all of the following are true:

- the absolute `x,y,z` position exists exactly once in the current raw tile-span report;
- the same position exists in the current canonical World Index;
- its raw span uses the approved canonical parent `(x & 0xFF00, y & 0xFF00, z)` `TILE_AREA` key;
- the approved current raw SHA-256, raw byte length, node type and canonical World Index tile SHA-256 still match;
- the approved current map, World Index and manifest provenance still match.

The materializer does **not**:

- remove or synthesize a parent `TILE_AREA`;
- insert or replace a tile;
- translate coordinates;
- convert an existing ordinary tile to a house tile or vice versa;
- delete, insert, or reorder individual item-stack entries;
- use a generic node or full-map serializer;
- modify the source map in place.

Deleting the last tile from a `TILE_AREA` is allowed only as a child deletion. The existing parent area remains physically present and the resulting map must pass native reparse and World Index rebuild.

## Approval contract

Use `docs/ai-agent/OTBM_TILE_DELETION_APPROVAL.schema.json`.

The approval must use:

```text
format = canary-otbm-tile-deletion-approval-v1
schemaVersion = 1
decision = approved
```

Each selection pins:

- `position`;
- canonical `areaKey`;
- current raw tile SHA-256 and byte length;
- current node type (`5` ordinary tile or `14` house tile);
- current canonical World Index tile SHA-256.

Top-level current provenance pins the source map, World Index, and World Index manifest.

## Physical write rule

The existing native structural scanner first accepts the complete current map and exposes exact complete raw tile spans through `scan_tile_spans()`.

The candidate writer copies the complete current byte stream while omitting only the selected scanner-proven spans. It never serializes a tile, item, area, or map node independently.

## Structural proof

Before publication the tool requires all of these checks:

1. approved current provenance matches;
2. selected positions exist exactly once in current raw spans and World Index;
3. selected raw/canonical state still matches approval;
4. candidate output SHA-256 and byte count equal the current byte sequence with exactly selected spans omitted;
5. the native scanner reparses the candidate;
6. selected positions are absent from the output raw tile report;
7. a canonical output World Index is rebuilt;
8. selected positions are absent from the output World Index;
9. bounded Semantic OTBM Diff is generated for the minimal selected-position box;
10. current map and scanner still match their pre-operation pins.

Only then are the output map copy and evidence directory published with create-new semantics.

## CLI

```sh
python tools/ai-agent/otbm_tile_deletion_materializer_tool.py \
  --artifact-root artifacts/otbm-deletion \
  --current-map /path/to/current.otbm \
  --scanner /path/to/otbm_area_materializer_scan \
  --approval approval.json \
  --current-index current.widx \
  --current-manifest current.widx.json \
  --output-map output.otbm \
  --evidence-dir evidence
```

Approval/index/manifest/output/evidence paths are confined below `--artifact-root` where required by the existing materialization safety helpers. Source map and scanner may be supplied from separate immutable locations.

## Result contract and rollback

The result uses `canary-otbm-tile-deletion-result-v1` and records operation counts, deleted raw spans, exact retained-current proof, canonical deleted-tile hashes, selected-position absence, Semantic Diff evidence, source pins, and safety non-claims.

Rollback is deletion of the generated output copy. The source map is never modified.

A successful result does not prove script correctness, reachability, gameplay correctness, player intent, or physical-client behavior.
