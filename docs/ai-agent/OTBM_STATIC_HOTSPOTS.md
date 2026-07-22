# OTBM Static Map Performance Hotspot Analyzer

`otbm_static_hotspots_tool.py` emits `canary-otbm-static-hotspots-v1` static investigation candidates from one exact Unified OTBM World Index.

## Evidence model

The tool consumes a reviewed `canary-otbm-static-hotspot-policy-v1` that pins the exact source-map and World Index SHA-256 values and declares explicit thresholds for:

- placements per tile;
- maximum item depth;
- mechanic-bearing placements per tile;
- indexed tile count per 256x256 World Index area/floor;
- placements per indexed area/floor.

The analyzer walks the existing World Index records only. It does not parse OTBM again, does not build a connectivity graph and does not run a profiler.

## Candidate findings

- `tile-placement-density`;
- `tile-item-depth`;
- `tile-mechanic-density`;
- `area-tile-density`;
- `area-placement-density`.

Thresholds are policy, not inferred intent. A finding means only that exact static structure meets a reviewed investigation threshold.

## Proof boundary

The report never proves CPU, memory, network, database, server tick or client-render performance impact. Runtime profiling and optimization remain owned by the relevant runtime/client subsystem. Static candidates may be used to prioritize bounded profiling, but may not authorize a performance claim or map mutation.

## CLI

```sh
python tools/ai-agent/otbm_static_hotspots_tool.py \
  --policy hotspot-policy.json \
  --world-index world.widx \
  --world-manifest world.widx.json \
  --output hotspots.json
```

Output is create-new/no-clobber by default. `--overwrite` uses atomic replacement. Symlink outputs and input/output collisions are rejected.
