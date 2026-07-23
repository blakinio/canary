# Tibia Client Reference Manifest

`canary-tibia-client-reference-manifest-v1` is the TCR-001 provenance boundary for exact, explicitly selected files from one user-supplied Tibia client reference package.

It is read-only evidence tooling. It does not parse StaticData or StaticMapData semantics, inspect a client directory recursively, execute selected content, infer an exact client build from names, copy proprietary inputs into Git, or authorize OTBM/client/runtime mutation.

## Inputs and trust boundary

The caller supplies exactly one package root and one or more `ID=RELATIVE_PATH` selections. Every selected path must be POSIX-style and relative to that root. The implementation rejects absolute paths, `.`/`..` segments, backslashes, missing files, directories, symlinks in any selected path component, duplicate logical IDs and duplicate resolved or hardlinked files.

The package root itself must be an existing non-symlink directory. Its absolute path is never emitted automatically. `packageRootLabel` is display metadata only and is never version proof.

Each selected file is size-checked before hashing. TCR-001 defaults to an 8 GiB per-file bound (`8589934592` bytes), configurable with `--max-file-bytes`; the exact applied bound is recorded as `policy.maxSelectedFileBytes`. Files are SHA-256 hashed with bounded streaming reads, and a file that changes identity, size or modification time during hashing fails closed.

## Build evidence

`clientBuild.evidence` is exactly one of:

- `proven` — an exact build value is supplied and supported by independent provenance outside this manifest;
- `declared` — an exact build value is supplied as a declaration but is not independently proven;
- `unknown` — no build value is emitted;
- `conflicting` — no single value is emitted and at least two distinct conflicting values are retained.

Filenames and directory labels never promote `declared` or `unknown` evidence to `proven`.

## Determinism and output safety

The caller provides `observedAt` explicitly as a timezone-aware ISO-8601 value and provides an exact 40- or 64-hex parser implementation revision. The tool does not synthesize a current timestamp, so stable inputs and arguments produce byte-identical JSON.

Selected inputs are sorted by logical ID. Generated index pins are optional `ID=SHA256` references and are also sorted; TCR-001 does not open arbitrary generated-index paths. Optional package metadata is a sorted string map.

Output is create-new/no-clobber by default. A symlink output, non-regular existing output, or output alias/hardlink collision with a selected input fails closed. `--overwrite` uses a same-directory temporary file, `fsync`, and atomic `os.replace`.

## CLI

Example with build state intentionally unknown:

```bash
python tools/ai-agent/tibia_client_reference_manifest_tool.py \
  --package-root /outside-git/tibia-client-reference \
  --reference-id tibia-client-reference-001 \
  --package-label "operator supplied reference package" \
  --source-role official-client-reference \
  --observed-at 2026-07-23T16:40:00+02:00 \
  --client-build-evidence unknown \
  --parser-revision "$(git rev-parse HEAD)" \
  --select staticdata=data/staticdata.dat \
  --select staticmapdata=data/staticmapdata.dat \
  --output artifacts/tibia-client-reference/manifest.json
```

The example paths are illustrative. Do not copy user-supplied client files into the repository to run this tool.

A later producer can pin its exact output without granting TCR-001 access to that output path:

```bash
--generated-index staticdata-index=<64-hex-sha256>
```

## Manifest fields

- `format`: `canary-tibia-client-reference-manifest-v1`;
- `schemaVersion`: `1`;
- `referenceId`: operator/task-assigned stable reference identifier;
- `packageRootLabel`: display-only package label;
- `sourceRole`: explicit reviewed role, normally `official-client-reference`;
- `observedAt`: explicit observation/import metadata timestamp;
- `clientBuild`: evidence state plus value/conflicts according to the rules above;
- `parserRevision`: exact implementation revision;
- `selectedInputs`: explicit relative path, byte size and SHA-256 for every selected input;
- `generatedIndexes`: optional exact output hashes from later TCR producers;
- `packageMetadata`: optional string metadata;
- `summary`: selected input count/bytes and generated-index count;
- `policy`: explicit-selection, non-recursive, non-execution, non-version-proof and file-size-bound facts.

The JSON schema is `docs/ai-agent/TIBIA_CLIENT_REFERENCE_MANIFEST.schema.json`.

## Acceptance and non-goals

TCR-001 proves only deterministic package/input provenance for selected files. It does not prove:

- the claimed/declared build is authentic unless separately evidenced as `proven`;
- StaticData or StaticMapData schema correctness;
- any mapping between client object IDs and Canary/OTBM item IDs;
- quest, house, proficiency, minimap or gameplay parity;
- runtime behavior or physical-client behavior;
- suitability of any reference finding for automatic mutation.

TCR-002 and later packages must consume this exact provenance boundary rather than rediscovering or recursively ingesting a client package.
