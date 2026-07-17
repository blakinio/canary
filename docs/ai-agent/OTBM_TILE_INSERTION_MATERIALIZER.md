# OTBM bounded raw tile insertion materializer

`tools/ai-agent/otbm_tile_insertion_materializer_tool.py` inserts one or more reviewed complete donor tile subtrees into a distinct copy of a current OTBM map.

This is a structural-confinement tool, not a gameplay editor.

## Hard boundary

A selected tile may be inserted only when all of the following are true:

- the absolute `x,y,z` position is absent from the current raw tile-span report and current World Index;
- the same absolute position exists exactly once in the donor map;
- the canonical parent `(x & 0xFF00, y & 0xFF00, z)` `TILE_AREA` already exists exactly once in current;
- the approved current parent `TILE_AREA` raw SHA-256 and byte length still match;
- the approved donor tile raw SHA-256, raw byte length, node type, and canonical World Index SHA-256 still match;
- current/donor OTBM and items headers are compatible and both maps have zero unknown attribute tails.

The materializer does **not**:

- create a missing `TILE_AREA`;
- delete or replace an existing tile;
- translate coordinates;
- rewrite teleport destinations;
- convert an existing ordinary tile to a house tile or vice versa;
- insert, delete, or reorder individual item-stack entries;
- use a generic node or full-map serializer;
- modify either source map in place.

## Physical write rule

The existing native structural scanner first accepts the complete map. The materializer then reuses:

- `scan_tile_area_spans()` for the exact target parent `TILE_AREA` physical span;
- `scan_tile_spans()` for the exact donor tile raw span.

The complete donor tile subtree, including its node framing, is copied immediately before the existing parent `TILE_AREA` `NODE_END`. For multiple insertions into one parent, new tiles are emitted in deterministic `(z,y,x)` order. No existing current child is reordered.

## Approval contract

Use `docs/ai-agent/OTBM_TILE_INSERTION_APPROVAL.schema.json`.

The approval must use:

```text
format = canary-otbm-tile-insertion-approval-v1
schemaVersion = 1
decision = approved
```

Each selection pins:

- `position`;
- canonical `areaKey`;
- reviewed current parent `TILE_AREA` raw SHA-256 and byte length;
- donor raw tile SHA-256 and byte length;
- donor node type (`5` ordinary tile or `14` house tile);
- donor canonical World Index tile SHA-256.

The top-level provenance pins the current/donor maps, World Index files, and World Index manifests.

## Structural proof

Before publication the tool requires all of these checks:

1. current and donor provenance match the approval;
2. selected positions are absent in current and unique in donor;
3. target current parent areas are unique and match their approved raw state;
4. the candidate is created by insertion only;
5. hashing the output while excluding only the inserted raw spans produces the exact complete current map SHA-256 and byte count;
6. every inserted raw output tile equals the donor raw subtree byte-for-byte;
7. the native scanner reparses the candidate;
8. a canonical output World Index is rebuilt;
9. every inserted canonical output tile equals its donor tile;
10. bounded Semantic OTBM Diff is generated for the minimal selected-position box;
11. source maps and scanner still match their pre-operation pins.

Only then are the output map copy and evidence directory published with create-new semantics.

## CLI

```sh
python tools/ai-agent/otbm_tile_insertion_materializer_tool.py \
  --artifact-root artifacts/otbm-insertion \
  --current-map /path/to/current.otbm \
  --donor-map /path/to/donor.otbm \
  --scanner /path/to/otbm_area_materializer_scan \
  --approval approval.json \
  --current-index current.widx \
  --current-manifest current.widx.json \
  --donor-index donor.widx \
  --donor-manifest donor.widx.json \
  --output-map output.otbm \
  --evidence-dir evidence
```

Approval/index/manifest/output/evidence paths are confined below `--artifact-root` where required by the existing materialization safety helpers. Source maps and scanner may be supplied from separate immutable locations.

## Result contract and rollback

The result uses `canary-otbm-tile-insertion-result-v1` and records operation counts, inserted raw spans, retained-current proof, donor equality, World Index equality, Semantic Diff evidence, source pins, and safety non-claims.

Rollback is deletion of the generated output copy. The source maps are never modified.

A successful result does not prove script correctness, reachability, gameplay correctness, or physical-client behavior.
