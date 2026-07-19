# Thais semantic landmark evidence

This document records the bounded static evidence used to bind `thais.temple` and `thais.depot` in `OTBM_SEMANTIC_LANDMARKS.json` for the first reference OTBM-aware physical route.

The evidence is read-only. The source OTBM, generated World Index, appearances binary and generated Reachability reports remain outside Git. This document does not claim physical-client gameplay success; that remains the downstream `OTBM-E2E-005` runtime proof.

## Exact provenance

| Evidence | SHA-256 | Size |
|---|---|---:|
| Source OTBM | `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2` | 184,776,037 bytes |
| Canonical World Index | `6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a` | 842,280,592 bytes |
| Current native scanner artifact | `63f278634ff6c55d58d6f75afb711ac5992f6dd9ff5cd9af7ef0258a5bc682bb` | 86,136 bytes |
| Client appearances | `aa44a154f30c7ed59acc25f246286396e4043851ef0b54ef3cf3951e46d1ce50` | 4,862,287 bytes |
| Broad depot-candidate Reachability report | `abde0a2891593b43ba9d5082a9350a7de9f07738bbbc3af858ba86e80e508de5` | 671,525 bytes |
| Final selected-route Reachability report | `88b53c4fd45c627137ca47d5804bff8ef98df5b0e2643b02b0d5e10129ba349a` | 157,746 bytes |

The scanner artifact came from the successful merged interaction-aware Reachability workflow for PR #580. Its source is the current `tools/ai-agent/otbm_item_audit_scan.cpp` blob `dbc778b51f91f5a95203bb491ef772bfd3ab1e24`.

The exact source map was indexed again locally with that scanner. The resulting World Index is byte-identical by SHA-256 to the baseline World Index recorded by the merged exact-map audit in PR #313. The rebuild summary is:

- tiles: `17,972,761`;
- placements: `23,359,571`;
- mechanic placements: `9,339`;
- indexed tile areas: `1,171`;
- raw OTBM tile-area nodes: `1,175,983`;
- used item IDs: `23,852`;
- unknown attribute tails: `0`;
- maximum item depth: `2`.

This proves the registry provenance against the exact selected map and the canonical current World Index contract without committing either binary.

## Thais temple

A read-only exact-map town-metadata query using the existing repository OTBM binary model resolved:

- town id: `8`;
- town name: `Thais`;
- temple position: `[32369,32241,7]`.

The OTBM town layout used by the existing tooling is the normal town id, town name and temple-position record. No coordinate was inferred from memory, minimap text or sprite imagery.

The registry therefore binds:

- landmark: `thais.temple`;
- anchor: `spawn`;
- role: `route-origin`;
- position: `[32369,32241,7]`.

## Thais depot

A read-only exact-map scan using the existing repository OTBM scanning implementation found four nearby depot lockers carrying `ATTR_DEPOT_ID=8`:

- `[32352,32225,7]`;
- `[32354,32225,7]`;
- `[32352,32231,7]`;
- `[32354,32231,7]`.

Current Canary runtime semantics preserve that exact attribute meaning:

- `src/items/containers/depot/depotlocker.cpp` reads `ATTR_DEPOT_ID` into the locker's `uint16_t depotId`;
- `src/lua/creature/actions.cpp` opens `player->getDepotLocker(depot->getDepotId())` and records the same value as `lastDepotId`.

Together with the exact town metadata identifying Thais as town id `8`, these placements are reviewed as the Thais depot lockers. The locker tile itself is not used as a route destination and is not assumed walkable.

### Route-destination selection

The current merged Reachability implementation was run against the exact World Index and exact appearances catalogue. The exploratory region was `[32335,32210,7]..[32385,32260,7]`. Every unique orthogonally adjacent tile to the four reviewed locker positions was tested from the exact temple origin `[32369,32241,7]`.

| Candidate | Strict result | Strict distance |
|---|---|---:|
| `[32351,32225,7]` | unreachable | — |
| `[32351,32231,7]` | unreachable | — |
| `[32352,32224,7]` | unreachable | — |
| `[32352,32226,7]` | confirmed | 66 |
| `[32352,32230,7]` | confirmed | 66 |
| `[32352,32232,7]` | unreachable | — |
| `[32353,32225,7]` | unreachable | — |
| `[32353,32231,7]` | unreachable | — |
| `[32354,32224,7]` | unreachable | — |
| `[32354,32226,7]` | confirmed | 68 |
| `[32354,32230,7]` | confirmed | 68 |
| `[32354,32232,7]` | unreachable | — |
| `[32355,32225,7]` | unreachable | — |
| `[32355,32231,7]` | unreachable | — |

The reviewed selection policy is deterministic: choose the minimum strict distance, then break equal-distance ties by lexicographic `[x,y,z]` order. That selects `[32352,32226,7]`, immediately adjacent to the reviewed locker at `[32352,32225,7]`.

The broad exploratory report contained two unrelated `tile_missing_ground` errors elsewhere in its deliberately oversized region. Therefore it is not used as the final route-health proof.

The selected route was rerun in the smallest inclusive bounding region covering its complete strict path:

- region: `[32347,32216,7]..[32369,32241,7]`;
- coordinate volume: `598`;
- origin: `[32369,32241,7]`;
- destination: `[32352,32226,7]`;
- report `ok`: `true`;
- error findings: `0`;
- route status: `confirmed`;
- strict distance: `66`;
- optimistic distance: `66`;
- path truncated: `false`;
- transition IDs used: none.

The report contains two informational/warning one-way transition findings from indexed mechanics inside the bounded region, but the selected route uses no transition edge. They do not participate in this same-floor strict path.

The registry therefore binds:

- landmark: `thais.depot`;
- anchor: `locker-32352-32225-approach`;
- role: `route-destination`;
- position: `[32352,32226,7]`.

## Boundary

This evidence proves exact-map static anchor identity and strict same-floor reachability for the selected snapshot. It does not prove that a live server/client session can traverse the path under runtime occupancy, dynamic state or timing. The downstream `OTBM-E2E-005` scenario must consume the reviewed registry read-only, rerun exact-map static preflight and then provide the controlled physical OTClient proof.
