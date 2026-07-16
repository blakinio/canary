# OAM-003 Engine Foundation Revalidation

Status: **evidence complete; target adaptation packages required**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-003`

Pinned task-start baselines:

```text
legacy/governance: blakinio/canary@c32e42469f302ab108dea08d9b90164458696328
target: blakinio/Otheryn@3cc7c1dfea747bb380f3761ee7ff7ac30141a115
upstream: opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689
donor/reference: zimbadev/crystalserver@fdd2b1f13f53894c584346ef3de43658045c42a7
```

This report is the durable evidence surface for the bounded OAM-003 foundation package. It does not authorize bulk legacy import, donor import, persistence migration or later domain migration.

# 1. Canonical modules and dispositions

| Module | Disposition | Immediate target action |
|---|---|---|
| `build-system` | `REUSE` | Keep the pinned upstream/target build foundation. Do not import legacy multichannel-only build dependencies. |
| `configuration` | `ADAPT` | Preserve upstream parsing/reload/deferred-load behavior, but move ownership/access toward the explicit Oteryn composition root and keep feature-specific legacy keys out of foundation migration. |
| `engine-runtime-lifecycle` | `ADAPT` | Preserve proven startup/shutdown semantics while removing legacy multichannel/distributed bootstrap from consideration and introducing explicit target lifecycle composition incrementally. |
| `engine-scheduler` | `REUSE` | Keep the pinned upstream lane/WDRR/barrier-parallel scheduler and its policy/tests. Reject legacy/Crystal `TaskGroup` scheduler replacement. |
| `engine-service-container` | `ADAPT` | Reuse existing Boost.DI primitives and bindings, but stop expanding contextual/global access; move new target-owned construction to explicit composition-root ownership. |
| `lua-runtime` | `ADAPT` | Reuse the current Lua runtime implementation and ownership fixes, but make lifecycle/reload ownership explicit; current `reInitState()` still has unresolved child-interface reload semantics. |
| `lua-bindings` | `ADAPT` | Reuse typed shared-userdata helpers and current binding infrastructure, but migrate domain-facing binding families toward explicit Oteryn adapter/use-case boundaries as their domains move. |

No module is approved for wholesale legacy or donor import.

# 2. Architecture invariants evaluated

- one authoritative server process/world/channel;
- application/bootstrap is the composition root;
- explicit lifecycle ownership and startup/shutdown ordering;
- scheduler/dispatcher is the controlled mutation boundary, not arbitrary worker mutation;
- service composition is explicit and must not add hidden globals/singletons;
- Lua is an adapter/extension surface and cannot bypass domain invariants;
- no speculative instance/multichannel/distributed abstractions in the initial core;
- no repository-wide path rewrite merely to match the target layout.

# 3. Evidence matrix

| Module | Target/upstream baseline | Legacy / donor evidence | Runtime/test evidence | Disposition rationale |
|---|---|---|---|---|
| `build-system` | Target is pinned upstream content. OAM-002 target bootstrap passed the required target CI before merge. | Legacy build files diverge; `BaseConfig.cmake` adds `hiredis` only under `FEATURE_MULTICHANNEL_REDIS`, a capability explicitly excluded from initial Oteryn. No donor evidence provides a superior target build contract. | OAM-002 target bootstrap and cleanup PRs passed exact-head target CI; final target differs from upstream only in two CI/governance paths. | `REUSE`: upstream-native build is already the validated target baseline. Legacy build deltas are feature/fork baggage unless re-proven by a later bounded package. |
| `configuration` | Upstream `ConfigManager` uses `std::atomic_bool loaded`, acquire/release visibility and `deferUntilLoaded()` guarded by a mutex; reload clears caches then calls `load()`. | Legacy uses a plain `bool loaded` in the pinned file and adds fork-specific configuration including disconnect protection and multichannel-related surfaces elsewhere. Crystal also uses plain `bool loaded`. | Target startup/runtime smoke necessarily loads `config.lua`; exact target source equals upstream. No dedicated concurrent reload proof was found. | `ADAPT`: retain upstream config implementation as the base because it is stronger than legacy/donor, but explicit ownership/access and reload contract need target architecture convergence. |
| `engine-runtime-lifecycle` | Upstream `CanaryServer` initializes dispatcher, config, DB, modules/maps, `MonsterComputeService`, game/service manager and shuts down compute service, DB backup, dispatcher, metrics and thread pool in explicit order. | Legacy `CanaryServer` injects multichannel channel/cluster/handoff/Redis/leadership bootstrap into the top-level lifecycle. Those responsibilities are explicitly excluded from initial Oteryn. | OAM-002 target CI exercised target startup/runtime smoke. Static evidence shows ordered startup/shutdown, but the current root still relies on many `g_*` accessors rather than the target composition-root model. | `ADAPT`: preserve proven upstream lifecycle behavior, reject legacy distributed bootstrap, and incrementally introduce explicit target composition/lifecycle ownership. |
| `engine-scheduler` | Upstream/target uses lane-based dispatcher policy, WDRR, barrier-parallel execution, background completion, admission/fairness/budget/telemetry helpers and `MonsterComputeService`. | Legacy pinned `dispatcher.hpp` uses the older `TaskGroup` model. Crystal donor also uses an older `TaskGroup` model. Neither is a stronger foundation candidate. | Upstream contains focused `dispatcher_wdrr_test.cpp` and `dispatcher_policy_test.cpp` covering lane weights, aging, FIFO/requeue, producer fairness, admission capacity, coalescing, lane semantics and telemetry. Target bootstrap CI passed runtime/build gates. Shutdown orders compute service before dispatcher/thread pool. | `REUSE`: keep upstream scheduler implementation. Composition ownership may change under lifecycle adaptation, but scheduler internals should not be replaced by legacy/donor code. |
| `engine-service-container` | Target/upstream `src/lib/di/container.hpp`, `runtime_provider.hpp`, `shared.hpp` are identical to legacy at the pinned SHAs. Existing tests include DI test-container and soft-singleton behavior. | Crystal uses substantially the same static `defaultContainer`/contextual `inject<T>()` pattern and does not provide a more explicit composition model. | Unit tests exercise test-container substitution and soft-singleton warnings. Static `defaultContainer`, `testContainer` and contextual `inject<T>()` remain global access points. | `ADAPT`: reuse Boost.DI implementation/primitives and current bindings, but new Oteryn code must use explicit constructor/composition ownership and must not grow the global contextual access pattern. |
| `lua-runtime` | Target/upstream and legacy `LuaEnvironment` are identical at the pinned source blob. It owns one shared Lua state, timer refs, area objects and shutdown flag; `closeState()` unreferences timer entries and closes the Lua state. | No better legacy implementation exists. Crystal does not provide evidence that supersedes the upstream runtime. | Target runtime smoke loads Lua scripts. However `LuaEnvironment::reInitState()` still has `TODO` for child reload and the runtime uses lazy/global access plus a static shutdown flag. | `ADAPT`: reuse runtime behavior and cleanup logic, but explicit lifecycle ownership and complete reload semantics remain required before calling the module architecture-complete. |
| `lua-bindings` | Target/upstream and legacy `lua_functions_loader.hpp` are identical and include typed `LuaUserdataTraits`, `registerSharedClass<T>`, `pushSharedUserdata<T>` and borrowed-shared helpers. The shared-userdata ownership contract is also identical. | Crystal's loader lacks the typed shared-userdata trait layer visible in the pinned upstream/target version, so it is not a stronger donor for binding ownership. | Existing Lua binding unit/doc infrastructure and target Lua/runtime CI are reusable. The ownership guide records fixed high-risk KV/Condition/NetworkMessage patterns and warns that polymorphic core userdata still requires separate audit. | `ADAPT`: preserve typed ownership helpers and loader infrastructure. Do not bulk-rewrite bindings; adapt each domain-facing binding family when its target domain/use-case boundary is migrated and audit polymorphic userdata separately. |

# 4. Boundary classification

| Boundary | State | Evidence / decision |
|---|---|---|
| ownership/lifecycle | applicable | `engine-runtime-lifecycle`, DI, config and Lua require explicit target ownership adaptation. |
| build/toolchain | applicable | `build-system` is reusable upstream-native; target CI already validates it. |
| configuration | applicable | upstream config base retained; ownership/access adaptation required. |
| service/API | applicable | DI primitives retained; contextual/global access cannot expand. Lua bindings become target adapters. |
| scheduling/concurrency | applicable | upstream lane/WDRR scheduler retained; legacy/donor TaskGroup models rejected. |
| persistence | not-applicable for OAM-003 implementation | OAM-004 owns DB/persistence foundation; lifecycle may call DB but this package does not alter persistence semantics. |
| protocol/session | not-applicable | no OAM-003 protocol/client contract change is required by the proven dispositions. |
| identifiers/assets | not-applicable | no identifier/asset migration. |
| world/map | not-applicable | no world-content migration. |
| runtime | applicable | startup/shutdown and Lua runtime evidence used; adaptation remains for explicit lifecycle/reload ownership. |
| tests | applicable | scheduler unit tests and target bootstrap/runtime CI reused; adaptation packages require their own focused current-head tests. |
| physical-client E2E | not-applicable | no user-visible/session/protocol behavior change in the revalidation package. |
| operations | applicable, bounded | preserve safe startup/shutdown and build gates; no production deployment change. |
| security/privacy | applicable to Lua lifetime safety | typed shared-userdata contract retained; polymorphic userdata remains a bounded audit concern. |

# 5. Source-role conclusions

## Upstream / target

`opentibiabr/canary@a879c931...` is the strongest starting foundation for all seven modules. Otheryn already contains this foundation at `3cc7c1df...` except the two proven target CI/governance files outside runtime code.

## Legacy `blakinio/canary`

Legacy is evidence-only. Repository history is `726` commits ahead and `3` behind the pinned upstream with merge base `e8237cef...`; it is not a monotonic successor.

Foundation-specific conclusions:

- scheduler: older than target/upstream at the pinned SHA;
- configuration: older load-state synchronization plus fork-specific keys;
- lifecycle: contaminated by multichannel/cluster/Redis/handoff startup responsibilities excluded from initial Oteryn;
- DI core: materially identical, so there is nothing unique to migrate;
- Lua runtime/shared-userdata foundation: materially identical, so there is nothing unique to migrate;
- build: contains fork-specific multichannel dependency/configuration deltas and must not be imported wholesale.

## Crystal donor

Pinned donor: `zimbadev/crystalserver@fdd2b1f13f53894c584346ef3de43658045c42a7`.

Crystal is comparison-only and not behavioral authority.

Observed foundation conclusions:

- dispatcher uses the older `TaskGroup` model rather than upstream target lanes/WDRR;
- config uses plain `bool loaded` rather than upstream atomic/deferred-load behavior;
- DI remains the same general static/contextual pattern and offers no cleaner composition root;
- Lua loader lacks the typed shared-userdata trait layer visible in upstream/target.

No OAM-003 module receives a donor-driven migration disposition.

# 6. Reuse and rejection decisions

## Reuse directly

```text
build-system: pinned upstream/target build foundation
engine-scheduler: pinned upstream lane/WDRR scheduler implementation and tests
```

## Reuse as implementation substrate, but adapt architecture

```text
configuration: parser/cache/reload/deferred-load implementation
engine-runtime-lifecycle: upstream startup/shutdown semantics
engine-service-container: Boost.DI primitives and existing bindings
lua-runtime: shared state/timer cleanup and Lua state management
lua-bindings: typed shared-userdata helpers and binding loader infrastructure
```

## Explicitly reject from initial target migration

```text
legacy multichannel cluster bootstrap
legacy Redis/handoff/session-leadership foundation
legacy TaskGroup scheduler replacement
Crystal TaskGroup scheduler replacement
Crystal/plain-bool config lifecycle as a target baseline
bulk legacy CMake/vcpkg dependency import
bulk donor Lua binding import
```

# 7. Required target adaptation packages

The `ADAPT` outcomes are too broad for one target code PR. They are split before target source changes:

## OAM-003A — composition root, lifecycle, DI and config ownership

Scope:

```text
configuration
engine-runtime-lifecycle
engine-service-container
```

Goal:

- establish one explicit target-owned composition/lifecycle seam without repository-wide path rewrite;
- keep existing upstream startup/shutdown behavior functioning;
- stop adding new target responsibilities through contextual `g_*`/`inject<T>()` access;
- keep configuration parsing/reload behavior while moving target-owned consumers toward explicit dependencies;
- do not introduce instances, multichannel, Redis, distributed ownership or persistence redesign.

## OAM-003B — Lua runtime and binding adapter boundary

Scope:

```text
lua-runtime
lua-bindings
```

Goal:

- make Lua runtime lifecycle/reload ownership explicit enough for Oteryn;
- retain typed shared-userdata helpers;
- define the adapter rule for domain-facing bindings;
- audit only the polymorphic/shared-userdata paths touched by the package;
- do not bulk-rewrite all existing Lua bindings.

Dependency:

```text
OAM-003B depends on the explicit ownership seam established by OAM-003A.
```

`build-system` and `engine-scheduler` require no OAM-003 target source migration package unless later evidence changes the pinned baseline.

# 8. Runtime and validation evidence

PROVEN:

- OAM-002 target bootstrap PR passed exact-head target CI before merge; final target runtime source is unchanged from the pinned upstream tree.
- Upstream scheduler has focused WDRR/policy tests for fairness, queue semantics, execution-mode/lane mapping, admission and telemetry.
- Upstream `CanaryServer::shutdown()` stops monster compute before dispatcher/thread-pool shutdown.
- Upstream target startup initializes configuration, DB, modules/maps, compute service and game/service manager in a visible order.
- Lua environment cleanup unreferences timer registry entries and closes the shared state.
- Shared Lua userdata ownership rules and typed helpers are present at the target baseline.

NOT PROVEN / intentionally deferred:

- concurrent configuration reload correctness under arbitrary consumers;
- architecture-complete removal of global/contextual service access;
- complete Lua child-interface reload semantics;
- safety of every polymorphic Lua userdata family;
- domain-invariant compliance of every existing feature binding.

These unresolved points justify `ADAPT`, not `REUSE`, for the affected canonical modules.

# 9. Decision summary

```text
build-system             REUSE
configuration            ADAPT
engine-runtime-lifecycle ADAPT
engine-scheduler         REUSE
engine-service-container ADAPT
lua-runtime              ADAPT
lua-bindings             ADAPT
```

No canonical module remains `REVALIDATE` inside the bounded OAM-003 evidence result. This does not globally promote unrelated modules or authorize OAM-004.

OAM-003 is not complete until the required target adaptation work is represented by explicitly linked bounded target tasks/PRs and the program queue records their dependency before OAM-004.
