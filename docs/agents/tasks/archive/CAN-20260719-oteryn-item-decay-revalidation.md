---
task_id: CAN-20260719-oteryn-item-decay-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-018
status: completed
agent: "GPT-5.5 Thinking"
branch: docs/oam-018-item-decay-lifecycle
base_branch: main
created: 2026-07-19
updated: 2026-07-19T13:15:00+02:00
completed: 2026-07-19T13:15:00+02:00
last_verified_commit: "df97440551ca141b340ff424b1d644430bbb3c28"
risk: high
related_pr: "578"
depends_on:
  - OAM-003
  - OAM-007
blocks:
  - OAM-019
modules_touched:
  - item-decay
---

# Goal

Revalidate canonical OAM-018 `item-decay` against immutable fresh baselines and complete the bounded migration-governance lifecycle.

# Final disposition

```text
item-decay → REUSE
```

# Immutable task-start baselines

- Canary: `3c4d2789ffa3d0c1e9453d20a8c5faeba35eb366`
- Otheryn: `952e7550182df739824bddea687ef89bd8997674`
- upstream: `691614c1a302aee776002ca3851eca399be1a82c`
- OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

# Exact target proof

```text
Otheryn PR #42 final head: 13e245f3c49477fa75c20171f0c845dec91d0824
target squash merge: 7ba76d2754a060a9a9eec0a23c686aefac725af2
autofix.ci #110 / 29682419114: SUCCESS
CI #130 / 29682419178: SUCCESS after one same-head failed-job rerun
Required #117 / 29682419125: SUCCESS
full CTest: 359/359 PASS
focused ItemDecayReuseTest: 2/2 PASS
artifact: 8441163603
digest: sha256:de3f541b41aa9d4f39a4d8d629de52a51e09b8eaff461c8706bb7a296cfd9631
```

The proof-only target diff changed exactly `tests/unit/items/CMakeLists.txt` and `tests/unit/items/decay/decay_test.cpp`. No production `src/items/decay/**`, scheduler, item runtime, persistence, protocol, data, map or client path changed.

The first macOS runtime-smoke wrapper failure was transient: its artifact showed a clean online startup and shutdown, and one failed-job rerun passed on the same exact head without code changes.

# Provenance decision

Target and pinned upstream share `src/items/decay/decay.cpp` blob `a337b872755217d87ac2261de6c3c1a593d805a6`. Legacy Canary differs only by omitting `DispatcherLane::Maintenance` from the three decay scheduling calls. OAM-003 already retained the target/upstream lane/WDRR scheduler and rejected the older legacy scheduler model, so the legacy delta is not a stronger donor.

# Canary governance proof

```text
governance PR #578 final head: 80681dd0bbaa6bed0d212bc90b7a0c728e73b836
Agent Task Ownership #2531 / 29683370000: SUCCESS
CI final gate #3675 / 29683558587: SUCCESS
comments: 0
reviews: 0
review threads: 0
latest Canary main before merge: f4dc24ddb80f05bb7d6d0a4e58ac6fbdd0c1363f
post-checkpoint main drift audited with no overlap in the two OAM-018 governance paths
governance squash merge: df97440551ca141b340ff424b1d644430bbb3c28
```

# Reviewed exclusions

- no scheduler fairness, ordering or starvation-freedom claim;
- no exact wall-clock decay-timing claim;
- no restart/crash decay-recovery claim;
- no persistence-completeness claim;
- no item movement/container transaction atomicity or duplication/loss claim;
- no static decay-metadata or exhaustive transform-correctness claim;
- no protocol/client UI or full Real Tibia decay-semantics claim.

# Lifecycle state

Target proof and Canary governance are complete. This authoritative lifecycle archive moves OAM-018 out of `tasks/active`. Durable one-file program reconciliation remains pending and must merge before a fresh OAM-019 preflight may begin. OAM-019 is NOT STARTED.
