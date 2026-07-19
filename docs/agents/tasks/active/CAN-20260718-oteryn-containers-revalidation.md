---
task_id: CAN-20260718-oteryn-containers-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-017
status: review
agent: "GPT-5.5 Thinking"
branch: docs/oam-017-containers-revalidation
base_branch: main
created: 2026-07-18
updated: 2026-07-19T10:15:00+02:00
last_verified_commit: "952e7550182df739824bddea687ef89bd8997674"
risk: high
related_issue: "blakinio/Otheryn#40"
related_pr: "555"
depends_on:
  - OAM-007
blocks:
  - OAM-018
modules_touched:
  - containers
owned_paths:
  exclusive:
    - docs/agents/OTERYN_OAM_017_CONTAINERS_REVALIDATION.md
    - docs/agents/tasks/active/CAN-20260718-oteryn-containers-revalidation.md
---

# Goal

Revalidate canonical OAM-017 `containers` against immutable task-start baselines and accept only the strongest dependency-valid target implementation.

# Final disposition

```text
containers → REUSE
```

The target proof is complete. Canary governance, lifecycle archive and durable program reconciliation remain before OAM-017 is fully closed.

# Immutable task-start baselines

```text
Canary:   6c2ed7fd5d7e0f51bf7bfc75ebcc30b840315e41
Otheryn:  46cc7458d644da356371aabf3ff18c0e51d228a8
upstream: 691614c1a302aee776002ca3851eca399be1a82c
OTClient: 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

# Evidence decision

Canonical `containers` depends only on completed OAM-007 `item-instances`. OAM-002 whole-tree provenance plus later target and upstream history through task start contains no canonical production mutation under `src/items/containers/**` or `src/items/cylinder.*`.

Representative task-start blobs shared by target, pinned upstream and legacy are:

```text
src/items/containers/container.cpp  2688a2d59bebac33b801cfdd11d0aa5c26a07016
src/items/cylinder.cpp              82c6cf3fd6dff9d579d35cfbaf1f4b52ec4c46b8
```

Reviewed legacy PR #60 changes house-transfer orchestration only. Reviewed legacy PR #108 changes Gameplay Analytics scripts only. Neither is a canonical container/cylinder runtime donor.

# Initial proof-harness failure and resolution

Initial exact target head `7dcdcff1dde59a702b00d77f5049bd99a126a6eb` failed only the two new `ContainerReuseTest` cases in CI #125 / run `29653898425`:

```text
357 total
355 passed
2 failed

ContainerReuseTest.PreservesDirectCapacityAndItemLifecycle — SEGFAULT
ContainerReuseTest.PreservesBoundedNestedTraversal — SEGFAULT
```

The red proof was isolated to the proof harness, not production runtime. The unit-test process starts without loaded item definitions. `Items::Items()` therefore leaves its item-type vector empty, while synthetic `Item(0)` / `Container(0, ...)` construction reaches the item-type lookup fallback before the container behavior under test. The tests were corrected with a local `ScopedItemTypeRegistry` fixture that supplies the minimum synthetic item-type entry only when the registry starts empty and restores the original size afterward.

No production container/cylinder or other runtime/data path was changed.

# Accepted exact target proof

```text
Otheryn issue #40: CLOSED / completed
Otheryn PR #41: MERGED
final target head: ee111cb6ef6299a0de7fb19de76934b6369b7cf0
target squash merge: 952e7550182df739824bddea687ef89bd8997674
autofix.ci #108 / 29679028025: SUCCESS
CI #127 / 29679028059: SUCCESS
Required #115 / 29679028000: SUCCESS
full CTest: 357/357 PASS
focused ContainerReuseTest: 2/2 PASS
artifact: 8440064893
artifact name: linux-debug-test-logs
digest: sha256:28d82a5a1d36d89a8892280e73bb671a846743962786922093a907e8b80b79c1
```

Final PR #41 scope is exactly `tests/unit/items/containers/container_test.cpp`. Target comments, reviews and review threads were empty. Otheryn `main` remained at task-start head `46cc7458d644da356371aabf3ff18c0e51d228a8` immediately before merge, so target-main drift was none. PR #41 merged with expected-head protection on `ee111cb6ef6299a0de7fb19de76934b6369b7cf0`.

# Exclusions

OAM-017 does not claim transactional move atomicity, absence of duplication or loss across generic move orchestration, exhaustive cycle safety, full serialization or persistence completeness, restart/crash recovery, depot/inbox/mailbox/reward parity, protocol/client UI parity, market/boss-reward/item-decay parity, or Real Tibia container semantics beyond the bounded proof.

OAM-004 SQL/KV non-atomicity and completed OAM-007 item-instance ownership remain authoritative.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T10:15:00+02:00
head: 33d8fa2809f1ff6214f81d75ac6ea4f7a1fa5b19
branch: docs/oam-017-containers-revalidation
pr: 555
status: validating
next_action: Pass final exact-head Agent Task Ownership and CI for Canary PR #555, then perform clean review and Canary-main drift audit before expected-head merge.
context_routes:
  - docs/agents/OTERYN_OAM_017_CONTAINERS_REVALIDATION.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260718-oteryn-containers-revalidation.md
owned_paths:
  - docs/agents/OTERYN_OAM_017_CONTAINERS_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260718-oteryn-containers-revalidation.md
proven:
  - Immutable task-start baselines are pinned above.
  - Canonical containers depends only on completed OAM-007 item-instances.
  - Open-PR ownership preflight found no overlap with the canonical container/cylinder runtime boundary.
  - Target and upstream production history through task start contain no canonical container/cylinder mutation.
  - Reviewed legacy PR #60 and PR #108 are not canonical container-runtime donors.
  - The initial two-test SEGFAULT was isolated to an empty synthetic item-type registry in the proof harness.
  - The corrected target proof changed exactly one test file and no production runtime/data path.
  - Exact target head ee111cb6ef6299a0de7fb19de76934b6369b7cf0 passed autofix, CI, Required, 357 of 357 full tests and 2 of 2 focused ContainerReuseTest cases.
  - Target comments, reviews and review threads were empty and target-main drift was none before expected-head merge.
  - Otheryn PR #41 merged exact head ee111cb6ef6299a0de7fb19de76934b6369b7cf0 as 952e7550182df739824bddea687ef89bd8997674.
derived:
  - Canonical OAM-017 disposition is REUSE.
  - The initial red target proof was a proof-harness defect and does not justify production container/cylinder runtime changes.
unknown:
  - Canary governance merge SHA is unavailable until PR #555 merges.
  - Authoritative lifecycle and durable program reconciliation merge SHAs are unavailable until those stages merge.
conflicts: []
rejected_hypotheses:
  - Treating the initial focused-test SEGFAULT as evidence of a production container/cylinder defect.
  - Treating house-transfer orchestration PR #60 as a canonical container-runtime donor.
  - Treating Gameplay Analytics PR #108 as a canonical container-runtime donor.
changed_paths:
  - docs/agents/OTERYN_OAM_017_CONTAINERS_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260718-oteryn-containers-revalidation.md
blockers:
  - Final exact-head Canary governance Agent Task Ownership and CI must pass.
  - Governance comments, reviews and review threads must be clean and Canary-main drift must be audited before expected-head merge.
  - A separate authoritative lifecycle archive must merge.
  - Any self-owned automatic docs(agents) archive duplicate for governance PR #555 must be closed after authoritative lifecycle is established.
  - A separate one-file durable program reconciliation must merge before OAM-018.
first_failure:
  marker: Otheryn CI #125 / Linux debug job 88104873970 / Run Tests
  evidence: 357 total, 355 passed; the two new focused tests SEGFAULT before behavior assertions because the synthetic unit fixture constructed item id 0 against an empty item-type registry.
validation:
  - command: OAM-017 fresh preflight
    result: PASS
    evidence: Dependency and open-PR ownership checks passed.
  - command: Initial Otheryn PR #41 exact-head CI #125 / 29653898425
    result: FAIL
    evidence: Linux debug passed build/runtime/database setup and failed only the two new focused tests.
  - command: Corrected Otheryn PR #41 exact-head autofix.ci #108 / 29679028025
    result: PASS
    evidence: Exact final target head passed formatting/autofix without further mutation.
  - command: Corrected Otheryn PR #41 exact-head CI #127 / 29679028059
    result: PASS
    evidence: Exact final target head passed all applicable CI, including Linux debug full CTest 357 of 357.
  - command: Corrected Otheryn PR #41 exact-head Required #115 / 29679028000
    result: PASS
    evidence: Required acceptance gate passed on exact final target head.
  - command: ContainerReuseTest corrected exact-target proof
    result: PASS
    evidence: 2 of 2 focused tests passed inside the 357 of 357 full CTest run; artifact 8440064893 digest sha256:28d82a5a1d36d89a8892280e73bb671a846743962786922093a907e8b80b79c1.
```

# Remaining sequence

1. Pass final exact-head Canary governance Agent Task Ownership and CI on PR #555.
2. Audit governance comments/reviews/threads and Canary-main drift, then expected-head squash merge #555.
3. Merge a separate authoritative lifecycle-only archive.
4. After authoritative lifecycle is established, explicitly close any self-owned automatic `docs(agents): archive merged PR #555 task` duplicate.
5. Merge a separate one-file durable program reconciliation.
6. Do not start OAM-018 before every OAM-017 stage above is merged.
