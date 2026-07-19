---
task_id: CAN-20260718-oteryn-containers-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-017
status: implementing
agent: "GPT-5.5 Thinking"
branch: docs/oam-017-containers-revalidation
base_branch: main
created: 2026-07-18
updated: 2026-07-19T09:41:00+02:00
last_verified_commit: "7dcdcff1dde59a702b00d77f5049bd99a126a6eb"
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

# Provisional disposition

```text
containers → REUSE
```

Not final. The current exact-target proof fails only in the two new focused tests.

# Immutable task-start baselines

```text
Canary:   6c2ed7fd5d7e0f51bf7bfc75ebcc30b840315e41
Otheryn:  46cc7458d644da356371aabf3ff18c0e51d228a8
upstream: 691614c1a302aee776002ca3851eca399be1a82c
OTClient: 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

# Handover state

```text
Otheryn issue #40: OPEN
Otheryn PR #41: OPEN
PR #41 head: 7dcdcff1dde59a702b00d77f5049bd99a126a6eb
PR #41 scope: tests/unit/items/containers/container_test.cpp only
autofix #106 / 29653898351: SUCCESS
CI #125 / 29653898425: FAILURE
Required #113 / 29653898361: FAILURE

Canary governance PR #555: OPEN / DRAFT
PR #555 head before handover: 3a41c15a36d6ec9eaefb25b105cba62c6c74dc0f
Ownership #2350 / 29653964593: SUCCESS
CI #3486 / 29653964672: SUCCESS
```

The Canary governance checks above are preliminary only. Final governance gates must rerun after an accepted target proof is merged and final evidence is written.

# First failure

Linux debug job `88104873970` passed CMake, Canary runtime smoke and database schema import, then failed at `Run Tests`.

```text
357 total
355 passed
2 failed

156 - ContainerReuseTest.PreservesDirectCapacityAndItemLifecycle (SEGFAULT)
157 - ContainerReuseTest.PreservesBoundedNestedTraversal (SEGFAULT)
```

Both new tests terminate immediately after their GoogleTest `[ RUN ]` line. Existing tests were not reported as failures.

Test artifact:

```text
artifact: 8432436019
name: linux-debug-test-logs
digest: sha256:8a8e5dc2d3156f783880ad37672d4a6ad9e9f66739571994495fda73c984d6fc
```

Other completed CI #125 jobs were green: macOS, Windows Solution, Windows CMake, Linux release, Fast Checks and Lua Tests.

# Current diagnosis

Treat this as a proof-harness failure unless further evidence isolates a production defect. The strongest current hypothesis is that the new tests construct synthetic `Container`/`Item` fixtures with type/id `0` in a unit-test process where the required item-definition state is not valid for that constructor path. This hypothesis is not yet proven by a stack trace.

Do not change production container/cylinder code merely to make the focused tests pass. First use a valid existing test fixture/item-construction pattern or initialize the minimum required test state.

## Context checkpoint

```yaml
checkpoint_version: 2
updated_at: 2026-07-19T09:41:00+02:00
head: 3a41c15a36d6ec9eaefb25b105cba62c6c74dc0f
branch: docs/oam-017-containers-revalidation
pr: 555
status: handover_target_proof_failed
next_action: Fix only the OAM-017 proof harness on Otheryn PR #41, push a new exact target head, and require fresh autofix, CI and Required. Do not reuse failed run 29653898425 as acceptance evidence.
context_routes:
  - docs/agents/OTERYN_OAM_017_CONTAINERS_REVALIDATION.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260718-oteryn-containers-revalidation.md
owned_paths:
  - docs/agents/OTERYN_OAM_017_CONTAINERS_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260718-oteryn-containers-revalidation.md
proven:
  - Fresh task-start baselines are pinned above.
  - Canonical containers depends only on completed OAM-007 item-instances.
  - Open-PR ownership audit found no overlap with the canonical container/cylinder runtime boundary.
  - Target and upstream history through task start contain no canonical container production mutation.
  - Task-start target, upstream and legacy share container.cpp blob 2688a2d59bebac33b801cfdd11d0aa5c26a07016 and cylinder.cpp blob 82c6cf3fd6dff9d579d35cfbaf1f4b52ec4c46b8.
  - Reviewed legacy PR #60 and PR #108 are not canonical container-runtime donors.
  - PR #41 head 7dcdcff1dde59a702b00d77f5049bd99a126a6eb changes one test file and no production code.
  - CI #125 ran 357 tests; 355 passed and only the two new ContainerReuseTest cases segfaulted.
derived:
  - Current target/upstream container core remains the strongest dependency-valid candidate.
  - The current red gate is best treated as proof-harness failure until stronger evidence says otherwise.
unknown:
  - Exact root cause of the two focused-test SEGFAULTs.
  - Final OAM-017 disposition until corrected exact-target proof passes and merges.
conflicts: []
blockers:
  - Correct PR #41 proof harness and push a new exact head.
  - Fresh target autofix, CI and Required must all pass.
  - Full CTest and focused tests must pass before target merge.
  - Audit target comments/reviews/threads and main drift before expected-head merge.
  - Finalize PR #555 evidence and rerun final exact-head Canary Ownership/CI.
  - Merge separate lifecycle archive and one-file durable program reconciliation before OAM-018.
  - Close any self-owned automatic docs(agents) archive duplicate after authoritative lifecycle is established.
first_failure:
  marker: Otheryn CI #125 / Linux debug job 88104873970 / Run Tests
  evidence: 357 total, 355 passed; two new ContainerReuseTest cases SEGFAULT.
validation:
  - command: OAM-017 fresh preflight
    result: PASS
    evidence: Dependency and open-PR ownership checks passed.
  - command: Otheryn PR #41 autofix #106 / 29653898351
    result: PASS
    evidence: Exact target head required no autofix mutation.
  - command: Otheryn PR #41 CI #125 / 29653898425
    result: FAIL
    evidence: Linux debug failed only on the two new focused tests.
  - command: Otheryn PR #41 Required #113 / 29653898361
    result: FAIL
    evidence: Target acceptance is not satisfied.
  - command: Canary draft PR #555 Ownership #2350 and CI #3486
    result: PASS_PRELIMINARY
    evidence: Draft task/governance structure is valid; final gates must rerun later.
```

# Next-agent sequence

1. Read root `AGENTS.md`, repository/context routing docs, this task and the OAM-017 evidence report.
2. Re-fetch live PR #41 and #555; do not assume heads are unchanged.
3. Preserve the immutable task-start baselines above.
4. Fix the focused proof harness first; do not modify production runtime without isolated evidence.
5. Require fresh exact-head target gates after any new PR #41 head.
6. After target proof passes, perform final target review/main-drift audit and expected-head merge.
7. Finalize governance #555 and require new exact-head Ownership/CI before merge.
8. Merge separate authoritative lifecycle-only archive and explicitly close any automatic duplicate archive PR.
9. Merge separate one-file durable program reconciliation.
10. Do not start OAM-018 before all OAM-017 stages merge.
