# ADR: OTBM reachability uses strict/optimistic geometry and reviewed floor transitions

- Status: accepted
- Date: 2026-07-13
- Scope: offline OTBM analysis tooling
- Coordination: `OTS-OTBM-VALIDATION`

## Context

The merged World Index exposes exact tiles, item placements, AID/UID/house-door attributes and teleport destinations. The appearances catalogue exposes ground, unpassable, avoid and interaction flags. Neither contract proves the destination offset or direction of every stair, hole, ladder or rope spot, and static data cannot prove current door, quest, storage or dynamic-script state.

A single passable/blocked graph would either create false routes by assuming doors and dynamic mechanics are open, or create false failures by assuming every conditional mechanic is permanently closed. Inferring cross-floor offsets from sprite imagery or item names would also violate the evidence-based map policy.

## Decision

1. Reachability analyses require an explicit bounded region plus explicit origins/start-goal routes.
2. Same-floor geometry is derived from the existing World Index and real appearance flags.
3. Two graphs are emitted:
   - strict: confirmed ground, no static blocker, no conditional blocker and no unknown appearance;
   - optimistic: confirmed ground and no static blocker, while conditional/unknown state remains reported.
4. Indexed teleport destinations are consumed automatically.
5. Stairs, ladders, holes, rope spots and other non-teleport floor changes require a reviewed `canary-otbm-transition-manifest-v1` edge with an explicit destination or delta.
6. Optional script-resolution status is preserved; unresolved/conflicting evidence is never promoted to handled.
7. Four-direction movement is the default. Optional diagonals require both orthogonal corner tiles and never cut corners.
8. The tool remains read-only and cannot authorize map writes.

## Consequences

Positive:

- confirmed paths remain distinguishable from condition-dependent paths;
- unknown appearance or script state is visible instead of guessed;
- non-teleport cross-floor edges are reviewable and hashable;
- no new OTBM parser, renderer or items database is created;
- downstream quest/spawn/storage/diff tools can reuse one deterministic report.

Trade-offs:

- a complete multi-floor route requires reviewed transition entries when the map does not use explicit teleport attributes;
- strict reachability can be intentionally conservative;
- optimistic reachability is not gameplay proof;
- live door, quest and dynamic-script behavior still requires runtime/E2E validation.

## Rejected alternatives

- **Infer stairs/holes from sprite names or visuals:** rejected because destination offset and direction are not proven.
- **Treat every unpassable usable item as walkable:** rejected because it hides closed doors and quest gates.
- **Treat every unknown appearance as permanently blocked:** rejected as the only result; strict mode blocks it, while optimistic mode preserves a conditional route when confirmed ground exists.
- **Create another OTBM parser or embed map writing:** rejected because the World Index is the canonical read-only cache and map writing remains a later gated phase.
