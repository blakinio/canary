# OAM-003 Engine Foundation Revalidation

Status: **evidence and bounded target adaptation complete; governance merge pending**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-003`

Pinned evidence baselines:

```text
legacy/governance task-start: blakinio/canary@c32e42469f302ab108dea08d9b90164458696328
target task-start: blakinio/Otheryn@3cc7c1dfea747bb380f3761ee7ff7ac30141a115
upstream: opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689
donor/reference: zimbadev/crystalserver@fdd2b1f13f53894c584346ef3de43658045c42a7
OAM-003A target merge: blakinio/Otheryn@9b5805aaeef50774e9db5225c05529a06cec507e
OAM-003B final target merge: blakinio/Otheryn@a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d
```

This report is the durable evidence surface for the bounded OAM-003 foundation package. It does not authorize bulk legacy import, donor import, persistence migration or later domain migration.

# 1. Canonical modules and final OAM-003 dispositions

| Module | Disposition | OAM-003 result |
|---|---|---|
| `build-system` | `REUSE` | Keep the pinned upstream/target build foundation. Do not import legacy multichannel-only build dependencies. |
| `configuration` | `ADAPT` | Preserve upstream parsing/reload/deferred-load behavior. OAM-003A establishes the first explicit composition seam; broader consumer-by-consumer dependency migration remains incremental. |
| `engine-runtime-lifecycle` | `ADAPT` | Preserve upstream startup/shutdown semantics, reject legacy multichannel/distributed bootstrap, and use the explicit composition seam introduced by OAM-003A. |
| `engine-scheduler` | `REUSE` | Keep the pinned upstream lane/WDRR/barrier-parallel scheduler and its policy/tests. Reject legacy/Crystal `TaskGroup` replacement. |
| `engine-service-container` | `ADAPT` | Reuse Boost.DI primitives, but new target-owned root construction must be explicit. OAM-003A begins that convergence without replacing the container. |
| `lua-runtime` | `ADAPT` | OAM-003B adds an explicit idempotent root-runtime shutdown/reload boundary while preserving the existing runtime implementation. Child-interface reconstruction remains unresolved. |
| `lua-bindings` | `ADAPT` | Preserve typed shared-userdata helpers and loader infrastructure. OAM-003B changes no domain/feature binding implementation and records the rule for future touched binding families. |

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

| Module | Target/upstream evidence | Legacy / donor evidence | Runtime/test evidence | Disposition rationale |
|---|---|---|---|---|
| `build-system` | Target started from pinned upstream content and retained the upstream build foundation through OAM-003. | Legacy build adds `hiredis` under `FEATURE_MULTICHANNEL_REDIS`, a capability excluded from initial Oteryn. No donor provides a stronger build contract. | OAM-002 bootstrap and both OAM-003 target PRs passed target build/runtime gates. | `REUSE`: upstream-native build remains the validated target base. |
| `configuration` | Upstream uses atomic load state and mutex-protected deferred callbacks; reload clears caches then calls `load()`. | Legacy and Crystal use a weaker plain-`bool loaded` model; legacy also carries fork-specific surfaces. | Target startup/runtime smoke loads configuration. No arbitrary-consumer concurrent reload proof was established. | `ADAPT`: keep implementation base, converge ownership/access incrementally. |
| `engine-runtime-lifecycle` | Upstream startup/shutdown ordering is explicit and target runtime smoke passes. | Legacy injects multichannel cluster/Redis/handoff/leadership bootstrap explicitly excluded from initial Oteryn. | OAM-003A full exact-head CI/Required passed before merge. | `ADAPT`: preserve behavior and introduce explicit composition seams incrementally. |
| `engine-scheduler` | Target/upstream uses lane/WDRR/barrier-parallel scheduling and `MonsterComputeService`. | Legacy and Crystal use older `TaskGroup` models. | Focused dispatcher WDRR/policy tests exist; target full build/runtime gates pass. | `REUSE`: no foundation replacement justified. |
| `engine-service-container` | Boost.DI primitives are already present and shared with legacy. | Crystal retains the same general static/contextual pattern and is not a cleaner donor. | OAM-003A proves explicit top-level `CanaryServer` construction can coexist with current DI. | `ADAPT`: retain container substrate, stop expanding contextual root construction. |
| `lua-runtime` | Target/upstream/legacy runtime base is materially identical and owns one shared state, timers and area objects. | No stronger legacy/donor runtime was found. | OAM-003B full exact-head CI, runtime smoke and `Required` passed. Root shutdown/reload ownership is explicit after OAM-003B. | `ADAPT`: bounded root lifecycle seam delivered; child-interface reload remains unresolved. |
| `lua-bindings` | Target/upstream contains typed `LuaUserdataTraits`, shared/borrowed shared-userdata helpers and documented ownership rules. | Crystal lacks the same typed ownership layer. | OAM-003B changed no domain/feature binding file; Lua tests and Lua API checks passed. | `ADAPT`: preserve typed infrastructure; future domain binding changes require explicit ownership-mode evidence. |

# 4. Boundary classification

| Boundary | State | Evidence / decision |
|---|---|---|
| ownership/lifecycle | applicable | OAM-003A and OAM-003B establish bounded explicit root seams; broader global/contextual access remains incremental work. |
| build/toolchain | applicable | `build-system` is reusable upstream-native and validated by target CI. |
| configuration | applicable | upstream config base retained; explicit consumer ownership remains incremental. |
| service/API | applicable | DI primitives retained; contextual/global access cannot expand. |
| scheduling/concurrency | applicable | upstream lane/WDRR scheduler retained; legacy/donor replacements rejected. |
| persistence | not-applicable for OAM-003 implementation | OAM-004 owns DB/persistence foundation. |
| protocol/session | not-applicable | no protocol/client contract change. |
| identifiers/assets | not-applicable | no identifier/asset migration. |
| world/map | not-applicable | no world-content migration. |
| runtime | applicable | exact-head target build/runtime smoke used for both adaptation slices. |
| tests | applicable | scheduler tests plus target CI/runtime smoke reused; OAM-003A/B each passed their exact-head gates. |
| physical-client E2E | not-applicable | no user-visible/session/protocol behavior change. |
| operations | applicable, bounded | startup/shutdown and root Lua lifecycle remain fail-safe; no deployment change. |
| security/privacy | applicable to Lua lifetime safety | typed shared-userdata contract retained; untouched polymorphic userdata remains outside this package. |

# 5. Source-role conclusions

## Upstream / target

`opentibiabr/canary@a879c931...` was the strongest starting foundation for all seven modules. OAM-003 retained its build/scheduler foundation and introduced only bounded target architecture seams.

## Legacy `blakinio/canary`

Legacy is evidence-only. At task start its history was `726` commits ahead and `3` behind the pinned upstream with merge base `e8237cef...`; it is not a monotonic successor.

Foundation conclusions:

- scheduler: older than target/upstream at the pinned SHA;
- configuration: weaker load-state synchronization plus fork-specific keys;
- lifecycle: contains multichannel/cluster/Redis/handoff responsibilities excluded from initial Oteryn;
- DI core: materially identical, with no unique foundation to migrate;
- Lua runtime/shared-userdata foundation: materially identical, with no unique foundation to migrate;
- build: contains fork-specific multichannel dependency/configuration deltas and must not be imported wholesale.

## Crystal donor

Pinned donor: `zimbadev/crystalserver@fdd2b1f13f53894c584346ef3de43658045c42a7`.

Crystal is comparison-only and not behavioral authority.

Observed conclusions:

- dispatcher uses an older `TaskGroup` model;
- config uses plain `bool loaded` rather than upstream atomic/deferred-load behavior;
- DI retains the same general static/contextual pattern;
- Lua loader lacks the typed shared-userdata trait layer visible in target/upstream.

No OAM-003 module receives a donor-driven migration disposition.

# 6. Reuse and rejection decisions

## Reuse directly

```text
build-system: pinned upstream/target build foundation
engine-scheduler: pinned upstream lane/WDRR scheduler implementation and tests
```

## Reuse as implementation substrate, with bounded adaptation

```text
configuration: parser/cache/reload/deferred-load implementation
engine-runtime-lifecycle: upstream startup/shutdown semantics
engine-service-container: Boost.DI primitives and existing bindings
lua-runtime: shared state/timer cleanup and Lua state management
lua-bindings: typed shared-userdata helpers and loader infrastructure
```

## Explicitly reject from initial target migration

```text
legacy multichannel cluster bootstrap
legacy Redis/handoff/session-leadership foundation
legacy TaskGroup scheduler replacement
Crystal TaskGroup scheduler replacement
Crystal/plain-bool config lifecycle as target baseline
bulk legacy CMake/vcpkg dependency import
bulk donor Lua binding import
```

# 7. Delivered target adaptation packages

## OAM-003A — composition root, lifecycle, DI and config ownership seam

Target PR: `blakinio/Otheryn#4`

Task-start target: `3cc7c1dfea747bb380f3761ee7ff7ac30141a115`

Merged target: `9b5805aaeef50774e9db5225c05529a06cec507e`

Delivered:

- `main()` resolves existing root dependencies and explicitly constructs `CanaryServer`;
- no second DI container or repository-wide refactor;
- scheduler, persistence, protocol and runtime behavior remain unchanged;
- full ready-cycle target CI, runtime smoke and `Required` passed on exact PR head before squash merge.

This is the first explicit composition seam, not a claim that all existing `g_*`/`inject<T>()` access has been removed.

## OAM-003B — Lua runtime lifecycle and binding boundary

Target issue: `blakinio/Otheryn#5` — completed.

Target PR: `blakinio/Otheryn#6`

Task-start target: `9b5805aaeef50774e9db5225c05529a06cec507e`

Merged target: `a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d`

Delivered:

- idempotent `LuaEnvironment::shutdown()` root-runtime boundary;
- root runtime refuses `initState()`, `reInitState()` and `reloadCore()` resurrection after shutdown begins;
- `LuaEnvironment::reloadCore()` centralizes root `core.lua` reload;
- composition root explicitly closes the root Lua runtime after normal server/doc-generation execution;
- SIGHUP and `GameReload::reloadCore()` use the same root-runtime reload API;
- no domain/feature binding implementation changed;
- typed shared-userdata ownership helpers remain unchanged;
- full exact-head CI #21, `Required` #18 and autofix passed on `49e9e4960d89476016c50d81523715b7551c1bf9` before squash merge;
- no comments, submitted reviews or unresolved review threads were present before merge.

