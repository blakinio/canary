# OTBM Coverage Dashboard and Evidence Model

`OTBM-QA-005` adds a deterministic read-only coverage dashboard over explicitly reviewed targets and already-delivered OTBM evidence.

Public contracts:

- reviewed targets: `canary-otbm-coverage-dashboard-targets-v1`;
- dashboard report: `canary-otbm-coverage-dashboard-v1`;
- target schema: `docs/ai-agent/OTBM_COVERAGE_DASHBOARD_TARGETS.schema.json`;
- report schema: `docs/ai-agent/OTBM_COVERAGE_DASHBOARD.schema.json`;
- implementation: `tools/ai-agent/otbm_coverage_dashboard.py`;
- CLI: `tools/ai-agent/otbm_coverage_dashboard_tool.py`.

## Purpose

The dashboard answers a narrower question than formal certification:

> For this explicitly reviewed target, which independent coverage dimensions are actually proven by current compatible evidence, which are blocked or stale, and which have not been evaluated?

It does not assign the QA-006 C0-C7 certification levels.

The required base evidence is:

```text
reviewed dashboard targets
  + current OTBM-E2E Coverage Matrix
  + compatible Map Quality report
  + compatible World Health report
  + optional exact Quest Map Validation reports
  + optional exact executable route plans
  + optional exact QA-004 reviewed candidate repair reports
  -> factual coverage dashboard
```

The dashboard never recomputes those inputs.

## Reviewed target kinds

The target manifest supports:

- `world` — the complete reviewed mechanic population present in the supplied Coverage Matrix;
- `region` — only reviewed Coverage Matrix mechanics whose exact selector positions fall inside the explicit inclusive region;
- `landmark-route` — explicit reviewed Coverage Matrix mechanic IDs plus optional exact route evidence;
- `quest` — explicit reviewed Coverage Matrix mechanic IDs plus optional exact Quest Map Validation evidence IDs;
- `mechanic-set` — an explicit reviewed set of Coverage Matrix mechanic IDs.

A `world` target is **not** proof that every mechanic in the OTBM has been enumerated. Its population is exactly the reviewed Coverage Matrix population. The report always retains `globalMapMechanicCoverageProven=false` for that population.

A `region` target does not infer mechanics from item names, visual appearance or proximity. It uses only exact selector positions already present in the Coverage Matrix.

Other target kinds require explicit mechanic IDs. Unknown IDs fail closed.

## Independent evidence dimensions

Every dashboard target retains separate states for:

- `indexedOnExactMap`;
- `sourceCorrelated`;
- `scriptResolved`;
- `staticallyReachable`;
- `interactionResolved`;
- `staticQualityCompatible`;
- `executableRouteCovered`;
- `physicallyRuntimeProven`;
- `candidateMapValidated`;
- `staleAgainstCurrentMap`.

Normal dimension states are:

- `proven`;
- `blocked`;
- `stale`;
- `not-evaluated`;
- `not-applicable`.

Current-map provenance is represented separately as `current`, `stale`, `mixed` or `not-evaluated`.

No dimension is synthesized from another. In particular:

- script resolution is not source correlation;
- route presence is not interaction resolution;
- static reachability is not Physical E2E proof;
- one successful candidate repair is not global world or region correctness;
- missing optional evidence is not global absence.

## Coverage Matrix dimensions

The dashboard reuses the current `canary-otbm-e2e-coverage-matrix-v1` mechanic rows directly.

For the selected reviewed population:

- indexed-on-exact-map requires every member to be indexed with a unique match;
- script-resolved requires every member to be uniquely resolved by the Coverage Matrix;
- statically-reachable requires every member to have current compatible reachability coverage;
- physically-runtime-proven requires every member to have runtime proof on the current map;
- stale/current provenance preserves `staleAgainstCurrentMapProvenance` and optional attached evidence freshness.

Stale runtime proof is never upgraded to current proof.

## Source correlation

Source correlation is optional and must be explicitly bound in the target manifest by:

- exact Quest Map Validation report SHA-256;
- one or more exact Quest Map Validation `evidenceId` values.

The dashboard proves `sourceCorrelated` only when:

- the referenced report is one of the supplied `canary-quest-map-validation-v1` inputs;
- its World Index SHA-256 matches the dashboard current World Index;
- every referenced evidence ID exists;
- every referenced classification is exactly `confirmed`.

`map-only`, `script-only`, `unresolved` and `conflicting` remain blocked. A mismatched World Index is stale.

Missing source-correlation bindings remain `not-evaluated`.

## Executable routes and interactions

Route evidence is optional and must be explicitly bound by exact canonical route-plan report SHA-256.

`executableRouteCovered` is proven only when every bound route plan:

- uses the exact current map SHA-256;
- uses the exact current World Index SHA-256;
- has `executionStatus=executable`;
- has a complete path.

A route with stale map/index provenance is `stale`. A current blocked route is `blocked`.

Interaction proof is independently controlled by the reviewed `interactionRequired` flag on each bound route reference.

When no bound route requires interaction, `interactionResolved` is `not-applicable`.

When interaction is required, proof requires:

- current exact executable route provenance;
- `routingMode=executable`;
- a pinned interaction registry in route provenance;
- at least one retained edge-level interaction resolution;
- every retained interaction resolution to have `executionStatus=executable` with no blockers.

Therefore a route can be executable while interaction coverage remains blocked.

## Static quality compatibility

Map Quality v1 is bounded. The dashboard proves `staticQualityCompatible` only when:

- the target has an explicit region;
- that region exactly equals both Map Quality Geometry and Reachability scopes;
- Map Quality reports `sameRegion=true`;
- Map Quality is green;
- Geometry, Reachability and Script Resolution inputs are all `inputOk=true` and `inputComplete=true`.

A world target never receives a global Map Quality proof because Map Quality v1 explicitly reports `globalCoverageProven=false`.

A non-world target without an exact matching region remains `not-evaluated` for static quality rather than receiving a guessed global claim.

## Candidate-map validation

QA-004 reviewed candidate repair evidence is optional and must be explicitly bound by exact report SHA-256.

A linked candidate report is accepted for a target only when:

- its source map SHA-256 equals the dashboard current map;
- its recommendation selector exactly equals one of the target's selected reviewed Coverage Matrix mechanic selectors;
- the QA-004 report is successful with status `physically-validated` or `validated-no-physical-e2e-required`.

A stale source map remains stale. A failed/pending candidate validation remains blocked. A selector that is not part of the target's reviewed population fails closed instead of broadening target membership.

This dimension means only that the explicitly linked candidate change evidence is validated for that reviewed target relationship. It is not proof that every mechanic in a world, region or quest has been candidate-validated.

## Transparent requirements, not formal certification

Each reviewed target declares a non-empty `requiredDimensions` list.

The dashboard derives only:

```text
requirementsSatisfied = every declared required dimension is proven
                        and current-map-provenance is current when required
```

The report always emits:

```text
formalCertificationLevel = null
```

and policy flags:

```text
formalCertificationAssigned = false
opaqueScoreEmitted = false
```

QA-006 remains the owner of C0-C7 certification levels and their policies.

## Coverage gaps

Every non-proven/non-applicable dimension is retained as a deterministic gap with:

- target ID;
- dimension;
- state;
- whether that dimension was required by the reviewed target;
- factual gap code.

Coverage gaps are downstream evidence. They do not instruct Universal E2E owners to create or prioritize any particular scenario.

## Safety boundary

The dashboard:

- never parses or scans OTBM;
- never builds a World Index;
- never reruns Script Resolution, Reachability, Map Quality, World Health, Quest Map Validation or Coverage Matrix;
- never generates a route or runs route preflight;
- never executes interaction resolution;
- never runs Physical E2E;
- never mutates or validates a candidate by execution;
- never creates a second runner or workflow;
- never assigns formal certification.

Generated reports stay outside Git.

## Output safety

All input files are read as stable regular non-symlink files and SHA-256 pinned in report provenance.

Inputs must be distinct. Output cannot alias an input by path or hard link. Output is create-new/no-clobber unless `--overwrite` is explicitly supplied, in which case replacement is atomic.

## CLI

```bash
python tools/ai-agent/otbm_coverage_dashboard_tool.py \
  --targets /external/dashboard-targets.json \
  --coverage-matrix /external/coverage-matrix.json \
  --map-quality /external/map-quality.json \
  --world-health /external/world-health.json \
  --quest-validation /external/quest-validation.json \
  --route-plan /external/route-plan.json \
  --candidate-repair /external/reviewed-candidate-repair.json \
  --output /external/coverage-dashboard.json
```

Optional evidence arguments are repeatable. Targets bind optional evidence by the exact SHA-256 of the supplied report bytes.
