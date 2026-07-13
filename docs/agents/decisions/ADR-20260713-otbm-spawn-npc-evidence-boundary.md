# ADR: Phase 4 consumes explicit active spawn evidence and Phase 3 geometry

- Status: accepted
- Date: 2026-07-13
- Decision owners: OTS OTBM validation programme

## Context

Canary loads static monsters and NPCs from companion XML, resolves creature types from Lua registrations and can create creatures dynamically from Lua. A useful validator must correlate these sources with the real map without pretending that source text proves successful runtime creation.

The repository already has a canonical OTBM scanner/World Index and a strict/optimistic reachability validator. Re-parsing OTBM or creating another walkability implementation would create contradictory evidence.

## Decision

1. Phase 4 scans one explicit datapack root and only explicit companion spawn XML files.
2. Paths and globs must remain below that root; symlink and traversal escapes fail closed.
3. Static XML coordinates follow the current C++ loaders: child x/y are offsets and runtime z is `centerz`; child z is evidence only.
4. Creature names resolve only against active literal `Game.createMonsterType` / `Game.createNpcType` registrations. Missing and duplicate definitions remain explicit.
5. Runtime spawn-block boss evidence follows `MonsterType::isBoss()` and therefore tracks a literal non-empty Bosstiary class separately from `rewardBoss`.
6. Monster spawntime above one day remains rate-dependent until runtime rate scaling; the validator does not claim an unconditional clamp.
7. Dynamic Lua is never executed. Only literal name/position calls are resolved; all other calls remain `unresolved`.
8. Exact tile existence comes from the existing World Index.
9. Walkability comes from `canary-otbm-reachability-v1`. Truncated Phase 3 diagnostics fail closed.
10. Findings are evidence for review, not automatic authorization to change spawn XML, definitions, scripts or OTBM.
11. Generated reports, maps, indexes and renders stay outside Git.

## Consequences

- The tool can prove exact static positions, definitions, map tile presence and bounded strict/optimistic geometry.
- It can identify missing definitions, invalid intervals, ignored child floors, radius inconsistencies, static/dynamic overlaps and blocked/missing placements.
- It cannot prove scheduler execution, player-dependent spawn blocking, zone variants, storage conditions, quest completion or live gameplay.
- Optional/custom/event XML is excluded unless explicitly selected after its active load path is proven.
- Phase 5 may consume Phase 4 creature evidence, but it must not reinterpret unresolved Lua as confirmed execution.
