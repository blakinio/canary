# Unified OTBM World Index

## Purpose

`tools/ai-agent/otbm_world_index_tool.py` builds a deterministic, read-only index of a complete OTBM world and answers bounded queries without rescanning the map for every agent task.

It is intended as the shared map-evidence layer for later quest, NPC, spawn, teleport, storage and semantic-diff validators.

The implementation extends the existing native `otbm_item_audit_scan.cpp` parser. It does not introduce a second OTBM binary parser and preserves the scanner's original two-argument JSON mode.

## Safety boundary

The tool:

- never edits the input map;
- opens the OTBM as a stable source and verifies that its size, timestamp and SHA-256 do not change during the build;
- writes a new `.widx` file atomically through a temporary path;
- refuses symlink output targets;
- refuses accidental overwrite unless `--overwrite` is explicit;
- keeps generated indexes and manifests outside Git;
- reports unknown item-attribute tails instead of guessing their layout.

A successful index is evidence about map contents. It is not authorization to alter the map or delete unresolved identifiers.

## Build

Compile the existing native scanner:

```bash
c++ -O2 -std=c++20 -Wall -Wextra -Wpedantic -Werror \
  tools/ai-agent/otbm_item_audit_scan.cpp \
  -o tools/ai-agent/otbm_item_audit_scan
```

Build an index:

```bash
python tools/ai-agent/otbm_world_index_tool.py build world.otbm \
  --scanner tools/ai-agent/otbm_item_audit_scan \
  --output artifacts/world.widx \
  --manifest artifacts/world.widx.json
```

The scanner also retains its legacy contract:

```bash
tools/ai-agent/otbm_item_audit_scan world.otbm artifacts/item-scan.json
```

## Query commands

```bash
# Header, counts and provenance
python tools/ai-agent/otbm_world_index_tool.py summary \
  artifacts/world.widx \
  --manifest artifacts/world.widx.json

# All placements of an item
python tools/ai-agent/otbm_world_index_tool.py item \
  artifacts/world.widx 1945 --limit 100 --offset 0

# Mechanics
python tools/ai-agent/otbm_world_index_tool.py action artifacts/world.widx 45001
python tools/ai-agent/otbm_world_index_tool.py unique artifacts/world.widx 60012
python tools/ai-agent/otbm_world_index_tool.py house-door artifacts/world.widx 7
python tools/ai-agent/otbm_world_index_tool.py teleport-destination \
  artifacts/world.widx 33210,31820,7

# Exact tile and complete stack
python tools/ai-agent/otbm_world_index_tool.py position \
  artifacts/world.widx 33210,31820,7

# Inclusive 3D region
python tools/ai-agent/otbm_world_index_tool.py region \
  artifacts/world.widx \
  33200,31800,7 33250,31850,8 \
  --limit 100 --offset 0 \
  --tile-limit 100 --tile-offset 0
```

All list queries are paginated. `--limit` is bounded to 10,000 so an agent cannot accidentally print millions of placements into a prompt or log. Every result includes the exact `totalCount` even when the returned page is truncated.

## Indexed evidence

The index stores:

- every tile position, tile kind, house ID and tile flags;
- every inline or node item placement;
- nested item depth up to the scanner's verified maximum;
- item-ID postings;
- `actionId`;
- `uniqueId`;
- `houseDoorId`;
- teleport source placement and destination;
- unique 256×256×floor area postings;
- map header versions and item versions;
- total/raw tile-area counts and unknown-attribute diagnostics.

A placement result contains a stable ordinal for that index build, exact position, item ID, source (`inline` or `node`), item depth and mechanic attributes when present.

## Binary format v1

The `.widx` file begins with the eight-byte magic `OTSWIDX1` and a fixed 256-byte little-endian header. Its sections are deterministic and contiguous:

1. 65,536-entry item directory;
2. unique area directory;
3. area-to-tile postings;
4. tile records;
5. placement records;
6. mechanic records;
7. item-to-placement postings.

The JSON manifest is the public provenance and summary contract `canary-otbm-world-index-v1`. The binary layout is validated before any query is accepted. Record sizes and section offsets are included in the header and checked against exact v1 expectations.

The index is intentionally uncompressed. Random queries can memory-map it and resolve records without loading a huge JSON document or maintaining a database. The manifest records its size and SHA-256.

## Determinism

For a stable input map and scanner binary, repeated builds produce byte-identical `.widx` output.

Deterministic ordering is:

- areas by floor, base Y, base X;
- tiles inside an area by Y then X;
- placements by tile stack traversal order;
- item postings by placement ordinal;
- mechanics by placement ordinal.

Repeated raw OTBM tile-area nodes with the same 256×256×floor key are merged into one query area. Duplicate exact tile positions are rejected.

## Real-map validation

The implementation was tested outside Git against the supplied map with SHA-256:

```text
a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
```

Measured result:

```text
source size: 184,776,037 bytes
build wall time: 32.72 seconds
peak RSS: 419,140 KiB
binary index size: 842,280,592 bytes
tiles: 17,972,761
placements: 23,359,571
used item IDs: 23,852
mechanic placements: 9,339
unique query areas: 1,171
raw OTBM tile-area nodes: 1,175,983
unknown attribute tails: 0
maximum item depth: 2
```

The Cobra Bastion bounds `33377,32631,7` through `33417,32671,7` returned 1,681 tiles and 2,627 item placements, matching the factual renderer's previous region counts.

These values describe that exact source snapshot and are not hard-coded expectations.

## Failure behavior

The build fails without publishing a partial index when:

- the OTBM is malformed or changes during scanning;
- a tile or placement exceeds v1 integer limits;
- the two scanner passes disagree;
- an area contains duplicate tile positions;
- a section size or offset overflows;
- the generated binary fails validation;
- scanner JSON and binary summaries disagree;
- output paths violate overwrite or symlink rules.

Queries fail on corrupt magic/version, invalid offsets, unsupported record sizes, escaped postings, invalid mechanic flags, inconsistent tile ownership or out-of-range coordinates.

## Current limitations

- The index records map evidence, not active Lua behavior. Use the script-resolution audit for runtime-handler correlation.
- Item walkability and appearance flags are not embedded yet; later geometry validation will join approved appearance/item metadata.
- Spawn, NPC and storage graphs are later roadmap phases.
- The binary is local-endian independent only because v1 explicitly requires little-endian encoding and readers decode it as little-endian.
- `.widx` files can be several times larger than compressed OTBM input. They are generated cache artifacts, not distribution assets.
- No map-writing capability is included.

## Focused tests

```bash
PYTHONPATH=tools/ai-agent \
  python -m unittest -v tools/ai-agent/test_otbm_world_index.py
```

Coverage includes legacy scan compatibility, all query dimensions, deterministic output, bounded pagination, repeated raw area merging, duplicate tile rejection, corrupt headers, overwrite protection and symlink output rejection.
