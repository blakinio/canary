---
task_id: CAN-20260718-ots-security-shared-state-economy-audit
program_id: CAN-PROGRAM-SECURITY-VALIDATION
status: implementing
agent: "GPT-5.5 Thinking"
branch: docs/ots-security-shared-state-economy-audit-20260718
base_branch: main
created: 2026-07-18T09:58:00+02:00
updated: 2026-07-18T10:47:00+02:00
last_verified_commit: "42b96ba79b7cccc9b02ad6a693035dedb96b08b8"
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

Continue the existing OTS security assessment from the durable PR #453 handover without restarting completed MyAAC/login-stack work. First analysis scope: Canary multichannel global/shared state and exactly-once economy behavior. This task records evidence only and does not implement remediation.

## Routes

- `agent-governance`
- `cpp-runtime`
- `cross-repo`

## Repository boundary

- Writable repository: `blakinio/canary` only.
- Upstream/MyAAC/client/tool repositories remain evidence-only/read-only.
- Dynamic testing, if added later, must use disposable local infrastructure only.
- This task does not modify or extend lifecycle-only PR #522.

## Scope

1. Identify global/shared tables, KV, caches and singleton-like jobs used across channel processes.
2. Trace writer multiplicity, partitioning, ownership, locking/fencing, transaction boundaries, retries, crash consistency, stale writers, duplicate execution and pruning.
3. Continue exactly-once review of market, bank/guild, GameStore/account coins, inbox/depot/stash, trade and house payment/auction flows.
4. Preserve exact source baselines and evidence states.
5. Do not reopen rejected hypotheses without new evidence.

## Acceptance criteria

- [x] Durable PR #453 report/handover and live PR #453/#522 state revalidated.
- [x] Task-start `main` verified as `d9c967d6e9b778da11a206d134d559f38ec1b8c8`.
- [x] Open-PR overlap checked; no exclusive-path overlap with this task identified.
- [x] Dedicated task branch and draft PR #526 created without mixing scope into PR #522.
- [ ] Mechanical global/shared-state inventory completed for the highest-risk remaining writers.
- [ ] Exactly-once/economy continuation completed for remaining depot/inbox/stash, final house settlement and paid-operation flows.
- [x] Qualified findings, revalidations and rejected candidates preserved in `docs/security/OTS_SECURITY_SHARED_STATE_ECONOMY_AUDIT_2026-07-18.md`.
- [x] Changed-file scope remains documentation-only and limited to this task record plus its evidence document.
- [ ] Required GitHub checks pass on the exact final head before readiness/merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T10:47:00+02:00
head: 42b96ba79b7cccc9b02ad6a693035dedb96b08b8
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
  - PR 522 remains lifecycle-only and is not part of this write scope
  - task-start main is d9c967d6e9b778da11a206d134d559f38ec1b8c8
  - OTS-MC-SS-001: every channel periodically rebuilds global players_online from process-local state and can prune other channels
  - OTS-ECO-MKT-001: concurrent partial market fills can both pass a stale amount check and perform value effects before final offer decrement
  - OTS-ECO-MKT-002: market acceptance can load, mutate and full-save a stale DB copy of a counterparty who is online on another channel, risking lost delivery/credit and unrelated stale overwrite
  - OTS-ECO-GUILD-001: process-local guild balances plus absolute saves permit cross-channel stale-snapshot double spend
  - OTS-ECO-HOUSE-001: a house-auction refund applied directly to a bidder online on another channel can be erased by that bidder's later stale full save
  - OTS-ECO-HOUSE-002: house-auction money/refund effects precede durable bid-state persistence, leaving a crash-time duplicate-refund or unbacked-state window
  - OTS-ECO-HOUSE-003: house-transfer debit/refund effects and transfer-state persistence are separate, creating crash-time repeated debit, stranded payment or duplicate refund windows
  - OTS-ECO-TRADE-001: completed bilateral trade is persisted as two independently committing player snapshots, permitting crash-time duplication or loss
  - existing mail-handoff exactly-once class remains current: durable enqueue can precede source-removal persistence, owned apply can be marked APPLIED before recipient save, and offline recipient save can commit before operation APPLIED
  - existing house-isolation finding remains current: channel-scoped schema intent conflicts with UNIQUE(id), unpartitioned load/save/list paths and global cleanup behavior
  - existing single-type account-coin RMW finding remains current; single-type add/remove use SELECT then absolute UPDATE
  - existing bank-transfer crash-consistency, GameStore effect-before-debit, transferable-coin credit-before-debit and market-expiry PENDING findings remain current
  - no public or third-party deployment is authorized for testing
  - shell environment cannot resolve github.com, so local git fetch/worktree preflight is unavailable and live GitHub connector evidence is used instead
