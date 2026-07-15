---
task_id: CAN-20260714-tibia-system-decomposition-analytics-security-ai
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-011
status: active
agent: "GPT-5.5 Thinking"
branch: docs/tibia-system-decomposition-analytics-security-ai
base_branch: main
created: 2026-07-15T11:45:00+02:00
updated: 2026-07-15T11:55:00+02:00
last_verified_commit: "99928c9a0c9bfce9d4fe873ad44f5a5c296995d0"
risk: low
related_issue: ""
related_pr: "374"
depends_on:
  - completed and archived TSD-010
blocks:
  - TSD-012 validation and live operations decomposition
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260714-tibia-system-decomposition-analytics-security-ai.md
    - docs/agents/real-tibia/TSD_011_ANALYTICS_SECURITY_AI_REPORT.md
    - docs/agents/real-tibia/registry/modules/gameplay-analytics.yaml
    - tools/agents/test_analytics_security_ai_registry.py
    - tools/agents/test_upstream_intelligence_analytics_security_ai.py
  shared:
    - docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
    - docs/agents/real-tibia/generated/**
    - tools/agents/test_protocol_client_registry.py
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/real-tibia/registry/modules/account-authentication.yaml
    - docs/agents/real-tibia/registry/modules/sanctions.yaml
    - docs/agents/real-tibia/registry/modules/upstream-intelligence.yaml
    - docs/agents/real-tibia/registry/modules/otbm-tooling.yaml
    - docs/agents/real-tibia/registry/modules/physical-client-e2e.yaml
    - tools/agents/real_tibia_registry*.py
    - tools/agents/upstream_intelligence*.py
    - tools/ai-agent/**
    - tools/analytics/**
    - .github/workflows/**
    - data-otservbr-global/scripts/config/gameplay_analytics.lua
    - data-otservbr-global/scripts/lib/gameplay_analytics*.lua
    - data-otservbr-global/scripts/systems/gameplay_analytics.lua
modules_touched:
  - Real Tibia module registry
  - gameplay analytics
reuses:
  - existing registry/generator/mapper
  - existing Gameplay Analytics runtime and dry-run stack
  - existing account authentication and sanctions boundaries
  - existing validation tooling reserved for TSD-012
public_interfaces:
  - bounded gameplay analytics discovery record
cross_repo_tasks: []
---

# Goal

Complete bounded TSD-011 analytics, security and AI inventory without implementing planned systems. Preserve existing authentication, sanctions, protocol and platform-tooling records. Add only durable current analysis domains with independent roots.

# Exact base and preflight

- Task-start live main: `c67c84749ffd1de04983be9ae9841b6ca5756aed`.
- TSD-010 feature PR #372 and lifecycle PR #373 are both squash-merged before this task.
- Open PRs #316 donor-map audit and #245 physical-client E2E are non-overlapping with this task's registry/docs/focused-test ownership.
- `ACTIVE_WORK.md` remains read-only.
- Writable repository is only `blakinio/canary`; upstream repositories remain read-only.

# Delivered implementation inventory

Registry records: 60 → 61. Added only:

- `gameplay-analytics`.

Existing records modified: 0. `account-authentication`, `sanctions`, `protocol`, `upstream-intelligence`, `otbm-tooling`, `physical-client-e2e`, validation/audit tooling and all gameplay records remain unchanged.

# Boundary decision

- optional Gameplay Analytics telemetry session/queue/retry/dead-letter/dry-run/reporting lifecycle → `gameplay-analytics`;
- password/session-token security remains `account-authentication`;
- throttling and account/IP/namelock restrictions remain `sanctions`;
- `security-analytics` remains deferred and unimplemented;
- `chat-safety-intelligence` remains deferred and unimplemented;
- `ai-investigation` remains deferred and unimplemented;
- generic `ai-agent-tooling` remains deferred because it would duplicate heterogeneous validators/OTBM tooling and preempt TSD-012;
- existing `otbm-tooling`, `upstream-intelligence` and `physical-client-e2e` remain unchanged.

Detailed evidence: `docs/agents/real-tibia/TSD_011_ANALYTICS_SECURITY_AI_REPORT.md`.

# Validation state

Implementation/generated-index head `99928c9a0c9bfce9d4fe873ad44f5a5c296995d0` passed:

- Real Tibia Module Registry #409: success;
- Upstream Intelligence #445: success;
- Agent Task Ownership #1273: success;
- repository CI #2395: success;
- focused registry/source-role tests: success;
- registry schema/contracts and dependency graph validation: success;
- deterministic `generate --check`: success;
- discovery and affected-module commands: success.

The earlier final-doc attempt on `27194fc95a5034705a8667fa1bb148c43955c730` exposed missing generated `MODULE_PATH_INDEX.md` and `STALE_MODULES.md`; both were repaired without changing module scope or runtime behavior.

This task-record and program update are documentation-only after the validated implementation head. Final current-head checks and ready-state Linux/Required remain mandatory before squash merge.

# Acceptance criteria

- [x] Add only independently supported analysis records.
- [x] Preserve authentication, sanctions and existing platform-tooling records unchanged.
- [x] Explicitly defer all forbidden planned security/AI systems.
- [x] Keep generic validation/OTBM/E2E tooling for TSD-012 rather than duplicating it here.
- [x] Use verified narrow paths and conservative maturity.
- [x] Regenerate deterministic indexes through the existing generator contract.
- [x] Add focused registry and source-role mapping tests.
- [ ] Pass final exact-head registry/UI/ownership/repository CI and ready-state Linux/Required.
- [x] Make no runtime, gameplay, analytics implementation, security implementation, AI implementation, client, DB, map, OTBM, datapack, asset, workflow or E2E implementation change.

# Safety limits

Inventory does not prove analytics completeness, privacy, retention, production runtime stability, persistence correctness, security assurance, abuse detection, anomaly detection, AI behavior, Real Tibia parity or Oteryn readiness.

# Handoff

After feature merge, archive this task in a separate lifecycle-only PR. Only after that archive merges may TSD-012 start from then-current `main`.
