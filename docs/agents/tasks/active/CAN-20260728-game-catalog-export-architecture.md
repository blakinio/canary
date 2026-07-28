---
task_id: CAN-20260728-game-catalog-export-architecture
program_id: none
agent: chatgpt
branch: docs/CAN-20260728-game-catalog-export-architecture
status: ready
related_pr: 989
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260728-game-catalog-export-architecture.md
    - docs/contracts/GAME_CATALOG_EXPORT_CONTRACT.md
    - docs/systems/GAME_CATALOG_EXPORTER.md
    - docs/agents/prompts/GAME_CATALOG_EXPORTER_IMPLEMENTATION_PROMPT.md
    - schemas/game-catalog/v1/game-catalog-snapshot.schema.json
  shared:
    - docs/agents/CROSS_REPO_CONTRACTS.md
required_reads:
  - AGENTS.md
  - docs/agents/REPOSITORY_MAP.md
  - docs/agents/CONTEXT_ROUTING.md
  - docs/contracts/GAME_CATALOG_EXPORT_CONTRACT.md
  - docs/systems/GAME_CATALOG_EXPORTER.md
  - schemas/game-catalog/v1/game-catalog-snapshot.schema.json
search_first:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/KNOWN_RISKS.md
  - docs/agents/BUILD_TEST_MATRIX.md
  - docs/agents/CROSS_REPO_CONTRACTS.md
optional_reads:
  - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
---

# CAN-20260728-game-catalog-export-architecture

## Goal

Persist the reviewed Canary-side architecture and cross-repository contract for a deterministic offline export of final runtime items, creatures and loot to Oteryn Platform.

## Acceptance criteria

- [x] Define Canary as the runtime semantic authority.
- [x] Define an offline CLI export boundary that does not start world services or mutate the database.
- [x] Define deterministic snapshot provenance, version, completeness and availability metadata.
- [x] Define proposed source, manifest, schema, tooling and test paths.
- [x] Define items, creatures and loot as the first bounded implementation slice.
- [x] Preserve NPCs, quests, map availability and historical snapshots as later slices.
- [x] Add an implementation prompt independent of chat history.
- [x] Add the proposed schema v1 and prove byte identity with Platform.
- [x] Register the durable cross-repository contract.
- [x] Open the draft architecture PR.
- [x] Merge the matching Platform architecture PR.
- [ ] Pass Canary final-head validation and merge PR #989.

## Ownership

```yaml
owned_paths:
  - docs/agents/tasks/active/CAN-20260728-game-catalog-export-architecture.md
  - docs/contracts/GAME_CATALOG_EXPORT_CONTRACT.md
  - docs/systems/GAME_CATALOG_EXPORTER.md
  - docs/agents/prompts/GAME_CATALOG_EXPORTER_IMPLEMENTATION_PROMPT.md
  - docs/agents/CROSS_REPO_CONTRACTS.md
  - schemas/game-catalog/v1/game-catalog-snapshot.schema.json
modules:
  - game-catalog-export
  - items
  - monsters
  - startup-cli
dependencies:
  - contract: oteryn.game-catalog/v1
  - OTERYN-20260728-versioned-game-catalog-architecture merged as 8aa1fc29dd13895efb2a7006204a6b88105e6972
blockers:
  - none for architecture documentation
cross_repository_tasks:
  - OTERYN-20260728-versioned-game-catalog-architecture
```

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-28T07:38:00Z
head: e3442bd505a5b5b02da34aa624bed34e381cb1aa
branch: docs/CAN-20260728-game-catalog-export-architecture
pr: 989
status: ready
context_routes:
  - agent-governance
  - cpp-runtime
  - lua-data
  - real-tibia-parity
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260728-game-catalog-export-architecture.md
  - docs/contracts/GAME_CATALOG_EXPORT_CONTRACT.md
  - docs/systems/GAME_CATALOG_EXPORTER.md
  - docs/agents/prompts/GAME_CATALOG_EXPORTER_IMPLEMENTATION_PROMPT.md
  - docs/agents/CROSS_REPO_CONTRACTS.md
  - schemas/game-catalog/v1/game-catalog-snapshot.schema.json
proven:
  - Canary loads appearances, items, core scripts, datapack scripts, monsters and NPCs before normal world startup.
  - Canary already has a CLI-only Lua API documentation mode that avoids normal server run behavior.
  - MonsterType contains runtime creature statistics and loot.
  - Protocol support, content completeness, datapack revision and map revision are independent facts.
  - Canary and Platform schema files have the same Git blob SHA a3c239a6d61385edde0b06f72cdf781f4ce58df3.
  - The shared schema content SHA-256 is 099a8373ff2b0017cc2b321991662dc4e4783b626391aa7a110a6db0559d146b.
  - Oteryn Platform architecture PR 271 merged as 8aa1fc29dd13895efb2a7006204a6b88105e6972 after all final-head workflows passed.
  - Canary Agent Task Ownership run 30338906129 passed after lifecycle metadata repair.
  - Canary incremental CI run 30338906295 completed with Required success before the final-gate commit.
derived:
  - A Game Catalog export mode should follow the existing CLI-only startup precedent.
  - Collectors must read final runtime registries instead of implementing a second partial parser.
  - Datapack-specific version and availability claims require explicit reviewed manifests.
unknown:
  - exact minimal loader split that avoids all database-dependent late startup operations
  - complete historical version metadata for current datapack content
  - complete quest and map availability registries
conflicts: []
first_failure:
  marker: Agent Task Ownership run 30338575516 / Validate active ownership
  evidence: frontmatter lacked active status, PR, branch and ownership claims; checkpoint head and PR formats were invalid
rejected_hypotheses:
  - Scrape external wikis to populate the production snapshot.
  - Infer availability only from the presence of a Lua definition.
  - Export by directly parsing a subset of files and claiming final runtime equivalence.
changed_paths:
  - docs/agents/CROSS_REPO_CONTRACTS.md
  - docs/agents/prompts/GAME_CATALOG_EXPORTER_IMPLEMENTATION_PROMPT.md
  - docs/agents/tasks/active/CAN-20260728-game-catalog-export-architecture.md
  - docs/contracts/GAME_CATALOG_EXPORT_CONTRACT.md
  - docs/systems/GAME_CATALOG_EXPORTER.md
  - schemas/game-catalog/v1/game-catalog-snapshot.schema.json
validation:
  - command: repository connector review
    result: PASS
    evidence: startup, item, MonsterType, NPC and protocol-profile boundaries inspected before writing
  - command: compare schema Git blob SHA across repositories
    result: PASS
    evidence: both paths resolve to blob a3c239a6d61385edde0b06f72cdf781f4ce58df3
  - command: parse proposed schema as JSON and calculate SHA-256
    result: PASS
    evidence: JSON valid; SHA-256 099a8373ff2b0017cc2b321991662dc4e4783b626391aa7a110a6db0559d146b
  - command: Agent Task Ownership run 30338575516
    result: FAIL
    evidence: invalid task lifecycle metadata; repaired and superseded by successful run 30338906129
  - command: Agent Task Ownership run 30338906129
    result: PASS
    evidence: changed checkpoint validation and full ownership index validation succeeded
  - command: CI run 30338906295
    result: PASS
    evidence: Detect Build Scope and Required succeeded; non-applicable runtime builds were skipped for documentation-only changes
blockers:
  - none
next_action: Wait for the ci:final-gate workflows on this exact final commit, then mark PR 989 ready and squash-merge if every required check remains green.
```

## Notes

This task changes documentation only. It does not add CLI flags, compile targets, datapack manifests, generated snapshots, runtime behavior or deployment changes.