derived:
  - a fresh audit-continuation task avoids mixing new findings into lifecycle-only PR 522
unknown:
  - CANDIDATE OTS-MC-SS-C01: global server record writer behavior pending exact Game::loadPlayersRecord/checkPlayersRecord/updatePlayersRecord implementation trace
  - CANDIDATE OTS-MC-SS-C02: raid daily-counter KV reset pending exact raid.kv persistence/namespace proof
  - CANDIDATE OTS-MC-SS-C03: individual global-event, cleanup, highscore and DB-optimization jobs pending concrete call-site classification
  - exhaustive current-source shared-state inventory
  - remaining depot/inbox/stash paths beyond revalidated mail and market call-sites, plus final house settlement exactly-once flows
  - exact-final-head Agent Task Ownership, CI and Security Validation results for the latest checkpoint commit
conflicts: []
first_failure:
  marker: agent-task-ownership-checkpoint-schema
  evidence: Agent Task Ownership run 29637494686 rejected an unsupported nested candidates mapping; after that correction run 29637583328 exposed the missing first_failure field and unsupported validation result tokens
rejected_hypotheses:
  - OTS-MC-JOB-RJ-001: overlapping market.expire leaders alone cannot both apply the same expiry effect because deterministic economic_ledger transaction_uuid insertion rejects the second worker
  - OTS-ECO-COIN-RJ-001: dual-type Account::removeCoins(primary, secondary) does not have the single-type unlocked RMW race; it uses a rollback transaction and SELECT FOR UPDATE
  - previously documented rejected hypotheses remain closed unless new evidence appears
changed_paths:
  - docs/agents/tasks/active/CAN-20260718-ots-security-shared-state-economy-audit.md
  - docs/security/OTS_SECURITY_SHARED_STATE_ECONOMY_AUDIT_2026-07-18.md
validation:
  - command: live GitHub main comparison
    result: PASS
    evidence: task-start main matched d9c967d6e9b778da11a206d134d559f38ec1b8c8
  - command: live open-PR/path overlap review
    result: PASS
    evidence: no exclusive-path overlap identified for the two task-owned documentation paths
  - command: draft PR creation safety check
    result: PASS
    evidence: PR 526 is same-repository branch -> blakinio/canary:main
  - command: current-source audit continuation
    result: PASS
    evidence: durable evidence report is preserved in the task-owned security document through report commit 42b96ba79b7cccc9b02ad6a693035dedb96b08b8
  - command: PR 526 changed-file scope
    result: PASS
    evidence: only the task record and audit evidence document are changed
  - command: Agent Task Ownership on head 421fbe5a21ee49f7b797bab3f56ee864dd6545fb
    result: PASS
    evidence: workflow run 29637804392 completed successfully after checkpoint schema normalization
  - command: CI on head 421fbe5a21ee49f7b797bab3f56ee864dd6545fb
    result: PASS
    evidence: workflow run 29637804516 completed successfully
  - command: Agent Task Ownership run 29637494686
    result: FAIL
    evidence: checkpoint used an unsupported nested candidates mapping
  - command: Agent Task Ownership run 29637583328
    result: FAIL
    evidence: diagnostics required first_failure and rejected validation result tokens UNAVAILABLE and FIXED_IN_HEAD
blockers:
  - disposable shell cannot currently fetch/clone GitHub, so physical two-process race/crash proofs are unavailable in this environment
next_action: Finish concrete shared-state writer inventory (global record, raid KV, cleanup/highscore/DB optimization), then continue remaining depot/inbox/stash and final house settlement exactly-once review before opening any remediation task.
```
