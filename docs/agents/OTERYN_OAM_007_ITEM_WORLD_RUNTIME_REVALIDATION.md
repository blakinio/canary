# OAM-007 — Item and World Runtime Foundation Revalidation

Status: ready

## Bounded scope

Canonical modules, in dependency order:

1. `item-definitions`
2. `item-instances`
3. `world-map-runtime`

Out of scope: `world-zones`, `instances`, houses, spawns, raids, quests, offline OTBM tooling, datapack/map-content migration, protocol/client mutation and OAM-008 implementation.

## Exact task-start baselines

- governance/legacy: `blakinio/canary@c2e181f892ce2f094e887f1da5c6c7df207629c9`
- target: `blakinio/Otheryn@c547d8ad70ef1252624c255476e6cb83fa125e14`
- upstream evidence: `opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f`
- maintained client used for exact runtime proof: `blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

## Final dispositions

| Module | Disposition | Result |
|---|---|---|
| `item-definitions` | `ADAPT` | bounded magic-field add-item registration fix delivered by Otheryn PR #23 |
| `item-instances` | `REUSE` | checked principal runtime instance paths are identical across task-start target, legacy and upstream; no required legacy-only behavior identified |
| `world-map-runtime` | `REUSE` | target/upstream align across the checked runtime boundary; the divergent legacy map fork has no proven target requirement and was not migrated |

## Disposition evidence

### item-definitions → ADAPT

- `src/items/items.cpp` and `src/items/items.hpp` are identical across target, legacy and upstream.
- `src/items/functions/item/item_parse.hpp` was identical at task start.
- `src/items/functions/item/item_parse.cpp` was target/upstream-identical while legacy differed.
- The legacy delta has concrete provenance: merged Canary PR #81 (`a3406fe3d0cb1df32406c9e1292f43b5d90462a7`) fixed upstream issue #3584, where a newly placed magic field failed to affect a creature already standing on the target tile.
- The bounded behavior registers the existing add-item-on-tile handler in addition to the existing step-in handler only for magic-field step-in definitions.
- The unrelated manual healing-rune part of PR #81 was deliberately excluded.

Otheryn PR #23:

- exact final head: `cd6fae153ebe495ec9030c9c729f2ceef06872ef`;
- draft CI #83 and Required #80: PASS;
- ready-triggered CI #84 and Required #81: PASS;
- autofix.ci #74: PASS;
- Windows Solution: PASS;
- Linux debug `Run Tests`: PASS, including the focused three-case `ItemParsePolicyTest`;
- final review gate: zero PR comments, zero submitted reviews and zero unresolved review threads;
- squash merge / final Otheryn target: `68c4f39f7b1b45f880543c258627b4ccf73dbc86`.

The target adaptation adds only the policy/test, a bounded three-argument parser registration overload and the required CMake/MSBuild source registration. It does not import the legacy Map/Tile/MapCache fork, datapacks, protocol or client code.

### item-instances → REUSE

Checked principal runtime instance paths are content-identical across task-start target, legacy and upstream:

- `src/items/item.cpp`
- `src/items/item.hpp`
- `src/items/functions/item/attribute.cpp`
- `src/items/functions/item/custom_attribute.cpp`

No target incompatibility or required legacy-only behavior was found in the bounded runtime item-instance boundary.

### world-map-runtime → REUSE

Target and upstream align across the checked principal runtime boundary, including:

- `src/io/iomap.cpp/.hpp`
- `src/map/spectators.cpp/.hpp`
- `src/map/map.cpp/.hpp`
- `src/items/tile.cpp/.hpp`
- `src/map/mapcache.cpp/.hpp`
- `src/map/utils/astarnodes.cpp`
- `src/map/utils/mapsector.cpp`
- `src/map/navigation_snapshot.cpp`

Legacy Canary diverges in `Map`, `Tile`, `MapCache` and `MapSector`, while the upstream-aligned target contains the separately built `navigation_snapshot` runtime source absent from the legacy tree. No focused target failure or target requirement justified importing that legacy fork.

## Exact final-target runtime proof

Full heavy Universal Agent E2E #136, run `29559180590`, passed on the temporary exact controlled-server pin:

- requested server: `blakinio/Otheryn@68c4f39f7b1b45f880543c258627b4ccf73dbc86`;
- artifact-recorded server source commit: `68c4f39f7b1b45f880543c258627b4ccf73dbc86`;
- server binary SHA-256: `dde78689009209901ca01bcffa94b8aa35267976d1c66037b63d756aff3c8a7a`;
- maintained client commit: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`;
- OTClient binary SHA-256: `ceb606775390296d2ce98c7f47e87a35ec457287123246119272e6f3eb6ad72a`;
- Universal E2E evidence artifact digest: `sha256:3d3386341791470d78ae6e4140f4009f5191998d08ca23e8a967f91feb932a6f`;
- controlled server checkout, revision recording and controlled server release build: PASS;
- physical-client `login/relog`: PASS;
- `Required physical E2E`: PASS;
- two protocol-1525 current-profile logins observed;
- two safe logout cycles completed;
- two packet records present;
- `lastlogin` and `lastlogout` persistence checks passed;
- final online count: zero;
- OTClient exit code: zero;
- no fatal runtime log hits.

The physical login/relog run is an exact-target runtime regression smoke for the item/map foundations. It does **not** directly prove damage application from a field placed under an occupied creature. That specific behavior is proven by the focused Otheryn policy unit test plus the bounded PR #81 provenance. The two proof layers are complementary, not interchangeable.

The temporary `.github/e2e-controlled-server.env` pin and `ci:final-gate` label were removed after successful evidence capture and are not part of final governance scope.

## Legacy-delta decision rule

A legacy-only delta enters OAM-007 only when all of the following are established:

1. a concrete target requirement falls inside one of the three canonical modules;
2. target/upstream behavior demonstrably fails that requirement or lacks the necessary invariant;
3. the legacy delta actually addresses that requirement;
4. focused tests and applicable runtime proof can be attached to the bounded target change.

PR #81 satisfies this rule for the magic-field item-definition behavior. The legacy Map/Tile/MapCache/MapSector fork does not satisfy it and is not migrated.

## Safety and known limits

- No module is declared Real Tibia parity-complete.
- No claim of exhaustive map completeness, pathfinding correctness, tile-stack correctness or every movement edge case.
- No item price/value/appearance parity claim.
- Item serialization review does not change or strengthen OAM-004 SQL/KV atomicity claims.
- The physical runtime smoke does not substitute for the focused magic-field behavior test.
- No legacy map/item code was copied wholesale.
- No second E2E orchestrator was created.
- `world-zones`, `instances` and OAM-008 remain outside this package.
