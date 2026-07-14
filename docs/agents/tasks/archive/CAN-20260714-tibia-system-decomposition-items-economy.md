---
task_id: CAN-20260714-tibia-system-decomposition-items-economy
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-007
status: merged
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition-items-economy
base_branch: main
created: 2026-07-14T23:30:00+02:00
updated: 2026-07-15T00:36:16+02:00
last_verified_commit: "4932c48d5899ac246404f65e2017a86fc6a5324b"
risk: low
related_issue: ""
related_pr: "#366"
depends_on:
  - completed and archived TSD-006
blocks:
  - TSD-008 world content decomposition
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260714-tibia-system-decomposition-items-economy.md
    - docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
  shared: []
  read_only:
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/real-tibia/**
    - tools/agents/**
    - .github/workflows/**
    - src/**
    - data/**
    - tests/**
modules_touched:
  - Real Tibia module registry
  - item definitions and instances
  - containers
  - item decay
reuses:
  - existing registry/generator/mapper
public_interfaces:
  - bounded item lifecycle discovery records
cross_repo_tasks: []
---

# Goal

Complete and archive bounded TSD-007 item and economy decomposition.

# Final result

PR #366 was squash-merged on `2026-07-14T22:36:16Z`.

- Task-start base: `821f213038770d68cd95b1b22afa78937b974210`.
- Final feature head: `de7d24658749b11a5bb93debce33de3264c553cf`.
- Squash merge SHA: `4932c48d5899ac246404f65e2017a86fc6a5324b`.
- Changed files: 15.
- Registry: 45 → 49.
- Modules added: `containers`, `item-decay`, `item-definitions`, `item-instances`.
- Existing records modified: 0.
- Runtime/gameplay/protocol/client/DB/map/OTBM/datapack/assets/workflows/E2E changed: no.

# Classification

- ItemType/Items registry and XML/appearance loading → `item-definitions`.
- Runtime factory, attributes, transforms and serialization → `item-instances`.
- Nested cylinder/container/depot/inbox/mailbox/reward-container lifecycle → `containers`.
- Scheduler-backed duration/transform lifecycle → `item-decay`.
- Movement, stacking, transfer, stash and managed-container behavior remain cross-cutting item/container capabilities.
- Market, Forge, Imbuements, weapons and boss rewards remain in existing records.
- Account coins and NPC trade remain deferred to later bounded inventories.

# Validation evidence

Final head `de7d24658749b11a5bb93debce33de3264c553cf`:

- Real Tibia Module Registry #302: success;
- Upstream Intelligence #333: success;
- Agent Task Ownership #1149: success;
- repository CI #2265: success;
- ready-state CI #2266: success;
- ready-state Lua Tests, Fast Checks, Linux release and Required: success;
- focused registry/source-role tests: success;
- schema/dependency validation and deterministic `generate --check`: success;
- changed-file review: 15 declared files;
- PR comments, reviews requesting changes and unresolved threads: none;
- exact final head preserved through ready-state CI.

Older TSD-005/TSD-006 tests were changed from exact global totals to package minimum baselines. TSD-007 alone owned the exact total 49 assertion. No mapper, module scope or runtime behavior changed.

# Safety boundary

Documentation, registry metadata, generated navigation and focused tests only. Path mapping remains discovery-only. This task proves neither item metadata parity, movement/transfer atomicity, duplication/loss safety, container correctness, serializer completeness, decay timing/restart behavior, economy correctness, runtime behavior, protocol compatibility, physical-client E2E, Real Tibia parity nor Oteryn readiness.

# Next exact task

```text
task: CAN-20260714-tibia-system-decomposition-world-content
program: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
package: TSD-008
branch: docs/tibia-system-decomposition-world-content
```

Start only after this lifecycle PR merges and current `main` is re-read.
