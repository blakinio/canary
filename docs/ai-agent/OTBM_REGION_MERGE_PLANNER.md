# OTBM Donor/Region Merge Planner

## Purpose

`otbm_region_merge_planner.py` builds a deterministic, read-only review plan for comparing an explicit donor World Index region with an explicit target region after a declared translation.

The planner does not parse or write OTBM. It consumes the existing canonical `canary-otbm-world-index-v1` format and reuses the Semantic Diff manifest/provenance validators. A future structural writer remains a separate ADR and bounded task.

Report format: `canary-otbm-region-merge-plan-v1`.

## Inputs

Required:

- current `.widx` and its World Index manifest;
- donor `.widx` and its World Index manifest;
- inclusive donor `--donor-from x,y,z` and `--donor-to x,y,z`;
- explicit `--target-origin x,y,z` corresponding to the normalized donor lower bound.

Optional:

- current `canary-otbm-script-resolution-v1` report;
- donor `canary-otbm-script-resolution-v1` report.

All inputs must live below `--artifact-root`. World Index hashes, sizes, headers, logical summaries, scanner build formats and OTBM/item versions are validated through the existing Semantic Diff provenance checks. The planner fails closed when either World Index reports unknown attribute tails.

## Translation

The translation delta is calculated exactly as:

```text
targetOrigin - normalizedDonorLowerBound
```

No city, island, quest area or fragment is aligned heuristically. Any translated tile or internal teleport destination outside the OTBM coordinate range fails closed.

## Policies

### `overlay`

- donor tile missing in current target region -> `add`;
- donor tile differs from current target tile -> `replace` plus explicit `current-content-replacement` review conflict;
- identical tile -> `unchanged`;
- current-only target tile -> `preserve-current-only`.

### `replace-region`

The first three rules are the same, but a current-only target tile becomes `delete-candidate` plus an explicit review conflict. The planner never performs the deletion.

## Canonical tile evidence

Each sampled action preserves:

- exact target position;
- exact donor source position when present;
- current tile snapshot;
- donor source snapshot;
- proposed translated snapshot.

Tile snapshots preserve tile kind, house ID, flags and ordered placements. Placements preserve `tilePlacementIndex`, item ID, source/depth and available action ID, unique ID, house-door ID and teleport destination evidence.

Action and conflict IDs are SHA-256-derived from canonical JSON evidence and remain deterministic for identical inputs and options.

## Mechanics conflict checks

### Unique IDs

A donor `uniqueId` colliding with any retained current-map occurrence is a blocking `unique-id-collision`. Handler similarity does not make duplicate UIDs safe.

### Action IDs

A donor `actionId` reused by retained current content is always surfaced.

With both explicit script-resolution reports:

- identical handler signatures -> `action-id-reuse-same-handler` (`review`);
- conflicting or different handler evidence -> blocking `action-id-reuse-handler-conflict`;
- unresolved or missing compatibility evidence -> blocking `action-id-reuse-unresolved`.

Without both reports, reuse remains unresolved. The planner never converts unresolved evidence into handled evidence.

### House doors

A `houseDoorId` without a donor/proposed house ID is blocking. Reuse of the same `(houseId, houseDoorId)` by retained current content is blocking. Reuse across different house IDs is not automatically classified as a collision.

### Teleports

Only destinations inside the selected donor region are translated by the declared delta.

- internal destination with donor tile -> translated deterministically;
- internal destination without donor tile -> explicit conflict; overlay may retain a matching current destination but still requires review;
- external destination -> never guessed or translated; it is preserved exactly and requires review when the current destination exists;
- external destination missing from current -> blocking conflict.

This is structural evidence, not proof that the destination is walkable or gameplay-correct.

## Output semantics

`ok` means there are no `error` or `unresolved` conflicts in the review plan. It does not mean the plan has been approved or executed.

`requiresHumanReview` remains independent from `ok` and becomes true for structural changes or review conflicts.

`writerReady` is always `false` in v1.

Action/conflict arrays are bounded by `--sample-limit`, while summary totals and per-kind/per-severity counts remain exact.

## CLI

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_region_merge_planner_tool.py \
  --artifact-root artifacts \
  --current-index current.widx \
  --current-manifest current.widx.json \
  --donor-index donor.widx \
  --donor-manifest donor.widx.json \
  --donor-from 32000,31000,7 \
  --donor-to 32100,31100,9 \
  --target-origin 33000,32000,7 \
  --policy overlay \
  --current-script-resolution current-script-resolution.json \
  --donor-script-resolution donor-script-resolution.json \
  --output region-merge-plan.json
```

Without `--output`, the report is written to stdout. An existing output is never overwritten unless `--overwrite` is explicit. Non-overwrite publication uses exclusive file creation.

## Safety boundaries

The planner:

- never modifies source or donor maps;
- never emits executable OTBM writer instructions;
- never broadens Phase 8 bounded fixed-width patch contracts;
- never performs heuristic coordinate alignment;
- never claims runtime or gameplay correctness;
- never treats unresolved script evidence as handled;
- never commits maps, `.widx`, assets or generated plans.

## Focused validation

```bash
PYTHONPATH=tools/ai-agent \
python -m unittest -v tools/ai-agent/test_otbm_region_merge_planner.py
```

The focused suite builds synthetic OTBM fixtures with the existing native scanner and World Index builder. It covers translated additions, delta-zero identity with internal teleports, overlay preservation, replace-region delete candidates, global UID/AID reuse outside the target region, same-handler AID review evidence, internal/external teleport handling, translation overflow, exact truncated counts and exclusive report publication.
