---
task_id: CAN-20260723-ots-social-itemization-qol-roadmap
program_id: CAN-PROGRAM-OTS-FUTURE-GAMEPLAY-SYSTEMS
coordination_id: OTS-SOCIAL-ITEMIZATION-QOL
status: review
agent: "GPT-5.6 Thinking"
branch: docs/ots-social-itemization-qol-20260723
base_branch: main
created: 2026-07-23T15:31:47+02:00
updated: 2026-07-24T17:02:00+02:00
last_verified_commit: "a17581fa41658f36a420bfc256fa39740f5c482d"
risk: low
related_issue: ""
related_pr: "799"
depends_on: []
blocks:
  - "PR #843 vocation-balance guidance reconciliation"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-ots-social-itemization-qol-roadmap.md
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md
    - docs/ai-agent/OTS_SOCIAL_ITEMIZATION_AND_QOL_SYSTEMS.md
    - docs/ai-agent/OTS_VOCATION_ROLE_AND_BALANCE_FRAMEWORK.md
    - docs/ai-agent/OTS_GEM_ATELIER_AND_GEM_PROGRESSION_REVIEW.md
  shared: []
  read_only:
    - docs/ai-agent/OTS_FORGE_SLOT_ITEM_ENHANCEMENT_AND_EQUIPMENT_PROFICIENCY.md
modules_touched:
  - OTS future gameplay roadmap
  - OTS gameplay proposal classification
  - OTS vocation/class role and balance framework
  - OTS Gem Atelier and gem progression review
reuses:
  - Character markers on minimap
  - Better Map UX
  - Party Finder 2.0
  - Loot System Rework
  - Equipment Presets
  - Financial & Trading System 2.0
  - Bounty and Weekly Tasks Rework
  - official Tibia Gem Atelier / Fragment Workshop foundation
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260723 — OTS Social, Itemization and QoL Roadmap

## Status

REVIEW — the approved social, itemization, QoL, vocation-role and Gem Atelier directions are persisted and classified. The stale ownership that previously blocked this PR was removed by merged lifecycle PR #878. No further feature-content commit is required; exact-final checks on the current task-checkpoint head are the remaining merge gate.

## Goal

Persist the approved future OTS directions for world/social map UX, consent-aware contacts, Party System 2.0, build/itemization tooling, inventory/storage, market/trade, Imbuement System 2.0, vocation/class identity and balance, and Gem Atelier / Fragment Workshop parity and balance review.

## Scope

Documentation/design only. No gameplay runtime, protocol, datapack, map, binary, economy configuration, client binary or production behavior changes.

## Acceptance criteria

- [x] Record the approved social/itemization/QoL directions in a detailed design file.
- [x] Integrate concise sections 29–35 into `OTS_FUTURE_GAMEPLAY_SYSTEMS.md`.
- [x] Extend the authoritative classification from entries 69–94 with explicit `ORIGIN` / `TYPE` labels.
- [x] Add the Vocation/Class Identity, Roles and Balance Framework.
- [x] Add the Gem Atelier / Fragment Workshop review grounded in current official Tibia evidence.
- [x] Keep current Canary/OTClient support unproven until a dedicated audit.
- [x] Preserve open balance questions rather than invent final numeric contracts.
- [x] Remove stale ownership conflicts through merged PR #878 without changing this feature scope.
- [x] Keep all changes documentation-only.
- [ ] Pass exact-final Agent Task Ownership, AI Agent Tools and CI.
- [ ] Mark ready and squash-merge through repository protection.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T17:02:00+02:00
head: a17581fa41658f36a420bfc256fa39740f5c482d
branch: docs/ots-social-itemization-qol-20260723
pr: 799
status: validating
context_routes:
  - agent-governance
  - real-tibia-parity
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-ots-social-itemization-qol-roadmap.md
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md
  - docs/ai-agent/OTS_SOCIAL_ITEMIZATION_AND_QOL_SYSTEMS.md
  - docs/ai-agent/OTS_VOCATION_ROLE_AND_BALANCE_FRAMEWORK.md
  - docs/ai-agent/OTS_GEM_ATELIER_AND_GEM_PROGRESSION_REVIEW.md
