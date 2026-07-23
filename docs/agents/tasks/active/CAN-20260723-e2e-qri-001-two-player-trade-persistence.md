---
task_id: CAN-20260723-e2e-qri-001-two-player-trade-persistence
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-001
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/e2e-qri-001-two-player-trade-persistence
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "4e5a013c1bccfc3b359f6610d8f9ffc36275ec44"
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

- [x] Reuse the existing Universal Physical E2E lifecycle and bounded one-secondary-client orchestration without modifying shared runner/workflow files.
- [x] Keep feature-specific trade intent only in the QRI-001 task/scenario/test/Lua paths.
- [x] Prove distinct Player A and Player B controlled-client identities and artifact streams.
- [x] Prove the real maintained-OTClient bilateral player-trade request/counter-offer/accept path; no DB mutation or internal server trade function substitutes for the transfer.
- [x] Prove immediate tracked-resource ownership `A=0`, `B=1`, `A+B=1` after trade.
- [x] Safely logout and relog both actors and prove the same `A=0`, `B=1`, `A+B=1` tracked-resource state.
- [x] Reuse typed persistence assertions where supported and bounded post-cycle SQL for secondary/cross-actor conservation.
- [x] Prove no tracked-resource duplication/loss and `players_online=0` after both controlled clients exit.
- [x] Preserve actor, last successful step, first failed step, expected/observed state and per-client logs in failure evidence.
- [ ] Pass focused contract/static tests, scenario/schema validation, relevant integration tests, physical two-client E2E, persistence/cleanup validation, Agent Task Ownership and repository CI on the exact final checkpoint head.
- [x] Apply `ci:final-gate` before the final checkpoint commit; make no post-gate head change without revalidation.
- [ ] Audit exact changed paths, reviews/comments and final checkpoint head before squash merge; then complete active-to-archive lifecycle closure.

## Integration debt

- `E2E-QRI-005` was not delivered on the verified baseline; QRI-001 consumes the current runner `result.json` contract and does not introduce a competing standard envelope.
- `E2E-QRI-006` was not delivered on the verified baseline; QRI-001 proves bounded cleanup with controlled exits plus `players_online=0`, but does not claim or implement `cleanup_certified`.
- Current typed persistence assertions are scoped to the primary scenario fixture. Secondary exact tracked-resource ownership and cross-actor conservation remain on the existing post-cycle SQL boundary.

## Candidate evidence audit

- Candidate feature head before this final checkpoint: `4e5a013c1bccfc3b359f6610d8f9ffc36275ec44`.
- Candidate PR merge candidate exercised by the successful physical run: `6fcbd1e61394e7cbb0ca7c99186df41918a59fd8`.
- Candidate Agent Task Ownership: PASS, run `30031054744`.
- Candidate CI: PASS, run `30031054735`.
- Physical Universal Agent E2E: PASS, run `30031054740`, physical job `89294034159`, required physical gate `89295543817`.
- Physical evidence artifact: `8574255440`, digest `sha256:6c68eba232b908f9efb8575299c888db972fc0df93973da93ee742b10124d401`.
- Physical result: `status=success`, primary client exit `0`, secondary client exit `0`, no fatal runtime log, required markers PASS, two primary packet records, two primary server logins, `lastlogin` and `lastlogout` persisted, all scenario SQL assertions PASS.
- Trade evidence: mutual visibility at primary `32369,32241,7` and secondary `32369,32242,7`; primary real `requestTrade`; secondary real counter-offer `requestTrade` using existing count-1 item `3374`; own/counter offers observed; bilateral `acceptTrade`; both trade-close events observed.
- Immediate conservation: `Paladin 15` tracked item `3043` count `0`, `Paladin 14` count `1`, total tracked count `1`.
- Relog conservation: after both actors safely logout and relog, tracked state remains `A=0`, `B=1`, total `1`.
- Post-cycle SQL: primary item `3043` absent, secondary item `3043` present exactly once, cross-actor total exactly one, both actors have persisted login/logout timestamps, final `players_online=0`, typed primary absence assertion PASS.
- Teardown evidence: both secondary sessions and both primary sessions complete; secondary release received; secondary exit clean; final primary logout complete; both controlled client exit codes are zero; final online count is zero.
- Latest verified `main` before this checkpoint: `baea9fc37156117be91dbcfc7985ef7b4ecd3573`. Changes since the physical run baseline do not modify QRI-001 paths, the shared Universal E2E runner/workflow, multi-client orchestration or persistence compiler; fresh PR compare still reports exactly five QRI-001 changed paths.
- Review audit before final checkpoint: no PR comments, no review submissions and no inline review threads.
- `ci:final-gate` was applied to PR #806 before this final checkpoint commit and the PR was marked ready for review.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T20:27:28+02:00
head: 4e5a013c1bccfc3b359f6610d8f9ffc36275ec44
branch: feat/e2e-qri-001-two-player-trade-persistence
pr: 806
status: ready
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
  - Exact candidate branch head 4e5a013c1bccfc3b359f6610d8f9ffc36275ec44 passed Agent Task Ownership and repository CI.
  - Universal Agent E2E run 30031054740 physically passed the QRI-001 two-client scenario; required physical gate 89295543817 passed.
  - The physical run exercised real maintained-OTClient primary requestTrade, real secondary counter-offer requestTrade, bilateral offer observation, bilateral acceptTrade and both close events.
  - Immediate tracked item 3043 conservation passed as A=0, B=1, total=1.
  - Both actors safely logged out and relogged; post-relog tracked conservation remained A=0, B=1, total=1.
  - All seven post-cycle SQL assertions passed, including typed primary absence and final players_online=0.
  - Both controlled client exit codes are zero; no fatal runtime log was found.
  - Physical artifact 8574255440 is retained with digest sha256:6c68eba232b908f9efb8575299c888db972fc0df93973da93ee742b10124d401.
  - Fresh current-main audit at baea9fc37156117be91dbcfc7985ef7b4ecd3573 found no overlap with QRI-001 or its shared read-only Universal E2E contracts; PR diff remains exactly five feature-owned paths.
  - PR #806 has no comments, reviews or review threads before the final checkpoint.
  - ci:final-gate was applied before this final checkpoint commit.
