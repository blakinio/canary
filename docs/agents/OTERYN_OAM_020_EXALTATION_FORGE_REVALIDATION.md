# OAM-020 — Exaltation Forge Revalidation

Status: **target adaptation proved and merged; Canary governance reconciliation in progress**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-020`

## Final disposition

```text
exaltation-forge → ADAPT
```

Whole-module `REUSE` was rejected because the task-start Otheryn target and fresh upstream comparison baseline lacked multiple coherent, reviewed Canary Forge correctness repairs. A broad rebuild was also rejected because the clean upstream-based Forge core remained usable. OAM-020 adapted only the reviewed Forge-specific donor chain plus target-required build-contract adjustments and focused proof.

## Immutable task-start baselines

```text
legacy/governance Canary: blakinio/canary@c353b89b5a7f783cf4ee22fe1ba91850de837a68
target Otheryn: blakinio/Otheryn@63547f30fc21e495217b8a92fa44aaad2db188ef
fresh upstream comparison: opentibiabr/canary@71a0f92b4da3f550b292fa7536a0e35c2769f1ae
previous OAM upstream pin: opentibiabr/canary@691614c1a302aee776002ca3851eca399be1a82c
maintained OTClient: blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

The fresh upstream head was one commit ahead of the previous OAM pin. That delta was dispatcher/performance-lifetime only and did not overlap the selected Forge boundary.

## Canonical dependency gate

Canonical module: `docs/agents/real-tibia/registry/modules/exaltation-forge.yaml`.

Fundamental dependencies:

- `player-persistence` — completed foundational OAM ownership;
- `protocol` — completed OAM-006 ownership.

Interactions with completed `combat` and separate `market` ownership did not block this bounded package. Protocol dependency completion did not authorize unresolved wire/client changes; F-014 through F-019 remain excluded.

## Fresh ownership and drift audit

At task start:

- Canary `main` was exactly `c353b89b5a7f783cf4ee22fe1ba91850de837a68`;
- Otheryn `main` was exactly `63547f30fc21e495217b8a92fa44aaad2db188ef`;
- maintained OTClient remained `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`;
- Otheryn had no open PR;
- no live task claimed exclusive Forge runtime/data/test write ownership.

Later parallel Canary PRs #599 and #600 were rechecked by actual changed paths and remained unrelated OTBM/E2E work with no OAM-020 overlap.

Before target merge, Otheryn `main` was still exactly the task-start baseline, so there was no target-main drift. PR #44 had zero PR comments, zero review submissions and zero review threads.

## Accepted coherent donor chain

The bounded adaptation is the reviewed result of these merged Canary repairs:

1. PR #89 / merge `209289d38e64aafe7ce3e036867bb632cd0363b8` — normal Transfer classification compatibility, donor-tier pricing/resource semantics, result tier and history values.
2. PR #110 / merge `84f5c09263f459d726fbc7b9f79557b2cbb0801d` — stable numeric item identity in Forge history with name fallback.
3. PR #177 / merge `f1d217c43e8e302978f533212e6aa9d1ce2b77c8` — direct/summon killer handling, one shared Dust roll and cap-aware actual credit.
4. PR #250 / merge `94f8a3b63271b3708e33496e937620a6cd4b9717` — server-authoritative regular/Convergence Fusion and Transfer validation before mutation.
5. PR #257 / merge `e16c9f769b1bcdd05e1719e861f0a52cc2594560` — transactional Fusion, Transfer and Sliver-to-Core mutation/rollback.
6. PR #259 / merge `444aa8ae13edc01c6e77b03139a43d386b437308` — reviewed Dust `325` and Fiendish `4` defaults.
7. PR #262 / merge `ded1830b143388d65c895ad30918faf128df66ed` — Premium Dust eligibility delegated to exact C++ `Player::isPremium()` semantics.
8. PR #267 / merge `7771bbec22d970d9779bff740e3f7f2e0df42f19` — Avatar mutual exclusion and truthful Momentum feedback.
9. PR #283 / merge `82348f9faca788a8cbb5c13feb75b4e06d8da9dc` — Forge history action-type and configured/actual amount correctness.

No whole-file legacy `player.cpp` or `protocolgame.cpp` transfer was accepted.

## Target-local adaptations

Otheryn local governance required two reviewable adjustments around the donor chain:

- the five new Forge/config helper headers were registered in tracked `vcproj/canary.vcxproj` as required by the target build-entry policy;
- standard-library includes already supplied by `src/pch.hpp` were guarded with `#ifndef USE_PRECOMPILED_HEADERS` fallback includes.

Donor test CMake changes that conflicted with the newer target layout were not copied wholesale. The exact Forge tests were registered deterministically in the current target `tests/unit/game/CMakeLists.txt` and `tests/unit/players/CMakeLists.txt`.

A target-specific `Oam020ExaltationForgeAdaptTest` was added to prove the accepted default, authority, effect-gate and transaction boundaries on the target itself.

## Materialization safety record

