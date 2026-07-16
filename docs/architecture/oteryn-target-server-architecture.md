# Oteryn Target Server Architecture

Status: **concrete design blueprint; implementation remains blocked by OAM-002 target identity gate**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Governing contract: `docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md`

This document defines the intended architecture of the first Oteryn server baseline. It is a target design, not an implementation claim. It does not create an Oteryn repository, choose a target SHA, authorize code migration or change Canary runtime behavior.

The canonical module inventory remains exclusively:

```text
docs/agents/real-tibia/registry/modules/*.yaml
```

This blueprint defines where responsibilities should live and how they may depend on each other. It is not a second module registry.

## 1. Design inputs and source roles

Observed while this blueprint was created:

```text
legacy laboratory: blakinio/canary@55f3e4126604ae26fbf09c04c90b96f330bd741d
upstream reference: opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689
comparison donor: zimbadev/crystalserver@fdd2b1f13f53894c584346ef3de43658045c42a7
```

These are design-time observations only. They are not the future OAM-002 target baseline.

Repository roles are fixed:

| Source | Role in architecture work | What it may prove | What it may not prove |
|---|---|---|---|
| `opentibiabr/canary` | upstream ancestry and default bootstrap candidate | current upstream structure, APIs, fixes and implementation direction | that every upstream behavior is correct for Oteryn or Real Tibia |
| `blakinio/canary` | legacy laboratory and migration-source candidate | local fixes, experiments, tests, tools and feature implementations | that fork-specific code belongs in Oteryn |
| `zimbadev/crystalserver` | read-only donor/comparison source | alternative implementations and candidate fixes | official behavior, superiority or migration authorization |
| official/independent Real Tibia evidence | question-specific behavior evidence | behavior appropriate to the evidence dimension | source-code architecture or Canary-specific implementation details |

Oteryn starts from a clean, exact then-current upstream Canary baseline after OAM-002 pins it. Legacy and donor code are evaluated selectively.

## 2. First-version product posture

The first Oteryn server is intentionally a **modular monolith**.

```text
one game-server process
+ one authoritative world runtime
+ one logical game-state authority
+ one channel
+ explicit modules and adapters
+ external database
+ explicit client/protocol contracts
```

This is not a microservice architecture and not a clustered game-world architecture.

The goal is to make ownership, lifecycle and dependency direction explicit while retaining the operational simplicity and performance characteristics appropriate to a C++ MMORPG server.

### 2.1 Explicitly deferred from initial Oteryn

The initial Oteryn core does **not** include:

- world instances / instanced gameplay runtime;
- multi-channel or multi-process world partitioning;
- Redis-backed channel coordination;
- cross-channel session leases/fencing;
- cross-process record handoff;
- channel switching;
- distributed world ownership.

The canonical `instances` module remains in the 62-module registry with migration posture `REVALIDATE`, but it is excluded from the initial implementation and migration waves. No stronger migration disposition is assigned by this blueprint.

Fork-specific `src/game/multichannel/**` work is acknowledged as future experimental evidence. It does not receive a new canonical module merely because the code exists, and it is not part of initial Oteryn bootstrap or core architecture.

Future instance or multichannel work must be a separately authorized architecture task after the single-world/single-channel Oteryn core is proven. The initial core must not introduce speculative abstractions solely to accommodate those future features.

## 3. Top-level architecture

```text
                         +----------------------+
                         |      Oteryn App      |
                         | composition/startup  |
                         +----------+-----------+
                                    |
             +----------------------+----------------------+
             |                      |                      |
             v                      v                      v
      +-------------+        +-------------+        +-------------+
      |   Engine    |        |  Protocol   |        |  Scripting  |
      | lifecycle   |        | adapters    |        | adapters    |
      | scheduler   |        | login/game  |        | Lua runtime |
      | services    |        | profiles    |        | bindings    |
      +------+------+        +------+------+        +------+------+
             |                      |                      |
             +----------------------+----------------------+
                                    |
                                    v
                         +----------------------+
                         |     Game Domain      |
                         | world/items/combat   |
                         | character/economy    |
                         | creatures/social     |
                         +----------+-----------+
                                    |
                         ports / explicit APIs
                                    |
                                    v
                         +----------------------+
                         |      Platform        |
                         | DB/persistence/net   |
                         | security/serialization|
                         +----------------------+
```

