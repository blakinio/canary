---
task_id: CAN-20260720-oteryn-sanctions-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-024
status: completed
agent: "GPT-5.5 Thinking"
branch: docs/oam-024-sanctions-lifecycle
base_branch: main
created: 2026-07-20
updated: 2026-07-20
completed: 2026-07-20
last_verified_commit: "7662d048a75df37f5bfc4238e12fd3b18c935151"
risk: medium
related_pr: "621"
depends_on:
  - OAM-004 database-connection
blocks:
  - OAM-025
modules_touched:
  - sanctions
---

# Goal

Revalidate canonical OAM-024 `sanctions`, classify the smallest dependency-valid clean-target disposition from current evidence, deliver only the bounded target implementation or proof required by that disposition, and complete the migration-governance lifecycle without absorbing protocol transport, account authentication, generic security analytics or unrelated E2E work.

# Final disposition

```text
sanctions → ADAPT
```

# Immutable task-start baselines

- Canary: `3fe0130a408d201d0ca846f86a37b0ab20479932`
- Otheryn: `bcc3e9f7e3e704f3c012bda8693648d52741630f`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

# Accepted adaptation boundary

Canonical `sanctions` is bounded to `src/creatures/players/management/ban.*` and depends only on completed OAM-004 `database-connection`. Exact legacy/target/upstream blob identity was supporting evidence only and did not establish `REUSE`.

Semantic and history review found no stronger independent legacy donor, but identified a bounded durability defect in expired account-ban archival: the history `INSERT` and active-ban `DELETE` were separate asynchronous database writes without one rollback boundary. The target already had OAM-004 `DBTransaction`, so the smallest valid disposition was `ADAPT`.

The accepted target change moves only expired account-ban history insertion and active-row deletion into one `DBTransaction` under `SELECT ... FOR UPDATE`. Active/permanent ban behavior is preserved and IP-ban behavior remains unchanged.

# Exact target proof

```text
Otheryn PR #48 final head: 58ba19e0affe75f47c4185c41327880f8403503b
target squash merge: 65d364b216843db27e84a19a673eee4e6d766c68
autofix.ci #153 / 29734614481: SUCCESS
CI #179 / 29734614607: SUCCESS
Required #160 / 29734614503: SUCCESS
Linux debug CTest: 406/406 PASS
focused SanctionsRepositoryDBTest: 3/3 PASS
test-log artifact: 8458101363
artifact digest: sha256:97b9aeb5e93bac69461720671ee58bfe5742fd20df2710b139d0aa2298cd30fc
```

The target PR changed exactly four intended paths: one bounded production file, one focused integration test, its CMake registration and the target evidence document. Comments, reviews and review threads were empty; Otheryn `main` had no task-start drift before expected-head squash merge.

# Canary governance proof

```text
governance PR #621 final head: 894fa6be932937a7b124461dffe6ac2d3a414f84
Agent Task Ownership #2805 / 29735949134: SUCCESS
draft exact-head CI #3956 / 29735949282: SUCCESS
ready-state final-gate CI #3957 / 29735989048: SUCCESS
governance changed paths: exactly 2
comments: 0
reviews: 0
review threads: 0
governance squash merge: 7662d048a75df37f5bfc4238e12fd3b18c935151
```

The first two ownership attempts failed only the task checkpoint schema (`first_failure` representation); the task contract was corrected without changing target scope or evidence. Final Ownership and CI passed on the exact final governance head. Canary `main` had no drift from the immutable task-start baseline before governance merge.

# Reviewed exclusions

OAM-024 does not claim exhaustive sanction enforcement at every entry point, generic account-authentication security, protocol compatibility, distributed/multi-database sanctions replication, moderation policy, generic security analytics, AI investigation, PvP skull/frag parity, physical-client sanctions E2E closure, generic persistence redesign, or changes to maintained OTClient, maps, OTBM, `items.otb`, assets, schema or deployment.

OAM-024 preserves the known OAM-004 limitation that player SQL persistence and later KV durability are not atomic; this sanctions adaptation does not touch that cross-store boundary.

# Lifecycle state

The target and governance stages are merged. This authoritative lifecycle PR owns only the active-task deletion and archive addition. Durable one-file program reconciliation remains pending after this lifecycle merge. OAM-025 must remain NOT STARTED until that reconciliation is merged.