derived:
  - The previous relog failure was client container-view materialization rather than persistence loss because post-cycle SQL already proved the secondary durable item; bounded re-open within the existing timeout resolved it without weakening persistence criteria.
  - The real bilateral protocol handshake requires a secondary counter-offer before both clients can observe complete offer state and accept.
unknown:
  - Exact final checkpoint-head gate results until this commit completes Agent Task Ownership, full final-gate CI and Universal Agent E2E validation.
  - Standalone local execution of tests/e2e/test_qri_001_two_player_trade.py remains unavailable because the local environment cannot resolve github.com; final-gate CI must provide the authoritative focused/static coverage required before merge.
conflicts: []
first_failure:
  marker: none
  evidence: Candidate physical run 30031054740 passed real bilateral trade, immediate conservation, safe logout/relog, durable conservation, SQL persistence and cleanup. Only final checkpoint-head validation remains.
rejected_hypotheses:
  - Increase runtime timeout; rejected because physical failures supplied deterministic protocol, visibility or container-materialization evidence rather than elapsed-time evidence.
  - Use ADM1 as the final primary actor; rejected because physical evidence proved asymmetric player visibility.
  - Treat fixture creation as trade proof; rejected because fixture creation without real transfer failed an earlier run.
  - Call acceptTrade on Player B immediately after Player A request; rejected because maintained-client protocol evidence requires complete counter-offer state.
  - Add a server-side trade helper or direct DB transfer; rejected because QRI-001 must prove the real player protocol path.
  - Implement QRI-005 or QRI-006 inside QRI-001; rejected as separate packages/integration debt.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-qri-001-two-player-trade-persistence.md
  - tests/e2e/scenarios/multiclient/player-trade-persistence.json
  - tests/e2e/scenarios/multiclient/player-trade-persistence/primary.lua
  - tests/e2e/scenarios/multiclient/player-trade-persistence/secondary.lua
  - tests/e2e/test_qri_001_two_player_trade.py
validation:
  - command: Agent Task Ownership run 30031054744
    result: PASS
    evidence: Ownership and task-record governance passed on candidate feature head 4e5a013c1bccfc3b359f6610d8f9ffc36275ec44.
  - command: CI run 30031054735
    result: PASS
    evidence: Repository required CI passed on candidate feature head 4e5a013c1bccfc3b359f6610d8f9ffc36275ec44.
  - command: Universal Agent E2E run 30031054740
    result: PASS
    evidence: Physical job 89294034159 and required gate 89295543817 passed real bilateral trade, relog persistence and cleanup; artifact 8574255440 retained exact evidence.
  - command: Physical artifact SQL and lifecycle audit
    result: PASS
    evidence: All seven SQL assertions passed; immediate and relog conservation are A=0 B=1 total=1; both client exits are zero; final players_online=0.
  - command: Current-main and review audit before final checkpoint
    result: PASS
    evidence: main baea9fc37156117be91dbcfc7985ef7b4ecd3573 adds no overlap with QRI-001/shared Universal E2E contracts; PR diff remains five feature-owned paths; comments, reviews and review threads are empty.
blockers:
  - Exact final checkpoint-head Agent Task Ownership, full ci:final-gate CI and Universal Agent E2E must pass with no later feature-branch commit.
  - Focused/static QRI-001 contract coverage must be green in the authoritative final-gate validation before merge; no standalone local PASS is claimed.
next_action: Make no further feature-branch commit. Require exact final checkpoint-head gates, then perform final scope/review audit, squash-merge PR #806 with expected head SHA, verify main, and complete lifecycle-only active-to-archive closure.
```
