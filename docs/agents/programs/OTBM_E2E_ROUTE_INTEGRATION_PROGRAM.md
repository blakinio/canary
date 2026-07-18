---
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
name: OTBM-aware Universal Physical E2E routing
status: active
owner: unassigned
created: 2026-07-18T23:05:00+02:00
updated: 2026-07-18T23:05:00+02:00
coordination_id: OTBM-E2E-ROUTE-V1
primary_paths:
  - tools/ai-agent/otbm_reachability*
  - docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md
  - docs/ai-agent/OTBM_*ROUTE*
  - docs/ai-agent/OTBM_*LANDMARK*
  - tools/e2e/run_agent_e2e.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tests/e2e/**
related_programs:
  - CAN-PROGRAM-OTBM
  - CAN-PROGRAM-E2E-PLATFORM
cross_repo_contracts:
  - OTS-E2E-CANARY-OTCLIENT
---

# Mission

Connect the completed static OTBM evidence stack to the existing Universal Physical E2E lifecycle so an agent can express a route intent such as:

```text
thais.temple -> thais.depot
```

and obtain a deterministic, evidence-backed physical execution pipeline:

```text
semantic landmark request
  -> exact evidence-backed coordinates and bounded routing region
  -> existing OTBM World Index
  -> existing Reachability graph/BFS
  -> edge-aware executable route plan
  -> exact-map static route preflight
  -> existing Universal Physical E2E
  -> controlled real OTClient follows the planned positions and interactions
  -> runtime evidence and exact failure classification
```

The programme does not create another OTBM parser, World Index, pathfinder, E2E orchestrator or physical-client lifecycle.

# Problem being solved

Current physical gameplay scenarios can execute bounded directional `walk` actions, but a route is still normally authored as manual direction/count sequences. That is sufficient for a small fixed proof but is not a reliable navigation interface for an autonomous agent.

The target state is that physical movement is driven by the exact OTBM map snapshot and existing static evidence:

- ordinary movement follows walkable tiles rather than guessed direction counts;
- static blockers are avoided;
- doors and other conditional barriers are crossed only when an evidence-backed supported interaction exists;
- teleports are taken as explicit transition edges with exact destinations;
- stairs, ladders, holes, rope and other floor changes use reviewed transition evidence rather than sprite/name guesses;
- every physical move is synchronized against the exact expected player position;
- stale map/index/landmark/interaction evidence fails closed before an expensive physical run.

# Confirmed foundations to reuse

## Unified OTBM World Index

Canonical map evidence layer. Reuse it for:

- exact tile `x,y,z` positions;
- complete item placements and stack order evidence;
- item IDs;
- AID;
- UID;
- house-door IDs;
- teleport source/destination evidence;
- deterministic provenance and map/index identity.

Do not rescan OTBM with a new parser.

## OTBM Reachability

Canonical routing graph/pathfinding layer. It already:

- joins World Index tiles with appearance semantics;
- classifies strict and optimistic walkability;
- builds cardinal and optional diagonal movement edges;
- prevents diagonal corner cutting;
- builds teleport and reviewed floor-transition edges;
- runs BFS;
- stores `previous[position] = (parent, transition_id)`;
- reconstructs ordered coordinate paths.

This programme extends the existing graph/export boundary. It must not implement an independent A*, BFS or other pathfinder beside Reachability.

## OTBM Script Resolution

Canonical static runtime-handler correlation layer. Reuse it to gate route interactions involving AID/UID/item/position handlers. Preserve `unresolved`, `partially-resolved`, `referenced-only` and `conflicting` states. Never promote unresolved evidence to handled.

## Reviewed transition manifest

Canonical evidence for non-teleport cross-floor transitions. Reuse stable transition IDs, sources, destinations/deltas, expected item IDs and uncertainty tags. Do not infer floor offsets from sprite appearance, item name or memory.

## Universal OTS E2E

Canonical physical lifecycle. Reuse:

- disposable MariaDB/bootstrap fixtures;
- exact Canary build/artifact;
- runtime-selected datapack and exact map;
- controlled pinned `blakinio/otclient`;
- client assets;
- physical login;
- first-session gameplay actions;
- safe logout;
- persistence sentinel;
- relog;
- second safe logout;
- logs, screenshots, records and machine-readable evidence;
- existing workflow and Required gate.

Do not create a second physical runner or workflow.

# Architecture boundary

The programme introduces only bridge contracts and bounded extensions:

1. **Route request** — exact coordinates or semantic landmark IDs.
2. **Semantic Landmark Registry** — maps reviewed names to exact map anchors and routing regions.
3. **Reachability executable route export** — reuses the existing BFS/predecessor graph and emits ordered edge-aware route evidence.
4. **Route Interaction Registry** — maps reviewed map/transition evidence to physical activation semantics such as `use-map-item`.
5. **Static Route Preflight** — revalidates all route-plan provenance and executable steps against the exact runtime map/index.
6. **Universal `follow_route` action** — existing controlled OTClient executes the plan one expected state transition at a time.

Detailed contracts are in `docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md`.

# Delivery rules

Every work package below is a separate task/branch/PR unless an implementation agent proves a smaller dependency-safe grouping is necessary. Do not mix OTBM reusable interfaces and E2E platform reusable interfaces into one broad PR.

Each task must:

- start from current live `main`;
- read root `AGENTS.md`, repository map, context routing, this programme and the technical integration document;
- inspect live open PR/task ownership before claiming paths;
- publish an active task record and draft PR early;
- update catalogue/changelog only when its reusable public interface is actually delivered;
- apply `ci:final-gate` before the final checkpoint commit;
- pass exact-final-head required checks before merge;
- use squash merge and lifecycle archive;
- never commit `.otbm`, `.widx`, `items.otb`, client assets or generated route reports.

# Ordered implementation programme

## OTBM-E2E-001 — Reachability executable route export

**Goal:** expose an executable edge-aware route from the existing Reachability BFS/predecessor graph without creating another pathfinder.

### Required reuse

- `tools/ai-agent/otbm_reachability_graph.py::_bfs`
- existing predecessor map `(parent, transition_id)`
- existing tile classification
- existing transition validation
- existing World Index reader

### Deliverables

- versioned `canary-otbm-e2e-route-plan-v1` schema/contract;
- a bounded route-plan export entrypoint implemented as an extension of the current Reachability module/tooling;
- exact ordered path positions;
- edge-level distinction between same-floor movement and transition edges;
- stable transition evidence copied from the already validated Reachability transition state;
- full-path requirement for executable output: an executable plan must never use a head/tail truncated route;
- deterministic output and provenance hashes;
- focused unit tests proving the exported route is derived from the same BFS/predecessor graph as the current report.

### Required behavior

- `confirmed` strict routes may become executable when every required transition has physical activation semantics that are already unambiguous or explicitly supplied;
- `conditional` geometry remains non-executable until every conditional barrier on the selected candidate path is resolved by the later interaction layer;
- `unreachable` and `invalid` remain non-executable;
- transition ID must be attached to the exact edge where it is used, not only emitted as a separate unordered/flattened summary;
- if an executable full route exceeds the supported bound, fail closed rather than publishing a truncated executable plan.

### Suggested owned paths

```text
tools/ai-agent/otbm_reachability*.py
docs/ai-agent/OTBM_E2E_ROUTE_PLAN.schema.json
docs/ai-agent/OTBM_E2E_ROUTE_PLAN.md
tools/ai-agent/test_otbm_reachability*.py
```

Verify live ownership before claiming these paths.

### Acceptance gate

A fixture with movement plus at least one transition must prove that:

```text
existing Reachability status/distance
== route-plan routing decision
```

and every exported edge is traceable to either `_movement_neighbors` or a validated existing transition edge.

### Depends on

- merged planning programme PR.

### Blocks

- E2E-ROUTE-001;
- OTBM-E2E-004;
- OTBM-E2E-005.

---

## OTBM-E2E-002 — Semantic Landmark Registry

**Goal:** resolve reviewed semantic IDs such as `thais.temple` and `thais.depot` to exact evidence-backed route anchors and bounded routing regions.

### Deliverables

- `canary-otbm-semantic-landmarks-v1` schema;
- deterministic validator/resolver;
- explicit routing regions with inclusive 3D bounds;
- landmarks with one or more role-specific anchors;
- map/index evidence pins or equivalent stale-evidence detection;
- no automatic guessing from sprites, item names, minimap labels or chat history.

### Minimum registry model

```text
region id
  -> inclusive bounds

landmark id
  -> region id
  -> anchors[]
       id
       role
       exact x,y,z
       evidence
```

Recommended anchor roles:

- `route-origin`;
- `route-destination`;
- `entrance`;
- `exit`;
- `interaction`.

### v1 scope

- same-region landmark routing is required;
- cross-region automatic region graph routing is not required;
- a caller may still provide explicit coordinates and explicit region bounds without landmarks.

### Suggested owned paths

```text
docs/ai-agent/OTBM_SEMANTIC_LANDMARKS.schema.json
docs/ai-agent/OTBM_SEMANTIC_LANDMARKS.json
tools/ai-agent/otbm_semantic_landmarks.py
tools/ai-agent/test_otbm_semantic_landmarks.py
```

### Acceptance gate

Resolve two test landmarks deterministically, reject duplicate IDs, out-of-bounds anchors, stale map/index evidence and an anchor outside its declared routing region.

### Depends on

- merged planning programme PR.

### Can run in parallel with

- OTBM-E2E-001, when exclusive paths do not overlap.

### Blocks

- OTBM-E2E-004;
- OTBM-E2E-005.

---

## OTBM-E2E-003 — Route interaction semantics

**Goal:** define the evidence-backed bridge from conditional map/transition evidence to supported physical client activation semantics.

### Why separate from landmarks

Landmarks answer **where** a place is. Interaction semantics answer **how** a reviewed mechanic is physically activated. They must remain separate contracts.

### Required activation kinds

Initial v1 vocabulary:

```text
step-on
walk-direction
use-map-item
use-inventory-on-map
```

Possible evidence selectors:

- stable reviewed transition ID;
- exact position + item ID;
- exact position + AID/UID;
- exact position + house-door evidence.

Avoid using World Index placement ordinal as the only long-lived selector because it is pinned to a specific index build; it may be retained as additional exact-plan provenance.

### Deliverables

- `canary-otbm-route-interactions-v1` schema;
- deterministic validator/resolver;
- explicit physical activation semantics;
- integration rules with Script Resolution;
- fail-closed handling for unresolved/conflicting handlers;
- no claim that a successful static resolution proves runtime gameplay state.

### Suggested owned paths

```text
docs/ai-agent/OTBM_ROUTE_INTERACTIONS.schema.json
docs/ai-agent/OTBM_ROUTE_INTERACTIONS.json
tools/ai-agent/otbm_route_interactions.py
tools/ai-agent/test_otbm_route_interactions.py
```

### Acceptance gate

- engine teleport can resolve to `step-on` when validated by existing teleport evidence;
- a reviewed ladder transition can resolve to `use-map-item` only with explicit interaction evidence;
- unresolved/conflicting script evidence cannot become executable;
- an unknown door/barrier cannot be silently treated as open or usable.

### Depends on

- merged planning programme PR;
- contract alignment with OTBM-E2E-001.

### Can run in parallel with

- OTBM-E2E-002.

### Blocks

- executable-interaction routing mode;
- E2E-ROUTE-001 full interaction support;
- OTBM-E2E-004;
- OTBM-E2E-005.

---

## OTBM-E2E-001B — Executable interaction-aware routing mode

**Goal:** allow the same existing Reachability BFS to traverse only conditional barriers that have explicit supported interaction semantics, without treating all optimistic/unknown tiles as executable.

This is a follow-up to route export after the interaction contract is stable. It may be folded into OTBM-E2E-001 only if ownership and dependency timing make that smaller and safer.

### Required rule

Do not use plain optimistic walkability as physical executability.

The executable tile/edge predicate must be equivalent to:

```text
strictly walkable
OR
conditional barrier whose exact crossing interaction is resolved and supported
```

Unknown appearances, unresolved quest state, unresolved dynamic scripts or unsupported interactions remain blocked.

Reuse the existing `_bfs()` graph traversal by injecting/deriving the executable predicate/edges. Do not create a parallel pathfinder.

### Acceptance gate

Provide a fixture where:

- strict route is unavailable;
- optimistic route exists through both an unknown barrier and a known reviewed door;
- executable routing selects a valid route only when all selected conditional crossings are explicitly resolved;
- removing interaction evidence makes the route non-executable.

### Depends on

- OTBM-E2E-001;
- OTBM-E2E-003.

### Blocks

- robust door/use routing in OTBM-E2E-005.

---

## E2E-ROUTE-001 — Universal `follow_route` execution

**Goal:** extend the existing Universal Physical E2E action layer with one reusable route-plan execution capability.

### Required reuse

- existing `run_agent_e2e.py` scenario validation/materialization;
- existing `agent_e2e_scenario.lua` controlled-client driver;
- existing MariaDB/Canary/OTClient physical lifecycle;
- existing evidence marker model;
- existing safe logout/persistence/relog sentinel.

### Required generic capabilities

1. `follow_route` action consuming a validated generated route-plan artifact owned by the canonical runner lifecycle, not an arbitrary manifest filesystem path;
2. exact-position synchronization for every movement edge or bounded movement chunk;
3. `use-map-item` physical activation;
4. `use-inventory-on-map` physical activation when the maintained OTClient API can be verified;
5. exact transition source/destination assertions;
6. bounded timeouts and first-failure diagnostics;
7. deterministic route step markers in the existing evidence stream.

### Execution rule

For movement edge `P0 -> P1`:

```text
assert current position == P0
send exactly one derived movement request
wait until current position == P1 or timeout/failure
only then execute next edge
```

Do not convert a long route back into blind `north x 19` style timing-only movement.

### Maintained OTClient boundary

Before coding `use-map-item` or `use-inventory-on-map`, verify the exact APIs available in the pinned maintained `blakinio/otclient` revision. If a required generic client API is missing, create a separately coordinated cross-repository task; do not invent an API in the Canary task.

### Suggested owned paths

```text
tools/e2e/run_agent_e2e.py
tools/e2e/client/agent_e2e_scenario.lua
tests/e2e/test_agent_e2e_scenario_plan.py
docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
```

Workflow/physical-runner changes require separate live ownership review because those are shared integration paths.

### Acceptance gate

A deterministic fixture route must prove:

- exact position checked before and after each movement edge;
- divergence fails at the first mismatched expected coordinate;
- transition destination mismatch fails with expected/actual positions;
- unsupported interaction kind fails before client execution;
- existing non-route scenarios remain backward compatible;
- login/logout/relog sentinel remains unchanged.

### Depends on

- OTBM-E2E-001 route-plan contract;
- OTBM-E2E-003 for generic interaction vocabulary.

### Blocks

- OTBM-E2E-005.

---

## OTBM-E2E-004 — Exact-map static route preflight

**Goal:** fail cheaply before expensive Canary + OTClient execution when a route plan is stale, incomplete or not physically executable under the reviewed v1 contract.

### Preflight inputs

As applicable:

- exact runtime OTBM SHA-256;
- World Index and manifest;
- appearances evidence;
- Script Resolution report;
- reviewed transition manifest;
- Semantic Landmark Registry;
- Route Interaction Registry;
- generated route plan.

### Mandatory checks

- route-plan format/version supported;
- runtime map hash matches route provenance;
- World Index hash matches route provenance;
- start and goal exist;
- start/goal match resolved landmark anchors when landmarks were requested;
- every walk edge is adjacent and uses an allowed movement rule;
- diagonal edge obeys no-corner-cutting rules when enabled;
- every referenced tile still exists and has the expected classification;
- every transition still has exact matching source/destination;
- every required expected item/mechanic selector still matches;
- Script Resolution has not become conflicting/unresolved where execution requires a handler;
- every physical activation is supported by the current Universal E2E capability set;
- executable route is complete and not truncated;
- no unknown conditional barrier is silently crossed.

### Output

A deterministic preflight result with explicit first blocker and all bounded findings. The output is evidence, not a replacement for runtime E2E.

### Runtime integration note

The physical workflow must generate or obtain the World Index from the exact selected map without committing `.widx`. Cache/reuse may be keyed by exact map SHA plus scanner/tool identity, but stale cache reuse must fail closed.

### Depends on

- OTBM-E2E-001;
- OTBM-E2E-002;
- OTBM-E2E-003;
- executable interaction routing when the scenario crosses conditional barriers.

### Blocks

- OTBM-E2E-005.

---

## OTBM-E2E-005 — Reference physical route: `thais.temple -> thais.depot`

**Goal:** deliver the first real semantic landmark-to-landmark physical route proof on the exact runtime-selected map.

### Hard rule

Do not use coordinates from this programme document or chat history. Determine and review exact `thais.temple` and `thais.depot` anchors from the exact map snapshot using existing OTBM evidence and factual rendering where needed.

### Required flow

```text
resolve thais.temple
resolve thais.depot
resolve common routing region
build/reuse exact World Index
plan route with existing Reachability
resolve required interactions
export route-plan-v1
run exact-map static preflight
start canonical Universal Physical E2E lifecycle
login controlled OTClient
follow_route
assert exact depot destination anchor
safe logout
persistence sentinel
relog
second safe logout
retain route + runtime evidence
```

### Scenario ownership

The feature scenario should own only deterministic route request/fixture/assertion data. Generic route planning, route following and lifecycle behavior remain read-only platform dependencies.

Suggested scenario root:

```text
tests/e2e/scenarios/movement/
```

Use current repository conventions after live inspection; do not assume a filename before task start.

### Acceptance gate

- route request uses semantic landmark IDs rather than a manually authored long direction/count sequence;
- route plan is generated from exact pinned OTBM evidence;
- physical OTClient reaches the exact reviewed depot anchor;
- client movement is exact-position synchronized;
- any required door/transition interaction is explicitly evidenced and executed;
- route preflight passes on the exact runtime map;
- physical run records route-plan provenance and map hash;
- canonical logout/persistence/relog sentinel passes;
- scenario is reproducible on the reviewed exact map snapshot.

### Depends on

- OTBM-E2E-001;
- OTBM-E2E-002;
- OTBM-E2E-003;
- OTBM-E2E-001B when an interactive conditional barrier is required;
- E2E-ROUTE-001;
- OTBM-E2E-004.

---

# Second-stage enhancements after the reference route

These are not blockers for v1 landmark routing. Start them only after OTBM-E2E-005 is merged and archived.

## OTBM-E2E-006 — Automatic E2E failure triage

Classify first failure from route plan plus current physical artifacts, including:

```text
ROUTE_RESOLUTION_FAILURE
ROUTE_PREFLIGHT_FAILURE
PLAN_LOAD_FAILURE
INITIAL_POSITION_MISMATCH
MOVEMENT_DIVERGENCE
BLOCKED_TILE
INTERACTION_UNSUPPORTED
INTERACTION_TIMEOUT
TELEPORT_NOT_TRIGGERED
WRONG_TRANSITION_DESTINATION
WRONG_FLOOR_DELTA
SERVER_DISCONNECT
PERSISTENCE_FAILURE
RELOG_FAILURE
```

Prefer deterministic evidence classification over natural-language guessing.

## OTBM-E2E-007 — OTBM mechanic to Physical E2E coverage matrix

Correlate static mechanics/evidence with physical scenarios to answer which critical mechanics are:

- statically indexed;
- script-resolved;
- reachability-covered;
- physically runtime-proven;
- stale against current map provenance;
- missing a physical scenario.

## OTBM-E2E-008 — Semantic Diff impacted E2E selection

Use existing Semantic OTBM Diff to select route/mechanic scenarios impacted by a reviewed map change. Do not run every physical scenario when the exact diff proves non-impact.

## OTBM-E2E-009 — Candidate-map physical validation

For an approved bounded repair/materialization output:

```text
source map
  -> bounded repair/materialization
  -> candidate map copy
  -> full static validation
  -> Semantic OTBM Diff
  -> impacted route selection
  -> disposable Canary on candidate map
  -> selected Physical E2E
```

Never deploy or overwrite the production/source map as part of this flow.

# Concurrency and ownership strategy

After this planning PR merges:

- OTBM-E2E-001 and OTBM-E2E-002 may start in parallel if their exact owned paths are disjoint;
- OTBM-E2E-003 may start in parallel with the landmark task but must align its final vocabulary with route-plan v1 before merge;
- E2E-ROUTE-001 must not finalize before route-plan v1 and interaction vocabulary are stable;
- OTBM-E2E-001B follows interaction semantics;
- OTBM-E2E-004 follows the stable route/landmark/interaction contracts;
- OTBM-E2E-005 is the integration consumer and starts only after all required reusable interfaces are merged and archived.

Agents must not share branches or claim overlapping files concurrently.

# Explicit non-goals

The following are not part of this programme:

- a new OTBM parser;
- a second World Index;
- an independent route/pathfinding engine;
- replacement of Reachability BFS with a new algorithm merely for E2E;
- a second E2E runner/workflow;
- production map writes or deployment;
- committed OTBM/WIDX/client assets;
- inference of stairs/ladders/holes from sprites or names;
- automatic guessing of semantic landmarks;
- automatic promotion of unresolved Script Resolution evidence;
- dynamic Lua execution by the static route planner;
- combat-aware dynamic replanning in v1;
- live creature/player/movable-item occupancy routing in v1;
- cross-region world-scale semantic routing in v1;
- claiming gameplay correctness from static route success alone.

# v1 completion definition

The programme v1 is complete only when all are true:

1. route-plan v1 is merged and archived;
2. semantic landmark registry/resolver is merged and archived;
3. route interaction semantics are merged and archived;
4. the existing Reachability graph can produce an executable interaction-aware route without a second pathfinder;
5. Universal Physical E2E can execute `follow_route` with exact-position synchronization;
6. exact-map static preflight is merged and archived;
7. `thais.temple -> thais.depot` passes through a real controlled OTClient on an exact reviewed map snapshot;
8. physical evidence proves exact final destination plus canonical logout/persistence/relog;
9. no required v1 task remains active or has an open unmerged feature/lifecycle PR;
10. final durable handover records the exact delivered contracts and non-goals.

# Start here for the next agent

1. Read root `AGENTS.md`.
2. Read `docs/agents/REPOSITORY_MAP.md` and `docs/agents/CONTEXT_ROUTING.md`.
3. Read this programme.
4. Read `docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md`.
5. For OTBM tasks, read only the relevant World Index, Reachability, Script Resolution and transition contracts.
6. For E2E platform tasks, read `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md` and `docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md`.
7. Inspect current open PRs and active task ownership.
8. Start the earliest uncompleted dependency-safe work package above.
9. Create a fresh task/branch/draft PR; do not continue this planning branch after merge.

The default first implementation task is **OTBM-E2E-001 — Reachability executable route export**. **OTBM-E2E-002 — Semantic Landmark Registry** may run concurrently on a separate branch when ownership is clean.
