# ADR-20260717: Bound OTBM raw tile type conversion to approved complete-subtree replacement

## Status

Accepted for bounded implementation.

## Context

The repository already has canonical OTBM World Index and Semantic Diff tooling plus approval-gated complete raw tile replacement, insertion and deletion materializers. The remaining explicitly queued same-coordinate structural operation is conversion between ordinary `OTBM_TILE` and `OTBM_HOUSETILE` nodes.

An ordinary tile and a house tile do not share an interchangeable raw property layout. A house tile carries additional house metadata, including its house ID. Editing only the node type could therefore reinterpret or omit bytes incorrectly. Synthesizing house metadata or allocating a house ID would introduce semantics not present in reviewed source evidence.

## Decision

Implement v1 tile type conversion only as replacement of complete scanner-proven raw tile subtrees with complete donor subtrees when all of the following are true:

- the absolute position is unchanged;
- the canonical parent `TILE_AREA` is unchanged;
- current and donor each contain exactly one tile at every selected position;
- current and donor node types are both in `{OTBM_TILE, OTBM_HOUSETILE}` and are different;
- a separate approval pins current/donor maps, World Indexes, manifests, complete raw subtree hashes, lengths, node types and canonical tile hashes;
- the existing raw complete-tile replacement writer is reused for byte materialization;
- all non-selected current bytes remain exact;
- selected output raw subtrees equal donor byte-for-byte;
- native reparse, output World Index rebuild, selected canonical donor equality and bounded Semantic Diff all pass before create-new publication.

No parser, scanner mode, generic serializer or item-level writer is added.

## Consequences

This supports both `OTBM_TILE → OTBM_HOUSETILE` and `OTBM_HOUSETILE → OTBM_TILE` without inventing house metadata and without expanding into a generic writer.

A conversion requires a real reviewed donor subtree. The materializer cannot create a house tile from an ordinary tile by assigning an inferred or generated house ID, and cannot preserve selected current children while independently changing only the tile type.

The resulting output is structural evidence only. It does not prove that a referenced house exists in runtime house data, that doors have correct house semantics, or that gameplay is correct. Those require the existing audits and, where needed, separate runtime or E2E evidence.

## Rejected alternatives

### Patch the node-type byte in place

Rejected because `OTBM_TILE` and `OTBM_HOUSETILE` property layouts differ and byte reinterpretation is unsafe.

### Synthesize a house ID or house metadata

Rejected because the tool must not invent map or runtime identifiers or semantics.

### Add a generic tile or node serializer

Rejected because complete donor subtrees and the existing byte-confinement writer are sufficient for this bounded operation. A generic serializer would expand the write boundary without being required.

### Combine conversion with translation, insertion, deletion or item-stack editing

Rejected for v1. Those are separate structural semantics with separate approval and verification requirements.
