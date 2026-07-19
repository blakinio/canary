---
task_id: CAN-20260719-oteryn-market-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-021
status: implementing
agent: "GPT-5.5 Thinking"
branch: task/CAN-20260719-oteryn-market-revalidation
base_branch: main
created: 2026-07-19
updated: 2026-07-19
last_verified_commit: "b90e287a40413102c87e8c7fa3d5c01ad401cb6d"
risk: high
related_pr: "607"
depends_on:
  - OAM-004 player-persistence foundation
  - OAM-006 protocol
blocks:
  - OAM-022
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260719-oteryn-market-revalidation.md
    - docs/agents/OTERYN_OAM_021_MARKET_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/real-tibia/registry/modules/market.yaml
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
modules_touched:
  - market
reuses:
  - completed OAM-004 player-persistence boundary
  - completed OAM-006 protocol boundary
  - completed OAM-020 exaltation-forge interaction boundary
public_interfaces:
  - market offers and history
  - market limits and fees
  - market item eligibility
  - server-client market packets
cross_repo_tasks:
  - blakinio/Otheryn OAM-021 target revalidation and bounded implementation/proof
---

# Goal

Revalidate canonical OAM-021 `market` against fresh live legacy, clean-target, upstream and maintained-client baselines; select only the strongest dependency-valid target disposition; implement or prove only the bounded accepted market contract in Otheryn; then complete governance, lifecycle archival and durable program reconciliation before OAM-022 starts.

# Immutable task-start baselines

- Canary: `183d7224cb5de57585294d72631f37783b93dc89`
- Otheryn: `d59207d05ab6dd9450b05d0a6b4d9122fda60489`
- upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`
- previous durable OAM-020 Canary reconciliation: `bde118d04d17cd3b11ba555a735448e92dffe2fe`

# Fresh preflight

- Otheryn had no open pull request at task start.
- Maintained OTClient had no open pull request at task start.
- No OAM-021 branch or pull request existed in Canary or Otheryn at task start.
- Canary advanced exactly one commit after the OAM-020 durable reconciliation, to `183d7224cb5de57585294d72631f37783b93dc89`; that commit changed only unrelated E2E skill-persistence documentation/tests/tooling and did not overlap this task's exclusive governance paths.
- Canonical `market` depends on completed `player-persistence` and `protocol`; `exaltation-forge` is an interaction and is completed.
- Open Canary PR #526 is an evidence-only shared-state/economy security audit whose changed paths are limited to its own active-task and security-audit documents. It is not a runtime writer, but its market findings were reviewed before classification.

# Final disposition

```text
market → ADAPT
```

Task-start Otheryn and fresh upstream are content-identical in the reviewed market core. Legacy market deltas are coupled to selected multichannel ledger/leader-election paths and do not form a complete generic exactly-once design. Open security evidence proves multiwriter/remote-owner hazards for the multichannel deployment, so unconditional `REUSE` is rejected, but the clean target does not import the separately owned cluster architecture.

The bounded target adaptation is server-only: strict persisted-tier parsing, centralized deterministic offer-counter derivation, fail-closed invalid timestamp-window decoding, and focused target tests. The maintained OTClient packet contract remains compatible and unchanged.

Generic crash/restart atomicity and any future multiwriter market contract remain explicit known gaps; OAM-021 does not claim those are solved.

# Exact target proof

```text
Otheryn PR #45 final head: f13d4d2d0626c99dd2318ef088ce155f67b0b5ae
target squash merge: b90e287a40413102c87e8c7fa3d5c01ad401cb6d
autofix.ci #144 / 29704971999: SUCCESS
CI #167 / 29704972077: SUCCESS
Required #151 / 29704972006: SUCCESS
Linux debug CTest: 396/396 PASS
focused Oam021MarketAdaptTest: 3/3 PASS
test-log artifact: 8447725005
artifact digest: sha256:f6f6b67fda044f1d8b88600a87234f4cb6559ae3e3d9270ddd2a98041948debb
```

Target pre-merge audit: exactly five intended paths; comments 0; reviews 0; review threads 0; Otheryn `main` drift none. The target merged by expected-head squash at exact head `f13d4d2d0626c99dd2318ef088ce155f67b0b5ae`.

# Acceptance criteria

- [x] Re-fetch and preserve exact task-start baseline SHAs for Canary, Otheryn, upstream and maintained OTClient.
- [x] Review canonical market registry dependencies, source requirements and boundaries.
- [x] Audit active/open work for ownership and changed-path overlap before target writes.
- [x] Compare target/upstream market behavior with bounded reviewed legacy donor history; reject inventory-only parity claims.
- [x] Review open economy/security evidence for market-specific correctness gaps before classifying `REUSE`.
- [x] Classify `market` as `ADAPT` with explicit rationale and known gaps.
- [x] Use only `dudantas/oam-021-market-adapt`, bounded reviewed target changes and focused target tests; no broad Player/protocol copy.
- [x] Obtain exact-final-head target CI/proof and perform changed-file, comment, review, thread and target-main-drift audits before expected-head squash merge.
- [ ] Reconcile Canary governance in this bounded PR with exact-head gates and clean blocker audit.
- [ ] Archive this active task in a separate lifecycle PR after target and governance merges.
- [ ] Reconcile the durable Oteryn program in a separate final one-file PR.
- [ ] Do not start OAM-022 until lifecycle and durable program reconciliation are merged.

# Current state

The target stage is merged at `b90e287a40413102c87e8c7fa3d5c01ad401cb6d`. Canary governance PR #607 still owns exactly this active task and the OAM-021 report. Its next gate is exact-head ownership plus forced final-gate CI on the final governance head before expected-head squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T24:00:00+02:00
head: 403079fd3cbb382a6b01d2b9881b286829f18b81
branch: task/CAN-20260719-oteryn-market-revalidation
pr: "607"
status: validating
next_action: Mark Canary PR 607 ready, apply ci:final-gate, complete exact-head ownership and full final-gate CI, audit blockers and drift, then expected-head squash merge governance.
context_routes:
  - docs/agents/OTERYN_OAM_021_MARKET_REVALIDATION.md
  - docs/agents/real-tibia/registry/modules/market.yaml
owned_paths:
  - docs/agents/tasks/active/CAN-20260719-oteryn-market-revalidation.md
  - docs/agents/OTERYN_OAM_021_MARKET_REVALIDATION.md
proven:
  - OAM-021 task-start baselines were freshly pinned for Canary Otheryn upstream and maintained OTClient.
  - Canonical market dependencies are complete and the selected target disposition is ADAPT.
  - Otheryn PR 45 merged by expected-head squash as b90e287a40413102c87e8c7fa3d5c01ad401cb6d after CI 167 and Required 151 succeeded.
  - Linux debug CTest passed 396 of 396 and focused Oam021MarketAdaptTest passed 3 of 3.
derived:
  - Legacy multichannel market ledger and leader-election deltas are not a complete generic exactly-once design and are excluded from the clean target adaptation.
unknown:
  - Exact Canary governance squash merge SHA remains unknown until final-gate validation succeeds.
conflicts: []
rejected_hypotheses:
  - Whole-module REUSE based only on target-upstream source identity.
  - Bulk import of generic multichannel EconomicLedgerStore or leader-election architecture.
changed_paths:
  - docs/agents/tasks/active/CAN-20260719-oteryn-market-revalidation.md
  - docs/agents/OTERYN_OAM_021_MARKET_REVALIDATION.md
blockers:
  - Canary PR 607 exact-head final-gate ownership and CI must pass before governance merge.
first_failure:
  marker: governance-agent-task-ownership-2739
  evidence: Initial governance checkpoint validation failed because the newly created active task lacked the mandatory Context checkpoint and current PR linkage; the schema was corrected and Agent Task Ownership 2741 subsequently passed.
validation:
  - command: Fresh live-state dependency ownership and cross-repository preflight
    result: PASS
    evidence: Task-start baselines and non-overlap are recorded in this task and OAM-021 report.
  - command: Otheryn PR 45 exact-head CI proof and pre-merge blocker audit
    result: PASS
    evidence: CI 167 Required 151 and autofix 144 succeeded on f13d4d2d0626c99dd2318ef088ce155f67b0b5ae; 396 of 396 CTest passed; five intended paths; zero review blockers; no target-main drift.
  - command: Otheryn PR 45 expected-head squash merge
    result: PASS
    evidence: Exact head f13d4d2d0626c99dd2318ef088ce155f67b0b5ae merged as b90e287a40413102c87e8c7fa3d5c01ad401cb6d.
```
