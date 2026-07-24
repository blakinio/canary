# Tibia StaticMapData House Reference Index

`canary-tibia-staticmapdata-index-v1` is the bounded, read-only TCR-003 producer for one explicitly selected Tibia `staticmapdata` file. It extends the stable `canary-tibia-client-reference-manifest-v1` provenance contract. It is not an OTBM parser, OTBM writer, content importer, object-ID mapper, gameplay validator, or map authority.

## Trust and provenance boundary

The operator supplies:

1. one stable TCR-001 client-reference manifest;
2. one selected StaticMapData file outside Git;
3. the exact manifest `selectedInputs[].id` for that file.

The producer reads both inputs with bounded stable-file checks. The selected source byte size and SHA-256 must exactly match the manifest entry. The output retains the manifest SHA-256, reference ID, manifest-relative source path, source SHA-256, encoded and decoded byte sizes, and detected encoding. Local absolute paths and proprietary source bytes are never emitted.

## Independently implemented wire contract

The parser independently implements the reviewed protobuf wire shape pinned by the programme:

```text
StaticMapData.houses
  HouseDetail.house_id
  HouseDetail.layout
    position.x/y/z
    size.width/height/floors
    tiles.floor_data.rows
      row.tiles
        object_id
        wall_info.is_wall
        door_info.is_door
      row.flags
```

Unknown fields, wrong wire types, malformed lengths, invalid booleans and excessive nesting fail closed. Singular-field duplication is retained as an explicit finding rather than silently treated as clean source evidence.

Supported source encodings match the reviewed TCR-002 safety model:

- raw protobuf;
- XZ container;
- LZMA-alone stream;
- the reviewed Tibia LZMA-alone header variant whose uncompressed-size bytes require normalization before standard decoding.

All reads, decompression and record construction are bounded. Default limits are 64 MiB encoded input, 256 MiB decoded input, 100,000 houses, 10,000,000 row records, 20,000,000 tile records and 20,000,000 declared cells. The CLI permits explicit reviewed overrides.

## Row and dimension consistency

Rows and flags are preserved exactly in source order. The independently reviewed real-file fixture established the deterministic encoded-span relationship:

```text
encodedCellSpan = rowCount + sum(row.flags or 0)
declaredCellCount = width * height * floors
```

The producer reports a `dimensionMismatches` finding when dimensions are non-positive or these values differ. It does not assign coordinates to individual rows or reinterpret `flags` beyond this consistency check. The policy therefore records row-flag semantics as `unresolved-beyond-encoded-cell-span`.

## Object-ID namespace boundary

Every client-side `object_id` remains in the exact namespace:

```text
staticmapdata.object_id
```

The report labels this namespace `unresolved` and sets `otbmItemIdEquivalent: false`. Numeric equality never proves correspondence with OTBM item IDs, Canary server IDs, appearance IDs or sprite IDs. Any future mapping requires a separate provenance-pinned resolver and bounded task.

## Findings and summary

The output records:

- duplicate house IDs with source ordinals;
- missing required house/layout/coordinate/dimension/tile fields;
- duplicate singular protobuf fields;
- non-positive dimensions and encoded-span mismatches;
- exact house, row, tile-record, declared-cell and encoded-span totals.

House, row and tile arrays retain source order with `sourceOrdinal`. Missing or malformed source evidence is never upgraded into OTBM, runtime or gameplay conclusions.

## CLI

```bash
python tools/ai-agent/tibia_staticmapdata_reference_index_tool.py \
  --manifest /outside-git/reference-manifest.json \
  --source /outside-git/staticmapdata.dat \
  --input-id staticmapdata \
  --output artifacts/tibia-staticmapdata-index.json
```

Output is create-new/no-clobber by default. `--overwrite` performs an explicit atomic replacement. The output may not alias the manifest or source.

## Validation

```bash
python -m unittest discover -s tools/ai-agent -p "test_tibia_staticmapdata_reference_index.py" -v
python -m py_compile \
  tools/ai-agent/tibia_staticmapdata_reference_index.py \
  tools/ai-agent/tibia_staticmapdata_reference_index_tool.py \
  tools/ai-agent/test_tibia_staticmapdata_reference_index.py
python -m json.tool docs/ai-agent/TIBIA_STATICMAPDATA_REFERENCE_INDEX.schema.json > /dev/null
```

The tests independently construct protobuf fixtures and cover exact record preservation, source ordering, namespace policy, duplicate/missing/dimension findings, malformed wire data, invalid booleans, raw/XZ/LZMA variants, decompression and record bounds, manifest binding, deterministic JSON and output collision/no-clobber behavior.

An opt-in test accepts `CANARY_TIBIA_STATICMAPDATA_FILE` for a real user-supplied file outside Git. CI never requires, copies or uploads proprietary client data or generated real-file reports.
