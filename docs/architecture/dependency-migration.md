# Dependency migration: reducing global singleton coupling

## Starting point

The premise that Canary still needs a broad migration from raw `g_x()` Meyers
singletons to dependency injection is mostly outdated in this fork. The
repository already has a working `boost::di` container under `src/lib/di/`, and
most accessors follow this compatibility-preserving path:

```text
global function -> dependency accessor using inject<T>() -> constructor injection where useful
```

`ConfigManager`, `Database`, `Dispatcher`, `Game`, `Logger` and most other
shared services already resolve through `inject<T>()`. The default container
still returns one shared production instance, while tests can install an
isolated container with `DI::setTestContainer()`.

The useful remaining work is therefore:

1. migrate the few raw accessors that were missed;
2. use constructor injection only in modules where it provides concrete
   isolation or testability benefits;
3. defer map/world ownership changes until the instance subsystem actually
   needs them.

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
| `g_scripts` | `Scripts` | **raw Meyers** | process-global, real callers |
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
| `g_counterPointer` | `SharedPtrManager` | migrated by this change | easy to isolate |
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

`Logger` already has test implementations. After this migration,
`SharedPtrManager` can also be resolved from an isolated test container while
production callers continue receiving the same default shared instance.

## SharedPtrManager migration

`SharedPtrManager::getInstance()` previously returned a function-local static:

```cpp
static SharedPtrManager instance;
return instance;
```

It now uses the same accessor pattern as the rest of the engine:

```cpp
return inject<SharedPtrManager>();
```

No explicit binding is needed because it is a concrete default-constructible
class. The default container still provides one shared instance. Tests cover:

- default-container identity through both `getInstance()` and
  `g_counterPointer()`;
- isolation through a test-installed injector;
- normal `store()` and `countAllReferencesAndClean()` behavior using the
  default container, which includes the real logger binding;
- RAII restoration of the previous test container.

## Next migration

The next small PR should migrate `g_scripts()` / `Scripts`, the remaining
non-multichannel raw Meyers singleton with real callers.

Expected change:

```cpp
Scripts &Scripts::getInstance() {
    return inject<Scripts>();
}
```

Requirements:

- inventory all `g_scripts()` callers;
- keep production behavior unchanged;
- add a default-container identity test;
- add an isolated-container test where construction permits it;
- run the complete C++ build and runtime smoke matrix;
- do not combine this accessor migration with call-site constructor injection.

After that, constructor injection should be introduced one consumer/module at
a time only when needed by tests or the `InstanceManager` integration.

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
