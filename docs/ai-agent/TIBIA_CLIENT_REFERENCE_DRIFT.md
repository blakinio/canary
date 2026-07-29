# Tibia Client Reference Drift

`canary-tibia-client-reference-drift-v1` is the deterministic, read-only TCR-009 comparison contract for two complete retained Tibia client-reference snapshot sets.

## Inputs

Each side requires five existing JSON reports:

- final `canary-tibia-client-reference-manifest-v1` with generated-index hashes;
- bootstrap manifest used by the index producers;
- `canary-tibia-staticdata-index-v1`;
- `canary-tibia-staticmapdata-index-v1`;
- `canary-tibia-proficiency-index-v1`.

The producer never opens StaticData, StaticMapData, proficiency source files, asset archives, appearances, sprites or OTBM. It consumes the existing manifests and indexes only.

## Fail-closed provenance gate

Before comparing records, the producer verifies:

- baseline and current reference IDs are distinct;
- final and bootstrap manifests select byte-identical input identities;
- manifest format, schema and parser revision are compatible;
- every final-manifest `generatedIndexes` hash equals the exact report bytes;
- every report source binds to the bootstrap-manifest SHA-256, reference ID and selected input path, size and SHA-256;
- StaticData, StaticMapData and proficiency report formats, schema versions and parser revisions are compatible;
- input paths are regular files, do not traverse symlinks and stay within `--input-root` when supplied;
- duplicate JSON keys and configured file/finding/field-change bounds fail closed.

## Findings

The producer emits deterministic findings for:

- selected input component added, removed or changed;
- StaticData category record added, removed or changed when both sides use the same schema family;
- StaticMapData house added, removed or changed by `houseId`;
- proficiency definition added, removed or changed by `proficiencyId`;
- explicit StaticData `legacy`/`newer` schema-family change.

A StaticData schema-family change uses comparison state:

```text
schema-family-changed-record-comparison-skipped
```

No record-level comparison is attempted across different StaticData families.

Changed records carry bounded JSON-pointer field changes and canonical semantic SHA-256 values. Added and removed records carry only the present-side semantic hash.

## Staleness

Freshness is dependency-scoped, not timestamp-based. A finding invalidates only the declared consumers of its changed component, such as house parity, content correlation or proficiency correlation. The report does not claim that unrelated evidence is stale.

## Proof boundary

The report proves deterministic drift between the two exact retained index sets. It does not prove:

- gameplay correctness or regression impact;
- runtime, persistence, protocol or physical-client behavior;
- OTBM item-ID equivalence, map authority or mutation safety;
- appearance or asset drift, which remain owned by their canonical comparison paths;
- release, staging or production approval.

## CLI

```bash
python tools/ai-agent/tibia_client_reference_drift.py \
  --baseline-manifest /retained/a/manifest.json \
  --baseline-bootstrap-manifest /retained/a/manifest.bootstrap.json \
  --baseline-staticdata /retained/a/staticdata-index.json \
  --baseline-staticmapdata /retained/a/staticmapdata-index.json \
  --baseline-proficiencies /retained/a/proficiency-index.json \
  --current-manifest /retained/b/manifest.json \
  --current-bootstrap-manifest /retained/b/manifest.bootstrap.json \
  --current-staticdata /retained/b/staticdata-index.json \
  --current-staticmapdata /retained/b/staticmapdata-index.json \
  --current-proficiencies /retained/b/proficiency-index.json \
  --parser-revision <exact-merged-producer-revision> \
  --input-root /retained \
  --output /tmp/client-reference-drift.json
```

Retained inputs and outputs remain outside Git.
