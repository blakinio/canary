---
task_id: CAN-20260723-e2e-qri-001-two-player-trade-persistence
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-001
status: active
agent: "GPT-5.6 Thinking"
branch: feat/e2e-qri-001-two-player-trade-persistence
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "489607174f22b8b36663fe2251cdba0423388fbd"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - canary-universal-e2e-two-client-orchestration-v1
  - existing Universal Physical E2E login and persistence assertion contracts
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-e2e-qri-001-two-player-trade-persistence.md
    - docs/agents/tasks/archive/CAN-20260723-e2e-qri-001-two-player-trade-persistence.md
    - tests/e2e/scenarios/multiclient/player-trade-persistence.json
    - tests/e2e/scenarios/multiclient/player-trade-persistence/primary.lua
    - tests/e2e/scenarios/multiclient/player-trade-persistence/secondary.lua
    - tests/e2e/test_qri_001_two_player_trade.py
  shared: []
  read_only:
    - tools/e2e/multi_client_orchestration.py
    - tools/e2e/client/agent_e2e_multi_client.lua
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/persistence_assertions.py
    - docker/data/01-test_account.sql
    - docker/data/02-test_account_players.sql
    - data/scripts/talkactions/god/create_item.lua
    - .github/workflows/universal-agent-e2e.yml
modules_touched:
  - Universal E2E feature-owned multiclient trade scenario
reuses:
  - existing disposable Canary/MariaDB/controlled-OTClient lifecycle
  - canary-universal-e2e-two-client-orchestration-v1
  - existing @test14/@test15 deterministic accounts and Paladin fixtures
  - existing god /i talk action for deterministic fixture preparation only
  - existing safe logout and controlled relog flow
  - existing persistence assertion compiler and post-cycle SQL evaluator
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260723 — E2E-QRI-001 real two-player trade + persistence

## Goal

Deliver one bounded deterministic physical two-player trade sentinel on the canonical Universal Physical E2E lifecycle: two controlled OTClients log in, Player A creates exactly one repository-known backpack fixture through the existing god `/i` talk action, Player A offers that real inventory item to Player B through the normal player-trade protocol, both clients accept, both clients verify immediate ownership/conservation, both safely logout and relog, both verify the same durable state, and final SQL verifies exact conservation plus zero connected test players.

The fixture action is preparation only. It is not accepted as trade proof. Trade proof requires the maintained OTClient `g_game.requestTrade`/`g_game.acceptTrade` protocol path and controlled-client observations on both actors.

## Bounded scope

Included:

- exactly two controlled actors: primary `Paladin 15` and secondary `Paladin 14`;
- exactly one deterministic backpack item (`server item id 2854`) created by the existing god `/i` talk action on Player A;
- one-way `A -> B` player trade;
- real request, counter-offer observation, bilateral accept and trade-close events;
- immediate controlled-client inventory assertions;
- safe logout/relog of both actors;
- post-relog controlled-client inventory assertions;
- typed primary persistence assertion plus exact cross-actor SQL conservation assertions;
- final `players_online = 0` cleanup assertion.

Explicitly excluded:

- multiple items or stack splitting;
- capacity/full-inventory edge cases;
- timeout/disconnect during trade;
- concurrent trade or retry/exactly-once semantics;
- market behavior;
- actor-count generalization;
- a second multi-client runner or workflow;
- QRI-005 result-envelope implementation;
- QRI-006 cleanup-certification implementation.

## Acceptance criteria

- [ ] Reuse the existing Universal Physical E2E lifecycle and bounded one-secondary-client orchestration without modifying shared runner/workflow files.
- [ ] Keep feature-specific trade intent only in the new QRI-001 scenario/test/Lua paths.
- [ ] Prove distinct Player A and Player B controlled-client identities and artifact streams.
- [ ] Prove the real OTClient player-trade request/accept path; no DB mutation or internal server trade function may substitute for the transfer.
- [ ] Prove immediate `A=0`, `B=1`, `A+B=1` inventory ownership after trade.
- [ ] Safely logout and relog both actors and prove the same `A=0`, `B=1`, `A+B=1` state after relog.
- [ ] Reuse typed persistence assertions where the current contract supports them and use bounded post-cycle SQL for secondary/cross-actor conservation.
- [ ] Prove no duplication, no loss and `players_online=0` after both clients exit.
- [ ] Preserve actor, last successful step, first failed step, expected/observed state and per-client logs in failure evidence.
- [ ] Pass focused static/unit tests, scenario/schema validation, relevant integration tests, physical two-client E2E, persistence/cleanup validation, Agent Task Ownership and repository CI on the exact final head.
- [ ] Apply `ci:final-gate` before the final checkpoint commit when required by current governance; make no post-gate head change without revalidation.
- [ ] Audit exact changed paths, reviews/comments and final head before squash merge; then complete active-to-archive lifecycle closure.

