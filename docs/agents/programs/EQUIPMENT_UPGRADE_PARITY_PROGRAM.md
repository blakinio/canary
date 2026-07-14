---
program_id: CAN-PROGRAM-EQUIPMENT-UPGRADE-PARITY
name: Equipment Upgrade / Exaltation Forge retail parity
status: paused
owner: unassigned
created: 2026-07-13T13:15:00+02:00
updated: 2026-07-14T18:45:00+02:00
last_verified_commit: "709693b4cca42214c52e63ea15a1a22b93f9a113"
primary_paths:
  - docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md
  - docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_HANDOFF_2026-07-14.md
  - src/creatures/players/player.cpp
  - data/libs/systems/exaltation_forge.lua
  - tests/integration/game/forge_it.cpp
shared_integration_paths:
  - src/server/network/protocol/protocolgame.cpp
  - src/game/functions/forge_fusion_policy.hpp
  - src/game/functions/forge_transfer_policy.hpp
  - src/game/functions/forge_transaction.hpp
  - src/game/functions/forge_effect_policy.hpp
  - docs/agents/CROSS_REPO_CONTRACTS.md
related_programs:
  - CAN-PROGRAM-E2E-PLATFORM
cross_repo_contracts:
  - Forge result payload and maintained OTClient presentation for F-014 through F-019
---

# Mission

Bring Canary's Equipment Upgrade / Exaltation Forge behavior to evidence-backed parity with the selected live Tibia rules, including server authority, resource safety, history, Dust eligibility, effects, result payloads and focused gameplay proof.

# Current lifecycle state

This program is paused with no assigned agent and no active Forge task. The 2026-07-13/14 implementation cycle was archived after all six feature PRs merged.

Paused does **not** mean complete. Server authority, defaults, Premium Dust, effect gating, transaction safety and history correctness are merged. Bonus/result protocol and maintained-client parity, selected reward/rounding evidence and focused physical-client gameplay proof remain open.

# Source of truth

Read in this order:

1. `AGENTS.md` and `docs/agents/README.md`;
2. this program;
3. `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_HANDOFF_2026-07-14.md`;
4. `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md`;
5. archived Forge task records;
6. current `main`, open PRs and active ownership;
7. `docs/agents/CROSS_REPO_CONTRACTS.md` before client/protocol work.

# Completed work

| Findings/scope | PR | Merge commit | Archive |
|---|---:|---|---|
| Normal Transfer baseline | #89 | `209289d38e64aafe7ce3e036867bb632cd0363b8` | preserved dependency |
| History item identity | #110 | `84f5c09263f459d726fbc7b9f79557b2cbb0801d` | preserved dependency |
| Dust killer/party/cap behavior | #177 | `f1d217c43e8e302978f533212e6aa9d1ce2b77c8` | preserved dependency |
| F-003–F-005 server authority | #250 | `94f8a3b63271b3708e33496e937620a6cd4b9717` | `tasks/archive/CAN-20260713-forge-server-authority.md` |
| F-001–F-002 live defaults | #259 | `444aa8ae13edc01c6e77b03139a43d386b437308` | `tasks/archive/CAN-20260713-forge-live-defaults.md` |
| F-011–F-012 effects | #267 | `7771bbec22d970d9779bff740e3f7f2e0df42f19` | `tasks/archive/CAN-20260713-forge-effect-correctness.md` |
| F-020–F-021 transaction safety | #257 | `e16c9f769b1bcdd05e1719e861f0a52cc2594560` | `tasks/archive/CAN-20260713-forge-transaction-safety.md` |
| F-006 Premium Dust | #262 | `ded1830b143388d65c895ad30918faf128df66ed` | `tasks/archive/CAN-20260713-forge-premium-dust.md` |
| F-022–F-024 history correctness | #283 | `82348f9faca788a8cbb5c13feb75b4e06d8da9dc` | `tasks/archive/CAN-20260713-forge-history-correctness.md` |

# Preserved invariants

- Validate every client-supplied Forge choice again in C++ before mutation.
- Normal Fusion requires distinct instances of the same item ID and requested tier.
- Convergence Fusion requires different class-4 item IDs, matching requested tier and normalized slot.
- Convergence Transfer requires class 4.
- Active imbuements remain disallowed.
- Fusion, Transfer and Sliver-to-Core mutations are transactional.
- History and result packets occur only after successful commit.
- Dust eligibility delegates to exact C++ Premium semantics.
- One death uses one shared Dust roll and cap-aware actual credit.
- Either Avatar source blocks Transcendence.
- Momentum feedback requires an actual eligible cooldown reduction.
- Distributed defaults are Dust `325` and Fiendish `4`, while server-owner overrides remain supported.

# Remaining queue

## Next — F-014 through F-019 contract audit

Create one bounded evidence/contract task before changing code:

- map all server bonus enum values and selection gates;
- pin the missing Dust-refill bonus behavior;
- verify `+2 tier` maximum-tier handling;
- define tier-aware bonus eligibility;
- map Fusion result/history state;
- map exact packet field order and values;
- inspect maintained OTClient decoding and UI presentation;
- record compatibility and rollout order in `docs/agents/CROSS_REPO_CONTRACTS.md`.

Do not modify another repository without explicit authorization. Do not change protocol bytes until the server and maintained-client contract is documented.

## Runtime/gameplay evidence

- F-007: party/logout/combat-block scenario;
- F-008: actual credited amount at Dust cap;
- F-013: one roll shared across direct, summon and party paths.

Reuse PR #177/#262 behavior unless a focused scenario reproduces a defect.

## Evidence-blocked rules

- F-009: exact difficulty-to-Sliver mapping;
- F-010: exact percentage precision and rounding.

Pin authoritative, versioned evidence before implementation. Do not infer from memory or an unversioned secondary summary.

## Physical-client proof

Reuse the universal E2E platform after it is merged and stable. Add only a Forge scenario and assertions; do not copy or modify platform orchestration from a feature task.

# Dependencies and blockers

- Maintained-client/protocol work requires explicit cross-repository authorization and rollout planning.
- F-009/F-010 lack sufficient authoritative selected-version evidence.
- Aggregate CI is not physical-client gameplay proof.
- Recheck current open PR #245 and the E2E program before adding a Forge scenario.

# Exact next task

```text
task: CAN-YYYYMMDD-forge-bonus-result-contract
branch: docs/forge-bonus-result-contract
scope: evidence and Canary ↔ maintained-OTClient contract for F-014 through F-019
```

The task must begin from then-current `main`, inspect active ownership and open PRs, and stay documentation/evidence-first until the contract is complete.

# Do not repeat

- Do not reopen completed Forge feature PRs #250, #257, #259, #262, #267 or #283.
- Do not continue helper PRs #252, #253, #254, #258, #260, #266, #268, #269, #270, #271, #280, #281 or #284.
- Do not bypass the merged policy/transaction helpers.
- Do not treat client-side filtering as server authority.
- Do not claim full parity from compilation or generic runtime smoke.
- Do not implement F-009/F-010 without pinned evidence.
- Do not combine reward mapping, rounding, bonus rules, protocol and client UI into one unbounded PR.

# Handoff

The previous agent cycle is archived. A new agent must create a fresh bounded active task and draft PR before editing. No active path ownership from the archived tasks remains.
