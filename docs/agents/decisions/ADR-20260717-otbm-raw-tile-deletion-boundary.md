# ADR-20260717: Bounded raw OTBM tile deletion boundary

Status: Accepted for the bounded v1 implementation in PR #488.

## Context

The merged raw tile replacement (#467) and insertion (#482) boundaries can replace an existing tile or insert a missing tile without a generic serializer. Repair work also needs the inverse narrow operation: remove an already-existing complete tile subtree at an exact reviewed position while preserving the containing `TILE_AREA`.

The repository already exposes canonical full-map parsing, raw tile spans, World Index construction, Semantic OTBM Diff, and create-new materialization safety helpers. A new parser, scanner mode, arbitrary node serializer, or full-map serializer is not justified.

## Decision

Introduce a separate bounded raw tile deletion materializer with these limits:

1. Every selected absolute position must exist exactly once in the current raw tile-span report and current World Index under the same canonical parent `TILE_AREA` key.
2. A separate `canary-otbm-tile-deletion-approval-v1` document pins the current map, current World Index and manifest plus each selected position, parent area key, exact current raw tile SHA-256/length/node type and canonical tile SHA-256.
3. The writer removes only complete scanner-proven selected raw tile spans from a distinct current-map copy.
4. The existing parent `TILE_AREA` node is never removed or rewritten by v1. Deleting its last tile is allowed only if the resulting empty area reparses successfully.
5. The output must be byte-for-byte equal to the current map with exactly the approved selected spans omitted. The proof compares output SHA-256 and byte count to the retained current byte sequence.
6. Before publication, the candidate must pass native reparse, canonical World Index rebuild, selected-position absence checks, and bounded Semantic OTBM Diff.
7. Current map and scanner are hash/stat pinned for the operation. Output and evidence use create-new artifact-root-confined publication.
8. A structurally green result proves only bounded structural confinement. It does not prove player intent, script correctness, reachability, gameplay correctness, or physical-client behavior.

## Rejected alternatives

- Building another OTBM parser or scanner mode.
- Deleting the parent `TILE_AREA` when its last selected child is removed.
- Combining deletion with replacement, insertion, translation, or type conversion.
- Deleting individual items or reordering item stacks.
- Serializing arbitrary nodes or the complete map.
- Modifying the source map in place.
- Treating successful structural validation as gameplay approval.

## Deferred work

Separate bounded ADRs/tasks remain required for:

- explicit ordinary-tile/house-tile conversion of an existing tile;
- creation or deletion of complete `TILE_AREA` parents outside the existing complete-area replacement contract;
- integration of raw replacement/insertion/deletion operation modes into the repair/materialization orchestrator;
- non-zero x/y/z translation and dependent teleport-destination rewriting;
- arbitrary item insertion, deletion, and stack reordering;
- generic OTBM node serialization;
- direct production-map execution.

Any expansion must preserve source-copy isolation, explicit reviewed approval, format detection, native reparse, World Index rebuild, bounded Semantic Diff, and truthful non-claims.
