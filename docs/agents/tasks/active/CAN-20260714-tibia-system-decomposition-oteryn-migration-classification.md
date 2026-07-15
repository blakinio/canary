---
task_id: CAN-20260714-tibia-system-decomposition-oteryn-migration-classification
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-013
status: active
agent: "GPT-5.5 Thinking"
branch: docs/tibia-system-decomposition-oteryn-migration-classification
base_branch: main
created: 2026-07-15T13:50:52+02:00
updated: 2026-07-15T13:55:00+02:00
last_verified_commit: "10d4bf63cf356a3cf912cbc8717854e6a6fd2895"
risk: low
related_issue: ""
related_pr: "379"
depends_on:
  - completed and archived TSD-012
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260714-tibia-system-decomposition-oteryn-migration-classification.md
    - docs/agents/real-tibia/TSD_013_OTERYN_MIGRATION_CLASSIFICATION_REPORT.md
    - tools/agents/test_oteryn_migration_classification.py
  shared:
    - docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
  read_only:
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/real-tibia/registry/**
    - docs/agents/real-tibia/generated/**
    - tools/agents/real_tibia_registry*.py
    - tools/agents/upstream_intelligence*.py
    - .github/workflows/**
    - src/**
    - data/**
    - data-canary/**
    - data-otservbr-global/**
    - tools/ai-agent/**
    - tools/e2e/**
    - tools/deploy/**
modules_touched:
  - completed Real Tibia module inventory classification
reuses:
  - existing canonical Real Tibia registry
  - existing maturity and proof metadata
  - existing package reports and program history
public_interfaces:
  - conservative Oteryn migration disposition checkpoint
cross_repo_tasks: []
---

# Goal

Complete TSD-013 by classifying the completed canonical 62-module inventory for Oteryn migration without copying code, creating another registry or inferring target compatibility from Canary inventory.

# Exact base and preflight

- Task-start live main: `10d4bf63cf356a3cf912cbc8717854e6a6fd2895`.
- TSD-012 feature PR #377 and lifecycle PR #378 are both squash-merged before this task.
- Open PR #316 donor-map audit and PR #245 physical-client E2E remain independently owned and non-overlapping with this docs/focused-test scope.
- `ACTIVE_WORK.md` remains read-only.
- Writable repository is only `blakinio/canary`; all external repositories remain read-only.
- Program-level `cross_repo_contracts` is empty; no Oteryn target architecture contract is present in the current program record.

# Classification rule

At this checkpoint every module in the canonical registry is classified **REVALIDATE** for Oteryn migration.

This is a disposition rule over the live canonical registry, not a duplicated per-module registry. It means:

- no module is approved for direct copy or port-as-is;
- no module is declared Oteryn-ready;
- no module is declared drop/rewrite without a target architecture decision;
- higher Canary evidence maturity remains useful source evidence but is not target compatibility proof;
- any future migration decision must re-read the then-current canonical registry and an explicit Oteryn architecture/contract.

Detailed evidence: `docs/agents/real-tibia/TSD_013_OTERYN_MIGRATION_CLASSIFICATION_REPORT.md`.

# Acceptance criteria

- [x] Preserve registry records and generated indexes unchanged.
- [x] Document one conservative disposition that applies to all 62 canonical records without duplicating the registry.
- [x] Add a focused regression test that reads the live registry rather than hard-coding module IDs.
- [x] Record the unresolved Oteryn architecture contract as a blocker for any stronger migration disposition.
- [ ] Pass exact-head ownership/repository CI and ready-state Linux/Required.
- [x] Copy no code to Oteryn and make no runtime/gameplay/protocol/client/DB/map/OTBM/datapack/asset/workflow/E2E implementation change.

# Safety limits

TSD-013 is classification only. `REVALIDATE` is not readiness, implementation authorization or migration approval. No target architecture is invented.

# Handoff

After feature merge, archive this task in a separate lifecycle-only PR and mark the bounded TSD-001..TSD-013 queue complete. Future Oteryn work requires an explicit architecture contract and a new bounded task; it must re-read the canonical registry rather than copying this report into a second registry.
