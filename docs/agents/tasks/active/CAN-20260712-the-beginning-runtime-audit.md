---
task_id: CAN-20260712-the-beginning-runtime-audit
status: ready-for-review
agent: "GPT-5.6 Thinking"
branch: docs/the-beginning-runtime-audit
base_branch: main
created: 2026-07-12
updated: 2026-07-12
risk: low
related_pr: "#146"
depends_on:
  - "PR #144 semantic classification"
  - "PR #145 tutorial MoveEvent restoration"
blocks: []
owned_paths:
  - docs/ai-agent/THE_BEGINNING_QUEST_DEPENDENCY_REPORT.md
  - docs/ai-agent/THE_BEGINNING_RUNTIME_TEST_PLAN.json
  - docs/ai-agent/THE_BEGINNING_QUEST_DEPENDENCY_REPORT.json
  - docs/ai-agent/OTBM_SCRIPT_REVIEW_RULES.json
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

- [x] Inventory active NPC, quest catalogue, storage, action, movement, creature-event and reward dependencies.
- [x] Classify dead-tree branch, Zirella cart, UID 50085 door, cockroach events, Santiago cellar ladder, snake-head lever and reward chests 50093/50094.
- [x] Record exact source files, identifiers, items, positions and expected state transitions.
- [x] Separate confirmed active behavior from historical evidence and unresolved runtime assumptions.
- [x] Produce machine-readable quest dependency and runtime test-plan JSON files.
- [x] Produce a human-readable audit report with bounded follow-up PR specifications.
- [x] Classify current Rookgaard border AID 50999 from `needs-manual-review` to `missing-script`.
- [x] Do not change `.otbm`, active datapack content, engine, NPCs, spawns or OTBM tooling.
- [x] Required documentation/AI-agent checks pass on reviewed head.

# Scope boundary

This task audits and documents. Any confirmed gameplay fix must use a separate focused branch and PR. No binary map edits are permitted.

# Confirmed findings

## Active dependencies

- Santiago, Zirella and Carlos are present in companion NPC XML at their current map positions.
- Coat UID 50080, torch UID 50082, shovel UID 50093 and rope UID 50094 are active AID 2000 reward chests with verified contents.
- Generic ladder/sewer, shovel and rope helpers cover the required cellar and cave navigation.
- Six tutorial-area cockroach placements exist and each cockroach guarantees one item 7882 leg.
- PR #145 registers the 24 tutorial route AIDs.

## Blocking gaps

- item 7753 dead trees have no branch-creation Action;
- item 7772 branch used on item 7751 Zirella cart has no handler, leaving Zirella stages 7/8 unreachable;
- Carlos' intended food sale has no persistent completion transition;
- four item 7886 Rookgaard-border tiles carry unresolved AID 50999 and no source writes terminal CarlosQuestLog=8.

## Bypasses and conflicts

- UID 50085 door has no quest seal and permits early reward-room access;
- Carlos' initial `outfit` branch writes final states and skips the food/trade mission;
- Santiago's alternate `easy` branch persists state 11 while the normal equivalent persists 12;
- tutorials 10/11 map stale UIDs 50084/50086 instead of current chest UIDs 50093/50094;
- rope success text checks stage 22 without persisting it;
- advertised `skip tutorial` dialogue has no Santiago handler.

## Non-blocking legacy behavior

- current snake-head and lever objects carry no historical UID and have no current quest dependency; classified `legacy-unused` and preserved.
- cockroach kill/body tutorial hints are absent, while core leg acquisition remains active.

# Validation performed

- verified map SHA-256 against the established baseline;
- native full-map item/mechanic scan: 17,972,761 tiles, 23,359,571 placements, 9,339 mechanic placements;
- bounded item-stack review of all four reward chests and relevant world objects;
- active Lua/NPC/catalog/storage/action search;
- companion NPC and monster spawn XML review;
- current items.xml name/description correlation;
- independent historical behavior used only as corroboration;
- OTBM Map Tools workflow run 82: success;
- AI Agent Tools workflow run 207: success;
- final changed-file list reviewed: six documentation/classification files only.

# Outputs

- `docs/ai-agent/THE_BEGINNING_QUEST_DEPENDENCY_REPORT.md`
- `docs/ai-agent/THE_BEGINNING_QUEST_DEPENDENCY_REPORT.json`
- `docs/ai-agent/THE_BEGINNING_RUNTIME_TEST_PLAN.json`
- updated semantic disposition for AID 50999 in `OTBM_SCRIPT_REVIEW_RULES.json`

# Follow-up order

1. Zirella dead-tree branch and cart delivery gameplay PR.
2. Zirella UID50085 door and current reward tutorial mappings.
3. Carlos NPC state-machine and valid-sale completion.
4. Rookgaard border AID50999 terminal MoveEvent after town/direction verification.
5. Optional cockroach hints and explicitly specified skip-tutorial feature after core E2E passes.

# Handoff

The map does not need a patch. Use the exact items, positions, storages and acceptance tests recorded in the dependency report. Keep each gameplay repair in its own focused branch/PR and rerun the resolver plus the runtime plan after each stage.
