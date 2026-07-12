---
task_id: CAN-20260712-the-beginning-runtime-audit
status: in-progress
agent: "GPT-5.6 Thinking"
branch: docs/the-beginning-runtime-audit
base_branch: main
created: 2026-07-12
updated: 2026-07-12
risk: low
related_pr: ""
depends_on:
  - "PR #144 semantic classification"
  - "PR #145 tutorial MoveEvent restoration"
blocks: []
owned_paths:
  - docs/ai-agent/THE_BEGINNING_QUEST_DEPENDENCY_REPORT.md
  - docs/ai-agent/THE_BEGINNING_RUNTIME_TEST_PLAN.json
  - docs/ai-agent/THE_BEGINNING_QUEST_DEPENDENCY_REPORT.json
  - docs/agents/tasks/active/CAN-20260712-the-beginning-runtime-audit.md
  - docs/agents/ACTIVE_WORK.md
modules_touched:
  - World Semantic Review
  - The Beginning quest audit
reuses:
  - OTBM script-resolution audit
  - merged PR #144 placement evidence
  - merged PR #145 MoveEvent implementation
cross_repo_tasks: []
---

# Goal

Build an evidence-based dependency graph and runtime/E2E validation plan for the complete The Beginning quest from Santiago through Zirella to Carlos. Identify confirmed, probable and unresolved gameplay dependencies without modifying the map or active datapack in this documentation-only PR.

# Acceptance criteria

- [ ] Inventory active NPC, quest catalogue, storage, action, movement, creature-event and reward dependencies.
- [ ] Classify dead-tree branch, Zirella cart, UID 50085 door, cockroach events, Santiago cellar ladder, snake-head lever and reward chests 50093/50094.
- [ ] Record exact source files, identifiers, items, positions and expected state transitions.
- [ ] Separate confirmed active behavior from historical evidence and unresolved runtime assumptions.
- [ ] Produce machine-readable quest dependency and runtime test-plan JSON files.
- [ ] Produce a human-readable audit report with bounded follow-up PR specifications.
- [ ] Do not change `.otbm`, active datapack content, engine, NPCs, spawns or OTBM tooling.
- [ ] Required documentation/AI-agent checks pass.

# Scope boundary

This task audits and documents. Any confirmed gameplay fix must use a separate focused branch and PR. No binary map edits are permitted.

# Initial evidence

- PR #144 classified 24 tutorial AIDs as `missing-script` with high confidence.
- PR #145 restored exactly those 24 map-present MoveEvent registrations.
- Resolver after PR #145 reported the 24 values as runtime-handled and reduced unresolved placements by 157.
- Full quest completeness has not yet been proven by runtime/E2E execution.

# Handoff

Use `docs/ai-agent/WORLD_SEMANTIC_REVIEW_ACTIONIDS_50058_50088.md` and the merged MoveEvent script as the starting point. Do not copy historical behavior into active gameplay unless current Canary dependencies and map evidence support it.
