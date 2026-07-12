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

Instance creation:

1. reserves the first free configured `InstanceMapRegion`;
2. stores the complete region in the instance record;
3. exposes the region through a read-only copy returned by `getRegion()`;
4. fails without creating a record when every region is reserved.

Instance close:

1. marks the record `Closing`, which immediately blocks new ownership
   registrations;
2. runs caller-supplied cleanup outside the manager lock and passes the complete
   reserved region;
3. verifies that the creature identity registry is empty;
4. releases the region only after cleanup returns successfully and no registered
   creature remains;
5. marks the record `Destroyed`.

If cleanup throws or leaves a registered creature behind, the instance remains
`Closing` and its region stays reserved. This deliberately quarantines
potentially dirty map space instead of exposing it to another instance.
Retry/recovery policy belongs to the later cleanup and recovery phase.

`availableSlotCount()` and `totalSlotCount()` are compatibility names whose
values come directly from the region pool.

## Creature identity ownership foundation

`InstanceManager` maintains a bidirectional ownership index using stable runtime
creature ids (`Creature::getID()` values). It does not retain raw or shared
creature pointers.

The registry contract is:

- id `0` is invalid because it means runtime identity has not been assigned;
- registration is allowed only while an instance is `Creating` or `Active`;
- registering the same id with the same instance is idempotent;
- one creature id cannot be registered to two instances;
- cleanup can enumerate ids deterministically and unregister them while the
  instance is `Closing`;
- a non-empty registry prevents region release and quarantines the instance;
- destroyed or unknown instances cannot be mutated.

This PR establishes lifecycle-safe bookkeeping only. A follow-up wires the
registry to `Creature`, summon inheritance, instance-aware spawns and actual
creature removal.

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

1. **Creature metadata and spawn wiring**: creatures, summons, NPCs and spawn
   products created for an instance carry `InstanceId` and register their stable
   runtime ids; cleanup removes them.
2. **Cross-instance isolation**: visibility, targeting and ownership changes are
   rejected across instance boundaries while normal-world behavior stays
   unchanged.
3. **Scheduler/event ownership**: scheduled callbacks carry `InstanceId`, are
   invalidated on close and cannot execute against destroyed state. The timeout
   sweep gets an actual periodic owner.
4. **Player enter/leave**: validated entry, safe return position, closing,
   logout, death and reconnect behavior.
5. **Lua API**: create/get/enter/leave/close/state with stable errors and no raw
   pointer exposure.
6. **Cleanup/recovery**: evacuate players, remove temporary creatures/items,
   cancel timers, define retry policy and return quarantined regions safely.
7. **Two parallel instances E2E**: prove region, creature, player and event
   isolation and clean region reuse.

## Tests

`instance_manager_test.cpp` covers:

- lifecycle and timeout sweeping;
- binding a concrete configured region to every instance;
- capacity derived from region availability;
- exactly-once cleanup with the concrete region;
- stable creature id registration and deterministic enumeration;
- same-owner idempotency and cross-instance ownership rejection;
- cleanup-time unregistration;
- creature-leak quarantine before region release;
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
- no creature pointer ownership in `InstanceManager`;
- no spawn, scheduler, player or Lua integration in the creature-registry PR.
