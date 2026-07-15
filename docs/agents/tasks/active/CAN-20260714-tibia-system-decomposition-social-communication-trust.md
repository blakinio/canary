---
task_id: CAN-20260714-tibia-system-decomposition-social-communication-trust
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-009
status: active
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition-social-communication-trust
base_branch: main
created: 2026-07-15T01:40:00+02:00
updated: 2026-07-15T10:44:00+02:00
last_verified_commit: "2d04246f583406711b01cdf0468510d72623ade0"
risk: low
related_issue: ""
related_pr: "370"
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
- During preflight, live `main` advanced to `f8deb9fa07488058f6c59ee666e87d9c7f1356a7` through merged protocol/session PR #360.
- PR #370 targets then-current `main`; #360 changed runtime/protocol paths and does not overlap TSD-009 registry/docs/test ownership.
- Remaining open PRs #316 donor-map audit and #245 physical-client E2E are read-only and non-overlapping.
- `ACTIVE_WORK.md` remains read-only.
- Writable repository is only `blakinio/canary`; all upstream repositories remain read-only.

# Delivered implementation inventory

Registry records: 52 → 56. Added only:

- `chat-communication`;
- `guilds`;
- `parties`;
- `sanctions`.

Existing records modified: 0. Account lifecycle/authentication, character lifecycle, NPC, protocol, player/world persistence and all gameplay records remain stable.

# Boundary decision

- `chat-communication`: configured public/private plus runtime party/guild channel registry, membership, invitations and join/leave/speak callbacks.
- `parties`: create/invite/join/leave/leadership/disband plus shared party state lifecycle.
- `guilds`: guild identity/ranks/online membership plus `IOGuild` persistence handoff.
- `sanctions`: connection throttling plus account/IP ban expiry/history and namelock lookup.

Public/private/party/guild chat variants, direct messaging, shared experience and guild wars remain capabilities rather than extra modules. Generic moderation/audit and player-group permission boundaries are deferred without sufficient independent lifecycle evidence. Account authentication/lifecycle, NPC, protocol and persistence remain existing records. Planned `chat-safety-intelligence`, `security-analytics` and `ai-investigation` remain explicitly deferred and unimplemented.

Detailed evidence: `docs/agents/real-tibia/TSD_009_SOCIAL_COMMUNICATION_TRUST_REPORT.md`.

# Validation state

Implementation/focused-test head `2d04246f583406711b01cdf0468510d72623ade0` passed:

- Real Tibia Module Registry #363: success;
- Upstream Intelligence #397: success;
- Agent Task Ownership #1231: success;
- repository CI #2350: success;
- focused registry/source-role tests: success;
- schema and dependency graph validation: success;
- deterministic `generate --check`: success;
- registry discovery integration: success.

The first exact-head registry/UI pass failed only because generated module/dependency/freshness rows placed `chat-communication` before `charms`. The generator's lexical order requires `charms` first. The three indexes were corrected; no module record, dependency, path scope or runtime behavior changed.

This task-record and program update are documentation-only after the validated implementation head. Final current-head checks and ready-state Linux/Required remain mandatory before squash merge.

# Acceptance criteria

- [x] Add only four confirmed records.
- [x] Preserve all existing records unchanged.
- [x] Classify all TSD-009 candidates explicitly.
- [x] Use verified narrow paths and conservative maturity.
- [x] Regenerate deterministic indexes through the existing generator contract.
- [x] Add focused registry and source-role mapping tests.
- [ ] Pass final exact-head registry/UI/ownership/repository CI and ready-state Linux/Required.
- [x] Make no runtime, gameplay, protocol, client, DB, map, OTBM, datapack, asset, workflow or E2E implementation change.

# Safety limits

Inventory does not prove message delivery, privacy, moderation, party sharing, guild persistence, sanction enforcement, audit completeness, runtime behavior, protocol compatibility, Real Tibia parity or Oteryn readiness.

# Handoff

After feature merge, archive this task in a separate lifecycle-only PR. Only after that archive merges may TSD-010 start from then-current `main`.
