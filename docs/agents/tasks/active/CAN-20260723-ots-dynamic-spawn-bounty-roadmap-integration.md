---
task_id: CAN-20260723-ots-dynamic-spawn-bounty-roadmap-integration
program_id: CAN-PROGRAM-OTS-FUTURE-GAMEPLAY-SYSTEMS
status: ready
agent: "GPT-5.6 Thinking"
branch: docs/dynamic-spawn-hunting-capacity-20260723
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "8d864d70438463dff265b6bf6ef9ec86efee0cb9"
risk: low
related_issue: ""
related_pr: "772"
depends_on:
  - CAN-20260721-ots-future-gameplay-roadmap
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-ots-dynamic-spawn-bounty-roadmap-integration.md
    - docs/ai-agent/OTS_DYNAMIC_SPAWN_AND_HUNTING_CAPACITY.md
    - docs/ai-agent/OTS_BOUNTY_AND_WEEKLY_TASKS_REWORK.md
  shared:
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md
  read_only: []
modules_touched:
  - future-gameplay-product-design
reuses:
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260723 — Dynamic Spawn and Bounty roadmap integration

## Status

READY — PR #772 now follows the established future-gameplay documentation structure. The two detailed documents remain bounded design specifications, while the central roadmap and authoritative ORIGIN/TYPE index provide discoverable summaries and provenance classification.

## Goal

Integrate the Dynamic Spawn/Hunting Capacity and Bounty/Weekly Tasks redesign into the established future-gameplay documentation structure and preserve a clear distinction between current original-Tibia foundations and our custom extensions.

## Scope

- Keep `OTS_DYNAMIC_SPAWN_AND_HUNTING_CAPACITY.md` as the detailed design record.
- Keep `OTS_BOUNTY_AND_WEEKLY_TASKS_REWORK.md` as the detailed design record.
- Add concise entries and links to `OTS_FUTURE_GAMEPLAY_SYSTEMS.md`.
- Add authoritative `ORIGIN` and `TYPE` rows to `OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md`.
- Classify only what current evidence supports; do not label our player-pressure dynamic spawn logic as an original-Tibia feature.
- Do not implement gameplay/runtime/client behavior in this PR.

## Current official-Tibia baseline used for classification

`PROVEN`

- The current official Tibia game guide documents Bounty Tasks with Beginner/Adept/Expert/Master difficulty grouping, Preferred List, rerolls, Silver/Gold tasks and the Bounty Talisman.
- The same current official guide documents Weekly Tasks with Kill Tasks and Delivery Tasks.
- Official 2026 Tibia news documents Rapid Respawn events and an existing improved respawn area bonus.
- No current authoritative evidence reviewed in this task proves our proposed player-pressure, sector-based, effective-power-aware Dynamic Spawn Scaling as an original Tibia system.

References reviewed:

- https://www.tibia.com/gameguides/?section=combat&subtopic=manual
- https://www.tibia.com/news/?id=8570&subtopic=newsarchive
- https://www.tibia.com/news/?id=8801&subtopic=newsarchive

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T13:40:00+02:00
head: 8d864d70438463dff265b6bf6ef9ec86efee0cb9
branch: docs/dynamic-spawn-hunting-capacity-20260723
pr: 772
status: ready
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-ots-dynamic-spawn-bounty-roadmap-integration.md
  - docs/ai-agent/OTS_DYNAMIC_SPAWN_AND_HUNTING_CAPACITY.md
  - docs/ai-agent/OTS_BOUNTY_AND_WEEKLY_TASKS_REWORK.md
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md
proven:
  - PR 772 is an open draft against blakinio/canary main and remains mergeable before exact-final validation.
  - Repository governance requires substantial work to have a discoverable active task record and checkpoint; that task record is now present in PR 772.
  - The two detailed design documents remain separate rather than inflating the central roadmap with more than 1400 lines of implementation-oriented design notes.
  - OTS_FUTURE_GAMEPLAY_SYSTEMS.md now contains concise sections for Dynamic Spawn and Hunting Capacity and Bounty and Weekly Tasks Rework, links to both detailed records, and dependency-cluster integration.
  - OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md now classifies the two top-level systems and the major approved sub-proposals through entries 59-68.
  - Current official Tibia documentation confirms Bounty Tasks, Weekly Tasks and Bounty Talisman as original-Tibia foundations.
  - Current official Tibia evidence confirms Rapid Respawn and improved respawn-area bonuses, but does not prove the proposed player-pressure sector-capacity algorithm as official behavior.
  - The ci:final-gate label was applied to PR 772 before this immutable ready-state checkpoint commit.
derived:
  - Bounty and Weekly Tasks Rework is classified as MIXED / TIBIA-EXTENSION because it redesigns a verified current Tibia system with substantial custom behavior.
  - Dynamic Spawn and Hunting Capacity is classified as MIXED / HYBRID because it combines an official respawn-acceleration foundation with our custom player-pressure, sector, power-range, capacity-budget and anti-abuse design.
unknown:
  - Exact current Canary and maintained OTClient implementation coverage for Bounty/Weekly Tasks and every proposed dynamic-spawn integration point; implementation-time audit remains required.
  - Exact-final-head CI, Agent Task Ownership and AI Agent Tools conclusions after this ready-state checkpoint commit.
conflicts: []
first_failure:
  marker: missing-roadmap-integration
  evidence: PR 772 initially added two detailed design files but did not add a task record, central-roadmap entries or ORIGIN/TYPE classification entries; all three structural gaps are repaired in the current scope.
rejected_hypotheses:
  - Delete the detailed design files and move all 1400+ lines into the central roadmap; rejected because the roadmap should remain a concise discoverability/index layer.
  - Classify Dynamic Spawn Scaling as TIBIA-OFFICIAL; rejected because current official evidence reviewed here proves respawn acceleration mechanisms, not the proposed player-pressure sector-capacity algorithm.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-ots-dynamic-spawn-bounty-roadmap-integration.md
  - docs/ai-agent/OTS_DYNAMIC_SPAWN_AND_HUNTING_CAPACITY.md
  - docs/ai-agent/OTS_BOUNTY_AND_WEEKLY_TASKS_REWORK.md
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md
validation:
  - command: live PR 772 changed-file audit
    result: PASS
    evidence: final intended scope is exactly five documentation/task paths with no runtime, map, binary, datapack, client or workflow changes.
  - command: current official Tibia source verification
    result: PASS
    evidence: official game guide and 2026 news establish the bounded classification baseline recorded above.
  - command: pre-final PR workflow cycle on head 8d864d70438463dff265b6bf6ef9ec86efee0cb9
    result: IN_PROGRESS
    evidence: CI, Agent Task Ownership and AI Agent Tools were triggered before the final checkpoint commit; exact-final-head runs triggered by this commit are authoritative.
blockers: []
next_action: Verify exact-final-head CI, Agent Task Ownership and AI Agent Tools on the resulting immutable head; if green and scope/review audit remains clean, update the PR body, mark ready and squash-merge under repository policy without further feature commits.
```
