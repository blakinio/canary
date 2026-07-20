---
task_id: CAN-20260720-oteryn-prey-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-022
status: completed
agent: "GPT-5.5 Thinking"
branch: docs/oam-022-prey-lifecycle
base_branch: main
created: 2026-07-20
updated: 2026-07-20
completed: 2026-07-20
last_verified_commit: "e3a5cc7321636270db150d289ba2da9ddb99ef0d"
risk: high
related_pr: "612"
depends_on:
  - OAM-004 player-persistence foundation
  - OAM-006 protocol
blocks:
  - OAM-023
modules_touched:
  - prey
---

# Goal

Revalidate canonical OAM-022 `prey`, prove the strongest dependency-valid clean-target disposition, and complete the bounded migration-governance lifecycle without absorbing separately owned Wheel of Destiny work.

# Final disposition

```text
prey → REUSE
```

# Immutable task-start baselines

- Canary: `800142e65c2975e57647bf34128ab468532218f0`
- Otheryn: `b90e287a40413102c87e8c7fa3d5c01ad401cb6d`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

# Accepted reuse boundary

The reviewed classic Prey/Task Hunting core has no stronger independent legacy donor. `src/io/ioprey.cpp`, `src/io/ioprey.hpp`, and the reviewed Prey/Task Hunting save boundary are exact-identical across the pinned clean target, fresh upstream and legacy baselines; reviewed load functions are functionally identical. Maintained OTClient already carries the standard Prey contract and required no write.

Legacy Taskboard differs only through Wheel-owned Bonus Promotion Shop integration that consumes Hunting Task points while persisting/applying Wheel promotion points. That explicit Prey↔Wheel interaction remains under the separately active Wheel parity program and was not copied into OAM-022.

# Exact target proof

```text
Otheryn PR #46 final head: 12d79e4532e5784e9530caf433cdad1c869f0142
target squash merge: 50dfa248251f245f5519495a4fbd430b6814ffe4
autofix.ci #145 / 29723046171: SUCCESS
CI #169 / 29723046359: SUCCESS
Required #152 / 29723046189: SUCCESS
Linux debug CTest: 400/400 PASS
focused Oam022PreyReuseTest: 4/4 PASS
test-log artifact: 8453371882
artifact digest: sha256:23e923635138726a33e7900ff84cd481d2182994cb68020c5d03698e4804886c
```

The target PR changed exactly three proof-only paths and no production runtime/data/persistence/protocol/client/schema/map/asset/deployment path. Comments, reviews and review threads were empty; Otheryn `main` had no task-start drift before expected-head squash merge.

# Canary governance proof

```text
governance PR #612 final head: 52b27ea5efedab9b0112c7e206e3c697e17a0ac3
Agent Task Ownership #2754 / 29723974759: SUCCESS
final-gate CI #3904 / 29723982438: SUCCESS
governance changed paths: exactly 2
comments: 0
reviews: 0
review threads: 0
governance squash merge: e3a5cc7321636270db150d289ba2da9ddb99ef0d
```

Canary `main` had no drift from the immutable OAM-022 task-start baseline before governance merge. The final-gate workflow correctly reused/incrementally validated the docs-only governance state while the full target build/test matrix remained separately proven on Otheryn.

# Reviewed exclusions

OAM-022 does not claim full modern official Hunting Task/Taskboard parity, Wheel Bonus Promotion Shop migration, Wheel allocation ownership, exhaustive Prey formulas/rarity/reroll-price/monster-pool parity, physical-client Prey or Taskboard E2E closure, generic persistence/protocol redesign, or map/OTBM/`items.otb`/asset/schema/deployment changes.

# Lifecycle state

The target and governance stages are merged. This authoritative lifecycle PR owns only the active-task deletion and archive addition. Durable one-file program reconciliation remains pending after this lifecycle merge. OAM-023 must remain NOT STARTED until that reconciliation is merged.
