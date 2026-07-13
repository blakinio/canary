# InstanceManager architecture

## Scope and boundaries

The instance subsystem builds isolated gameplay areas inside one Canary world.
It does not implement multiworld or multi-channel routing. It uses pre-carved,
physically separated regions in the existing map rather than copying the full
map for every instance.

`InstanceManager` and `InstanceRegionPool` are plain constructor-owned
components, not new `g_*()` singletons. `Game` owns the single runtime
instance through `Game::getInstanceManager()`, constructed with zero
configured regions until a concrete instanced feature defines real ones -
`createInstance()` simply fails with `"no available instance regions"` until
then. Nothing calls `getInstanceManager()` yet: spawn/NPC creation, the
scheduler and player enter/leave all still run entirely in the normal world.
This only removes the prerequisite that was blocking those follow-ups from
wiring in for real.

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
   registrations and instance interactions;
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
- destroyed or unknown instances cannot be mutated;
- insertion into both ownership indexes is transactional on allocation failure.

## Automatic cleanup on removal

`Game::removeCreature()` is the one path every removed creature passes
through (monsters, NPCs, players on logout, and summons recursively). It now
looks up `getInstanceManager().getCreatureOwner(creature->getID())` and calls
`unregisterCreature()` when an owner is found, so a registered creature's
ownership entry cannot outlive the creature itself regardless of which future
call site registered it (spawn, summon inheritance, player enter/leave).

This is intentionally generic and not spawn/NPC-specific: it closes the
"automatically unregister on removal" half of the spawn/NPC ownership
integration step below without waiting for the "register at creation" half,
which still needs a design decision (Spawn/NpcSpawn have no concept today of
"which instance am I in"). Today this is a safe no-op in production, since
nothing yet calls `registerCreature()`/`InstanceCreatureBinder::bind()`
outside tests.

## Summon inheritance and interaction policy

Ownership inheritance and interaction decisions use only stable runtime ids and
the manager's authoritative registry. They do not duplicate ownership fields or
retain creature pointers.

`inheritCreatureOwnership(masterId, summonId)` applies these rules atomically:

- invalid or identical ids fail;
- an unowned normal-world master accepts only an unowned summon and leaves both
  unowned;
- a Creating or Active instance-owned master registers an unowned summon to the
  same instance;
- inheritance is idempotent when both already share the same owner;
- a summon already owned by another instance is rejected without mutation;
- Closing or Destroyed instance owners cannot acquire new summons.

`getCreatureRelation()` centralizes the fail-closed policy used by later
visibility, targeting and combat wiring:

- two unowned runtime ids are `SameWorld`;
- two ids owned by the same Creating or Active instance are `SameInstance`;
- invalid ids, owned/unowned pairs, different owners and Closing/Destroyed
  owners are `Isolated`.

`canCreaturesInteract()` is true only for `SameWorld` and `SameInstance`.

## Runtime creature binder

`InstanceCreatureBinder` is the synchronous adapter from runtime objects to the
stable-ID registry. It accepts any object exposing `getID()` and stores only one
`InstanceManager &` reference. It never retains the supplied object, a raw
`Creature*` or a shared pointer after the call returns.

The binder:

- binds a runtime object's nonzero id to an instance through
  `registerCreature()`;
- unbinds by first resolving the authoritative reverse owner rather than
  trusting a caller-provided instance id;
- delegates master/summon inheritance to the tested manager policy;
- delegates relation and interaction decisions to the same authoritative
  registry;
- preserves normal-world behavior when both ids are unowned;
- inherits all unknown, Closing, Destroyed and cross-instance rejection rules
  from `InstanceManager`.

The adapter deliberately does not mutate `Creature` internals and does not own
runtime lifetimes. Actual spawn, `setMaster`, removal, spectator, targeting and
combat call sites remain separate focused integrations.

## Scheduler/event liveness

`InstanceScopedEvent` is the lazy-check counterpart to the creature binder: a
scheduled task can outlive the instance it was created for (the instance may
close, or never leave `Creating`, before the task fires), and `InstanceManager`
has no visibility into scheduler/dispatcher task handles, so it cannot reach in
and cancel them.

Instead, `InstanceScopedEvent` wraps the *callback* side:

- it retains only an `InstanceManager &` and an `InstanceId`, never a
  scheduler/dispatcher handle, so it stays cheap to copy into a scheduled task
  without coupling this module to a specific scheduler implementation;
