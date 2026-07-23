# OTBM World Assurance Campaign

`tools/ai-agent/otbm_world_assurance_campaign.py` composes reviewed world-assurance campaign targets from the existing OTBM QA evidence contracts. It is the durable composition layer for `OWA-001 — Real-World Certification Campaign`.

The campaign layer does **not** parse OTBM, build a World Index, resolve scripts, run Reachability/BFS, create route plans, rerun route preflight, execute Physical E2E, validate candidate maps, or mutate map/evidence inputs.

## Public contracts

- reviewed target manifest: `canary-otbm-world-assurance-campaign-manifest-v1`;
- generated report/ledger: `canary-otbm-world-assurance-campaign-v1`.

Schemas:

- `docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN_MANIFEST.schema.json`;
- `docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN.schema.json`.

The first reviewed target manifest is:

- `docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN_TARGETS.json`.

Generated campaign reports and supporting QA-016 / QA-018 run artifacts stay outside Git.

## Canonical evidence reuse

The campaign consumes, but does not replace, these existing contracts:

- QA-005 `canary-otbm-coverage-dashboard-v1`;
- QA-006 `canary-otbm-region-quest-certification-v1`;
- QA-016 `canary-otbm-release-provenance-v1`;
- QA-018 `canary-otbm-evidence-bundle-v1`;
- retained Universal Physical E2E artifact ZIPs by exact SHA-256.

When a reviewed QA-005/QA-006 binding exists, the campaign copies the canonical coverage dimensions and certification result after exact target-kind and map/World Index provenance checks. It never recalculates or upgrades them.

When no valid reviewed QA-005 binding exists, every QA-005 dimension remains `not-evaluated` and formal QA-006 remains `C0_NOT_EVALUATED`. Route-level Physical E2E cannot independently raise the certification.

QA-016 freshness is consumed per declared dimension. `stale`, `not-compared`, and missing dimensions fail closed. Timestamps are not used as freshness evidence.

QA-018 is used only to verify exact reviewed JSON extracts by both raw source SHA-256 and canonical extracted-value SHA-256. The campaign does not reinterpret source semantics.

Retained Physical E2E is verified by the exact artifact ZIP digest supplied at campaign execution. The reviewed target manifest also pins the expected runtime-map, result-file and scenario-manifest hashes. This proves only the reviewed route-level runtime evidence represented by that exact artifact; it is not QA-005 mechanic proof and is not candidate-change revalidation.

## OWA-001 pilot

Reviewed target:

`owa-001.thais-temple-to-depot`

Class:

`landmark-route`

Semantic route:

`thais.temple -> thais.depot`

Exact reviewed endpoints:

- origin: `[32369, 32241, 7]`;
- destination: `[32352, 32226, 7]`;
- region: `thais.temple-depot`.

Exact provenance:

- source map SHA-256: `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`;
- World Index SHA-256: `6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a`.

Existing route evidence:

- canonical route plan hash: `0736a819ef656f9040ea14c51f1ab474beabe9e4da50435e1eb9e7fd0c28974b`;
- retained route-plan file SHA-256: `ef3257fd1f9330ebf13b583c176e109170f67c103afedc18a4212685dec03b16`;
- retained preflight file SHA-256: `7dea691ee7a9bc30c2b392ea8d15db359672ef44c33f7b5ebff0a89c656a197f`;
- preflight: `passed`;
- route distance: `59`;
- transition IDs: none;
- interaction required: false.

Existing retained Physical E2E evidence:

- workflow run: `29704821423`;
- artifact ID: `8447816376`;
- artifact ZIP SHA-256: `131faa08eaaccdacda62788b2e173b0f9ecc422a62ecd4769e874e4d136aeb40`;
- runtime map SHA-256: exact source-map hash above;
- result file SHA-256: `b659bb99d7cab3eaf98a8f94673b2281d0bd1c0898ba289aa8843d60206ee3b3`;
- scenario-manifest file SHA-256: `e8c1f802a51bfd0e9fd0559fbc09b107bc37e01a4c93e99eda61b8fd16ad8b95`.

### First campaign outcome

The first external campaign run is intentionally fail-closed:

- QA-005 coverage dimensions: all `not-evaluated`;
- QA-006 certification: `C0_NOT_EVALUATED`;
- QA-016 static-route freshness: `current`;
- QA-016 route-level Physical E2E freshness: `current`;
- retained route-level Physical E2E: `proven`;
- campaign target state: `blocked`.

Exact formal blockers:

- `QA005_LANDMARK_ROUTE_REQUIRES_REVIEWED_MECHANIC_IDS`;
- `QA005_NO_REVIEWED_MECHANIC_BINDING_FOR_PURE_MOVEMENT_ROUTE`;
- `QA006_REQUIRES_CANONICAL_QA005_TARGET`.

The reason is contractual, not a failed walk. QA-005 landmark-route coverage is mechanic-oriented: it requires reviewed Coverage Matrix `mechanicIds`, and Physical E2E mechanic association requires an exact route transition or interaction selector. The Thais pilot is a pure movement route with no transitions or interactions. Walking the route successfully therefore cannot be promoted into QA-005 mechanic coverage.

The campaign can prove the exact route/preflight provenance and retained route-level Physical E2E. It cannot currently prove C1-C5 formal QA-006 certification for this target, complete QA-005 mechanic dimensions, C6 feature/mechanic proof, or C7 candidate-change revalidation.

No alternative target was substituted because the reviewed repository evidence inspected for OWA-001 did not provide a stronger existing QA-005/QA-006 binding with equally exact current provenance. OWA-001 does not invent a mechanic ID, coordinate, landmark, or target just to raise the level.

## Run

A campaign execution may omit QA-005/QA-006 only for targets whose reviewed manifest explicitly marks those bindings `unavailable`. Such targets remain C0.

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_world_assurance_campaign_tool.py \
  --manifest docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN_TARGETS.json \
  --freshness artifacts/OWA_001_FRESHNESS.json \
  --evidence-bundle artifacts/OWA_001_EVIDENCE_BUNDLE.json \
  --physical-artifact artifacts/universal-agent-e2e-movement-physical-thais-temple-depot.zip \
  --output artifacts/OWA_001_CAMPAIGN_REPORT.json
```

For a future reviewed target with canonical QA-005 and QA-006 evidence, add:

```text
--coverage-dashboard artifacts/OTBM_COVERAGE_DASHBOARD.json
--certification artifacts/OTBM_REGION_QUEST_CERTIFICATION.json
```

The CLI uses create-new output semantics by default. `--overwrite` performs atomic replacement and never permits output/input path collision.

## Validation

Focused tests:

```bash
python -m unittest -v \
  tools/ai-agent/test_otbm_world_assurance_campaign.py \
  tools/ai-agent/test_otbm_world_assurance_campaign_output_safety.py \
  tools/ai-agent/test_otbm_world_assurance_campaign_schema.py
```

The focused suite covers:

- deterministic output;
- exact source-map / World Index provenance mismatch;
- QA-016 stale evidence;
- QA-018 source/value hash mismatch;
- missing exact retained Physical E2E artifact digest;
- fail-closed C0 for the pure movement pilot;
- exact bound C5 preservation from canonical QA-005/QA-006 evidence;
- landmark-route C5 certification cap;
- exact QA-006-to-QA-005 report pinning;
- create-new/no-clobber output safety;
- manifest/report schema validity.

The first real external run was repeated byte-for-byte with the same inputs; both generated reports were identical. The generated report SHA-256 field was `d5bda59b5a6f46695ed9d4037bbbdf5c825b3aae214e4430fd2580d2eb4fc86d`.
