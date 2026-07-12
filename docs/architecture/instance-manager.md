# InstanceManager architecture

## Scope and boundaries

The instance subsystem builds isolated gameplay areas inside one Canary world.
It does not implement multiworld or multi-channel routing. It uses pre-carved,
physically separated regions in the existing map rather than copying the full
map for every instance.

`InstanceManager` and `InstanceRegionPool` are plain constructor-owned
components, not new `g_*()` singletons. Their eventual runtime owner should be
an explicit component such as `Game`.

## Lifecycle foundation

`InstanceManager` provides:

- strong `InstanceId` and `InstanceSlotId` types;
- `Creating -> Active -> Closing -> Destroyed` lifecycle;
- optional timeout and on-demand expiry sweeping;
- idempotent close;
- exactly-once cleanup callback outside the manager lock;
- concurrent create/close safety.

## Region-backed lifecycle

`InstanceManager` owns one `InstanceRegionPool` constructed from the complete
configured region list. There is no second vector-based slot allocator and no
independent capacity counter.

Instance creation now:

1. reserves the first free configured `InstanceMapRegion`;
2. stores the complete region in the instance record;
3. exposes the region through a read-only copy returned by `getRegion()`;
4. fails without creating a record when every region is reserved.

Instance close now:

1. marks the record `Closing`;
2. runs caller-supplied cleanup outside the manager lock and passes the complete
   reserved region;
3. releases the region only after cleanup returns successfully;
4. marks the record `Destroyed`.

If cleanup throws, the instance remains `Closing` and its region stays reserved.
This deliberately quarantines potentially dirty map space instead of exposing
it to another instance. Retry/recovery policy belongs to the later cleanup and
recovery phase.

`availableSlotCount()` and `totalSlotCount()` are compatibility names whose
values now come directly from the region pool.

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

Construction validates the complete configuration before the pool can be used:

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
- lookup of configured bounds;
- available/total counters;
- thread-safe concurrent reservations.

It deliberately does not inspect `Map`, create tiles, move players or clean
creatures.

## Remaining integration sequence

1. **Creature/spawn ownership**: creatures, summons, NPCs and spawn products
   created for an instance carry `InstanceId`; cleanup can enumerate them.
2. **Scheduler/event ownership**: scheduled callbacks carry `InstanceId`, are
   invalidated on close and cannot execute against destroyed state. The timeout
   sweep gets an actual periodic owner.
3. **Player enter/leave**: validated entry, safe return position, closing,
   logout, death and reconnect behavior.
4. **Lua API**: create/get/enter/leave/close/state with stable errors and no raw
   pointer exposure.
5. **Cleanup/recovery**: evacuate players, remove temporary creatures/items,
   cancel timers, define retry policy and return quarantined regions safely.
6. **Two parallel instances E2E**: prove region, creature, player and event
   isolation and clean region reuse.

## Tests

`instance_manager_test.cpp` covers:

- lifecycle and timeout sweeping;
- binding a concrete configured region to every instance;
- capacity derived from region availability;
- exactly-once cleanup with the concrete region;
- region release and deterministic reuse;
- cleanup-failure quarantine;
- concurrent create/close behavior.

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
- no creature, scheduler, player or Lua integration in the region-binding PR.
