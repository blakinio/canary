---
task_id: CAN-20260720-oteryn-oam026-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-026
status: completed
agent: "GPT-5.5 Thinking"
branch: docs/oam-026-guilds-lifecycle
base_branch: main
created: 2026-07-20
updated: 2026-07-20
completed: 2026-07-20
last_verified_commit: "5a2bc2be3b91abdd46c9edf2f825336472515299"
risk: medium
related_pr: "635"
depends_on:
  - OAM-004 database-connection and world-persistence foundation
  - OAM-005 character-lifecycle
blocks:
  - OAM-027
modules_touched:
  - guilds
---

# Goal

Revalidate canonical OAM-026 `guilds`, preserve completed target persistence contracts, deliver the smallest evidence-backed target proof, close Canary governance, then archive lifecycle before separate durable program reconciliation.

# Final disposition

```text
guilds → ADAPT
```

# Immutable task-start baselines

- Canary: `052d96014c805aacaa120ce888b7bed038817a72`
- Otheryn: `1cf38d354b493b4cd9ec8e841ec8f2a6ff322029`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`

# Accepted adaptation boundary

The canonical guild core remains upstream-compatible. Whole-module `REUSE` is rejected because Otheryn intentionally preserves completed OAM-004C persistence behavior: `IOGuild::saveGuild()` returns database status and `SaveManager` propagates guild-save failure into aggregate server-save status.

OAM-026 required no new production guild mutation. The accepted target delivery is proof-only and retains guild identity, ranks, membership projection, war-list loading and process-local online-member cache behavior while protecting the existing target persistence contract.

The shared player loader was not copied wholesale. No maintained-client, protocol/opcode, map/OTBM, schema or deployment change was required.

# Exact target proof

```text
Otheryn PR #53 final head: 4709f0c49962dee14e98acb384baab75b21c97a8
autofix.ci run 29775483679: SUCCESS
CI run 29775483958: SUCCESS
Required run 29775483628: SUCCESS
Linux debug Run Tests: SUCCESS
target squash merge: 418a9f0bfc72cc58b9806a49e966d9c3ea3c1a6d
```

PR #53 changed exactly four proof/test paths and no production guild path. Target comments, reviews and review threads were empty; target `main` had no task-start drift before expected-head squash merge.

# Canary governance proof

```text
governance PR #635 final head: a81d637bd63b58a0e4df79e24a1cac64716bd7ae
Agent Task Ownership run 29777372413 / #2891: SUCCESS
final-gate CI run 29777392434 / #4045: SUCCESS
governance changed paths: exactly 2
comments: 0
reviews: 0
review threads: 0
governance squash merge: 5a2bc2be3b91abdd46c9edf2f825336472515299
```

The governance branch was reconstructed onto current non-overlapping Canary `main` `191cad8779ec84aaa09c8f62e9b6ff76e958b8fa` after independent OTBM/E2E drift. Exact-final-head ownership and CI passed, and Canary `main` remained unchanged through the merge gate.

# Security and reviewed exclusions

Legacy `OTS-ECO-GUILD-001` remains evidence of a future multiwriter guild-bank stale-balance risk. OAM-026 does not import the legacy multichannel ownership model and does not claim generic distributed guild ownership or atomic multiwriter guild-bank debit safety.

OAM-026 does not claim Real Tibia guild parity, website guild-management parity, guild-chat delivery parity, protocol/client UI parity, generic transaction atomicity, generic crash/restart durability, physical-client guild E2E closure or map/asset/schema/deployment changes.

# Lifecycle state

Target and governance stages are merged. This authoritative lifecycle PR owns only active-task deletion and archive addition. Separate one-file durable program reconciliation remains pending after this lifecycle merge. OAM-027 must remain NOT STARTED until that reconciliation merges.
