# OTBM Dependency and Blast-Radius Graph

`OTBM-QA-008` adds a deterministic read-only overlay that answers one narrow question:

> Given explicitly reviewed dependency nodes and directed edges, which reviewed targets are directly or transitively impacted by a reviewed change root, and where does exact evidence stop?

The tool does **not** discover dependencies. It validates reviewer-declared nodes and edges against exact supplied evidence and computes graph reachability only across edges whose evidence is current and proven.

## Contracts

- reviewed input: `canary-otbm-dependency-graph-manifest-v1`
- generated output: `canary-otbm-dependency-blast-radius-v1`

Generated reports remain artifacts and are not committed.

## Required evidence

The CLI requires:

1. one reviewed dependency manifest;
2. one compatible `canary-otbm-world-health-v1` report;
3. one compatible `canary-otbm-map-change-regression-v1` report.

An exact compatible `canary-otbm-coverage-dashboard-v1` report is optional.

The World Health source map must equal the Regression Guard `afterMapSha256`. If World Health carries a World Index SHA, it must equal the Regression Guard `afterWorldIndexSha256`. An optional Coverage Dashboard must prove that same current map and World Index.

## Reviewed graph model

Supported v1 node kinds are:

- `tile`;
- `item`;
- `mechanic`;
- `action-id`;
- `unique-id`;
- `house-door`;
- `teleport`;
- `transition`;
- `script-handler`;
- `storage`;
- `landmark`;
- `route`;
- `quest`;
- `coverage-target`;
- `scenario`.

Every directed edge explicitly states `source`, `target` and one reviewed relation. Direction is the blast-radius direction: when the source node is a proven root or proven impact, the target may be impacted only when the edge itself is proven.

The graph does not infer edges from names, map proximity, sprites, source proximity, route similarity or chat history.

## Exact evidence references

Every node and edge carries zero or more evidence references:

```json
{
  "reportSha256": "<exact supplied report SHA-256>",
  "pointer": "/impactEvidence/sampledMechanics/0",
  "expectation": {
    "mode": "subset",
    "value": {
      "kind": "action-id-changed"
    }
  }
}
```

Evidence resolution is limited to the exact SHA-pinned reports supplied to the invocation.

`pointer` uses RFC 6901 JSON Pointer syntax. Optional expectation modes are:

- `equals` — resolved evidence must exactly equal the supplied value;
- `subset` — every key/value in the supplied object must recursively exist with the same value in the resolved object.

A missing report SHA, invalid/missing pointer, expectation mismatch, missing evidence list, ambiguous review state, or unproven endpoint makes the node/edge `unresolved`. It is not traversed as a proven dependency.

## Blast-radius queries

A manifest contains explicit query roots. For every query the output provides:

- proven and unresolved roots;
- direct proven impacts;
- all transitive proven impacts;
- deterministic shortest `pathNodeIds` and `pathEdgeIds`;
- unresolved outgoing boundaries encountered from the proven reachable subgraph.

Traversal is deterministic and cycle-safe. Proven cycles do not create repeated results. Unresolved edges are surfaced but never crossed.

A blast-radius result is bounded to the explicit reviewed graph and supplied evidence. Absence from the graph is never proof of global non-impact.

## CLI

```sh
python tools/ai-agent/otbm_dependency_graph_tool.py \
  --manifest artifacts/dependency-manifest.json \
  --world-health artifacts/world-health.json \
  --regression-guard artifacts/map-change-regression.json \
  --coverage-dashboard artifacts/coverage-dashboard.json \
  --output artifacts/dependency-blast-radius.json
```

`--coverage-dashboard` is optional.

The CLI:

- rejects symlink inputs/output;
- caps each input at 256 MiB;
- hashes each input before and after parsing and rejects read-time changes;
- rejects duplicate input files and output/input collisions;
- creates a new output by default;
- requires `--overwrite` for atomic replacement of an existing report.

## Ownership boundaries

This layer never:

- parses or scans OTBM;
- builds a World Index;
- reruns Script Resolution;
- reconstructs the Storage Dependency Graph;
- pathfinds or plans routes;
- recomputes Semantic Diff or OTBM-E2E-008 selection;
- executes Physical E2E;
- mutates a map;
- assigns QA-006 certification;
- prioritizes downstream scenarios.

Reuse the canonical World Index, Script Resolution, Storage Dependency Graph, Reachability, Semantic Diff, QA-001/002/005 and Universal E2E contracts for those responsibilities.
