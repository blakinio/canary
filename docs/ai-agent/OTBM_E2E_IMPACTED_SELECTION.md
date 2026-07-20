# OTBM Semantic Diff impacted Physical E2E selection

## Purpose

`tools/ai-agent/otbm_e2e_impacted_selection.py` builds `canary-otbm-e2e-impacted-selection-v1`, a deterministic fail-closed bridge from existing `canary-otbm-semantic-diff-v1` evidence to the set of reviewed route/mechanic Universal Physical E2E scenarios that must be rerun after a map change.

The selector does not parse OTBM, build a World Index, calculate or repair routes, execute the client, create another E2E runner/workflow, or modify either map. Existing Semantic OTBM Diff remains the authoritative change detector; existing Reachability remains the sole route/pathfinding implementation; existing Universal E2E remains the physical lifecycle owner.

## Inputs

The selector consumes:

1. one existing `canary-otbm-semantic-diff-v1` report;
2. one or more reviewed Universal E2E scenario manifests;
3. a directory containing baseline `route-<logical-id>.json` `canary-otbm-e2e-route-plan-v1` plans referenced by those scenarios.

The scenario manifest is used only to read `suite`, `id`, and `follow_route` logical route IDs. The baseline route plan supplies exact ordered route positions, transition/interaction target positions, source-map SHA-256 and World Index SHA-256.

## Run

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_e2e_impacted_selection.py \
  --semantic-diff artifacts/OTBM_SEMANTIC_DIFF.json \
  --scenario tests/e2e/scenarios/movement/physical-thais-temple-depot.json \
  --route-plan-root artifacts/baseline-route-plans \
  --output artifacts/OTBM_E2E_IMPACTED_SELECTION.json
```

Repeat `--scenario` for each reviewed route/mechanic scenario that is a candidate for physical rerun. The tool emits selection evidence only; the existing Universal E2E runner remains responsible for actual scenario resolution and execution.

Output schema: `docs/ai-agent/OTBM_E2E_IMPACTED_SELECTION.schema.json`.

## Exact non-impact rule

A scenario may be safely marked `skipped` only when all of the following are proven:

- Semantic Diff format/schema and compatibility are valid;
- the diff is `full-index`;
- `summary.findings.truncated` is false;
- every sampled finding has an exact position;
- every referenced baseline route plan exists and is a complete executable `canary-otbm-e2e-route-plan-v1`;
- every baseline route plan map SHA-256 equals Semantic Diff `before.provenance.sourceMap.sha256`;
- every baseline route plan World Index SHA-256 equals Semantic Diff `before.provenance.worldIndex.sha256`;
- no exact diff finding position intersects any route path position, transition source/destination, or exact interaction selector position collected from the baseline route plan.

Only then does the selector emit `EXACT_FULL_INDEX_DIFF_PROVES_NON_IMPACT` and `selected: false`.

This is evidence that the reviewed baseline route/mechanic scenario is not touched by the exact diff. It is not a general gameplay-correctness claim and does not authorize skipping unrelated non-OTBM test suites.

## Impact selection

A scenario is selected normally when an exact Semantic Diff finding position intersects its compatible baseline route evidence. The output retains the stable Semantic Diff finding IDs under `impactedFindingIds` and emits `SEMANTIC_DIFF_INTERSECTS_BASELINE_ROUTE`.

Exact route evidence includes:

- every position in the canonical route plan `path`;
- edge `from`/`to` positions;
- exact `position`, `source`, `destination`, `from`, or `to` triples nested in transition/interaction evidence, including `selectorQuery.position` for reviewed map-item interactions.

This deliberately catches a use-target tile that may be adjacent to the player's movement path rather than a tile the player stands on.

## Fail-closed selection

The selector chooses `selected: true` with `failClosed: true` instead of claiming non-impact when proof is incomplete. Reasons include:

- `SEMANTIC_DIFF_SCOPE_NOT_FULL_INDEX`;
- `SEMANTIC_DIFF_FINDINGS_TRUNCATED`;
- `SEMANTIC_DIFF_FINDING_POSITION_UNKNOWN`;
- `SCENARIO_FOLLOW_ROUTE_MISSING`;
- `BASELINE_ROUTE_PLAN_MISSING` or invalid;
- `BASELINE_ROUTE_NOT_EXECUTABLE`;
- `BASELINE_ROUTE_PATH_MISSING` or invalid;
- `BASELINE_ROUTE_MAP_PROVENANCE_STALE`;
- `BASELINE_ROUTE_WORLD_INDEX_PROVENANCE_STALE`.

Malformed or unsupported top-level Semantic Diff evidence is rejected rather than converted into a skip decision.

A bounded-region Semantic Diff is useful review evidence, but by itself it cannot prove that no relevant change exists outside the bounded comparison scope. Therefore v1 selects candidate scenarios fail-closed for bounded-region diffs. Candidate-map workflows that need safe skip decisions should provide a compatible full-index Semantic Diff between the approved source and candidate maps.

## Determinism and boundaries

- scenario results are ordered by `(suite, id, manifest path)`;
- route plan entries, impacted finding IDs and decision reasons are sorted;
- duplicate scenario identities are rejected;
- input JSON files are capped at 64 MiB and direct symlinks are rejected;
- generated output is written atomically and is never a committed map artifact;
- `.otbm`, `.widx`, `items.otb`, client assets and generated selection reports do not belong in Git.

## Focused tests

```bash
python -m unittest -v tools/ai-agent/test_otbm_e2e_impacted_selection.py
```

The suite covers exact path impact, interaction target impact, proven non-impact, truncated and bounded diffs, missing finding positions, stale map/World Index route provenance, missing/blocked route plans, missing `follow_route`, duplicate scenario IDs, unsupported diff format, deterministic ordering and explicit no-parser/no-pathfinder/no-runner policy.
