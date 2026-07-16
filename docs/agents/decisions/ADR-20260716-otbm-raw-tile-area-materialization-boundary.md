# ADR-20260716: Bounded raw OTBM TILE_AREA materialization boundary

Status: Accepted for the bounded v1 implementation in PR #426.

## Context

Phase 8 intentionally mutates only already-existing fixed-width attributes and must not be expanded into structural map writing. The merged donor/region planner (#424) is read-only and keeps `writerReady: false`. A safe next step is needed for reviewed same-coordinate map upgrades without building a second OTBM parser or a complete-map serializer.

The existing native scanner already validates OTBM node framing, item/tile structure and escape handling. Canonical World Index and Semantic OTBM Diff already provide post-write structural evidence.

## Decision

Introduce a separate bounded materializer with these hard limits:

1. The native materializer scanner is an extension wrapper around the existing `otbm_item_audit_scan.cpp` implementation. Existing scanner modes are delegated unchanged; the added mode records only direct `OTBM_TILE_AREA` physical subtree spans after the existing scanner successfully parses the complete map.
2. v1 accepts only `replace-region` plans with zero translation and x/y bounds aligned to complete 256x256 tile areas.
3. The planner report is never executable by itself. A separate `canary-otbm-area-materialization-approval-v1` document must pin the exact plan SHA-256, every selected area key and every non-blocking review conflict.
4. Materialization writes only a distinct artifact copy. Selected donor tile-area subtrees are copied byte-for-byte. Selected current subtrees are replaced/deleted, and donor subtrees absent from current may be inserted at the scanner-proven end of the contiguous tile-area section.
5. The implementation proves exact retained-byte equality outside selected current/output area spans and exact donor-byte equality for every selected output subtree.
6. Before publication, the output must pass the native scanner again, rebuild a canonical World Index, equal the donor World Index for every selected area, and produce a bounded Semantic OTBM Diff against current.
7. Current and donor map hashes must remain unchanged for the full operation. Output/evidence publication is create-new only and confined below the explicit artifact root.
8. A structurally green result proves bounded materialization only. It does not prove gameplay correctness, player intent, script correctness, reachability or physical-client E2E.

## Rejected alternatives

- Expanding the Phase 8 attribute patcher into tile/item/node insertion or deletion.
- Building a new complete OTBM parser or serializer.
- Heuristic donor-to-target alignment.
- Arbitrary translated fragment writing in v1.
- Tile-level overlay merging in v1.
- Treating `writerReady: false` planner output as executable without a separate approval contract.
- Modifying the source map in place.

## Deferred work

A future ADR and bounded task are required for any of:

- non-zero x/y/z translation;
- teleport destination rewriting caused by translation;
- partial-area or tile-level structural merge;
- arbitrary item stack insertion/deletion/reordering;
- generic OTBM node serialization;
- direct production-map execution.

Any such work must preserve source-copy isolation, format detection, escape safety, round-trip validation, bounded-area proof and post-write World Index/Semantic Diff verification.
