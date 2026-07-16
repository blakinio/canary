# TSD-002A Engine Foundation Classification Report

> Task-start baseline: `blakinio/canary@6d368766cc47794ec0145b4b32613edaf7588adb`.
> This is registry/discovery evidence only. It does not prove runtime correctness, thread safety, Lua API safety, compiler portability or Oteryn readiness.

## Scope split

The original TSD-002 candidate set mixed stable engine infrastructure with active database and persistence work. TSD-002 is therefore split sequentially:

- **TSD-002A** — engine scheduling, dependency injection, Lua bindings and build contracts;
- **TSD-002B** — database connection, migrations, transaction boundaries, player/world persistence and save/restart/reload.

PR #308 actively changes schema, migrations and multichannel DB/runtime code. TSD-002A does not inspect those changes as merged evidence and does not modify persistence records.

## Candidate decisions

| Candidate | Decision | Reason | Registry action |
|---|---|---|---|
| `engine-scheduler` | `ADD_NOW` | Dispatcher/task/thread-pool scheduling has its own queueing, delay, cancellation, execution-group, context and shutdown lifecycle. | Add one conservative inventory record. |
| `engine-service-container` | `ADD_NOW` | The DI container owns construction, singleton scope, test-container substitution and legacy contextual injection as a durable cross-cutting contract. | Add one conservative inventory record limited to `src/lib/di/**`. |
| `lua-bindings` | `ADD_NOW` | `src/lua/functions/**` is a dedicated server-to-Lua registration and value/userdata conversion surface with a central loader and domain binding families. | Add one conservative inventory record. |
| `data-registries` | `MERGE_WITH_ANOTHER_MODULE` | Current loaders are separate vocation, outfit, familiar, imbuement, storage, item, NPC, event, module, script and monster domains. Startup order belongs to `engine-runtime-lifecycle`; each registry's behavior belongs to its functional module. | No standalone record. |
| `build-system` | `ADD_NOW` | CMake/vcpkg/presets/Visual Studio metadata form a stable configure, dependency, target, compiler-option and platform-build contract independently useful for discovery and validation. | Add one conservative inventory record. |
| `platform-compatibility` | `MERGE_WITH_ANOTHER_MODULE` | Current platform policy is expressed mainly through compiler/CPU/toolchain branches and maintained build entry points, not through an independently owned runtime subsystem. | Keep as a capability/evidence dimension inside `build-system`. |

## Evidence inventory

### `engine-scheduler`

Verified implementation roots:

```text
src/game/scheduling/dispatcher.*
src/game/scheduling/task.*
src/lib/thread/thread_pool.*
```

The dispatcher defines task groups, event types, delayed/cyclic scheduling, cancellation, async execution, queue merging, execution budgets, dispatcher context, queue latency and shutdown signaling. The task abstraction carries delayed/cyclic execution state. The thread pool provides the worker execution substrate.

Explicit exclusions:

- `src/game/scheduling/events_scheduler.*` — gameplay event-rate scheduling, not the generic engine scheduler;
- `src/game/scheduling/save_manager.*` — save/persistence orchestration deferred to TSD-002B;
- feature-specific timers and callbacks;
- claims of ordering, starvation freedom, race freedom or shutdown correctness.

### `engine-service-container`

Verified implementation root:

```text
src/lib/di/**
```

`DI` defines default bindings, singleton scope, test-container substitution, new-instance creation, shared-instance retrieval and the legacy `inject<T>()` compatibility helper.

Explicit exclusions:

- network `ServiceManager` and listening ports in `src/server/server.*`;
- feature-specific service classes;
- physical source-tree refactoring;
- claims that all legacy globals or soft singletons are migrated or safe.

### `lua-bindings`

Verified implementation and test roots:

```text
src/lua/functions/**
tests/unit/lua/*_functions_test.cpp
docs/lua-api/**
```

The functions tree has one central loader plus core, creature, event, item and map binding families. The public binding support covers registration, userdata traits, stack conversion, metatables, error handling and protected calls.

Explicit exclusions:

- shared Lua state and script-interface lifecycle already owned by `lua-runtime`;
- gameplay scripts and individual feature registrations;
- callbacks, script loading and reload safety outside the binding surface;
- claims that every binding is documented, type-safe or runtime-tested.