Explicitly unresolved:

- `LuaEnvironment::reInitState()` child-interface reconstruction TODO;
- broader child `LuaScriptInterface` lifecycle/reload;
- safety audit of untouched polymorphic userdata families;
- domain-invariant review of untouched feature bindings.

Those gaps remain bounded future evidence requirements and are not silently promoted to `REUSE`.

# 8. Runtime and validation evidence

PROVEN:

- OAM-002 established the clean target baseline before OAM-003.
- OAM-003A target PR #4 passed full exact-head target CI and `Required` before merge.
- OAM-003B target PR #6 passed full exact-head target CI #21, including Fast Checks, Lua Tests, Linux debug/release, Windows, macOS, Docker and runtime smoke, plus `Required` #18 before merge.
- Upstream scheduler has focused WDRR/policy tests.
- Target startup/runtime smoke exercises configuration and Lua loading.
- Shared Lua userdata ownership rules and typed helpers remain present and unchanged.

NOT PROVEN / intentionally deferred:

- concurrent configuration reload correctness under arbitrary consumers;
- architecture-complete removal of global/contextual service access;
- complete Lua child-interface reload semantics;
- safety of every untouched polymorphic Lua userdata family;
- domain-invariant compliance of every untouched feature binding.

These unresolved points do not invalidate the delivered seams; they define future bounded evidence requirements.

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

All seven OAM-003 modules now have explicit evidence-backed dispositions. This result does not globally promote unrelated canonical modules and does not itself authorize OAM-004 implementation.

# 10. OAM-003 completion gate

Target implementation chain is complete:

```text
OAM-003A -> merged as 9b5805aaeef50774e9db5225c05529a06cec507e
OAM-003B -> merged as a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d
```

The remaining OAM-003 work is governance-only:

1. merge Canary PR #411 after exact-current-head ownership, CI and review gates;
2. archive the OAM-003 task through a separate lifecycle-only PR;
3. only after lifecycle completion may OAM-004 become the next eligible bounded task, with fresh live target/upstream baselines and ownership checks.
