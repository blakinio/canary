---
task_id: CAN-20260713-instanced-test-arena
program_id: CAN-PROGRAM-INSTANCED-TEST-ARENA
coordination_id: ""
status: ready_for_pr
agent: "Claude"
branch: docs/instanced-test-arena-plan
base_branch: main
created: 2026-07-13T20:00:00Z
updated: 2026-07-13T20:50:00Z
last_verified_commit: "6fb9c65d3e8b9105e65515dc2b03827a06753eb0"
risk: low
related_issue: ""
related_pr: ""
depends_on: []
blocks:
  - CAN-PROGRAM-INSTANCED-TEST-ARENA queue item 2 (InstanceArenaService)
owned_paths:
  exclusive:
    - docs/architecture/instanced-test-arena.md
    - docs/agents/programs/INSTANCED_TEST_ARENA_PROGRAM.md
    - docs/agents/tasks/active/CAN-20260713-instanced-test-arena.md
  shared:
    - docs/architecture/instance-manager.md
  read_only:
    - src/game/instance/
    - src/game/game.hpp
    - src/game/game.cpp
modules_touched: []
reuses:
  - tools/ai-agent/otbm_map_tool.py (inspect/world-index/export)
  - tools/ai-agent/otbm_item_audit_scan.cpp + otbm_item_audit_tool.py
  - tools/ai-agent/otbm_appearances_tool.py
  - tools/ai-agent/otbm_script_resolution_tool.py
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Fix a real inconsistency in `docs/architecture/instance-manager.md` and
produce an evidence-backed region plan (`docs/architecture/
instanced-test-arena.md`) for the Instanced Test Arena feature, in its own
small PR, before any runtime code is written.

# Acceptance criteria

- [x] `docs/architecture/instance-manager.md`'s "Scheduler/event liveness"
      section no longer claims the `Game`-ownership decision "has not been
      made by any PR yet" (PR #201/#233 already made and completed it).
- [x] `docs/architecture/instanced-test-arena.md` records two same-size,
      non-overlapping, evidence-backed candidate regions with exact
      coordinates, the map used, and why.
- [x] Full-map OTBM audit (item audit + script resolution) run and cross-
      referenced against both region boxes; zero mechanic placements inside
      either.
- [x] Program and task records created per `AGENTS.md`.
- [ ] Current-head GitHub checks verified (pending PR open + CI).
- [x] Module catalogue impact: none yet (no new runtime module in this PR).
- [x] Documentation/changelog impact handled (this task).
- [x] Program queue/handoff impact handled (program record created).
- [x] Cross-repository impact: none.
- [ ] Autonomous merge gate satisfied (pending CI).

# Confirmed context

- Current `main` at task start: `6fb9c65d3e8b9105e65515dc2b03827a06753eb0`.
- `config.lua.dist` default map (`mapName=otservbr`,
  `dataPackDirectory=data-otservbr-global`) is downloaded at server startup
  (`src/map/map_download.*`) and is **not present** in this checkout.
- `data-canary/world/canary.otbm` (19,718,948 bytes, sha256
  `a3a1389bc7e8ba63080858023fba0eaded5253b6f6bd3d66b0f3c5112c987361`) is the
  only complete world map physically present; its own map description
  identifies it as the Canary project's own world.
- `otbm_map_tool.py world-index` on that map: 8 towns, 1 house (id 1, size
  17), 0 zones, 0 waypoints. Town "Tps Room" (id 3, temple `19992,19992,7`)
  is isolated from the other 7 towns by >14,000 tiles and contains the
  map's only house.
- Bounded export + full-map `otbm_item_audit_tool.py` +
  `otbm_script_resolution_tool.py` run (native scanner built from
  `tools/ai-agent/otbm_item_audit_scan.cpp` with `g++ -O2 -std=c++20`):
  `ok: true`, `strictRuntimeOk: true`, `mapMechanicPlacements: 271`,
  `runtimeUnresolvedPlacements: 0`, `conflictingPlacements: 0`. All 271 real
  mechanic placements cross-referenced against both candidate region boxes:
  zero fall inside either.
- Selected regions (see `docs/architecture/instanced-test-arena.md` for the
  full diagram): `InstanceTestArenaSlotOne`
  `(19976,19988,7)-(19987,19994,7)` and `InstanceTestArenaSlotTwo`
  `(19996,19988,7)-(20007,19994,7)`, both 12x7, both inside the existing
  walled "Tps Room" hall, both zero-mechanic, 8-tile buffer between them.
