---
program_id: CAN-PROGRAM-EQUIPMENT-UPGRADE-PARITY
name: Equipment Upgrade / Exaltation Forge retail parity
status: active
owner: "GPT-5.6 Thinking"
created: 2026-07-13T13:15:00+02:00
updated: 2026-07-13T13:15:00+02:00
last_verified_commit: "3ad10132cbd76adc42f946da3ca3077e5bd6bbd0"
primary_paths:
  - docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md
  - src/creatures/players/player.cpp
  - data/libs/systems/exaltation_forge.lua
  - tests/integration/game/forge_it.cpp
shared_integration_paths:
  - src/server/network/protocol/protocolgame.cpp
  - src/game/functions/forge_transfer_policy.hpp
  - docs/agents/CROSS_REPO_CONTRACTS.md
related_programs:
  - CAN-PROGRAM-E2E-PLATFORM
cross_repo_contracts:
  - Forge result payload and maintained OTClient presentation for F-014 through F-019
---

# Mission

Bring Canary's Equipment Upgrade / Exaltation Forge behavior to evidence-backed parity with the live Tibia rules selected on 2026-07-13, including server authority, resource safety, history, Dust eligibility, effects, result payloads and focused runtime/gameplay proof.

# Scope

- Resolve findings F-001 through F-024 recorded in `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md`.
- Preserve merged repairs from PRs #89, #110 and #177.
- Keep each remediation in a bounded task and PR with focused negative and success-path regression coverage.
- Treat the server as authoritative even when a supported client filters invalid choices.
- Coordinate protocol/result changes with the maintained client before claiming F-014 through F-019 complete.

# Explicit exclusions

- No writes to `opentibiabr/*`.
- No invented rule, probability, reward mapping or rounding formula where the selected live-version evidence is incomplete.
- No all-findings mega-PR.
- No claim of complete parity from compilation, static inspection or aggregate CI alone.
- No modification of the universal E2E platform; feature work may only add a Forge scenario after that platform is merged and reusable.

# Existing systems to reuse

| Module/tool/contract | Source | Required reuse rule |
|---|---|---|
| Forge transfer policy | `src/game/functions/forge_transfer_policy.hpp` | Preserve normal-transfer classification, resource-tier and result-tier behavior from PR #89. |
| Forge history ID resolution | PR #110 and Player Forge history paths | Keep ID-based item identity; later history fixes must not regress it. |
| Dust reward remediation | PR #177 and `data/libs/systems/exaltation_forge.lua` | Preserve direct/summon killer resolution, one shared party roll and capped credited amount. |
| Equipment Upgrade validation report | `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md` | Update finding state only with exact code/test/runtime evidence. |
| Universal E2E platform | `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`, PR #245 | Reuse when merged; do not create Forge-specific orchestration. |
| Canary ↔ OTClient contract registry | `docs/agents/CROSS_REPO_CONTRACTS.md` | Record field order, values, rollout and linked tasks before protocol changes. |

# Active tasks

| Task ID | Branch | PR | State | Exact next action |
|---|---|---:|---|---|
| CAN-20260713-forge-server-authority | `fix/forge-server-authority` | draft pending | active | Enforce F-003–F-005 before mutation and add crafted-request integration regressions. |

# Queue

1. F-003–F-005: server authority for Fusion, Convergence Fusion and Convergence Transfer.
2. F-020–F-021: transactional mutation/rollback for Fusion, Transfer and Sliver-to-Core conversion.
3. F-022–F-024: correct history action types and configurable amounts.
4. F-006 plus runtime proof for F-007/F-008/F-013: exact Premium semantics and Dust recipient/cap/shared-roll scenarios.
5. F-011–F-012: Transcendence/Avatar mutual exclusion and Momentum feedback correctness.
6. F-001–F-002: supported live defaults and boundary tests after authoritative version confirmation.
7. F-014–F-019: versioned bonus contract, server result/history, protocol and maintained OTClient presentation; cross-repository writes require explicit authorization and an atomic rollout plan.
8. F-009–F-010: only after authoritative difficulty/reward and precision/rounding evidence is pinned.
9. Focused runtime, gameplay and physical-client Forge scenarios using the shared E2E platform.

# Completed work

| Task/PR | Result | Merge commit | Follow-up |
|---|---|---|---|
| PR #89 | Normal Transfer rules, donor-tier costs/result and history costs | `209289d38e64aafe7ce3e036867bb632cd0363b8` | Preserve. |
| PR #110 | Forge history item identity by ID | `84f5c09263f459d726fbc7b9f79557b2cbb0801d` | Preserve. |
| PR #177 | Killer resolution, one party Dust roll and actual capped credit | `f1d217c43e8e302978f533212e6aa9d1ce2b77c8` | Runtime proof and Premium remain. |
| PR #242/#244 | Current finding handoff and archived lifecycle record | `56ee9bc72b91ba1110cd6d957c7eb0d974fc54e1` / `88e0140329a91fb877633307d2b749fecb175a43` | Source of truth for the queue. |

# Dependencies and blockers

- The execution container cannot resolve `github.com`; local clone/build/test commands are unavailable. GitHub API writes and current-head CI are separate evidence.
- F-014–F-019 require a maintained OTClient contract and explicit authorization before any cross-repository write.
- F-009/F-010 remain blocked until the selected live-version rule is authoritative enough to encode.

# Decisions and invariants

- Target the live rule set observed on 2026-07-13; pin later rule changes explicitly rather than silently moving the target.
- Validate every client-supplied Forge choice again in C++ before inventory or resource mutation.
- Rejection tests must prove unchanged items, tiers, Dust, cores, money and history.
- One task owns one bounded responsibility; authority, atomicity, history, rewards, effects and protocol/client work stay separate.
- Compilation and generic CI are not focused Forge gameplay proof.

# Validation strategy

- Focused C++ unit/integration tests for each rule and each crafted/stale request.
- Required Linux build, generated Lua API documentation check, Lua/Fast checks and repository ownership validation on every current head.
- Runtime/gameplay tests for reward/effect behavior and real supported-client E2E for protocol/UI parity.
- Record skipped workflow steps and unavailable local checks; never report them as passed.

# Handoff

## Start here

Read `AGENTS.md`, `docs/agents/README.md`, this program record, the current task, open Forge PRs and `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md`.

## Task creation protocol

1. Select one bounded queue item.
2. Recheck current `main`, open PRs and active ownership.
3. Create one task record, branch and draft PR.
4. Declare exact exclusive/shared/read-only paths.
5. Implement, validate, merge, archive the task and update this program.

## Do not repeat

- Do not reopen #177, #241 or #246 or continue their historical branches.
- Do not treat client-side filtering as server authority.
- Do not implement F-009/F-010 from memory or an unversioned secondary summary.
- Do not combine the coordinated bonus/protocol/client program with transactional or history cleanup.

## Open questions

- Exact live difficulty-to-Sliver mapping for F-009.
- Exact live percentage precision/rounding for F-010.
- Authorization and rollout order for maintained `blakinio/otclient` changes required by F-014–F-019.
