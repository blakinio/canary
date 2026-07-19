---
task_id: CAN-20260719-oteryn-item-decay-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-018
status: active
agent: "GPT-5.5 Thinking"
branch: docs/oam-018-item-decay-revalidation
base_branch: main
created: 2026-07-19
updated: 2026-07-19T11:18:08+02:00
last_verified_commit: "3c4d2789ffa3d0c1e9453d20a8c5faeba35eb366"
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

# Provisional disposition

```text
item-decay → REUSE (candidate; target proof required)
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
- Otheryn has no open PRs.
- Live Canary PRs #573, #572, #559, #526 and #514 do not touch `src/items/decay/**`.

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

# Current blocker

Fresh preflight is complete, but repository policy permits mutations only in `blakinio/canary` unless the user explicitly authorizes mutation of another named repository. No OAM-018 write has been made to `blakinio/Otheryn`.

The next target step requires explicit authorization to mutate `blakinio/Otheryn` for OAM-018. Until then, the target remains read-only and no proof branch/issue/PR will be created there.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T11:18:08+02:00
head: 211f6690ca5cd2a519a66d4b3b497d9c05138d28
branch: docs/oam-018-item-decay-revalidation
pr: 578
status: preflight-complete
next_action: After explicit user authorization to mutate blakinio/Otheryn for OAM-018, create a proof-only target branch/PR and add bounded item-decay tests without changing production decay runtime unless concrete evidence proves a defect.
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
  - Fresh task-start baselines are pinned above.
  - Canonical item-decay depends on completed OAM-003 engine-scheduler and OAM-007 item-instances boundaries.
  - Otheryn has no open PR and the five live Canary PRs do not overlap src/items/decay/**.
  - Target history since verified bootstrap contains no item-decay production mutation.
  - Pinned upstream history through task start contains no item-decay production mutation.
  - Target and upstream share decay.cpp blob a337b872755217d87ac2261de6c3c1a593d805a6.
  - Legacy Canary decay.cpp differs only in the reviewed scheduler-lane call surface and uses the weaker legacy scheduler boundary rejected by OAM-003.
  - All three repositories share decay.hpp blob 0d540e10dc73b65f2ce1aa00bfb9dd72994dcc5f.
derived:
  - item-decay is the next dependency-valid canonical OAM package.
  - The strongest current implementation candidate is target/upstream REUSE, not legacy import.
unknown:
  - Exact target proof shape and final proof head remain unknown until target mutation is authorized and the focused harness is implemented.
  - Final OAM-018 disposition remains provisional until exact-head target proof passes.
conflicts: []
rejected_hypotheses:
  - Treating legacy decay.cpp blob inequality as sufficient reason to import legacy runtime.
  - Treating omission of DispatcherLane::Maintenance as a stronger item-decay behavior.
changed_paths:
  - docs/agents/OTERYN_OAM_018_ITEM_DECAY_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260719-oteryn-item-decay-revalidation.md
blockers:
  - Explicit user authorization is required before mutating blakinio/Otheryn for the OAM-018 target proof.
validation:
  - command: OAM-018 fresh live-state and ownership preflight
    result: PASS
    evidence: Canary/Otheryn/upstream/OTClient baselines pinned; Otheryn has zero open PRs; live Canary PR changed-file lists do not overlap src/items/decay/**.
  - command: Otheryn bootstrap-to-task-start boundary comparison
    result: PASS
    evidence: No src/items/decay/** file changed between 3cc7c1dfea747bb380f3761ee7ff7ac30141a115 and 952e7550182df739824bddea687ef89bd8997674.
  - command: Upstream bootstrap-to-task-start boundary comparison
    result: PASS
    evidence: No src/items/decay/** file changed between a879c9312e34381e8eedf397b8ed44510698b689 and 691614c1a302aee776002ca3851eca399be1a82c.
  - command: Exact item-decay blob comparison
    result: PASS
    evidence: Target/upstream decay.cpp are identical; all decay.hpp blobs are identical; legacy decay.cpp differs at the scheduler lane call boundary already classified by OAM-003.
```

# Next-agent sequence

1. Read this task and `docs/agents/OTERYN_OAM_018_ITEM_DECAY_REVALIDATION.md`.
2. Verify live Canary/Otheryn `main`, open PRs and current task branch/head again.
3. Do not mutate Otheryn until explicit user authorization for OAM-018 target writes is available.
4. Once authorized, design the smallest proof-only target test package for the existing target decay lifecycle.
5. Treat any red focused proof as a proof-harness problem until concrete evidence demonstrates a production `item-decay` defect.
6. Require fresh exact-head target gates after every target-head mutation.
7. Only after target proof merge continue governance → authoritative lifecycle archive → close automatic duplicate archive PR if created → one-file durable program reconciliation.
8. Do not start OAM-019 until every OAM-018 stage is merged.
