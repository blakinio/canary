---
task_id: CAN-20260712-the-beginning-tutorial-moveevents
status: in-progress
agent: "GPT-5.6 Thinking"
branch: fix/the-beginning-tutorial-moveevents
base_branch: main
created: 2026-07-12T14:30:00+02:00
updated: 2026-07-12T14:30:00+02:00
last_verified_commit: "ad71123296aac38281b5c8cfb292b1936de567c8"
risk: medium
related_pr: ""
depends_on:
  - "PR #144 semantic classification"
blocks: []
owned_paths:
  - data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua
  - tools/ai-agent/test_the_beginning_tutorial_moveevents.py
  - docs/agents/tasks/active/CAN-20260712-the-beginning-tutorial-moveevents.md
  - docs/agents/ACTIVE_WORK.md
modules_touched:
  - The Beginning tutorial gameplay
reuses:
  - Storage.Quest.U8_2.TheBeginningQuest
  - existing MoveEvent API
  - OTBM resolver from PR #104
cross_repo_tasks: []
---

# Goal

Restore current-API MoveEvent handlers for the 24 map action IDs classified by PR #144 as missing gameplay scripts for The Beginning tutorial, without changing the OTBM or unrelated quest content.

# Acceptance criteria

- [ ] Register exactly the 24 AIDs present in the verified map; do not register absent 50073 or 50089.
- [ ] Restore one-shot tutorial hints, map marks, effects and monotonic TutorialHintsStorage progression.
- [ ] Restore Santiago/Zirella/cave route gates without trapping advanced characters.
- [ ] Use current `Storage.Quest.U8_2.TheBeginningQuest.*` keys and current Canary APIs.
- [ ] Add focused deterministic tests for registration and critical branches.
- [ ] Resolver reports the 24 values as runtime-handled.
- [ ] No `.otbm`, parser, renderer, resolver implementation, NPC, spawn or engine changes.
- [ ] Required CI passes on the final head.

# Confirmed context

- Source map SHA-256: `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`.
- PR #144 classified 24 AIDs / 157 placements as `missing-script`, confidence high.
- Active Santiago/Zirella NPCs and quest catalogue retain the matching current storage chain.
- Historical ORTS code is evidence only and must be adapted rather than copied blindly.
- No open PR or active task overlaps this quest or the proposed owned paths.

# Plan

1. Audit current storage/API/item conventions needed by the two MoveEvent families.
2. Add a narrow current-convention script registering only map-present AIDs.
3. Add focused tests and run resolver/AI-agent validation.
4. Keep the PR limited to gameplay restoration and tests.

# Risks

Wrong storage thresholds can trap new or existing characters, repeat messages, or bypass tutorial ordering. Advanced storage states must always remain passable.

# Handoff

Start from `docs/ai-agent/WORLD_SEMANTIC_REVIEW_ACTIONIDS_50058_50088.md`. Do not modify the binary map or register absent AIDs 50073/50089 without new map evidence.
