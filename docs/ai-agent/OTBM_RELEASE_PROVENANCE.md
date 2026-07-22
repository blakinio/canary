# OTBM Release Provenance and Certification Freshness

`otbm_release_provenance_tool.py` compares exact versioned OTBM evidence bills of materials without treating file timestamps as freshness proof.

## Release BOM

`canary-otbm-release-bom-v1` contains:

- a stable reviewed `releaseId`;
- exact SHA-256 components such as source map, World Index, scanner, items, appearances, asset index, datapack, Script Resolution, transition/landmark/interaction registries, quality, coverage or certification evidence;
- explicit named evidence/certification dimensions with `dependsOn` component IDs.

Component and dimension IDs are unique. A dimension may depend only on components declared in the same BOM.

## Freshness comparison

When both a previous and current BOM are supplied, `canary-otbm-release-provenance-v1` reports exact component additions, removals and hash/format/kind changes. A current dimension is marked `stale` only when one of its explicitly declared dependencies changed; unrelated dimensions stay `current`.

With no previous BOM, dimensions remain `not-compared`. The tool does not invent a historical baseline.

## Boundaries

- Upload, modified and filesystem timestamps are never freshness evidence.
- The comparator does not rerun Semantic Diff, static validators or Physical E2E.
- A stale dimension means its prior evidence must be re-established by the owning validator; it does not prove a regression.
- A current dimension means none of its declared exact dependencies changed between the compared BOMs; it does not prove runtime gameplay correctness.
- The tool never modifies maps, assets, sources, evidence or certification records.

## CLI

```sh
python tools/ai-agent/otbm_release_provenance_tool.py \
  --current release-bom.json \
  --previous previous-release-bom.json \
  --output release-provenance.json
```

`--previous` is optional. Output is create-new/no-clobber by default; `--overwrite` performs atomic replacement. Symlink output and input/output aliases are rejected.
