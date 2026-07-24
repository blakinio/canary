# OTBM House Reference Parity

TCR-005 provides two deterministic, read-only evidence contracts:

- `canary-otbm-house-id-resolver-v1` — an explicit provenance-pinned mapping from `client-reference.house-id` to `otbm.house-id`;
- `canary-otbm-house-reference-parity-v1` — review findings across StaticData registry evidence, StaticMapData layout evidence and canonical OTBM World Index evidence.

Neither contract changes an OTBM, resolves `staticmapdata.object_id`, mutates runtime data or proves gameplay parity.

## Reused authorities

The consumer does not implement another OTBM parser. It consumes:

- `canary-tibia-client-reference-manifest-v1`;
- `canary-tibia-staticdata-index-v1` schemaVersion 2 or later;
- `canary-tibia-staticmapdata-index-v1`;
- `canary-otbm-world-index-v1` binary plus manifest;
- the existing `WorldIndex` reader.

All inputs are bound by exact SHA-256 and size evidence. A resolver becomes stale when any client manifest, producer output, World Index binary, source map or reviewed StaticData house-field order changes.

## StaticData HouseData requirement

TCR-005 requires the TCR-002A house-order contract:

- `source.houseFieldOrder`;
- `categories.houses.houseFieldOrder`;
- `policy.houseFieldOrderResolution`.

The three declarations must agree and be one of `unresolved`, `legacy` or `newer`.

Resolved `legacy` or `newer` semantics require non-empty reviewed evidence. With `unresolved`, raw `houseField5` and `houseField7` remain reference evidence and the parity consumer does not compare a declared `size` against OTBM house-tile population.

No field-order heuristic exists in TCR-005.

## Resolver derivation

The reviewed derivation mode uses one exact rule:

1. read a StaticData house registry position;
2. query that exact position in the canonical World Index;
3. accept the tile only when it is an OTBM house tile;
4. record its OTBM `houseId`;
5. reject one-to-many or many-to-one collisions.

Names, nearby tiles, numeric identity and StaticMapData object IDs are not used.

```bash
python tools/ai-agent/otbm_house_reference_parity_tool.py derive-resolver \
  --client-manifest /outside-git/client-manifest.json \
  --staticdata-index /outside-git/staticdata-index.json \
  --staticmapdata-index /outside-git/staticmapdata-index.json \
  --world-index /outside-git/world.widx \
  --world-manifest /outside-git/world.json \
  --review-id TCR-005-REGISTRY-POSITION-REVIEW \
  --review-statement "Exact registry position tile and canonical World Index house ID only." \
  --output artifacts/house-id-resolver.json
```

The resolver preserves unresolved records and conflicts instead of guessing.

## Parity dimensions

The parity report keeps evidence dimensions separate:

- StaticData registry presence and exact registry position;
- reviewed declared `size`, only when the StaticData producer emits it;
- StaticMapData layout origin, width, height, floors, row/tile counts and wall/door flags;
- OTBM house-tile count, placement count, floors and observed bounds;
- exact OTBM house-door placements grouped through the World Index.

A direct numeric comparison is a review finding, not a claim that the two fields have identical gameplay semantics. StaticMapData wall/door flags and OTBM house-door placements are emitted as independent counts because `staticmapdata.object_id` remains unresolved.

```bash
python tools/ai-agent/otbm_house_reference_parity_tool.py parity \
  --client-manifest /outside-git/client-manifest.json \
  --staticdata-index /outside-git/staticdata-index.json \
  --staticmapdata-index /outside-git/staticmapdata-index.json \
  --world-index /outside-git/world.widx \
  --world-manifest /outside-git/world.json \
  --resolver artifacts/house-id-resolver.json \
  --output artifacts/house-reference-parity.json
```

## Review states

Each house row uses one bounded state:

- `conforming`;
- `reference-only`;
- `otbm-only`;
- `mismatch`;
- `partial`;
- `unresolved-id-space`;
- `conflicting`;
- `stale-evidence.

Stale provenance fails closed before a report is produced. Missing mappings and unresolved positions remain explicit findings.

## Output safety

Inputs must be distinct regular files and symlinks are rejected. JSON reads are bounded and checked for file-identity changes. Duplicate JSON keys and non-finite constants fail closed.

Output is create-new/no-clobber by default. `--overwrite` writes a same-directory temporary file, flushes it and atomically replaces the target. An output path may not alias any protected input.

## Evidence boundaries

TCR-005 does not prove:

- exact client build identity unless the client manifest separately proves it;
- equality of client-reference and OTBM house IDs without the resolver;
- equivalence of declared size, layout dimensions or OTBM tile counts beyond the emitted review comparisons;
- any mapping from `staticmapdata.object_id` to OTBM, server or appearance IDs;
- reachability, pathfinding, critical access or geometry semantics;
- runtime house behavior, persistence, protocol/UI behavior or gameplay parity.

## Validation

```bash
python -m unittest discover -s tools/ai-agent -p "test_otbm_house_reference_parity.py" -v
python -m py_compile \
  tools/ai-agent/otbm_house_reference_parity.py \
  tools/ai-agent/otbm_house_reference_parity_tool.py \
  tools/ai-agent/test_otbm_house_reference_parity.py
python -m json.tool docs/ai-agent/OTBM_HOUSE_ID_RESOLVER.schema.json > /dev/null
python -m json.tool docs/ai-agent/OTBM_HOUSE_REFERENCE_PARITY.schema.json > /dev/null
python tools/ai-agent/otbm_house_reference_parity_tool.py --help > /dev/null
```

Exact external validation is opt-in:

```bash
CANARY_TCR005_EXACT_DIR=/outside-git/tcr005-exact \
CANARY_TCR005_STATICDATA_INDEX=/outside-git/staticdata-reviewed-index.json \
  python -m unittest discover -s tools/ai-agent -p "test_otbm_house_reference_parity.py" -v
```

Exact source files and generated reports remain outside Git.