The diagram is dependency-oriented, not a process diagram. Network I/O and database work may execute asynchronously, but authoritative game-state mutation must enter the controlled game runtime boundary rather than mutate world state from arbitrary worker contexts.

## 4. Dependency rules

### 4.1 Domain does not depend on transport or storage formats

Game/domain code must not require knowledge of:

- packet byte layouts;
- socket connection objects;
- MariaDB result objects;
- SQL row layouts;
- Lua stack indexes;
- protobuf wire details unrelated to domain-owned serialization;
- OTClient UI structures.

Protocol, persistence and Lua bindings adapt external representations into domain-facing commands, queries and values.

### 4.2 Protocol depends inward

Protocol handlers may call stable game/application service APIs. Domain modules must not call protocol serializers or construct network packets directly as their primary business interface.

Where legacy behavior currently mixes game mutation and packet emission, migration must identify and separate the authoritative state transition from its client projection before claiming `REUSE`.

### 4.3 Persistence uses owned ports

A module that owns durable state owns the persistence contract for that state. Concrete MariaDB code belongs in the platform/persistence adapter side, not scattered through unrelated domain code.

A persistence port may live next to the owning domain module when that makes ownership explicit. The concrete database adapter implements it under the platform layer.

Transaction boundaries are defined by the use case that requires atomicity. The existence of a generic transaction helper never proves that a business operation is atomic.

### 4.4 Scripting is an adapter and extension surface

Lua may orchestrate gameplay and content behavior through explicit bindings, but it must not bypass authoritative invariants such as:

- item ownership and transfer validation;
- economy mutation rules;
- authentication/authorization;
- persistence transaction boundaries;
- protocol compatibility gates;
- world-position legality;
- sanctions or security enforcement.

C++ owns invariants that must remain authoritative regardless of script behavior. Lua owns high-level content and gameplay orchestration where the required capability is safely exposed.

### 4.5 App/bootstrap is the composition root

Construction and startup wiring belong at the application boundary. New global `g_*` ownership and hidden Meyers singletons are forbidden unless a later explicit architecture decision proves they are required.

The service container/DI layer composes concrete dependencies. Domain modules should receive dependencies explicitly instead of discovering them through unrelated globals.

### 4.6 Tools never become runtime dependencies accidentally

OTBM analyzers, Upstream Intelligence, agent tooling, validators and E2E orchestration live outside the game runtime dependency graph. Production code must not depend on audit artifacts or agent-only tooling.

## 5. Process and runtime architecture

### 5.1 Process model

Initial Oteryn runs one authoritative game-server process for one world/channel.

External dependencies may include:

- MariaDB;
- the maintained login/web-service boundary where selected by the exact upstream baseline;
- observability/export destinations;
- the maintained game client.

Those are integrations, not reasons to split the game domain into microservices.

### 5.2 Runtime ownership

The target runtime separates:

```text
process lifecycle
configuration
service composition
scheduler/dispatcher
network I/O
protocol decoding/encoding
game command execution
domain state
persistence
Lua runtime
content loading
observability
```

One class such as legacy `Game` may temporarily remain a compatibility facade during migration, but it must not be treated as justification for adding every new responsibility to one god object.

New Oteryn-owned responsibilities should have one explicit lifecycle owner and one narrow public surface.

### 5.3 Authoritative mutation path

The intended request flow is:

```text
socket input
→ transport validation/decryption/decompression
→ protocol decode
→ authenticated/session context
→ game command/application service
→ authoritative domain mutation
→ persistence/event side effects where required
→ domain result/projection
→ protocol encode
→ socket output
```

Worker threads may perform bounded computation or I/O where safe. They may not mutate shared world state directly without passing through the runtime's explicit synchronization/dispatch contract.

