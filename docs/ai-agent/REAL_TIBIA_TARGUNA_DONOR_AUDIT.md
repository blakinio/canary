# Real Tibia Targuna donor isolation audit

This is a bounded, read-only donor-evidence audit. It does not write OTBM data and does not authorize whole-cluster import.

## Provenance

- Canary commit: `d88e7f354eb5b33068cdded7696e9cdb89b05268`
- CrystalServer commit: `fc0d53b9f9965463b6082c07e6d3d482294541a7`
- Baseline OTBM SHA-256: `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`
- Crystal logical OTBM SHA-256: `4b2099f38df05d4be68d1ba1265754e9fd6da09742025d92644fa4b1a12eb120`
- Successful audit workflow run: `29526630176` (run #5)
- Evidence artifact SHA-256: `f75965735e5690740e546e1d6a7523ae78157f4836086d8715d3a6f0d675a5da`

## Source and actor inventory

- Targuna source files: **42**
- Monster definitions: **16**
- NPC definitions/references: **11**
- Selected static actor placements: **197**
- Literal/source/actor/house anchors: **331**
- Houses: **2** (`Targuna Cottage 1`, `Targuna Cottage 2`)
- Storage dependencies: **27**
- Literal item-ID dependencies: **7**
- Engine/API call families: **36**

## Spatial clusters

| Cluster | Evidence labels | Anchors | Audit bounds | Semantic findings | Crystal mechanics | Teleports |
|---|---|---:|---|---:|---:|---:|
| `cluster-01` | hidden-lizard-temple, targuna, main-continent-dependency, aragonia, crimson-court, targuna-island | 91 | `[31488, 31488, 4] → [32255, 32255, 10]` | 272,575 | 184 | 31 |
| `cluster-02` | targuna | 1 | `[32000, 30720, 5] → [32767, 31487, 7]` | 123,968 | 651 | 171 |
| `cluster-03` | crimson-court, herald-of-fire, targuna | 88 | `[32000, 30976, 5] → [33791, 33279, 15]` | 2,004,158 | 8,405 | 1,976 |
| `cluster-04` | aragonia, targuna, targuna-sandcastles | 151 | `[33024, 32256, 6] → [34047, 33023, 9]` | 627,971 | 500 | 104 |

The cluster bounds are deterministic review scopes derived from source, actor and house anchors with 256×256 cell connectivity/context. They are intentionally coarse and are **not** authorization to copy every changed tile inside the bounds.

## Dependency boundary

The machine-readable report preserves the exact selected source-file list, actor definitions and static actor positions, house records, storage names, literal item IDs, registration tokens and API-call counts. Per-cluster mechanic identifier/count inventories cover action IDs, unique IDs, house-door IDs and teleport totals for both baseline and Crystal evidence.

Placement-level mechanic records and bounded semantic finding samples remain in the successful workflow artifact rather than Git, preventing a multi-megabyte raw evidence dump from becoming repository state.

## Import boundary

This audit identifies bounded donor candidates and dependencies only. It does not prove live Real Tibia parity, does not execute Lua, does not resolve dynamic positions, does not merge datapacks and does not authorize map writing. Any future materialization proposal must review each cluster independently, resolve relevant runtime/script evidence and use the repository's bounded OTBM planning/materialization contracts rather than treating these coarse bounds as a copy request.
