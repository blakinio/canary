---
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
name: Tibia System Decomposition
status: active
owner: repository-wide
created: 2026-07-14T15:43:00+02:00
updated: 2026-07-15T11:55:00+02:00
last_verified_commit: "99928c9a0c9bfce9d4fe873ad44f5a5c296995d0"
primary_paths:
  - docs/agents/real-tibia/**
  - docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
shared_integration_paths:
  - tools/agents/real_tibia_registry*.py
  - tools/agents/upstream_intelligence*.py
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
related_programs:
  - CAN-PROGRAM-REAL-TIBIA-PARITY
  - CAN-PROGRAM-UPSTREAM-INTELLIGENCE
  - CAN-PROGRAM-E2E-PLATFORM
cross_repo_contracts: []
---

# Mission

Maintain one durable logical decomposition of Tibia and Canary through the existing Real Tibia registry so agents can discover bounded domains, coordinate work, map upstream changes, assign proof layers and later classify migration work for Oteryn without changing gameplay or physically reorganizing the legacy source tree.

This program is architecture, registry metadata, documentation and coordination only. It never authorizes runtime changes.

# Source-of-truth and safety contract

The only canonical module inventory is `docs/agents/real-tibia/registry/**`. Generated indexes are derived artifacts; package reports explain decisions but are not a second registry.

Permanent rules:

- path hints are discovery, not ownership or edit authorization;
- broad existing IDs remain stable umbrellas;
- narrow records use verified current paths and never broad server `src/**`;
- `depends_on` means a fundamental dependency and must remain acyclic;
- file/schema/helper/migration/test presence supports at most inventory;
- no TSD package claims gameplay/runtime, persistence, protocol, parity, E2E or Oteryn readiness;
- no second registry, generator, watcher, mapper, parser, renderer or E2E orchestrator;
- no physical source-tree refactor or normal-task edit to `ACTIVE_WORK.md`.

New decomposition records start at lifecycle/implementation/evidence `inventory`; persistence, protocol, automated tests, runtime validation and gameplay E2E stay `not-assessed` unless a later narrow proof task establishes otherwise.

# Bounded package queue

| ID | Scope | Status | Evidence baseline | Exact next action |
|---|---|---|---|---|
| `TSD-001` | taxonomy/hierarchy foundation and pilot | completed | PR #335; registry 19 → 22 | preserve archive |
| `TSD-002A` | engine foundation | completed | PR #340; registry 22 → 26 | preserve archive |
| `TSD-002B` | persistence and transactions | completed | PR #342; registry 26 → 29 | preserve archive |
| `TSD-003` | account, character and progression | completed | PR #355; registry 29 → 35 | preserve archive |
| `TSD-004` | Cyclopedia family | completed | PR #359; registry 35 → 39 | preserve archive |
| `TSD-005` | combat, weapons and vocations | completed | PR #362; registry 39 → 41 | preserve archive |
| `TSD-006` | creatures, hunting, raids and bosses | completed | PR #364; registry 41 → 45 | preserve archive |
| `TSD-007` | items and economy | completed | PR #366/#367; registry 45 → 49 | preserve archive |
| `TSD-008` | world content | completed | PR #368/#369; registry 49 → 52 | preserve archive |
| `TSD-009` | social, communication and trust | completed | PR #370/#371; registry 52 → 56 | preserve archive |
| `TSD-010` | protocol and client | completed | PR #372/#373; registry 56 → 60 | preserve archive |
| `TSD-011` | analytics, security and AI | active | PR #374; implementation head `99928c9a0c9bfce9d4fe873ad44f5a5c296995d0`; registry 60 → 61 | finish final exact-head/ready CI, squash merge and lifecycle archive |
| `TSD-012` | validation and live operations | next | OTBM/E2E/UI modules | register only non-duplicative tooling |
| `TSD-013` | Oteryn migration classification | planned | completed inventories/proof packages | classify modules; do not copy code or create another registry |

# Completed delivery evidence

| Package | Feature merge | Lifecycle merge | Registry result |
|---|---|---|---|
| TSD-001 | `44fe3af9f29b3ae0164ac5d60fc1f14137b5cea5` | `cc8b3bdc9b34fb8e6802bd1a0fc0d535de2dd9ba` | 19 → 22 |
| UI-001A prerequisite | `09f7049401253dd38c8f34506946c2fbe287d220` | `6d368766cc47794ec0145b4b32613edaf7588adb` | source registry v1 → v2 |
| TSD-002A | `82f35c0147fdd33c8d4e70d98d003385daf61de6` | `709693b4cca42214c52e63ea15a1a22b93f9a113` | 22 → 26 |
| TSD-002B | `1410a8622aaca5e4afe1bd15aa2695e2dbb7bb94` | `d3dbca52ced28e747f1764167e1d479bd2568a6d` | 26 → 29 |
| TSD-003 | `1098363a708a1f5f875850670a5aad411031e188` | `9f82f93977e82784370961a72104efacd497c8e0` | 29 → 35 |
| TSD-004 | `6d6df89b02fca525ef76011369d8c6243de231d8` | `f163ed8e3b3d51e65c7fef1bc03830b12b2e6bfa` | 35 → 39 |
| TSD-005 | `68b9836cc8e6f55add9a6f3f8d7919e031defc50` | `f68f826915882b0b20081b8fca5ed975ce303f45` | 39 → 41 |
| TSD-006 | `8dfec274b0f460c1f0d6bee6c8a4b95a3ecf8c12` | `821f213038770d68cd95b1b22afa78937b974210` | 41 → 45 |
| TSD-007 | `4932c48d5899ac246404f65e2017a86fc6a5324b` | `350739e5df12db5f3c749540a36bb7c3922cc5ee` | 45 → 49 |
| TSD-008 | `8692347930d86c5411dede46cb90251e5c677d96` | `c68855a0c9ee33d454bb0d6bbab697693578bb0a` | 49 → 52 |
| TSD-009 | `8425845f79d161cb2cd6aab2276aeb39c3616c3e` | `381cc076fa35e138292197f751f26c2e7b89dd08` | 52 → 56 |
| TSD-010 | `9a5f2ee0f1ed95c306876e868109f28848f0ae66` | `c67c84749ffd1de04983be9ae9841b6ca5756aed` | 56 → 60 |

# Current active package — TSD-011

Task: `CAN-20260714-tibia-system-decomposition-analytics-security-ai`; draft PR #374.

Registry 60 → 61. Added only:

```text
gameplay-analytics
```

Existing records modified: 0. Authentication remains `account-authentication`; throttling and account/IP/namelock restrictions remain `sanctions`; `protocol`, `upstream-intelligence`, `otbm-tooling`, `physical-client-e2e`, validation/audit tooling and gameplay records remain stable.

Classification:

- optional Gameplay Analytics telemetry session/queue/retry/dead-letter/dry-run/reporting lifecycle → `gameplay-analytics`;
- password/session-token security remains `account-authentication`;
- throttling and account/IP/namelock restrictions remain `sanctions`;
- `security-analytics`, `chat-safety-intelligence` and `ai-investigation` remain explicitly deferred and unimplemented;
- generic `ai-agent-tooling` remains deferred because it would duplicate heterogeneous validators/OTBM tooling and preempt TSD-012.

Implementation/generated-index head `99928c9a0c9bfce9d4fe873ad44f5a5c296995d0` passed:

- Real Tibia Module Registry #409;
- Upstream Intelligence #445;
- Agent Task Ownership #1273;
- repository CI #2395;
- focused registry/source-role tests;
- registry schema/contracts and dependency graph validation;
- deterministic `generate --check`;
- discovery and affected-module commands.

The earlier `27194fc95a5034705a8667fa1bb148c43955c730` docs attempt exposed generated drift in `MODULE_PATH_INDEX.md` and `STALE_MODULES.md`; both were repaired without changing scope or runtime behavior.

Detailed evidence: `docs/agents/real-tibia/TSD_011_ANALYTICS_SECURITY_AI_REPORT.md`.

No completed package evidence establishes telemetry completeness, metric semantics, queue durability, database transactionality, privacy, retention, production runtime stability, security posture, abuse/anomaly detection, AI investigation capability, physical-client E2E, Real Tibia parity or Oteryn readiness.

# Oteryn migration policy

The legacy repository remains the evidence laboratory. No code is copied to Oteryn by this program. Classification defaults to undecided or `REVALIDATE` until inventory, evidence, runtime proof and E2E proof exist.

# Exact next operational task

After PR #374 passes final exact-head review, ready-state Linux/Required, squash merge and a separate lifecycle archive, re-read then-current `main` and create only:

```text
task: CAN-20260714-tibia-system-decomposition-validation-live-operations
package: TSD-012
branch: docs/tibia-system-decomposition-validation-live-operations
```

Preserve the canonical `otbm-tooling`, `physical-client-e2e`, `upstream-intelligence`, Real Tibia registry and existing validation/audit roots. Register only durable validation or live-operations boundaries with independent current roots that do not duplicate parsers, renderers, mappers, generators, watchers or E2E orchestration.

# Handoff

Continue one task, branch and PR at a time. Re-read current main, open PRs, active tasks and ownership before every package. Preserve all proof limits and never infer behavioral correctness from inventory paths or passing CI.
