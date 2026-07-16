# OTBM static map quality gate

## Purpose

`tools/ai-agent/otbm_map_quality_tool.py` is a read-only static quality gate over existing OTBM evidence. It does not parse or scan an OTBM itself. Version 1 consumes exactly three already-generated reports:

1. `canary-otbm-geometry-audit-v1`;
2. `canary-otbm-reachability-v1`;
3. `canary-otbm-script-resolution-v1`.

The gate answers a narrower question than gameplay E2E:

> For one cryptographically proven map source, what static geometry, reachability and runtime-resolution evidence is currently classified as error, warning, unresolved or informational?

A green report is not proof that a player can complete every quest or that map content matches designer intent or Real Tibia.

## Safety boundary

The quality gate:

- never opens or parses an `.otbm`;
- never builds another map scanner or World Index;
- never modifies maps, `.widx` files, datapacks, scripts or assets;
- consumes only existing versioned evidence contracts;
- requires all three component reports to prove the same map SHA-256;
- hashes and pins each input report before aggregation;
- rejects symlink inputs and report/source output collisions;
- checks each input file is stable while being read;
- creates a new output with exclusive no-clobber semantics unless `--overwrite` is explicit;
- never infers gameplay correctness, player intent or global map coverage.

Generated reports are artifacts and must not be committed.

## Source identity

Aggregation fails closed unless the same lowercase SHA-256 is available at the exact supported provenance path for every component:

| Component | Required map identity |
|---|---|
| Geometry Audit | `provenance.source.sha256` |
| Reachability | `provenance.worldIndexManifest.source.sha256` |
| Script Resolution | `sources.itemAudit.map.sha256` |

The gate does not recursively search arbitrary JSON fields for a plausible hash. Missing or mismatched provenance is an input error, not an unresolved quality finding.

This means a reachability report built without a World Index manifest cannot be combined into v1, even when its `.widx` hash is known: the gate requires explicit evidence tying that index back to the source map.

## Outcome model

The normalized outcomes are intentionally separate:

- `error` — component evidence already classifies a concrete error, or Script Resolution reports a conflicting placement;
- `warning` — component evidence already classifies a warning;
- `unresolved` — Script Resolution reports `unresolved`, `referenced-only` or `partially-resolved` runtime evidence;
- `info` — component evidence already classifies an informational finding.

The gate does not turn a reviewed unresolved identifier into handled evidence. Review disposition and runtime resolution remain separate.

Geometry and Reachability severities are preserved as emitted by their existing contracts. The quality gate does not reinterpret an orphan candidate, one-way transition, conditional route or other component finding as a stronger gameplay defect.

## Counts and samples

Exact aggregate counts come from the component summaries:

- Geometry: `summary.findings.bySeverity`;
- Reachability: `summary.findings.bySeverity`;
- Script Resolution: `summary.conflictingPlacements` and `summary.runtimeUnresolvedPlacements`.

The `findings` array is only a deterministic bounded sample. Component reports may already contain truncated finding samples; therefore the quality gate never derives exact totals from array length.

Normalized sample order is deterministic:

1. outcome: `error`, `warning`, `unresolved`, `info`;
2. component: Geometry, Reachability, Script Resolution;
3. position `(z,y,x)` when available;
4. kind and deterministic finding ID.

`summary.total` is the sum of component evidence events. Version 1 deliberately does **not** deduplicate findings across components into inferred root causes. A geometry error and a reachability error at the same tile remain two evidence events.

## Coverage

Geometry and Reachability are bounded analyses. Their exact scopes are retained under `coverage`.

- `sameRegion: true` means the two bounded region objects are equal;
- `sameRegion: false` means they differ;
- `globalCoverageProven` is always `false` in v1.

Script Resolution may cover the full item-audit mechanic placement set, but that does not promote bounded Geometry/Reachability evidence into a global map-quality proof.

## Gate policy

`--fail-on-severity` controls only severity outcomes:

- `none` — errors and warnings do not make `ok` false;
- `error` — default; one or more errors make `ok` false;
- `warning` — errors or warnings make `ok` false.

`--fail-on-unresolved` is independent. When supplied, one or more unresolved outcomes also make `ok` false.

The policy changes only the gate result. It never changes or suppresses evidence classification.

## Run

```bash
python tools/ai-agent/otbm_map_quality_tool.py \
  --geometry /external/artifacts/OTBM_GEOMETRY_AUDIT.json \
  --reachability /external/artifacts/OTBM_REACHABILITY.json \
  --script-resolution /external/artifacts/OTBM_SCRIPT_RESOLUTION.json \
  --output /external/artifacts/OTBM_MAP_QUALITY.json \
  --fail-on-severity error
```

For a stricter static gate:

```bash
python tools/ai-agent/otbm_map_quality_tool.py \
  --geometry /external/artifacts/OTBM_GEOMETRY_AUDIT.json \
  --reachability /external/artifacts/OTBM_REACHABILITY.json \
  --script-resolution /external/artifacts/OTBM_SCRIPT_RESOLUTION.json \
  --output /external/artifacts/OTBM_MAP_QUALITY_STRICT.json \
  --fail-on-severity warning \
  --fail-on-unresolved
```

Exit code is zero when the generated report has `ok: true`; policy failures return 2 after publishing the factual report. Invalid/mismatched inputs also fail with a nonzero CLI exit and do not publish a quality report.

Existing output requires explicit `--overwrite`. Without it, final publication uses exclusive creation, so a file appearing after initial path validation is not replaced.

## Report contract

Format:

```text
canary-otbm-map-quality-v1
```

Normative schema:

```text
docs/ai-agent/OTBM_MAP_QUALITY_GATE.schema.json
```

The report includes:

- exact common source map SHA-256;
- report-file pins for every component;
- component formats and original `ok`/completeness evidence;
- separate exact `error`, `warning`, `unresolved` and `info` counts;
- bounded deterministic normalized finding samples with original component evidence embedded;
- bounded Geometry/Reachability coverage;
- explicit read-only/no-independent-parser/no-gameplay-proof policy fields.

## Deliberate v1 exclusions

The following are not silently folded into v1:

- Quest Map Validator;
- Spawn/NPC Validator;
- Storage dependency graph;
- donor-map comparison or region import;
- Phase 8 patch execution;
- server-side gameplay scenarios;
- physical-client E2E.

Quest and Spawn/NPC reports use selected source and scope semantics that need explicit adapter compatibility rules before their findings can be aggregated without overclaiming coverage.

A future repair sandbox verifier should consume this quality gate after applying an existing reviewed Phase 8 plan to a distinct temporary/copy map. That verifier remains a separate bounded task and must prove the original source map is unchanged.

## Tests

```bash
python -m unittest tools/ai-agent/test_otbm_map_quality.py -v
python -m unittest tools/ai-agent/test_otbm_map_quality_output_safety.py -v
```

Focused coverage includes:

- same-map SHA enforcement;
- missing provenance rejection;
- exact counts independent of truncated component samples;
- unresolved preservation;
- independent severity/unresolved gate policy;
- deterministic finding ordering;
- explicit bounded-region mismatch;
- input report pins;
- output/input collision rejection;
- create-new no-clobber publication and explicit overwrite behavior.
