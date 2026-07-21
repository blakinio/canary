# OTBM World Health Aggregator

## Purpose

`OTBM-QA-001` adds one deterministic, read-only aggregation layer over already-produced OTBM evidence.

It answers a narrower question than any individual validator:

> For one exact source map, what health evidence is currently available, what explicit problem/uncertainty dimensions does it contain, and which parts remain stale, unreachable/conditional or physically unproven?

The aggregator does **not** parse or scan OTBM, rebuild the Unified World Index, resolve Lua/XML handlers, run pathfinding, execute Lua, mutate maps, render maps or run Physical E2E. Those responsibilities stay with the existing canonical tools.

## Contract

Output format:

```text
canary-otbm-world-health-v1
```

Schema:

```text
docs/ai-agent/OTBM_WORLD_HEALTH.schema.json
```

Generated world-health JSON is an external evidence artifact and must not be committed to Git.

## Current v1 inputs

The smallest complete v1 composes three already-delivered evidence surfaces:

1. exactly one required `canary-otbm-map-quality-v1` report;
2. zero or more `canary-otbm-reachability-v1` reports for explicit bounded regions;
3. zero or more `canary-otbm-e2e-coverage-matrix-v1` reports for reviewed mechanic target sets.

This slice deliberately reuses Map Quality as the structural/runtime-handler summary boundary instead of reopening Geometry Audit or Script Resolution semantics. Direct Reachability reports add explicit route/transition/mechanic state totals. Coverage matrices add stale-provenance and missing-Physical-E2E dimensions.

Future roadmap inputs such as Quest Map Validation, Spawn/NPC validation or Storage dependency evidence may be added only as new explicit compatible adapters. They must not be silently inferred from names, nearby positions, sprites or unrelated report absence.

## Exact provenance rules

Every accepted input report is pinned by:

- file name;
- byte size;
- SHA-256;
- exact report format.

The required Map Quality report establishes the exact source-map SHA-256.

Every direct Reachability report must additionally provide:

- `provenance.worldIndex.sha256`;
- `provenance.worldIndexManifest.source.sha256` equal to the Map Quality source-map SHA-256;
- `provenance.worldIndexManifest.index.sha256` equal to the Reachability World Index SHA-256.

Every coverage matrix must provide `currentMap.mapSha256` equal to the same source map and `currentMap.worldIndexSha256` equal to the same World Index used by any direct Reachability evidence.

Mismatched, missing or malformed provenance fails closed. Duplicate contributing report SHA-256 pins are rejected.

When neither direct Reachability nor coverage-matrix evidence is supplied, `source.worldIndexSha256` is `null`; the report does not invent a World Index identity from Map Quality.

## Health dimensions

### Structural

Derived from the existing Map Quality `geometry` and `reachability` component outcome totals.

The aggregator sums those exact component counts by:

- `error`;
- `warning`;
- `unresolved`;
- `info`.

It does not deduplicate a Geometry finding and a Reachability finding into an invented shared defect.

### Runtime handlers

Derived from the existing Map Quality `scriptResolution` component.

The dimension preserves:

- exact placement finding outcome totals;
- conflicting placements;
- unresolved placements;
- unreviewed identifiers;
- unresolved dynamic registrations.

`unresolved`, `partially-resolved`, `referenced-only` and equivalent unresolved evidence remain unresolved. The aggregator never promotes them to handled.

### Reachability

Derived from explicit direct Reachability reports.

The dimension preserves report-summed exact totals and status counts for:

- routes;
- transitions;
- mechanics;
- tile-status evidence;
- one-way transitions;
- dead-end transitions;
- transition loops.

`attentionTotal` is the deterministic sum of `conditional` plus `unreachable` mechanic counts. It is a presentation count, not a new inferred failure class.

Reachability is static evidence. Optimistic/conditional or even confirmed static reachability is not Physical E2E proof.

### Stale evidence

Derived from coverage-matrix targets whose `staleAgainstCurrentMapProvenance` is explicitly `true`.

The aggregator checks that the matrix summary count matches the target-level evidence. It does not infer staleness from timestamps or filenames.

### Missing Physical E2E coverage

Derived from explicit coverage-matrix target state.

The dimension keeps separate counts for:

- targets with `missingPhysicalScenario=true`;
- targets without Physical E2E runtime proof on the current exact map.

A missing scenario or missing current-map runtime proof is a **coverage gap**, not proof that the mechanic is broken. OTBM reports this evidence to downstream owners; it does not define or prioritize a feature-specific E2E scenario.

## Totals, samples and boundedness

Source summaries remain authoritative for exact totals where the source contract exposes exact totals.

World Health emits deterministic bounded samples for inspection. Sample ordering is stable and independent of input argument order.

Two truncation signals remain distinct:

- `outputSampleTruncated`: World Health applied its own sample limit;
- `sourceEvidenceTruncated`: the contributing source report itself declared incomplete sampled evidence.

`truncated` is true when either condition applies.

A truncated source sample never causes the aggregator to reduce an exact source summary total.

Reports from multiple explicit regions or target sets are summed as separate evidence events. Cross-report and cross-dimension deduplication is intentionally disabled because there is no evidence-backed identity contract authorizing such deduplication.

## Scope and absence semantics

`globalCoverageProven` is always `false` in v1.

This is intentional. Map Quality and Reachability inputs may be bounded, and coverage matrices cover reviewed target sets rather than the entire world.

Therefore:

- zero findings in a selected region does not prove zero findings globally;
- no Reachability input means no direct Reachability evidence was supplied, not that everything is reachable;
- no coverage matrix means no reviewed Physical E2E coverage evidence was supplied, not that all mechanics are covered;
- missing Physical E2E evidence does not prove gameplay failure.

## No opaque health score

V1 deliberately emits no single health percentage or opaque score:

```text
policy.healthScoreEmitted = false
```

Future presentation layers may derive a convenience score only if they expose deterministic inputs. Such a score must never replace the explicit evidence dimensions or become the sole merge/certification gate.

## CLI

```bash
python tools/ai-agent/otbm_world_health_tool.py \
  --map-quality /evidence/map-quality.json \
  --reachability /evidence/reachability-thais.json \
  --reachability /evidence/reachability-quest-region.json \
  --coverage-matrix /evidence/e2e-coverage.json \
  --sample-limit 500 \
  --output /evidence/world-health.json
```

`--reachability` and `--coverage-matrix` are repeatable and optional. `--map-quality` is required.

Use `--overwrite` only for an intentional replacement. Without it, output uses create-new semantics and refuses an existing destination.

The CLI also:

- rejects symlink inputs and symlink outputs;
- rejects an output that aliases an input;
- rejects duplicate resolved input paths;
- caps each input report at 256 MiB;
- detects an input changing while it is read;
- SHA-pins every contributing input;
- writes create-new output with exclusive creation where supported;
- uses atomic replacement for explicit overwrite.

Invalid/incompatible input is a fail-closed CLI error. A successfully generated report returns exit code `0`; the report itself is evidence aggregation, not a gameplay pass/fail verdict.

## Architecture boundary

World Health reuses the delivered OTBM stack and preserves ownership:

- Unified OTBM World Index remains the only canonical index;
- OTBM Reachability remains the only canonical pathfinder/BFS;
- Script Resolution remains the only runtime-handler correlation engine;
- Map Quality remains the static quality aggregation boundary used by this v1 slice;
- OTBM-E2E coverage remains the source of Physical E2E coverage/staleness state;
- Universal E2E retains scenario definitions, fixture design, client/server lifecycle, execution, runtime assertions, persistence/relog behavior and feature-acceptance decisions.

This package adds no parser, scanner, resolver, pathfinder, renderer, writer/materializer, E2E runner or workflow.
