# OTBM E2E executable route plan

## Purpose

`canary-otbm-e2e-route-plan-v1` is the deterministic bridge from the existing OTBM Reachability graph to later Universal Physical E2E route execution.

The routing architecture is intentionally:

```text
Unified OTBM World Index
  -> existing Reachability tile classification and validated transitions
  -> existing _bfs()
  -> existing previous[position] = (parent, transition_id)
  -> optional reviewed executable edge policy
  -> full edge-aware route reconstruction
  -> canary-otbm-e2e-route-plan-v1
```

It is **not** a second pathfinder. The exporter does not run A*, Dijkstra, another BFS implementation, another OTBM parser or another World Index builder. Interaction-aware execution reruns the same existing `_bfs()` with a narrower fail-closed edge predicate.

Schema: `docs/ai-agent/OTBM_E2E_ROUTE_PLAN.schema.json`

## Export

Geometry-only route-plan export:

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_reachability_tool.py route-plan \
  /path/to/world.widx \
  --world-manifest /path/to/world.widx.json \
  --appearances /path/to/appearances.dat \
  --transitions /path/to/OTBM_TRANSITIONS.json \
  --script-resolution /path/to/OTBM_SCRIPT_RESOLUTION.json \
  --from 32055,32265,7 \
  --to 32090,32295,8 \
  --origin 32062,32271,7 \
  --destination 32070,32280,8 \
  --output /tmp/OTBM_E2E_ROUTE_PLAN.json
```

Interaction-aware executable export adds the reviewed registry:

```bash
  --interactions /path/to/OTBM_ROUTE_INTERACTIONS.json
```

`--from` and `--to` are the same inclusive Reachability routing bounds. `--origin`, `--destination` and all emitted path positions are exact OTBM coordinates.

`--max-positions` defaults to `10000`. It limits the complete executable path, including the origin and destination positions.

Generated route plans are artifacts and must not be committed.

## Relationship to the Reachability report

The existing `canary-otbm-reachability-v1` geometry report remains unchanged when interaction-aware executable routing is not requested. Its public `path` may still be a deterministic head/tail sample controlled by `--path-limit`.

The route-plan exporter does not reuse that sampled path. It selects a predecessor map produced by the same canonical `_bfs()` implementation and reconstructs the route directly from that map.

Therefore:

- `routeStatus` preserves the existing strict/optimistic geometry decision;
- `strictDistance` and `optimisticDistance` remain the existing BFS distances;
- `executableDistance` is present when interaction-aware routing was evaluated and is the distance under the executable edge policy, or `null` when no executable route exists;
- `distance` is the distance of the predecessor map actually exported;
- every route-plan edge corresponds to one predecessor relation from the selected `_bfs()` result;
- `transitionId` remains attached to the exact predecessor edge where Reachability used the validated transition.

A route may therefore have:

```text
routeStatus = conditional
optimisticDistance = 4
executableDistance = 6
routingMode = executable
executionStatus = executable
```

This means geometry found a shorter optimistic path, but executable routing rejected unsafe optimistic crossings and selected a different route whose every conditional crossing has explicit supported interaction evidence.

## Interaction-aware executable routing

Supplying `--interactions` enables `OTBM-E2E-001B` behavior.

The exact reviewed `canary-otbm-route-interactions-v1` registry is validated against:

- source-map SHA-256 from the World Index manifest;
- actual World Index SHA-256;
- transition-manifest SHA-256 when supplied;
- Script Resolution SHA-256 when supplied.

The registry file itself is also hashed and emitted as `provenance.interactionRegistry`.

The executable movement predicate is equivalent to:

```text
strictly walkable destination
OR
optimistically walkable conditional destination
  AND every exact conditional blocker placement resolves to a supported reviewed interaction
  AND required handler evidence is explicitly handled
```

The following remain blocked:

- static blockers;
- unknown appearances, even when a registry selector mentions the unknown item ID;
- missing exact blocker placement evidence;
- unresolved or missing handler evidence for AID/UID-gated blockers;
- unresolved, partially resolved, referenced-only or conflicting Script Resolution states;
- unsupported or ambiguous interaction semantics;
- conditional diagonal crossings that would require implicit interactions on corner tiles.

Strict diagonal movement remains supported with the existing no-corner-cutting rule. Interaction-aware diagonal movement never treats a conditional corner tile as silently crossed.

The executable transition predicate starts from existing validated optimistic transition edges and then requires the exact transition ID to resolve through the reviewed interaction registry. Fail-closed transition uncertainties and unsupported activation semantics remove that edge from the executable graph.

`walk-direction` transition activations are additionally checked against the exact directional edge. A reviewed direction that does not match the selected edge is blocked.

The traversal algorithm remains the existing `_bfs()` in `otbm_reachability_graph.py`.

## Full-path fail-closed rule

An executable plan must contain the complete route.

If the selected route requires more than `maxExecutablePositions` positions, the exporter emits a blocked plan with:

```json
{
  "executionStatus": "blocked",
  "pathComplete": false,
  "path": [],
  "edges": [],
  "blockers": [
    {
      "code": "route-exceeds-supported-bound",
      "requiredPositions": 10001,
      "supportedMaxPositions": 10000
    }
  ]
}
```

No head/tail sample is copied into executable output. A partial path is never published as executable.

## Route and execution status

`routeStatus` preserves the existing Reachability geometry semantics:

- `confirmed` — a strict path exists;
- `conditional` — no strict path exists, but an optimistic path exists;
- `unreachable` — neither strict nor optimistic geometry route exists inside the explicit bounds;
- `invalid` — the request is invalid, for example the destination is outside the explicit bounds.

`executionStatus` remains separate:

- `executable` — the selected complete route satisfies provenance and executable edge requirements;
- `blocked` — geometry selected a route, but no safe complete executable route is available under the requested policy;
- `not-applicable` — the route is `unreachable` or `invalid`.

A plain optimistic route is never sufficient for `executionStatus=executable`.

Without `--interactions`, a `conditional` geometry route remains blocked and a route containing transitions remains blocked by unresolved transition interaction semantics.

With `--interactions`, the exporter builds an executable edge set and reruns the existing `_bfs()`. Only that executable predecessor map may promote a conditional geometry route to `executionStatus=executable`.

## Ordered path and edges

`path` is the complete ordered list of positions when `pathComplete` is true.

`edges` has one entry for every adjacent pair in that path and preserves path order.

### Movement edge

Geometry-only example:

```json
{
  "from": [100, 100, 7],
  "to": [101, 100, 7],
  "kind": "movement",
  "isTransition": false,
  "transitionId": null,
  "evidence": {
    "source": "reachability-bfs-predecessor",
    "edgeSource": "_movement_neighbors",
    "routingMode": "strict"
  }
}
```

A movement edge is a predecessor edge whose stored `transition_id` is `None`. The edge therefore comes from the existing Reachability movement-neighbor path.

When executable routing crosses a reviewed conditional blocker, the same edge also carries exact resolver evidence:

```json
{
  "from": [100, 100, 7],
  "to": [101, 100, 7],
  "kind": "movement",
  "isTransition": false,
  "transitionId": null,
  "evidence": {
    "source": "reachability-bfs-predecessor",
    "edgeSource": "_movement_neighbors",
    "routingMode": "executable"
  },
  "interactions": [
    {
      "format": "canary-otbm-route-interaction-resolution-v1",
      "schemaVersion": 1,
      "executionStatus": "executable",
      "matchedEntryId": "reviewed-door",
      "activation": {
        "kind": "use-map-item",
        "target": "selector-position"
      }
    }
  ],
  "executionBlockers": []
}
```

The full resolution object retains its exact selector query, matched IDs, reviewed evidence and blockers.

### Transition edge

```json
{
  "from": [102, 100, 7],
  "to": [104, 103, 7],
  "kind": "transition",
  "isTransition": true,
  "transitionId": "teleport:123",
  "evidence": {
    "source": "validated-transition-edge",
    "provenanceKey": "worldIndex",
    "transition": {
      "id": "teleport:123",
      "kind": "teleport",
      "source": [102, 100, 7],
      "destination": [104, 103, 7],
      "valid": true,
      "strictEligible": true
    }
  }
}
```

The embedded transition object is copied from the already validated Reachability `TransitionState`. It retains the existing transition kind, source, destination, item/evidence fields, uncertainties, script status, eligibility and issues.

In executable routing mode, the edge is present only if its exact transition interaction resolved as executable. The edge then includes `interactions` and `executionBlockers` just like a reviewed conditional movement edge.

The exporter does not infer stairs, ladders, holes, rope destinations, door behavior or dynamic Lua behavior.

## Provenance and stale-plan detection

Top-level provenance is machine-readable:

- `map` — source map identity from the validated World Index manifest;
- `worldIndex` — actual `.widx` file identity calculated by Reachability;
- `appearances` — exact appearances input identity;
- `transitionManifest` — exact reviewed transition manifest identity when supplied;
- `scriptResolution` — exact script-resolution report identity when supplied;
- `interactionRegistry` — exact reviewed route-interaction registry identity when supplied.

A plan cannot be `executable` without SHA-256 identity for the source map, World Index and appearances. When transition-manifest, Script Resolution or interaction-registry evidence influences the executable decision, the corresponding SHA-256 identity is required.

Two deterministic hashes are emitted:

- `inputHashSha256` hashes provenance, exact origin/destination, exact routing bounds and routing options;
- `planHashSha256` hashes the complete plan payload before the `planHashSha256` field itself is added.

Hash input uses UTF-8 canonical JSON with sorted keys and compact separators. Identical routing inputs and evidence therefore produce identical semantic output and identical hashes.

A later static preflight must compare these identities with the exact runtime-selected map/evidence before physical execution. A matching hash is stale-evidence detection, not gameplay proof.

## Determinism

Route selection remains deterministic because every mode reuses the existing Reachability `_bfs()` and deterministic neighbor ordering. No route-plan-specific search ordering exists.

For identical:

- map and World Index;
- appearances;
- transition and script evidence;
- reviewed interaction registry;
- bounds;
- origin and destination;
- diagonal option;
- executable position bound;

route-plan output and hashes are deterministic.

## Safety boundary

The route plan is static evidence. It does not:

- execute the physical client;
- execute Lua;
- prove door/quest/runtime state;
- invent interaction semantics;
- treat unknown appearances as reviewed mechanics;
- modify OTBM or `.widx` files;
- replace the Universal Physical E2E lifecycle.

Universal `follow_route` belongs to `E2E-ROUTE-001` and remains outside this work package.