The exact scheduler implementation is revalidated during OAM-003 against then-current upstream Canary. This blueprint does not select legacy-fork scheduler code over newer upstream scheduling work merely because one version exists locally.

### 5.4 Startup sequence

Target startup order:

1. parse and validate configuration;
2. initialize logging/observability required for startup diagnostics;
3. create the service container/composition root;
4. establish database connectivity;
5. validate/apply the explicitly approved schema-migration lifecycle;
6. load static definitions required by dependent systems;
7. initialize Lua runtime and binding surfaces;
8. load the selected world and world-content roots;
9. initialize domain services and scheduled work;
10. open login/status/game listeners only after required dependencies are ready.

A failed required stage stops startup cleanly. Partial startup must not silently expose a listener for a world that is not ready.

### 5.5 Shutdown sequence

Target shutdown reverses ownership safely:

1. stop accepting new game/login work;
2. prevent creation of new sessions;
3. quiesce or reject new game commands;
4. complete or explicitly cancel bounded in-flight work;
5. execute approved player/world persistence steps;
6. stop scheduled work;
7. unload scripting/content only after dependents stop using it;
8. close database/network resources;
9. destroy services in explicit ownership order.

Crash recovery and restart correctness require separate persistence evidence; an orderly shutdown path does not prove crash consistency.

## 6. Concrete target repository layout

The intended **destination layout** is:

```text
oteryn/
├── CMakeLists.txt
├── CMakePresets.json
├── vcpkg.json
├── cmake/
├── src/
│   ├── app/
│   │   ├── main.cpp
│   │   ├── oteryn_server.*
│   │   └── bootstrap/
│   ├── engine/
│   │   ├── runtime/
│   │   ├── scheduling/
│   │   ├── services/
│   │   └── config/
│   ├── platform/
│   │   ├── database/
│   │   ├── persistence/
│   │   ├── network/
│   │   ├── security/
│   │   ├── serialization/
│   │   └── observability/
│   ├── protocol/
│   │   ├── transport/
│   │   ├── login/
│   │   ├── game/
│   │   ├── compatibility/
│   │   └── session/
│   ├── scripting/
│   │   ├── runtime/
│   │   ├── bindings/
│   │   └── support/
│   └── game/
│       ├── account/
│       ├── character/
│       ├── progression/
│       ├── world/
│       ├── items/
│       ├── economy/
│       ├── combat/
│       ├── creatures/
│       ├── social/
│       └── systems/
├── data/
│   ├── definitions/
│   ├── scripts/
│   │   ├── actions/
│   │   ├── movements/
│   │   ├── events/
│   │   ├── npcs/
│   │   ├── quests/
│   │   ├── spells/
│   │   ├── weapons/
│   │   └── systems/
│   ├── world/
│   │   ├── maps/
│   │   ├── spawns/
│   │   ├── houses/
│   │   └── zones/
│   └── migrations/
├── schema/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   ├── runtime/
│   └── e2e/
├── tools/
└── docs/
```

This is a convergence target, not permission for a bulk rename/move.

### 6.1 Bootstrap transition rule

OAM-002 must bootstrap from a pinned upstream Canary revision. Therefore inherited upstream paths may exist initially.

No package may perform a repository-wide tree rewrite merely to make the checkout visually match this blueprint.

Instead:

1. untouched upstream code may temporarily retain its inherited path;
2. when a canonical module is revalidated, the package names its target ownership root;
3. code is moved only when the move is necessary for that bounded module/package and the build/tests remain reviewable;
4. new Oteryn-owned code follows the target layout;
5. compatibility shims are removed after their last proven consumer is migrated;
6. empty speculative folder scaffolding is not created.

The destination architecture is mandatory for ownership direction; immediate physical relocation of all legacy files is not.

## 7. Folder and file ownership rules

### 7.1 Avoid generic dumping grounds

New target code should not accumulate unrelated responsibilities under generic roots such as:

```text
utils/
helpers/
functions/
managers/
misc/
```

