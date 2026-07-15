---
task_id: CAN-20260714-tibia-system-decomposition-analytics-security-ai
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-011
status: active
agent: "GPT-5.5 Thinking"
branch: docs/tibia-system-decomposition-analytics-security-ai
base_branch: main
created: 2026-07-15T11:45:00+02:00
updated: 2026-07-15T11:45:00+02:00
last_verified_commit: "c67c84749ffd1de04983be9ae9841b6ca5756aed"
risk: low
related_issue: ""
related_pr: ""
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

# Evidence baseline

Current source/documentation establishes one independent durable analytics root:

- optional Gameplay Analytics runtime under `data-otservbr-global/scripts/**`;
- bounded session telemetry lifecycle with queues, retry/dead-letter behavior and optional persistence;
- deterministic dry-run validators/test harnesses under `tools/analytics/**`;
- dedicated dry-run workflow and reporting/maintenance documentation.

Existing security roots remain already covered:

- password verification, login session tokens and cryptographic password handling → `account-authentication`;
- connection throttling plus account/IP/namelock sanctions → `sanctions`.

AI/validation roots under `tools/ai-agent/**` remain reusable validation tooling for TSD-012. This task must not create a generic AI platform module or duplicate OTBM/validation tooling.

# Candidate classification under review

- `gameplay-analytics` — candidate `ADD_NOW`;
- `authentication-security` — `ALREADY_COVERED` by `account-authentication`;
- `sanction-security` — `ALREADY_COVERED` by `sanctions`;
- `security-analytics` — `DEFER`, planned system explicitly forbidden;
- `chat-safety-intelligence` — `DEFER`, planned system explicitly forbidden;
- `ai-investigation` — `DEFER`, planned system explicitly forbidden;
- generic `ai-agent-tooling` / validator family — defer to TSD-012 and reuse existing tooling rather than creating a duplicate umbrella.

# Acceptance criteria

- [ ] Add only independently supported analysis records.
- [ ] Preserve authentication, sanctions and existing platform-tooling records unchanged.
- [ ] Explicitly defer all forbidden planned security/AI systems.
- [ ] Keep generic validation/OTBM/E2E tooling for TSD-012 rather than duplicating it here.
- [ ] Use verified narrow paths and conservative maturity.
- [ ] Regenerate deterministic indexes through the existing generator contract.
- [ ] Add focused registry and source-role mapping tests.
- [ ] Pass exact-head registry/UI/ownership/repository CI and ready-state Linux/Required.
- [ ] Make no runtime, gameplay, analytics implementation, security implementation, AI implementation, client, DB, map, OTBM, datapack, asset, workflow or E2E implementation change.

# Safety limits

Inventory does not prove analytics completeness, privacy, retention, production runtime stability, persistence correctness, security assurance, abuse detection, anomaly detection, AI behavior, Real Tibia parity or Oteryn readiness.

# Handoff

After feature merge, archive this task in a separate lifecycle-only PR. Only after that archive merges may TSD-012 start from then-current `main`.
