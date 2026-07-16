# Universal OTS E2E physical gameplay action plans

## Purpose

The Universal OTS E2E platform already owns disposable MariaDB bootstrap, exact server builds, a controlled pinned OTClient build, matching client assets, physical login/logout/relog execution, runtime evidence and cleanup.

This document defines the bounded client-action layer used to extend that same physical lifecycle into gameplay scenarios. It is not a second E2E orchestrator and it does not authorize production targets.

A scenario may add an optional `steps` array. When present, `tools/e2e/run_agent_e2e.py` validates the plan and materializes a deterministic `scenario-plan.lua`. The scenario chooses `tools/e2e/client/agent_e2e_scenario.lua` as its client automation driver. The driver executes the plan during the first physical session, performs a safe logout, waits for server persistence, then executes the existing second login/logout sentinel.

## Safety contract

- Maximum 64 actions per plan.
- Unknown actions and unknown action fields fail validation.
- Step IDs must be unique lowercase slugs.
- Text actions reject embedded newlines, carriage returns and NUL and are bounded to 512 characters.
- Waits and polling timeouts are bounded to 120 seconds.
- Walk repetitions are bounded to 64.
- Item identifiers are bounded unsigned 16-bit values and must be supplied by a feature-owned deterministic fixture; the platform never invents item IDs.
- Creature names, map positions, NPC names, storage values and gameplay expectations belong to feature-owned scenario tasks and must be evidence-backed.
- Credentials are referenced through environment variables; scenario JSON must not embed passwords, tokens or private keys.
- A successful action plan proves only the declared physical assertions. It does not prove full gameplay parity.
- The existing physical E2E lifecycle, exact-head provenance, MariaDB assertions, packet records and fatal-runtime-log checks remain authoritative.

## Supported actions

| Action | Required fields | Optional fields | Physical intent |
|---|---|---|---|
| `wait` | `id`, `action`, `ms` | — | Bounded dispatcher wait. |
| `walk` | `id`, `action`, `direction` | `count`, `interval_ms` | Send bounded directional walk requests. |
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

## Evidence markers

Every step emits:

- `step_<id>=start` before execution;
- `step_<id>=success` after the action or observation succeeds;
- optional `step_<id>_detail=<value>` with bounded diagnostic detail.

After all first-session steps complete, the driver emits `plan=success` and enters the normal safe-logout/persistence/relog lifecycle. A failed action emits `e2e=failure` and terminates the client run.

Feature scenarios should include the exact required step markers in `assertions.required_markers` in addition to the existing login/logout/relog markers.

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

`tests/e2e/scenarios/platform/action-plan-contract.json` is the platform-owned contract scenario. It deliberately avoids map coordinates, item IDs, NPCs and monsters.

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
