# OTBM to Universal Physical E2E Route Integration

> Programme: `CAN-PROGRAM-OTBM-E2E-ROUTING`  
> Coordination: `OTBM-E2E-ROUTE-V1`  
> Status: architecture ratification / implementation queue  
> Repository writes: `blakinio/canary` only

## Purpose

Define the minimal bridge between the completed OTBM analysis stack and the existing Universal Physical E2E platform so physical OTClient movement can be driven by exact map evidence instead of hand-authored blind direction/count sequences.

Target user intent:

```text
Go from thais.temple to thais.depot.
```

Target deterministic execution:

```text
semantic request
  -> exact landmark anchors
  -> exact bounded routing region
  -> exact runtime map identity
  -> existing World Index
  -> existing Reachability graph/BFS
  -> interaction-aware executable route plan
  -> exact-map preflight
  -> Universal Physical E2E follow_route
  -> controlled real OTClient
  -> exact-position and transition evidence
```

This document is a design and implementation contract. It does not claim that `thais.temple` or `thais.depot` coordinates have already been verified. Implementation agents must determine those anchors from the exact runtime-selected map snapshot.

# Architectural decision

## Reuse the existing pathfinder

The canonical pathfinding implementation remains OTBM Reachability.

Existing code already provides:

```text
World Index tiles
  + appearance semantics
  + strict/optimistic tile classification
  + teleport transition edges
  + reviewed floor-transition edges
  -> _bfs()
  -> previous[position] = (parent, transition_id)
  -> _reconstruct_path()
```

The integration must extend this graph/export boundary. It must not create a second BFS/A*/Dijkstra implementation under E2E or another AI-agent tool.

## Separate static planning from physical execution

OTBM tooling owns:

- map evidence;
- tile classification;
- route graph;
- transition evidence;
- semantic landmark resolution;
- interaction evidence;
- route-plan generation;
- route preflight.

Universal E2E owns:

- disposable runtime;
- exact server/client lifecycle;
- physical client commands;
- current player-position observation;
- runtime interaction execution;
- transition result observation;
- logout/persistence/relog;
- physical evidence artifacts.

Static success never becomes gameplay proof until the controlled physical client completes the declared assertions.

# Existing components and direct reuse

## Unified OTBM World Index

Use directly for:

- every exact tile `x,y,z`;
- tile kind and house ID;
- item placements;
- item IDs;
- AID;
- UID;
- house-door ID;
- teleport destination;
- deterministic map/index provenance.

Do not add a second OTBM parser or map scanner.

## OTBM Reachability

Use directly for route search.

Current relevant behavior:

- default cardinal movement;
- optional diagonal movement;
- no diagonal corner cutting;
- missing tile is non-traversable;
- strict walkability excludes conditional blockers and unknown appearances;
- optimistic walkability allows conditional/unknown non-static barriers;
- teleport destinations create transition candidates from World Index;
- reviewed transition manifest adds stairs/ladder/hole/rope/floor-change/custom transitions;
- BFS caches distances and predecessor graph;
- predecessor entry retains the transition ID used on a graph edge;
- public report reconstructs a path and reports transition IDs used.

Current public report limitation for E2E:

```text
path[] may be truncated
transitionIdsUsed[] is separate from exact path edge positions
route status is geometry evidence, not physical-execution readiness
```

Therefore Reachability requires an **export extension**, not replacement.

## OTBM Script Resolution

Use as a safety/evidence input when a route requires AID/UID/item/position behavior.

Important rule:

```text
unresolved != handled
conflicting != executable
```

A route interaction requiring a runtime handler must not become executable when the relevant evidence is unresolved, partially resolved, referenced-only or conflicting unless a separately reviewed engine/generic handling rule proves execution.

## Reviewed transition manifest

Use directly for non-teleport floor transitions.

The existing fields already provide:

- stable transition ID;
- kind;
- source;
- destination or delta;
- expected item IDs;
- bidirectionality;
- uncertainties;
- review evidence.

The route bridge adds physical activation semantics separately rather than guessing them.

## Universal Physical E2E

Use directly for:

- exact Canary runtime;
- runtime-selected datapack/map;
- MariaDB fixture;
- controlled pinned `blakinio/otclient`;
- first-session action execution;
- safe logout and persistence;
- second login/logout sentinel;
- logs/screenshots/session records/result artifacts.

Do not create another workflow or launcher.

# Route planning states

Keep geometry and physical executability distinct.

Recommended v1 fields:

```text
routeStatus:
  confirmed
  conditional
  unreachable
  invalid

executionStatus:
  executable
  blocked
  not-applicable
```

Rules:

- `confirmed` + all required transitions/interactions physically supported -> `executable`;
- `confirmed` + unsupported required physical activation -> `blocked`;
- `conditional` -> `blocked` until every selected conditional crossing is explicitly resolved by interaction evidence and the same Reachability graph is rerun/evaluated with an executable predicate;
- `unreachable` or `invalid` -> `not-applicable` for physical execution.

Plain optimistic reachability is never sufficient proof of physical executability.

# Proposed route-plan contract

Format:

```text
canary-otbm-e2e-route-plan-v1
```

The schema should be added in the first implementation task and remain deterministic.

## Minimal document

The coordinates below are intentionally illustrative and are **not Thais evidence**.

```json
{
  "format": "canary-otbm-e2e-route-plan-v1",
  "schemaVersion": 1,
  "provenance": {
    "mapSha256": "<sha256>",
    "worldIndexSha256": "<sha256>",
    "appearancesSha256": "<sha256>",
    "scriptResolutionSha256": null,
    "transitionManifestSha256": null,
    "landmarkRegistrySha256": null,
    "interactionRegistrySha256": null
  },
  "request": {
    "from": {"landmark": "example.origin"},
    "to": {"landmark": "example.destination"},
    "region": "example.region",
    "allowDiagonal": false
  },
  "start": [100, 100, 7],
  "goal": [105, 103, 7],
  "routeStatus": "confirmed",
  "executionStatus": "executable",
  "distance": 8,
  "steps": [
    {
      "kind": "walk",
      "positions": [
        [100, 100, 7],
        [101, 100, 7],
        [102, 100, 7]
      ]
    },
    {
      "kind": "transition",
      "transitionId": "teleport:123",
      "transitionKind": "teleport",
      "activation": "step-on",
      "source": [102, 100, 7],
      "destination": [104, 103, 7],
      "itemId": 1959
    },
    {
      "kind": "walk",
      "positions": [
        [104, 103, 7],
        [105, 103, 7]
      ]
    }
  ],
  "uncertainties": [],
  "blockers": []
}
```

## Contract rules

### Provenance

`mapSha256` and `worldIndexSha256` are mandatory for executable plans.

Other hashes are mandatory when their corresponding evidence influenced the executable decision.

Examples:

- pure same-floor strict walk: Script Resolution may be null;
- engine teleport: transition evidence comes from World Index, Script Resolution may be null when no AID/UID requires correlation;
- AID door use: Script Resolution and interaction registry hashes are required;
- reviewed ladder: transition manifest and interaction registry hashes are required.

### Start and goal

Always materialize exact coordinates even when the request used landmarks.

The preflight must verify that landmark resolution still yields the exact same selected anchors.

### Distance

Distance is graph edge count under the exact planning policy. It is not wall-clock duration.

### Full path

An executable plan must contain all required movement positions and transitions.

```text
pathTruncated == true
=> executionStatus = blocked
```

The route-plan contract should not expose a truncated plan as executable.

### Determinism

For identical inputs and policy, output ordering and route selection must be deterministic.

Reuse the current deterministic neighbor ordering in Reachability.

# Route step vocabulary

## `walk`

Represents one or more consecutive same-floor movement edges.

```json
{
  "kind": "walk",
  "positions": [
    [100, 100, 7],
    [101, 100, 7],
    [102, 100, 7]
  ]
}
```

Rules:

