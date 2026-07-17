# OTBM Repair / Materialization Pipeline

## Purpose

`tools/ai-agent/otbm_repair_materialization_pipeline_tool.py` is the fail-closed finalization boundary over the repository's existing OTBM repair and structural materialization contracts.

It does not add another OTBM parser, serializer, writer, World Index, Semantic Diff, script resolver, renderer, E2E runner, or deployment path.

The pipeline supports exactly one mutation mode per run:

1. `attribute` — replays an already-reviewed `canary-otbm-bounded-patch-plan-v1` through the existing repair sandbox verifier and Phase 8 bounded patcher.
2. `tile-area` — replays an approved zero-translation complete `OTBM_TILE_AREA` materialization through `materialize_area_plan()`.
3. `tile-replacement` — replays an approved same-coordinate complete raw `OTBM_TILE`/`OTBM_HOUSETILE` replacement through `materialize_tile_replacements()`.
4. `tile-insertion` — replays an approved same-coordinate complete raw tile insertion into an already-existing current parent `TILE_AREA` through `materialize_tile_insertions()`.
5. `tile-deletion` — replays an approved deletion of complete existing raw tile subtrees through `materialize_tile_deletions()` while preserving parent `TILE_AREA` nodes.
6. `tile-type-conversion` — replays an approved same-coordinate complete donor-subtree `OTBM_TILE ↔ OTBM_HOUSETILE` conversion through `materialize_tile_type_conversions()`.

The result contract remains `canary-otbm-repair-materialization-pipeline-v1`.

## Finalization workflow

Map Quality Gate does not invent reachability origins, routes, floor transitions, or player intent. Geometry, Reachability, and Script Resolution evidence must already exist for the exact deterministic candidate SHA-256.

```text
explicit source/current map
    ->
reviewed Phase 8 plan OR approved structural materializer inputs
    ->
existing sandbox/materializer creates and verifies an internal candidate
    ->
explicit Geometry + Reachability + Script Resolution evidence for that candidate SHA-256
    ->
canonical Repair / Materialization Pipeline
      - verify the existing mutation result contract
      - rebuild the existing Map Quality Gate from supplied component reports
      - require quality source SHA-256 == candidate SHA-256
      - require the configured quality gate to pass
      - prove source and all direct file inputs stayed unchanged
      - publish a byte-identical create-new final map
    ->
optional Universal OTS physical-client E2E
    ->
separate controlled staging/promotion
```

This replay/finalization boundary binds reviewed static/runtime evidence to exact deterministic output bytes without introducing another approval format or another writer.

## Safety invariants

The pipeline fails closed unless all applicable invariants hold:

- exactly one mutation mode is selected by the CLI subcommand;
- every direct file input is a regular non-symlink file and is SHA-256 pinned before mutation;
- the source map and all direct inputs remain unchanged through final publication;
- final output and evidence paths are artifact-root confined, create-new, non-symlink destinations;
- the underlying mutation writes only an internal candidate first;
- the mutation report has the exact existing contract for the selected mode;
- structural raw-tile modes must report `structuralVerificationComplete: true`, exact current/output pins, their operation-specific verification flags, no in-place source write, no full-map serializer, no arbitrary node serialization, and their existing approval/same-coordinate safety flags;
- Geometry, Reachability, and Script Resolution reports pass the existing Map Quality Gate compatibility checks;
- Map Quality source SHA-256 equals the internal candidate SHA-256;
- severity policy is at least `error`; unresolved evidence remains unresolved unless `--fail-on-unresolved` is selected;
- final output is a byte-for-byte copy of the verified candidate;
- no production-map execution is authorized by this tool.

If mutation or quality verification fails, no final output map is published. The create-new evidence directory may retain the candidate and diagnostics for review.

## Attribute mode

Attribute mode does not broaden Phase 8. Writable changes remain the existing fixed-width, already-present mechanic attributes:

- `set-action-id`;
- `set-unique-id`;
- `set-house-door-id`;
- `set-teleport-destination`.

The pipeline reuses the existing repair sandbox verifier, native reparse, World Index, Semantic Diff, before/after item audit, and script-resolution verification. Unresolved/conflicting runtime evidence remains review evidence and is never promoted to handled.

## TILE_AREA mode

`tile-area` retains the existing materializer boundary:

- `replace-region` planning semantics;
- zero translation `[0,0,0]`;
- complete 256x256 `OTBM_TILE_AREA` boundaries;
- compatible current/donor headers;
- separate SHA-pinned `canary-otbm-area-materialization-approval-v1`;
- pinned current/donor World Index inputs and manifests;
- exact retained current bytes outside selected complete area subtrees;
- native reparse, rebuilt World Index, selected-area donor equality, and bounded Semantic Diff.

