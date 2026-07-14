# ADR-20260714: Bound the first OTBM writer to existing fixed-width attributes

- Status: accepted for Phase 8 implementation
- Date: 2026-07-14
- Decision owners: OTS OTBM validation program
- Scope: offline tooling in `tools/ai-agent`; no runtime or active map change

## Context

The existing OTBM tooling can index, resolve, compare, audit and render map evidence, but it is intentionally read-only. A first write-capable tool creates a materially higher corruption risk because OTBM is a node stream with escaped marker bytes. A logical payload byte may therefore occupy a different number of physical bytes, and a general serializer could reorder or rewrite unrelated data even when the intended change is small.

The repository already has one native structural scanner, canonical World Index and Semantic Diff implementations. Building another parser or serializer would duplicate format knowledge and weaken the proof chain.

## Decision

Phase 8 may replace only a payload that satisfies every condition below:

1. The attribute already exists on an item node.
2. It is one of action ID, unique ID, house-door ID or teleport destination.
3. Its payload is fixed-width at the logical format level.
4. The existing native scanner exposes every logical payload byte with exact physical offset, encoded size and decoded value.
5. The reviewed plan pins source hash, size, OTBM/items versions, bounded region, exact target identity, expected old value and replacement value.
6. Every replacement logical byte retains the same physical escape width as the source byte.
7. The source is never an output and remains byte-for-byte untouched.
8. The output has identical byte length and differs only at the exact scanner-proven logical payload locations; an escape prefix inside an encoded span remains immutable.
9. Full native reparse, before/after World Index and bounded Semantic Diff prove exactly the planned mechanic changes.
10. Target paths reject destination and parent symlinks, path escape and overwrite.
11. Publication is external, no-overwrite and atomic; rollback is deletion of the patched copy.

The Python layer orchestrates and validates scanner evidence. It does not parse the OTBM tree independently.

## Target identity

An operation is matched by the tuple:

```text
(x, y, z, tilePlacementIndex, itemId, itemDepth, attribute)
```

The expected old value is validated separately. Redundant identity is intentional. Item ID or position alone is insufficient when one tile contains duplicate items or nested containers.

Repeated matching attributes are ambiguous and must be rejected rather than resolved heuristically.

## OTBM escape-width invariant

The native scanner decodes properties but now also records physical spans. Canonical marker bytes `0xFD`, `0xFE` and `0xFF` occupy two bytes in the file: the escape prefix `0xFD` followed by the logical value. Other logical bytes occupy one byte.

For every payload position:

```text
encoded_width(old_logical_byte) == recorded_physical_size
encoded_width(new_logical_byte) == recorded_physical_size
changed_physical_offset == recorded_offset + (recorded_physical_size == 2 ? 1 : 0)
```

A replacement such as `0xFC -> 0xFD` is rejected because it would increase the physical width and shift the remaining node stream. Non-canonical source escape encodings are also rejected in v1. The escape prefix is structural framing and cannot be part of the permitted changed-byte set.

## Consequences

### Positive

- No second OTBM parser or complete-map serializer is introduced.
- The changed payload-byte set is explicit and independently comparable.
- File length, escape framing and all following offsets remain stable.
- Plans are version- and state-pinned and cannot silently apply to another map revision.
- Semantic validation uses the already reviewed World Index and Semantic Diff contracts.
- Destination and parent symlinks cannot redirect published artifacts.
- The untouched source provides immediate rollback.

### Negative

- The tool cannot repair a missing attribute.
- Values crossing an OTBM escape-width boundary cannot be changed in v1.
- General geometry, stack, item and tile edits remain unsupported.
- A full before/after index and diff can be expensive on large maps; this cost is accepted for the first writer safety boundary.
- Output and evidence must be on the artifact-root filesystem to support atomic no-overwrite publication.

## Rejected alternatives

### Reuse an RME save operation for a one-field change

Rejected for this phase. A complete save can rewrite unrelated serialization details and makes byte-level confinement harder to prove. RME remains a read-only format reference and optional manual review surface.

### Implement a Python OTBM parser/writer

Rejected. It would duplicate the existing native parser and create two authorities for node traversal and escaping.

### Patch by searching for an encoded value near a coordinate

Rejected. Byte signatures are not unique and do not establish item identity, depth or attribute ownership.

### Allow file growth while recalculating offsets

Rejected. That becomes a structural writer and requires a separate architecture and validation model.

### Treat a successful reparse as sufficient

Rejected. A structurally valid map can still contain unintended mechanic, stack or tile changes. Exact outside-payload equality and exact Semantic Diff are both required.

## Follow-up boundary

Any future support for inserting attributes, changing item IDs, editing stacks, adding/removing items or tiles, or reserializing nodes requires a new ADR and a separate task. Success of this fixed-width patcher is evidence for the validation pipeline, not approval for a general writer.
