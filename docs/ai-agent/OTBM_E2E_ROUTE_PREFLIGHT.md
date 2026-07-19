# OTBM E2E Exact-Map Route Preflight

`OTBM-E2E-004` adds a deterministic fail-closed static validation layer for executable `canary-otbm-e2e-route-plan-v1` artifacts before an expensive Canary + controlled-OTClient physical run.

The result format is:

```text
canary-otbm-e2e-route-preflight-v1
```

Schema:

```text
docs/ai-agent/OTBM_E2E_ROUTE_PREFLIGHT.schema.json
```

Implementation:

```text
tools/ai-agent/otbm_route_preflight.py
```

## Architectural boundary

This tool does not parse OTBM, build another World Index, implement another pathfinder, render maps, execute Lua, start Canary, or drive OTClient.

It reuses:

- the existing Unified OTBM World Index and its provenance manifest;
- the existing Reachability exporter and the same `_bfs()` graph traversal;
- the existing appearance classification and no-corner-cutting movement rules;
- the existing transition manifest and transition validation;
- the existing Script Resolution report states;
- the existing `canary-otbm-semantic-landmarks-v1` resolver;
- the existing `canary-otbm-route-interactions-v1` resolver;
- the existing deterministic `canary-otbm-e2e-route-plan-v1` contract.

A passing preflight is static evidence only. It is not gameplay proof and does not replace the Universal Physical E2E lifecycle.

## Why canonical route regeneration is required

The preflight does not independently decide whether a tile or transition is traversable. After exact provenance checks, it asks the existing Reachability layer to regenerate the route plan from the current exact inputs:

```text
runtime map
  + exact matching World Index
  + appearances
  + referenced transition manifest
  + referenced Script Resolution report
  + referenced interaction registry
  -> existing export_route_plan_index_path()
  -> existing Reachability classification + _bfs()
  -> current canonical route plan
```

The supplied plan must still match the deterministic current routing result. This catches stale tile classification, changed transitions, newly blocked interactions, unresolved handler evidence, and route changes without creating a parallel pathfinder.

## Mandatory exact inputs

The CLI requires:

```text
--route-plan
--runtime-map
--world-index
--appearances
--world-index-manifest
```

Optional evidence must be supplied when the plan provenance references it:

```text
--transitions
--script-resolution
--interaction-registry
```

Semantic request revalidation is optional and uses both:

```text
--landmark-registry
--landmark-request
```

They must be supplied together.

The landmark request shape is deliberately separate from the already-merged route-plan v1 schema:

```json
{
  "from": {
    "landmarkId": "example.origin"
  },
  "to": {
    "landmarkId": "example.destination"
  }
}
```

An exact reviewed anchor can be selected with `anchorId`. Without it, the preflight resolves `route-origin` for `from` and `route-destination` for `to`. Ambiguous, missing, unbound, or stale landmark evidence fails closed.

## Checks

### Route-plan integrity

The preflight verifies:

- format `canary-otbm-e2e-route-plan-v1` and schema version 1;
- canonical `planHashSha256` after removing only the hash field itself;
- `executionStatus == executable`;
- routing mode is `strict` or interaction-aware `executable`, never plain `optimistic`;
- `pathComplete == true`;
- no plan-level or edge-level execution blockers;
- path endpoints equal `origin` and `destination`;
- edge count and `distance` match the full path;
- every edge exactly matches adjacent path states.

### Exact provenance

The preflight computes current SHA-256 values for the runtime map, World Index, appearances, and supplied optional evidence.

Every non-null evidence reference in route-plan provenance must be present and hash-identical. The runtime map must also equal the source-map SHA-256 in the exact World Index provenance manifest, and the manifest must match the exact `.widx` hash.

### Movement

Every movement edge must:

- remain on one floor;
- move by exactly one adjacent x/y step;
- obey `allowDiagonal`;
- retain `diagonalCornerCutting == false`;
- remain traceable to Reachability `_movement_neighbors` evidence.

Current physical executability, including diagonal corner tiles and unknown/conditional blockers, is rechecked by canonical Reachability regeneration rather than duplicated here.

### Transitions

Every transition edge must retain:

- one non-empty transition ID;
- exact route source and destination;
- validated transition evidence;
- exact matching embedded transition source/destination;
- `valid == true`;
- exactly one executable reviewed physical interaction.

