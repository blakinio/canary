---
task_id: CAN-20260714-real-tibia-evidence-sources
program_id: ""
coordination_id: REAL-TIBIA-SOURCES
status: active
agent: "GPT-5.6 Thinking"
branch: docs/real-tibia-evidence-sources
base_branch: main
created: 2026-07-14T00:13:22+02:00
updated: 2026-07-14T00:15:49+02:00
last_verified_commit: "c9b607bdc5b9253f3eaf75b0f4a513877b8a42d7"
risk: low
related_issue: ""
related_pr: ""
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
    - docs/agents/tasks/active/CAN-20260714-real-tibia-evidence-sources.md
  shared: []
  read_only:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/KNOWN_RISKS.md
    - docs/agents/BUILD_TEST_MATRIX.md
    - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
    - docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md
modules_touched:
  - agent evidence and provenance documentation
reuses:
  - Unified OTBM World Index
  - Quest Map Validator
  - OTBM teleport and reachability validator
  - OTBM spawn, boss and NPC validator
  - OTBM script-resolution audit
  - factual OTBM renderer
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Create one durable, evidence-ranked registry that tells future agents how to use CrystalServer, OTLand map attachments, official-client-derived data and community references when moving this Canary fork closer to Real Tibia.

# Acceptance criteria

- [ ] `docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md` exists and is self-contained.
- [ ] The registry distinguishes target baseline, official evidence, maintained implementations, public donor fragments, narrative references and unverified claims.
- [ ] CrystalServer `data-global`, Targuna and Newhaven evidence is recorded with explicit limitations.
- [ ] Public OTLand candidates discovered in July 2026 are recorded with version labels, files, coordinates, known gaps and source URLs.
- [ ] Agents receive a mandatory intake/audit procedure that reuses existing OTBM tools and forbids blind map replacement or datapack mixing.
- [ ] Documentation-only validation and final changed-file review complete.
- [ ] Current-head GitHub checks are verified.
- [ ] Module catalogue impact is recorded as none because no reusable code interface is added or changed.
- [ ] Changelog impact is recorded as none because runtime behavior and architecture are unchanged.
- [ ] Program queue/handoff impact is recorded as none; the active CrystalServer comparison program remains read-only for this task.
- [ ] Cross-repository impact is recorded as read-only evidence only.
- [ ] Autonomous merge gate is satisfied.

# Confirmed context

- The only writable repository is `blakinio/canary`.
- `opentibiabr/canary`, `zimbadev/crystalserver`, OTLand, TibiaMaps and all other external sources are read-only.
- Root policy forbids committing or modifying `.otbm`, `items.otb`, client assets or generated large reports.
- Current OTBM tooling already provides deterministic World Index, quest/map correlation, reachability, spawn/NPC validation, script resolution and factual rendering; this task must document reuse rather than invent another parser.
- Open PR #299 owns the next OTBM tooling phase and may edit roadmap/catalogue files; this task avoids those active paths.
- Open PR #297 shares the CrystalServer comparison program record; this task treats that program as read-only.
- Current `main` observed after refresh: `c9b607bdc5b9253f3eaf75b0f4a513877b8a42d7`.
- Local checkout, `git status`, branch tracking and worktree inspection are unavailable through the current connector-only environment; GitHub branch, PR, diff and CI state are authoritative.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Unified OTBM World Index | Exact tiles, stacks, item IDs, AID/UID, house doors and teleports | `tools/ai-agent/otbm_world_index*` | Canonical binary evidence cache; no second OTBM parser. |
| Quest Map Validator | Correlate quest source facts with bounded map evidence | `tools/ai-agent/quest_map_validation*` | Prevents treating a donor map placement as proof of a working quest. |
| OTBM reachability | Validate walkability, teleports and reviewed floor transitions | `tools/ai-agent/otbm_reachability*` | Prevents visual-only route assumptions. |
| OTBM spawn/NPC validation | Correlate XML, definitions, dynamic creations and map geometry | `tools/ai-agent/otbm_spawn_npc*` | Required for region donors and companion XML. |
| Script-resolution audit | Resolve AID/UID/item/position handlers | `tools/ai-agent/otbm_script_resolution*` | Keeps unresolved mechanics explicit. |
| CrystalServer comparison program | Read-only implementation-difference evidence | `docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md` | Crystal code is a candidate source, not an authority over Canary. |

