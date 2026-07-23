# Tibia StaticData Reference Index

`canary-tibia-staticdata-index-v1` is the bounded, read-only TCR-002 producer for one explicitly selected Tibia `staticdata` file. It extends the stable `canary-tibia-client-reference-manifest-v1` provenance contract; it is not an OTBM parser, content importer, gameplay validator, or map authority.

## Trust and provenance boundary

The operator supplies three explicit inputs:

1. a stable TCR-001 client-reference manifest;
2. the selected StaticData file outside Git;
3. the exact manifest `selectedInputs[].id` for that file.

Before parsing, the indexer reads both files with bounded stable-file checks and requires the source byte size and SHA-256 to match exactly the selected manifest entry. The output retains the exact manifest SHA-256, reference ID, manifest-relative path, source SHA-256, encoded byte size, decoded byte size, encoding and selected schema family. Local absolute paths are not emitted.

Proprietary client files remain outside Git. The parser never executes selected content and never scans an arbitrary client directory.

## Independently implemented schema families

TCR-002 supports exactly two reviewed schema families:

| Family | Top-level source categories |
|---|---|
| `legacy` | `creatures`, `titles`, `houses`, `bosses`, `quests` |
| `newer` | `monsters`, `monsterClasses`, `achievements`, `houses`, `bosses`, `quests` |

The parser implements the bounded protobuf wire structures independently. It does not depend on generated protobuf classes and does not copy the pinned research implementation.

Successful protobuf decoding alone is not schema proof because unknown fields can be skipped. Selection therefore combines strict known-field/wire-shape validation with explicit discriminators such as legacy title/house fields and newer house/boss/quest field positions. When both schemas remain structurally plausible without discriminating evidence, selection fails closed as ambiguous. Conflicting legacy/newer evidence also fails closed. Unsupported top-level or nested fields fail closed instead of being silently ignored.

The output preserves source-family vocabulary. A legacy `title` is not silently relabeled as a newer `achievement`, and a newer `monsterClass` remains a distinct category.

## Supported encodings and bounds

Supported source encodings are:

- raw protobuf;
- XZ container;
- LZMA-alone stream;
- the reviewed Tibia LZMA-alone header variant whose uncompressed-size bytes require normalization before standard LZMA decoding.

All source reads and decompression are bounded. Trailing/concatenated compressed streams, truncated streams, oversized expansion and malformed protobuf fail closed. Defaults are 64 MiB encoded input, 256 MiB decoded input and 2,000,000 top-level records; the CLI permits smaller or reviewed larger explicit bounds.

## Record and finding semantics

Supported records retain only fields represented by the selected schema: IDs, names, source-specific descriptive/scalar fields, outfits/colors, house metadata and coordinates. Records are sorted deterministically while `sourceOrdinal` preserves original category order for evidence and duplicate reporting.

The report explicitly records:

- duplicate IDs per source category;
- missing `id` or `name` fields used by the reference index contract;
- duplicate occurrences of singular protobuf fields.

Quest records intentionally remain **ID/name inventory only**. Presence in StaticData does not prove quest stages, storages, handlers, map positions, rewards, completion, runtime behavior, content parity or Real Tibia gameplay correctness.

## CLI

```bash
python tools/ai-agent/tibia_staticdata_reference_index_tool.py \
  --manifest /outside-git/reference-manifest.json \
  --source /outside-git/staticdata.dat \
  --input-id staticdata \
  --output artifacts/tibia-staticdata-index.json
```

Output is create-new/no-clobber by default. `--overwrite` performs an atomic explicit replacement. The output may not alias the source or manifest.

## Validation

Canary-owned tests construct protobuf fixtures independently of the production parser and cover:

- legacy and newer schema selection;
- ambiguous/conflicting/unsupported schema failures;
- source-category preservation and legacy/newer house field ordering;
- duplicate IDs, missing fields and quest inventory-only output;
- raw, XZ, LZMA-alone and Tibia-header LZMA decoding;
- decompression bounds and malformed protobuf;
- exact manifest source size/SHA-256 binding;
- deterministic JSON and output collision/no-clobber behavior.

An opt-in test accepts `CANARY_TIBIA_STATICDATA_FILE` for a real user-supplied file outside Git. CI never requires or uploads proprietary client data.
