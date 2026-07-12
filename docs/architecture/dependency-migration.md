# Dependency migration: reducing global singleton coupling

## Starting point (read this before assuming there's a big rewrite ahead)

The premise "the engine is full of raw `g_x()` Meyers singletons that need
migrating to DI" turned out to be mostly **already done**. This repo has a
working `boost::di`-based container (`src/lib/di/`, see `src/lib/di/README.md`)
and the standard migration path it documents —

```
global function  ->  dependency accessor (inject<T>())  ->  constructor injection
```

— has already been applied to nearly every `g_x()` accessor in the codebase.
`ConfigManager::getInstance()`, `Database::getInstance()`,
`Dispatcher::getInstance()`, `Game::getInstance()`, and 33 others already read:

```cpp
Game &Game::getInstance() {
	return inject<Game>();
}
```

instead of the old

```cpp
Game &Game::getInstance() {
	static Game instance;
	return instance;
}
```

`inject<T>()` (`src/lib/di/injector.hpp`) resolves through `DI::get<T>()`,
which checks a test-installed container first (`DI::setTestContainer`) before
falling back to the process-wide default container. This preserves the exact
shared-instance behavior of the old Meyers singleton in production (same
object, every call), while giving tests a documented way to swap in an
isolated or fake instance (`tests/unit/lib/di/soft_singleton_test.cpp` and
`tests/unit/security/rsa_test.cpp` already do this for `Logger` via
`InMemoryLogger`).

So the real remaining work here isn't "introduce DI" - it's (a) finding the
handful of accessors that were never migrated, and (b) planning the next
tier: call sites still reach in via the global accessor even for
already-migrated types, rather than receiving their dependency through a
constructor. That second tier is real work and is *not* attempted in this
PR - see "What's next" below.

## Full audit

Every `g_x()` global accessor in `src/`, and whether its `getInstance()`
already routes through `inject<T>()`:

| Accessor | Class | Status | Category |
|---|---|---|---|
| `g_game` | `Game` | DI-backed | process-global |
| `g_dispatcher` | `Dispatcher` | DI-backed | process-global |
| `g_eventsScheduler` | `EventsScheduler` | DI-backed | process-global |
| `g_configManager` | `ConfigManager` | DI-backed | process-global |
| `g_database` | `Database` | DI-backed | process-global |
| `g_databaseTasks` | `DatabaseTasks` | DI-backed | process-global |
| `g_accountRepository` | `AccountRepository` | DI-backed (explicitly bound to `AccountRepositoryDB`) | process-global |
| `g_kv` | `KVStore` | DI-backed (explicitly bound to `KVSQL`) | process-global |
| `g_logger` | `LogWithSpdLog` | DI-backed (explicitly bound, `Logger` interface) | easy-to-mock (already mocked in tests) |
| `g_RSA` | `RSAManager` | DI-backed | process-global |
| `g_threadPool` | `ThreadPool` | DI-backed | process-global |
| `g_saveManager` | `SaveManager` | DI-backed | process-global |
| `g_gameReload` | `GameReload` | DI-backed | process-global |
| `g_modules` | `Modules` | DI-backed | process-global |
| `g_scripts` | `Scripts` | **raw Meyers** | process-global, real call sites (see below) |
| `g_luaEnvironment` | `LuaEnvironment` | DI-backed | process-global |
| `g_callbacks` | `EventsCallbacks` | DI-backed | process-global |
| `g_globalEvents` | `GlobalEvents` | DI-backed | world-dependent |
| `g_moveEvents` | `MoveEvents` | DI-backed | world-dependent |
| `g_creatureEvents` | `CreatureEvents` | DI-backed | world-dependent |
| `g_actions` | `Actions` | DI-backed | world-dependent |
| `g_events` | `Events` | DI-backed | world-dependent |
| `g_talkActions` | `TalkActions` | DI-backed | world-dependent |
| `g_spells` | `Spells` | DI-backed | world-dependent |
| `g_monsters` | `Monsters` | DI-backed | world-dependent |
| `g_npcs` | `Npcs` | DI-backed | world-dependent |
| `g_chat` | `Chat` | DI-backed | world-dependent |
| `g_vocations` | `Vocations` | DI-backed | world-dependent |
| `g_storages` | `Storages` | DI-backed | world-dependent |
| `g_imbuements` | `Imbuements` | DI-backed | world-dependent |
| `g_imbuementDecay` | `ImbuementDecay` | DI-backed | world-dependent |
| `g_weapons` | `Weapons` | DI-backed | world-dependent |
| `g_decay` | `Decay` | DI-backed | world-dependent |
| `g_webhook` | `Webhook` | DI-backed | process-global |
| `g_metrics` | `Metrics` (feature-gated real/no-op variants) | DI-backed | process-global |
| `g_iobestiary` | `IOBestiary` | DI-backed | world-dependent |
| `g_ioBosstiary` | `IOBosstiary` | DI-backed | world-dependent |
| `g_ioprey` | `IOPrey` | DI-backed | world-dependent |
| `g_counterPointer` | `SharedPtrManager` | **migrated in this PR** | easy-to-mock, zero production call sites |
| `g_channelContext` | `ChannelContext` | DI-backed | instance/channel-dependent (multichannel) |
| `g_channelRegistry` | `ChannelRegistry` | DI-backed | instance/channel-dependent (multichannel) |
| `g_clusterRuntime` | `ClusterRuntime` | raw Meyers | instance/channel-dependent (multichannel) - **out of scope, see below** |

Also relevant: `Map` (`src/game/game.hpp`, `Map map;`) is **not** a global
singleton at all - it's a plain member owned by `Game`. It's reached through
`g_game()` transitively, which still means "the map" is effectively a
process-global today, but the ownership shape (one `Map` value, owned by one
object) is exactly what per-instance map ownership will build on for
Zadanie E - it doesn't need to become its own singleton first.

