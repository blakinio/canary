---
task_id: CAN-20260724-ots-prey-system-2-0
program_id: CAN-PROGRAM-OTS-FUTURE-GAMEPLAY-SYSTEMS
coordination_id: OTS-PREY-SYSTEM-2-0
status: implementing
agent: "GPT-5.6 Thinking"
branch: docs/ots-prey-system-2-0-20260724
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: ""
risk: low
related_issue: ""
related_pr: "894"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-ots-prey-system-2-0.md
    - docs/ai-agent/OTS_PREY_SYSTEM_2_0.md
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_EXTENSION_PACKS.md
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md
  shared: []
  read_only:
    - src/io/ioprey.cpp
    - src/io/ioprey.hpp
    - data/events/scripts/player.lua
    - docs/ai-agent/OTS_BOUNTY_AND_WEEKLY_TASKS_REWORK.md
modules_touched:
  - OTS future gameplay roadmap
  - OTS gameplay proposal classification
  - Prey future design
reuses:
  - current Canary Prey slot, bonus, reroll and persistence concepts
  - current OTClient game_prey module as implementation-time UI baseline
  - existing Bounty/Weekly design boundaries without merging the systems
public_interfaces: []
cross_repo_tasks: []
---

# Prey System 2.0 future-design integration

## Goal

Redesign Prey so that it rewards the hunt the player actually chose without wasting paid or earned Prey time when the player changes activity, and without requiring recurring expensive wildcard payments merely to preserve a selected creature.

## Scope

Documentation and classification only. No runtime, protocol, OTClient, store, economy configuration, database, datapack, map or production behavior changes.

## Acceptance criteria

- [ ] Record current official Tibia, Canary and OTClient evidence without claiming unresolved parity.
- [ ] Define target-specific active-use time consumption.
- [ ] Separate target reservation from bonus locking and bonus renewal.
- [ ] Define bankable free reroll/reactivation charges and non-store maintenance paths.
- [ ] Define anti-abuse, mixed-spawn, party and migration boundaries.
- [ ] Add distinct proposal entries after classification entry 120.
- [ ] Pass exact-final Agent Task Ownership, AI Agent Tools and CI.
- [ ] Mark ready and squash-merge through repository protection.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24
head: 8fa902aa9552ffa4a3af4340ce31c530fff36b86
branch: docs/ots-prey-system-2-0-20260724
pr: 894
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
  - cpp-runtime
  - lua-data
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-ots-prey-system-2-0.md
  - docs/ai-agent/OTS_PREY_SYSTEM_2_0.md
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_EXTENSION_PACKS.md
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md
proven:
  - Official Tibia currently offers up to three Prey slots, one free list reroll every 20 hours, 2 hours of hunting time, wildcard bonus reroll, one-wildcard automatic reroll and five-wildcard Lock Prey renewal.
  - Current Canary calls removePreyStamina from the generic stamina path when experience is gained from a non-player target, before applying the selected-race Prey XP check.
  - Current Canary Lock Prey renews the same target and bonus by consuming PREY_SELECTION_LIST_PRICE when the timer expires.
  - Current OTClient exposes the official-style prey actions and only None, Automatic Reroll and Lock Prey options.
  - No sufficiently evidenced custom OTS design was found that should be attributed as the origin of this redesign.
derived:
  - Current Canary can consume active Prey time while the player hunts a different eligible monster.
  - Target reservation, bonus persistence and time consumption should be independent responsibilities.
unknown:
  - Exact current official Tibia server trigger for decrementing hunting time is not proven beyond the official wording that time decreases while hunting.
  - Exact costs, charge caps, grace windows and protocol payload remain open until implementation-time simulation and client-contract design.
conflicts: []
first_failure: null
rejected_hypotheses:
  - Treat target-specific time consumption as proven current Tibia parity.
  - Remove all Prey economy sinks or make maximum bonuses permanently free.
  - Merge Prey and Bounty into one progression system.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-ots-prey-system-2-0.md
validation:
  - command: source evidence review
    result: PASS
    evidence: Official Tibia manual/support, current fork Canary source and upstream OTClient game_prey module were inspected.
blockers: []
next_action: Create the detailed Prey System 2.0 design, append roadmap section and classification entries 121 onward, then review the exact diff and final-gate the PR.
```
