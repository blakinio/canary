---
task_id: CAN-20260723-ots-quest-journal-postal-market-logistics
program_id: CAN-PROGRAM-OTS-FUTURE-GAMEPLAY-SYSTEMS
coordination_id: OTS-QUEST-JOURNAL-POSTAL-MARKET
status: review
agent: "GPT-5.6 Thinking"
branch: docs/quest-journal-postal-market-logistics-20260723
base_branch: main
created: 2026-07-23
updated: 2026-07-24
last_verified_commit: "eee8b36961c1c847f45c9b444eb995b4fea2c1ce"
risk: low
related_issue: ""
related_pr: "789"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-ots-quest-journal-postal-market-logistics.md
    - docs/ai-agent/OTS_QUEST_JOURNAL_POSTAL_AND_MARKET_LOGISTICS.md
  shared: []
  read_only:
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md
modules_touched:
  - future-gameplay-product-design
  - quest-journal-postal-market-design
reuses:
  - existing Tibia quest, mail and market foundations as implementation-time baselines
public_interfaces: []
cross_repo_tasks: []
---

# Quest Journal, Postal Network and Market Logistics design

## Goal

Preserve the future design for Quest Journal 2.0, explicit quest dependencies, Party Quest Sync, selective account-wide access, postal services and bounded market logistics.

## Acceptance criteria

- [x] Preserve Campaign-to-Objective hierarchy, blockers, history, breadcrumbs and Current Objective UX.
- [x] Preserve Party Quest Sync and selective account-wide progression boundaries.
- [x] Preserve postal item delivery, COD, insurance/tracking and market-logistics direction.
- [x] Preserve legacy rewards and avoid blindly copying fully isolated city markets.
- [x] Make no runtime, quest, mail, market, datapack, client or map changes.
- [ ] Pass exact-final Agent Task Ownership and CI on the current PR head.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T16:52:00+02:00
head: eee8b36961c1c847f45c9b444eb995b4fea2c1ce
branch: docs/quest-journal-postal-market-logistics-20260723
pr: 789
status: validating
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-ots-quest-journal-postal-market-logistics.md
  - docs/ai-agent/OTS_QUEST_JOURNAL_POSTAL_AND_MARKET_LOGISTICS.md
proven:
  - The detailed design document is the only product-design file introduced by the original PR head.
  - The document explicitly states that it is a proposal and not a claim about current Tibia or Canary behavior.
  - Implementation is staged through a representative quest pilot rather than broad migration.
derived:
  - Quest, mail and market are Tibia foundations, while the structured journal, sync, renown, modern postal services and logistics layer are custom extensions requiring later central classification.
unknown:
  - Exact current Tibia, Canary and OTClient behavior and implementation coverage at future implementation time.
conflicts: []
first_failure:
  marker: missing-task-record
  evidence: PR 789 originally added only the detailed design document without the active task/checkpoint required by repository governance.
rejected_hypotheses:
  - Replace all legacy quest rewards or copy fully isolated Albion-style city markets.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-ots-quest-journal-postal-market-logistics.md
  - docs/ai-agent/OTS_QUEST_JOURNAL_POSTAL_AND_MARKET_LOGISTICS.md
validation:
  - command: changed-file and design-boundary review
    result: PASS
    evidence: Scope is limited to one future design document plus this task record; no runtime or binary paths are changed.
  - command: exact-head Agent Task Ownership and CI
    result: NOT_RUN
    evidence: Required workflows must run on the task-record final commit after ci:final-gate was applied.
blockers: []
next_action: Require exact-head checks, mark PR 789 ready and squash-merge if all gates pass.
```
