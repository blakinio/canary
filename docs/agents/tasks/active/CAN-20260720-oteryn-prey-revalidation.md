---
task_id: CAN-20260720-oteryn-prey-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-022
status: implementing
agent: "GPT-5.5 Thinking"
branch: task/CAN-20260720-oteryn-prey-revalidation
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "50dfa248251f245f5519495a4fbd430b6814ffe4"
risk: high
related_pr: "612"
depends_on:
  - OAM-004 player-persistence foundation
  - OAM-006 protocol
blocks:
  - OAM-023
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260720-oteryn-prey-revalidation.md
    - docs/agents/OTERYN_OAM_022_PREY_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/real-tibia/registry/modules/prey.yaml
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
modules_touched:
  - prey
reuses:
  - completed OAM-004 player-persistence boundary
  - completed OAM-006 protocol boundary
public_interfaces:
  - Prey state and rerolls
  - Prey bonuses
  - Hunting Tasks and Task Shop integration boundary
  - related persistence and packets
cross_repo_tasks:
  - blakinio/Otheryn OAM-022 target revalidation and bounded implementation/proof
---

# Goal

Revalidate canonical OAM-022 `prey` against fresh live legacy, clean-target, upstream and maintained-client evidence; select only the strongest dependency-valid target disposition; implement or prove only the smallest coherent Prey/Hunting Tasks boundary in Otheryn; then complete governance, lifecycle archival and durable program reconciliation before OAM-023 starts.

# Immutable task-start baselines