# Ownership and overlap check

- Program record: none; this is a standalone documentation task.
- Open PRs inspected: all open PRs returned on 2026-07-14, especially #299 and #297.
- Active tasks inspected: `ACTIVE_WORK.md`, live PR metadata and the task/program diffs exposed by the overlapping PRs.
- Ownership checker result: pending GitHub CI after task publication.
- Exclusive claims: the new evidence registry and this task record only.
- Shared claims: none.
- Read-only dependencies: governance docs, OTBM roadmap and CrystalServer comparison program.
- Overlaps: none for exclusive paths.
- Resolution: proceed without changing active roadmap, catalogue or program files.

# Current state

Branch refreshed to current `main`; task record is published before the substantive registry document.

# Plan

1. Create the evidence-ranked registry with verified CrystalServer, TibiaMaps and OTLand entries.
2. Review the final file for unsupported claims, stale version conflation and forbidden operational guidance.
3. Open a draft PR, inspect the full diff and documentation checks, then mark ready and merge when the autonomous gate is satisfied.
4. Archive the task record in a separate post-merge cleanup task if repository convention requires it.

# Work log

## 2026-07-14T00:13:22+02:00

- Changed: created `docs/real-tibia-evidence-sources` and claimed two unique documentation paths.
- Learned: active PR #299 owns OTBM roadmap work and PR #297 owns a narrow CrystalServer runtime candidate plus shared program updates.
- Failed/blocked: local Git/worktree inspection is unavailable in this connector-only session.
- Result: a non-overlapping documentation-only path is available.

## 2026-07-14T00:15:49+02:00

- Changed: refreshed the unpublished branch from `3290da23c18f378f124928e9a83019b187791e3f` to current `main` `c9b607bdc5b9253f3eaf75b0f4a513877b8a42d7` before opening a PR.
- Learned: `main` advanced during source research.
- Failed/blocked: none; the branch had no PR or shared consumers, so a clean reset avoided an unnecessary merge commit.
- Result: implementation continues from current main.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Create a standalone registry under `docs/agents/` | It is durable agent memory and avoids active roadmap/program conflicts. | none |
| Rank evidence by dimension rather than one global source order | A minimap can be authoritative for explored geometry but says nothing about AID/UID, quest logic or spawn timing. | none |
| Record OTLand packages as audit candidates only | Thread labels and screenshots do not prove completeness, compatibility or Real Tibia parity. | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md` | exclusive | Durable external evidence/source registry and agent workflow | planned |
| `docs/agents/tasks/active/CAN-20260714-real-tibia-evidence-sources.md` | exclusive | Task ownership, decisions, validation and handoff | active |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| pending | Markdown/path review | not-run | Run after registry creation. |
| pending | `git diff --check` equivalent / repository fast checks | not-run | GitHub CI is required in the connector-only environment. |
| pending | Agent Task Ownership | not-run | Must pass on final head. |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- Repository code search is not indexed for `blakinio/canary`; exact files were opened directly and live PR metadata was used instead.
- The OTLand Winter Update 2026 thread currently returns a cache miss through the available web reader; only the forum index title/date/reply count and exact thread URL are verified.

# Risks and compatibility

- Runtime: none; documentation only.
- Data/migration: none; no binaries or datapack files change.
- Security: external archives may be hostile; registry requires download outside Git, hash capture and content inventory before use.
- Backward compatibility: none.
- Cross-repo rollout: external repositories remain read-only.
- Rollback: revert the documentation commit.

# Remaining work

1. Publish and review the registry document.
2. Open PR and verify current-head checks.
3. Merge after final diff/review gate.

# Handoff

## Start here

Read `docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md` after it is created; use it before proposing any Real Tibia map/datapack import or parity task.

## Do not repeat

- Do not create another OTBM parser or pathfinder.
- Do not treat a version label such as `15.x` or `15.25` as proof of full map/content coverage.
- Do not mix CrystalServer or OTLand datapacks directly into the active Canary datapack.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/MODULE_CATALOG.md`
- `docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md`
- `docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md`
- all overlapping active task records and PRs

## Open questions

- The exact downloadable contents of the OTLand Winter Update 2026 thread remain unverified because the thread body is not currently fetchable.

# Completion

- Final status: active
- PR:
- Merge commit:
- Program record updated: not applicable
- Catalogue updated: not required
- Changelog updated: not required
- Archived at:
