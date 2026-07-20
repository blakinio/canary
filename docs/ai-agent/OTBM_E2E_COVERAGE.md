# OTBM mechanic to Physical E2E coverage matrix

## Purpose

`tools/ai-agent/otbm_e2e_coverage.py` builds the deterministic `canary-otbm-e2e-coverage-matrix-v1` report for reviewed critical OTBM mechanic placements.

For each exact reviewed mechanic selector, the matrix records whether the mechanic is:

- present in existing OTBM Item Audit evidence for the current map;
- resolved by existing OTBM Script Resolution evidence;
- covered by supplied OTBM Reachability evidence;
- referenced by a supplied Universal Physical E2E `follow_route` scenario;
- physically runtime-proven by a successful Universal E2E artifact;
- proven only against stale map/World Index provenance;
- missing a physical scenario.

The tool is an evidence aggregator. It does not parse OTBM, build a World Index, resolve scripts, calculate reachability, execute a client, create a second E2E runner, or modify maps.

## Inputs

The tool consumes existing deterministic evidence only:

1. a reviewed `canary-otbm-e2e-coverage-targets-v1` target file;
2. the current `canary-otbm-world-index-v1` manifest;
3. a `canary-otbm-item-audit-v1` report for that exact map;
4. a `canary-otbm-script-resolution-v1` report;
5. zero or more `canary-otbm-reachability-v1` reports;
6. zero or more retained Universal Physical E2E artifact directories or ZIP files.

A target selector always contains an exact `[x,y,z]` position and at least one mechanic identity field: `itemId`, `actionId`, `uniqueId`, `houseDoorId`, or `teleportDestination`.

Criticality is reviewed input. The coverage tool never guesses that a placement is critical from sprites, item names, identifiers, map location, or chat history.

## Example target file

```json
{
  "format": "canary-otbm-e2e-coverage-targets-v1",
  "schemaVersion": 1,
  "targets": [
    {
      "id": "example.reviewed-teleport",
      "reason": "Reviewed example only; replace with exact evidence-backed project target.",
      "selector": {
        "position": [100, 100, 7],
        "itemId": 1387,
        "teleportDestination": [200, 200, 7]
      }
    }
  ]
}
```

The coordinates above are illustrative and are not committed Canary map evidence.

Target schema: `docs/ai-agent/OTBM_E2E_COVERAGE_TARGETS.schema.json`.

## Run

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_e2e_coverage.py \
  --targets artifacts/OTBM_E2E_COVERAGE_TARGETS.json \
  --world-manifest artifacts/world.widx.json \
  --item-audit artifacts/OTBM_ITEM_AUDIT.json \
  --script-resolution artifacts/OTBM_SCRIPT_RESOLUTION.json \
  --reachability artifacts/OTBM_REACHABILITY.json \
  --physical-artifact artifacts/universal-agent-e2e-route.zip \
  --output artifacts/OTBM_E2E_COVERAGE_MATRIX.json
```

`--reachability` and `--physical-artifact` may be repeated. Physical artifacts may be retained workflow ZIP files or extracted artifact directories.

Output schema: `docs/ai-agent/OTBM_E2E_COVERAGE_MATRIX.schema.json`.

## Evidence rules

### Statically indexed

`static.indexed` is true only when the exact target selector matches a mechanic placement in the supplied existing Item Audit report. The Item Audit map SHA-256 must equal the source-map SHA-256 in the supplied current World Index manifest, otherwise the tool fails before producing a matrix.

An ambiguous exact selector is not treated as a unique indexed mechanic and emits `STATIC_MECHANIC_AMBIGUOUS`.

### Script resolved

`script.resolved` requires Script Resolution evidence whose embedded Item Audit map SHA-256 matches the current World Index source map, plus exactly one matching placement whose status is an existing `handled-*` state.

`partially-resolved`, `referenced-only`, `unresolved`, and `conflicting` never become resolved. Missing or ambiguous Script Resolution evidence also fails closed. Review dispositions do not promote unresolved runtime evidence.

### Reachability covered

`reachability.covered` means at least one supplied Reachability report contains the exact mechanic and pins both the same source-map SHA-256 and World Index SHA-256 as the current World Index manifest.

Reachability evidence from another map or index is retained under `staleEvidence` but is not counted as current coverage. A Reachability `confirmed` status is geometry evidence only and is never physical gameplay proof.

### Physical scenario present

A physical scenario is associated with a mechanic only when all of these are true:

- the retained artifact has `scenario-manifest.json`;
- the manifest contains an executed `follow_route` step for the route plan being inspected;
- the corresponding canonical `route-<logical-id>.json` contains an exact transition evidence object or interaction `selectorQuery` matching the target.

Merely walking through or adjacent to the target position does not associate a physical scenario with the mechanic.

### Physically runtime-proven

`physical.runtimeProven` additionally requires:

- Universal E2E `result.json` status `success`;
- every explicit result check, when present, to be true;
- the matched route plan to have `executionStatus: executable`.

`physical.runtimeProvenOnCurrentMap` also requires the route-plan map and World Index hashes **and** retained runtime `map.sha256` to match the current World Index manifest. Missing runtime map provenance fails closed to non-current proof.

A successful physical run against stale provenance is retained as stale evidence and is never promoted to current-map proof.

### Missing physical scenario

`missingPhysicalScenario` is true only for an exact statically indexed target for which none of the supplied physical artifacts references the mechanic through executed route evidence.

This is a coverage gap, not proof that the mechanic is broken.

## Failure behavior

The tool fails closed for malformed JSON, unsupported formats, duplicate target IDs, selectors without an exact position and mechanic identity, stale Item Audit or Script Resolution map evidence, corrupt artifact JSON, invalid runtime map hashes, or unsafe output replacement.

Generated reports remain artifacts and are not map-writing authorization. No `.otbm`, `.widx`, client asset, or generated physical report should be committed by this workflow.

## Focused tests

```bash
python -m unittest -v tools/ai-agent/test_otbm_e2e_coverage.py
```

Coverage includes current-map static/script/reachability/physical correlation, unresolved script evidence, stale reachability and physical artifacts, ambiguous selectors, pure movement routes, retained ZIP artifacts, exact target requirements, duplicate IDs, and current-map Item Audit and Script Resolution provenance.
