# Universal OTS E2E physical gameplay action plans

## Purpose

The Universal OTS E2E platform already owns disposable MariaDB bootstrap, exact server builds, a controlled pinned OTClient build, matching client assets, physical login/logout/relog execution, runtime evidence and cleanup.

This document defines the bounded client-action and persistence-assertion layers used to extend that same physical lifecycle into gameplay scenarios. It is not a second E2E orchestrator and it does not authorize production targets.

A scenario may add an optional `steps` array. When present, `tools/e2e/run_agent_e2e.py` validates the plan and materializes a deterministic `scenario-plan.lua`. The scenario chooses `tools/e2e/client/agent_e2e_scenario.lua` as its client automation driver. The driver executes first-session actions, performs a safe logout, waits for server persistence, relogs, executes any client-readable typed persistence checks through the real client, then performs the second safe logout. The existing final SQL assertion evaluator runs only after that full two-session client cycle exits.

## Safety contract

- Maximum 64 actions per plan.
- Maximum 32 typed persistence checks per scenario.
- Unknown actions, persistence types, player fields and unknown contract fields fail validation.
- Step and persistence-check IDs must be unique lowercase slugs within their respective lists.
- Text actions reject embedded newlines, carriage returns and NUL and are bounded to 512 characters.
- Waits and polling timeouts are bounded to 120 seconds.
- Walk repetitions are bounded to 64.
- Exact movement-edge coordinates are bounded to the OTBM coordinate range (`x,y` 0..65535 and `z` 0..15), must remain on one floor and must describe exactly one adjacent tile edge.
- Item identifiers are bounded unsigned 16-bit values and must be supplied by a feature-owned deterministic fixture; the platform never invents item IDs.
- Creature names, map positions, NPC names, storage keys/values and gameplay expectations belong to feature-owned scenario tasks and must be evidence-backed.
- Credentials are referenced through environment variables; scenario JSON must not embed passwords, tokens or private keys.
- A successful action plan proves only the declared physical assertions. It does not prove full gameplay parity.
- `player_field` persistence checks require the same expected value after relog through the controlled client and after the full cycle through compiled scalar SQL.
- `player_storage` persistence checks are database-only after the full two-session cycle because arbitrary server-side storage values have no generic trustworthy controlled-client read surface; they must not be fabricated as phase-two client checks.
- `player_item_presence` persistence checks are database-only row-presence assertions after the full two-session cycle. They support only the fixed inventory/depot/inbox persistence tables and deliberately do not expose serialized hierarchy or interpret the persisted `count` column as universal item quantity.
- `player_balance` persistence checks are database-only exact unsigned-64 equality assertions against the durable `players.balance` column after the full two-session cycle. The platform does not fabricate a generic controlled-client bank-balance getter.
- The existing physical E2E lifecycle, exact-head provenance, MariaDB assertions, packet records and fatal-runtime-log checks remain authoritative.

## Server runtime selection

The existing `scenario.server.datapack` and `scenario.server.map` fields select the datapack directory and map basename used by the same physical server lifecycle. Both values are restricted to single repository-local path segments; traversal, nested paths and symlink escapes are rejected before Canary starts.

The canonical `data-otservbr-global` / `otservbr` pair preserves the existing configured map-download fallback when its map file is absent. Any non-default selection must already exist as a non-empty `<datapack>/world/<map>.otbm` file inside the repository checkout; the scenario cannot supply a map URL, arbitrary filesystem path or external target. The selected datapack/map and runtime helper are included in physical-run provenance evidence.

Server selection changes only which repository-owned datapack/map the canonical lifecycle starts. It does not create a second runner, alter the controlled OTClient contract, or make a static map fixture itself proof of gameplay correctness.

## Pull-request scenario selection