proven:
  - The roadmap branch contains exactly six intended documentation/task paths and no runtime, map, datapack, protocol or client-binary changes.
  - `OTS_SOCIAL_ITEMIZATION_AND_QOL_SYSTEMS.md` records the approved world/social map, consent/privacy, Party 2.0, party visibility/accounting, build, Training Arena, inventory/storage, market/trade and Imbuement 2.0 directions.
  - `OTS_VOCATION_ROLE_AND_BALANCE_FRAMEWORK.md` defines class identity contracts, role taxonomy, solo/party viability, target bands, context-separated balance, telemetry and governance without inventing final values.
  - `OTS_GEM_ATELIER_AND_GEM_PROGRESSION_REVIEW.md` treats Gem Atelier and Fragment Workshop as official Tibia foundations requiring Canary/OTClient parity and balance audit.
  - `OTS_FUTURE_GAMEPLAY_SYSTEMS.md` contains concise sections 29–35 and the related dependency-map extension.
  - `OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md` preserves entries 1–68 and adds entries 69–94.
  - Earlier CI and AI Agent Tools passed on feature head a17581fa41658f36a420bfc256fa39740f5c482d.
  - PR 878 merged as 2a39c71355f43910a34eb4b1275987ddadb31d6d and archived four completed roadmap tasks that had retained stale active ownership.
  - PR 823 was closed without merge because it contained only a blocked checkpoint and no supported Paladin supplement deliverable.
derived:
  - The vocation/class framework is the upstream design dependency for later Party, itemization, Imbuement, build-calculator, Training Arena and vocation-balance work.
  - Gem Atelier cannot be balanced independently from Wheel/Revelation progression, vocation identity, build tooling and economy sinks.
  - Open detailed equipment-progression design remains a separate document and requires responsibility mapping before implementation.
unknown:
  - Exact current Tibia/Canary/OTClient parity for every Imbuement, Gem Atelier and vocation detail.
  - Exact per-vocation role assignments and numeric target bands.
  - Exact privacy/PvP information-leak rules for live social tracking.
  - Exact market alternative-currency legal, accounting, protocol and abuse constraints.
  - Exact party accounting settlement mechanism.
conflicts: []
first_failure:
  marker: stale-active-ownership
  evidence: Agent Task Ownership run 30017932223 failed while already-merged PRs 664, 667, 674 and 772 still retained active ownership over roadmap paths; PR 878 removed those stale records.
rejected_hypotheses:
  - Create a parallel Party Finder instead of extending the existing direction.
  - Treat Gem Atelier as an OTS-original system.
  - Force identical DPS or a rigid tank/healer/DPS trinity across all content.
  - Treat narrow code-search absence as proof that Canary or OTClient lacks Gem Atelier support.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-ots-social-itemization-qol-roadmap.md
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md
  - docs/ai-agent/OTS_SOCIAL_ITEMIZATION_AND_QOL_SYSTEMS.md
  - docs/ai-agent/OTS_VOCATION_ROLE_AND_BALANCE_FRAMEWORK.md
  - docs/ai-agent/OTS_GEM_ATELIER_AND_GEM_PROGRESSION_REVIEW.md
validation:
  - command: feature-content and classification review
    result: PASS
    evidence: Existing entries 1–68 are preserved; intended additions are roadmap sections 29–35 and classification entries 69–94.
  - command: official Gem Atelier / Fragment Workshop evidence review
    result: PASS
    evidence: The recorded official foundation is separated from unknown Canary/OTClient implementation support and any later custom changes.
  - command: stale ownership lifecycle cleanup
    result: PASS
    evidence: PR 878 merged and released the four completed roadmap task claims.
  - command: exact-final Agent Task Ownership, AI Agent Tools and CI
    result: NOT_RUN
    evidence: Required workflows must run on the final checkpoint commit after ci:final-gate was applied.
blockers: []
next_action: Require exact-final checks, inspect reviews/threads, mark PR 799 ready and squash-merge with expected head if all gates pass.
```