A narrowly scoped helper is placed with its owning module. Truly cross-cutting infrastructure requires an explicit stable responsibility before it enters `engine/` or `platform/`.

### 7.2 One primary owner per implementation file

A file should normally have one primary module/architecture owner. Multiple canonical modules may still reference or interact with the same path in discovery metadata; that does not authorize shared edit ownership.

When one legacy file contains several module responsibilities, migration should expose stable APIs and extract responsibilities incrementally instead of copying the monolith and declaring all modules `REUSE`.

### 7.3 Public surfaces are explicit

A module with callers outside its ownership root should expose a narrow public surface. Depending on module size this may be:

```text
api/
ports/
services/
```

Do not create all three directories mechanically. Use the minimum structure that makes ownership and dependency direction clear.

Private implementation details must not become cross-module dependencies merely because a header is reachable.

## 8. Mapping canonical modules to architecture zones

The 62 canonical registry records remain the only module list. The mapping below defines **architecture zones**, not duplicate module identities.

| Architecture zone | Canonical responsibilities that normally belong here | Typical target root |
|---|---|---|
| engine foundation | build, configuration, process lifecycle, scheduler, service composition | `src/engine/**`, build roots |
| persistence infrastructure | database connection, migrations, player/world persistence adapters | `src/platform/database/**`, `src/platform/persistence/**`, `schema/**`, `data/migrations/**` |
| account/character/social | account/authentication, character lifecycle, chat, parties, guilds, sanctions | `src/game/account/**`, `character/**`, `social/**` |
| progression | progression, vocations, achievements, Bestiary/Bosstiary/Cyclopedia, Prey, Wheel, titles/proficiency | `src/game/progression/**`, bounded `systems/**` |
| items/economy | item definitions/instances, containers, decay, market, imbuements, Forge | `src/game/items/**`, `src/game/economy/**` |
| combat | combat engine, conditions, spells, weapons | `src/game/combat/**` |
| creatures/world | creature definitions/AI, world runtime, zones, NPCs, spawns, raids, houses, quests | `src/game/creatures/**`, `src/game/world/**`, `data/**` |
| client/protocol | transport, login, compatibility, session handoff, game protocol | `src/platform/network/**`, `src/protocol/**` |
| scripting | Lua runtime and bindings; script-facing adapters | `src/scripting/**`, `data/scripts/**` |
| engineering platforms | OTBM tooling, E2E, upstream intelligence, deployment and analytics tooling where non-runtime | `tools/**`, `tests/e2e/**`, workflows/docs |

A canonical module may touch more than one technical layer. Example: `houses` spans world runtime, persistence and protocol projection. The module still has one functional owner; persistence/protocol pieces are adapters to that owner rather than separate duplicate house modules.

## 9. Module architecture contract

Every migrated canonical module must identify:

```text
module_id
primary target ownership root
public API / commands / queries
owned state
lifecycle owner
required dependencies
interactions
persistence port and adapter, if applicable
protocol adapter, if applicable
Lua binding/script surface, if applicable
content/data roots, if applicable
configuration keys, if applicable
focused tests
integration/runtime proof
physical-client E2E, if applicable
migration disposition and provenance
```

A canonical module is a logical ownership and migration unit. It does not have to compile into one C++ library and it is not a runtime plugin by default.

Oteryn must not introduce a generic dynamic module/plugin framework solely because the inventory uses the word "module".

## 10. Game/domain architecture

### 10.1 Account and authentication

Account identity, authentication and character ownership are separate responsibilities from protocol framing.

Target direction:

```text
protocol login request
→ authentication service
→ account repository/authentication ports
→ authenticated account/session result
→ login protocol response
```

Password/session-token policy belongs to authentication/security boundaries. Character-list packet layout belongs to protocol.

### 10.2 Character lifecycle

Character load, online initialization, gameplay ownership, logout and save are one explicit lifecycle crossing domain and persistence adapters.

