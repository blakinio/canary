# OTBM quest state reachability

## Purpose

`OTBM-QA-010` derives a conservative static state-transition view for explicitly selected quest or mechanic scopes.

It composes two already-delivered contracts:

- `canary-otbm-storage-graph-v1` for exact same-key storage transitions already proven by the canonical Storage Dependency Graph;
- `canary-otbm-route-interactions-v1` for reviewed physical interaction semantics when a selected transition requires an explicit interaction gate.

It does not parse Lua, rescan OTBM, rebuild the Storage Dependency Graph, infer callback order, run a pathfinder or execute gameplay.

Public formats:

```text
canary-otbm-quest-state-reachability-manifest-v1
canary-otbm-quest-state-reachability-v1
```

Entrypoints:

- `tools/ai-agent/otbm_quest_state_reachability.py`
- `tools/ai-agent/otbm_quest_state_reachability_tool.py`
- `docs/ai-agent/OTBM_QUEST_STATE_REACHABILITY_MANIFEST.schema.json`
- `docs/ai-agent/OTBM_QUEST_STATE_REACHABILITY.schema.json`

## Evidence model

The tool starts only from explicit initial states declared by the reviewed manifest.

A selected edge is not invented by QA-010. Its `transitionId` must already exist in the supplied complete Storage Graph and therefore already obey the Storage Graph exact-transition rule:

```text
same namespace/key
+ exact prerequisite operator ==
+ exact literal/delete/same-key delta result
= canonical static transition evidence
```

QA-010 then applies additional selected-scope evidence gates before traversing that edge:

```text
known reachable state
+ exact existing Storage Graph transition
+ exact expected map context and/or reviewed Route Interaction resolution
-> proven selected transition
-> newly reachable static state
```

A selected transition must declare at least one of:

- non-empty `mapContextExpected` evidence that must occur exactly in the existing transition `mapContext`; or
- an `interaction` query resolved by the existing Route Interaction Registry resolver.

This prevents QA-010 from turning a bare storage write into an inferred playable quest step.

## Manifest

A minimal selected target looks like:

```json
{
  "format": "canary-otbm-quest-state-reachability-manifest-v1",
  "schemaVersion": 1,
  "source": {
    "mapSha256": "<64 hex>",
    "worldIndexSha256": "<64 hex>"
  },
  "targets": [
    {
      "id": "quest.example",
      "kind": "quest",
      "reason": "Reviewed selected quest state chain",
      "initialStates": [
        {
          "namespace": "player-storage",
          "key": "Storage.Quest.Example.Stage",
          "value": 0
        }
      ],
      "transitions": [
        {
          "transitionId": "<existing Storage Graph transition id>",
          "mapContextExpected": [
            {
              "position": [100, 100, 7],
              "actionId": 45001
            }
          ],
          "interaction": null
        }
      ],
      "goals": [
        {
          "id": "stage-one",
          "namespace": "player-storage",
          "key": "Storage.Quest.Example.Stage",
          "value": 1
        }
      ]
    }
  ]
}
```

The manifest is a reviewed selected-scope contract. It does not expand source discovery or authorize a global quest claim.

## Exact map-context gating

`mapContextExpected` uses exact object equality against the selected Storage Graph transition's existing `mapContext` entries.

When map-context evidence is required, the Storage Graph must also retain a non-null `questValidation` input pin. Missing provenance or a missing expected context blocks the transition.

QA-010 does not reinterpret nearby coordinates, item names, source lines or visual similarity.

## Route Interaction reuse

An interaction-gated transition uses the existing `resolve_interaction(...)` implementation from `otbm_route_interactions.py`.

Example manifest fragment:

```json
{
  "interaction": {
    "query": {
      "position": [100, 100, 7],
      "actionId": 45001,
      "scriptStatus": "handled-by-action-id"
    },
    "expectedScriptResolutionSha256": "<64 hex>"
  }
}
```

The manifest's `source.mapSha256` and `source.worldIndexSha256` are supplied as exact expectations to the reviewed interaction registry. Optional transition-manifest and Script Resolution SHA-256 expectations are forwarded unchanged.

The Route Interaction Registry remains authoritative for:

- selector matching;
- ambiguity detection;
- supported activation semantics;
- transition-kind/evidence-source requirements;
- fail-closed Script Resolution statuses.

QA-010 does not copy or weaken those rules.

## Goal classifications

Each declared goal receives exactly one classification:

- `reachable` — a fully proven selected transition chain reaches the exact state from a declared initial state;
- `blocked-by-evidence` — the selected structural chain exists, but one or more map/interaction evidence gates are blocked;
- `unreachable-in-selected-scope` — the selected scope contains a producer for the state, but no predecessor path from declared initial states can be proven even when considering the selected transitions structurally;
- `external-or-unproven` — the selected scope contains no producer for the goal and the goal is not an initial state.

`unreachable-in-selected-scope` is not a global impossibility claim. `external-or-unproven` explicitly preserves the possibility of initialization or progression from another quest, migration, runtime system or source set not selected by the manifest.

The report also exposes `externalPrerequisites` for consumed predecessor states that are not reachable and have no selected producer.

## Runtime boundary

The report always keeps:

```text
runtimeGameplayCompletionProven = false
runtimeGameplayCompletionClaimed = false
globalImpossibilityClaimed = false
```

A green static result proves only that the selected exact state chain is statically supported by the supplied evidence. It does not prove:

- Lua callback execution order;
- current player/account/global values;
- transaction or concurrency behavior;
- client interaction success;
- successful quest completion at runtime.

Physical E2E remains a separate proof layer.

## CLI

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_quest_state_reachability_tool.py \
  --manifest /tmp/OTBM_QUEST_STATE_REACHABILITY_MANIFEST.json \
  --storage-graph /tmp/OTBM_STORAGE_GRAPH.json \
  --route-interactions /tmp/OTBM_ROUTE_INTERACTIONS.json \
  --output /tmp/OTBM_QUEST_STATE_REACHABILITY.json
```

`--route-interactions` is optional only when no selected transition declares an interaction requirement.

The CLI rejects:

- symlink inputs or outputs;
- duplicate input files;
- input/output collisions and hard-link collisions;
- oversized inputs;
- output clobber unless `--overwrite` is explicit.

Create-new output is the default; overwrite uses atomic replacement.

## Non-goals

QA-010 does not:

- build another OTBM parser, scanner or World Index;
- rebuild or broaden Storage Graph source selection;
- infer transitions from inequalities, `else`, lexical proximity or callback proximity;
- execute dynamic Lua;
- run Script Resolution itself;
- run Reachability/BFS or create a route planner;
- mutate maps or datapacks;
- direct repair or Physical E2E prioritization;
- assign certification or gameplay correctness.
