# OTBM Route Interaction Registry

## Purpose

`canary-otbm-route-interactions-v1` is the reviewed bridge from exact OTBM mechanic or transition evidence to physical activation semantics that a later Universal Physical E2E executor may support.

It answers only:

```text
reviewed exact mechanic/transition evidence
  -> supported physical activation semantics
```

It does not execute the client, change Reachability, infer map mechanics, prove gameplay success, or make optimistic reachability executable by itself.

Schema: `docs/ai-agent/OTBM_ROUTE_INTERACTIONS.schema.json`

Committed seed: `docs/ai-agent/OTBM_ROUTE_INTERACTIONS.json`

Validator/resolver: `tools/ai-agent/otbm_route_interactions.py`

## Safety boundary

The registry is deliberately fail-closed.

- Unknown mechanics remain blocked.
- Unknown transition IDs remain blocked.
- Duplicate exact selectors are rejected.
- Overlapping selectors that both match one query resolve as ambiguous and remain blocked.
- `unresolved`, `partially-resolved`, `referenced-only` and `conflicting` Script Resolution evidence never satisfies a handler-gated interaction.
- A successful static interaction resolution is not runtime gameplay proof.
- The resolver does not parse OTBM, build another World Index, run another pathfinder, execute Lua or call the physical client.

`OTBM-E2E-001B` is responsible for later reusing the existing Reachability `_bfs()` with an executable predicate. This registry does not add a second BFS/A*/Dijkstra implementation.

## Registry state

The committed registry is intentionally:

```json
{
  "format": "canary-otbm-route-interactions-v1",
  "schemaVersion": 1,
  "registryStatus": "unbound",
  "provenance": null,
  "entries": []
}
```

An `unbound` registry cannot resolve executable interactions.

A `reviewed` registry must pin exact source-map and World Index SHA-256 provenance. It may also pin transition-manifest and Script Resolution SHA-256 provenance when those evidence sources are required by entries.

## Selectors

### Stable transition selector

Use a stable reviewed transition ID:

```json
{
  "transitionId": "teleport:fixture"
}
```

The entry must also constrain allowed transition kinds and evidence sources. Example engine teleport semantics:

```json
{
  "id": "fixture.teleport-step-on",
  "selector": {
    "transitionId": "teleport:fixture"
  },
  "activation": {
    "kind": "step-on"
  },
  "requirements": {
    "transitionKinds": ["teleport"],
    "transitionEvidenceSources": ["worldIndex"],
    "scriptResolution": {
      "required": false,
      "allowedStatuses": []
    }
  },
  "evidence": {
    "status": "reviewed",
    "references": ["review-record:engine-teleport"]
  }
}
```

This can resolve only when the caller presents the same transition ID, an allowed transition kind and an allowed transition evidence source.

### Exact mechanic selector

Use exact position plus at least one mechanic identifier:

```json
{
  "position": [100, 100, 7],
  "itemId": 1234,
  "actionId": 45001
}
```

A position by itself is too broad and is rejected.

Supported exact mechanic fields are:

- `itemId`;
- `actionId`;
- `uniqueId`;
- `houseDoorId`.

The resolver requires every field declared by the selector to match the caller's exact evidence.

## Activation vocabulary

The v1 activation kinds are:

- `step-on`;
- `walk-direction`;
- `use-map-item`;
- `use-inventory-on-map`.

`step-on` and `walk-direction` require a transition selector.

For map-targeting activations, `target` is one of:

- `transition-source` for transition selectors;
- `selector-position` for exact mechanic selectors;
- `explicit-position` with an explicit `targetPosition`.

`use-inventory-on-map` additionally requires an exact `inventoryItemId`.

These values define static physical intent only. The maintained OTClient API and Universal E2E action support must still be verified by the later E2E implementation task.

## Script Resolution integration

Each entry contains:

```json
{
  "scriptResolution": {
    "required": true,
    "allowedStatuses": ["handled-by-action-id"]
  }
}
```

When `required` is `true`:

1. the reviewed registry must pin a Script Resolution SHA-256;
2. the caller must provide the exact expected Script Resolution SHA-256;
3. the caller must provide the exact placement/runtime `scriptStatus`;
4. that status must be explicitly listed in `allowedStatuses`.

The registry permits only runtime-handled statuses in `allowedStatuses`:

```text
handled-directly
handled-by-range
handled-generically
handled-by-item-id
handled-by-action-id
handled-by-unique-id
handled-by-position
handled-as-target
handled-by-fallback
handled-by-engine
handled-multiple
```

The following remain fail-closed and cannot be whitelisted:

```text
partially-resolved
referenced-only
unresolved
conflicting
```

This preserves the existing Script Resolution rule:

```text
unresolved != handled
conflicting != executable
```

## Reviewed transition manifest integration

An entry whose `transitionEvidenceSources` includes `transitionManifest` requires the reviewed registry to pin the exact transition-manifest SHA-256.

For executable resolution using that source, the caller must also provide the exact expected transition-manifest SHA-256. Missing or stale evidence blocks or rejects resolution before physical execution.

World-Index-backed engine teleports may instead use `worldIndex` as their reviewed transition evidence source and do not require Script Resolution when no handler correlation is part of the mechanic.

## Resolution result

The resolver emits `canary-otbm-route-interaction-resolution-v1`.

Successful example:

```json
{
  "format": "canary-otbm-route-interaction-resolution-v1",
  "schemaVersion": 1,
  "executionStatus": "executable",
  "matchedEntryId": "fixture.teleport-step-on",
  "matchedEntryIds": ["fixture.teleport-step-on"],
  "selectorQuery": {
    "transitionId": "teleport:fixture",
    "transitionKind": "teleport",
    "transitionEvidenceSource": "worldIndex"
  },
  "activation": {
    "kind": "step-on"
  },
  "evidence": {
    "status": "reviewed",
    "references": ["review-record:engine-teleport"]
  },
  "blockers": []
}
```

Blocked results use `executionStatus: blocked`, omit executable activation by setting `activation` to `null`, and provide deterministic blocker codes such as:

- `interaction-not-reviewed`;
- `interaction-selector-ambiguous`;
- `transition-kind-required`;
- `transition-kind-not-allowed`;
- `transition-evidence-source-required`;
- `transition-evidence-source-not-allowed`;
- `transition-manifest-provenance-required`;
- `script-resolution-provenance-required`;
- `script-status-required`;
- `script-status-fail-closed`;
- `script-status-not-allowed`.

## CLI

Validate the committed unbound seed:

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_route_interactions.py validate \
  docs/ai-agent/OTBM_ROUTE_INTERACTIONS.json
```

A reviewed registry can be validated against exact evidence pins:

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_route_interactions.py validate \
  /path/to/reviewed-route-interactions.json \
  --require-reviewed \
  --map-sha256 <sha256> \
  --world-index-sha256 <sha256> \
  --transition-manifest-sha256 <sha256> \
  --script-resolution-sha256 <sha256>
```

Resolve a reviewed engine teleport interaction:

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_route_interactions.py resolve \
  /path/to/reviewed-route-interactions.json \
  --map-sha256 <sha256> \
  --world-index-sha256 <sha256> \
  --transition-id teleport:fixture \
  --transition-kind teleport \
  --transition-evidence-source worldIndex
```

Generated resolution reports are evidence artifacts and must not be committed as map/runtime truth.

## Relationship to route-plan v1

`canary-otbm-e2e-route-plan-v1` remains the canonical full edge-aware route export from the existing Reachability predecessor graph.

This interaction registry is a later evidence input. It does not change the route-plan status or distance and does not alter the predecessor graph.

The intended later pipeline remains:

```text
World Index
  -> existing Reachability graph
  -> existing _bfs/predecessor map
  -> canary-otbm-e2e-route-plan-v1
  -> reviewed route interaction resolution
  -> later executable interaction-aware routing/preflight
  -> existing Universal Physical E2E
```