The existing `run_agent_e2e.py resolve` boundary keeps `login/relog` as the canonical pull-request fallback. For a same-repository `pull_request` that reaches the resolver with exactly that fallback pair, it may replace the fallback only when the exact base/head delta proves exactly one existing `tests/e2e/scenarios/<suite>/*.json` manifest changed. The selected scenario ID comes from the validated manifest, not from its filename.

The selector first attempts an exact local Git diff and, for the shallow checkout used by the existing workflow, can fall back to GitHub's immutable exact-SHA compare API. Fork pull requests, zero or multiple candidate manifests, and deleted-only manifests retain `login/relog`. Invalid or unavailable exact-delta evidence fails closed rather than silently claiming a feature scenario was validated. GitHub compare evidence at the 300-file response boundary is rejected as potentially truncated.

Explicit non-canonical `workflow_dispatch` suite/scenario inputs are never replaced by PR selection. Scenario discovery and validation, controlled server/client selection, physical execution, evidence and the Required gate remain owned by the same Universal Agent E2E workflow and runner; this adds no second workflow or lifecycle.

## Supported actions

| Action | Required fields | Optional fields | Physical intent |
|---|---|---|---|
| `wait` | `id`, `action`, `ms` | — | Bounded dispatcher wait. |
| `walk` | `id`, `action`, `direction` | `count`, `interval_ms` | Send bounded directional walk requests. |
| `walk_edge` | `id`, `action`, `from_x`, `from_y`, `from_z`, `to_x`, `to_y`, `to_z` | `timeout_ms` | Assert the exact current source position, derive one adjacent movement direction from the coordinate delta, send exactly one walk request, and wait for the exact destination or fail closed on drift/timeout. |
| `talk` | `id`, `action`, `text` | — | Send normal client talk text; feature scenarios may use this for spells or NPC dialogue only with evidence-backed text. |
| `attack_visible` | `id`, `action`, `creature` | `timeout_ms` | Find a visible named creature and confirm it becomes the attacking target. |
| `use_inventory_item` | `id`, `action`, `item_id` | — | Require the item in local-player inventory and send the inventory-use request. |
| `request_quest_log` | `id`, `action` | — | Request the quest log through the maintained-client game API. |
| `request_channels` | `id`, `action` | — | Request the channel list through the maintained-client game API. |
| `observe_online` | `id`, `action`, `expected` | — | Assert the physical game online state. |
| `observe_position_changed` | `id`, `action` | — | Assert the player no longer occupies the initial first-session position. |
| `observe_floor_delta` | `id`, `action`, `delta` | — | Assert a bounded z-floor delta relative to the initial first-session position. |
| `observe_health_percent_below` | `id`, `action`, `percent` | — | Assert current health percentage is below the declared threshold. |
| `observe_inventory_count_at_least` | `id`, `action`, `item_id`, `count` | `tier` | Assert a minimum local-player inventory count. |
| `wait_creature` | `id`, `action`, `creature`, `present` | `timeout_ms` | Poll bounded visible-creature presence or absence. |
| `observe_attacking` | `id`, `action`, `expected` | — | Assert whether the client currently has an attacking target. |

Directions accepted by `walk` are `north`, `east`, `south`, `west`, `northeast`, `southeast`, `southwest` and `northwest`.

`walk` remains backward-compatible for tiny bounded probes whose directional movement is itself under test. OTBM-aware route execution must use `walk_edge` for ordinary same-floor movement so the real client is synchronized against each exact expected `P0 -> P1` edge rather than advancing through blind direction/count timing. `walk_edge` does not consume or plan a route by itself, does not cross floors and does not implement map-item interactions; full `follow_route` remains a separate route-plan consumption layer.

For `walk_edge`, the caller supplies exact source and destination coordinates but never a direction. Validation derives the direction from the exact adjacent delta. At runtime the driver first requires `current == source`, sends exactly one `g_game.walk(derivedDirection)`, then polls until `current == destination`. Any observed third position is route drift and fails the action; timeout or a rejected walk request also fails closed. The success detail is the exact destination coordinate string.

