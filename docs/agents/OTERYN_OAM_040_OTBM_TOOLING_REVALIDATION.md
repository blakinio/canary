# OAM-040 OTBM tooling revalidation

## Final disposition

`otbm-tooling → DO_NOT_MIGRATE`

## Baselines

- Canary OAM-040 preflight merge: `90b5054ebc8b2a19d52cc1bc2731e9dc6f3080f3`
- Canary fresh governance base: `c5841f0b31b830cfb1497a67f44e29e0fc11e5ac`
- Otheryn target task-start main: `5eea55ca3dd7689d097fadef3ff92eee84f8c163`
- Otheryn target disposition merge: `e607887533bbbff13ff36d781e3f7f25d2f71675`
- fresh upstream Canary baseline: `7323503b3dc61ed86bf1f04a611b2d0aec64b35a`
- maintained OTClient baseline: `1e5305395159142634f182d9e888e5f9164228c6`

## Canonical responsibility and target boundary

Canonical `otbm-tooling` is a dependency-free `platform-tooling` module. It owns no server, client or data path. Its responsibility is the deterministic OTBM analysis/evidence stack used by migration and world-content validation, including World Indexing, reachability, spawn/NPC evidence, storage graph analysis, semantic diff, geometry audit and bounded patch safety.

The Oteryn target architecture contract assigns the legacy Canary repository the roles of laboratory, evidence source and validation environment, while Otheryn is the clean selectively populated target. The contract also requires OTBM/map/content work to reuse the existing deterministic analysis stack instead of creating competing tooling.

The maintained OTBM roadmap is explicitly scoped to `blakinio/canary`; its phases 1 through 8 are recorded merged and archived there. Representative `tools/ai-agent/otbm_world_index.py` exists in Canary and is absent from clean Otheryn and fresh upstream, as is the OTBM tooling roadmap.

## Dependency impact

Canonical `spawns` and `npcs` depend on `otbm-tooling`; `quests` depends on `otbm-tooling` and `player-persistence`.

OAM-040 resolves those dependencies as cross-repository evidence dependencies, not target-local runtime/library imports. Downstream packages must pin exact Canary tooling/report provenance and prove their own target data/runtime behavior. No identified Otheryn runtime, service, protocol, client, map-loader, production build or data path requires a target-local copy of the OTBM analysis stack.

The canonical registry entry remains intact. `DO_NOT_MIGRATE` means the tooling is excluded from Otheryn core; it does not delete, deprecate or freeze the maintained Canary evidence stack.

## Target proof

Otheryn PR #83 final head `06d1a692e2e6ed0eaaf98d7acb54281a1cd5d4c3` changed exactly two documentation/task paths:

- `docs/agents/tasks/active/OTH-20260723-oam040-otbm-tooling-do-not-migrate.md`
- `docs/oam-040-otbm-tooling-do-not-migrate.md`

It introduced no production, test-runtime, protocol, client, data, map, asset, schema, deployment or build mutation. Exact-head Required run `30007035180` succeeded. Comments, submitted reviews and review threads were empty, Otheryn `main` had no task-start drift, and PR #83 squash-merged as `e607887533bbbff13ff36d781e3f7f25d2f71675`.

## Why `DO_NOT_MIGRATE`

- `REUSE` is incorrect because no target-local runtime/product responsibility needs transfer.
- `ADAPT`/`REWRITE` are unnecessary because the established Canary evidence stack already owns the responsibility.
- `EXPERIMENTAL_ONLY` is too weak because the tooling is maintained deterministic infrastructure, not experimental-only functionality; the target decision is explicit exclusion from Otheryn core.

## Final conclusion

OAM-040 is `DO_NOT_MIGRATE`. The canonical dependency is considered resolved for migration ordering through the explicit cross-repository evidence contract. Future world-content packages may now evaluate their own dependency-validity, but each must independently pin the exact Canary tooling/report evidence it consumes.

## Nonclaims

OAM-040 does not claim that static OTBM evidence proves live gameplay, that the tooling is permanently feature-complete, that generated reports/assets belong in Otheryn, or that `spawns`, `npcs` or `quests` are already migrated or correct.