`Player` may remain a large compatibility type during bootstrap, but migration packages should not add unrelated responsibilities to it. New bounded components should have explicit ownership and persistence/protocol adapters.

### 10.3 Progression

Level/skills/vocations and larger progression systems remain separate canonical responsibilities where the registry already distinguishes them.

Progression mutations must use domain-owned APIs so protocol handlers, Lua scripts and persistence code do not each implement their own formula or unlock rule.

### 10.4 Items and economy

The target preserves these distinct concepts:

```text
item definitions
!= runtime item instances
!= containers/cylinders
!= decay lifecycle
!= economy transactions
```

Transfers and economy mutations must validate ownership and invariants before mutation. Durable economy operations define explicit transaction/idempotency expectations where applicable.

### 10.5 Combat

Combat is an authoritative domain pipeline. Conditions, spells and weapons remain separable canonical responsibilities but interact through explicit combat APIs.

Protocol and visual effects project combat results; they do not own damage/healing legality or state mutation.

### 10.6 Creatures

Creature definition loading is separate from runtime creature AI/state. Spawn placement is separate from creature definitions. Boss encounter reward logic is separate from generic creature AI.

This separation follows the existing canonical decomposition and prevents one monster file path from implicitly owning AI, spawn, reward and protocol behavior.

### 10.7 World runtime

Initial world runtime owns:

- static map load/materialization;
- tiles and spatial lookup;
- movement/placement legality;
- spectators/visibility queries;
- pathfinding as a world-runtime capability;
- zones;
- towns/waypoints as embedded world registries where applicable;
- houses through their canonical domain boundary;
- normal-world NPC/creature/spawn integration.

It does **not** own an instance manager or distributed channel ownership in the first Oteryn version.

Offline OTBM analysis remains tooling and never becomes the runtime map owner.

## 11. Persistence architecture

Persistence is divided into explicit responsibilities:

```text
database connection / query primitives
schema migration lifecycle
player persistence
world persistence
module-owned repositories/adapters
```

Rules:

1. Domain state ownership is not inferred from table location.
2. SQL access from a module must be through an owned persistence boundary or an explicitly justified narrow adapter.
3. Player save and world save remain separate lifecycles.
4. A global save does not imply cross-domain atomicity.
5. Each critical mutation documents transaction scope, retry semantics and idempotency expectations.
6. Schema migrations are versioned, reviewable and validated independently of runtime startup success.
7. Rollback/recovery expectations are explicit; a migration is not called reversible without proof.
8. Database connection retry does not authorize retrying a non-idempotent business transaction.

The initial architecture is designed for one authoritative game process, so no distributed ownership/fencing or cross-channel command inbox is required.

## 12. Network and protocol architecture

The target separates five protocol concerns:

```text
transport
login protocol
game protocol
compatibility/profile registry
session handoff/context
```

### Transport

Owns connection lifecycle, framing, checksum/sequence, crypto and compression mechanics.

### Login

Owns login request/response wire semantics and character/world-list projection. Credential policy remains authentication-owned.

### Game protocol

Owns opcode decode/encode and client projection. It calls domain APIs instead of owning gameplay rules.

### Compatibility

Owns version/profile/capability decisions and exact server-client compatibility gates.

### Session context

Carries the minimum proven context required between login and game connections. It is not a second account/session database.

Any protocol change coupled to maintained OTClient requires exact server/client revisions, byte/field contracts, supported combination matrix and rollout policy.

## 13. Lua and content architecture

### 13.1 Lua runtime

The Lua runtime owns:

- VM/state lifecycle;
- script interfaces;
- loading and approved reload behavior;
- callback registration infrastructure;
- protected execution/error boundaries;
- userdata lifetime policy.

### 13.2 Lua bindings

Bindings translate Lua calls to stable C++ capabilities. They do not own the gameplay domain they expose.

Shared C++ object ownership must use safe typed userdata/lifetime patterns. Raw-pointer or manual shared-pointer ownership shortcuts are not target architecture.

### 13.3 Script responsibilities

Lua is appropriate for bounded high-level behavior such as:

- quests and actions;
- NPC conversations;
- content event orchestration;
- spells/weapons when the authoritative engine invariants remain enforced;
- raids and scripted encounters;
- configuration-driven content systems.

Lua must not become a bypass around authoritative C++ safety or persistence rules.

### 13.4 Content roots

The long-term target is one unambiguous active content layout under `data/**` rather than accidental mixing of multiple active datapacks.

A migration package may retain inherited upstream data roots temporarily. When a content area is migrated, the package must declare the authoritative target path and prevent duplicate active registration.

Do not bulk-copy or mass-merge `data/**`, `data-canary/**` and `data-otservbr-global/**` merely to normalize paths.

## 14. World, OTBM and assets

Runtime world loading and offline world evidence are separate.

Offline architecture reuses the existing stack for:

- canonical World Index;
- item/mechanic audit;
- AID/UID;
- teleports;
- houses/doors;
- script resolution;
- reachability;
- spawn/NPC evidence;
- storage graph;
- Semantic OTBM Diff;
- geometry/consistency analysis;
- factual rendering.

Map/content migration requires bounded evidence and exact asset/item compatibility. No whole-map donor replacement or blind donor region import follows from this architecture.

## 15. Test architecture

Target test layers are:

```text
unit
→ module/component integration
→ persistence/protocol contract
→ controlled runtime
→ physical-client E2E where applicable
```

### Unit

Pure rules, state transitions, parsers and bounded components.

### Integration

Real interactions between module boundaries and concrete adapters where appropriate.

### Contract

Byte-exact protocol fixtures, persistence/schema expectations, serialization and cross-repository contracts.

### Runtime

Controlled server process evidence for lifecycle, scheduling, load/save and failure behavior.

### Physical-client E2E

The existing Universal Physical-Client E2E platform is reused for real user-visible/session/protocol proof. A module adds scenarios/assertions, not a second orchestrator.

Compilation and legacy CI never substitute for target-side module evidence.

## 16. Build architecture

Initial bootstrap inherits the exact upstream Canary build system pinned by OAM-002.

Target direction:

- keep CMake/vcpkg/presets as the authoritative portable build contract unless OAM-003 evidence selects otherwise;
- one server executable with testable core targets/libraries where useful;
- each new/relocated C++ source is registered in all maintained build entry points;
- target layering should be reflected by CMake targets only when doing so improves ownership/testability without creating circular libraries;
- no repository-wide library split is required before the first module migration.

The current upstream's scheduler/build changes and the legacy fork's additional runtime code must be re-evaluated at OAM-003 rather than choosing whichever tree is larger.

## 17. Observability and operations

Observability is an adapter concern and must not own gameplay truth.

Metrics/logs may observe:

- process lifecycle;
- scheduler queues/latency;
- network/session health;
- DB latency/failures;
- persistence outcomes;
- bounded gameplay metrics.

Metrics must not directly mutate gameplay.

Deployment remains a separate operational lifecycle with staging, manifests, atomic switch and rollback evidence where applicable. Initial Oteryn architecture does not assume Kubernetes, multichannel clustering or distributed world processes.

## 18. Three-way module evaluation

Every Oteryn module package evaluates the relevant boundary using at least:

```text
then-current pinned upstream Canary
vs
pinned legacy blakinio/canary
vs
pinned CrystalServer when relevant
+
question-specific Real Tibia evidence when parity is claimed
```

This is semantic comparison, not a three-way text merge.

For each relevant behavior/API/path:

| Finding | Interpretation | Default action |
|---|---|---|
| upstream contains the needed current implementation and no contrary evidence exists | target-ancestry candidate | inherit through target baseline, still revalidate module contract |
| legacy fork adds behavior absent upstream | local candidate | prove value, target compatibility and tests before `REUSE`/`ADAPT` |
| Crystal adds behavior absent both | donor candidate | investigate independently; never auto-import |
| upstream is newer/cleaner than legacy | legacy baggage candidate | prefer upstream direction unless evidence requires adaptation |
| legacy and Crystal independently solve the same defect differently | corroborated defect candidate, not equivalent patches | reproduce defect and select/design the safest target fix |
| all three differ | unresolved architecture/behavior decision | keep `REVALIDATE` until evidence closes the conflict |
| donor behavior conflicts with official/current evidence | donor rejected or deferred | do not migrate |

