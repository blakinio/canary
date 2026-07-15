---
task_id: CAN-20260714-tibia-system-decomposition-protocol-client
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-010
status: active
agent: "GPT-5.5 Thinking"
branch: docs/tibia-system-decomposition-protocol-client
base_branch: main
created: 2026-07-15T11:11:00+02:00
updated: 2026-07-15T11:12:00+02:00
last_verified_commit: "381cc076fa35e138292197f751f26c2e7b89dd08"
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

# Evidence baseline

Current Canary separates:

- `Connection`, base `Protocol` and `TransportCodec` framing/connection/crypto/checksum/compression and release lifecycle;
- `ProtocolLogin` account-login request/response, profile resolution, session-key handoff and character-list phase;
- `ProtocolProfileRegistry` version/assets/wire-family/transport/layout/feature compatibility metadata;
- `ProtocolSessionHintStore` bounded register → lease → consume/resolve → expire/clear state bridging account-login profile knowledge into the game connection without owning authentication.

Maintained OTClient separately exposes:

- base `framework/net/Protocol` connection, checksum, sequence, XTEA and compression state;
- `modules/gamelib/ProtocolLogin` account-login packet/character-list/session-key phase;
- `modules/game_features` version-gated client feature matrix.

The monolithic server/client `ProtocolGame` packet router and game state remain under the existing broad `protocol` umbrella unless a narrower independent lifecycle root is proven. A parser implementation or matching class name is not wire-compatibility proof.

# Candidate classification under review

- `network-transport` — candidate `ADD_NOW`;
- `login-protocol` — candidate `ADD_NOW`;
- `protocol-compatibility` — candidate `ADD_NOW`;
- `protocol-session-handoff` — candidate `ADD_NOW` based on independent TTL/lease/consume lifecycle;
- `game-protocol` — preserve existing `protocol` umbrella;
- `game-session` — merge/defer because current server/client roots are intertwined with the monolithic `ProtocolGame` packet router and client `Game` state;
- individual opcodes/features/client modules — reject as too granular unless already covered by existing gameplay modules.

# Acceptance criteria

- [ ] Add only independently supported protocol/client records.
- [ ] Preserve the existing `protocol` record unchanged.
- [ ] Preserve physical-client E2E and account-authentication ownership unchanged.
- [ ] Classify wire, session and client-feature candidates explicitly.
- [ ] Use verified narrow server/client paths and conservative maturity.
- [ ] Regenerate deterministic indexes through the existing generator contract.
- [ ] Add focused registry and source-role mapping tests.
- [ ] Pass exact-head registry/UI/ownership/repository CI and ready-state Linux/Required.
- [ ] Make no runtime, gameplay, protocol implementation, client, DB, map, OTBM, datapack, asset, workflow or E2E implementation change.

# Safety limits

Inventory does not prove packet layout equivalence, handshake correctness, encryption/checksum/sequence compatibility, session handoff correctness, malformed-input safety, maintained-client interoperability, physical-client E2E, Real Tibia parity or Oteryn readiness.

# Handoff

After feature merge, archive this task in a separate lifecycle-only PR. Only after that archive merges may TSD-011 start from then-current `main`.
