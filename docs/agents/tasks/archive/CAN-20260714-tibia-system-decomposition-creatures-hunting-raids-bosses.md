---
task_id: CAN-20260714-tibia-system-decomposition-creatures-hunting-raids-bosses
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-006
status: merged
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition-creatures-hunting-raids-bosses
base_branch: main
created: 2026-07-14T22:50:00+02:00
updated: 2026-07-14T23:20:50+02:00
last_verified_commit: "8dfec274b0f460c1f0d6bee6c8a4b95a3ecf8c12"
risk: low
related_issue: ""
related_pr: "#364"
depends_on:
  - completed and archived TSD-005
blocks:
  - TSD-007 items and economy decomposition
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260714-tibia-system-decomposition-creatures-hunting-raids-bosses.md
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
  - creature definitions
  - creature AI
  - boss encounters
  - raids
reuses:
  - existing Real Tibia registry-as-code
  - existing deterministic generator
  - source-role-aware Upstream Intelligence mapper
  - existing spawn/NPC validation tooling
public_interfaces:
  - bounded creature, encounter and raid discovery records
cross_repo_tasks: []
---

# Goal

Complete and archive bounded TSD-006 creatures, hunting, raids and bosses decomposition.

# Final result

PR #364 was squash-merged on `2026-07-14T21:20:50Z`.

- Task-start base: `f68f826915882b0b20081b8fca5ed975ce303f45`.
- Final feature head: `80092bebd03969d68b6b4e0c040926a712c7880f`.
- Squash merge SHA: `8dfec274b0f460c1f0d6bee6c8a4b95a3ecf8c12`.
- Changed files: 13.
- Registry: 41 → 45.
- Modules added: `boss-encounters`, `creature-ai`, `creature-definitions`, `raids`.
- Existing records modified: 0.
- Runtime/gameplay/protocol/client/DB/map/OTBM/datapack/assets/workflows/E2E changed: no.

# Classification

- Monster definitions and data registry → `creature-definitions`.
- Runtime think/target/follow/flee/movement/attack lifecycle → `creature-ai`.
- Reward-boss participation/scoring/reward-container lifecycle → `boss-encounters`.
- Raid registry/scheduling/ordered events/reset/reload → `raids`.
- Static placement and generic dynamic creation remain in `spawns`.
- Prey/Hunting Tasks, Bestiary and Bosstiary credit remain in existing records.
- Individual creatures, bosses and raids remain data entries.

# Validation evidence

Final head `80092bebd03969d68b6b4e0c040926a712c7880f`:

- Real Tibia Module Registry #277: success;
- Upstream Intelligence #307: success;
- Agent Task Ownership #1128: success;
- repository CI #2243: success;
- ready-state CI #2244: success;
- ready-state Lua Tests, Fast Checks, Linux release and Required: success;
- focused registry/source-role tests: success;
- schema/dependency validation and deterministic `generate --check`: success;
- changed-file review: 13 declared files;
- PR comments, reviews requesting changes and unresolved threads: none;
- mergeable immediately before merge: yes;
- exact-head merge guard used.

The only review fix normalized `interacts_with` ordering in `creature-ai` and `raids`; scope, paths, dependencies and runtime behavior remained unchanged.

# Safety boundary

Documentation, registry metadata, generated navigation and focused tests only. Path mapping remains discovery-only. This task proves neither creature AI, pathfinding, target choice, spawn timing, boss scoring/rewards, raid probability/order, hunting credit, persistence safety, runtime behavior, parity nor Oteryn readiness.

# Next exact task

```text
task: CAN-20260714-tibia-system-decomposition-items-economy
program: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
package: TSD-007
branch: docs/tibia-system-decomposition-items-economy
```

Start only after this lifecycle PR merges and current `main` is re-read.
