---
task_id: CAN-20260713-quest-map-validator
coordination_id: "OTS-OTBM-VALIDATION"
status: validating
agent: "GPT-5.6 Thinking"
branch: feat/quest-map-validator
base_branch: main
created: 2026-07-13T00:18:00+02:00
updated: 2026-07-13T09:10:00+02:00
last_verified_commit: "0525d0924c6ea83a5f858aa4c6057b53a2ecd6a7"
risk: medium
related_issue: ""
related_pr: "#225"
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

Create a deterministic read-only Quest Map Validator that extracts static quest evidence from explicitly selected active Lua/XML sources and correlates AID/UID, item IDs, exact positions and teleport destinations with the merged OTBM World Index and optional script-resolution report.

# Acceptance criteria

- [x] Scan selected active source roots without evaluating Lua or guessing dynamic expressions.
- [x] Extract static action IDs, unique IDs, item IDs, exact positions, teleport destinations and storage reads/writes with file/line/context evidence.
- [x] Support explicit include/exclude globs so one quest or questline can be audited without treating every datapack file as one quest.
- [x] Produce reusable `canary-quest-map-evidence-v1` JSON independent of a private map artifact.
- [x] Correlate evidence with `.widx` and classify results as `confirmed`, `map-only`, `script-only`, `unresolved` or `conflicting`.
- [x] Reuse script-resolution when supplied and never convert reviewed unresolved identifiers into handled evidence.
- [x] Detect map mechanics in an explicitly bounded quest region that are not referenced by the selected source set.
- [x] Bound all placement samples and retain exact counts.
- [x] Add focused synthetic tests for comments/strings, aliases/constants, dynamic references, duplicate evidence, conservative map semantics, status combinations, bounded samples and safe output.
- [x] Run a representative repository scan in CI and publish a machine-readable evidence artifact without requiring private OTBM.
- [x] Publish a local-correlation toolkit containing the compiled scanner and required Python modules.
- [x] Run local real-map correlation with the supplied map/index outside Git.
- [x] Add schema, documentation, catalogue/changelog updates and exact handoff.
- [x] Confirm no map, `.widx`, generated report, asset, datapack or runtime behavior is committed.
- [x] Cross-repository impact is none.
- [ ] Current-head GitHub checks pass and final changed-file/review inspection is clear.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- Unified OTBM World Index #219 is merged at `97ff786663b30cafbd933799d8549a6dd3e3370b`.
- The supplied real map has SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`.
- Its local world index contains 17,972,761 tiles, 23,359,571 placements, 23,852 used item IDs and 9,339 map mechanics.
- OTBM script-resolution #104 parses active Action/MoveEvent registrations and preserves dynamic/unresolved evidence.
- Full storage transition semantics, NPC/spawn parsing and pathfinding remain later phases.
- Coordination policy #214 requires normal task branches to leave `docs/agents/ACTIVE_WORK.md` unchanged.

# Existing work reused

| Module/task/PR | Reuse | Why it fits |
|---|---|---|
| Unified OTBM World Index / #219 | bounded item/mechanic/position/region queries | Provides exact map evidence without rescanning OTBM. |
| OTBM script resolution / #104 | Action/MoveEvent registration and runtime statuses | Prevents a competing registration parser and preserves unresolved semantics. |
| Factual renderer / #154/#161 | optional bounded visual context | Visual evidence remains optional review material, not correctness proof. |

# Ownership and overlap check

- Open PR/task search showed no competing Quest Map Validator implementation.
- Specific tutorial quest PRs own gameplay files, not validator implementation paths.
- The branch does not edit `ACTIVE_WORK.md`, maps, assets or active datapack behavior.

# Implemented behavior

- Source-only `scan` command requires explicit include globs and records file hashes, lines and contexts.
- Static evidence includes AID, UID, item IDs, positions, teleport destinations and storage reads/writes.
- Direct aliases rooted at `Storage`, including `tutorialStorage.ZirellaQuestLog`, are canonicalized without evaluating Lua.
- `validate` correlates evidence with a memory-mapped `.widx` and optional script-resolution report.
- AID/UID conflicts and reviewed-unresolved statuses are preserved.
- Item IDs absent from static OTBM remain unresolved because rewards/inventory/dynamic creation may not be map placements.
- Generic missing `Position()` values remain unresolved; missing explicit registrations and teleport destinations are script-only.
- Optional regions report unreferenced map AID/UID/teleport mechanics with bounded samples.
- JSON outputs are atomic and symlink output targets are rejected.

# Work log

## 2026-07-13T00:18:00+02:00

- Created the phase-two branch and draft PR #225.
- Confirmed reuse boundaries with World Index and script-resolution.

## 2026-07-13T06:52:00+02:00

- Added source scanner, map correlation library, CLI, tests and initial documentation.
- Removed a non-portable test dependency on `/mnt/data/otbm_world_impl`; tests now compile the existing native scanner or consume an explicit scanner path.
- Added the versioned JSON Schema and dedicated workflow.

## 2026-07-13T07:00:00+02:00

- Diagnosed the first evidence-smoke failure as a real CLI import defect: the World Index CLI exports `position`, not `position_from_text`.
- Corrected the import and added `WorldIndexError` to the fail-closed CLI boundary.
- Dedicated workflow run `29230595250` passed all scanner/test/schema/evidence/artifact steps.

## 2026-07-13T07:05:00+02:00

- Workflow run `29230690806` passed and published both source evidence and a local-correlation toolkit.
- Built the real map index outside Git in 40.21 seconds with peak RSS 418,956 KiB.
- Correlated Zirella tutorial evidence against region `32055,32265,7 -> 32090,32295,7`.
- The bounded review found six confirmed source/map facts and ten neighboring map-only mechanics; those map-only entries are review candidates, not proven defects.

## 2026-07-13T09:10:00+02:00

- Hardened semantics after real-map review: missing static item placements and generic positions no longer create false script-only defects.
- Added direct Storage alias resolution, atomic output and symlink rejection.
- Expanded focused coverage and updated schema, workflow, documentation, catalogue and changelog.
- Current-head CI is running; final real-map correlation will be repeated from the hardened evidence artifact before merge.

# Decisions

| Decision | Reason/evidence |
|---|---|
| Split source evidence generation from private-map correlation | CI can inspect repository sources while `.otbm`/`.widx` remain local. |
| Require explicit source selection | Automatically grouping a datapack into one quest would create false associations. |
| Reuse script-resolution output | Avoids competing handler classifications. |
| Treat map absence conservatively | Static OTBM cannot prove reward/item registry validity or the semantics of every position literal. |
| Keep storage handling to read/write inventory | Full transition and reachability graphs are separate roadmap phases. |
| Publish a toolkit artifact | Enables reproducible local correlation without committing private maps or generated indexes. |

# Files and interfaces

| Path/interface | Purpose | Status |
|---|---|---|
| `tools/ai-agent/quest_map_validation.py` | static evidence and map correlation library | implemented |
| `tools/ai-agent/quest_map_validation_tool.py` | scan/validate CLI | implemented |
| `tools/ai-agent/test_quest_map_validation.py` | synthetic source/map contracts | implemented |
| `docs/ai-agent/QUEST_MAP_VALIDATION.schema.json` | report contract | implemented |
| `.github/workflows/quest-map-validation.yml` | focused tests and artifacts | implemented |
| `canary-quest-map-evidence-v1` | map-independent source evidence | implemented |
| `canary-quest-map-validation-v1` | correlated report | implemented |

# Validation and CI

| Commit/source | Check | Result |
|---|---|---|
| `0525d092...` | dedicated Quest Map Validator run `29230690806` | success |
| `0525d092...` | focused tests, Python compile, schema syntax, evidence invariants, both artifacts | success |
| supplied real map | world-index build and Zirella region correlation | passed outside Git |
| current hardened head | dedicated workflow and required CI | running |

# Failed approaches and corrections

- The first test suite depended on a temporary `/mnt/data` implementation directory. It was replaced with self-contained compilation of the repository scanner.
- Initial workflow glob selection was made explicit to one known quest source for a deterministic smoke artifact.
- The CLI referenced a nonexistent `position_from_text` export. It now aliases the canonical `position` parser.
- Initial correlation treated every missing item/position as script-only. Real-map review showed that was overconfident, so those cases now remain unresolved unless map presence is semantically required.

# Risks and compatibility

- Runtime/data migration: none; read-only offline tool.
- False positives: reduced through explicit globs, conservative classifications and unresolved evidence.
- Dynamic Lua: retained as unresolved; never executed or guessed.
- Security: private map/index artifacts remain local; generated JSON is atomic and symlink targets are rejected.
- Backward compatibility: no existing report or runtime interface is changed.
- Rollback: revert PR #225; no persistent cleanup.

# Remaining work

1. Wait for current-head checks.
2. Download the hardened evidence/toolkit artifacts and repeat real-map correlation.
3. Review final changed files and review threads.
4. Mark PR #225 ready and merge after the required gate passes.
5. Archive this task in a documentation-only follow-up.

# Handoff

Read this task, `docs/ai-agent/QUEST_MAP_VALIDATION.md`, `OTBM_WORLD_INDEX.md` and `OTBM_SCRIPT_RESOLUTION.md`. Do not edit `ACTIVE_WORK.md`, create another OTBM parser, commit `.otbm`/`.widx`, promote unresolved evidence to handled, or mix gameplay fixes into this validator PR.

# Completion

- Final status: validating
- PR: #225
- Merge commit:
- Catalogue updated: yes
- Changelog updated: yes
- Archived at:
