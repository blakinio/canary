# OTBM Repair / Materialization Pipeline

## Purpose

`tools/ai-agent/otbm_repair_materialization_pipeline_tool.py` is the smallest fail-closed finalization boundary over the existing OTBM repair and structural materialization contracts.

It does not add another OTBM parser, serializer, writer, World Index, Semantic Diff, script resolver, renderer, E2E runner, or deployment path.

The pipeline supports exactly two mutation modes:

1. `attribute`
   - consumes an already-reviewed `canary-otbm-bounded-patch-plan-v1`;
   - reuses `otbm_repair_sandbox_tool.py`;
   - therefore reuses the existing Phase 8 bounded patcher, native reparse, World Index, Semantic Diff, real before/after item audit, and script-resolution verification.

2. `tile-area`
   - consumes an existing `canary-otbm-region-merge-plan-v1` plus a separate `canary-otbm-area-materialization-approval-v1`;
   - reuses `materialize_area_plan()`;
   - therefore retains the materializer's zero-translation, complete-`OTBM_TILE_AREA`, raw-subtree, retained-byte, native-reparse, World Index, and Semantic Diff boundary.

The result contract is `canary-otbm-repair-materialization-pipeline-v1`.

## Why this is a finalization pipeline

Map Quality Gate intentionally does not invent reachability origins, routes, floor transitions, or player intent. Its three inputs must already exist for one exact map SHA-256:

- `canary-otbm-geometry-audit-v1`;
- `canary-otbm-reachability-v1`;
- `canary-otbm-script-resolution-v1`.

Therefore a safe automated pipeline cannot create those inputs from unspecified intent.

The bounded workflow is:

```text
explicit source/current map
    ->
existing repair preflight OR existing donor/region plan
    ->
reviewed Phase 8 plan OR separate TILE_AREA approval
    ->
existing sandbox/materializer candidate
    ->
explicit Geometry + Reachability + Script Resolution evidence for that candidate SHA-256
    ->
OTBM Repair / Materialization Pipeline
      - re-run the exact pinned mutation into an internal create-new candidate
      - verify the existing mutation result
      - rebuild the existing Map Quality Gate from the supplied component reports
      - require the quality source SHA-256 to equal the newly materialized candidate SHA-256
      - require the configured quality gate to pass
      - prove source and every direct file input stayed unchanged
      - publish a byte-identical create-new final map only after all checks pass
    ->
optional Universal OTS physical-client E2E
    ->
separate controlled staging/promotion
```

This candidate-to-final replay is intentional. It lets reviewed geometry/reachability/runtime evidence bind the exact deterministic output bytes without adding a second reachability policy or a new approval format.

## Safety invariants

The pipeline fails closed unless all applicable invariants hold:

- one explicit mutation mode is selected by the CLI subcommand;
- every direct file input is a regular non-symlink file and is SHA-256 pinned before mutation;
- the original source map remains unchanged in size, modification timestamp, and SHA-256 through final publication;
- all direct file inputs remain unchanged through final publication;
- final output and pipeline evidence paths are relative to the explicit artifact root;
- path escape, symlink traversal, existing destination paths, and silent overwrite are rejected;
- the final output is outside the pipeline evidence directory;
- the underlying mutation writes only an internal candidate first;
- the mutation report must be the exact existing sandbox or area-materialization contract and must prove its existing verification boundary;
- Geometry, Reachability, and Script Resolution reports must pass the existing Map Quality Gate compatibility checks;
- the Map Quality Gate source SHA-256 must equal the internal candidate SHA-256;
- pipeline severity policy is at least `error`; `none` is not accepted;
- unresolved evidence remains unresolved unless the caller explicitly chooses `--fail-on-unresolved`;
- the final map is published as a byte-for-byte copy of the verified internal candidate only after the quality gate passes;
- final output publication uses exclusive create-new semantics;
- no production map execution is authorized by this tool.

If mutation or quality verification fails, no final output map is published. The create-new pipeline evidence directory may retain the internal candidate and available diagnostic evidence for review.

## Attribute mode

Attribute mode does not broaden Phase 8.

The only writable map changes remain the four existing fixed-width, already-present mechanic attributes supported by `canary-otbm-bounded-patch-plan-v1`:

- `set-action-id`;
- `set-unique-id`;
- `set-house-door-id`;
- `set-teleport-destination`.

A human-reviewed Phase 8 plan is the existing authorization boundary for this mode. No second approval manifest is introduced.

The pipeline invokes the existing repair sandbox verifier with explicit:

- source map;
- reviewed plan;
- native scanner;
- appearances index;
- `items.xml`;
- repository root;
- one or more explicit active script roots;
- optional runtime/review rules.

The persisted sandbox verification report is pinned into the pipeline result. Its runtime unresolved/conflict evidence remains review evidence and is not promoted to handled.

Example:

```bash
python3 tools/ai-agent/otbm_repair_materialization_pipeline_tool.py attribute \
  --artifact-root /tmp/otbm-finalize \
  --source-map /maps/current.otbm \
  --plan /review/phase8-plan.json \
  --scanner /tools/otbm_item_audit_scan \
  --appearances-index /assets/appearances-index.json \
  --items-xml /repo/data/items/items.xml \
  --repository-root /repo \
  --script-root data/scripts \
  --script-root data-otservbr-global/scripts \
  --geometry /review/candidate-geometry.json \
  --reachability /review/candidate-reachability.json \
  --script-resolution /review/candidate-script-resolution.json \
  --output-map finalized/current-repaired.otbm \
  --evidence-dir evidence/current-repaired
```

The output/evidence arguments are artifact-root-relative create-new paths.

## TILE_AREA mode

TILE_AREA mode does not broaden the bounded materializer.

It still requires:

- `replace-region` planning semantics;
- zero translation `[0,0,0]`;
- complete 256x256 `OTBM_TILE_AREA` boundaries;
- compatible current/donor headers;
- a separate SHA-pinned `canary-otbm-area-materialization-approval-v1` covering every selected area and every non-blocking conflict;
- current/donor World Index inputs and manifests pinned by the existing region plan/materializer contracts.

The region plan, approval, current/donor indexes, and manifests remain confined below the materializer artifact root as required by the existing materializer.

Example:

```bash
python3 tools/ai-agent/otbm_repair_materialization_pipeline_tool.py tile-area \
  --artifact-root /tmp/otbm-finalize \
  --current-map /maps/current.otbm \
  --donor-map /maps/donor.otbm \
  --scanner /tools/otbm_area_materializer_scan \
  --plan reviewed/region-plan.json \
  --approval reviewed/area-approval.json \
  --current-index indexes/current.widx \
  --current-manifest indexes/current.widx.json \
  --donor-index indexes/donor.widx \
  --donor-manifest indexes/donor.widx.json \
  --geometry /review/candidate-geometry.json \
  --reachability /review/candidate-reachability.json \
  --script-resolution /review/candidate-script-resolution.json \
  --output-map finalized/current-with-area.otbm \
  --evidence-dir evidence/current-with-area
```

No translated donor import, partial TILE_AREA import, tile-level merge, arbitrary item insertion/deletion, stack reordering, generic serialization, or production-map mutation is added.

## Map Quality Gate behavior

The pipeline calls the existing `build_quality_report()` implementation over the three supplied reports.

Default policy:

- fail on `error`;
- preserve `warning`;
- preserve `unresolved`;
- preserve `info`.

Use `--fail-on-severity warning` to reject warnings too.

Use `--fail-on-unresolved` to reject any unresolved runtime evidence too.

`--fail-on-severity none` is intentionally not exposed by this pipeline because final artifact publication is fail-closed against quality errors.

The pipeline stores the generated `canary-otbm-map-quality-v1` report under the pipeline evidence directory and pins it into the final result.

A green static Map Quality Gate does not prove gameplay correctness, player intent, global world coverage, or physical-client behavior.

## Evidence layout

For an evidence directory such as `evidence/current-repaired`, successful output contains at least:

```text
evidence/current-repaired/
  candidate.otbm
  map-quality.json
  pipeline-result.json
```

Attribute mode additionally contains the existing sandbox/Phase 8 outputs, including:

```text
  phase8-evidence/
  phase8-result.json
  sandbox-verification.json
```

TILE_AREA mode additionally contains:

```text
  area-materialization/
    materialization-result.json
    output.widx
    output.widx.json
    semantic-diff.json
    ...
```

All generated maps, `.widx` files, reports, renders, and client assets remain local artifacts and must stay outside Git.

## Result contract

`canary-otbm-repair-materialization-pipeline-v1` records:

- mutation mode;
- exact unchanged source SHA-256/size;
- final create-new output SHA-256/size/path;
- SHA-256 pins for every direct file input;
- exact underlying mutation-report pin and bounded summary;
- generated Map Quality Gate report pin;
- exact `error`, `warning`, `unresolved`, and `info` totals;
- the three quality component pins;
- coverage and quality policy;
- evidence directory;
- rollback instruction;
- explicit safety/non-proof flags.

The final output SHA-256 equals both the internal verified candidate SHA-256 and the Map Quality Gate source SHA-256.

## Physical E2E and promotion

Physical runtime validation is deliberately outside this slice.

When deterministic feature-owned runtime evidence exists, reuse the merged Universal OTS physical-client E2E platform and declarative gameplay action plans. Do not add another Canary/MariaDB/OTClient lifecycle.

Coordinates, item IDs, NPCs, monsters, routes, transitions, and interactions must come from deterministic feature-owned evidence. Never invent them.

A pipeline success does not deploy or promote a map. Controlled staging/promotion remains a separate bounded workflow.
