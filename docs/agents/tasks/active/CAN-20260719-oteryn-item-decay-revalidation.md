---
task_id: CAN-20260719-oteryn-item-decay-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-018
status: ready
agent: "GPT-5.5 Thinking"
branch: docs/oam-018-item-decay-revalidation
base_branch: main
created: 2026-07-19
updated: 2026-07-19T12:31:00+02:00
last_verified_commit: "c2e27060165b91c1de6a5f40571060e480cdcb06"
risk: high
related_pr: "578"
depends_on:
  - OAM-003
  - OAM-007
blocks:
  - OAM-019
modules_touched:
  - item-decay
owned_paths:
  exclusive:
    - docs/agents/OTERYN_OAM_018_ITEM_DECAY_REVALIDATION.md
    - docs/agents/tasks/active/CAN-20260719-oteryn-item-decay-revalidation.md
---

# Goal

Revalidate canonical OAM-018 `item-decay` against immutable fresh task-start baselines and accept only the strongest dependency-valid target implementation.

# Final disposition

```text
item-decay → REUSE
```

# Immutable task-start baselines

```text
Canary:   3c4d2789ffa3d0c1e9453d20a8c5faeba35eb366
Otheryn:  952e7550182df739824bddea687ef89bd8997674
upstream: 691614c1a302aee776002ca3851eca399be1a82c
OTClient: 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

# Dependency and ownership preflight

Canonical `item-decay` depends on `engine-scheduler` and `item-instances`.

- OAM-003 completed `engine-scheduler → REUSE` and retained the target/upstream lane/WDRR scheduler.
- OAM-007 completed the target item foundation containing `item-instances` ownership.
- Otheryn had no open PRs at preflight.
- Live Canary PRs #573, #572, #559, #526 and #514 did not touch `src/items/decay/**` at preflight.

No overlapping live ownership was found for the canonical runtime boundary.

# Provenance result

Target history from `3cc7c1dfea747bb380f3761ee7ff7ac30141a115` through task-start Otheryn contains no `src/items/decay/**` mutation. Pinned upstream history from `a879c9312e34381e8eedf397b8ed44510698b689` through `691614c1a302aee776002ca3851eca399be1a82c` also contains no decay-boundary mutation.

Exact task-start blobs:

```text
Otheryn/upstream decay.cpp: a337b872755217d87ac2261de6c3c1a593d805a6
Canary decay.cpp:           458cda4ac92f21289ca1072447e79c71de645ae8
all decay.hpp:              0d540e10dc73b65f2ce1aa00bfb9dd72994dcc5f
```

The legacy `decay.cpp` delta removes the three `DispatcherLane::Maintenance` arguments from decay scheduling. OAM-003 already established the target/upstream lane scheduler as canonical and rejected the older legacy scheduler model. The legacy delta is therefore rejected as a stronger decay donor.

# Exact target proof

Target PR: `blakinio/Otheryn#42` — merged.

```text
task-start target: 952e7550182df739824bddea687ef89bd8997674
final target proof head: 13e245f3c49477fa75c20171f0c845dec91d0824
target squash merge: 7ba76d2754a060a9a9eec0a23c686aefac725af2
autofix.ci #110 / 29682419114: SUCCESS
CI #130 / 29682419178: SUCCESS after one failed-job rerun
Required #117 / 29682419125: SUCCESS after rerun against green CI #130
full Linux debug CTest: 359/359 PASS
focused ItemDecayReuseTest: 2/2 PASS
linux-debug-test-logs artifact: 8441163603
digest: sha256:de3f541b41aa9d4f39a4d8d629de52a51e09b8eaff461c8706bb7a296cfd9631
comments: 0
reviews: 0
review threads: 0
```

The target diff changed exactly:
- `tests/unit/items/CMakeLists.txt`;
- `tests/unit/items/decay/decay_test.cpp`.

No production `src/items/decay/**`, scheduler, item runtime, persistence, protocol, data, map or client path changed.

The first ready-cycle macOS job compiled successfully but reported a runtime-smoke wrapper failure. Its artifact showed the server reached online state and shut down cleanly with empty stderr. A single failed-job rerun on the same exact head passed the macOS runtime smoke without code changes. This is classified as a transient smoke-harness/timing false negative, not an `item-decay` defect.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T12:31:00+02:00
head: dd22f7babb80ff838bcd7c20e8df211e62f28659
branch: docs/oam-018-item-decay-revalidation
pr: 578
status: ready
next_action: Require fresh exact-final-head Agent Task Ownership and CI success for Canary PR #578 after this final task commit, then audit changed files, reviews, threads and main drift and squash-merge PR #578 with expected-head before starting the separate lifecycle archive.
first_failure:
  marker: Canary Agent Task Ownership #2506 first exposed an invalid OAM-018 checkpoint schema; #2511 narrowed the next defect to first_failure being a scalar; #2523 then exposed the invalid frontmatter status active.
  evidence: Ownership artifacts successively reported missing first_failure plus unsupported preflight-complete status, first_failure must be a YAML mapping, and record under tasks/active has non-active status active; all are governance metadata defects and none implicates target item-decay runtime.
context_routes:
  - docs/agents/OTERYN_OAM_018_ITEM_DECAY_REVALIDATION.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  - docs/agents/real-tibia/registry/modules/item-decay.yaml
  - docs/agents/real-tibia/TSD_007_ITEMS_ECONOMY_REPORT.md
owned_paths:
  - docs/agents/OTERYN_OAM_018_ITEM_DECAY_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260719-oteryn-item-decay-revalidation.md
proven:
  - OAM-017 is fully complete through target, governance, lifecycle and durable program reconciliation.
  - Fresh OAM-018 task-start baselines are pinned above.
  - Canonical item-decay depends on completed OAM-003 engine-scheduler and OAM-007 item-instances boundaries.
  - Target history since verified bootstrap contains no item-decay production mutation.
  - Pinned upstream history through task start contains no item-decay production mutation.
  - Target and upstream share decay.cpp blob a337b872755217d87ac2261de6c3c1a593d805a6.
  - Legacy Canary decay.cpp differs only at the weaker scheduler-lane call surface rejected as a stronger donor by OAM-003 architecture evidence.
  - All three repositories share decay.hpp blob 0d540e10dc73b65f2ce1aa00bfb9dd72994dcc5f.
  - Otheryn PR #42 changed only two unit-test paths and no production runtime path.
  - Otheryn PR #42 exact head 13e245f3c49477fa75c20171f0c845dec91d0824 passed autofix #110, CI #130 and Required #117.
  - Otheryn PR #42 Linux debug CTest passed 359 of 359 tests including both ItemDecayReuseTest focused cases.
  - The first macOS smoke-wrapper failure was transient; a single same-head failed-job rerun passed without code changes.
  - Otheryn PR #42 had zero comments, zero submitted reviews and zero review threads before merge.
  - Otheryn main did not drift from task-start target before merge.
  - Otheryn PR #42 was squash-merged as 7ba76d2754a060a9a9eec0a23c686aefac725af2.
  - Final OAM-018 disposition is item-decay REUSE.
derived:
  - The target/upstream decay lifecycle is the strongest dependency-valid implementation among the reviewed sources.
  - No legacy runtime import or target production adaptation is justified for OAM-018.
unknown:
  - Canary PR #578 exact-final-head ownership and CI results are pending after this final task commit.
  - Canary main drift must be re-audited immediately before governance merge.
conflicts: []
rejected_hypotheses:
  - Treating legacy decay.cpp blob inequality as sufficient reason to import legacy runtime.
  - Treating omission of DispatcherLane::Maintenance as a stronger item-decay behavior.
  - Treating draft CI #129 and Required #116 as sufficient target proof when build/test jobs were skipped.
  - Treating the first macOS smoke-wrapper failure as a production item-decay defect despite successful compilation, clean runtime artifact evidence and a green same-head rerun.
changed_paths:
  - docs/agents/OTERYN_OAM_018_ITEM_DECAY_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260719-oteryn-item-decay-revalidation.md
blockers: []
validation:
  - command: OAM-018 fresh live-state and ownership preflight
    result: PASS
    evidence: Canary/Otheryn/upstream/OTClient baselines pinned; no preflight ownership overlap was found for src/items/decay/**.
  - command: Otheryn bootstrap-to-task-start boundary comparison
    result: PASS
    evidence: No src/items/decay/** file changed between 3cc7c1dfea747bb380f3761ee7ff7ac30141a115 and 952e7550182df739824bddea687ef89bd8997674.
  - command: Upstream bootstrap-to-task-start boundary comparison
    result: PASS
    evidence: No src/items/decay/** file changed between a879c9312e34381e8eedf397b8ed44510698b689 and 691614c1a302aee776002ca3851eca399be1a82c.
  - command: Exact item-decay blob comparison
    result: PASS
    evidence: Target/upstream decay.cpp are identical; all decay.hpp blobs are identical; legacy decay.cpp differs at the scheduler lane call boundary already classified by OAM-003.
  - command: Otheryn PR #42 proof-only changed-file audit
    result: PASS
    evidence: Exactly tests/unit/items/CMakeLists.txt and tests/unit/items/decay/decay_test.cpp changed; no production path changed.
  - command: Otheryn PR #42 exact-head target gates
    result: PASS
    evidence: Autofix #110, CI #130 and Required #117 all succeeded on 13e245f3c49477fa75c20171f0c845dec91d0824; full CTest 359/359 and focused ItemDecayReuseTest 2/2 passed.
  - command: Otheryn PR #42 expected-head squash merge
    result: PASS
    evidence: Exact head 13e245f3c49477fa75c20171f0c845dec91d0824 merged as 7ba76d2754a060a9a9eec0a23c686aefac725af2.
```

# Next-agent sequence

1. Do not mutate this governance branch after the exact-final-head gate turns green.
2. Verify PR #578 final changed-file list, comments, reviews, review threads, mergeability and current-main drift.
3. Squash-merge PR #578 using its exact final head.
4. Create a separate authoritative lifecycle-only PR that archives this task and removes the active record.
5. Close any automation-created duplicate archive PR only after the authoritative lifecycle PR merges.
6. Create a separate one-file durable program reconciliation PR for OAM-018.
7. Do not start OAM-019 until every OAM-018 stage is merged.
