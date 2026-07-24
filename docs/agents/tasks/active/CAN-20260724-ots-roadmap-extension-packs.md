---
task_id: CAN-20260724-ots-roadmap-extension-packs
program_id: CAN-PROGRAM-OTS-FUTURE-GAMEPLAY-SYSTEMS
coordination_id: OTS-ROADMAP-EXTENSION-PACKS
status: in_progress
agent: "GPT-5.6 Thinking"
branch: docs/ots-roadmap-extension-packs-20260724
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: ""
risk: low
related_issue: ""
related_pr: "887"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-ots-roadmap-extension-packs.md
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_EXTENSION_PACKS.md
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md
  shared: []
  read_only:
    - docs/ai-agent/OTS_CHARM_BESTIARY_AND_DROME_MASTERY.md
    - docs/ai-agent/OTS_QUEST_JOURNAL_POSTAL_AND_MARKET_LOGISTICS.md
    - docs/ai-agent/OTS_FORGE_SLOT_ITEM_ENHANCEMENT_AND_EQUIPMENT_PROFICIENCY.md
modules_touched:
  - OTS future gameplay roadmap
  - OTS gameplay proposal classification
reuses:
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md
  - docs/ai-agent/OTS_CHARM_BESTIARY_AND_DROME_MASTERY.md
  - docs/ai-agent/OTS_QUEST_JOURNAL_POSTAL_AND_MARKET_LOGISTICS.md
  - docs/ai-agent/OTS_FORGE_SLOT_ITEM_ENHANCEMENT_AND_EQUIPMENT_PROFICIENCY.md
public_interfaces: []
cross_repo_tasks: []
---

# OTS roadmap extension-pack integration

## Goal

Promote the three already-merged future-design packages into the authoritative proposal index without collapsing their distinct sub-systems into three ambiguous umbrella entries:

1. Charm, Bestiary and Drome Mastery;
2. Quest Journal, Postal Network and Market Logistics;
3. Forge Slot Mastery, Item Enhancement and Equipment Proficiency.

## Scope

Documentation and classification only. No runtime, client, protocol, datapack, map, item, economy configuration or production behavior changes.

## Acceptance criteria

- [x] Preserve the three existing detailed design documents unchanged.
- [x] Add a concise integrated roadmap addendum with practical `FEATURE`, `UPGRADE` and `FIX` labels.
- [ ] Extend the authoritative classification after entry 94 with distinct proposal entries and explicit `ORIGIN` / `TYPE` labels.
- [x] Avoid duplicating existing entry 4 (`Account-wide quest progression`) or official Weapon Proficiency.
- [x] Keep illustrative formulas, costs, caps and migration rules explicitly non-final.
- [ ] Pass exact-final Agent Task Ownership and CI.
- [ ] Mark ready and squash-merge through repository protection.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24
head: ""
branch: docs/ots-roadmap-extension-packs-20260724
pr: 887
status: implementing
context_routes:
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-ots-roadmap-extension-packs.md
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_EXTENSION_PACKS.md
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md
proven:
  - The three detailed design documents are already merged on main.
  - The authoritative classification currently ends at entry 94.
  - PR 884 merged as ad8b978236e6dfa8c40b06170f19f281b84b395d and released ownership of the central roadmap/classification paths.
  - Account-wide quest progression already exists as classification entry 4 and is not duplicated.
  - Weapon Proficiency is an official Tibia system and is not relabeled as an OTS-original feature.
  - PR 887 contains the integrated extension-pack addendum and no runtime, map, datapack, protocol or client-binary changes.
derived:
  - The new packages require multiple proposal-level entries because they contain independent features, upgrades and safeguards.
unknown:
  - Exact current implementation parity for each future package remains outside this documentation-only task.
conflicts: []
first_failure: null
rejected_hypotheses:
  - Add only three umbrella classification rows and hide all distinct sub-systems inside them.
  - Duplicate account-wide quest progression as a new proposal.
  - Treat Equipment Proficiency as a replacement for official Weapon Proficiency.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-ots-roadmap-extension-packs.md
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_EXTENSION_PACKS.md
validation:
  - command: source-design review
    result: PASS
    evidence: New addendum is derived only from the three merged detailed design records.
blockers: []
next_action: Append classification entries 95-120, review the exact diff, update the final checkpoint, apply ci:final-gate and validate the exact final head.
```
