# OTServBR ↔ CrystalServer global OTBM parity baseline — 2026-07-25

## Decision

The selected maps are the same global-world coordinate frame and are compatible with the same canonical World Index and Semantic OTBM Diff formats.

- CrystalServer global map: `data-global/world/world.otbm`.
- Current OTServBR map: external `otservbr(4).otbm`.
- Shared canonical 256×256×floor area keys: `1159`.
- Exact unchanged tiles: `17214872`.
- Exact positions with at least one structural, static or item/mechanic difference: `1884169`.

The first draft of this baseline used `data-crystal/world/world.otbm`, which is CrystalServer's separate small custom/test world. That source selection was wrong for comparison with the full OTServBR world. PR #913 was returned to draft before merge, the first report was invalidated, and every map-derived count below was regenerated from `data-global/world/world.otbm`.

No finding in this report authorizes automatic copying, map mutation, ID remapping or treating CrystalServer as authoritative.

## Inputs and provenance

### Current OTServBR map

| Field | Value |
|---|---|
| Role | current target map |
| External filename | `otservbr(4).otbm` |
| Size | `184776037` bytes |
| SHA-256 | `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2` |
| Repository status | external only; not committed |

### CrystalServer global reference

| Field | Value |
|---|---|
| Role | read-only donor/reference evidence |
| Repository | `zimbadev/crystalserver` |
| User-selected branch | `main` |
| Pinned commit | `75e9c72e33ce2c3f193e4f2d2ff17ebae4bbfaac` |
| Canonical path | `data-global/world/world.otbm` |
| Git blob SHA-1 | `ca281acba48de2ebdf785b2d025f1e4696d3cc5f` |
| Repository blob size | `52836960` bytes |
| Repository blob SHA-256 | `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034` |
| Repository status | external read-only input; not committed |

Despite the `.otbm` filename, the tracked repository blob is gzip-compressed. The canonical scanner was run only after bounded gzip verification and decompression:

| Payload field | Value |
|---|---|
| Decompressed OTBM size | `186660172` bytes |
| Decompressed OTBM SHA-256 | `4b2099f38df05d4be68d1ba1265754e9fd6da09742025d92644fa4b1a12eb120` |
| OTBM prefix | four zero bytes followed by the canonical escaped root node |

The repository blob hash and the decompressed OTBM payload hash are separate provenance axes and must not be substituted for each other.

Acquisition evidence:

- workflow run: `30158472867`;
- one-day artifact: `8619590722`, `crystal-global-otbm-75e9c72`;
- artifact archive digest: `sha256:927dd61dfb3b56545ba3133e1608e468ed197835f0660cbab7b4f79e6d2dc019`;
- artifact contained the exact compressed map, provenance JSON and the pinned `data-global/world` / `data-crystal/world` Git tree listing;
- the temporary acquisition workflow removed itself and no map or archive is part of the durable PR diff.

The pinned tree also contains supplemental event, quest, custom and world-change `.otbm` fragments. This baseline selects only the canonical `data-global/world/world.otbm`; it does not merge or reinterpret those fragments.

## Exact analysis implementation

The analysis source was exported from PR head `f6ddfe37bc55b04e29c0ea1fa94cb1146abc2161` by workflow run `30158587982` and one-day artifact `8619618393`.

Both maps were indexed with the same compiled `tools/ai-agent/otbm_item_audit_scan.cpp` binary:

```text
scanner SHA-256: 5e78f93c2d5488c2b7eba33a726ea5a109caaee69776bf152dbf2c1261bbcc2f
World Index format: canary-otbm-world-index-v1
OTBM version: 4 / 4
items major/minor: 4 / 4 on both maps
unknown attribute tails: 0 / 0
maximum item depth: 2 / 2
```

Generated maps, `.widx` files, manifests, item scans and the full Semantic Diff JSON remained outside Git.

### World Index provenance

| Dimension | Crystal global | OTServBR |
|---|---|---|
| World Index size | `887242734` | `842280592` |
| World Index SHA-256 | `c2bc741ad023f9bd7cad64a7b3b60adb1143243c8def37d2f3ab64e07d6b9ed3` | `6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a` |
| Tiles | `18997668` | `17972761` |
| Item placements | `24504223` | `23359571` |
| Mechanic placements | `9323` | `9339` |
| Canonical areas | `1197` | `1171` |
| Raw OTBM tile-area nodes | `167838` | `1175983` |
| Used item IDs | `25324` | `23852` |

The very different raw tile-area-node counts are source-serialization evidence. They do not imply a proportional gameplay or geometry difference because both sources normalize into similar canonical area sets.

## Coordinate and area alignment

### Exact indexed bounds

| Map | Minimum tile | Maximum tile |
|---|---|---|
| Crystal global | `1006,1013,0` | `34143,33812,15` |
| OTServBR | `1340,1643,0` | `34143,33812,15` |

### Canonical area overlap

| Dimension | Count |
|---|---:|
| Crystal areas | `1197` |
| OTServBR areas | `1171` |
| Shared area keys | `1159` |
| Crystal-only area keys | `38` |
| OTServBR-only area keys | `12` |
| Crystal tiles inside shared areas | `18884125` |
| OTServBR tiles inside shared areas | `17943962` |
| Crystal tiles inside Crystal-only areas | `113543` |
| OTServBR tiles inside OTServBR-only areas | `28799` |

The maps are therefore position-aligned enough for exact-coordinate comparison. A coordinate transform is not required for this pair.

## Static world inventory

