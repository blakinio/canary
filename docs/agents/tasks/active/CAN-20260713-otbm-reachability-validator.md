---
task_id: CAN-20260713-otbm-reachability-validator
program_id: ""
coordination_id: "OTS-OTBM-VALIDATION"
status: active
agent: "GPT-5.6 Thinking"
branch: feat/otbm-reachability-validator
base_branch: main
created: 2026-07-13T18:43:00+02:00
updated: 2026-07-13T18:43:00+02:00
last_verified_commit: "444aa8ae13edc01c6e77b03139a43d386b437308"
risk: medium
related_issue: ""
related_pr: "pending"
depends_on:
  - "merged Unified OTBM World Index #219/#223"
  - "merged Quest Map Validator #225/#236"
  - "merged OTBM script-resolution audit #104"
  - "merged factual renderer/appearance catalogue tooling"
blocks:
  - "OTBM spawn/NPC validation phase"
  - "OTBM storage graph phase"
  - "OTBM semantic diff and geometry phases"
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_reachability.py
    - tools/ai-agent/otbm_reachability_tool.py
    - tools/ai-agent/test_otbm_reachability.py
    - docs/ai-agent/OTBM_REACHABILITY.md
    - docs/ai-agent/OTBM_REACHABILITY.schema.json
    - docs/ai-agent/OTBM_TRANSITIONS.schema.json
    - .github/workflows/otbm-reachability.yml
    - docs/agents/decisions/ADR-20260713-otbm-reachability-evidence-boundary.md
    - docs/agents/tasks/active/CAN-20260713-otbm-reachability-validator.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
    - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
  read_only:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/ACTIVE_WORK.md
    - tools/ai-agent/otbm_world_index.py
    - tools/ai-agent/otbm_world_index_tool.py
    - tools/ai-agent/otbm_appearances.py
    - tools/ai-agent/otbm_script_resolution.py
    - tools/ai-agent/otbm_renderer.py
    - docs/ai-agent/OTBM_WORLD_INDEX.md
    - docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md
    - docs/ai-agent/QUEST_MAP_VALIDATION.md
modules_touched:
  - OTBM reachability validator
reuses:
  - Unified OTBM World Index
  - appearances catalogue parser
  - OTBM script-resolution report
  - factual OTBM renderer contract
public_interfaces:
  - canary-otbm-reachability-v1
  - canary-otbm-transition-manifest-v1
  - OTBM reachability CLI
cross_repo_tasks: []
---

# Goal

Deliver Phase 3 of the OTBM tooling roadmap: a deterministic read-only validator for bounded teleport/floor-transition correctness and conservative player reachability without creating another OTBM parser or modifying any map.

# Acceptance criteria

- [ ] Analyze only explicit bounded regions and explicit origins/start-goal routes.
- [ ] Reuse `WorldIndex` for tiles, placements, mechanics, teleports and exact coordinates.
- [ ] Reuse object appearance flags for confirmed ground, unpassable, avoid and interactive-state evidence.
- [ ] Validate every indexed teleport source/destination in the selected region.
- [ ] Accept reviewed stairs/ladder/hole/rope/floor-change edges through a versioned transition manifest; never infer them from visual memory or item-name guesses.
- [ ] Correlate optional script-resolution placement status and preserve conflicting/unresolved evidence.
- [ ] Produce strict and optimistic reachability, with door/quest/dynamic/unknown uncertainty separated from confirmed geometry.
- [ ] Detect unreachable routes/mechanics, one-way transitions, destination dead ends and transition cycles.
- [ ] Prevent diagonal corner cutting when optional diagonal movement is enabled.
- [ ] Bound region size, route starts, routes, transitions, samples and path output.
- [ ] Write reports atomically and reject symlink outputs and provenance mismatches.
- [ ] Add focused tests, schemas, documentation, dedicated CI, catalogue/changelog/roadmap updates and a durable evidence-boundary ADR.
- [ ] Confirm no `.otbm`, `.widx`, `items.otb`, appearances binary, client asset, generated report/render, gameplay, protocol or production configuration is committed.
- [ ] Current-head required GitHub checks pass and autonomous merge gate is satisfied.

# Confirmed context

- Write target is exactly `blakinio/canary`; upstream repositories are read-only.
- Branch was created from `main`; latest repository commit observed immediately before branch creation was `444aa8ae13edc01c6e77b03139a43d386b437308`.
- Local Git access was attempted once with `git ls-remote https://github.com/blakinio/canary.git HEAD` and failed with `Could not resolve host: github.com`; GitHub API is the repository mutation path and no local checkout result will be claimed.
- Open PR search for OTBM/reachability/teleport/stairs/pathfinding ownership returned no overlap. Adjacent open work is Forge, achievements, Wheel and E2E; none owns the claimed paths.
- `ACTIVE_WORK.md` is stale and read-only for this task.
- Phases 1 and 2 are merged; roadmap Phases 3–8 remain unimplemented before this task.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Unified OTBM World Index #219 | memory-mapped exact tile/placement/mechanic/region queries | `tools/ai-agent/otbm_world_index.py` | Avoids rescanning and avoids a competing OTBM parser. |
| Appearances catalogue | object ground/unpassable/avoid/usable flags | `tools/ai-agent/otbm_appearances.py` | Supplies conservative geometry semantics from actual client metadata. |
| Script resolution #104 | placement runtime status | `OTBM_SCRIPT_RESOLUTION_REPORT.schema.json` | Distinguishes engine/direct handling, unresolved registrations and conflicts. |
| Factual renderer | review-only visual context | `tools/ai-agent/otbm_renderer.py` | Later users can render exact reported bounds without AI-generated map imagery. |

