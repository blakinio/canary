# Compact OTBM Evidence Gateway

`otbm_evidence_gateway_tool.py` composes bounded exact extracts from already-produced canonical OTBM JSON reports. It is a transport/query boundary, not a new validator.

## Manifest

`canary-otbm-evidence-gateway-manifest-v1` declares up to 32 source JSON files relative to the manifest directory. Every source pins:

- a stable source ID;
- safe relative path;
- exact SHA-256;
- expected report `format`;
- one or more globally unique extract IDs with JSON Pointer selectors.

The gateway supports at most 128 extracts per manifest. Each serialized extracted value is capped at 256 KiB. Unsafe relative paths, symlinks, hash mismatches, format mismatches, missing pointers and oversized extracts fail closed.

## Bundle

`canary-otbm-evidence-bundle-v1` retains:

- exact source ID/path/hash/format provenance;
- each extract ID, source ID and JSON Pointer;
- the exact extracted JSON value;
- a SHA-256 of the canonical serialized extracted value;
- deterministic manifest and bundle hashes.

The gateway does not reinterpret the meaning of a source finding. Downstream consumers remain responsible for using the source contract correctly.

## Ownership boundary

The gateway:

- does not parse OTBM;
- does not validate source-report semantics beyond exact format/hash identity and pointer existence;
- does not pathfind;
- does not run Physical E2E;
- does not own downstream scenario design, runtime execution or acceptance decisions.

## CLI

```sh
python tools/ai-agent/otbm_evidence_gateway_tool.py \
  --manifest evidence-gateway.json \
  --output compact-evidence.json
```

Output is create-new/no-clobber by default. `--overwrite` performs atomic replacement. The output must not alias the manifest.
