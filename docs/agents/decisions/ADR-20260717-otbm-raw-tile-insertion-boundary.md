# ADR-20260717: Bounded raw OTBM tile insertion boundary

Status: Accepted for the bounded v1 implementation in PR #482.

## Context

The merged raw tile materializer in PR #467 safely replaces an already-existing current tile with a complete donor tile at the exact same position and parent `TILE_AREA`. It deliberately rejects insertion. Repair work also needs a narrower structural operation for a tile that is missing from current but already exists in a reviewed donor map.

The repository already exposes canonical full-map parsing, raw `TILE_AREA` spans, raw tile spans, World Index construction, and Semantic OTBM Diff. A new parser, generic node serializer, or full-map serializer is not justified.

## Decision

Introduce a separate bounded raw tile insertion materializer with these limits:

1. Every selected absolute position must be absent from the current tile-span report and current World Index, and exist exactly once in the donor tile-span report and donor World Index.
2. The canonical parent `TILE_AREA` for every selected position must already exist exactly once in current. v1 does not create a missing `TILE_AREA`.
3. A separate `canary-otbm-tile-insertion-approval-v1` document pins both maps, both World Index files/manifests, each target position and area key, the exact reviewed current parent `TILE_AREA` raw hash/length, and the donor raw/canonical tile state.
4. The writer copies each complete donor raw tile subtree and inserts it immediately before the scanner-proven `NODE_END` of the existing current parent `TILE_AREA`.
5. Multiple selected insertions into one parent are emitted in deterministic `(z,y,x)` position order. Existing current children are never reordered.
6. The complete current map byte sequence must remain exact: hashing the output while excluding only inserted spans must equal the complete current map SHA-256 and byte count.
7. Every inserted output raw tile subtree must equal its donor subtree byte-for-byte.
8. Before publication, the candidate must pass native reparse, World Index rebuild, inserted-tile canonical equality with donor, and bounded Semantic OTBM Diff.
9. Current map, donor map and scanner are immutable and pinned across execution. Output and evidence use create-new artifact-root-confined publication.
10. A green result proves bounded structural confinement only. It does not prove player intent, scripts, reachability, gameplay correctness, or physical-client behavior.

## Rejected alternatives

- Building another OTBM parser.
- Serializing a tile from World Index/canonical data rather than copying the reviewed donor raw subtree.
- Creating a missing `TILE_AREA` in v1.
- Combining insertion and deletion in one operation mode.
- Translating coordinates or rewriting teleport destinations in v1.
- Converting an existing ordinary tile to a house tile or vice versa.
- Inserting/deleting/reordering individual item-stack entries.
- Modifying either source map in place.

## Deferred work

Separate bounded ADRs/tasks remain required for:

- same-coordinate raw tile deletion;
- explicit ordinary-tile/house-tile conversion of an existing tile;
- creation/deletion of complete `TILE_AREA` parents outside the existing area materializer contract;
- non-zero x/y/z translation and dependent teleport-destination rewriting;
- arbitrary item insertion, deletion, and stack reordering;
- generic OTBM node serialization;
- integration of structural operation modes into the repair/materialization orchestrator;
- direct production-map execution.

Any expansion must preserve source-copy isolation, explicit reviewed approval, format detection, native reparse, World Index rebuild, bounded Semantic Diff, and truthful non-claims.
