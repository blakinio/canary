---
task_id: CAN-20260714-tibia-system-decomposition-protocol-client
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-010
status: active
agent: "GPT-5.5 Thinking"
branch: docs/tibia-system-decomposition-protocol-client
base_branch: main
created: 2026-07-15T11:11:00+02:00
updated: 2026-07-15T11:23:00+02:00
last_verified_commit: "f0c92d68cd3025d66214de4b5108cd8c0e5fcbba"
risk: low
related_issue: ""
related_pr: "372"
depends_on:
  - completed and archived TSD-009
blocks:
  - TSD-011 analytics security and AI decomposition
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260714-tibia-system-decomposition-protocol-client.md
    - docs/agents/real-tibia/TSD_010_PROTOCOL_CLIENT_REPORT.md
    - docs/agents/real-tibia/registry/modules/network-transport.yaml
    - docs/agents/real-tibia/registry/modules/login-protocol.yaml
    - docs/agents/real-tibia/registry/modules/protocol-compatibility.yaml
    - docs/agents/real-tibia/registry/modules/protocol-session-handoff.yaml
    - tools/agents/test_protocol_client_registry.py
    - tools/agents/test_upstream_intelligence_protocol_client.py
  shared:
    - docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
    - docs/agents/real-tibia/generated/**
    - tools/agents/test_social_registry.py
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/real-tibia/registry/modules/protocol.yaml
    - docs/agents/real-tibia/registry/modules/physical-client-e2e.yaml
    - docs/agents/real-tibia/registry/modules/account-authentication.yaml
    - docs/agents/real-tibia/registry/modules/player-persistence.yaml
    - tools/agents/real_tibia_registry*.py
    - tools/agents/upstream_intelligence*.py
    - .github/workflows/**
    - src/server/network/connection/**
    - src/server/network/protocol/**
    - tests/unit/server/network/**
    - tests/integration/**
modules_touched:
  - Real Tibia module registry
  - network transport
  - login protocol
  - protocol compatibility profiles
  - protocol session handoff
reuses:
  - existing registry/generator/mapper
  - existing protocol umbrella
  - existing physical-client E2E platform
public_interfaces:
  - bounded transport/login/compatibility/session-handoff discovery records
cross_repo_tasks: []
---

# Goal

Complete bounded TSD-010 protocol and client inventory. Preserve the current broad `protocol` umbrella, physical-client E2E platform, account authentication/session cleanup and all gameplay records. Add only durable transport, login-protocol, compatibility-profile and protocol-session-handoff boundaries supported by verified current Canary and maintained OTClient roots.

# Exact base and preflight

- Task-start live main: `381cc076fa35e138292197f751f26c2e7b89dd08`.
- TSD-009 feature PR #370 and lifecycle PR #371 are both squash-merged before this task.
- Open PRs #316 donor-map audit and #245 physical-client E2E remain read-only and non-overlapping with this task's registry/docs/focused-test ownership.
- `ACTIVE_WORK.md` remains read-only.
- Writable repository is only `blakinio/canary`.
- Read-only upstream server baseline: `opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689`.
- Read-only maintained-client baseline: `opentibiabr/otclient@bdea0b23b4a738809d698cb7e4f88a299dd6bffc`.

# Delivered implementation inventory

Registry records: 56 → 60. Added only:

- `login-protocol`;
- `network-transport`;
- `protocol-compatibility`;
- `protocol-session-handoff`.

Existing records modified: 0. The broad `protocol` record and its existing maturity remain unchanged. Physical-client E2E, account authentication/lifecycle, character lifecycle, player persistence and all gameplay records remain stable.

# Boundary decision

- `network-transport`: connection/socket/framing/checksum/sequence/XTEA/compression and connection-scoped protocol release lifecycle.
- `login-protocol`: account-login wire request/response, client/profile selection, session-key and character/world-list phase around the existing authentication boundary.
- `protocol-compatibility`: server version/wire/assets/layout/feature profiles plus maintained-client version-gated feature matrix.
- `protocol-session-handoff`: bounded login-to-game protocol-profile hint register/lease/consume/expiry state.
- `game-protocol`: already covered by the broad `protocol` umbrella.
- `game-session`: merged/deferred because server/client roots remain intertwined with `ProtocolGame`, transport and client `Game` state.
- connection/session release coordination remains `network-transport`; leave-game semantics remain `protocol`.
- individual opcodes, feature flags and client modules remain capabilities or too granular unless already owned by gameplay modules.

Detailed evidence: `docs/agents/real-tibia/TSD_010_PROTOCOL_CLIENT_REPORT.md`.

# Validation state

Implementation/focused-test head `f0c92d68cd3025d66214de4b5108cd8c0e5fcbba` includes:

- four new inventory-only registry records;
- deterministic module/dependency/path/freshness generated indexes;
- exact TSD-010 registry total assertion and TSD-009 minimum-total regression adjustment;
- focused server/client path discovery tests;
- focused Upstream Intelligence source-role isolation tests;
- unchanged broad `protocol` maturity assertions.

Exact-head Real Tibia Module Registry, Upstream Intelligence, Agent Task Ownership and repository CI are authoritative and still pending for the current docs-only head. `generate --check` must pass before readiness. Ready-state Linux/Required remains mandatory before squash merge.

# Acceptance criteria

- [x] Add only four independently supported protocol/client records.
- [x] Preserve the existing `protocol` record unchanged.
- [x] Preserve physical-client E2E and account-authentication ownership unchanged.
- [x] Classify wire, session and client-feature candidates explicitly.
- [x] Use verified narrow server/client paths and conservative maturity.
- [x] Materialize deterministic indexes through the existing generator contract; `generate --check` remains authoritative.
- [x] Add focused registry and source-role mapping tests.
- [ ] Pass exact-head registry/UI/ownership/repository CI and ready-state Linux/Required.
- [x] Make no runtime, gameplay, protocol implementation, client, DB, map, OTBM, datapack, asset, workflow or E2E implementation change.

# Safety limits

Inventory does not prove packet layout equivalence, handshake correctness, encryption/checksum/sequence compatibility, session handoff correctness, malformed-input safety, maintained-client interoperability, physical-client E2E, Real Tibia parity or Oteryn readiness.

A matching parser, serializer, class name, compile result or unit test is not wire compatibility evidence.

# Handoff

After feature merge, archive this task in a separate lifecycle-only PR. Only after that archive merges may TSD-011 start from then-current `main`.
