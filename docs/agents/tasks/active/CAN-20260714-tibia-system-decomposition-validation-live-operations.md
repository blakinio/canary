---
task_id: CAN-20260714-tibia-system-decomposition-validation-live-operations
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-012
status: active
agent: "GPT-5.5 Thinking"
branch: docs/tibia-system-decomposition-validation-live-operations
base_branch: main
created: 2026-07-15T13:10:00+02:00
updated: 2026-07-15T13:25:00+02:00
last_verified_commit: "da7a609b35dd25beb86c8a03eda2344daefb77f3"
risk: low
related_issue: ""
related_pr: "377"
depends_on:
  - completed and archived TSD-011
blocks:
  - TSD-013 Oteryn migration classification
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260714-tibia-system-decomposition-validation-live-operations.md
    - docs/agents/real-tibia/TSD_012_VALIDATION_LIVE_OPERATIONS_REPORT.md
    - docs/agents/real-tibia/registry/modules/deployment-operations.yaml
    - tools/agents/test_validation_live_operations_registry.py
  shared:
    - docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
    - docs/agents/real-tibia/generated/**
    - tools/agents/test_analytics_security_ai_registry.py
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/real-tibia/registry/modules/otbm-tooling.yaml
    - docs/agents/real-tibia/registry/modules/physical-client-e2e.yaml
    - docs/agents/real-tibia/registry/modules/upstream-intelligence.yaml
    - tools/agents/real_tibia_registry*.py
    - tools/agents/upstream_intelligence*.py
    - tools/ai-agent/**
    - tools/e2e/**
    - tools/deploy/**
    - .github/workflows/**
modules_touched:
  - Real Tibia module registry
  - deployment operations
reuses:
  - existing registry/generator/mapper
  - canonical OTBM tooling
  - universal physical-client E2E platform
  - Upstream Intelligence source-aware watcher/mapper
  - existing Canary staging/deployment pipeline
public_interfaces:
  - bounded deployment operations discovery record
cross_repo_tasks: []
---

# Goal

Complete bounded TSD-012 validation and live-operations decomposition without duplicating existing tooling. Preserve canonical OTBM analysis, physical-client E2E, Upstream Intelligence and current validators. Add only the independently rooted deployment-operations lifecycle already present under `tools/deploy/**` and its operational documentation.

# Exact base and preflight

- Task-start live main: `145929ec7f438dc492d4b618a386a4418953d7ec`.
- TSD-011 feature PR #374 and lifecycle PR #376 are both squash-merged before this task.
- Open PR #316 donor-map audit and PR #245 physical-client E2E are read-only and non-overlapping with this task's registry/docs/focused-test ownership.
- `ACTIVE_WORK.md` remains read-only.
- Writable repository is only `blakinio/canary`; upstream repositories remain read-only.

# Delivered implementation inventory

Registry records: 61 → 62. Added only:

- `deployment-operations`.

Existing records modified: 0. `otbm-tooling`, `physical-client-e2e`, `upstream-intelligence`, Real Tibia registry/generator/mapper and all existing gameplay/validation records remain unchanged.

# Boundary decision

- `deployment-operations`: existing trusted-base/overlay staging, real Canary preflight, atomic release publication, active/previous switch, post-switch smoke, rollback, release manifest and dry-run/production-confirmation lifecycle.
- `otbm-tooling`: already canonical for World Index, mechanic audit, script resolution, reachability, spawn/NPC, storage graph, semantic diff, geometry audit and factual rendering.
- `physical-client-e2e`: already canonical; open PR #245 remains independently owned and read-only.
- `upstream-intelligence`: already canonical; UI-001A is source-role-aware Upstream Intelligence mapping, not a separate UI module.
- quest-map/reachability/spawn/NPC/storage/diff/geometry validators remain capabilities, not new umbrella records.
- generic validation platform and second deployment/E2E/watcher/parser/renderer systems are rejected as duplicates.

Detailed evidence: `docs/agents/real-tibia/TSD_012_VALIDATION_LIVE_OPERATIONS_REPORT.md`.

# Validation state

Implementation/generated-index head `da7a609b35dd25beb86c8a03eda2344daefb77f3` passed:

- Real Tibia Module Registry #428: success;
- Upstream Intelligence #464: success;
- Agent Task Ownership #1289: success;
- repository CI #2412: success;
- focused registry regression tests: success;
- registry schema/contracts and dependency graph validation: success;
- deterministic `generate --check`: success;
- discovery and affected-module commands: success.

This task-record and program update are documentation-only after the validated implementation head. Final current-head checks and ready-state Linux/Required remain mandatory before squash merge.

# Acceptance criteria

- [x] Add only independently supported live-operations records.
- [x] Preserve existing OTBM/E2E/UI records unchanged.
- [x] Do not create duplicate validators, parsers, renderers, mappers, generators, watchers or E2E orchestration.
- [x] Regenerate deterministic registry indexes through the existing generator contract.
- [x] Add focused registry regression tests.
- [ ] Pass final exact-head registry/UI/ownership/repository CI and ready-state Linux/Required.
- [x] Make no runtime, gameplay, deployment implementation, client, DB, map, OTBM, datapack, asset, workflow or E2E implementation change.

# Safety limits

Inventory does not prove production deployment safety, operator correctness, host-supervisor integration, rollback availability, runtime stability, Real Tibia parity or Oteryn readiness.

# Handoff

After feature merge, archive this task in a separate lifecycle-only PR. Only after that archive merges may TSD-013 start from then-current `main`.
