# ADR-20260717: Bounded raw OTBM tile replacement boundary

Status: Accepted for the bounded v1 implementation in PR #467.

## Context

The merged complete `OTBM_TILE_AREA` materializer (#426) provides a safe raw-subtree structural boundary, but it intentionally requires full 256x256 aligned tile areas. Repair work sometimes needs a substantially narrower reviewed change: replacing one already-existing tile with the complete donor tile at the exact same world position.

Phase 8 remains limited to scanner-proven fixed-width existing attributes and must not be expanded into structural writes. The repository also already has a native scanner wrapper, canonical World Index, and Semantic OTBM Diff, so a second parser or complete-map serializer is not justified.

## Decision

Introduce a separate bounded raw tile materializer with these hard limits:

1. Extend the existing `otbm_area_materializer_scan.cpp` wrapper with a `--tile-spans` mode. The wrapper still runs the existing full native scanner first and only records physical spans for direct `OTBM_TILE` or `OTBM_HOUSETILE` children of a `TILE_AREA`.
2. Every selected tile must already exist exactly once in both current and donor maps at the same absolute `x,y,z` position and under the same canonical `TILE_AREA` key.
3. v1 requires the current and donor tile node type to match. It does not convert ordinary tiles into house tiles or house tiles into ordinary tiles.
4. A separate `canary-otbm-tile-materialization-approval-v1` document must pin both maps, both World Index files and manifests, every selected position and area key, and the exact current/donor raw and canonical tile hashes reviewed before execution.
5. Materialization replaces only complete selected raw tile subtrees in a distinct current-map copy. No tile is inserted or deleted and no item within a tile is independently serialized or reordered.
6. The implementation proves exact retained-byte equality outside selected current/output tile spans and exact donor-byte equality for every selected output tile subtree.
7. Before publication, the candidate must pass native reparse, canonical World Index rebuild, selected-tile canonical equality with donor, and a bounded Semantic OTBM Diff against current.
8. Current and donor maps plus the scanner are hash/stat pinned for the operation. Output and evidence use create-new semantics below an explicit artifact root.
9. A structurally green result proves only bounded structural confinement. It does not prove player intent, gameplay correctness, script correctness, reachability, or physical-client behavior.

## Rejected alternatives

- Expanding the Phase 8 fixed-width attribute patcher into structural mutation.
- Building another OTBM parser or a complete-map serializer.
- Replacing a tile at a different coordinate or parent `TILE_AREA`.
- Converting between ordinary and house tile node types in v1.
- Inserting or deleting tiles in v1.
- Independently inserting, deleting, or reordering item-stack entries.
- Modifying either source map in place.
- Treating successful structural validation as gameplay approval.

## Deferred work

A future ADR and bounded task are required for any of:

- same-coordinate tile insertion or deletion;
- ordinary-tile/house-tile type conversion;
- non-zero x/y/z translation;
- teleport-destination rewriting caused by translation;
- arbitrary item insertion, deletion, or stack reordering;
- generic OTBM node serialization;
- adding this writer as another repair/materialization pipeline execution mode;
- direct production-map execution.

Any future structural expansion must preserve source-copy isolation, format detection, escape safety, explicit reviewed approval, retained-byte proof where applicable, native reparse, World Index rebuild, and bounded Semantic Diff verification.