## Evidence markers

Every first-session step emits:

- `step_<id>=start` before execution;
- `step_<id>=success` after the action or observation succeeds;
- optional `step_<id>_detail=<value>` with bounded diagnostic detail.

After all first-session steps complete, the driver emits `plan=success` and enters the normal safe-logout/persistence/relog lifecycle. A failed action emits `e2e=failure` and terminates the client run.

Each client-readable typed post-relog persistence check emits `persistence_check_<id>=start`, `persistence_check_<id>=success` and a bounded `persistence_check_<id>_detail=<actual>` value. After all client-readable checks pass, the driver emits `persistence_plan=success` before the second safe logout. Database-only `player_storage`, `player_item_presence` and `player_balance` checks do not emit client persistence markers; their evidence is the compiled post-cycle SQL assertion result after the second safe logout.

Feature scenarios should include exact required step and client persistence markers in `assertions.required_markers` when applicable, in addition to the existing login/logout/relog markers.

## Typed persistence assertions

The optional feature-owned contract supports directly comparable player fields, durable player storage rows, fixed-location item-row presence/absence and durable bank-balance equality:

```json
{
  "assertions": {
    "persistence": {
      "required": true,
      "checks": [
        {
          "id": "level",
          "type": "player_field",
          "field": "level",
          "equals": 500
        },
        {
          "id": "quest-stage",
          "type": "player_storage",
          "key": 123456,
          "equals": 7
        }
      ]
    }
  }
}
```

`required` must be explicit. A required persistence declaration must contain at least one check; checks are rejected when `required` is false.

`player_field` supports only `level` and `experience`, because those values have directly comparable durable `players` columns and controlled-client getters after relog. Raw server vocation IDs remain deliberately excluded because the maintained client exposes its own vocation representation; a future vocation contract needs an explicit normalization layer rather than assuming numeric identity.

`player_storage` accepts an exact `key` in the current `player_storage.key` unsigned 32-bit range (`0..4294967295`) and an exact signed 32-bit `equals` value (`-2147483648..2147483647`). The compiler emits a fixed-shape semicolon-free `EXISTS` query that joins `player_storage` to the exact fixture character. Missing rows, wrong values and wrong characters evaluate false. The typed contract never accepts caller-supplied table names, columns, predicates or SQL fragments.

`player_storage` deliberately does not enter `scenario-plan.lua.persistence_checks`: arbitrary Canary player storages are server-side state and are not exposed through a generic trustworthy controlled-OTClient getter. Their M3 persistence evidence is therefore the successful physical two-session lifecycle followed by the compiled SQL check after the second safe logout. A future feature may add a separate client-visible quest/UI assertion when that feature has a real maintained-client surface; that must not be confused with generic storage access.

`player_item_presence` accepts only `location`, `item_id` and `present` in addition to the common `id` and `type`. `location` is exactly one of `inventory`, `depot` or `inbox`; the compiler maps those values internally to the fixed current tables `player_items`, `player_depotitems` and `player_inboxitems`. `item_id` is an evidence-backed item type in the supported `1..65535` range and `present` is a strict boolean. The compiler emits only a fixed-shape semicolon-free `EXISTS` or `NOT EXISTS` query joined to the exact fixture character. Callers cannot select a table, column, predicate, `pid`, `sid` or SQL fragment.

The item-presence contract intentionally ignores the persisted `count` field. Canary's shared item serializer writes `item->getSubType()` there, so its meaning depends on item type and is not a universal stack-quantity contract. The typed assertion therefore proves only that at least one serialized row with the exact item type exists or does not exist in the selected persistence location. Feature scenarios that need quantity, container hierarchy or a client-visible outcome must own a stronger evidence-backed assertion separately.

`player_item_presence` also deliberately does not enter `scenario-plan.lua.persistence_checks`. Inventory, depot and inbox do not share one generic trustworthy controlled-client getter, so the reusable contract uses one consistent database-only boundary after the full two-session physical lifecycle. A feature may separately assert a client-visible inventory state when its action and maintained-client surface support that proof.

