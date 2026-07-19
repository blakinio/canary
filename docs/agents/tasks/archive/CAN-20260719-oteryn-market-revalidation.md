---
task_id: CAN-20260719-oteryn-market-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-021
status: completed
agent: "GPT-5.5 Thinking"
branch: docs/oam-021-market-lifecycle
base_branch: main
created: 2026-07-19
updated: 2026-07-19
completed: 2026-07-19
last_verified_commit: "76273c0cb7c2e297c8896a8e7fb6809649fa2870"
risk: high
related_pr: "607"
depends_on:
  - OAM-004 player-persistence foundation
  - OAM-006 protocol
blocks:
  - OAM-022
modules_touched:
  - market
---

# Goal

Revalidate canonical OAM-021 `market`, adapt only the bounded server-side market correctness boundary supported by fresh target/upstream/legacy/client evidence, and complete the migration-governance lifecycle without importing unrelated multichannel architecture.

# Final disposition

```text
market → ADAPT
```

# Immutable task-start baselines

- Canary: `183d7224cb5de57585294d72631f37783b93dc89`
- Otheryn: `d59207d05ab6dd9450b05d0a6b4d9122fda60489`
- fresh upstream comparison: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`
- previous durable OAM-020 reconciliation: `bde118d04d17cd3b11ba555a735448e92dffe2fe`

# Source and evidence decision

Task-start Otheryn and fresh upstream were content-identical in the reviewed market core. Legacy market deltas were coupled to selected multichannel `EconomicLedgerStore` and leader-election paths and did not form a complete generic exactly-once design. Open security evidence proved cross-process partial-fill and remote-owner hazards for the multichannel deployment; those findings blocked unconditional whole-module `REUSE` but did not justify importing the separately owned cluster runtime into the clean target.

The accepted target adaptation remained server-only: strict persisted-tier parsing, centralized deterministic 16-bit offer-counter derivation, and fail-closed invalid timestamp-window decoding. The maintained OTClient request/response packet shapes remained compatible and unchanged, so no client write was made.

Generic crash/restart atomicity and future multiwriter market ownership remain explicit known gaps rather than hidden completion claims.

# Exact target proof

```text
Otheryn PR #45 final head: f13d4d2d0626c99dd2318ef088ce155f67b0b5ae
target squash merge: b90e287a40413102c87e8c7fa3d5c01ad401cb6d
autofix.ci #144 / 29704971999: SUCCESS
CI #167 / 29704972077: SUCCESS
Required #151 / 29704972006: SUCCESS
full Linux debug CTest: 396/396 PASS
focused Oam021MarketAdaptTest: 3/3 PASS
test-log artifact: 8447725005
digest: sha256:f6f6b67fda044f1d8b88600a87234f4cb6559ae3e3d9270ddd2a98041948debb
```

The target PR changed exactly five intended paths. Comments, reviews and review threads were empty. Otheryn `main` had no drift from the task-start target base before expected-head squash merge.

# Canary governance proof

```text
governance PR #607 final head: d2290f6072a8fd9e90f43a164a8426076ff6c718
Agent Task Ownership #2743 / 29705475496: SUCCESS
final-gate CI #3892 / 29705479591: SUCCESS
governance changed paths: exactly 2
comments: 0
reviews: 0
review threads: 0
governance squash merge: 76273c0cb7c2e297c8896a8e7fb6809649fa2870
```

The `ci:final-gate` workflow ran on the exact governance head. Fast Checks and Lua Tests passed. Its build-scope/immediate-parent policy deliberately skipped Linux/macOS/Windows/Docker rebuild jobs for this two-document governance diff, and the aggregate Required job passed. Canary `main` had no drift from the task-start Canary baseline before the expected-head governance merge.

# Reviewed exclusions

OAM-021 does not claim crash-safe exactly-once market create/cancel/accept/expiry, cross-process/multiwriter market safety, remote-player mutation routing, generic multichannel Redis/session ownership or leader election, generic `economic_ledger` recovery, bank/account/guild economy redesign, exhaustive current Real Tibia market parity, NPC shops, store products, direct player trade, maps, OTBM, `items.otb`, world assets, schema, deployment, maintained-OTClient changes or physical-client Market E2E closure.

# Lifecycle state

The target and governance stages are merged. This authoritative lifecycle PR owns only the active-task deletion and archive addition.

Durable one-file program reconciliation remains pending after this lifecycle merge. OAM-022 must remain not started until that reconciliation is merged.