The current canonical regenerated plan must still contain matching transition state. Changed or missing transitions produce `TRANSITION_STALE`.

### Interactions and Script Resolution

Embedded interaction resolutions must use `canary-otbm-route-interaction-resolution-v1`, be executable, have no blockers, and use one of the currently supported Universal E2E activation kinds:

```text
step-on
walk-direction
use-map-item
use-inventory-on-map
```

The static preflight also rejects embedded fail-closed script states:

```text
partially-resolved
referenced-only
unresolved
conflicting
```

The canonical route regeneration re-runs the existing interaction resolver against current exact evidence, so stale selectors or newly blocked Script Resolution evidence cannot remain silently executable.

### Semantic landmarks

When a landmark request is supplied, the existing semantic landmark resolver must still produce:

- one exact reviewed origin anchor;
- one exact reviewed destination anchor;
- one common region;
- the same routing bounds as the route plan;
- exact positions equal to route-plan `origin` and `destination`;
- exact runtime map and World Index provenance.

No landmark coordinates are guessed by this tool.

## Deterministic result

A passing result has:

```json
{
  "format": "canary-otbm-e2e-route-preflight-v1",
  "schemaVersion": 1,
  "status": "passed",
  "ok": true,
  "staticEvidenceOnly": true,
  "firstBlocker": null,
  "findings": [],
  "summary": {
    "total": 0,
    "byCode": {},
    "truncated": false
  }
}
```

A blocked result records the first deterministic blocker and a bounded ordered finding stream. `--max-findings` bounds retained samples without changing the total counts.

Representative blocker codes include:

```text
ROUTE_PLAN_INVALID
ROUTE_PLAN_HASH_MISMATCH
ROUTE_PROVENANCE_MISMATCH
ROUTE_INCOMPLETE
ROUTE_TRUNCATED
MOVEMENT_EDGE_INVALID
DIAGONAL_NOT_ALLOWED
DIAGONAL_CORNER_BLOCKED
LANDMARK_NOT_FOUND
LANDMARK_AMBIGUOUS
LANDMARK_STALE
ROUTING_REGION_INVALID
TRANSITION_STALE
SCRIPT_RESOLUTION_BLOCKED
INTERACTION_STALE
INTERACTION_UNSUPPORTED
WORLD_INDEX_MANIFEST_INVALID
ROUTE_NOT_CURRENTLY_EXECUTABLE
ROUTE_CURRENT_EVIDENCE_MISMATCH
```

## CLI

Example without semantic landmarks:

```bash
python3 tools/ai-agent/otbm_route_preflight.py \
  --route-plan /evidence/route-primary.json \
  --runtime-map /runtime/map.otbm \
  --world-index /cache/map.widx \
  --world-index-manifest /cache/map.widx.json \
  --appearances /runtime/appearances.json \
  --output /evidence/route-primary-preflight.json
```

Example with evidence referenced by an interaction-aware route:

```bash
python3 tools/ai-agent/otbm_route_preflight.py \
  --route-plan /evidence/route-primary.json \
  --runtime-map /runtime/map.otbm \
  --world-index /cache/map.widx \
  --world-index-manifest /cache/map.widx.json \
  --appearances /runtime/appearances.json \
  --transitions /evidence/transitions.json \
  --script-resolution /evidence/script-resolution.json \
  --interaction-registry docs/ai-agent/OTBM_ROUTE_INTERACTIONS.json \
  --landmark-registry docs/ai-agent/OTBM_SEMANTIC_LANDMARKS.json \
  --landmark-request /evidence/landmark-request.json \
  --output /evidence/route-primary-preflight.json
```

Exit codes:

```text
0  preflight passed
1  deterministic static blocker found
2  invalid CLI/input I/O prevented a preflight result
```

Generated `.otbm`, `.widx`, route plans, preflight results, and physical-client artifacts remain outside Git.

## Deliberate non-goals

This package does not:

- bind real `thais.temple` or `thais.depot` coordinates;
- implement OTBM-E2E-005;
- modify the Universal Physical E2E runner or workflow;
- write or repair maps;
- infer transitions from sprites or names;
- promote unresolved Script Resolution evidence to handled;
- claim runtime gameplay correctness from static evidence.
