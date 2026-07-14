# ADR-20260714: OTBM geometry audit evidence boundary

## Status

Accepted for Phase 7 implementation.

## Context

Geometry findings mix exact binary facts with visual or gameplay expectations. The canonical World Index proves tile positions, raw flags, house IDs, item stacks and mechanic attributes. The appearances catalogue proves selected object flags and sprite identifiers. Neither source alone proves intended wall style, runtime connectivity, transparent sprite pixels, quest state or player reachability.

Phase 3 already defines ground and blocker classification. Phase 6 already owns semantic comparison and factual renderer integration. Building another parser, walkability engine or renderer would create conflicting policy.

## Decision

1. Phase 7 requires one explicit inclusive region capped at 1,000,000 coordinates.
2. It consumes the canonical World Index and reuses the Phase 3 tile classifier.
3. `item-without-floor` is exact evidence that no supplied appearance marks any indexed placement as ground.
4. Multiple ground placements are warnings because layered ground may be intentional.
5. Cardinal components are bounded structural evidence. Small or disconnected components remain review candidates; boundary contact lowers confidence.
6. House continuity uses exact house IDs and cardinal components only.
7. Only OTBM protection-zone bit `0x0001` is interpreted. The value is verified in current read-only Remere's Map Editor `source/tile.h`; all other raw tile flags remain opaque.
8. Wall and border consistency requires a reviewed versioned adjacency-rule manifest. Names, sprites and proximity do not create implicit rules.
9. An invisible-blocker candidate requires `unpassable` appearance evidence and no nonzero sprite ID. It remains low confidence because sprite pixels and runtime state are not inspected.
10. Factual render requests use the existing renderer and real external inputs. AI-generated or stylized images are excluded.
11. Reports are deterministic, bounded, provenance-verified and atomic. Maps, indexes, appearances, assets, generated reports and renders stay outside Git.
12. Findings do not authorize map repair or Phase 8 writes.

## Consequences

- The audit intentionally emits fewer wall/border findings until maintainers provide reviewed adjacency rules.
- PZ conclusions are limited to one verified bit and selected-scope geometry.
- Component warnings can contain false positives from runtime transitions or intentionally isolated construction, but their exact positions and scope limitations remain reviewable.
- Phase 8 remains blocked until Phase 7 implementation, validation and lifecycle completion are merged.