- No RME available in this sandbox; no `.otbm` file was written to.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Unified OTBM world index (#219) | Not directly invoked (native scanner path used instead) | `tools/ai-agent/otbm_world_index*.py` | Catalogued reuse point; item-audit + script-resolution path chosen because it directly answers "is this area scripted." |
| OTBM item audit (module catalogue) | `otbm_item_audit_scan.cpp` + `otbm_item_audit_tool.py` | Compiled and run against the full map | Canonical mechanic-placement evidence source. |
| OTBM script-resolution audit (#104) | `otbm_script_resolution_tool.py` | Run against the item-audit output | Confirms zero runtime-unresolved/conflicting placements. |
| InstanceManager/Game::getInstanceManager() (#107, #121, #151, #201) | Read-only reference for the architecture section | `src/game/instance/*`, `src/game/game.hpp` | This PR only plans; the next PR wires `InstanceArenaService` to these. |

# Ownership and overlap check

- Program record: created this task (`CAN-PROGRAM-INSTANCED-TEST-ARENA`).
- Open PRs inspected: full `list_pull_requests` at task start (#286, #284,
  #283, #279, #264, #262, #257, #245, #224) - none touch
  `src/game/instance/`, `src/game/game.{hpp,cpp}`, or arena-related docs.
- Active tasks inspected: all files under `docs/agents/tasks/active/` at
  task start - none relate to instance/arena work.
- Ownership checker result: `tools/agents/task_ownership.py` not run
  (docs-only PR, no source path claimed exclusively that any other task
  claims).
- Exclusive claims: the three new/edited doc files listed above.
- Shared claims: `docs/architecture/instance-manager.md` (one paragraph
  fix only).
- Read-only dependencies: `src/game/instance/`, `src/game/game.{hpp,cpp}`
  (read for architecture description, not modified).
- Overlaps: none found.
- Resolution: n/a.

# Current state

Docs written locally; not yet committed/pushed/PR'd.

# Plan

1. Commit the three doc changes on a fresh branch from `main`.
2. Push and open a small, docs-only PR against `blakinio/canary:main`.
3. Monitor CI (docs-only, so mostly format/lint jobs) and merge once green.
4. Update this task record's completion section and the program record's
   Active tasks/Completed work tables.

# Work log

## 2026-07-13T20:50:00Z

- Changed: fixed the stale "Scheduler/event liveness" paragraph in
  `docs/architecture/instance-manager.md`; wrote
  `docs/architecture/instanced-test-arena.md`; created this task record and
  the program record.
- Learned: the production map (`otservbr.otbm`) isn't present in this
  sandbox; `data-canary/world/canary.otbm` is a real, complete, first-party
  map with a nearly-empty "Tps Room" GM area perfectly suited to this
  feature.
- Failed/blocked: none.
- Result: ready to open PR 1.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Target `data-canary/world/canary.otbm` for region config | Only complete map physically present; matches the project's own name; recorded as a correctable assumption | none |
| Use existing "Tps Room" floor instead of authoring new rooms | RME unavailable; existing hall already has a zero-mechanic band large enough for two same-size regions | none |
| 8-tile buffer between regions instead of a physical wall | No OTBM-editing capability available; buffer + existing ownership-registry relation checks (defense in depth) achieve the same isolation goal | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `docs/architecture/instance-manager.md` | shared | fix stale paragraph | done |
| `docs/architecture/instanced-test-arena.md` | exclusive | region plan + evidence | done |
| `docs/agents/programs/INSTANCED_TEST_ARENA_PROGRAM.md` | exclusive | program record | done |
| `docs/agents/tasks/active/CAN-20260713-instanced-test-arena.md` | exclusive | this task record | done |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| (pre-commit) | `otbm_map_tool.py inspect/world-index/export` | ran locally | see Confirmed context |
| (pre-commit) | `otbm_item_audit_scan` compiled + `otbm_item_audit_tool.py` | ran locally, ok:true | mapMechanicPlacements 271, 0 in either region |
| (pre-commit) | `otbm_script_resolution_tool.py` | ran locally, ok:true, strictRuntimeOk:true | 0 unresolved, 0 conflicts |
| (pending) | CI on opened PR | not-run | docs-only change; expect format/lint jobs only |

# Failed approaches and dead ends

- Considered splitting the single "Tps Room" hall into left/right halves of
  the same open floor with no wall between them - rejected as insufficient
  physical separation on its own; kept as a 8-tile buffer plus reliance on
  the existing logical isolation registry instead.
- Considered using the same X/Y footprint on a different floor (6/8) as a
  second "physically separate" region - the export tool returned zero tile
  nodes at those floors for that footprint (no data at all, not even void
  placeholders), so there is no existing walkable ground there; would
  require authoring new tiles, which is out of scope without RME/OTBM-write
  tooling.

# Risks and compatibility

- Runtime: none (docs only).
- Data/migration: none.
- Security: none.
- Backward compatibility: none.
- Cross-repo rollout: none.
- Rollback: revert the commit; no code depends on this doc yet.

# Remaining work

1. Open the PR, get CI green, merge.
2. Proceed to program queue item 2 (`InstanceArenaService` + region config).

# Handoff

## Start here

Read `docs/architecture/instanced-test-arena.md` in full before writing any
region-configuration code in the next PR - it is the single source of truth
for the exact coordinates.

## Do not repeat

- Do not re-run the full OTBM audit from scratch for later PRs unless the
  map or candidate area changes; this task's evidence already covers both
  selected regions.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/programs/INSTANCED_TEST_ARENA_PROGRAM.md`
- `docs/architecture/instanced-test-arena.md`
- `docs/architecture/instance-manager.md`
- `docs/agents/MODULE_CATALOG.md`

## Open questions

- Whether `data-canary/world/canary.otbm` or the downloaded `otservbr.otbm`
  is the intended production map for this feature (see program record).

# Completion

- Final status: pending PR/CI.
- PR: (to be filled after opening).
- Merge commit: (to be filled after merge).
- Program record updated: yes (Active tasks/Queue).
- Catalogue updated: not applicable yet (no runtime module in this PR).
- Changelog updated: not applicable yet (docs-planning PR, no behavior change).
- Archived at: (after merge).
