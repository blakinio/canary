---
task_id: CAN-20260723-otbm-tibia-client-reference-architecture
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: active
agent: GPT-5.6 Thinking
branch: docs/otbm-tibia-client-reference-20260723
base_branch: main
created: 2026-07-23T10:00:00+02:00
updated: 2026-07-23T11:20:00+02:00
last_verified_commit: "39d2a40bff08bae36c77a9f28cc0c974a16bea32"
risk: low
related_issue: ""
related_pr: "#762"
depends_on:
  - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
  - docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md
  - docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md
  - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
  - Unified OTBM World Index and existing OTBM QA/repair stack
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-otbm-tibia-client-reference-architecture.md
    - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
    - docs/ai-agent/OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md
  shared:
    - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
    - docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md
    - docs/agents/real-tibia/registry/modules/otbm-tooling.yaml
    - docs/agents/CHANGELOG.md
  read_only:
    - AGENTS.md
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/CONTEXT_ROUTING.md
    - beats-dh/Beats-Assets-Editor at ed827be34c279d1279ad3dde3af434b148ac05c7
modules_touched:
  - OTBM analysis tooling
  - Real Tibia parity governance
  - official-client reference evidence
reuses:
  - canary-otbm-world-index-v1
  - canary-appearances-index-v1
  - canary-client-assets-index-v1
  - canary-otbm-asset-compatibility-v1
  - Quest Map Validator
  - OTBM spawn/boss/NPC validator
  - OTBM Geometry Audit
  - OTBM Reachability
  - OTBM Critical Access Integrity
  - Semantic OTBM Diff
  - bounded repair/materialization pipelines
  - release provenance/change risk/evidence gateway
public_interfaces:
  - planned Tibia client reference evidence contracts and programme queue
cross_repo_tasks: []
---

# Goal

Define a concrete, durable architecture and phased implementation plan for ingesting exact user-supplied Tibia 15.x client reference files as read-only evidence and correlating them with the existing canonical OTBM/Canary analysis stack without creating a second OTBM parser, pathfinder, renderer, script resolver, mutation engine or E2E platform.

# Scope

This task is documentation and architecture only. It does not implement parsers, mutate `.otbm`, `items.otb`, client assets or datapack/runtime code, and does not commit proprietary Tibia client files.

The architecture covers:

- exact client-package provenance and SHA-256 pinning;
- `staticdata` old/new schema evidence;
- `staticmapdata` house-layout evidence;
- proficiency reference evidence and item/appearance bindings;
- reuse of existing appearances/assets indexes;
- optional minimap/reference evidence boundaries;
- parity consumers for houses, monsters/bosses/quests and proficiency;
- deterministic drift between two client-reference snapshots;
- adoption routing into existing bounded OTBM repair/materialization or non-OTBM subsystem tasks;
- explicit licensing boundary for `beats-dh/Beats-Assets-Editor` as research/reference, not copied implementation.

# Acceptance criteria

- [x] Add a durable programme with bounded queue entries and exact next action.
- [x] Add a technical architecture defining contracts, provenance, joins, failure states and non-goals.
- [x] Update the OTBM real-Tibia registry record without creating a duplicate tooling module.
- [x] Ensure the plan does not authorize raw client files, `.otbm`, `.widx`, `items.otb` or generated large artifacts in Git.
- [x] Ensure `staticmapdata` is treated as bounded house-layout/reference evidence, not a full OTBM source or automatic map generator.
- [x] Ensure minimap evidence cannot replace canonical World Index/Reachability mechanics evidence.
- [x] Ensure all proposed mutation/adoption routes require existing review/approval and post-mutation validation contracts.
- [x] Include a bounded kickoff prompt for the implementation agent in the programme handoff.
- [ ] Regenerate and validate the derived Real Tibia registry indexes after the `otbm-tooling` registry change.
- [ ] Add narrow discovery mirrors to `MODULE_CATALOG.md`, `OTS_OTBM_TOOLING_ROADMAP.md`, `REAL_TIBIA_EVIDENCE_SOURCES.md`, `REAL_TIBIA_PARITY_PROGRAM.md` and `CHANGELOG.md` if still required after re-reading then-current main.
- [ ] Run repository-required documentation/registry validation and verify PR #762 CI on its final head.

# Evidence baseline

## PROVEN

- Current task branch was created from `blakinio/canary:main` at `8837f35eb43da6a3ed7efc6a1e8f3bca19342d2e`.
- Open PR #759 owns only QA-006/QA-007 certification/assurance implementation paths and does not overlap this task's delivered documentation paths.
- Draft PR #762 owns this task.
- `beats-dh/Beats-Assets-Editor` HEAD observed for this design is `ed827be34c279d1279ad3dde3af434b148ac05c7`.
- Canary Studio exposes feature domains for appearances, sprites, staticdata, staticmapdata, proficiency, minimap, monsters, NPCs, dat merge, QM, RCC and sounds.
- Its newer-client `staticdata` schema contains monsters, monster classes, achievements, houses, bosses and quests; `staticmapdata` contains house IDs, position, size/floors and tile-level object/wall/door evidence.
- Its proficiency reader models proficiency IDs, levels, XP requirements and perks, and it can correlate proficiency IDs with Canary `items.xml`.
- The source repository is CC BY-NC-SA 4.0; this task therefore treats it as a format/research reference and does not authorize source-code copying into GPLv2 Canary.
- Existing Canary OTBM tooling already owns canonical OTBM parsing/indexing, appearances/assets indexing, script resolution, reachability, semantic diff, geometry, QA evidence and bounded mutation pipelines.
- `OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md`, `OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md` and the updated `otbm-tooling` registry record are published on the task branch.

## UNKNOWN / deferred

- Exact Tibia client build/version carried by future user-supplied files must be recorded per ingestion; it must never be inferred from filename alone.
- Exact filenames/packaging of proficiency data may vary by client build and must be discovered by a bounded implementation task rather than hard-coded by this architecture task.
- Whether every proposed client-reference field has a stable semantic meaning across builds remains implementation evidence, not assumed architecture truth.
- Derived Real Tibia registry indexes and repository CI have not yet been validated on the current PR head.

# Context checkpoint

STATUS: active

PROVEN:
- Branch `docs/otbm-tibia-client-reference-20260723` started from main `8837f35eb43da6a3ed7efc6a1e8f3bca19342d2e`.
- Draft PR #762 exists and currently contains the architecture document, programme/queue/kickoff prompt, active task record and updated `otbm-tooling` registry record.
- No changed-path overlap was found with open OTBM QA PR #759 at task start.
- Architecture source inventory is pinned to `beats-dh/Beats-Assets-Editor@ed827be34c279d1279ad3dde3af434b148ac05c7`.
- This task is docs-only and adds no parser/runtime/map implementation.

BLOCKED / PENDING:
- The current connector session cannot safely perform line-level patches to the large shared Markdown indexes, and local GitHub DNS is unavailable, so those shared discovery mirrors and generated registry indexes have not been completed or validated here.
- PR #762 must remain draft until registry generation/validation, any still-required narrow shared-index mirrors, and final-head CI are complete.

NEXT_ACTION:
- In a local checkout on PR #762, re-fetch current main, regenerate/validate Real Tibia registry derived indexes, apply only still-required narrow discovery updates to the shared catalogue/roadmap/evidence/program/changelog files, run the required docs/registry validation, update this checkpoint, and keep the PR draft until final-head CI is green. After TCR-000 merges and archives, start exactly TCR-001 Client Package Manifest in a new task/branch/PR.
