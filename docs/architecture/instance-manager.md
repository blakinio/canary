# InstanceManager architecture

## Scope and boundaries

The instance subsystem builds isolated gameplay areas inside one Canary world.
It does not implement multiworld or multi-channel routing. It uses pre-carved,
physically separated regions in the existing map rather than copying the full
map for every instance.

`InstanceManager` and `InstanceRegionPool` are plain constructor-owned
components, not new `g_*()` singletons. Their eventual owner should be an
explicit runtime component such as `Game`.

## Lifecycle foundation

`InstanceManager` provides:

- strong `InstanceId` and `InstanceSlotId` types;
- `Creating -> Active -> Closing -> Destroyed` lifecycle;
- optional timeout and on-demand expiry sweeping;
- fixed-capacity slot reservation;
- idempotent close;
- exactly-once cleanup callback outside the manager lock;
- concurrent create/close safety.

A slot is released only after cleanup completes and the record reaches
`Destroyed`.

## Map region pool

`InstanceRegionPool` gives each `InstanceSlotId` concrete map meaning without
owning or copying tiles.

Each `InstanceMapRegion` contains inclusive XYZ bounds:

```text
slot
minX, minY, minZ
maxX, maxY, maxZ
name
```

Construction validates the complete configuration before the pool can be
used:

- slot id must not be `Invalid`;
- minimum coordinates must not exceed maximum coordinates;
- floors must stay within Tibia's `0..15` range;
- slot ids must be unique;
- no two regions may overlap on X, Y and Z simultaneously.

Regions with the same X/Y bounds are valid when their Z ranges are disjoint.
Touching regions are valid only when their inclusive bounds do not share a
coordinate.

The pool supports:

- deterministic reserve-any in configuration order;
- reservation of a specific slot;
- release and reuse;
- lookup of configured bounds before reservation;
- available/total counters;
- thread-safe concurrent reservations.

It deliberately does not inspect `Map`, create tiles, move players or clean
creatures. Those responsibilities belong to later integration layers.

## Integration sequence

1. **Connect `InstanceManager` to `InstanceRegionPool`** so instance creation
   reserves a real configured region rather than an opaque vector index, while
   preserving the current constructor/API as a compatibility adapter if
   needed.
2. **Creature/spawn ownership**: creatures, summons, NPCs and spawn products
   created for an instance carry `InstanceId`; cleanup can enumerate them.
3. **Scheduler/event ownership**: scheduled callbacks carry `InstanceId`, are
   invalidated on close and cannot execute against destroyed state. The
   timeout sweep gets an actual periodic owner.
4. **Player enter/leave**: validated entry, safe return position, closing,
   logout, death and reconnect behavior.
5. **Lua API**: create/get/enter/leave/close/state with stable errors and no raw
   pointer exposure.
6. **Cleanup/recovery**: evacuate players, remove temporary creatures/items,
   cancel timers and return a region only after cleanup succeeds.
7. **Two parallel instances E2E**: prove region, creature, player and event
   isolation and clean slot reuse.

## Current tests

`instance_manager_test.cpp` covers lifecycle, capacity, timeout sweeping,
exactly-once cleanup and concurrent create/close behavior.

`instance_region_pool_test.cpp` covers:

- bounds and floor validation;
- containment and three-dimensional overlap semantics;
- duplicate and overlapping region rejection;
- deterministic reserve/release/reuse;
- lookup of configured bounds;
- concurrent reservations never returning the same slot.

## Explicit non-goals

- no full-map copies;
- no multiworld identifiers;
- no channel identifiers;
- no global `InstanceManager` singleton;
- no map ownership move before a real integration requires it;
- no gameplay/Lua API in the region-pool PR.
