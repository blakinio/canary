---
task_id: CAN-20260723-e2e-qri-001-two-player-trade-persistence
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-001
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/e2e-qri-001-two-player-trade-persistence
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "930d7553e87c66e9e00a68c640c86f3d22d16e88"
risk: medium
related_issue: ""
related_pr: "806"
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
  - existing god /i talk action for deterministic tracked-resource preparation only
  - existing safe logout and controlled relog flow
  - existing persistence assertion compiler and post-cycle SQL evaluator
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260723 — E2E-QRI-001 real two-player trade + persistence

## Goal

Deliver one bounded deterministic physical two-player trade sentinel on the canonical Universal Physical E2E lifecycle. Two controlled OTClients (`Paladin 15` and `Paladin 14`) must reach mutual visibility, prove both actors initially have zero tracked item `3043`, prepare exactly one tracked item `3043` for Player A through the existing god `/i` talk action, complete the real bilateral player-trade offer handshake through maintained-OTClient `requestTrade` calls, accept on both clients, prove immediate tracked-resource ownership and conservation, safely logout/relog, prove the same durable tracked-resource state, and finish with exact SQL conservation plus `players_online = 0`.

The `/i` action is fixture preparation only. It is not accepted as trade proof. Trade proof requires maintained-client request/counter-offer/accept/close observations on both actors and the post-trade ownership transition.

## Bounded scope

Included:

- exactly two controlled actors: primary `Paladin 15` on `@test15` and secondary `Paladin 14` on `@test14`;
- exactly one tracked resource, item `3043`, created by the existing god `/i` talk action on Player A;
- one existing count-1 non-3043 Player B inventory item selected deterministically as the real protocol counter-offer;
- real bilateral `requestTrade`, own/counter offer observation, bilateral `acceptTrade`, and close events;
- tracked-resource transfer `A -> B` with immediate `A=0`, `B=1`, `A+B=1`;
- safe logout/relog of both actors and the same post-relog tracked-resource assertions;
- typed primary persistence assertion plus exact cross-actor SQL tracked-resource conservation;
- final `players_online = 0` cleanup assertion.

Explicitly excluded:

- multiple tracked resources or stack splitting;
- capacity/full-inventory edges;
- timeout/disconnect during trade;
- concurrent trade or retry/exactly-once semantics;
- market behavior;
- actor-count generalization;
- a second multi-client runner or workflow;
- QRI-005 result-envelope implementation;
- QRI-006 cleanup-certification implementation.

## Acceptance criteria

- [ ] Reuse the existing Universal Physical E2E lifecycle and bounded one-secondary-client orchestration without modifying shared runner/workflow files.
- [ ] Keep feature-specific trade intent only in the QRI-001 task/scenario/test/Lua paths.
- [ ] Prove distinct Player A and Player B controlled-client identities and artifact streams.
- [ ] Prove the real maintained-OTClient bilateral player-trade request/counter-offer/accept path; no DB mutation or internal server trade function may substitute for the transfer.
- [ ] Prove immediate tracked-resource ownership `A=0`, `B=1`, `A+B=1` after trade.
- [ ] Safely logout and relog both actors and prove the same `A=0`, `B=1`, `A+B=1` tracked-resource state.
- [ ] Reuse typed persistence assertions where supported and bounded post-cycle SQL for secondary/cross-actor conservation.
- [ ] Prove no tracked-resource duplication/loss and `players_online=0` after both controlled clients exit.
- [x] Preserve actor, last successful step, first failed step, expected/observed state and per-client logs in failure evidence.
- [ ] Pass focused contract/static tests, scenario/schema validation, relevant integration tests, physical two-client E2E, persistence/cleanup validation, Agent Task Ownership and repository CI on the exact final head.
- [ ] Apply `ci:final-gate` before the final checkpoint commit; make no post-gate head change without revalidation.
- [ ] Audit exact changed paths, reviews/comments and final head before squash merge; then complete active-to-archive lifecycle closure.

## Integration debt

