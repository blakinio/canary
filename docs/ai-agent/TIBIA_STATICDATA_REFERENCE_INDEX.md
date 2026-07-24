# Tibia StaticData Reference Index

`canary-tibia-staticdata-index-v1` is the bounded, read-only TCR-002 producer for one explicitly selected Tibia `staticdata` file. Schema version 2 separates top-level category-family evidence from nested HouseData field-order evidence. It is not an OTBM parser, content importer, gameplay validator or map authority.

## Trust and provenance boundary

The operator supplies:

1. a stable TCR-001 client-reference manifest;
2. the selected StaticData file outside Git;
3. the exact manifest `selectedInputs[].id` for that file;
4. optional reviewed HouseData field-order evidence.

Before parsing, the indexer reads both files with bounded stable-file checks and requires source byte size and SHA-256 to match the selected manifest entry. The output retains exact manifest SHA-256, reference ID, manifest-relative path, source SHA-256, encoded/decoded size, encoding, top-level schema family and independent HouseData field-order state. Local absolute paths are not emitted.

Proprietary client files remain outside Git. The parser never executes selected content and never scans an arbitrary client directory.

## Top-level schema families

TCR-002 supports two reviewed top-level category families:

| Family | Top-level source categories |
|---|---|
| `legacy` | `creatures`, `titles`, `houses`, `bosses`, `quests` |
| `newer` | `monsters`, `monsterClasses`, `achievements`, `houses`, `bosses`, `quests` |

The parser implements bounded protobuf wire structures independently. It does not depend on generated protobuf classes and does not copy the pinned research implementation.

Successful protobuf decoding alone is not schema proof because unknown fields can be skipped. Top-level selection combines strict known-field/wire-shape validation with explicit discriminators. Ambiguous or conflicting evidence fails closed. Unsupported top-level or nested fields fail closed instead of being silently ignored.

The output preserves source-family vocabulary. A legacy `title` is not silently relabeled as a newer `achievement`, and a newer `monsterClass` remains distinct.

## Independent HouseData field ordering

Top-level family no longer assigns HouseData field 5/7 semantics automatically.

Pinned reviewed protobuf evidence contains both orders:

| House field order | Field 5 | Field 7 |
|---|---:|---:|
| `legacy` | `size` | `beds` |
| `newer` | `beds` | `size` |

Exact client files may combine a legacy top-level category layout with newer nested house ordering. Therefore schemaVersion 2 supports:

- `unresolved` — default; emits `houseField5` and `houseField7`, omits semantic `size` and `beds`, and records `unresolvedHouseFieldOrder`;
- `legacy` — emits `size` from field 5 and `beds` from field 7 only with a non-empty review ID and statement;
- `newer` — emits `beds` from field 5 and `size` from field 7 only with a non-empty review ID and statement.

Value distribution is useful review evidence but is never an automatic discriminator. Top-level schema and HouseData field order are independent output dimensions.

Example safe unresolved run:

```bash
python tools/ai-agent/tibia_staticdata_reference_index_tool.py \
  --manifest /outside-git/reference-manifest.json \
  --source /outside-git/staticdata.dat \
  --input-id staticdata \
  --output artifacts/tibia-staticdata-index.json
```

Example reviewed hybrid run:

```bash
python tools/ai-agent/tibia_staticdata_reference_index_tool.py \
  --manifest /outside-git/reference-manifest.json \
  --source /outside-git/staticdata.dat \
  --input-id staticdata \
  --house-field-order newer \
  --house-field-order-review-id TCR-002A-EXACT-HYBRID-HOUSE-ORDER-20260724 \
  --house-field-order-review-statement "Pinned protobuf comparison and exact-file review establish newer HouseData ordering for this exact source." \
  --output artifacts/tibia-staticdata-index.json
```

Resolved ordering without both review fields fails closed. `unresolved` may not claim reviewed evidence.

## SchemaVersion 1 to 2 migration

The format remains `canary-tibia-staticdata-index-v1`; `schemaVersion` changes from `1` to `2`.

New source fields:

- `houseFieldOrder`;
- `houseFieldOrderEvidence`.

The `houses` category gains `houseFieldOrder`. The report gains `findings.unresolvedHouseFieldOrder`, `summary.unresolvedHouseFieldOrderCount`, `policy.houseFieldOrderResolution` and `policy.houseFieldOrderHeuristics=false`.

Consumers must not assume `size` or `beds` exists. When `houseFieldOrder=unresolved`, consume raw `houseField5`/`houseField7` only as unsigned source values without gameplay semantics. When resolved, consumers must retain the review metadata and exact index provenance.

## Supported encodings and bounds

Supported source encodings are raw protobuf, XZ, LZMA-alone and the reviewed Tibia LZMA-alone header variant whose uncompressed-size bytes require normalization before standard decoding.

All source reads and decompression are bounded. Trailing/concatenated streams, truncated streams, oversized expansion and malformed protobuf fail closed. Defaults are 64 MiB encoded input, 256 MiB decoded input and 2,000,000 top-level records; the CLI permits smaller or reviewed larger explicit bounds.

## Record and finding semantics

Supported records retain only reviewed fields represented by the selected top-level schema and HouseData field-order state. Records are sorted deterministically while `sourceOrdinal` preserves original category order.

The report explicitly records duplicate IDs, missing `id`/`name`, duplicate singular protobuf fields and unresolved HouseData field order.

Quest records remain **ID/name inventory only**. Presence does not prove stages, storages, handlers, map positions, rewards, completion, runtime behavior, content parity or gameplay correctness.

Output is create-new/no-clobber by default. `--overwrite` performs atomic explicit replacement. Output may not alias the source or manifest.

## Exact TCR-002A evidence

For source SHA-256 `0bd51e1660f9d58594eb10000c35ea51113fc668aa3ee416c8c6b7ebb59b78ff`:

- top-level family is `legacy`;
- 995 house field-5 values range from 0 to 34 with median 2;
- 995 house field-7 values range from 5 to 750 with median 26;
- reviewed `newer` house ordering yields Spiritkeep `beds=23`, `size=382` and Sunset Homes Flat 01 `beds=1`, `size=13`.

The exact source and generated reports remain outside Git. Exact client build identity remains unknown unless separately proven by the manifest.

## Validation

Focused tests cover top-level legacy/newer selection, unresolved raw preservation, reviewed legacy/newer ordering, hybrid independence, missing review evidence, ambiguous/conflicting/unsupported schema failures, duplicate/missing fields, raw/XZ/LZMA decoding, bounds, exact manifest binding, deterministic JSON and no-clobber safety.

```bash
python -m unittest discover -s tools/ai-agent -p "test_tibia_staticdata_reference_index.py" -v
python -m py_compile \
  tools/ai-agent/tibia_staticdata_reference_index.py \
  tools/ai-agent/tibia_staticdata_reference_index_tool.py \
  tools/ai-agent/test_tibia_staticdata_reference_index.py
python -m json.tool docs/ai-agent/TIBIA_STATICDATA_REFERENCE_INDEX.schema.json > /dev/null
python tools/ai-agent/tibia_staticdata_reference_index_tool.py --help > /dev/null
```

Opt-in exact validation:

```bash
CANARY_TIBIA_STATICDATA_FILE=/outside-git/staticdata.dat \
  python -m unittest discover -s tools/ai-agent -p "test_tibia_staticdata_reference_index.py" -v
```
