# OAM-038 World Zones revalidation

## Final disposition

`world-zones → REUSE`

## Baselines

- Canary OAM-038 preflight merge: `615648ae0b17c18ee58c3f118b38f78607316a2d`
- Canary fresh governance base: `5db171bbee0af3d3c64b88cb34a7fa936b037860`
- Otheryn target task-start base: `651ff1c6261eb25bd0992d7530e50e3690c2b5de`
- canonical target/upstream `src/game/zones/zone.cpp` blob: `f80af238eb2b4b10193a9b5961652591d9dafeb5`
- canonical target/upstream `src/game/zones/zone.hpp` blob: `d413dccc690d37dc1a24af6c5d2e630b14b087d1`

## Selection and ownership

Canonical `world-zones` owns the zone registry by name, id and position, static and dynamic zone lifecycle, area and position indexing, creature/player/monster/NPC/item membership caches, remove destinations and bulk removal, refresh, monster-variant metadata and XML zone loading. Tile protection/PvP flag semantics, quest/event scripting inside zones, instance region allocation, generic map runtime, protocol/client, physical-client orchestration, map content, assets, schema and deployment remain outside OAM-038.

The clean Otheryn target and reviewed fresh upstream share exact canonical `zone.cpp` and `zone.hpp` roots. The older legacy Canary roots are not a stronger whole-module donor because the target retains `cacheMutex` protection around weak membership-cache reads, writes, removals and refresh plus safer typed weak-pointer erasure behavior.

Identity alone was not accepted. The bounded target source-contract proof verified registry/index lifecycle, area index/unindex cleanup, synchronized weak membership caches, dynamic-zone cleanup while preserving static zones, remove-destination and bulk removal surfaces, monster-variant propagation and XML loading. Existing `zone_weak_cache_test.cpp` separately continues to prove expired weak owners are pruned without changing key ordering.

## Target proof

Otheryn PR #79 final head `a2a6eb155a2c2ec4bf74524b94c1df9ebf72f7d1` changed exactly four intended proof/task paths and no production runtime/data path. Exact-head autofix run `29995158391`, CI run `29995158283` and Required run `29995157990` all succeeded. Fast checks, Lua tests, Linux release runtime smokes, Linux debug including database import and full `Run Tests`, both Windows build paths and macOS all succeeded.

Comments, submitted reviews and review threads were empty. Otheryn `main` had no drift from immutable target base before merge. PR #79 squash-merged as `d1ce61df934843e2f54800f4ea9efce6cf374a09`.

## Final conclusion

OAM-038 is `REUSE`: preserve the existing canonical world-zones registry, indexing and synchronized membership-cache lifecycle and add proof only. No production repair, maintained-client mutation or protocol change was required.

## Nonclaims

OAM-038 does not claim exhaustive zone membership or eviction correctness under every movement/reload/concurrency schedule, tile protection/PvP flag correctness, quest/event behavior inside zones, instance isolation, exact monster-variant gameplay semantics, map-content parity, persistence guarantees, protocol/client compatibility, physical-client E2E closure or full Real Tibia parity.