## Raw tile modes

All raw tile modes are thin composition over already-merged materializers. The pipeline does not reproduce their writer or scanner logic.

### `tile-replacement`

Requires the existing `canary-otbm-tile-materialization-approval-v1`. Current and donor must each contain exactly one selected tile at the same absolute position, same canonical parent `TILE_AREA`, and same node type. The materializer proves complete donor raw-subtree equality and exact retention of non-selected current bytes.

### `tile-insertion`

Requires `canary-otbm-tile-insertion-approval-v1`. The selected tile is absent from current, unique in donor, and the canonical parent `TILE_AREA` already exists in current. The materializer proves complete-current byte-sequence retention outside inserted spans and exact donor equality for inserted subtrees.

### `tile-deletion`

Requires `canary-otbm-tile-deletion-approval-v1`. Selected complete raw tile subtrees must exist in current. The materializer proves only selected spans were removed and parent `TILE_AREA` nodes remain, including when they become empty.

### `tile-type-conversion`

Requires `canary-otbm-tile-type-conversion-approval-v1`. Current and donor contain the same selected position under the same parent area but with different node types limited to `OTBM_TILE` and `OTBM_HOUSETILE`. Conversion copies the complete donor subtree; it never patches only the node-type byte or invents house metadata.

For replacement, insertion, and type conversion, the approval, current/donor indexes, and manifests remain confined below the materializer artifact root. Deletion uses the corresponding current-only approval/index inputs.

Example raw replacement:

```bash
python3 tools/ai-agent/otbm_repair_materialization_pipeline_tool.py tile-replacement \
  --artifact-root /tmp/otbm-finalize \
  --current-map /maps/current.otbm \
  --donor-map /maps/donor.otbm \
  --scanner /tools/otbm_area_materializer_scan \
  --approval reviewed/tile-approval.json \
  --current-index indexes/current.widx \
  --current-manifest indexes/current.widx.json \
  --donor-index indexes/donor.widx \
  --donor-manifest indexes/donor.widx.json \
  --geometry /review/candidate-geometry.json \
  --reachability /review/candidate-reachability.json \
  --script-resolution /review/candidate-script-resolution.json \
  --output-map finalized/current-with-tiles.otbm \
  --evidence-dir evidence/current-with-tiles
```

`tile-insertion` and `tile-type-conversion` use the same donor/current structural input shape. `tile-deletion` omits donor map/index/manifest arguments. `tile-area` additionally requires `--plan`.

## Explicit non-goals

This pipeline extension does not add:

- non-zero coordinate translation;
- teleport destination rewriting caused by translation;
- partial `TILE_AREA` import;
- arbitrary independent item insertion/deletion or stack reordering;
- generic OTBM node serialization;
- a full-map serializer;
- in-place map writes;
- direct production-map execution;
- automatic gameplay correctness or physical-client proof.

Those remain separate architecture boundaries and are not required to claim completion of this bounded finalization pipeline.

## Map Quality Gate behavior

The pipeline reuses `build_quality_report()` over the three supplied reports. Default policy fails on `error` while preserving `warning`, `unresolved`, and `info`. `--fail-on-severity warning` rejects warnings too; `--fail-on-unresolved` rejects unresolved runtime evidence. `none` is intentionally not exposed.

A green static Map Quality Gate does not prove gameplay correctness, player intent, global world coverage, or physical-client behavior.

## Evidence layout

Every successful run retains:

```text
evidence/<run>/
  candidate.otbm
  map-quality.json
  pipeline-result.json
```

The selected underlying sandbox/materializer adds its existing evidence directory and `materialization-result.json` or sandbox report. Raw tile modes use mode-specific subdirectories such as `tile-replacement-materialization/` and retain their rebuilt `.widx`, manifest, Semantic Diff, and span evidence as produced by the existing materializer.

All generated maps, `.widx` files, reports, renders, and client assets are runtime artifacts and must stay outside Git.

## Result contract

`canary-otbm-repair-materialization-pipeline-v1` records the selected mode, unchanged source pin, final create-new output pin, every direct input pin, exact underlying mutation-report pin and bounded summary, generated Map Quality report, exact outcome counts, component pins, coverage/policy, evidence directory, rollback instruction, and explicit safety/non-proof flags.

The final output SHA-256 equals both the internal verified candidate SHA-256 and the Map Quality Gate source SHA-256.

## Physical E2E and promotion

Physical runtime validation remains outside structural finalization. When deterministic feature-owned runtime evidence exists, reuse Universal OTS physical-client E2E and declarative gameplay action plans. Never invent coordinates, item IDs, NPCs, monsters, routes, transitions, or interactions.

Pipeline success does not deploy or promote a map. Controlled staging/promotion remains separate.
