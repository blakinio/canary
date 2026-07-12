# Dependency migration: reducing global singleton coupling

## Starting point

The premise that Canary still needs a broad migration from raw `g_x()` Meyers
singletons to dependency injection is outdated in this fork. The repository
already has a working `boost::di` container under `src/lib/di/`, and the normal
compatibility-preserving path is:

```text
global function -> dependency accessor using inject<T>() -> constructor injection where useful
```

`ConfigManager`, `Database`, `Dispatcher`, `Game`, `Logger` and the other
standard services resolve through `inject<T>()`. The default container still
returns one shared production instance, while tests can install an isolated
container with `DI::setTestContainer()`.

The accessor migration is now complete for non-multichannel code. Future work
is limited to constructor injection in modules where it provides concrete
instance isolation or testability benefits.

## Audit summary

| Accessor | Class | Current state | Category |
|---|---|---|---|
| `g_game` | `Game` | DI-backed | process/world-global |
| `g_dispatcher` | `Dispatcher` | DI-backed | process-global |
| `g_eventsScheduler` | `EventsScheduler` | DI-backed | process-global |
| `g_configManager` | `ConfigManager` | DI-backed | process-global |
| `g_database` | `Database` | DI-backed | process-global |
| `g_databaseTasks` | `DatabaseTasks` | DI-backed | process-global |
| `g_accountRepository` | `AccountRepository` | DI-backed, interface binding | process-global |
| `g_kv` | `KVStore` | DI-backed, interface binding | process-global |
| `g_logger` | `Logger` / `LogWithSpdLog` | DI-backed, interface binding | easy to fake |
| `g_RSA` | `RSAManager` | DI-backed | process-global |
| `g_threadPool` | `ThreadPool` | DI-backed | process-global |
| `g_saveManager` | `SaveManager` | DI-backed | process-global |
| `g_gameReload` | `GameReload` | DI-backed | process-global |
| `g_modules` | `Modules` | DI-backed | process-global |
| `g_scripts` | `Scripts` | DI-backed by the Scripts migration | process-global, isolated in tests |
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
| `g_metrics` | `Metrics` | DI-backed | process-global |
| `g_iobestiary` | `IOBestiary` | DI-backed | world-dependent |
| `g_ioBosstiary` | `IOBosstiary` | DI-backed | world-dependent |
| `g_ioprey` | `IOPrey` | DI-backed | world-dependent |
| `g_counterPointer` | `SharedPtrManager` | DI-backed by PR #117 | easy to isolate |
| `g_channelContext` | `ChannelContext` | DI-backed | multi-channel |
| `g_channelRegistry` | `ChannelRegistry` | DI-backed | multi-channel |
| `g_clusterRuntime` | `ClusterRuntime` | raw Meyers | multi-channel, out of scope |

`Map` is not a global singleton. It is a value owned by `Game`. It is reached
through `g_game()` today, so it behaves as a process-global map in practice,
but its ownership should only change when the instance subsystem has a real
consumer for separate regions or map state.

## Categories

### Process-global services

Configuration, database access, logging, thread pool, save/reload services,
metrics and similar process-lifetime services can legitimately remain
DI-backed singletons. Future work for these should be selective constructor
injection at well-defined consumers, not elimination of the shared instance.

### World-dependent services

Game state, map access, events, actions, spells, monsters, NPCs, chat,
vocations, storages, imbuements, decay and bestiary/prey services are one-per
world today. Their access pattern only needs to change when a concrete
multi-instance ownership boundary requires it.

### Multi-channel services

`ChannelContext`, `ChannelRegistry` and `ClusterRuntime` belong to the separate
multi-channel workstream. Further multi-channel development is currently
paused, so this migration does not modify them.

### Proven test seams

`Logger` already has test implementations. `SharedPtrManager` and `Scripts`
can now also be resolved from isolated test containers while production
callers continue receiving their normal default shared instances.

## SharedPtrManager migration

PR #117 changed `SharedPtrManager::getInstance()` from a function-local static
to:

```cpp
return inject<SharedPtrManager>();
```

Tests cover default-container identity, isolated test-container resolution,
normal `store()`/cleanup behavior and RAII restoration of the previous test
container.

## Scripts migration

`Scripts::getInstance()` now follows the same pattern:

```cpp
return inject<Scripts>();
```

The constructor is public so Boost.DI can construct the concrete service and a
test injector can create an isolated instance. This does not create a second
Lua runtime: every `LuaScriptInterface` still attaches to the process-wide
`LuaEnvironment`, while each interface owns a separate Lua registry reference
and releases only that reference in its destructor.

Tests are intentionally limited to identity and isolation. They do not load,
clear or register gameplay scripts and therefore do not mutate production Lua
registries.

## Remaining dependency work

There is no remaining broad accessor migration in the active workstream.
Constructor injection should be introduced only when a concrete consumer needs
one of these seams, for example:

- an instance-owned scheduler/event context;
- map-region cleanup tests;
- a module that currently cannot be tested without reaching a process-global
  service.

Each consumer migration must remain a small, behavior-preserving PR. The
`g_*()` accessor may stay as the production wiring adapter while constructors
receive explicit references in the code under test.

## Map and InstanceManager boundary

Do not move `Map` ownership pre-emptively. The instance roadmap should first
introduce a region/slot pool over physically separate map regions. Only if a
later phase proves that one `Game`-owned map cannot express the required
isolation should map ownership be reconsidered in a dedicated design PR.

## Explicit exclusions

- no global-accessor mega-refactor;
- no multiworld work;
- no new multi-channel phase;
- no `ClusterRuntime` migration;
- no behavior changes to gameplay, protocol, datapacks or persistence.
