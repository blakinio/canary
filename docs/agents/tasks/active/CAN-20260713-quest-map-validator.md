---
task_id: CAN-20260713-quest-map-validator
coordination_id: "OTS-OTBM-VALIDATION"
status: active
agent: "GPT-5.6 Thinking"
branch: feat/quest-map-validator
base_branch: main
created: 2026-07-13T00:18:00+02:00
updated: 2026-07-13T00:18:00+02:00
last_verified_commit: "97ff786663b30cafbd933799d8549a6dd3e3370b"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - "merged Unified OTBM World Index #219"
  - "merged OTBM script-resolution audit #104"
blocks:
  - "teleport/pathfinding validation phase"
  - "storage dependency graph phase"
  - "quest repair evidence bundles"
owned_paths:
  - tools/ai-agent/quest_map_validation.py
  - tools/ai-agent/quest_map_validation_tool.py
  - tools/ai-agent/test_quest_map_validation.py
  - docs/ai-agent/QUEST_MAP_VALIDATION.md
  - docs/ai-agent/QUEST_MAP_VALIDATION.schema.json
  - .github/workflows/quest-map-validation.yml
  - docs/agents/tasks/active/CAN-20260713-quest-map-validator.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
modules_touched:
  - Unified OTBM World Index
  - OTBM script-resolution audit
reuses:
  - tools/ai-agent/otbm_world_index.py
  - tools/ai-agent/otbm_script_resolution.py
public_interfaces:
  - "canary-quest-map-evidence-v1"
  - "canary-quest-map-validation-v1"
  - "Quest Map Validator CLI"
cross_repo_tasks: []
---

# Goal

Create a deterministic read-only Quest Map Validator that extracts static quest evidence from active Lua/XML sources and correlates item IDs, AID/UID, exact positions and teleport destinations with the merged OTBM World Index and optional script-resolution report.

# Acceptance criteria

- [ ] Scan selected active source roots without evaluating Lua or guessing dynamic expressions.
- [ ] Extract static action IDs, unique IDs, item IDs, exact positions, teleport destinations and storage reads/writes with file/line/context evidence.
- [ ] Support explicit include/exclude globs so one quest or questline can be audited without treating every datapack file as one quest.
- [ ] Produce reusable `canary-quest-map-evidence-v1` JSON independent of a private map artifact.
- [ ] Correlate evidence with `.widx` and classify requirements as `confirmed`, `map-only`, `script-only`, `unresolved` or `conflicting`.
- [ ] Reuse the script-resolution report when available; never convert reviewed unresolved identifiers into handled evidence.
- [ ] Detect map mechanics in an explicitly bounded quest region that are not referenced by the selected source set.
- [ ] Bound all placement samples and retain exact counts.
- [ ] Add focused synthetic tests for comments/strings, aliases/constants, dynamic references, duplicate evidence, map/script status combinations and pagination.
- [ ] Run repository scan in CI and publish a machine-readable evidence artifact without requiring the private OTBM.
- [ ] Run local real-map correlation with the supplied `.widx` after downloading the CI evidence artifact.
- [ ] Add schema, documentation, catalogue/changelog updates and exact handoff.
- [ ] Confirm no map, `.widx`, generated report, asset, datapack or runtime behavior is committed.
- [ ] Cross-repository impact is none.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- Unified OTBM World Index #219 is merged at `97ff786663b30cafbd933799d8549a6dd3e3370b`.
- World-index real-map artifact exists locally outside Git and contains 17,972,761 tiles, 23,359,571 placements and 9,339 map mechanics.
- OTBM script-resolution #104 already parses active Action/MoveEvent registrations and preserves dynamic/unresolved evidence.
- Existing quest fixes in open PRs own specific gameplay files, not the new validator paths.
- Coordination policy #214 forbids normal task branches from editing `docs/agents/ACTIVE_WORK.md`.
- Full storage dependency semantics, NPC/spawn parsing and pathfinding are later phases; this phase inventories only evidence needed to connect selected quest sources to map placements.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Unified OTBM World Index / #219 | bounded item/mechanic/position/region queries | `tools/ai-agent/otbm_world_index.py` | Provides exact map evidence without rescanning OTBM. |
| OTBM script resolution / #104 | Action/MoveEvent registration and runtime statuses | `tools/ai-agent/otbm_script_resolution.py` | Prevents a competing Lua registration parser and preserves unresolved semantics. |
| Factual renderer / #154/#161 | later bounded visual context | existing OTBM renderer/HD tools | Visual evidence remains optional output, not correctness proof. |

# Ownership and overlap check

- Open PR search for `quest map validator` returned no overlapping task.
- Specific tutorial quest PRs remain independent because this phase changes only validator code/docs/workflow.
- `ACTIVE_WORK.md` is intentionally not edited.

# Current state

Task claimed from merged World Index main. Static evidence contract and synthetic validator implementation are next.

# Plan

1. Implement comment/string-safe Lua/XML evidence extraction with deterministic deduplication.
2. Implement world-index and optional script-resolution correlation.
3. Add CLI, schemas, tests, documentation and CI artifact scan.
4. Download CI evidence and run real-map correlation locally against the supplied `.widx`.
5. Review findings, current-head checks and merge without gameplay changes.

# Work log

## 2026-07-13T00:18:00+02:00

- Changed: created the phase-two branch and claimed new validator paths.
- Learned: the merged index exposes all required bounded map queries; the script resolver exposes static registrations/references and dynamic uncertainty.
- Failed/blocked: full repository source is not available in the local container, so CI will publish the source-only evidence artifact for local correlation with the private world index.
- Result: ready for early draft PR and implementation.

# Decisions

| Decision | Reason/evidence |
|---|---|
| Split source evidence generation from private-map correlation | CI can scan public repository sources while private/large map indexes remain local. |
| Require explicit source selection | File names and directories are evidence; automatically grouping all datapack files into quests would create false associations. |
| Reuse script-resolution output | Avoids conflicting handler classifications. |
| Keep storage handling to read/write inventory | Full transition graph is a separate roadmap phase. |

# Files and interfaces

| Path/interface | Purpose | Status |
|---|---|---|
| `quest_map_validation.py` | static evidence and map correlation library | planned |
| `quest_map_validation_tool.py` | scan/validate CLI | planned |
| `canary-quest-map-evidence-v1` | map-independent source evidence | planned |
| `canary-quest-map-validation-v1` | correlated report | planned |

# Validation and CI

| Commit | Check | Result |
|---|---|---|
| | focused tests and `py_compile` | not-run |
| | repository source-only scan artifact | not-run |
| | local real-map correlation | not-run |
| | current-head GitHub checks | not-run |

# Risks and compatibility

- Runtime/data migration: none; read-only offline tool.
- False positives: reduced through explicit globs, source evidence and unresolved classifications.
- Dynamic Lua: retained as unresolved; never executed or guessed.
- Security: private map/index artifacts remain local and are never uploaded by default.
- Backward compatibility: no existing report format changes.
- Rollback: revert the validator PR; no persistent cleanup.

# Remaining work

1. Publish the draft PR and implement the source-evidence scanner.

# Handoff

Read this task, `docs/ai-agent/OTBM_WORLD_INDEX.md` and `docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md`. Do not edit `ACTIVE_WORK.md`, create another OTBM parser, commit `.widx`, or mix gameplay fixes into the validator PR.

# Completion

- Final status: active
- PR:
- Merge commit:
- Catalogue updated: pending
- Changelog updated: pending
- Archived at:
