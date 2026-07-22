# OTBM connectivity resilience

## Purpose

`OTBM-QA-011` provides a deterministic static review layer for connectivity resilience, route fragility, selected entry/exit entrapment candidates and reviewed transition/teleport topology.

It deliberately reuses the canonical OTBM Reachability implementation:

- `_bfs()` is the only pathfinder used for baseline routes, single-edge perturbations, full baseline-edge exclusion and entry-to-exit checks;
- `_movement_neighbors()` remains the movement-topology authority;
- `_transition_edges()` remains the reviewed transition-edge authority;
- `_reconstruct_route()` reconstructs canonical predecessor routes;
- `_tarjan_cycles()` remains the transition-cycle implementation.

Public formats:

```text
canary-otbm-connectivity-resilience-manifest-v1
canary-otbm-connectivity-resilience-v1
```

Entrypoints:

- `tools/ai-agent/otbm_connectivity_resilience.py`
- `tools/ai-agent/otbm_connectivity_resilience_tool.py`
- `docs/ai-agent/OTBM_CONNECTIVITY_RESILIENCE_MANIFEST.schema.json`
- `docs/ai-agent/OTBM_CONNECTIVITY_RESILIENCE.schema.json`

QA-011 does not implement another parser, World Index, transition resolver, route planner or BFS.

## Reviewed manifest

The manifest pins one exact source map and World Index and selects one bounded region:

```json
{
  "format": "canary-otbm-connectivity-resilience-manifest-v1",
  "schemaVersion": 1,
  "source": {
    "mapSha256": "<64 hex>",
    "worldIndexSha256": "<64 hex>"
  },
  "region": {
    "from": [100, 100, 7],
    "to": [200, 200, 7],
    "allowDiagonal": false
  },
  "routes": [],
  "entrapmentTargets": [],
  "topology": null
}
```

At least one route, entrapment target or topology view must be selected.

Every route and entry/exit coordinate must be explicitly reviewed and inside the declared region. QA-011 never infers coordinates from semantic names, sprites, labels, proximity or chat history.

## Evidence modes

Selected targets use one explicit mode:

- `strict` — canonical strict walkability plus strict-eligible reviewed transitions;
- `optimistic` — canonical optimistic walkability plus optimistic-eligible reviewed transitions;
- `executable` — available only when an exact reviewed Route Interaction Registry is supplied; the existing Reachability interaction-aware movement/transition resolvers are reused unchanged.

The report always records strict and optimistic reachability for reviewed route pairs. A route that exists only optimistically is marked `conditionalOnly` and receives `ROUTE_REQUIRES_CONDITIONAL_EVIDENCE`.

Optimistic or unresolved evidence is never promoted to strict proof.

## Route fragility

For each reviewed route target:

1. QA-011 runs canonical `_bfs()` in the requested mode.
2. If reachable, it reconstructs one complete canonical predecessor route with `_reconstruct_route()`.
3. For each directed edge on that route, it reruns the same canonical `_bfs()` while excluding exactly that edge.
4. An edge is reported as critical only when that one exact exclusion makes the reviewed goal unreachable.
5. QA-011 then excludes every edge from the first canonical route at once and reruns canonical `_bfs()` again.
6. If the goal remains reachable, one fully edge-disjoint alternative route is proven from canonical predecessor evidence.

Route classifications:

- `unreachable`;
- `single-edge-fragile`;
- `edge-disjoint-alternative`;
- `single-edge-resilient-no-full-disjoint-alternative`.

The final class is intentionally narrower than a general graph-connectivity theorem. It means no edge on the selected canonical route is individually critical, but a second route avoiding every edge from that entire first route was not proven.

A `single-edge-fragile` finding is review evidence. It does not by itself make the report fail and does not authorize a map repair.

## Static entrapment candidates

An entrapment target declares one reviewed entry and one or more reviewed exits.

QA-011 runs canonical `_bfs()` from the entry in the selected mode:

- `exit-proven` — at least one declared exit is reachable;
- `static-entrapment-candidate` — none of the declared exits is proven reachable.

The report selects the nearest reachable exit deterministically by `(distance, position)` and preserves the canonical predecessor path.

`static-entrapment-candidate` is bounded static evidence only. The report always keeps:

```text
runtimeEntrapmentProven = false
runtimeEntrapmentClaimed = false
globalConnectivityClaimed = false
```

Runtime quest/storage/door state, dynamic Lua, unselected transitions, external movement mechanisms or Physical E2E may change actual gameplay behavior.

## Transition and teleport topology

The optional topology view uses canonical transition edges for explicitly selected transition kinds and one selected evidence mode.

It reports:

- directed transition-edge count;
- one-way reviewed transition edges;
- destinations with no canonical movement or transition exit in the selected mode;
- strongly connected transition cycles from the existing `_tarjan_cycles()` implementation.

A transition carrying reviewed uncertainty marker `one-way-intended` is classified as `reviewed-one-way-intended` and is not promoted to a defect finding.

Other one-way edges remain `one-way-review-candidate`. Dead ends and closed cycles are also review candidates, not automatic defects.

The topology view does not infer reverse stairs, holes, ladders, ropes, teleport destinations or scripted transitions.

## Canonical Reachability validation

Preparing a real-map QA-011 context reuses the same evidence boundary as Reachability:

- canonical World Index;
- exact World Index manifest source-map SHA-256;
- appearance semantics;
- reviewed transition manifest when supplied;
- Script Resolution when supplied;
- reviewed Route Interaction Registry when executable evidence is requested.

Tile classification and transition validation reuse `_classify_tile()`, `_transition_from_manifest()` and `_validate_transition()` before any resilience analysis. Their bounded findings are preserved in `canonicalReachabilityValidation` rather than reinterpreted as QA-011 findings.

## CLI

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_connectivity_resilience_tool.py \
  --manifest /tmp/OTBM_CONNECTIVITY_RESILIENCE_MANIFEST.json \
  --world-index /tmp/world.widx \
  --world-manifest /tmp/world.manifest.json \
  --appearances /tmp/appearances.json \
  --transitions /tmp/OTBM_TRANSITIONS.json \
  --script-resolution /tmp/OTBM_SCRIPT_RESOLUTION.json \
  --route-interactions /tmp/OTBM_ROUTE_INTERACTIONS.json \
  --output /tmp/OTBM_CONNECTIVITY_RESILIENCE.json
```

Optional evidence inputs may be omitted when the selected analysis does not require them. `executable` mode is unavailable unless a reviewed interaction registry is supplied.

The CLI rejects:

- symlink inputs or outputs;
- duplicate input files;
- input/output collisions and hard-link collisions;
- oversized JSON inputs;
- output clobber unless `--overwrite` is explicit.

Create-new output is the default; overwrite uses atomic replacement.

## Report success boundary

`ok` is false when a reviewed route is unreachable or a reviewed entry has no proven selected exit.

Route fragility, conditional-only routing and transition-topology review candidates remain explicit findings but do not automatically make `ok` false. This keeps the report transparent instead of turning heterogeneous review evidence into one opaque quality score.

## Non-goals

QA-011 does not:

- implement a second pathfinder or route planner;
- parse or write OTBM independently;
- build another World Index;
- infer transition destinations or reverse edges;
- execute Lua or simulate runtime quest/storage/door state;
- execute Physical E2E;
- claim global world connectivity or runtime entrapment;
- recommend or apply map repairs.
