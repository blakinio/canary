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
last_verified_commit: "800142e65c2975e57647bf34128ab468532218f0"
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

# Disposition

`UNRESOLVED AT TASK START`.

`REUSE` must not be inferred from path/blob presence. OAM-022 must compare exact target/upstream/legacy behavior and relevant maintained-client packet support before classification.

# Acceptance criteria

- [x] Pin exact task-start Canary, Otheryn, upstream and maintained-OTClient revisions.
- [x] Select one dependency-valid canonical module after OAM-021 durable completion.
- [x] Audit open work and ownership for Prey/Taskboard/protocol overlap before target writes.
- [ ] Revalidate exact Prey runtime, persistence, data and packet behavior across target/upstream/legacy evidence.
- [ ] Inspect maintained-client Prey/Hunting Task contract where related.
- [ ] Classify the module from evidence and record explicit exclusions/known gaps.
- [ ] Implement or prove only the bounded accepted Otheryn target boundary.
- [ ] Obtain exact-final-head target CI/proof and perform changed-file/review/thread/main-drift audits before expected-head target merge.
- [ ] Reconcile Canary governance with exact target evidence and exact-head gates.
- [ ] Archive this active task in a separate lifecycle PR.
- [ ] Reconcile the durable Oteryn program in a separate one-file PR.
- [ ] Do not start OAM-023 until lifecycle and durable reconciliation are merged.

# Current state

OAM-022 is formally active with canonical module `prey`. Target classification is unresolved. The next action is exact source/history/client revalidation before any Otheryn runtime write.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20T08:49:00+02:00
head: 4f91d9f1e4eec4892b1a3f118b4c23a7d0fe4f53
branch: task/CAN-20260720-oteryn-prey-revalidation
pr: "612"
status: investigating
next_action: Compare exact task-start Otheryn Prey and Hunting Task behavior with fresh upstream and reviewed legacy history, then inspect any related maintained-OTClient packet contract before selecting the target disposition.
context_routes:
  - docs/agents/OTERYN_OAM_022_PREY_REVALIDATION.md
  - docs/agents/real-tibia/registry/modules/prey.yaml
owned_paths:
  - docs/agents/tasks/active/CAN-20260720-oteryn-prey-revalidation.md
  - docs/agents/OTERYN_OAM_022_PREY_REVALIDATION.md
proven:
  - OAM-021 durable completion is merged and OAM-022 is now eligible to start.
  - Canonical prey dependencies player-persistence and protocol are completed.
  - Fresh reviewed open work does not own Prey runtime or Taskboard data paths.
derived:
  - Prey is the smallest currently reviewed dependency-valid candidate compared with broader Cyclopedia and separately active Wheel ownership.
unknown:
  - Final OAM-022 migration disposition remains unresolved pending exact source and contract comparison.
conflicts: []
rejected_hypotheses:
  - Select Wheel of Destiny while its separate active parity program owns the broader domain.
  - Infer Prey REUSE from file presence or target-upstream ancestry alone.
changed_paths:
  - docs/agents/tasks/active/CAN-20260720-oteryn-prey-revalidation.md
  - docs/agents/OTERYN_OAM_022_PREY_REVALIDATION.md
blockers: []
first_failure:
  marker: none-at-task-start
  evidence: No OAM-022 validation failure has occurred yet; classification and target proof have not run.
validation:
  - command: Fresh live-state dependency ownership and cross-repository preflight
    result: PASS
    evidence: Exact baselines and reviewed non-overlap are recorded in this task and the OAM-022 report.
  - command: Exact Prey target upstream legacy and maintained-client revalidation
    result: NOT_RUN
    evidence: This is the concrete next action before any target runtime write.
```
