---
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
name: Tibia System Decomposition
status: completed
owner: repository-wide
created: 2026-07-14T15:43:00+02:00
updated: 2026-07-15T14:06:39+02:00
last_verified_commit: "e3b08e36c503a36b0eb47696e50567155050c757"
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
| `TSD-011` | analytics, security and AI | completed | PR #374/#376; registry 60 → 61 | preserve archive |
| `TSD-012` | validation and live operations | completed | PR #377/#378; registry 61 → 62 | preserve archive |
| `TSD-013` | Oteryn migration classification | completed | PR #379; merge `e3b08e36c503a36b0eb47696e50567155050c757`; registry remains 62 | preserve archive |

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
| TSD-011 | `dd85d8f886b3e76ec9cc3d3e24c3cb0f7607181c` | `145929ec7f438dc492d4b618a386a4418953d7ec` | 60 → 61 |
| TSD-012 | `81fe5417345c64098e8bb4fd25b27ba234a8406e` | `10d4bf63cf356a3cf912cbc8717854e6a6fd2895` | 61 → 62 |
| TSD-013 | `e3b08e36c503a36b0eb47696e50567155050c757` | lifecycle PR live metadata | 62 → 62 |

# TSD-013 completion evidence

- Feature PR #379, final head `6afa9320385ba8f21660031071d9675bc3c77e94`.
- Squash merge `e3b08e36c503a36b0eb47696e50567155050c757` at `2026-07-15T12:06:39Z`.
- Changed files: 4.
- Registry 62 → 62; records added 0; existing records modified 0; generated indexes modified 0.
- Classification: `ALL_CANONICAL_MODULES -> REVALIDATE`.
- Implementation/classification-head checks: Registry #436, Upstream #472, Ownership #1300 and CI #2424 — success.
- Final-head checks: Registry #438, Upstream #474, Ownership #1302 and CI #2426 — success.
- Ready-state CI #2427: Fast Checks, Lua Tests, Linux release and Required — success.
- Archive: `docs/agents/tasks/archive/CAN-20260714-tibia-system-decomposition-oteryn-migration-classification.md`.

# Final program state

The bounded TSD-001 through TSD-013 queue is complete.

- Canonical registry total: 62 records.
- The registry remains the only module source-of-truth; no second migration registry was created.
- No code was copied to Oteryn.
- No module is declared Oteryn-ready.
- Every canonical module remains `REVALIDATE` for future Oteryn migration decisions.
- `REVALIDATE` is not copy/port/rewrite/drop authorization.
- `cross_repo_contracts` remains empty; a stronger migration disposition requires a new bounded task/program with an explicit Oteryn repository/architecture contract, exact target baseline and module-appropriate target evidence.

# Oteryn migration policy

The legacy repository remains the evidence laboratory. Future Oteryn work must re-read the then-current canonical registry and compare each affected boundary with an explicit target architecture contract. Inventory paths, source-side maturity, compilation and passing CI are not target compatibility or migration-readiness proof.

# Handoff

No further package remains in `CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION`. Preserve all archives and the canonical registry. Any future decomposition extension or Oteryn migration decision must start as a new bounded task/program after fresh live preflight and ownership review.