### `build-system`

Verified implementation/validation roots:

```text
CMakeLists.txt
CMakePresets.json
src/CMakeLists.txt
cmake/**
vcpkg.json
vcproj/canary.vcxproj
tests/CMakeLists.txt
.github/workflows/ci.yml
```

The build contract owns configure options, source/target composition, dependency/toolchain integration, compiler flags, test-build activation, platform-specific target metadata and the required CI build gate.

Explicit exclusions:

- deployment and production configuration;
- runtime operating-system behavior;
- container orchestration or release operations as independent domains;
- proof that every supported compiler/CPU/OS combination builds or runs correctly.

## Why `data-registries` is not a module

`CanaryServer::loadModules()` coordinates ordered loading, but the loaded state is not one registry with one lifecycle. It invokes independent domain systems, including weapon proficiencies, appearances, vocations, outfits, familiars, imbuements, storages, items, scripts, NPCs, events, modules and monsters.

A standalone `data-registries` record would duplicate many future functional modules, obscure ownership and turn a startup sequence into a false domain boundary. TSD-002A therefore records:

- ordering and startup failure behavior inside `engine-runtime-lifecycle`;
- Lua script/interface state inside `lua-runtime`;
- each feature registry inside its current or future functional module.

## Why `platform-compatibility` is not a module

The current evidence is primarily conditional CMake/compiler/CPU/platform configuration and maintained build-entry metadata. There is no separately owned platform state machine or stable implementation root independent from the build contract.

Platform portability, compiler coverage, architecture flags and Windows project parity remain findings/capabilities within `build-system`. A separate record may be reconsidered only if a durable runtime/platform abstraction and independent validation queue emerge.

## Relationships

- `engine-scheduler` interacts with `engine-runtime-lifecycle` and `engine-service-container`.
- `engine-service-container` interacts with `engine-runtime-lifecycle`, `configuration`, `engine-scheduler` and `lua-runtime`.
- `lua-bindings` depends on `lua-runtime` and interacts with `engine-service-container`.
- `build-system` interacts with `configuration`, `engine-runtime-lifecycle`, `engine-service-container`, `engine-scheduler`, `lua-bindings` and `lua-runtime`.

Only `lua-bindings → lua-runtime` is encoded as `depends_on`: the binding surface fundamentally requires the shared Lua runtime. Other edges are descriptive interactions and must not imply initialization order or runtime proof.

## Maturity baseline

All four records begin conservatively:

```text
lifecycle: inventory
implementation: inventory
evidence: inventory
persistence: not-assessed
protocol: not-assessed
automated_tests: not-assessed
runtime_validation: not-assessed
gameplay_e2e: not-assessed
```

Existing unit files and CI entry points are path inventory only. TSD-002A does not promote maturity because it does not audit complete behavior, coverage or runtime execution for these narrow contracts.

## Source-aware discovery expectations

For the configured `upstream-server` source:

- scheduler paths may map to `engine-scheduler` and broader correct records, but never through client-only buckets;
- DI paths map to `engine-service-container`;
- Lua function paths map to both `lua-bindings` and the broader `lua-runtime` umbrella;
- build paths map to `build-system` where an exact registered pattern exists;
- outputs remain deterministic and `triage_status` remains `needs-triage`.

## Safety and evidence limits

TSD-002A changes no runtime source. File and API presence do not prove:

- scheduler fairness, ordering, latency or race freedom;
- dependency graph correctness or singleton lifetime safety;
- Lua stack/userdata/object-lifetime safety;
- build portability across supported platforms;
- restart/reload safety;
- persistence or transaction correctness;
- Real Tibia parity;
- physical-client E2E;
- Oteryn readiness.

## Exact next package

After TSD-002A feature and lifecycle PRs are merged, create from then-current `main`:

```text
task: CAN-20260714-tibia-system-decomposition-persistence-transactions
package: TSD-002B
branch: docs/tibia-system-decomposition-persistence-transactions
```

Reclassify `database-connection`, `database-migrations`, `transaction-boundaries`, `world-persistence`, `database-reconciliation` and `save-restart-reload`, while preserving the existing `player-persistence` record until a narrower boundary is proven safe.
