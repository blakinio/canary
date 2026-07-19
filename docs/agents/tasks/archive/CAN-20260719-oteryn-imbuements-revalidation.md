---
task_id: CAN-20260719-oteryn-imbuements-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-019
status: completed
agent: "GPT-5.5 Thinking"
branch: docs/oam-019-imbuements-lifecycle
base_branch: main
created: 2026-07-19
updated: 2026-07-19T15:45:00+02:00
completed: 2026-07-19T15:45:00+02:00
last_verified_commit: "f38832dd160910e76d1576bb2c1221374a6ae8b1"
risk: high
related_pr: "588"
depends_on:
  - OAM-013
blocks:
  - OAM-020
modules_touched:
  - imbuements
---

# Goal

Revalidate canonical OAM-019 `imbuements`, migrate only the strongest coherent dependency-valid implementation into Otheryn, and complete the bounded migration-governance lifecycle.

# Final disposition

```text
imbuements → ADAPT
```

# Immutable task-start baselines

- Canary: `e551f3fd33c9642399bb1e70d1f2f6383464b936`
- Otheryn: `7ba76d2754a060a9a9eec0a23c686aefac725af2`
- upstream: `691614c1a302aee776002ca3851eca399be1a82c`
- OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

# Accepted donor chain

The accepted coherent adaptation is the bounded result of merged Canary PRs #86, #206, #239, #251 and #282: configured-storage filtering correctness, Powerful Forgotten Knowledge storage reconciliation, Vibrancy scroll mappings, confirmed fee/Strike/Punch/Featherweight/Vibrancy data, and direct numeric-ID premium/storage authorization before relevant resource mutation.

No whole-file legacy `player.cpp` import was accepted.

# Exact target proof

```text
Otheryn PR #43 final head: 4e993c4ee160fe03d8575c1b830ef71dde450562
target squash merge: 63547f30fc21e495217b8a92fa44aaad2db188ef
autofix.ci #121 / 29687711140: SUCCESS
Repository Audit #12 / 29687711133: SUCCESS
CI #142 / 29687711219: SUCCESS
Required #128 / 29687711131: SUCCESS
full Linux debug CTest: 367/367 PASS
new focused OAM-019 tests: 8/8 PASS
artifact: 8442743109
digest: sha256:a0ef33bd15be8d004dce89ce5014782990961cb239c50e9f48f19d906694c6e0
```

The target PR changed exactly ten intended Imbuement runtime/data/test paths and no temporary materializer paths. Comments, reviews and review threads were empty. Otheryn `main` had no drift before expected-head merge.

The first target macOS smoke wrapper attempt was transient: its artifact proved a clean online startup/shutdown with empty stderr, and one same-head rerun passed without code changes.

# Canary governance proof

```text
governance PR #588 final head: 42d46421df0f0c5191eaf857f19aa4fa3fe42df9
Agent Task Ownership #2607 / 29688560927: SUCCESS
Imbuement Validation #326 / 29688560945: SUCCESS
full final-gate CI #3750 / 29688564115: SUCCESS after one same-head Docker Quickstart failed-job rerun
governance changed paths: exactly 2
comments: 0
reviews: 0
review threads: 0
Canary main before merge: 0db6289cc55069ddb0194a58758bcc97c242bf8b
governance squash merge: f38832dd160910e76d1576bb2c1221374a6ae8b1
```

The first final-gate attempt failed only in the Docker Quickstart/Required tail after every platform build/test job had passed. One permitted same-head failed-jobs rerun passed Docker Quickstart and the overall final-gate workflow completed successfully without a governance head change.

# Reviewed exclusions

OAM-019 does not claim exhaustive current Real Tibia Imbuement parity, exhaustive equipment eligibility, full live quest-unlock visibility, exact protocol/UI presentation for every client, physical-client E2E closure, exhaustive combat-math parity, production crash/restart persistence completeness, generic resource transaction atomicity, or changes to generic items, Exaltation Forge, maps, assets, `items.otb`, schema or client code.

# Lifecycle state

The target and governance stages are merged. This authoritative lifecycle PR owns only the active-task deletion and archive addition.

Durable one-file program reconciliation remains pending after this lifecycle merge. Any automation-created duplicate archive PR for governance #588 must remain unmerged until this authoritative lifecycle merge is established, then be closed unmerged.

OAM-020 is NOT STARTED.
