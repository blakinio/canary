# OTBM E2E executable route plan

## Purpose

`canary-otbm-e2e-route-plan-v1` is the deterministic bridge from the existing OTBM Reachability graph to later Universal Physical E2E route execution.

The routing architecture is intentionally:

```text
Unified OTBM World Index
  -> existing Reachability tile classification and validated transitions
  -> existing _bfs()
  -> existing previous[position] = (parent, transition_id)
  -> full edge-aware route reconstruction
  -> canary-otbm-e2e-route-plan-v1
```

It is **not** a second pathfinder. The exporter does not run A*, Dijkstra, another BFS, another OTBM parser or another World Index builder.

Schema: `docs/ai-agent/OTBM_E2E_ROUTE_PLAN.schema.json`

## Export

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

`--from` and `--to` are the same inclusive Reachability routing bounds. `--origin`, `--destination` and all emitted path positions are exact OTBM coordinates.

`--max-positions` defaults to `10000`. It limits the complete executable path, including the origin and destination positions.

Generated route plans are artifacts and must not be committed.

## Relationship to the Reachability report

The existing `canary-otbm-reachability-v1` report remains unchanged by normal `analyze` calls. Its public `path` may still be a deterministic head/tail sample controlled by `--path-limit`.

The route-plan exporter does not reuse that sampled path. It selects the same strict or optimistic BFS cache that produced the existing route decision and reconstructs the route directly from the corresponding predecessor map.

Therefore:

- `routeStatus` is the existing Reachability route status;
- `strictDistance` and `optimisticDistance` are the existing BFS distances;
- `distance` is the selected route distance for `confirmed` or `conditional`;
- every route-plan edge corresponds to one predecessor relation from that selected BFS result;
- `transitionId` is preserved on the exact predecessor edge where Reachability used the validated transition.

## Full-path fail-closed rule

An executable plan must contain the complete route.

If the selected route requires more than `maxExecutablePositions` positions, the exporter emits:

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

`routeStatus` preserves the existing Reachability semantics:

- `confirmed` — a strict path exists;
- `conditional` — no strict path exists, but an optimistic path exists;
- `unreachable` — neither route exists inside the explicit bounds;
- `invalid` — the request is invalid, for example the destination is outside the explicit bounds.

`executionStatus` is separate:

- `executable` — currently possible only for a complete `confirmed` route whose required provenance is present and whose edges need no unresolved interaction semantics;
- `blocked` — a geometrically selected route exists but is not safe to execute under the current contract;
- `not-applicable` — the route is `unreachable` or `invalid`.

A plain optimistic `conditional` route is always blocked. Doors, quest gates and other conditional barriers are not promoted to executable by this contract.

Transition activation semantics belong to `OTBM-E2E-003 — Route interaction semantics` and the possible later `OTBM-E2E-001B — Executable interaction-aware routing mode`. Until those semantics are explicitly resolved, a selected route containing a transition is exported with exact transition evidence but remains blocked by `transition-interaction-semantics-unresolved`.

This conservative rule does not alter Reachability's geometry decision or distance.

## Ordered path and edges

`path` is the complete ordered list of positions when `pathComplete` is true.

`edges` has one entry for every adjacent pair in that path and preserves path order.

### Movement edge

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

The exporter does not infer stairs, ladders, holes, rope destinations, door behavior or dynamic Lua behavior.

## Provenance and stale-plan detection

Top-level provenance is machine-readable:

- `map` — source map identity from the validated World Index manifest;
- `worldIndex` — actual `.widx` file identity calculated by Reachability;
- `appearances` — exact appearances input identity;
- `transitionManifest` — exact reviewed transition manifest identity when supplied;
- `scriptResolution` — exact script-resolution report identity when supplied.

A plan cannot be `executable` without SHA-256 identity for the source map, World Index and appearances. When transition-manifest or script-resolution evidence influenced the selected route, the corresponding SHA-256 identity is also required.

Two deterministic hashes are emitted:

- `inputHashSha256` hashes provenance, exact origin/destination, exact routing bounds and routing options;
- `planHashSha256` hashes the complete plan payload before the `planHashSha256` field itself is added.

Hash input uses UTF-8 canonical JSON with sorted keys and compact separators. Identical routing inputs and evidence therefore produce identical semantic output and identical hashes.

A later static preflight must compare these identities with the exact runtime-selected map/evidence before physical execution. A matching hash is stale-evidence detection, not gameplay proof.

## Determinism

Route selection remains deterministic because the exporter reuses the existing Reachability BFS and its deterministic neighbor ordering. No route-plan-specific search ordering exists.

For identical:

- map and World Index;
- appearances;
- transition and script evidence;
- bounds;
- origin and destination;
- diagonal option;
- executable position bound;

the route-plan output and both hashes are deterministic.

## Safety boundary

The route plan is static evidence. It does not:

- execute the physical client;
- execute Lua;
- prove door/quest/runtime state;
- invent interaction semantics;
- modify OTBM or `.widx` files;
- replace the Universal Physical E2E lifecycle.

Universal `follow_route` belongs to `E2E-ROUTE-001` and is deliberately outside this work package.
