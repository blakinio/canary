# OTBM TCR-to-QA Freshness Impact

`OWA-003A` adds one bounded read-only composition between the stable Tibia Client Reference adoption router and the existing OTBM release-provenance/freshness contract.

Public formats:

- reviewed input: `canary-otbm-tcr-qa-freshness-manifest-v1`;
- generated output: `canary-otbm-tcr-qa-freshness-impact-v1`.

Generated manifests and reports remain external artifacts and are not committed.

## Purpose

The package answers one narrow question:

> For an exact stable TCR-011 route and an exact existing QA-016 provenance report, did a reviewer explicitly map every routed target to the exact QA-016 components and dimensions that QA-016 already marked changed/stale?

A successful report confirms only this exact freshness relationship. It does not prove a map defect, gameplay impact, runtime regression, successful validation or refreshed certification.

## Required inputs

The CLI consumes three distinct, regular, non-symlink JSON files:

1. one exact `canary-tibia-reference-adoption-routing-v1` report;
2. one exact `canary-otbm-release-provenance-v1` report;
3. one reviewer-authored `canary-otbm-tcr-qa-freshness-manifest-v1`.

The manifest pins:

- routing file SHA-256 and routing `reportSha256`;
- QA-016 file SHA-256, `reportSha256`, current BOM SHA-256 and optional previous BOM SHA-256;
- one reviewed mapping for every TCR route/target;
- the exact extract ID, source ID, JSON Pointer and value SHA-256 copied from the route;
- explicit QA-016 component IDs and dimension IDs;
- a review ID, statement and optional context references.

## Coverage and fail-closed rules

Every TCR route must be covered.

For `routed` routes:

- every exact `(owner, capability)` target must appear once;
- targetless mappings are forbidden;
- each mapping must declare at least one component and dimension;
- each component must be present in QA-016 `componentChanges` and must not be `removed`;
- each dimension must exist, must not be removed and must have status `stale`;
- after aggregation across mappings, the mapped component set for each dimension must exactly equal QA-016 `changedDependencies`.

For `unsupported` or `blocked` routes:

- exactly one targetless mapping is required;
- component and dimension arrays must be empty;
- the outcome remains `not-mapped` and `reviewRequired=true`.

Unknown routes, duplicate route/target mappings, stale file/report pins, altered extract references, current/not-compared dimensions, removed components/dimensions and partial dependency sets fail closed.

Unrelated QA-016 dimensions are not copied into the impact set and remain owned by QA-016.

## Downstream boundary

Every impact explicitly records:

```text
qa008: not-evaluated
qa002: not-evaluated
qa007: not-evaluated
qa006: not-refreshed
```

The package does not:

- parse Tibia client files, StaticData, StaticMapData, proficiency inputs or minimap data;
- parse or scan OTBM or build a World Index;
- guess identifier equivalence or discover dependency edges;
- rerun QA-016;
- invoke QA-008;
- generate Semantic Diff or select QA-002 validators;
- create QA-007 execution-ledger/result evidence;
- execute validators or Universal Physical E2E;
- refresh or assign QA-006 certification;
- mutate maps, datapacks, assets, evidence or game state;
- authorize deployment or claim gameplay parity.

QA-008/002/007/006 remain separate downstream owners and require their canonical inputs.

## CLI

```bash
python tools/ai-agent/otbm_tcr_qa_freshness_tool.py \
  --routing-report artifacts/tcr-routing.json \
  --release-provenance artifacts/release-provenance.json \
  --manifest artifacts/tcr-qa-freshness-manifest.json \
  --output artifacts/tcr-qa-freshness-impact.json
```

Output is create-new by default. `--overwrite` performs an explicit atomic replacement. Input/output aliasing, symlink inputs/outputs, duplicate inputs, unsafe output parents, implicit clobbering, malformed JSON, duplicate JSON keys, non-finite numbers and read-time input changes are rejected.

## Interpretation

`freshnessStatus: stale` means the exact supplied QA-016 report already marked the reviewed dimension stale because the exact mapped components changed.

It does not establish why the reference changed, whether the map or server is wrong, which repair is desired, which validator will fail, whether runtime behavior changed or whether certification can be refreshed.

`unsupported` and `blocked` are evidence outcomes, not invitations to invent a mapping or widen downstream authority.
