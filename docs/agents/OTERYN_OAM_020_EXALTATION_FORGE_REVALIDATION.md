# OAM-020 — Exaltation Forge Revalidation

Status: **fresh preflight complete; target adaptation pending**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-020`

## Selected canonical package

```text
exaltation-forge → ADAPT
```

The canonical registry record is `docs/agents/real-tibia/registry/modules/exaltation-forge.yaml`.

Whole-module `REUSE` is rejected. The task-start Otheryn target and fresh upstream comparison baseline do not contain a coherent set of merged legacy Forge correctness repairs that are present in current Canary. A broad rebuild is also not justified: the clean target/upstream Forge core remains the architectural base, and only reviewed Forge-specific repairs should be adapted.

## Immutable task-start baselines

```text
legacy/governance Canary: blakinio/canary@c353b89b5a7f783cf4ee22fe1ba91850de837a68
target Otheryn: blakinio/Otheryn@63547f30fc21e495217b8a92fa44aaad2db188ef
fresh upstream comparison: opentibiabr/canary@71a0f92b4da3f550b292fa7536a0e35c2769f1ae
previous OAM upstream pin: opentibiabr/canary@691614c1a302aee776002ca3851eca399be1a82c
maintained OTClient: blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

The fresh upstream head is one commit ahead of the previous OAM pin. That upstream delta is confined to dispatcher scheduling/performance-lifetime documentation and tests and does not overlap the selected Forge boundary.

## Dependency gate

Canonical dependencies:

- `player-persistence` — completed foundational OAM ownership;
- `protocol` — completed OAM-006 ownership.

Interactions:

- `combat` — completed OAM ownership;
- `market` — remains a separate canonical package and is not migrated by OAM-020.

No unresolved dependency blocks bounded Forge revalidation. Protocol/client changes are not implied by dependency completion: any wire-shape or maintained-client mutation remains a separate explicit contract boundary.

## Fresh live-state and ownership audit

At task start:

- Canary `main` is exactly `c353b89b5a7f783cf4ee22fe1ba91850de837a68`;
- Otheryn `main` is exactly `63547f30fc21e495217b8a92fa44aaad2db188ef`;
- maintained OTClient `main` remains `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`;
- Otheryn has no open pull request;
- Canary open PRs are #559, #526, #514 and #479;
- #559 is MyAAC documentation closeout only;
- #526 owns only security evidence documents and treats `src/**`/`data/**` as read-only evidence;
- #514 owns security validation tooling/workflow/docs and treats `protocolgame.*` as read-only;
- #479 is lifecycle archive-only;
- no live task claims exclusive Forge runtime/data/test ownership.

Shared `MODULE_CATALOG.md` / `CHANGELOG.md` ownership exists in unrelated security work, so OAM-020 start-up changes deliberately avoid those shared files.

## Fresh target/upstream/legacy evidence

Task-start evidence already proves material target gaps:

1. `src/game/functions/forge_fusion_policy.hpp` exists in current legacy Canary and is absent from both task-start Otheryn and fresh upstream.
2. `src/game/functions/forge_transfer_policy.hpp`, `forge_transaction.hpp` and `forge_effect_policy.hpp` are legacy-reviewed Forge helpers that are absent from the task-start target/upstream baseline.
3. `src/config/forge_config_defaults.hpp` exists in current legacy Canary and is absent from task-start Otheryn.
4. `data/libs/systems/exaltation_forge.lua` is still the upstream/target blob with `maxFiendish = 3`, while current legacy Canary carries the reviewed `maxFiendish = 4` correction.
5. `PlayerForgeHistory` in task-start Otheryn lacks the `firstItemId` / `secondItemId` fields present in current legacy Canary after the reviewed history-identity repair.

These are not accepted from file identity alone. They correlate with merged, bounded legacy delivery history and the paused Equipment Upgrade parity program.

## Reviewed donor chain for bounded adaptation

The exact implementation hunks must be re-reviewed against task-start target before materialization. The coherent merged legacy evidence set is:

- PR #89 — normal Transfer classification, donor-tier cost/result and history correctness;
- PR #110 — Forge history item identity by numeric item ID with fallback;
- PR #177 — direct/summon killer handling, one shared Dust roll and cap-aware actual credit;
- PR #250 — server-authoritative regular/Convergence Fusion and Transfer validation before mutation;
- PR #257 — transactional Fusion, Transfer and Sliver-to-Core mutation/rollback;
- PR #259 — reviewed Dust `325` and Fiendish `4` defaults with regression coverage;
- PR #262 — Premium Dust eligibility delegated to exact C++ `Player::isPremium()` semantics;
- PR #267 — Avatar mutual exclusion and truthful Momentum feedback;
- PR #283 — Forge history action types and configured/actual amount correctness.

No broad legacy `player.cpp` or `protocolgame.cpp` copy is authorized. Only Forge-specific hunks and isolated helpers/tests may be adapted after exact target-context review.

## Explicit exclusions

OAM-020 does not absorb unresolved or separately contracted work:

- F-014 through F-019 bonus/result/protocol/maintained-OTClient contract work;
- F-009 exact difficulty-to-Sliver mapping;
- F-010 exact percentage precision/rounding;
- generic market ownership;
- generic combat, item, persistence or protocol rewrites;
- maps, OTBM, `items.otb`, assets, schema or deployment changes;
- writes to `blakinio/otclient` or upstream repositories.

The maintained client is evidence-only for this package unless a later explicitly authorized cross-repository package establishes a durable contract and rollout order.

## Boundary classification at start

- ownership/lifecycle: applicable; existing Player/Forge lifecycle retained;
- build/toolchain: applicable; C++/Lua/test changes require full affected-platform validation;
- configuration: applicable for bounded Forge defaults only;
- service/API: applicable only to existing Forge APIs plus reviewed isolated helpers;
- scheduling/concurrency: no generic scheduler change; fresh upstream dispatcher drift is non-overlapping;
- persistence: applicable to existing Forge history/resource state, without redesigning player persistence;
- protocol/session: interaction boundary; no wire-shape change accepted in this package;
- identifiers/assets: no new identifiers or assets;
- world/map: not applicable;
- runtime: applicable; generic runtime smoke plus focused Forge tests required;
- physical-client E2E: current package does not claim unresolved bonus/result UI parity; any required Forge gameplay scenario must reuse the existing universal platform;
- security/operations: validation-before-mutation and transactional rollback are in scope; production rollout is not.

## Next action

Create the OAM-020 active task record and draft governance PR, create a dedicated `dudantas/` target branch from the immutable Otheryn baseline, then perform exact donor-hunk/target-context review before the first target implementation commit. Keep all target changes bounded and reviewable.