A package records exact SHAs and the role of every compared source.

## 19. Migration disposition under this architecture

A source comparison is evaluated against this target architecture before disposition:

### REUSE

Only when the implementation already fits target ownership, lifecycle, dependencies, persistence/protocol contracts and tests with minimal structural change.

### ADAPT

Preferred when behavior is valuable but code is coupled to legacy globals, monolithic ownership, direct DB/protocol access or a different target path/API.

### REWRITE

Used when the responsibility belongs in Oteryn but the implementation violates target boundaries sufficiently that transferring it would preserve baggage.

### DO_NOT_MIGRATE

Used when the responsibility is outside the target product or superseded and no required consumer remains.

### EXPERIMENTAL_ONLY

Used for optional laboratory features that should not enter initial core.

### REVALIDATE

Remains the default until a bounded package proves one of the above.

This blueprint itself changes no canonical module disposition.

## 20. Initial migration sequence

After OAM-002 resolves the target repository and baseline, the architecture sequence remains:

```text
OAM-003  engine/build/runtime foundation
OAM-004  database/persistence foundation
OAM-005  account/character lifecycle
OAM-006  network/login/protocol
OAM-007  item/world runtime foundation
OAM-008  first evidence-selected low-risk module
OAM-009  physical-client E2E proof
OAM-010+ dependency-ordered domain packages
```

For initial Oteryn:

- `instances` is skipped/deferred when world-runtime packages are evaluated;
- fork-specific `multichannel` code is skipped/deferred entirely;
- neither may block delivery of the single-world/single-channel core;
- neither may be copied as hidden dependency of another package;
- any shared helper originating in those areas may migrate only if it has an independently proven core consumer and no future-feature coupling.

## 21. Architecture acceptance gate for each module

Before implementation of a canonical module begins, answer:

1. What is its target ownership root?
2. What state does it own?
3. Who creates and destroys it?
4. What is its public API?
5. Which canonical dependencies are required?
6. Which concrete legacy dependencies are forbidden in target?
7. Does it need persistence? Which port/adapter owns it?
8. Does it affect protocol/client compatibility?
9. Does it expose Lua capabilities or own scripts/content?
10. What configuration does it own?
11. What unit/integration/runtime evidence is required?
12. Is physical-client E2E applicable?
13. What do upstream Canary, legacy Canary and relevant donors each contribute?
14. What exact migration disposition is supported?
15. What is the rollback/provenance plan?

Any applicable unresolved boundary blocks `REUSE`.

## 22. Initial-core invariants

The first Oteryn core preserves these non-negotiable architecture invariants:

1. clean pinned upstream bootstrap, never legacy-fork cloning;
2. modular monolith before distributed complexity;
3. one world and one channel initially;
4. explicit lifecycle ownership;
5. no new hidden global ownership;
6. authoritative game mutation through controlled runtime boundaries;
7. domain independent of packet and SQL representation;
8. explicit persistence ownership and transaction scope;
9. protocol compatibility versioned and cross-repository when coupled;
10. Lua as controlled extension surface, not invariant bypass;
11. one canonical module registry only;
12. existing OTBM, E2E and Upstream Intelligence platforms reused;
13. no bulk source-tree, datapack, map or donor import;
14. exact SHA provenance for every migration decision;
15. unresolved evidence remains unresolved.

## 23. Current blockers

This architecture is now concrete enough to guide target packages, but implementation remains blocked until OAM-002 can record:

```text
Oteryn target repository
Oteryn default branch
Oteryn target task-start SHA
Oteryn write authorization
exact then-current opentibiabr/canary bootstrap SHA
target ancestry/bootstrap relationship
```

Until those are resolved, this document is architecture/governance evidence only.
