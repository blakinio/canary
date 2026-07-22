# OTBM Dead/Orphaned Content and Completeness Audit

`OTBM-QA-009` adds a deterministic read-only selected-scope audit over already-delivered QA-008 dependency evidence and QA-005 coverage evidence.

It answers bounded questions such as:

- does a reviewed quest/mechanic target have explicit evidence for its declared stages;
- which required stages are confirmed, partial, unresolved or conflicting;
- does an explicitly reviewed placement/handler/storage/transition/access node have the reviewed counterpart relationship expected inside the selected graph;
- where does exact evidence stop.

It does **not** discover quest topology, execute scripts, prove runtime completion or declare content globally dead.

## Contracts

- reviewed input: `canary-otbm-content-completeness-manifest-v1`
- generated output: `canary-otbm-content-completeness-audit-v1`

Generated reports remain external artifacts and are not committed.

## Required evidence

The CLI requires:

1. one reviewed completeness manifest;
2. one `canary-otbm-dependency-blast-radius-v1` QA-008 report;
3. one `canary-otbm-coverage-dashboard-v1` QA-005 report.

All three must pin the same current map SHA-256 and World Index SHA-256. Mismatch fails closed.

## Reviewed targets and stages

Supported target kinds are `quest` and `mechanic-set`.

A target declares explicit stages. Supported stage roles are:

- `entry`;
- `npc-source-trigger`;
- `storage-prerequisite` and `storage-result`;
- `mechanic`, `door`, `lever`, `passage`;
- `teleport`, `transition`;
- `boss`, `spawn`;
- `reward`;
- `exit`, `return`.

A stage may bind any combination of:

- exact QA-008 dependency node IDs;
- exact QA-005 target/dimension requirements;
- one existing QA-008 query plus exact target node IDs that must already appear among that query's roots or transitive impacts.

The audit never reruns QA-008 graph traversal. It only consumes the query result already present in the supplied report.

## Classifications

The report preserves explicit classifications:

- `confirmed`;
- `map-only`;
- `script-only`;
- `unresolved`;
- `conflicting`;
- `not-applicable`.

A required stage is satisfied only when its composed evidence is `confirmed`.

Unproven path evidence is `unresolved`; it is not proof that gameplay is impossible. Stale or conflicting coverage evidence remains `conflicting`.

`requirementsSatisfied` is a selected-scope static convenience boolean. Every target also states `runtimeGameplayCompletionProven=false`.

## Orphan/disconnection checks

A reviewed target may declare exact checks over one QA-008 node. Each check explicitly states:

- the node ID;
- incoming, outgoing or either direction;
- allowed QA-008 relations;
- allowed counterpart node kinds;
- the classification to use only when no matching selected-scope edge exists;
- one bounded finding kind.

Supported finding kinds include placement-without-handler, handler-without-placement, unreachable-transition, disconnected spawn/NPC, storage producer/consumer gap, missing route/interaction evidence and disconnected access context.

A proven matching edge means the check is confirmed. If a matching QA-008 edge exists but is unresolved, the result remains `unresolved` or `conflicting`; the audit never converts that boundary into `map-only` or `script-only` merely because the edge is not proven.

An explicit `map-only` or `script-only` finding is therefore permitted only by the reviewed check's missing-side classification when no matching selected-scope dependency edge exists at all.

This remains selected-scope evidence. Missing edges outside the supplied reviewed QA-008 graph are unknown, not globally absent.

## CLI

```sh
python tools/ai-agent/otbm_content_completeness_tool.py \
  --manifest artifacts/content-completeness-manifest.json \
  --dependency-graph artifacts/dependency-blast-radius.json \
  --coverage-dashboard artifacts/coverage-dashboard.json \
  --output artifacts/content-completeness-audit.json
```

The CLI rejects symlinks, duplicate inputs, input/output collisions and files larger than 256 MiB. It hashes inputs before and after parsing, creates new output by default and requires `--overwrite` for atomic replacement.

## Ownership boundaries

This layer never:

- parses or scans OTBM;
- builds a World Index;
- reruns Script Resolution;
- rebuilds the Storage Dependency Graph;
- executes Reachability/pathfinding;
- recomputes QA-008 dependencies or blast radius;
- executes dynamic Lua;
- executes Physical E2E;
- mutates a map;
- assigns QA-006 certification;
- directs repair or scenario prioritization.

Runtime quest completion and feature-specific gameplay acceptance remain owned by Universal E2E and the relevant subsystem.