- `isLive()` is true only while the instance is `Active`; `Creating`,
  `Closing`, `Destroyed` and unknown ids are all unsafe to run gameplay logic
  against;
- `runIfLive(callback)` runs the callback only if the instance is still
  `Active` at the moment it is actually invoked, and reports whether it ran.

This intentionally does not give scheduled tasks a way to keep an instance
alive, and does not touch `src/game/scheduling/*`. `Game::start()` now gives
`closeExpiredInstances()` a real periodic owner (see "Remaining integration
sequence" item 4 below). Wiring an actual dispatcher/task call site through
`InstanceScopedEvent` itself remains open - nothing schedules instance-scoped
work at all today, since nothing creates a real instance in production.

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

0. **Runtime owner**: `Game::getInstanceManager()` (done - see above). Nothing
   calls it yet.
1. **Runtime call-site wiring**: `Creature::setMaster(master, binder)` exists
   and is tested (done), but no production spawn/summon call site passes
   `Game::getInstanceManager()`'s binder to it yet - only direct unit tests
   exercise the overload today.
2. **Spawn and NPC ownership**: automatic unregistration on removal is done
   (see above, `Game::removeCreature()`). Still open: spawn/NPC creation
   itself has no concept of "which instance am I in", so nothing registers a
   spawn product's id at creation time yet - that needs a design decision on
   how a `Spawn`/`SpawnNpc` becomes instance-scoped in the first place.
3. **Cross-instance isolation**: spectator, targeting and combat call sites use
   the central relation policy while normal-world behavior stays unchanged.
4. **Scheduler/event ownership**: `InstanceScopedEvent` gives a scheduled
   callback a lazy liveness check (done - see above). `closeExpiredInstances()`
   now has a real periodic owner: `Game::start()` registers a
   `g_dispatcher().cycleEvent(EVENT_INSTANCE_TIMEOUT_SWEEP_MS, ...)` tick that
   calls `getInstanceManager().closeExpiredInstances()` (done). Still open: no
   actual dispatcher/task call site wraps its callback with
   `InstanceScopedEvent` yet - nothing schedules instance-scoped work at all,
   since nothing creates a real instance in production.
5. **Player enter/leave**: validated entry, safe return position, closing,
   logout, death and reconnect behavior.
6. **Lua API**: create/get/enter/leave/close/state with stable errors and no raw
   pointer exposure.
7. **Cleanup/recovery**: evacuate players, remove temporary creatures/items,
   cancel timers, define retry policy and return quarantined regions safely.
8. **Two parallel instances E2E**: prove region, creature, player and event
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

`instance_creature_ownership_policy_test.cpp` covers:

- normal-world summon inheritance as a no-op;
- owned-master inheritance and idempotency;
- cross-instance and owned-to-unowned boundary rejection;
- invalid/self inheritance;
- the complete interaction relation matrix;
- fail-closed behavior after close begins;
- concurrent summon inheritance.

`instance_creature_binder_test.cpp` covers:

- binding runtime objects through `getID()`;
- no dependency on the runtime object's lifetime after binding;
- invalid, unknown, Closing and cross-instance rejection;
- authoritative-owner unbind;
- owned-master summon inheritance;
- cross-instance master assignment rollback;
- unchanged normal-world relation behavior;
- fail-closed runtime relations after close begins.

`instance_scoped_event_test.cpp` covers:

- liveness true only while `Active`, false for `Creating`, unknown ids and
  after `close()`;
- liveness already false from inside the `Closing`-state cleanup callback,
  before the instance reaches `Destroyed`;
- `runIfLive()` executing the callback only while live and reporting whether
  it ran.

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
- no creature pointer ownership in `InstanceManager` or its binder;
- no direct spawn, scheduler, player or Lua integration in the binder PR;
- no dispatcher/task call site wiring or periodic sweep owner in the scoped-event PR - both need a live, `Game`-owned `InstanceManager` first;
- no spawn/NPC/scheduler/player/Lua call site changes in the `Game::getInstanceManager()` PR - it only removes the ownership prerequisite, configured with zero regions;
- no instance-scoped `Spawn`/`SpawnNpc` concept in the automatic-cleanup PR - `Game::removeCreature()` only unregisters whatever a future call site already registered.