- `E2E-QRI-005` was not delivered on the verified baseline; QRI-001 consumes the current runner `result.json` contract and does not introduce a competing standard envelope.
- `E2E-QRI-006` was not delivered on the verified baseline; QRI-001 proves bounded cleanup with controlled exits plus `players_online=0`, but does not claim or implement `cleanup_certified`.
- Current typed persistence assertions are scoped to the primary scenario fixture. Secondary exact tracked-resource ownership and cross-actor conservation remain on the existing post-cycle SQL boundary.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T19:03:00+02:00
head: d4fdfaeeb7a2877d2528d5d5e00c34470c471dfb
branch: feat/e2e-qri-001-two-player-trade-persistence
pr: 806
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
  - Latest verified main before this checkpoint was 930d7553e87c66e9e00a68c640c86f3d22d16e88; exact compare showed only the five QRI-001 changed paths and no overlap with the merged QRI-003 paths.
  - The bounded two-client contract provides exactly one secondary controlled OTClient; no shared runner or workflow file is modified by QRI-001.
  - The maintained OTClient ref exposes requestTrade, acceptTrade and onOwnTrade/onCounterTrade/onCloseTrade. Its player-trade module enables acceptance only after a counter offer is received.
  - Physical run 30020718345 proved the ADM1 primary fixture is asymmetric for player visibility; the actor was reverted to Paladin 15 without increasing timeout.
  - Physical run 30024132772 proved Paladin 15 and Paladin 14 mutual visibility, zero-item-3043 preconditions, /i fixture creation, and a real primary requestTrade. It failed before transfer because only the primary own offer was observed; the secondary received no offer callback and no counter offer existed.
  - The current implementation performs a real secondary requestTrade with one existing count-1 non-3043 item after the primary request marker, requires secondary own plus counter offer observations, and only then sends bilateral acceptance.
  - CI run 30027183101 and Agent Task Ownership run 30027182837 passed on head 8ae04c98c6f194dd589f46bb274b1649dab96ddf.
  - Universal Agent E2E run 30027183156 reached a Resolve scenario failure before physical execution; database bootstrap passed. No physical result is claimed from that run.
derived:
  - Run 30024132772 failed on a missing bilateral trade handshake, not timing: maintained-client acceptance requires counter-offer state while the run recorded only the primary own offer.
  - A count-1 non-3043 counter-offer avoids stack-split behavior and keeps item 3043 as the sole tracked conservation resource.
unknown:
  - Exact physical runtime result for the bilateral handshake implementation.
  - Focused QRI-001 unittest result; local execution was attempted but the available local environment could not resolve github.com, so no PASS is claimed.
conflicts: []
first_failure:
  marker: trade_offer
  evidence: Physical run 30024132772 last succeeded at trade_request_sent; primary own offer was observed, secondary offer was absent, item 3043 remained with Player A, and players_online returned to zero. The implementation now adds the real secondary counter-offer request required before bilateral acceptance.
rejected_hypotheses:
  - Increase runtime timeout; rejected because physical failures supplied deterministic protocol/visibility evidence rather than elapsed-time evidence.
  - Use ADM1 as the final primary actor; rejected because physical evidence proved asymmetric player visibility.
  - Treat fixture creation as trade proof; rejected because run 30024132772 created item 3043 but no transfer occurred.
  - Call acceptTrade on Player B immediately after Player A request; rejected because maintained-client protocol evidence shows acceptance becomes actionable only after a counter offer.
  - Add a server-side trade helper or direct DB transfer; rejected because QRI-001 must prove the real player protocol path.
  - Implement QRI-005 or QRI-006 inside QRI-001; rejected as separate packages/integration debt.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-qri-001-two-player-trade-persistence.md
  - tests/e2e/scenarios/multiclient/player-trade-persistence.json
  - tests/e2e/scenarios/multiclient/player-trade-persistence/primary.lua
  - tests/e2e/scenarios/multiclient/player-trade-persistence/secondary.lua
  - tests/e2e/test_qri_001_two_player_trade.py
validation:
  - command: CI run 30027183101
    result: PASS
    evidence: Repository CI passed on bilateral-handshake head 8ae04c98c6f194dd589f46bb274b1649dab96ddf.
  - command: Agent Task Ownership run 30027182837
    result: PASS
    evidence: Ownership and task-record governance passed on bilateral-handshake head 8ae04c98c6f194dd589f46bb274b1649dab96ddf.
  - command: Universal Agent E2E run 30027183156
    result: FAIL
    evidence: Resolve scenario failed before physical execution; database bootstrap passed. Fresh validation is required on this checkpoint successor.
blockers:
  - Fresh Universal Agent E2E must resolve the scenario and execute the bilateral physical trade path successfully.
  - Focused QRI-001 unittest still needs an executable repository environment; no PASS is claimed yet.
next_action: Run fresh exact-head validation, inspect the first causal failure if any, then apply only QRI-001-owned fixes until physical trade, relog persistence and cleanup pass.
```
