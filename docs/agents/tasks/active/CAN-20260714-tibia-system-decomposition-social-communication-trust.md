---
task_id: CAN-20260714-tibia-system-decomposition-social-communication-trust
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-009
status: active
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition-social-communication-trust
base_branch: main
created: 2026-07-15T01:40:00+02:00
updated: 2026-07-15T01:40:00+02:00
last_verified_commit: "c68855a0c9ee33d454bb0d6bbab697693578bb0a"
risk: low
related_issue: ""
related_pr: ""
depends_on:
  - completed and archived TSD-008
blocks:
  - TSD-010 protocol and client decomposition
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260714-tibia-system-decomposition-social-communication-trust.md
    - docs/agents/real-tibia/TSD_009_SOCIAL_COMMUNICATION_TRUST_REPORT.md
    - docs/agents/real-tibia/registry/modules/chat-communication.yaml
    - docs/agents/real-tibia/registry/modules/parties.yaml
    - docs/agents/real-tibia/registry/modules/guilds.yaml
    - docs/agents/real-tibia/registry/modules/sanctions.yaml
    - tools/agents/test_social_registry.py
    - tools/agents/test_upstream_intelligence_social.py
  shared:
    - docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
    - docs/agents/real-tibia/generated/**
    - tools/agents/test_world_registry.py
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/real-tibia/registry/modules/account-authentication.yaml
    - docs/agents/real-tibia/registry/modules/account-lifecycle.yaml
    - docs/agents/real-tibia/registry/modules/npcs.yaml
    - docs/agents/real-tibia/registry/modules/protocol.yaml
    - docs/agents/real-tibia/registry/modules/player-persistence.yaml
    - docs/agents/real-tibia/registry/modules/world-persistence.yaml
    - tools/agents/real_tibia_registry*.py
    - tools/agents/upstream_intelligence*.py
    - .github/workflows/**
    - src/creatures/interactions/chat.*
    - src/creatures/players/grouping/party.*
    - src/creatures/players/grouping/guild.*
    - src/creatures/players/management/ban.*
    - src/io/ioguild.*
    - data/chatchannels/**
    - tests/**
modules_touched:
  - Real Tibia module registry
  - chat communication
  - parties
  - guilds
  - sanctions
reuses:
  - existing registry/generator/mapper
public_interfaces:
  - bounded social and trust discovery records
cross_repo_tasks: []
---

# Goal

Complete bounded TSD-009 social, communication and trust inventory. Preserve account lifecycle/authentication, NPC, protocol and persistence records. Add only durable chat-channel, party, guild and sanction lifecycles supported by verified current paths.

# Exact base and preflight

- Task-start main: `c68855a0c9ee33d454bb0d6bbab697693578bb0a`.
- TSD-008 feature/lifecycle were merged first.
- Open PRs #360 protocol/session, #316 donor-map audit and #245 physical-client E2E remain read-only and non-overlapping.
- `ACTIVE_WORK.md` remains read-only.

# Boundary decision

- `chat-communication`: public/private/party/guild channel registry, membership, invitations and speak callbacks.
- `parties`: invite/join/leave/leadership/shared-experience/status/analyzer lifecycle.
- `guilds`: guild membership, rank, online member, MOTD, bank and persistence handoff lifecycle.
- `sanctions`: connection throttling, IP/account ban and namelock lookup lifecycle.

Direct messaging, channel moderation scripts and guild/party protocol packets remain capabilities of these records or `protocol`. Account authentication/lifecycle and persistence remain existing records. Repository/content audit tooling is not a gameplay trust module and is deferred to tooling packages.

# Acceptance criteria

- [ ] Add only four confirmed records.
- [ ] Preserve all existing records unchanged.
- [ ] Classify all TSD-009 candidates explicitly.
- [ ] Use verified narrow paths and conservative maturity.
- [ ] Regenerate deterministic indexes through the existing generator.
- [ ] Add focused registry and source-role mapping tests.
- [ ] Pass exact-head registry/UI/ownership/repository CI and ready-state Linux/Required.
- [ ] Make no runtime, gameplay, protocol, client, DB, map, OTBM, datapack, asset, workflow or E2E implementation change.

# Safety limits

Inventory does not prove message delivery, privacy, moderation, party sharing, guild persistence, sanction enforcement, audit completeness, runtime behavior or parity.

# Handoff

After feature merge, archive this task in a separate lifecycle-only PR. Only after that archive merges may TSD-010 start from then-current `main`.