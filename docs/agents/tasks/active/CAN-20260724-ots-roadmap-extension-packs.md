---
task_id: CAN-20260724-ots-roadmap-extension-packs
program_id: CAN-PROGRAM-OTS-FUTURE-GAMEPLAY-SYSTEMS
coordination_id: OTS-ROADMAP-EXTENSION-PACKS
status: review
agent: "GPT-5.6 Thinking"
branch: docs/ots-roadmap-extension-packs-20260724
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "7dbd7c34e6cff2b2b4c6dc5de86b9afb3ced7698"
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
- [x] Extend the authoritative classification after entry 94 with distinct proposal entries and explicit `ORIGIN` / `TYPE` labels.
- [x] Avoid duplicating existing entry 4 (`Account-wide quest progression`) or official Weapon Proficiency.
- [x] Keep illustrative formulas, costs, caps and migration rules explicitly non-final.
- [ ] Pass exact-final Agent Task Ownership, AI Agent Tools and CI.
- [ ] Mark ready and squash-merge through repository protection.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24
head: 7dbd7c34e6cff2b2b4c6dc5de86b9afb3ced7698
branch: docs/ots-roadmap-extension-packs-20260724
pr: 887
status: validating
context_routes:
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-ots-roadmap-extension-packs.md
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_EXTENSION_PACKS.md
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md
proven:
  - The three detailed design documents are already merged on main and remain unchanged by this PR.
  - PR 884 merged as ad8b978236e6dfa8c40b06170f19f281b84b395d and released ownership of the central roadmap/classification paths.
  - The authoritative classification contains entries 95-120 derived from the three merged detailed designs.
  - Account-wide quest progression remains entry 4 and is not duplicated.
  - Weapon Proficiency remains explicitly official and separate from proposed Equipment Proficiency.
  - PR 887 changes exactly the task record, the classification index and the integrated extension-pack addendum.
  - Agent Task Ownership run 30113143226 passed on pre-final head 7dbd7c34e6cff2b2b4c6dc5de86b9afb3ced7698.
  - AI Agent Tools run 30113143239 passed on pre-final head 7dbd7c34e6cff2b2b4c6dc5de86b9afb3ced7698.
  - CI run 30113143401 passed on pre-final head 7dbd7c34e6cff2b2b4c6dc5de86b9afb3ced7698.
  - The ci:final-gate label was applied before this final checkpoint commit.
derived:
  - The new packages require multiple proposal-level entries because they contain independent features, upgrades and safeguards.
unknown:
  - Exact current implementation parity for each future package remains outside this documentation-only task.
conflicts: []
first_failure:
  marker: checkpoint-schema
  evidence: Early ownership validation exposed invalid guessed frontmatter values; the task now follows repository-defined review/validating lifecycle compatibility.
rejected_hypotheses:
  - Add only three umbrella classification rows and hide all distinct sub-systems inside them.
  - Duplicate account-wide quest progression as a new proposal.
  - Treat Equipment Proficiency as a replacement for official Weapon Proficiency.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-ots-roadmap-extension-packs.md
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_EXTENSION_PACKS.md
validation:
  - command: source-design review
    result: PASS
    evidence: Entries 95-120 and the addendum are derived only from the three merged detailed design records.
  - command: changed-file and full-diff review
    result: PASS
    evidence: The PR changes exactly three documentation/task paths and no runtime, client, protocol, map, datapack or production files.
  - command: pre-final Agent Task Ownership, AI Agent Tools and CI
    result: PASS
    evidence: Runs 30113143226, 30113143239 and 30113143401 passed on head 7dbd7c34e6cff2b2b4c6dc5de86b9afb3ced7698.
blockers: []
next_action: Require exact-final Agent Task Ownership, AI Agent Tools and CI on the final checkpoint head; if green and review threads are clear, mark PR 887 ready and squash-merge without further commits.
```
