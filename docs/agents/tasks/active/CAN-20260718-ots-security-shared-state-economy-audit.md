---
task_id: CAN-20260718-ots-security-shared-state-economy-audit
program_id: CAN-PROGRAM-SECURITY-VALIDATION
status: implementing
agent: "GPT-5.5 Thinking"
branch: docs/ots-security-shared-state-economy-audit-20260718
base_branch: main
created: 2026-07-18T09:58:00+02:00
updated: 2026-07-18T10:12:00+02:00
last_verified_commit: "fad383bd15f58e99b086e5ca82ed5039eab34d06"
risk: high
related_issue: ""
related_pr: "526"
depends_on:
  - "CAN-20260717-myaac-canary-security-audit / PR #453 durable handover"
blocks:
  - future bounded multichannel/economy remediation tasks
  - future dynamic race validation scenarios
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260718-ots-security-shared-state-economy-audit.md
    - docs/security/OTS_SECURITY_SHARED_STATE_ECONOMY_AUDIT_2026-07-18.md
  shared: []
  read_only:
    - src/**
    - data/**
    - data-otservbr-global/**
    - schema.sql
    - docker/**
    - opentibiabr/canary
    - opentibiabr/login-server
    - slawkens/myaac
    - opentibiabr/otclient
    - opentibiabr/remeres-map-editor
    - opentibiabr/client-editor
modules_touched:
  - security-audit
  - multichannel shared-state review
  - economy exactly-once review
reuses:
  - existing MyAAC/Canary security audit and OTS security continuation handover
  - existing agent task governance and evidence-state contracts
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260718 — OTS shared-state / economy security audit continuation

## Goal

Continue the existing OTS security assessment from the durable PR #453 handover without restarting completed MyAAC/login-stack work. The first analysis scope is Canary multichannel global/shared state and exactly-once economy behavior. This task records evidence only and does not implement remediation.

## Routes

- `agent-governance`
- `cpp-runtime`
- `cross-repo`

## Repository boundary

- Writable repository: `blakinio/canary` only.
- `opentibiabr/canary`, `opentibiabr/login-server`, `slawkens/myaac`, `opentibiabr/otclient`, `opentibiabr/remeres-map-editor`, and `opentibiabr/client-editor` remain evidence-only/read-only.
- Dynamic testing, if added later, must use disposable local infrastructure only.
- This task does not modify or extend lifecycle-only PR #522.

## Scope

1. Mechanically identify global/shared tables, KV, caches and singleton-like jobs used across channel processes.
2. Trace writer multiplicity, partitioning, ownership, locking/fencing, transaction boundaries, retries, crash consistency, stale writers, duplicate execution and pruning.
3. Continue exactly-once review of market partial fills, bank/guild transfers, GameStore/account coins, inbox/depot/stash handoff, trade completion, house auctions/payments and paid MyAAC operations where current evidence warrants follow-up.
4. Preserve exact source baselines and classify each hypothesis as `PROVEN`, `DYNAMICALLY CONFIRMED`, `DERIVED`, `CONFIGURATION-DEPENDENT`, `CANDIDATE`, `UNKNOWN`, or `REJECTED`.
5. Do not reopen explicitly rejected hypotheses without new evidence.

## Acceptance criteria

- [x] Durable PR #453 report/handover and live PR #453/#522 state revalidated.
- [x] Current `main` verified as `d9c967d6e9b778da11a206d134d559f38ec1b8c8` through live GitHub compare evidence.
- [x] Open-PR overlap checked; no exclusive path overlap with this task's two documentation paths identified.
- [x] Dedicated task branch and draft PR #526 created without mixing scope into PR #522.
- [ ] Mechanical global/shared-state inventory completed for the highest-risk multichannel writers.
- [ ] Exactly-once/economy continuation completed for the highest-risk remaining flows with concrete failure timelines.
- [x] New findings and rejected candidates preserved in `docs/security/OTS_SECURITY_SHARED_STATE_ECONOMY_AUDIT_2026-07-18.md`.
- [ ] Changed-file scope remains documentation-only and limited to this task record plus its evidence document.
- [ ] Required GitHub checks pass on the exact final head before readiness/merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T10:12:00+02:00
head: fad383bd15f58e99b086e5ca82ed5039eab34d06
branch: docs/ots-security-shared-state-economy-audit-20260718
pr: 526
status: implementing
context_routes:
  - agent-governance
  - cpp-runtime
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260718-ots-security-shared-state-economy-audit.md
  - docs/security/OTS_SECURITY_SHARED_STATE_ECONOMY_AUDIT_2026-07-18.md
proven:
  - PR 453 is squash-merged with merge SHA 6b42890347338a13daca5fd6291b56b8dc6aa091
  - PR 522 is still open and lifecycle-only for the merged PR 453 task record
  - current main at task start is d9c967d6e9b778da11a206d134d559f38ec1b8c8
  - open PR 514 owns security runtime validation paths and does not overlap this task's exclusive documentation paths
  - open PR 487 changes only tests/unit/game/multichannel/channel_registry_test.cpp
  - draft PR 526 targets blakinio/canary:main from the dedicated same-repository task branch
  - OTS-MC-SS-001: every channel periodically rebuilds global players_online from process-local player state and can prune other channels
  - OTS-ECO-MKT-001: concurrent partial market fills can both pass a stale offer-amount check and perform value effects before final offer decrement
  - OTS-ECO-GUILD-001: guild balance is loaded into process-local state and later saved as an absolute value, permitting multichannel stale-snapshot double-spend/lost update
  - existing GameStore effect-before-debit and transferable-coin credit-before-debit findings remain current at this baseline
  - existing market-expiry PENDING crash-recovery wedge remains current
  - no public or third-party deployment is authorized for testing
  - shell environment cannot resolve github.com, so local git fetch/worktree preflight is unavailable and live GitHub connector evidence is used instead
derived:
  - a fresh audit-continuation task avoids mixing new findings into lifecycle-only PR 522
candidates:
  - global server record writer race pending Game::loadPlayersRecord/checkPlayersRecord implementation trace
  - raid daily-counter KV reset pending exact raid.kv persistence/namespace proof
  - individual global-event, cleanup, highscore and DB-optimization jobs pending concrete call-site classification
unknown:
  - complete current-source shared-state inventory
  - remaining bank/trade/stash/house-payment exactly-once flows
conflicts: []
rejected_hypotheses:
  - OTS-MC-JOB-RJ-001: overlapping market.expire leaders alone cannot both apply the same expiry effect because deterministic economic_ledger transaction_uuid primary-key insertion fails closed for the second worker
  - previously documented rejected hypotheses remain closed unless new evidence appears
changed_paths:
  - docs/agents/tasks/active/CAN-20260718-ots-security-shared-state-economy-audit.md
  - docs/security/OTS_SECURITY_SHARED_STATE_ECONOMY_AUDIT_2026-07-18.md
validation:
  - command: local disposable git clone/preflight
    result: UNAVAILABLE
    evidence: shell DNS could not resolve github.com; no existing checkout was present
  - command: live GitHub main comparison
    result: PASS
    evidence: main is identical to d9c967d6e9b778da11a206d134d559f38ec1b8c8 at task start
  - command: live open-PR/path overlap review
    result: PASS
    evidence: no exclusive-path overlap identified for the new task/evidence paths
  - command: draft PR creation safety check
    result: PASS
    evidence: PR 526 base/head repositories are blakinio/canary and base is main
  - command: current-source audit continuation
    result: PASS
    evidence: durable evidence report added at fad383bd15f58e99b086e5ca82ed5039eab34d06
blockers:
  - disposable shell currently cannot fetch/clone GitHub, so physical two-process dynamic race proofs are not available in this environment
next_action: Trace Game::loadPlayersRecord/checkPlayersRecord, raid.kv persistence, concrete cleanup/highscore/DB-optimization writers, then continue bank/trade/depot-inbox-stash/house-payment exactly-once review before creating any remediation tasks.
```
