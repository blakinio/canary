# OAM-026 Guilds Revalidation

## Disposition

```text
guilds → ADAPT
```

The canonical guild core is retained, but whole-module `REUSE` is not correct because Otheryn already carries an intentional persistence adaptation from completed OAM-004C: `IOGuild::saveGuild()` returns the database write status and `SaveManager` propagates guild-save failure into aggregate server-save status. OAM-026 preserves that target-owned contract instead of replacing `IOGuild` from legacy or upstream.

No new production guild mutation was required by OAM-026. The target delivery is proof-only: architecture evidence plus focused unit coverage guarding the retained guild state contract and the existing `bool` save API.

## Immutable task-start baselines

- legacy / governance Canary: `052d96014c805aacaa120ce888b7bed038817a72`
- Otheryn target: `1cf38d354b493b4cd9ec8e841ec8f2a6ff322029`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`

## Canonical package

Canonical `guilds` owns:

- guild identity and ranks;
- online-member lifecycle and process-local guild cache;
- guild bank balance load/save projection;
- player guild membership/rank loading;
- guild war-list loading;
- cache removal when the last online member leaves.

Its fundamental dependencies are completed `character-lifecycle` and `database-connection`. Website/account-management flows, guild chat delivery, party lifecycle, wire compatibility and proof of generic durable transaction correctness remain outside OAM-026.

## Source and history evidence

At the immutable baselines:

- `src/creatures/players/grouping/guild.cpp` is blob-identical across legacy, target and upstream: `346bfc562275a5835fd81f146eb235048ce9d45b`;
- `src/creatures/players/grouping/guild.hpp` is blob-identical across legacy, target and upstream: `0e4c53a615d5df90e561cc211da002a89c72a413`;
- the guild-specific `IOLoginDataLoad::loadPlayerGuild` behavior is semantically identical between pinned target and legacy;
- the shared player loader was not copied or claimed wholesale because its unrelated responsibilities differ;
- target `src/io/ioguild.*` intentionally differs from legacy/upstream through completed OAM-004C save-failure propagation;
- Otheryn history from bootstrap to task start contains no stronger later canonical guild-core donor;
- reviewed legacy multichannel work did not change canonical guild production files.

Blob identity is supporting provenance only. The persistence divergence is why the final package disposition is `ADAPT`, not `REUSE`.

## Accepted target boundary

OAM-026 retains:

1. upstream-compatible guild identity, ranks, membership projection, war-list loading and process-local online-member cache behavior;
2. OAM-004C `IOGuild::saveGuild() -> bool` database-result propagation;
3. `SaveManager::saveGuild()` failure propagation and logging;
4. aggregate `SaveManager::saveAll()` guild-failure accounting while preserving its existing best-effort independent-domain behavior.

No maintained OTClient change, protocol/opcode change, map/OTBM change, schema change or new deployment contract is introduced.

## Target proof

Otheryn PR #53 added only:

- `docs/agents/tasks/active/OTH-20260720-oam026-guilds-revalidation.md`;
- `docs/oam-026-guilds-adapt.md`;
- `tests/unit/game/oam_026_guilds_adapt_test.cpp`;
- focused registration in `tests/unit/game/CMakeLists.txt`.

No production guild path changed.

Exact final target head:

```text
4709f0c49962dee14e98acb384baab75b21c97a8
```

Exact-head gates:

- `autofix.ci` run `29775483679`: `success`;
- `CI` run `29775483958`: `success`;
- `Required` run `29775483628`: `success`;
- Linux debug `Run Tests`: `success`;
- Windows CMake build: `success`;
- Windows solution build: `success`;
- macOS build: `success`;
- PR comments: none;
- submitted reviews: none;
- inline review threads: none;
- target `main` remained at immutable baseline `1cf38d354b493b4cd9ec8e841ec8f2a6ff322029` through the final pre-merge drift gate.

PR #53 was expected-head squash-merged as:

```text
418a9f0bfc72cc58b9806a49e966d9c3ea3c1a6d
```

## Security and multiwriter boundary

Legacy security evidence `OTS-ECO-GUILD-001` proves that a multiwriter deployment can double-spend a global guild balance when multiple processes authorize against stale process-local `Guild::bankBalance` snapshots and later perform absolute saves.

OAM-026 does not import that legacy multichannel ownership model and does not claim generic distributed guild-bank safety. Any future Otheryn move to multiple authoritative guild writers requires a separate durable ownership/atomic-debit contract before concurrent guild-bank mutation is enabled.

## Governance drift evidence

After immutable OAM-026 task start, Canary `main` advanced from `052d96014c805aacaa120ce888b7bed038817a72` to governance reconstruction base `191cad8779ec84aaa09c8f62e9b6ff76e958b8fa` only through independent OTBM/E2E coverage and lifecycle paths plus `docs/agents/MODULE_CATALOG.md`. No canonical guild production path, OAM-026 evidence path or Oteryn program record overlapped that drift.

The governance branch was therefore reconstructed onto `191cad8779ec84aaa09c8f62e9b6ff76e958b8fa` before final OAM-026 governance gating.

## Explicit non-claims

OAM-026 does not claim Real Tibia guild parity, website guild-management parity, guild-chat delivery parity, protocol/client UI parity, generic transaction atomicity, generic crash/restart durability, distributed guild ownership, multiwriter guild-bank safety, map/OTBM/assets changes or physical-client guild E2E closure.