## Integration debt

- `E2E-QRI-005` is not delivered on verified `main`; QRI-001 will consume the current runner `result.json` contract and must not introduce a competing standard envelope.
- `E2E-QRI-006` is not delivered on verified `main`; QRI-001 will prove bounded cleanup with both controlled client exits plus `players_online=0`, but must not claim or implement the future standard `cleanup_certified` contract.
- Current typed persistence assertions are scoped to the primary scenario fixture. Secondary exact ownership and cross-actor conservation therefore remain on the existing post-cycle SQL boundary in this package.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T16:20:00+02:00
head: 489607174f22b8b36663fe2251cdba0423388fbd
branch: feat/e2e-qri-001-two-player-trade-persistence
pr: null
status: implementing
context_routes:
  - universal-e2e
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-qri-001-two-player-trade-persistence.md
  - docs/agents/tasks/archive/CAN-20260723-e2e-qri-001-two-player-trade-persistence.md
  - tests/e2e/scenarios/multiclient/player-trade-persistence.json
  - tests/e2e/scenarios/multiclient/player-trade-persistence/primary.lua
  - tests/e2e/scenarios/multiclient/player-trade-persistence/secondary.lua
  - tests/e2e/test_qri_001_two_player_trade.py
proven:
  - main is exactly 489607174f22b8b36663fe2251cdba0423388fbd at preflight.
  - No PR tagged E2E-QRI-001, E2E-QRI-002, E2E-QRI-003, E2E-QRI-005 or E2E-QRI-006 was found during fresh PR search.
  - The merged bounded two-client contract supports exactly one secondary controlled OTClient and is runtime-proven by the E2E-GAMEPLAY-006 lineage.
  - The pinned maintained OTClient ref exposes g_game.requestTrade, g_game.acceptTrade and trade lifecycle callbacks onOwnTrade/onCounterTrade/onCloseTrade.
  - The existing god /i talk action accepts item names and creates backpack item id 2854 when needed; it will be used only for fixture preparation.
  - The existing persistence assertion contract supports player_item_presence on player_items; cross-actor checks can use the existing semicolon-free SELECT SQL assertion boundary.
  - Current main result.json is runner schema v2 but is not the QRI-005 standard result envelope, and current cleanup does not provide QRI-006 cleanup certification.
derived:
  - A single non-stackable backpack fixture avoids stack-split and recipient-container edge cases while preserving a real item transfer.
  - Primary Paladin 15 can reuse the already-established administrator test account for the fixed fixture command while secondary Paladin 14 remains a normal distinct actor.
unknown:
  - Exact maintained-client inventory slot behavior for the traded backpack until focused implementation/physical evidence runs.
  - Exact final GitHub Actions outcome and physical runtime evidence for QRI-001.
conflicts: []
first_failure:
  marker: none
  evidence: No QRI-001 implementation has run yet.
rejected_hypotheses:
  - Add a second multi-client runner; rejected because the bounded reusable orchestration already exists.
  - Add a new scenario-specific SQL fixture contract; rejected because that would create a competing shared runner interface when the existing fixed god talk action can prepare the one-item fixture through a controlled client.
  - Implement QRI-005 or QRI-006 inside QRI-001; rejected because both are separate packages and absent dependencies are recorded as integration debt.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-qri-001-two-player-trade-persistence.md
validation: []
blockers: []
next_action: Open the draft PR, then add only the feature-owned scenario, primary/secondary controlled-client automations and focused contract tests; keep all shared Universal E2E paths read-only.
```