### Multichannel-owned singletons are excluded

`g_clusterRuntime` / `ClusterRuntime` is a raw Meyers singleton and would
otherwise be a fine small-module candidate, but it's multichannel/cluster
code, which is explicitly out of scope for this workstream. Left untouched.

## Category breakdown (as requested)

1. **Process-global, genuinely global**: `g_configManager`, `g_database`,
   `g_databaseTasks`, `g_accountRepository`, `g_kv`, `g_logger`, `g_RSA`,
   `g_threadPool`, `g_saveManager`, `g_gameReload`, `g_modules`, `g_scripts`,
   `g_luaEnvironment`, `g_callbacks`, `g_webhook`, `g_metrics`,
   `g_counterPointer`, `g_dispatcher`, `g_eventsScheduler`. One server
   process, one instance of each, for the lifetime of the process. These are
   legitimate candidates for staying DI-backed singletons long-term;
   "migration" for these means constructor injection at call sites, not
   eliminating the shared instance.
2. **World-dependent**: `g_game` and everything that only makes sense
   relative to "the currently loaded world" - `g_globalEvents`,
   `g_moveEvents`, `g_creatureEvents`, `g_actions`, `g_events`,
   `g_talkActions`, `g_spells`, `g_monsters`, `g_npcs`, `g_chat`,
   `g_vocations`, `g_storages`, `g_imbuements`, `g_imbuementDecay`,
   `g_weapons`, `g_decay`, `g_iobestiary`, `g_ioBosstiary`, `g_ioprey`, and
   `Map` (via `Game`). Single-world today, so "world-dependent" and
   "process-global" collapse to the same thing in practice - but these are
   the ones that would need to become per-world/per-instance if that ever
   changes, so they're kept in their own bucket rather than merged with #1.
3. **Instance-dependent**: `g_channelContext`, `g_channelRegistry`,
   `g_clusterRuntime` - all multichannel, all out of scope here. Zadanie E's
   `InstanceManager` will need its own instance-scoped equivalents
   eventually, but that's Zadanie E's problem, not something this audit
   should pre-design.
4. **Easy to inject a fake for in tests today**: `g_logger` (already has
   `InMemoryLogger`), and now `g_counterPointer` (no interface to swap, but a
   test container gives it an isolated instance - see this PR's test).
   Everything else in category 1/2 is DI-backed but has no fake
   implementation registered anywhere, so "easy" here specifically means
   "already proven in a real test," not just "goes through inject<T>()."

## This PR

`SharedPtrManager` (`g_counterPointer`, `src/utils/counter_pointer.{hpp,cpp}`)
was the raw-Meyers singleton with the least risk to migrate: it's ~30 lines,
has no production call sites at all (`grep -rn g_counterPointer src` outside
its own definition returns nothing), and needed zero new bindings - it's a
concrete, default-constructible class, exactly the shape `inject<T>()`
already handles for the 37 other unbound-concrete-type accessors in this
codebase.

Change: `SharedPtrManager::getInstance()` now returns `inject<SharedPtrManager>()`
instead of a function-local `static SharedPtrManager instance;`. Nothing else
changed. `tests/unit/utils/counter_pointer_test.cpp` pins down that (a) the
default container still gives every caller the same shared instance (no
runtime behavior change), and (b) a test-installed container now gives an
isolated instance instead (the actual testability gain).

## What's next

In migration order, smallest/lowest-risk first:

1. **`g_scripts` / `Scripts`** (`src/lua/scripts/scripts.{hpp,cpp}`) - the
   only other raw-Meyers, non-multichannel singleton. ~14 real call sites
   (`grep -rl "g_scripts()" src`), all in event/script-registration modules
   (`spells.cpp`, `npcs.cpp`, `globalevent.cpp`, `talkaction.cpp`,
   `creatureevent.cpp`, `actions.cpp`, `movement.cpp`, `event_callback.cpp`,
   and a couple of Lua binding files). Same one-line change as this PR
   (`return inject<Scripts>();`), but because it has real callers, it needs
   an actual CI build/test round-trip to confirm nothing regressed - this
   sandbox can't compile the C++ engine, so that verification has to happen
   in CI, not before opening the PR.
2. **Category 1 constructor injection, one module at a time**: pick a
   process-global type whose consumers are a small, well-defined set (e.g.
   `SaveManager` or `SharedPtrManager` once it has real callers) and change
   *that module's* constructor to accept its dependency instead of calling
   `g_x()` internally, keeping the `g_x()` accessor as the production
   wiring path (`SomeClass(SomeDep &dep = g_someDep())` or an explicit
   factory) so nothing else has to change. This is the actual "constructor
   injection" end state the DI README describes as better than the
   `inject<T>()` contextual-injection shortcut, and it's real, per-module
   work - not something to batch across many modules in one PR.
3. **`Map` ownership**: once Zadanie E's `InstanceManager` needs more than
   one map region, decide whether `Map` moves from a `Game` member to
   something `InstanceManager`-owned. Not before then - there is exactly one
   world today, and pre-building for multi-instance map ownership without a
   consumer is exactly the kind of premature abstraction this workstream is
   supposed to avoid.
4. **Multichannel singletons** (`g_clusterRuntime`, and re-checking
   `g_channelContext`/`g_channelRegistry`'s actual DI usage) are explicitly
   deferred to whoever owns that workstream - not this one.

Each of these should stay its own small PR, per the same reasoning as this
one: a compatibility-preserving accessor change is cheap to review and
revert in isolation; a batch of them, or a batch mixed with real call-site
refactors, is not.