A temporary self-removing materializer pinned legacy `c353b89b5a7f783cf4ee22fe1ba91850de837a68`, applied only explicit donor paths with `git apply --3way`, enforced an allowlist, and was absent from the final PR diff.

The materializer failed closed during development until target-specific integration issues were resolved:

- an older donor `tests/unit/players/CMakeLists.txt` hunk conflicted with the newer target layout; only the required Forge test registrations were adapted;
- `vcproj/canary.vcxproj` required explicit force-staging because that path is ignored by the target checkout despite being a tracked maintained build entry point;
- executing a self-modifying shell script directly caused Bash to reach EOF after the script replaced itself; the runner was corrected to execute a stable temporary copy.

These failures produced no accepted target runtime commit. Final materialization succeeded, all temporary workflow/script paths were removed, and only the reviewed target scope remained.

## Accepted target scope

Otheryn PR #44 final head:

```text
f05787db7f165d0dae0584b3e06c6526f89a42cd
```

Final diff: exactly 24 intended paths — 23 bounded Forge runtime/data/test/build paths plus one OAM-020 target proof test:

```text
config.lua.dist
data/libs/systems/exaltation_forge.lua
docs/lua-api/lua_api.json
src/config/configmanager.cpp
src/config/forge_config_defaults.hpp
src/creatures/players/components/player_forge_history.hpp
src/creatures/players/player.cpp
src/game/functions/forge_effect_policy.hpp
src/game/functions/forge_fusion_policy.hpp
src/game/functions/forge_transaction.hpp
src/game/functions/forge_transfer_policy.hpp
src/lua/functions/creatures/player/player_functions.cpp
src/lua/functions/creatures/player/player_functions.hpp
src/server/network/protocol/protocolgame.cpp
tests/integration/game/forge_it.cpp
tests/lua/test_exaltation_forge_premium.lua
tests/unit/game/CMakeLists.txt
tests/unit/game/forge_config_test.cpp
tests/unit/players/CMakeLists.txt
tests/unit/players/forge_effect_policy_test.cpp
tests/unit/players/forge_test.cpp
tests/unit/players/forge_transaction_test.cpp
tests/unit/players/oam_020_exaltation_forge_adapt_test.cpp
vcproj/canary.vcxproj
```

No temporary `.github` materializer path remained in the accepted diff.

## Exact target proof

Accepted head `f05787db7f165d0dae0584b3e06c6526f89a42cd` passed:

- autofix.ci #142 / run `29701626292` — SUCCESS;
- Repository Audit #19 / run `29701626282` — SUCCESS;
- CI #164 / run `29701626343` — SUCCESS;
- Required #149 / run `29701626255` — SUCCESS;
- Fast Checks — PASS;
- Lua Tests — PASS;
- Linux release compile and Canary/global runtime smoke — PASS;
- Linux debug compile, schema import and CTest — PASS;
- macOS compile/runtime smoke — PASS;
- Windows CMake compile/runtime smoke — PASS;
- Windows Solution/MSBuild compile — PASS;
- Docker image build/validation — PASS.

Linux debug CTest completed:

```text
393/393 PASS
```

The focused OAM-020 target proof completed:

```text
Oam020ExaltationForgeAdaptTest: 2/2 PASS
```

Primary test artifact:

```text
id: 8446751016
name: linux-debug-test-logs
digest: sha256:1bc0b22f42693c2eaa4404de0b4e66846d399a1046c1620254a493b9bcba5eef
```

The one autofix delta before the accepted head was formatting-only in the target proof test; no runtime/data behavior changed.

## Target merge

Final target audit:

- changed files: 24 intended paths;
- comments: 0;
- reviews: 0;
- review threads: 0;
- target-main drift: none.

PR #44 was squash-merged with expected head `f05787db7f165d0dae0584b3e06c6526f89a42cd` as:

```text
d59207d05ab6dd9450b05d0a6b4d9122fda60489
```

Post-merge Otheryn `main` is exactly one commit ahead of the task-start baseline and the 24 changed paths match the accepted target scope.

## Explicit exclusions and non-claims

OAM-020 does not claim or implement:

- F-014 through F-019 Forge bonus/result/protocol/maintained-OTClient parity;
- F-009 exact difficulty-to-Sliver mapping;
- F-010 exact percentage precision/rounding;
- exhaustive current Real Tibia Forge parity;
- physical-client Forge E2E closure;
- generic market, combat, item, persistence or protocol rewrites;
- map, OTBM, `items.otb`, asset, schema or deployment changes;
- writes to maintained OTClient or upstream repositories.

Any future Forge physical-client proof must reuse the existing universal E2E platform. Any future F-014–F-019 work requires an explicit Canary ↔ maintained-OTClient contract and rollout plan.

## Current state

OAM-020 target implementation/proof is complete and merged. Canary governance PR #598 is now the active reconciliation boundary. After governance merge, OAM-020 still requires a separate authoritative active→archive lifecycle PR and a separate one-file durable program reconciliation before OAM-021 may start.