| Dimension | Crystal global | OTServBR |
|---|---:|---:|
| House tiles | `109744` | `109539` |
| Distinct house IDs | `995` | `993` |
| House ID range | `2628..3702` | `2628..3696` |
| Distinct action IDs | `736` | `697` |
| Action-ID placements | `2311` | `2248` |
| Distinct unique IDs | `597` | `587` |
| Unique-ID placements | `597` | `587` |
| Distinct house-door IDs | `39` | `39` |
| House-door placements | `4527` | `4674` |
| Distinct teleport destinations | `697` | `680` |
| Teleport placements | `2406` | `2342` |

These are exact static inventories in each source namespace. Numeric equality or difference alone does not establish intended correspondence, missing runtime behavior or a safe remap. Crystal Lua/XML handler parity was not executed or inferred.

## Full exact-position Semantic Diff

Command shape:

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_semantic_diff_tool.py diff \
  --artifact-root <external-artifact-root> \
  --before-index crystal-global.widx \
  --before-manifest crystal-global.widx.json \
  --after-index otservbr.widx \
  --after-manifest otservbr.widx.json \
  --before-map crystal-global-world.payload.otbm \
  --after-map 'otservbr(4).otbm' \
  --sample-limit 100 \
  --output OTBM_SEMANTIC_DIFF_GLOBAL.json
```

Result provenance:

```text
format: canary-otbm-semantic-diff-v1
scope: full-index
report size: 64178 bytes
report SHA-256: e093fefdf603120933a52faf3bcd625cb94c650f7acba87acf4d95f66a56b04a
elapsed: 656.27 seconds
source maps modified: false
heuristic item matching: false
exact counts preserved: true
appearance/walkability evidence supplied: false
correlation reports supplied: none
sample count: 100
samples truncated: true
```

### Tile-position summary

| Dimension | Count |
|---|---:|
| Crystal tiles | `18997668` |
| OTServBR tiles | `17972761` |
| Shared exact tile positions | `17871388` |
| Exact unchanged tiles | `17214872` |
| Changed shared positions | `656516` |
| Crystal-only tile positions | `1126280` |
| OTServBR-only tile positions | `101373` |
| Positions with at least one finding | `1884169` |

### Exact findings by kind

| Finding kind | Count |
|---|---:|
| `tile-removed` | `1126280` |
| `tile-added` | `101373` |
| `tile-kind-changed` | `95` |
| `tile-flags-changed` | `19530` |
| `house-id-changed` | `95` |
| `item-removed` | `1271092` |
| `item-added` | `126440` |
| `item-replaced` | `631302` |
| `stack-order-changed` | `677` |
| `mechanic-removed` | `66` |
| `mechanic-added` | `181` |
| `house-door-id-changed` | `1` |
| `teleport-source-removed` | `69` |
| `teleport-source-added` | `32` |
| `teleport-destination-changed` | `41` |
| **Total** | **`3277274`** |

### Classification and evidence totals

| Axis | Value | Count |
|---|---|---:|
| Classification | added | `228026` |
| Classification | removed | `2397507` |
| Classification | changed | `651741` |
| Evidence | structural | `1267162` |
| Evidence | static | `19625` |
| Evidence | semantic | `1990487` |

The full report intentionally retains only 100 bounded samples. The exact counters above are not sample estimates. Because no appearances catalogue was supplied, this baseline does not emit ground or walkability regressions. Because no correlation report was supplied, it does not claim handler, quest, storage, spawn/NPC or route impact.

## Semantic Diff correction validated by the real inputs

The World Index contract is deterministic and area-major:

1. areas ordered by `(z, baseY, baseX)`;
2. tiles inside each area ordered by `(y, x)`.

The prior full-index path incorrectly assumed that concatenated physical tile records were globally position-sorted. The correction:

- compares exact compound area/tile keys;
- keeps exact position equality as the only cross-index tile identity;
- adds no parser, index format, matcher, pathfinder or renderer;
- avoids constructing discarded finding objects after the bounded sample budget is full;
- bulk-counts unmatched validated areas while preserving exact item/mechanic totals;
- preserves report format, retained stable IDs and fail-closed correlation behavior.

The corrected implementation completed this overlapping 18–19 million tile comparison and passes 34 focused tests, including bounded and full-index adjacent-area ordering, bounded-sample exact totals and fully disjoint-area exact counts.

## What this baseline proves

- The exact target map and exact pinned CrystalServer global source are reproducible.
- The tracked Crystal blob is gzip transport content and the decompressed OTBM payload is separately pinned.
- Both maps are readable by the same canonical scanner and World Index contract.
- Their OTBM and item versions are compatible.
- They share the same broad coordinate frame and `1159` canonical areas.
- `17214872` exact tile positions are unchanged under the indexed semantic contract.
- The reported structural, static, item and mechanic totals are exact for the selected full-index comparison.
- Neither source map was modified.

## What this baseline does not prove

- that every Crystal-only or OTServBR-only tile should be copied or removed;
- that an item replacement is a defect rather than intentional version/content divergence;
- that matching numeric item, house, AID, UID or town identifiers have the same intent;
- that any Crystal Lua/XML handler exists or is active in OTServBR;
- runtime behavior, gameplay parity, route reachability or Physical E2E;
- global completeness or an overall parity percentage;
- that CrystalServer is authoritative.

## Evidence gate for continuation

The next useful comparison is bounded, not another unfiltered global sample. A selected city, quest or mechanic should provide reviewed exact bounds or semantic landmarks and then reuse:

- this exact source-map and World Index provenance;
- bounded Semantic Diff with a larger local sample budget;
- OTBM item/mechanic audit;
- Script Resolution for current OTServBR Lua/XML handlers;
- Reachability and route interaction evidence where access matters;
- factual rendering only through the existing renderer when visual review is justified.

Unresolved, conflicting or missing handler evidence must remain explicit. No finding alone authorizes map mutation or candidate materialization.