- every adjacent pair must be a movement edge produced by the existing Reachability movement-neighbor rules;
- `positions[0]` must equal the prior route state;
- executor derives direction from coordinate delta;
- executor does not trust a precomputed direction string as source of truth;
- physical execution synchronizes after every tile.

## `interact`

Represents an action required before the following movement/transition can execute.

```json
{
  "kind": "interact",
  "interactionId": "thais-door-example",
  "activation": "use-map-item",
  "actorPosition": [102, 100, 7],
  "targetPosition": [103, 100, 7],
  "itemId": 1234,
  "actionId": 45001,
  "uniqueId": null,
  "houseDoorId": null,
  "scriptStatus": "handled-by-action-id"
}
```

Rules:

- long-lived interaction selection should use stable reviewed selectors such as transition ID or exact position plus mechanic identifiers;
- placement ordinal may be carried as exact-plan evidence but should not be the sole durable registry key;
- missing supported activation blocks physical execution;
- unresolved/conflicting required script evidence blocks physical execution.

## `transition`

Represents a graph edge where destination is not an ordinary adjacent same-floor movement edge.

```json
{
  "kind": "transition",
  "transitionId": "thais-ladder-up",
  "transitionKind": "ladder",
  "activation": "use-map-item",
  "source": [100, 100, 8],
  "destination": [100, 100, 7],
  "expectedItemIds": [1948]
}
```

Supported v1 transition kinds reuse current Reachability vocabulary:

```text
teleport
stairs
ladder
hole
rope
floor-change
custom
```

# Physical activation vocabulary

Initial v1 values:

## `step-on`

Client reaches the source tile through normal movement; the server mechanic should relocate/change floor automatically.

Typical use:

- engine teleport;
- step-in move event when explicitly resolved.

Physical assertion:

```text
before trigger: current == transition.source
trigger
wait bounded timeout
current == transition.destination
```

## `walk-direction`

The transition is triggered by one specific movement request from an adjacent source state.

Use only with explicit reviewed evidence. Do not infer direction from sprite/name.

## `use-map-item`

Controlled client sends use on an exact map tile/item target.

Typical use:

- doors;
- ladders;
- levers;
- reviewed map interactions.

The exact maintained OTClient API must be verified before implementation.

## `use-inventory-on-map`

Controlled client uses a specific inventory item on an exact map target.

Typical use:

- rope/tool interactions when explicitly reviewed.

The exact maintained OTClient API must be verified before implementation.

# Semantic Landmark Registry

Format:

```text
canary-otbm-semantic-landmarks-v1
```

Purpose:

```text
human/agent semantic name
-> reviewed exact route anchor(s)
-> bounded routing region
```

Do not infer landmarks automatically from sprites, item names or chat memory.

## Proposed model

Coordinates below are illustrative only.

```json
{
  "format": "canary-otbm-semantic-landmarks-v1",
  "schemaVersion": 1,
  "provenance": {
    "mapSha256": "<sha256>",
    "worldIndexSha256": "<sha256>"
  },
  "regions": [
    {
      "id": "example.city",
      "from": [50, 50, 6],
      "to": [300, 300, 8]
    }
  ],
  "landmarks": [
    {
      "id": "example.temple",
      "region": "example.city",
      "anchors": [
        {
          "id": "main-floor-route-origin",
          "role": "route-origin",
          "position": [100, 100, 7],
          "evidence": {
            "source": "reviewed OTBM evidence"
          }
        }
      ]
    },
    {
      "id": "example.depot",
      "region": "example.city",
      "anchors": [
        {
          "id": "main-entrance-route-destination",
          "role": "route-destination",
          "position": [200, 200, 7],
          "evidence": {
            "source": "reviewed OTBM evidence"
          }
        }
      ]
    }
  ]
}
```

## Landmark selection rules

v1 should require deterministic anchor selection.

Recommended caller form:

```text
from landmark + optional anchor id
 to landmark + optional anchor id
```

If multiple anchors match a requested role and no deterministic default exists, fail as ambiguous instead of choosing heuristically.

## Region rules

The region provides the explicit bounded Reachability search volume.

For v1:

- same-region semantic routes are required;
- start and goal anchors must lie inside the region;
- region coordinate volume must respect existing Reachability bounds;
- cross-region automatic routing is deferred.

# Route Interaction Registry

Format:

```text
canary-otbm-route-interactions-v1
```

Purpose:

```text
reviewed map mechanic/transition evidence
-> physical activation semantics
```

This registry is separate from landmarks.

## Proposed model

Illustrative example only:

```json
{
  "format": "canary-otbm-route-interactions-v1",
  "schemaVersion": 1,
  "entries": [
    {
      "id": "example-ladder-up",
      "selector": {
        "transitionId": "example-ladder-transition"
      },
      "activation": {
        "kind": "use-map-item",
        "target": "transition-source"
      },
      "requirements": {
        "allowedScriptStatuses": [
          "handled-by-engine",
          "handled-by-item-id",
          "handled-by-action-id"
        ]
      },
      "evidence": {
        "source": "reviewed physical mechanic contract"
      }
    }
  ]
}
```

Alternative selector for a door:

```json
{
  "position": [100, 100, 7],
  "itemId": 1234,
  "actionId": 45001
}
```

Every selector must be narrow enough to avoid applying one physical behavior to unrelated mechanics.

# Interaction-aware executable routing

## Why optimistic Reachability alone is insufficient

Current optimistic mode may traverse:

- a known usable door;
- an unknown non-ground appearance;
- a quest barrier;
- a dynamic-script barrier;
- another runtime-dependent blocker.

Therefore:

```text
optimistic path exists
```

does not imply:

```text
physical route is executable
```

## Required executable predicate

The same existing BFS should be reused with a policy equivalent to:

```text
tile/edge is executable when:
  strict walkability permits it
  OR
  every conditional crossing on that exact edge is resolved by a supported reviewed interaction
```

Still blocked:

- static blocker;
- unknown appearance with no reviewed interaction;
- unresolved quest-state requirement;
- unresolved dynamic script;
- conflicting Script Resolution;
- unsupported physical activation.

This may require refactoring the Reachability movement-neighbor predicate so `_bfs()` can consume an executable policy. The traversal algorithm itself remains the existing `_bfs()`.

# Universal E2E integration

## Scenario-level contract

Do not place arbitrary host filesystem paths in scenario JSON.

Recommended future scenario shape:

```json
{
  "routeRequests": [
    {
      "id": "primary",
      "fromLandmark": "thais.temple",
      "toLandmark": "thais.depot",
      "policy": "executable"
    }
  ],
  "steps": [
    {
      "id": "travel-to-depot",
      "action": "follow_route",
      "route": "primary"
    }
  ]
}
```

The canonical runner/lifecycle resolves `primary` to a generated evidence artifact such as:

```text
<evidence-dir>/route-primary.json
```

The scenario references the logical route ID, not an arbitrary path.

The exact top-level field name must be finalized by the implementation task after inspecting current scenario validation conventions. Do not add an incompatible parallel scenario format.

## Route generation timing

The route must be generated against the exact map selected for the physical runtime.

Required ordering:

```text
resolve scenario
acquire/materialize exact runtime map
hash map
build or reuse exact World Index cache
load exact appearance semantics
load reviewed landmarks/interactions/transitions/script evidence
resolve route request
export route plan
run static route preflight
start/continue physical client execution
```

If current Universal E2E lifecycle starts Canary before the exact route planning inputs are available, the platform task should insert the smallest bounded planning hook at the point after map/assets are materialized and before the controlled client executes `follow_route`.

Do not duplicate map download/acquisition in a new workflow.

## World Index caching

Generated `.widx` remains outside Git.

Cache reuse may use a key including at least:

```text
map SHA-256
scanner/tool identity
World Index format version
```

A hash mismatch must rebuild or fail closed. Never silently use an index for another map snapshot.

# `follow_route` physical execution algorithm

Pseudo-flow:

```text
load validated route plan from canonical evidence path
assert executionStatus == executable
assert route-plan provenance matches preflight result
current = observe exact local-player position
assert current == plan.start

for step in plan.steps:
  if step.kind == walk:
    for next_position in step.positions[1:]:
      assert current == previous expected position
      derive direction from current -> next_position
      send one movement request
      wait bounded timeout until exact current position == next_position
      if timeout or different position:
        fail MOVEMENT_DIVERGENCE with expected and actual
      current = next_position

  if step.kind == interact:
    assert current == step.actorPosition
    execute declared supported activation
    wait declared bounded settle/condition if contract requires it

  if step.kind == transition:
    assert current == step.source when activation semantics require source occupancy
    execute trigger (step-on, walk-direction, use-map-item, use-inventory-on-map)
    wait bounded timeout
    assert exact current position == step.destination
    current = step.destination

assert current == plan.goal
emit follow_route success
continue existing safe logout/persistence/relog lifecycle
```

## Exact-position synchronization

This is mandatory.

The route executor must not do:

```text
north x 19 with interval 300 ms
then assume position
```

It must do:

```text
send one expected move
observe exact expected position
continue only after confirmation
```

A future optimization may batch safe client inputs only if it preserves exact checkpoint synchronization and deterministic first-failure evidence.

# Static route preflight

Format name may be finalized by the implementation task. Suggested result:

```text
canary-otbm-e2e-route-preflight-v1
```

## Mandatory checks

### Provenance

- exact runtime map SHA equals plan map SHA;
- exact World Index SHA equals plan index SHA;
- required appearance/script/transition/landmark/interaction evidence hashes match;
- no referenced evidence is missing.

### Request resolution

- semantic landmarks still exist;
- selected anchors still resolve exactly;
- start and goal match plan;
- routing region matches the plan and contains both anchors.

### Walk path

For every adjacent coordinate pair:

- source exists;
- destination exists;
- movement delta is valid;
- destination satisfies the planning/execution policy;
- diagonal movement, when enabled, has both orthogonal corner tiles valid;
- no unexpected transition is assumed as ordinary walk.

### Interactions

- selector still matches exact position/mechanic evidence;
- required item/AID/UID/houseDoor evidence still matches;
- required Script Resolution status is still allowed;
- activation kind is supported by Universal E2E;
- no unresolved/conflicting behavior is hidden.

### Transitions

- transition ID still resolves;
- source matches;
- destination matches;
- expected item IDs match where declared;
- transition remains eligible under the same planning policy;
- activation semantics are supported.

### Completeness

- route is not truncated;
- all steps form one continuous state sequence from start to goal;
- no gaps or duplicate contradictory states;
- `executionStatus == executable`.

# Failure codes

At minimum the bridge should converge on deterministic first-failure classes.

## Static/planning

```text
LANDMARK_NOT_FOUND
LANDMARK_AMBIGUOUS
LANDMARK_STALE
ROUTING_REGION_INVALID
ROUTE_UNREACHABLE
ROUTE_CONDITIONAL_UNRESOLVED
ROUTE_TOO_LONG
ROUTE_TRUNCATED
ROUTE_PROVENANCE_MISMATCH
INTERACTION_NOT_FOUND
INTERACTION_UNSUPPORTED
SCRIPT_RESOLUTION_BLOCKED
TRANSITION_STALE
ROUTE_PREFLIGHT_FAILED
```

## Physical

```text
INITIAL_POSITION_MISMATCH
MOVEMENT_DIVERGENCE
MOVEMENT_TIMEOUT
INTERACTION_FAILED
INTERACTION_TIMEOUT
TRANSITION_NOT_TRIGGERED
WRONG_TRANSITION_DESTINATION
FINAL_POSITION_MISMATCH
```

Existing generic E2E login/server/persistence/relog failures remain owned by Universal E2E and should not be duplicated under new names unless the existing contract requires a mapping layer.

# Exact example flow: `thais.temple -> thais.depot`

No coordinates are specified here because they must be verified against the exact runtime-selected map.

## 1. Resolve semantic request

Input:

```text
from = thais.temple
to   = thais.depot
```

Landmark resolver returns:

```text
from anchor = exact reviewed x,y,z
to anchor   = exact reviewed x,y,z
region      = thais.city (or the exact reviewed region ID used by the registry)
```

If either landmark is missing/ambiguous/stale, stop.

## 2. Pin runtime map

Universal E2E acquires/materializes its exact repository-approved runtime map and records SHA-256.

The route process builds or reuses the matching World Index only when the cache provenance matches exactly.

## 3. Load static evidence

Load:

```text
World Index
appearances
reviewed transition manifest
Script Resolution when required
Semantic Landmark Registry
Route Interaction Registry
```

## 4. Route through existing Reachability

Run the existing graph/BFS from temple anchor to depot anchor inside the exact bounded city region.

Planning preference:

1. strict path when available;
2. otherwise interaction-aware executable path using only explicitly resolved conditional crossings;
3. never fall back to arbitrary optimistic unknown crossings for physical execution.

## 5. Export route plan

Produce `canary-otbm-e2e-route-plan-v1` with:

- exact provenance;
- exact start/goal;
- complete movement positions;
- exact transition edge annotations;
- exact required interactions;
- zero unresolved executable blockers.

## 6. Preflight

Validate the full route against the exact runtime map and current integration capability set.

A single stale coordinate, unsupported door use or changed transition destination blocks physical execution before OTClient travel begins.

## 7. Physical execution

Existing Universal E2E logs in the controlled OTClient.

`follow_route(primary)`:

- checks exact temple start anchor;
- executes one expected tile movement at a time;
- confirms position after every movement edge;
- executes any explicit door/use action;
- validates exact teleport/floor-transition destinations;
- reaches the exact depot destination anchor.

## 8. Existing sentinel

After route success:

```text
safe logout
server persistence confirmation
logout complete
second login
second safe logout
E2E success
```

## 9. Retained evidence

In addition to existing physical artifacts, retain generated local artifacts such as:

```text
route request resolution
route-plan JSON
route-preflight JSON
map SHA
World Index SHA/provenance
bounded route execution event stream
first-failure classification when failed
```

Generated `.widx`, OTBM and client assets remain uncommitted.

# What is missing today

The following are the actual missing bridge capabilities:

1. edge-aware full route export from existing Reachability predecessor data;
2. executable non-truncated route-plan contract;
3. semantic landmark registry/resolver;
4. physical interaction registry/resolver;
5. interaction-aware executable policy using the same Reachability BFS;
6. exact-map route preflight;
7. Universal E2E `follow_route` action;
8. exact-position movement synchronization;
9. generic `use-map-item` support;
10. generic `use-inventory-on-map` support when verified against maintained OTClient API;
11. runtime hook that generates/preflights route plans after exact map acquisition and before physical route execution;
12. first real landmark scenario with verified Thais anchors.

Everything else should reuse existing OTBM and Universal E2E infrastructure.

# Explicit safety boundaries

- no new OTBM parser;
- no new World Index;
- no independent E2E pathfinder;
- no second physical runner/workflow;
- no AI-generated map visualization;
- no committed `.otbm`, `.widx`, `items.otb` or client assets;
- no guessed Thais coordinates;
- no guessed floor-transition offsets;
- no guessed door/use activation;
- no dynamic Lua execution by static tooling;
- no unresolved-to-handled promotion;
- no production target;
- no in-place map writes;
- no claim of gameplay correctness from static route evidence.

# Implementation entrypoint for agents

The first implementation agent should start with:

```text
OTBM-E2E-001 — Reachability executable route export
```

Required first reads:

```text
AGENTS.md
docs/agents/REPOSITORY_MAP.md
docs/agents/CONTEXT_ROUTING.md
docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
this document
docs/ai-agent/OTBM_REACHABILITY.md
docs/ai-agent/OTBM_REACHABILITY.schema.json
relevant otbm_reachability source/tests
```

The Semantic Landmark Registry task may start concurrently on a different branch when live ownership is clean.

Every implementation agent must create its own active task record and draft PR. This planning branch is not an implementation branch.
