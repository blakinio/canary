---
task_id: CAN-20260726-oteryn-oam051-wheel-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-051
status: review
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-051-wheel-of-destiny-preflight
base_branch: main
created: 2026-07-26
updated: 2026-07-26
last_verified_commit: "0a2d7377a7ed53dd49dccb672446e1e30de9edde"
risk: high
related_issue: ""
related_pr: "951"
depends_on:
  - OAM-050 durably completed as d0c76c6f964a5266789b252173eb24832a309e80
blocks:
  - OAM-051A target Wheel safety adaptation
  - OAM-051 later Task Shop and parity follow-ups
  - OAM-051 lifecycle, governance and durable reconciliation
  - OAM-052 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260726-oteryn-oam051-wheel-preflight.md
  shared: []
  read_only:
    - docs/agents/real-tibia/registry/modules/wheel-of-destiny.yaml
    - docs/agents/programs/WHEEL_OF_DESTINY_PARITY_PROGRAM.md
    - docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION.md
    - docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION_PROJECT.md
    - src/creatures/players/components/wheel/**
    - src/io/io_wheel.*
    - src/server/network/protocol/protocolgame.*
    - src/creatures/combat/**
    - data/scripts/spells/**
    - data/modules/scripts/taskboard/**
    - tests/unit/players/**
    - tests/integration/**
    - blakinio/Otheryn
    - blakinio/otclient
    - opentibiabr/canary
    - zimbadev/crystalserver
---

# OAM-051 Wheel of Destiny preflight

Select canonical `wheel-of-destiny → ADAPT candidate` after durable OAM-050 closure.

The target must not bulk-copy the legacy Wheel subsystem. Canary contains useful reviewed hardening and the bounded Hunting Task Shop Promotion Point package, but the canonical module remains partial across persistence, protocol, combat effects, stances, replacement spells and gameplay E2E.

## Exact adaptation manifest

### OAM-051A — first target package: Wheel safety and state-integrity adaptation

Only evidence-backed hardening from PR #220 is eligible for the first target branch:

- `src/creatures/players/components/wheel/player_wheel.cpp`
  - atomic proposal validation before slot mutation;
  - temple-only decrease enforcement;
  - saturating/validated unused-point accounting;
  - gem capacity, item/money ordering and bounded restoration;
  - modifier-position, grade, index and active-gem state checks;
  - load/reset and persistence-state hardening;
- `src/creatures/players/components/wheel/player_wheel.hpp`
  - declarations and bounded state required by those safety invariants only;
- `src/creatures/players/components/wheel/wheel_gems.cpp` and `.hpp`
  - safe grade/resonance/state handling required by the selected invariants;
- `src/io/functions/iologindata_load_player.cpp`
  - Wheel load-order correction required for authoritative extra-point/state reconstruction;
- `src/server/network/protocol/protocolgame.cpp`
  - truncated payload, enum, quality, fragment-type and index validation for existing Wheel actions;
- `tests/unit/players/wheel_validation_test.cpp`
  - focused deterministic acceptance coverage for every selected invariant;
- `tests/unit/players/CMakeLists.txt`
  - additive registration of the new target test only.

The target branch must apply selected hunks semantically. It must not replace whole files. `protocolgame.cpp`, `player_functions.*` and test manifests have target-specific OAM changes and require symbol-level rebasing.

### Deferred from OAM-051A — current-behavior parity refresh required

The following PR #220 deltas are not authorized for the first target branch because they change values, formulas, areas or effect ordering and require a refreshed official/current comparison matrix:

- `data/scripts/spells/attack/flurry_of_blows.lua`;
- `data/scripts/spells/attack/front_sweep.lua`;
- `src/creatures/monsters/monster.cpp`;
- `src/game/game.cpp`;
- balance/effect portions of `src/creatures/players/components/wheel/wheel_definitions.hpp`;
- balance/spell portions of `src/io/io_wheel.cpp`;
- any critical-healing, stance, replacement-spell or geometry behavior from WHEEL-003 onward.

These remain Wheel parity work, not implicit OAM migration permission.

### Deferred second bounded package — Hunting Task Shop Promotion Points

PR #230 proves a real target gap, but its target adaptation follows OAM-051A and requires a separate transaction/client contract:

- applicable behavior roots: `data/modules/scripts/taskboard/taskboard.lua`, selected `player_wheel.cpp/.hpp` additions and selected `player_functions.cpp/.hpp` Lua binding additions;
- target tests must cover 1–50 cost progression, invalid offer IDs, insufficient points, max cap, KV clamp/load, relog and failure boundaries;
- `docs/lua-api/lua_api.*` are generated outputs, never copied source;
- `tools/ai-agent/test_wheel_task_shop_validation.py` remains Canary evidence tooling and is not migrated;
- historical task, ACTIVE_WORK and validation-document paths are governance evidence only.

The current Canary implementation removes Hunting Task Points before writing Wheel KV. OAM-051 must preserve the known OAM-004 durability boundary and must not claim atomic purchase persistence without explicit failure/rollback evidence.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T01:42:00+02:00
head: 0a2d7377a7ed53dd49dccb672446e1e30de9edde
branch: dudantas/oam-051-wheel-of-destiny-preflight
pr: 951
status: validating
context_routes:
  - agent-governance
  - cross-repo
  - real-tibia-parity
  - universal-e2e
  - github-actions
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-oteryn-oam051-wheel-preflight.md
proven:
  - OAM-050 is durably complete as d0c76c6f964a5266789b252173eb24832a309e80 and no OAM implementation task remains active.
  - Fresh Canary main is d0c76c6f964a5266789b252173eb24832a309e80 and fresh Otheryn main is ff90e93d872b6b47720f711483a9832203d5258d.
  - Fresh comparison heads are opentibiabr/canary@7644bcbcbbad4a09e52a5707ed531e4dd21d8a79, blakinio/otclient@ff36aa74324eddbe6a64a79b23bd42d6a185fb7f and zimbadev/crystalserver@75e9c72e33ce2c3f193e4f2d2ff17ebae4bbfaac.
  - Otheryn has no open PR. Canary open PRs 948, 815, 559, 526 and 514 do not claim Wheel implementation paths; PR 948 is separately governed E2E baseline work and PR 514 is the existing network-transport blocker.
  - The Wheel programme has no active task and names WHEEL-003 as its preferred next parity behavior package only after fresh evidence review.
  - OTClient PR 25 is ahead of current main only by two audit documents; current open client PRs do not own Wheel runtime paths.
  - Canonical Wheel dependencies are represented in Otheryn by OAM-013 combat reuse 3628effc5f22e7edbdc66dc5f514e4df5c9f0cda, OAM-004 persistence hardening including 4b5b94eced0f3c5d88b9a4293e849d888333e0cb and 67212530b03c10175da2c0d9eabcee8991a05924, OAM-006 secure protocol c547d8ad70ef1252624c255476e6cb83fa125e14 and OAM-044 profile proof 5c8f48e2a7cb7f841cfb6614e8e804245f17c0ca.
  - For flurry_of_blows.lua, front_sweep.lua, monster.cpp, player_wheel.cpp/.hpp, wheel_definitions.hpp, wheel_gems.cpp/.hpp, game.cpp, iologindata_load_player.cpp and io_wheel.cpp, current Otheryn blobs equal current upstream blobs while current Canary blobs differ.
  - Current Otheryn protocolgame.cpp and tests/unit/players/CMakeLists.txt differ from both upstream and Canary because prior OAM packages added target-specific protocol/test state; selected Wheel changes require semantic rebasing.
  - tests/unit/players/wheel_validation_test.cpp exists in Canary and is absent from Otheryn and upstream.
  - Current Otheryn and upstream use identical taskboard.lua blob 23ec7e00121695d4fb35941921a05478d7476cea and send zero Task Shop offers; Canary blob b15bd734df796032047c247dea4e3451c462f199 implements the bounded Bonus Promotion package from PR 230.
  - PR 230 adds only one new Player Lua method, setWheelHuntingTaskShopPoints, plus bounded Wheel state/load/payload/accounting and Taskboard purchase behavior; generated docs and Canary validators are separable.
  - PR 220 protocol hardening validates truncated and invalid existing Wheel action payloads without defining a new opcode or client field.
  - Canary Wheel audit/hardening PR 220 and Task Shop PR 230 are explicitly bounded historical deliveries; the programme rejects the broad claim that all Wheel 15.25 behavior is complete.
derived:
  - REUSE is invalid because the target lacks reviewed Wheel safety and Task Shop behavior already present in Canary.
  - ADAPT is the correct candidate because target-specific protocol/Lua/test changes require semantic integration and because parity-sensitive legacy behavior cannot be transferred wholesale.
  - OAM-051A can be client-first-neutral and server-first-safe when it changes only server validation/state invariants for existing packet shapes and adds no opcode or payload field.
  - Hunting Task Shop must remain a later bounded package because it changes the current-client payload interpretation and persistence transaction surface.
unknown:
  - Exact target compile/test adjustments required when selected PR 220 hunks meet OAM-004, OAM-006, OAM-044 and OAM-047 target changes.
  - Whether the PR 230 Task Shop payload and UI behavior remain fully compatible with maintained OTClient ff36aa74324eddbe6a64a79b23bd42d6a185fb7f under exact physical runtime proof.
  - Exact current official-source authority for deferred 15.25 values, effect ordering, spell areas, critical healing, stances and replacement spells.
  - Transaction/failure semantics required before the Task Shop package can claim durable purchase correctness.
conflicts: []
first_failure:
  marker: target-missing-reviewed-wheel-safety
  command: exact PR 220 and PR 230 path/blob/semantic inventory
  result: FAIL
  evidence: Target matches upstream on the selected Wheel roots and lacks the reviewed Canary hardening/test package; target protocol and Lua roots also contain independent OAM changes that prohibit raw patch or whole-file replacement.
rejected_hypotheses:
  - Mark Wheel REUSE from upstream-derived target code or file presence.
  - Bulk-copy all legacy Wheel, combat, protocol, spell or Taskboard paths.
  - Apply PR 220 or PR 230 as whole-file replacements.
  - Include balance, formula, area, critical-healing, stance or replacement-spell changes in OAM-051A without refreshed parity evidence.
  - Claim atomic Task Shop purchase persistence from the current Canary sequence.
  - Start WHEEL-003 critical healing implementation as an automatic consequence of OAM selection.
  - Modify blakinio/otclient or external comparison repositories from this OAM task.
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-oteryn-oam051-wheel-preflight.md
validation:
  - command: fresh main, open-PR, ownership and canonical dependency audit
    result: PASS
    evidence: No live OAM or Wheel owner conflicts; required target foundations exist and separately blocked network/login work is not claimed.
  - command: exact PR 220 and PR 230 changed-path inventory
    result: PASS
    evidence: Every changed path is classified into OAM-051A safety, deferred Task Shop, parity-refresh-required, generated, governance-only or Canary evidence-tooling scope.
  - command: target/upstream/legacy blob and semantic comparison
    result: PASS
    evidence: Target/upstream identity is proven on ordinary Wheel roots; target-specific protocol/Lua/test divergences and the direct empty-shop gap are explicitly recorded.
  - command: maintained-client overlap and rollout review
    result: PASS
    evidence: No live client Wheel owner exists; OAM-051A changes existing server validation/state only and Task Shop remains separately client-coupled.
  - command: final OAM-051A target manifest proof
    result: PASS
    evidence: First target package is restricted to Wheel safety/state-integrity hunks plus focused tests and excludes balance/effect and Task Shop behavior.
  - command: Canary preflight exact-head gates
    result: NOT_RUN
    evidence: PR 951 must pass Ownership and CI on the final synchronized head.
blockers:
  - Canary preflight exact-head Ownership and CI
  - clean discussion and Canary-main drift audit
next_action: Merge PR 951 after exact-head gates and clean audits, then open Otheryn OAM-051A from ff90e93d872b6b47720f711483a9832203d5258d with only the approved Wheel safety/state-integrity hunks and focused deterministic tests.
```