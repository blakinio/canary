# OTBM World Assurance Factual Certification and Coverage Map

`tools/ai-agent/otbm_world_assurance_map.py` implements `OWA-002 — Factual Certification and Coverage Map` as a deterministic visualization layer over the exact `canary-otbm-world-assurance-campaign-v1` contract delivered by OWA-001.

The package does not create a second map renderer. The base map PNG is produced only by the existing factual renderer `tools/ai-agent/otbm_renderer.py:render_region`. OWA-002 adds an evidence-linked SVG annotation layer and a machine-readable manifest around that output.

## Public contract

Generated visualization manifest:

- `canary-otbm-world-assurance-map-v1`

Schema:

- `docs/ai-agent/OTBM_WORLD_ASSURANCE_MAP.schema.json`

Generated PNG, SVG and manifest outputs are external artifacts and are not committed to Git.

## Evidence model

The input campaign report must:

- use `canary-otbm-world-assurance-campaign-v1` schema version 1;
- contain a valid canonical `reportSha256` matching its exact content;
- contain reviewed target bounds and endpoints;
- contain exact source-map and World Index provenance.

The tool additionally records the raw campaign-file SHA-256. When rendering is executed, the source OTBM file is hashed before the factual renderer runs and must exactly match the campaign's source-map SHA-256.

Every visible OWA annotation and proof panel carries at least one exact evidence reference:

```text
campaign:<campaign-report-sha256>#/targets/<index>/<json-pointer>
```

The annotation layer never infers semantic meaning from sprites or visual proximity.

## What is visualized

For each selected reviewed target, OWA-002 can show:

- the exact reviewed routing bounds as a region outline;
- the exact reviewed origin marker;
- the exact reviewed destination marker;
- formal QA-006 certification state;
- independent QA-005 coverage-dimension states;
- QA-016 freshness state and dimensions;
- retained route-level Physical E2E state and proof boundary;
- explicit blockers.

The package deliberately does **not** reconstruct or draw an inferred route path. The OWA-001 campaign report records route distance and route/preflight provenance but not the full ordered route geometry. OWA-002 does not rerun Reachability/BFS to manufacture presentation data.

## OWA-001 pilot representation

For `owa-001.thais-temple-to-depot`, the factual view preserves these independent facts:

1. QA-006 formal certification is `C0_NOT_EVALUATED`;
2. QA-005 coverage dimensions are `not-evaluated` because no reviewed mechanic binding exists for the pure-movement route;
3. QA-016 static-route and retained route-level Physical E2E freshness are `current`;
4. retained route-level Physical E2E is `proven`, but this is not QA-005 mechanic proof and does not independently raise QA-006 certification;
5. the three exact QA-005/QA-006 blockers remain visible.

A successful walk is therefore not rendered as a green certified mechanic and no composite health score is produced.

## Render flow

```text
exact OWA-001 campaign report
  -> verify canonical campaign reportSha256
  -> select reviewed targets
  -> preserve exact reviewed bounds/endpoints and proof dimensions
  -> verify exact source-map SHA-256
  -> existing factual renderer creates base PNG
  -> OWA-002 creates SVG annotations/panels only
  -> write deterministic canary-otbm-world-assurance-map-v1 manifest
```

The SVG references the renderer-produced base PNG as a sibling artifact. It does not draw map terrain or sprites itself.

## CLI

Plan-only manifest:

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_world_assurance_map_tool.py \
  --campaign artifacts/OWA_001_CAMPAIGN_REPORT.json \
  --artifact-root artifacts/owa-002 \
  --output-dir renders \
  --manifest OWA_002_MAP_MANIFEST.json
```

Render with the exact OTBM and compatible real client assets:

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_world_assurance_map_tool.py \
  --campaign artifacts/OWA_001_CAMPAIGN_REPORT.json \
  --artifact-root artifacts/owa-002 \
  --map world.otbm \
  --assets client-assets \
  --output-dir renders \
  --manifest OWA_002_MAP_MANIFEST.json \
  --target-id owa-001.thais-temple-to-depot \
  --execute
```

For execution, the map and assets paths are confined to `--artifact-root`, matching the existing artifact-oriented renderer workflow. The manifest is also confined to that root.

By default outputs are create-new/no-clobber. `--overwrite` performs atomic replacement. Symlink outputs, path escape, output inside the client-assets root, source-map provenance mismatch and exact input/output collisions fail closed.

## Hard boundaries

OWA-002 does not:

- parse OTBM independently;
- build a World Index;
- resolve scripts;
- pathfind or reconstruct route geometry;
- rerun QA-005, QA-006, QA-016 or QA-018;
- execute Physical E2E;
- assign certification independently;
- turn route-level Physical E2E into mechanic coverage;
- infer map semantics from visual appearance;
- generate AI map imagery;
- mutate OTBM, assets or datapacks;
- authorize merge, release or deployment from colours, percentages or presentation state.

## Validation

Focused tests:

```bash
PYTHONPATH=tools/ai-agent python -m unittest -v \
  tools/ai-agent/test_otbm_world_assurance_map.py \
  tools/ai-agent/test_otbm_world_assurance_map_output_safety.py \
  tools/ai-agent/test_otbm_world_assurance_map_schema.py
```

The suite covers:

- deterministic planning;
- exact campaign self-hash validation;
- unknown target rejection;
- reviewed-bounds enforcement;
- preservation of C0 / not-evaluated / current / Physical-E2E-proven as separate facts;
- stale-state preservation without upgrade;
- no inferred route polyline/path;
- exact map SHA validation before renderer execution;
- existing-renderer materialization through an injected deterministic test double;
- sibling base-image linkage in generated SVG;
- evidence references on visible panels and annotations;
- no-clobber and explicit atomic overwrite;
- output confinement and client-assets-root protection;
- symlink rejection;
- plan tamper detection;
- campaign/manifest input-output collision rejection;
- schema contract shape.