- Canary: `800142e65c2975e57647bf34128ab468532218f0`
- Otheryn: `b90e287a40413102c87e8c7fa3d5c01ad401cb6d`
- upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`
- previous durable OAM-021 Canary reconciliation: `800142e65c2975e57647bf34128ab468532218f0`

# Fresh preflight

- OAM-021 durable program reconciliation is merged and its task is archived.
- Otheryn had no open pull request at task start.
- Maintained OTClient had no open pull request at task start.
- No pre-existing OAM-022 branch or pull request was found before this task began.
- Canonical `prey` depends only on completed `player-persistence` and `protocol`; `wheel-of-destiny` is an interaction and remains separately owned.
- Open Canary PR #514 owns security-validation tooling and declares protocol implementation files read-only; it is not a Prey runtime writer.
- Open Canary PR #600 is unrelated OTBM/E2E route work; #526 and #559 are evidence/documentation-only security work; #479 is archive-only cleanup.
- No reviewed open work writes the canonical Prey component or Taskboard data paths.

# Final disposition

```text
prey → REUSE
```

The reviewed classic Prey/Task Hunting core has no stronger independent legacy donor. `src/io/ioprey.cpp`, `src/io/ioprey.hpp`, and the Prey/Task Hunting save boundary are exact-identical across the pinned target, fresh upstream and legacy baselines; reviewed load functions are functionally identical. Maintained OTClient already carries the standard Prey contract.

Legacy Taskboard differs only through Wheel-owned Bonus Promotion Shop integration that consumes Hunting Task points while persisting/applying Wheel promotion points. That interaction remains under the separate Wheel parity program and is deliberately excluded from OAM-022.

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

Target PR #46 changed exactly three proof-only paths, with no production runtime/data/persistence/protocol/client/schema/map/asset/deployment mutation. Comments, reviews and review threads were empty; Otheryn `main` had no task-start drift before expected-head squash merge.

# Acceptance criteria

- [x] Pin exact task-start Canary, Otheryn, upstream and maintained-OTClient revisions.
- [x] Select one dependency-valid canonical module after OAM-021 durable completion.
- [x] Audit open work and ownership for Prey/Taskboard/protocol overlap before target writes.
- [x] Revalidate exact Prey runtime, persistence, data and packet behavior across target/upstream/legacy evidence.
- [x] Inspect maintained-client Prey/Hunting Task contract where related.
- [x] Classify the module from evidence and record explicit exclusions/known gaps.
- [x] Implement or prove only the bounded accepted Otheryn target boundary.
- [x] Obtain exact-final-head target CI/proof and perform changed-file/review/thread/main-drift audits before expected-head target merge.
- [ ] Reconcile Canary governance with exact target evidence and exact-head gates.
- [ ] Archive this active task in a separate lifecycle PR.
- [ ] Reconcile the durable Oteryn program in a separate one-file PR.
- [ ] Do not start OAM-023 until lifecycle and durable reconciliation are merged.

# Explicit exclusions

OAM-022 does not claim full modern official Hunting Task/Taskboard parity, Wheel Bonus Promotion Shop migration, Wheel allocation ownership, exhaustive Prey formulas/rarity/reroll-price/monster-pool parity, physical-client Prey or Taskboard E2E closure, generic persistence/protocol redesign, or map/OTBM/`items.otb`/asset/schema/deployment changes.

# Current state

The target stage is merged at `50dfa248251f245f5519495a4fbd430b6814ffe4`. Canary governance PR #612 owns exactly this active task and the OAM-022 report. Its next gate is exact-head Agent Task Ownership plus forced final-gate CI, followed by a clean blocker/drift audit and expected-head squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20T09:15:00+02:00
head: d717bd4a2404067df89724570c2c719a64c609cd
branch: task/CAN-20260720-oteryn-prey-revalidation
pr: "612"
status: validating
next_action: Mark Canary PR 612 ready, apply ci:final-gate, complete exact-head ownership and final-gate CI, audit changed files reviews threads and main drift, then expected-head squash merge governance.
context_routes:
  - docs/agents/OTERYN_OAM_022_PREY_REVALIDATION.md
  - docs/agents/real-tibia/registry/modules/prey.yaml
owned_paths:
  - docs/agents/tasks/active/CAN-20260720-oteryn-prey-revalidation.md
  - docs/agents/OTERYN_OAM_022_PREY_REVALIDATION.md
proven:
  - OAM-021 durable completion is merged and OAM-022 was dependency-valid to start.
  - Canonical prey dependencies player-persistence and protocol are completed.
  - Fresh reviewed open work did not own Prey runtime or Taskboard data paths at task start.
  - Exact source and persistence comparison plus maintained-client evidence support prey REUSE for the reviewed classic core.
  - Otheryn PR 46 merged by expected-head squash as 50dfa248251f245f5519495a4fbd430b6814ffe4 after CI 169 and Required 152 succeeded.
  - Linux debug CTest passed 400 of 400 and focused Oam022PreyReuseTest passed 4 of 4.
derived:
  - Legacy Wheel-coupled Taskboard Bonus Promotion Shop is an explicit interaction boundary and not a stronger independent Prey-core donor.
unknown:
  - Exact Canary governance squash merge SHA remains unknown until final-gate validation succeeds.
conflicts: []
rejected_hypotheses:
  - Select Wheel of Destiny while its separate active parity program owns the broader domain.
  - Infer Prey REUSE from file presence or target-upstream ancestry alone.
  - Copy legacy Wheel Taskboard Shop as if it were independent Prey core.
changed_paths:
  - docs/agents/tasks/active/CAN-20260720-oteryn-prey-revalidation.md
  - docs/agents/OTERYN_OAM_022_PREY_REVALIDATION.md
blockers:
  - Canary PR 612 exact-head ownership and final-gate CI must pass before governance merge.
first_failure:
  marker: none
  evidence: OAM-022 target proof completed without a validation failure; governance final-gate validation is pending.
validation:
  - command: Fresh live-state dependency ownership and cross-repository preflight
    result: PASS
    evidence: Exact baselines and reviewed non-overlap are recorded in this task and the OAM-022 report.
  - command: Exact Prey target upstream legacy and maintained-client revalidation
    result: PASS
    evidence: Reviewed classic Prey core and persistence are exact or functionally identical and maintained OTClient already carries the standard Prey contract; Wheel Taskboard interaction is explicitly excluded.
  - command: Otheryn PR 46 exact-head CI proof and pre-merge blocker audit
    result: PASS
    evidence: CI 169 Required 152 and autofix 145 succeeded on 12d79e4532e5784e9530caf433cdad1c869f0142; 400 of 400 CTest and 4 of 4 focused tests passed; exactly three proof paths; zero review blockers; no target-main drift.
  - command: Otheryn PR 46 expected-head squash merge
    result: PASS
    evidence: Exact head 12d79e4532e5784e9530caf433cdad1c869f0142 merged as 50dfa248251f245f5519495a4fbd430b6814ffe4.
```
