# OAM-003 Engine Foundation Revalidation

Status: **in progress**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-003`

Pinned task-start baselines:

```text
legacy/governance: blakinio/canary@c32e42469f302ab108dea08d9b90164458696328
target: blakinio/Otheryn@3cc7c1dfea747bb380f3761ee7ff7ac30141a115
upstream: opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689
```

This report is the durable evidence surface for the bounded OAM-003 foundation package. It does not authorize bulk legacy import or later persistence/domain migration.

## Canonical modules

```text
build-system
configuration
engine-runtime-lifecycle
engine-scheduler
engine-service-container
lua-runtime
lua-bindings
```

All dispositions remain `REVALIDATE` until the evidence matrix below is completed.

## Architecture invariants under test

- one authoritative server process/world/channel;
- application/bootstrap is the composition root;
- explicit lifecycle ownership and startup/shutdown ordering;
- scheduler/dispatcher is the controlled mutation boundary, not arbitrary worker mutation;
- service composition is explicit and must not add hidden globals/singletons;
- Lua is an adapter/extension surface and cannot bypass domain invariants;
- no speculative instance/multichannel/distributed abstractions in the initial core;
- no repository-wide path rewrite merely to match the target layout.

## Evidence matrix

| Module | Target/upstream baseline | Legacy delta | Key boundaries | Runtime/test evidence | Disposition | Rationale |
|---|---|---|---|---|---|---|
| `build-system` | pending refresh | pending | build/toolchain, platform | pending | `REVALIDATE` | Inventory only. |
| `configuration` | pending refresh | pending | configuration, lifecycle | pending | `REVALIDATE` | Inventory only. |
| `engine-runtime-lifecycle` | pending refresh | pending | ownership/lifecycle, runtime | pending | `REVALIDATE` | Runtime proof required. |
| `engine-scheduler` | pending refresh | pending | scheduling/concurrency, runtime | pending | `REVALIDATE` | Ordering/shutdown proof required. |
| `engine-service-container` | pending refresh | pending | ownership/lifecycle, service API | pending | `REVALIDATE` | Lifetime safety must be proven. |
| `lua-runtime` | pending refresh | pending | lifecycle, scripting, runtime | pending | `REVALIDATE` | Reload/shutdown safety unresolved. |
| `lua-bindings` | pending refresh | pending | scripting API, userdata lifetime | pending | `REVALIDATE` | Binding presence/docs do not prove runtime safety. |

## Package boundary classification

| Boundary | State | Evidence |
|---|---|---|
| ownership/lifecycle | applicable | lifecycle, DI and Lua runtime modules |
| build/toolchain | applicable | build-system |
| configuration | applicable | configuration |
| service/API | applicable | DI container and Lua bindings |
| scheduling/concurrency | applicable | engine-scheduler and authoritative runtime mutation path |
| persistence | not-applicable for implementation in OAM-003; interactions deferred | OAM-004 owns persistence foundation |
| protocol/session | not-applicable unless new evidence appears | no current OAM-003 protocol/client delta |
| identifiers/assets | not-applicable | no IDs/assets in scope |
| world/map | not-applicable | no world-content migration |
| runtime | applicable | lifecycle/scheduler/Lua |
| tests | applicable | build/unit/runtime evidence required |
| physical-client E2E | not-applicable unless a user-visible/session behavior change is introduced | no such target change authorized yet |
| operations | applicable only to startup/shutdown/build gates | no production deployment |
| security/privacy | applicable to Lua userdata/lifetime safety; otherwise bounded | known shared-userdata risk |

## Current findings

### PROVEN

- Otheryn foundation source begins OAM-003 from the pinned upstream content baseline, except two target-only CI/governance files outside these seven runtime modules.
- Legacy Canary has diverged substantially from the pinned upstream history and cannot be treated as a monotonic successor.
- Existing reusable DI access exists under `src/lib/di/**`; a second service-container abstraction is not justified by inventory alone.
- The architecture blueprint explicitly requires app/bootstrap composition, explicit lifecycle owners and revalidation of scheduler implementation during OAM-003.

### UNKNOWN

- Exact semantic value of each legacy foundation delta.
- Runtime correctness of startup/shutdown and scheduler cancellation/ordering at the target baseline.
- Lua runtime reload/shutdown and userdata lifetime safety across all relevant binding families.

## Next evidence step

Refresh `TSD_002A_ENGINE_FOUNDATION_REPORT.md` findings against the exact pinned task-start SHAs, then replace each `pending` matrix cell with path/symbol/test/runtime evidence and an evidence-backed disposition.
