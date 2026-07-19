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
related_pr: ""
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
- Open Canary PR #526 is an evidence-only shared-state/economy security audit whose changed paths are limited to its own active-task and security-audit documents. It is not a runtime writer, but its market findings must be reviewed as potentially blocking evidence before any `REUSE` decision.
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

# Acceptance criteria

- [ ] Re-fetch and preserve exact task-start baseline SHAs for Canary, Otheryn, upstream and maintained OTClient.
- [ ] Review canonical market registry dependencies, source requirements and boundaries.
- [ ] Audit active/open work for ownership and changed-path overlap before target writes.
- [ ] Compare target/upstream market behavior with bounded reviewed legacy donor history; reject inventory-only parity claims.
- [ ] Review open economy/security evidence for market-specific correctness gaps before classifying `REUSE`.
- [ ] Classify `market` as `REUSE`, `ADAPT`, `REWRITE`, `DO_NOT_MIGRATE` or `EXPERIMENTAL_ONLY` with explicit rationale and known gaps.
- [ ] If target changes are required, use only a `dudantas/` Otheryn branch, bounded reviewed changes and target-side focused tests; do not bulk-copy legacy Player/protocol code.
- [ ] Obtain exact-final-head target CI/proof and perform changed-file, comment, review, thread and target-main-drift audits before expected-head squash merge.
- [ ] Reconcile Canary governance in a separate bounded PR with exact-head gates and clean blocker audit.
- [ ] Archive this active task in a separate lifecycle PR after target and governance merges.
- [ ] Reconcile the durable Oteryn program in a separate final one-file PR.
- [ ] Do not start OAM-022 until lifecycle and durable program reconciliation are merged.

# Current state

OAM-021 has started at the immutable baselines above. Final disposition is intentionally unresolved pending function-level source, persistence, transaction, protocol and maintained-client evidence review.