`player_balance` accepts only an exact `equals` value in the unsigned 64-bit range (`0..18446744073709551615`) used by the current `players.balance` load path. The compiler emits one fixed-shape semicolon-free scalar equality query against the exact fixture character's `players.balance` column. Callers cannot select another table, column, predicate or SQL fragment.

`player_balance` deliberately does not enter `scenario-plan.lua.persistence_checks`. The maintained controlled-client surface does not provide one verified generic bank-balance getter suitable for this reusable boundary, so M3 evidence is the successful physical two-session lifecycle followed by the compiled SQL equality check after the second safe logout. Feature-owned bank/NPC scenarios may add a real client-visible bank or UI assertion when they have a maintained-client surface for it.

`tools/e2e/persistence_assertions.py` validates the typed contract. `run_agent_e2e.py` uses validated assertions in two bounded outputs:

1. client-readable `player_field` checks in `scenario-plan.lua.persistence_checks`, executed only after the second physical login by `agent_e2e_scenario.lua`;
2. all typed checks compiled to semicolon-free scalar `SELECT` assertions appended to the normalized manifest and evaluated by the existing SQL assertion path only after the second safe logout.

Feature-specific expected values, storage keys, item IDs and bank balances remain in feature scenario JSON. The shared E2E fixtures contain no invented quest storage numbers, item IDs, economy values or feature-specific outcomes. Arbitrary SQL is not accepted through the typed persistence contract; the legacy scenario-owned `assertions.sql` list remains separately supported for existing scenarios.

A pre-logout SQL observation alone must not be reported as persistence proof. For `player_field`, M3 evidence requires successful safe logout, the existing server-persistence sentinel, relog, controlled-client re-verification, second safe logout and final compiled SQL verification. For `player_storage`, `player_item_presence` and `player_balance`, the same two-session lifecycle must complete before final compiled SQL verification; none of those database-only contracts makes a false claim of direct generic client visibility.

## Example

```json
{
  "steps": [
    {
      "id": "online",
      "action": "observe_online",
      "expected": true
    },
    {
      "id": "channels",
      "action": "request_channels"
    },
    {
      "id": "settle",
      "action": "wait",
      "ms": 250
    }
  ]
}
```

`tests/e2e/scenarios/platform/action-plan-contract.json` is the platform-owned contract scenario. It deliberately avoids map coordinates, item IDs, NPCs and monsters and proves typed `level` persistence through the canonical relog cycle. Storage keys, item IDs and expected bank balances are intentionally not invented in this shared fixture; feature-owned scenarios supply evidence-backed values when they consume `player_storage`, `player_item_presence` or `player_balance`.

The existing `tests/e2e/scenarios/movement/physical-movement.json` scenario is the physical proof consumer for `walk_edge`. Its exact `32369,32241,7 -> 32370,32241,7` fixture was pinned from prior controlled-OTClient artifact evidence in merged PR #481 rather than inferred from memory or invented by the platform task.

## Feature scenario ownership

Concrete physical scenarios should be delivered as bounded child tasks that own their deterministic fixtures and assertions:

1. movement, floor transitions, teleports and doors;
2. combat, damage, death, spells, cooldowns and loot;
3. items, equipment, containers, depot and persistence;
4. NPC dialogue, bank, quest/storage and NPC trade;
5. multi-client player trade, party, guild and chat;
6. forced reconnect, server restart and crash-recovery behavior;
7. malformed-packet and hostile-runtime scenarios through the Security Validation Platform while reusing Universal OTS E2E lifecycle.

Multi-client orchestration and runtime fault injection are not implemented by the action-plan driver itself because they require process/lifecycle capabilities owned by the shared E2E runner/workflow. They must extend the canonical platform rather than creating parallel launchers.
