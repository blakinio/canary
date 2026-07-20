# Oteryn OAM-022 Prey Revalidation

Date: 2026-07-20

Task: `CAN-20260720-oteryn-prey-revalidation`

Coordination: `OAM-022`

Canonical module: `prey`

Final disposition: `REUSE`

## Immutable task-start baselines

- Canary legacy/governance: `800142e65c2975e57647bf34128ab468532218f0`
- clean Otheryn target: `b90e287a40413102c87e8c7fa3d5c01ad401cb6d`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

## Canonical dependency and ownership gate

`prey` depends on completed `player-persistence` and completed `protocol`. Its interaction with `wheel-of-destiny` does not broaden OAM-022 and does not authorize Wheel-owned changes.

The canonical scope includes Prey state/rerolls, bonuses, Hunting Tasks and related persistence/packets, while excluding Wheel allocation except an explicit Task Shop integration boundary.

Fresh task-start ownership review found no Otheryn or maintained-OTClient PR and no Prey-specific writer. Canary PR #514 owns security-validation tooling and treats protocol implementation paths as read-only evidence only; #600 is unrelated OTBM/E2E route work; #526 and #559 are documentation/evidence-only security work; #479 is archive-only cleanup. No reviewed open work writes the Prey component or Taskboard data paths.

## Source comparison and classification

The reviewed classic Prey and Task Hunting core has no stronger independent legacy donor than the clean target/upstream implementation.

Exact task-start source identity:

- `src/io/ioprey.cpp` blob `b0e335f5a4f7f9d8a3da75196dedf0d49242ef17` in target, fresh upstream and legacy Canary;
- `src/io/ioprey.hpp` blob `52b5ebf36037e2c9eee8b24741075e24b1680410` in target, fresh upstream and legacy Canary;
- `src/io/functions/iologindata_save_player.cpp` blob `5bb44a2f2e15c33b39a5b24206440057ded4ab5b` in target, fresh upstream and legacy Canary;
- reviewed `loadPlayerPreyClass` and `loadPlayerTaskHuntingClass` implementations are functionally identical across the three baselines.

The maintained OTClient at `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f` already contains `modules/game_prey/prey.lua` with the standard Prey action/options and UI event contract. No packet-layout or maintained-client change is required by the accepted boundary.

Therefore the accepted disposition is:

```text
prey → REUSE
```

This classification is based on exact source, persistence and client-contract evidence plus focused target proof, not on path presence alone.

## Taskboard / Wheel interaction boundary

Target and fresh upstream share the minimal official 15.25 Taskboard packet shim at blob `23ec7e00121695d4fb35941921a05478d7476cea`.

Legacy Canary differs because merged Wheel PR #230 added a Bonus Promotion Shop offer that consumes Hunting Task points while persisting/applying purchased promotion points under the `wheel-of-destiny` KV scope. The donor PR also changes Wheel components, Wheel Lua bindings and Wheel tests.

That is an explicit Prey↔Wheel integration, not a stronger independent Prey-core implementation. OAM-022 deliberately does not copy the Wheel-coupled Taskboard Shop. The separately active Wheel parity program remains authoritative for that integration boundary.

## Exact target proof

Target PR: `blakinio/Otheryn#46`

Target branch: `dudantas/oam-022-prey-reuse`

```text
Otheryn PR #46 final head: 12d79e4532e5784e9530caf433cdad1c869f0142
target squash merge: 50dfa248251f245f5519495a4fbd430b6814ffe4
autofix.ci #145 / 29723046171: SUCCESS
CI #169 / 29723046359: SUCCESS
Required #152 / 29723046189: SUCCESS
Linux debug CTest: 400/400 PASS
focused Oam022PreyReuseTest: 4/4 PASS
test-log artifact: 8453371882
artifact digest: sha256:23e923635138726a33e7900ff84cd481d2182994cb68020c5d03698e4804886c
```

The target PR changed exactly three proof-only paths:

- `docs/oam-022-prey-reuse.md`
- `tests/unit/game/CMakeLists.txt`
- `tests/unit/game/oam_022_prey_reuse_test.cpp`

The focused proof locks deterministic Prey wire-enum values, Prey slot state/reset helpers, Task Hunting slot state/reset helpers, and duplicate monster-list removal behavior. Full Linux debug CTest completed `400/400`, including all four focused OAM-022 cases.

Target comments, reviews and review threads were empty. Otheryn `main` had no drift from task-start target base before merge. PR #46 merged by expected-head squash at exact head `12d79e4532e5784e9530caf433cdad1c869f0142`.

No production runtime, data, persistence, protocol, schema, client, map/OTBM, asset or deployment path changed in the target PR.

## Explicit exclusions and known gaps

OAM-022 does not claim:

- full modern official Hunting Task/Taskboard parity;
- Wheel Bonus Promotion Shop migration or Wheel allocation ownership;
- exhaustive Prey formula, rarity, reroll-price or monster-pool parity;
- physical-client Prey or Taskboard E2E closure;
- generic player-persistence or protocol redesign;
- maps, OTBM, `items.otb`, assets, schema or deployment changes.

These exclusions are deliberate boundaries and do not weaken `REUSE` for the reviewed classic Prey/Task Hunting core.

## Governance and lifecycle gate

The target stage is merged. Canary governance PR #612 must now be validated at its exact final head with Agent Task Ownership and final-gate CI, followed by a clean changed-file/comment/review/thread/main-drift audit and expected-head squash merge.

After governance merge, OAM-022 still requires a separate authoritative lifecycle active→archive PR and then a separate one-file durable program reconciliation. OAM-023 must not start before both stages are merged.
