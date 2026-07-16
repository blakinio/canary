# OTBM Bounded Tile-Area Materializer

## Purpose

The bounded tile-area materializer is the first structural OTBM write boundary after the read-only donor/region merge planner. It is intentionally narrower than a general map writer.

It can replace, delete, or insert **complete same-coordinate `OTBM_TILE_AREA` subtrees** in a distinct copy of the current map. It never serializes arbitrary OTBM nodes and never modifies the source or donor map in place.

Public contracts:

- `canary-otbm-tile-area-spans-v1`
- `canary-otbm-area-materialization-approval-v1`
- `canary-otbm-area-materialization-result-v1`

The architecture boundary is recorded in `docs/agents/decisions/ADR-20260716-otbm-raw-tile-area-materialization-boundary.md`.

## Required workflow

1. Build canonical current and donor World Index files and manifests.
2. Run the merged `canary-otbm-region-merge-plan-v1` planner with:
   - `policy=replace-region`;
   - zero translation;
   - complete 256x256 x/y tile-area bounds.
3. Review the plan.
4. Create a separate `canary-otbm-area-materialization-approval-v1` document that pins:
   - the exact plan SHA-256;
   - every tile-area key covered by the aligned region;
   - every non-blocking conflict ID in the untruncated plan;
   - a non-empty rationale.
5. Run the materializer against the original current and donor maps plus the exact indexes/manifests used by the plan.
6. Consume only the generated output copy and evidence after the tool reports `ok: true`.

A planner report remains `writerReady: false`. The materializer does not reinterpret that field as approval; the separate approval document is mandatory.

## Native scanner reuse

Compile `tools/ai-agent/otbm_area_materializer_scan.cpp` instead of creating a separate parser:

```sh
c++ -O2 -std=c++20 -Wall -Wextra -Wpedantic -Werror \
  tools/ai-agent/otbm_area_materializer_scan.cpp \
  -o artifacts/otbm_area_materializer_scan
```

The translation unit includes the existing `otbm_item_audit_scan.cpp` implementation. All existing scanner modes are delegated unchanged. The additional `--tile-area-spans` mode first runs the existing full scanner and then records physical spans only for direct `OTBM_TILE_AREA` children of `MAP_DATA`.

The normalized `canary-otbm-tile-area-spans-v1` evidence pins the map and scanner SHA-256 and records exact raw subtree offsets and hashes.

## CLI

Example:

```sh
python tools/ai-agent/otbm_area_materializer_tool.py \
  --artifact-root artifacts/otbm-area-materialization \
  --current-map /path/to/current.otbm \
  --donor-map /path/to/donor.otbm \
  --scanner artifacts/otbm_area_materializer_scan \
  --plan region-plan.json \
  --approval area-approval.json \
  --current-index current.widx \
  --current-manifest current.widx.json \
  --donor-index donor.widx \
  --donor-manifest donor.widx.json \
  --output-map output/materialized.otbm \
  --evidence-dir output/materialization-evidence
```

The plan, approval, indexes, and manifests are confined below `--artifact-root`. Source and donor maps may be external regular files, but symlinks are rejected. Output and evidence must be new paths below the artifact root.

## Structural safety gates

Before any publication, the implementation requires all of the following:

- exact current/donor source-map pins from the merge plan;
- exact current/donor World Index and manifest pins from the merge plan;
- current/donor OTBM version, width, height, items major, and items minor compatibility;
- zero unknown attribute tails;
- a contiguous direct `MAP_DATA` tile-area section;
- no duplicate raw span for any selected area key;
- zero translation and full tile-area aligned bounds;
- `replace-region` policy;
- zero blocking plan conflicts;
- complete, untruncated review-conflict evidence;
- exact approval coverage of every selected area and review conflict;
- create-new output/evidence paths with symlink/path confinement checks.

## Raw materialization proof

For selected area keys:

- donor raw `TILE_AREA` subtrees are copied byte-for-byte;
- a selected current subtree is replaced by the donor subtree, or deleted when the donor area is absent;
- a donor subtree absent from current is inserted at the native-scanner-proven end of the contiguous tile-area section.

The implementation hashes the concatenation of every non-selected current byte and compares it with the output after excluding selected output subtrees. Those retained byte streams must be identical in both length and SHA-256.

Every selected output raw subtree must also have the exact donor subtree SHA-256.

## Mandatory post-write verification

The temporary candidate is not published until it passes:

1. the native scanner again;
2. normalized output tile-area span validation;
3. output selected raw-subtree equality with donor;
4. canonical output World Index rebuild;
5. canonical selected-area World Index equality with donor;
6. bounded Semantic OTBM Diff from current to output over the approved region;
7. current map, donor map, and scanner pre/post SHA-256/stat checks.

Only after all gates pass are the output map and evidence directory published with create-new semantics.

Evidence includes:

- `materialization-result.json`
- `current-area-spans.json`
- `donor-area-spans.json`
- `output-area-spans.json`
- `output.widx`
- `output.widx.json`
- `semantic-diff.json`

These files are runtime artifacts and must not be committed.

## What v1 does not do

v1 does not support:

- non-zero x/y/z translation;
- teleport destination rewriting caused by translation;
- partial tile areas;
- tile-level overlay merge;
- arbitrary item stack editing;
- arbitrary node serialization;
- a complete-map writer;
- in-place map writes;
- automatic approval of planner conflicts;
- gameplay, player-intent, reachability, script-runtime, or physical-client E2E proof.

Those require separate bounded work and, where the structural contract changes, a new ADR.
