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
last_verified_commit: "183d7224cb5de57585294d72631f37783b93dc89"
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

- Otheryn has no open pull request at task start.
- Maintained OTClient has no open pull request at task start.
- No OAM-021 branch or pull request existed in Canary or Otheryn at task start.
- Canary advanced exactly one commit after the OAM-020 durable reconciliation, to `183d7224cb5de57585294d72631f37783b93dc89`; that commit changes only unrelated E2E skill-persistence documentation/tests/tooling and does not overlap this task's exclusive governance paths.
- Canonical `market` depends on completed `player-persistence` and `protocol`; `exaltation-forge` is an interaction and is completed.
- Open Canary PR #526 is an evidence-only shared-state/economy security audit whose changed paths are limited to its own active-task and security-audit documents. It is not a runtime writer, but its market findings were reviewed as potentially blocking evidence before classification.
- Open Canary PRs #514, #559 and #600 remain unrelated to this OAM package unless later changed-file evidence proves overlap.

# Scope

Included canonical responsibilities:

- market offers and history;
- limits and fees;
- item eligibility;
- server-client market packet contracts;
- persistence and transaction behavior directly owned by the market module;
- maintained-client compatibility evidence required by the canonical registry.

Excluded unless independently proven necessary for the bounded market contract:

- NPC shops;
- store products;
- direct player trade;
- generic multichannel architecture;
- generic economic-ledger or leader-election redesign;
- unrelated bank/guild/store economy;
- maps, OTBM, `items.otb`, world assets or deployment;
- maintained-OTClient writes without separate explicit authorization.

# Revalidation result

The accepted disposition is:

```text
market → ADAPT
```

Task-start Otheryn and fresh upstream are content-identical in the reviewed market core. Legacy market deltas are coupled to selected multichannel ledger/leader-election paths and do not form a complete generic exactly-once design. Open security evidence proves multiwriter/remote-owner hazards for the multichannel deployment, so unconditional `REUSE` is rejected, but the clean target must not silently import the separately owned cluster architecture.

The bounded target adaptation is server-only: strict persisted-tier parsing, centralized deterministic offer-counter derivation, fail-closed invalid timestamp-window decoding, and focused target tests. The maintained OTClient packet contract remains compatible and unchanged.

Generic crash/restart atomicity and any future multiwriter market contract remain explicit known gaps; OAM-021 does not claim those are solved.

# Acceptance criteria

- [x] Re-fetch and preserve exact task-start baseline SHAs for Canary, Otheryn, upstream and maintained OTClient.
- [x] Review canonical market registry dependencies, source requirements and boundaries.
- [x] Audit active/open work for ownership and changed-path overlap before target writes.
- [x] Compare target/upstream market behavior with bounded reviewed legacy donor history; reject inventory-only parity claims.
- [x] Review open economy/security evidence for market-specific correctness gaps before classifying `REUSE`.
- [x] Classify `market` as `ADAPT` with explicit rationale and known gaps.
- [x] Use only `dudantas/oam-021-market-adapt`, bounded reviewed target changes and focused target tests; no broad Player/protocol copy.
- [ ] Obtain exact-final-head target CI/proof and perform changed-file, comment, review, thread and target-main-drift audits before expected-head squash merge.
- [ ] Reconcile Canary governance in this bounded PR with exact-head gates and clean blocker audit.
- [ ] Archive this active task in a separate lifecycle PR after target and governance merges.
- [ ] Reconcile the durable Oteryn program in a separate final one-file PR.
- [ ] Do not start OAM-022 until lifecycle and durable program reconciliation are merged.

# Current state

OAM-021 target PR #45 is ready on exact head `f13d4d2d0626c99dd2318ef088ce155f67b0b5ae`. Its diff is exactly five intended paths; comments, reviews and review threads are empty; target `main` had no drift at the checked pre-merge checkpoint. Ready-state autofix succeeded without changing the head. Full ready-state CI and Required remain the next target gate before any merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T23:55:00+02:00
head: 4280193015629fc1d3ae29b60aaa8fe8969808fd
branch: task/CAN-20260719-oteryn-market-revalidation
pr: "607"
status: validating
next_action: Complete exact-head Otheryn PR #45 CI, blocker and drift audit, then expected-head squash merge before finalizing Canary governance evidence.
context_routes:
  - docs/agents/OTERYN_OAM_021_MARKET_REVALIDATION.md
  - docs/agents/real-tibia/registry/modules/market.yaml
owned_paths:
  - docs/agents/tasks/active/CAN-20260719-oteryn-market-revalidation.md
  - docs/agents/OTERYN_OAM_021_MARKET_REVALIDATION.md
proven:
  - OAM-021 task-start baselines were freshly pinned for Canary Otheryn upstream and maintained OTClient.
  - Canonical market dependencies are complete and the selected target disposition is ADAPT.
  - Otheryn PR 45 contains exactly five intended target paths at reviewed head f13d4d2d0626c99dd2318ef088ce155f67b0b5ae.
derived:
  - Legacy multichannel market ledger and leader-election deltas are not a complete generic exactly-once design and are excluded from the clean target adaptation.
unknown:
  - Exact final target squash merge SHA remains unknown until exact-head Required and full CI pass.
conflicts: []
rejected_hypotheses:
  - Whole-module REUSE based only on target-upstream source identity.
  - Bulk import of generic multichannel EconomicLedgerStore or leader-election architecture.
changed_paths:
  - docs/agents/tasks/active/CAN-20260719-oteryn-market-revalidation.md
  - docs/agents/OTERYN_OAM_021_MARKET_REVALIDATION.md
blockers:
  - Otheryn PR 45 exact-head full CI and Required must pass before target merge.
first_failure:
  marker: governance-agent-task-ownership-2739
  evidence: Initial governance checkpoint validation failed because the newly created active task lacked the mandatory Context checkpoint and current PR linkage; this update supplies the required schema.
validation:
  - command: Fresh live-state dependency ownership and cross-repository preflight
    result: PASS
    evidence: Task-start baselines and non-overlap are recorded in this task and OAM-021 report.
  - command: Otheryn PR 45 changed-file and review-blocker audit at head f13d4d2d0626c99dd2318ef088ce155f67b0b5ae
    result: PASS
    evidence: Exactly five intended paths; zero comments reviews and review threads; target main identical to task-start base at checked checkpoint.
  - command: Otheryn PR 45 ready-state full CI and Required
    result: NOT_RUN
    evidence: Runs 29704972077 and 29704972006 are in progress at this checkpoint.
```
