# Tibia Proficiency Reference Index

`canary-tibia-proficiency-index-v1` is the TCR-004 deterministic, read-only definition index for one explicitly selected proficiency JSON file whose exact bytes are already pinned by `canary-tibia-client-reference-manifest-v1`.

It is reference evidence only. It does not reparse appearances, update `items.xml`, register Canary runtime proficiencies, validate persistence or protocol behavior, or prove gameplay parity.

## Input and provenance boundary

The caller supplies:

- one stable TCR-001 manifest;
- one selected proficiency source file;
- the exact logical selected-input ID from the manifest.

The producer checks the source byte size and SHA-256 against the manifest before parsing. The manifest and source must be distinct regular files, symlinks are rejected, and both inputs are checked for identity changes during bounded reads.

Supported source encodings are:

- raw UTF-8 JSON;
- bounded XZ;
- bounded LZMA-alone, including the reviewed Tibia-style LZMA header-size normalization used by the earlier TCR producers.

Malformed, truncated, concatenated or over-limit compressed input fails closed.

## Reviewed JSON contract

The top level is an array of proficiency definitions. Each definition preserves source order and contains:

- `ProficiencyId` — required positive unsigned integer;
- `Name` — required non-empty string;
- `Version` — optional unsigned integer;
- `Levels` — required ordered array.

Each level contains:

- `Perks` — required ordered array;
- `XpRequired` — optional unsigned integer.

Each perk requires `Type` and finite numeric `Value`. The reviewed optional fields are:

- `AugmentType`;
- `BestiaryId`;
- `BestiaryName`;
- `DamageType`;
- `ElementId`;
- `Range`;
- `SkillId`;
- `SpellId`.

Unknown fields, duplicate JSON object keys, wrong types, non-finite numbers and values outside the supported unsigned ranges fail closed. This prevents a newer or different file shape from being silently truncated or relabeled.

## Output guarantees

The index preserves:

- exact manifest and selected-source provenance;
- source encoding and decoded byte size;
- source ordinals for definitions, levels and perks;
- complete reviewed definition fields;
- exact array ordering;
- duplicate proficiency-ID findings without overwriting records;
- duplicate-name findings as review evidence;
- deterministic JSON output.

The identifier namespace is explicitly:

```text
client-reference.proficiency-id
```

Its output state is `definition-only`. Numeric equality with an appearance proficiency ID or Canary runtime binding is not declared by this producer.

## CLI

```bash
python tools/ai-agent/tibia_proficiency_reference_index_tool.py \
  --manifest /outside-git/reference/manifest.json \
  --source /outside-git/reference/proficiencies.json \
  --input-id proficiency \
  --output artifacts/tibia-client-reference/proficiency-index.json
```

Output is create-new/no-clobber by default. `--overwrite` writes a same-directory temporary file, flushes it and atomically replaces the target. Output paths that alias the manifest or source fail closed.

Available bounds:

- `--max-source-bytes`;
- `--max-decompressed-bytes`;
- `--max-manifest-bytes`;
- `--max-proficiencies`;
- `--max-levels`;
- `--max-perks`.

## Evidence boundaries

TCR-004 proves only that one exact selected file contains the emitted proficiency definitions.

It does not prove:

- exact client build identity unless the manifest separately records proven build evidence;
- equivalence with `canary-appearances-index-v1` proficiency flags;
- equivalence with `data/items/proficiencies.json` or `items.xml` bindings;
- XP gain/mastery formulas;
- runtime perk application;
- persistence correctness;
- protocol or maintained-client UI correctness;
- gameplay or Real Tibia parity.

Those dimensions remain separate. TCR-007 may later correlate exact TCR-004 IDs with the canonical appearance index and Canary evidence, without creating a second appearance parser.

## Validation

```bash
python -m unittest discover -s tools/ai-agent -p "test_tibia_proficiency_reference_index.py" -v
python -m py_compile \
  tools/ai-agent/tibia_proficiency_reference_index.py \
  tools/ai-agent/tibia_proficiency_reference_index_tool.py \
  tools/ai-agent/test_tibia_proficiency_reference_index.py
python -m json.tool docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX.schema.json > /dev/null
python tools/ai-agent/tibia_proficiency_reference_index_tool.py --help > /dev/null
```

Opt-in validation against an exact external file uses:

```bash
CANARY_TIBIA_PROFICIENCY_FILE=/outside-git/proficiencies.json \
  python -m unittest discover -s tools/ai-agent -p "test_tibia_proficiency_reference_index.py" -v
```

The external source and any generated real-file report remain outside Git.
