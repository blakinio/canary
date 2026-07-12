---
task_id: CAN-20260712-the-beginning-tutorial-moveevents
status: completed
agent: "GPT-5.6 Thinking"
branch: fix/the-beginning-tutorial-moveevents
base_branch: main
created: 2026-07-12T14:30:00+02:00
updated: 2026-07-12T14:45:00+02:00
last_verified_commit: "e3a3ccc2ba487876a54e82c2be836e4fa6fc8288"
risk: medium
related_pr: "#145"
depends_on:
  - "PR #144 semantic classification"
blocks: []
owned_paths:
  - data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua
  - tools/ai-agent/test_the_beginning_tutorial_moveevents.py
  - docs/agents/CHANGELOG.md
  - docs/agents/tasks/archive/CAN-20260712-the-beginning-tutorial-moveevents.md
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

- [x] Register exactly the 24 AIDs present in the verified map; absent 50073 and 50089 remain unregistered.
- [x] Restore one-shot tutorial hints, map marks, effects and monotonic TutorialHintsStorage progression.
- [x] Restore Santiago/Zirella/cave route gates with advanced-state safety.
- [x] Use current `Storage.Quest.U8_2.TheBeginningQuest.*` keys and current Canary APIs.
- [x] Add focused deterministic tests for registration and critical branches.
- [x] Resolver reports all 24 values as `handled-directly`.
- [x] No `.otbm`, parser, renderer, resolver implementation, NPC, spawn or engine changes.
- [x] CI, Account Quests and AI Agent Tools pass on the implementation head.

# Implementation

Added `the_beginning_tutorial_moveevents.lua` with two bounded `stepin` MoveEvents:

- hint family: `50058..50069`, `50075..50079`, `50081`;
- stop/gate family: `50070`, `50071`, `50072`, `50074`, `50080`, `50088`.

The implementation uses current quest storage names, preserves one-shot monotonic hint progression, restores map marks/tutorial UI/effects, retains the paired `50071`/`50074` pass behavior, and avoids trapping characters whose tutorial state is already advanced.

Historical code was used only as corroboration. Absent map IDs `50073` and `50089`, plus unrelated historical branch/cart/door/corpse/lever actions, were intentionally excluded.

# Validation

## Verified source map

```text
SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
```

## Focused contract tests

`tools/ai-agent/test_the_beginning_tutorial_moveevents.py` verifies:

- exact registration set and family split;
- current storage namespace;
- one-shot progression stages;
- critical Santiago, shovel, paired-pass and exit gates;
- absence of map/world item mutation APIs.

The initial CI attempt failed because the test parser matched `.aid(...)` instead of Canary's `:aid(...)`. The parser was corrected; the implementation itself was unchanged.

## Resolver result

Fresh local resolver run against the verified map and active datapack overlay:

```text
files scanned: 5,385
registrations: 1,184
resolved placements: 9,121
runtime-unresolved/partial placements: 218
runtime-unresolved identifiers: 127
conflicts: 0
```

All selected 24 AIDs are `handled-directly`. Compared with the pre-fix baseline:

```text
runtime-unresolved identifiers: 151 -> 127 (-24)
runtime-unresolved/partial placements: 375 -> 218 (-157)
```

This exactly matches the 24 identifiers and 157 placements classified in PR #144.

## GitHub workflows on implementation head `e3a3ccc2...`

- CI: success;
- Account Quests: success;
- AI Agent Tools: success;
- autofix.ci: skipped as expected.

# Safety and compatibility

- No binary map or map attribute changed.
- No OTBM tooling implementation changed.
- No NPC, spawn, monster, engine, database or production configuration changed.
- Existing advanced tutorial states remain passable.
- Runtime E2E with a fresh character is still recommended as staging validation; the exact 19-step plan remains in `WORLD_SEMANTIC_REVIEW_ACTIONIDS_50058_50088.md`.

# Remaining related work

The two MoveEvent families are restored, but PR #144 identified separate dependencies that still require their own semantic/implementation tasks:

- dead-tree branch acquisition and branch-on-cart action;
- Zirella door UID 50085;
- cockroach kill/body tutorial hints;
- Santiago cellar ladder behavior;
- snake-head lever behavior;
- reward chest UID mapping for current map UIDs 50093/50094;
- full fresh-character runtime/E2E execution of The Beginning.

# Completion

- Final status: completed
- PR: #145
- Merge commit: pending
- Changelog: updated
- Module catalogue: not required; no reusable interface introduced
- Cross-repository impact: none