# Ownership and overlap check

- Program record: no separate structured program record exists; `docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md` is the authoritative programme handoff.
- Open PRs inspected: current user-owned open PR list plus targeted OTBM/reachability search; no matching ownership.
- Active tasks inspected: stale `ACTIVE_WORK.md`, targeted repository search, and live PRs.
- Ownership checker result: unavailable without a checkout; structured claims will be validated by Agent Task Ownership CI.
- Exclusive claims: new reachability source, CLI, tests, schemas, workflow, ADR and this task.
- Shared claims: narrow catalogue/changelog/roadmap entries.
- Read-only dependencies: World Index, appearances, script resolution, renderer and existing contracts.
- Overlaps: none confirmed.
- Resolution: dedicated branch and early draft PR; stop if CI discovers a structured ownership conflict.

# Current state

Task claimed. Architecture is fixed around strict/optimistic evidence and an explicit reviewed transition manifest; implementation is being prepared locally with synthetic fixtures because the repository checkout is unavailable.

# Plan

1. Publish the early draft PR.
2. Implement deterministic core/CLI and versioned schemas.
3. Add focused synthetic tests and workflow.
4. Update reusable-module and roadmap documentation.
5. Inspect full diff and current-head CI; repair failures until green.
6. Mark ready, merge, then archive this task in a separate lifecycle PR.

# Work log

## 2026-07-13T18:43:00+02:00

- Changed: created `feat/otbm-reachability-validator` and claimed exact paths.
- Learned: World Index already exposes tile stacks and teleport destinations; appearances expose `bank`, `unpassable`, `avoid`, `usable`, `multiUse` and `forceUse`; script-resolution placements provide exact status.
- Failed/blocked: local Git DNS is unavailable; no local repository checkout or real-map WIDX rebuild is currently possible.
- Result: no parser duplication is required; implementation can be a read-only consumer of existing contracts.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Require explicit reviewed manifests for stairs/holes/ladders | Item appearance flags do not prove cross-floor destination offsets; guessing would create false routes. | `ADR-20260713-otbm-reachability-evidence-boundary.md` planned |
| Emit strict and optimistic reachability | Doors, quest gates, dynamic scripts and unknown appearance state must remain visible instead of being flattened into passable/blocked. | same ADR |
| Default to four-direction movement | Prevents diagonal corner cutting and avoids claiming exact client movement semantics without explicit opt-in. | same ADR |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `tools/ai-agent/otbm_reachability.py` | exclusive | core classification, transitions, graph and reporting | local implementation in progress |
| `tools/ai-agent/otbm_reachability_tool.py` | exclusive | bounded CLI | local implementation in progress |
| `canary-otbm-reachability-v1` | exclusive | machine-readable output | planned |
| `canary-otbm-transition-manifest-v1` | exclusive | reviewed explicit floor-transition evidence | planned |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| local uncommitted | `python -m unittest -v test_otbm_reachability.py` | passed | 15 synthetic tests; repository checkout unavailable, so this is not current-main/full-suite evidence |
| local uncommitted | `python -m py_compile otbm_reachability.py otbm_reachability_tool.py test_otbm_reachability.py` | passed | local isolated files only |
| pending | dedicated GitHub workflow and required CI | not-run | implementation not published yet |

# Failed approaches and dead ends

- Local `git ls-remote` failed once due DNS; it will not be repeatedly retried.
- Automatic stairs/ladder inference from sprite names/visuals was rejected because it cannot prove destination offsets or direction.

# Risks and compatibility

- Runtime: none; offline read-only tooling.
- Data/migration: none.
- Security: input hashes, bounded memory/output, atomic writes and symlink rejection are required.
- Backward compatibility: existing World Index, Quest Map Validator, script-resolution and renderer contracts remain unchanged.
- Cross-repo rollout: none; no OTClient protocol or client-code change.
- Rollback: squash-revert the tooling PR; no map or production state changes.

# Remaining work

1. Open the draft PR and publish implementation files.

# Handoff

## Start here

Continue only `feat/otbm-reachability-validator` and its draft PR. Read this task and the exact dependencies listed above.

## Do not repeat

Do not create a new OTBM parser, infer floor transitions from imagery, execute dynamic Lua, modify the map, commit binary assets or edit `ACTIVE_WORK.md`.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md`
- `tools/ai-agent/otbm_world_index.py`
- `tools/ai-agent/otbm_appearances.py`
- `docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md`

## Open questions

- A real-map smoke requires an existing local `.widx` plus compatible appearances catalogue; absence of those artifacts must remain an explicit evidence limitation rather than prompting asset upload to GitHub.

# Completion

- Final status: active
- PR: pending
- Merge commit:
- Program record updated: pending
- Catalogue updated: pending
- Changelog updated: pending
- Archived at:
