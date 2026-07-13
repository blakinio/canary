---
task_id: CAN-20260714-real-tibia-evidence-sources
program_id: ""
coordination_id: REAL-TIBIA-SOURCES
status: merged
agent: "GPT-5.6 Thinking"
branch: docs/real-tibia-evidence-sources
base_branch: main
created: 2026-07-14T00:13:22+02:00
updated: 2026-07-14T00:28:30+02:00
last_verified_commit: "af338e2abb9a515774d35ee29c69aaaaebb6cc51"
risk: low
related_issue: ""
related_pr: "#300"
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

- [x] `docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md` exists and is self-contained.
- [x] The registry distinguishes target baseline, official evidence, maintained implementations, public donor fragments, narrative references and unverified claims.
- [x] CrystalServer `data-global`, Targuna and Newhaven evidence is recorded with explicit limitations.
- [x] Public OTLand candidates discovered in July 2026 are recorded with version labels, files, coordinates, known gaps and source URLs.
- [x] Agents receive a mandatory intake/audit procedure that reuses existing OTBM tools and forbids blind map replacement or datapack mixing.
- [x] Documentation content and final changed-file scope were reviewed on final head `af338e2abb9a515774d35ee29c69aaaaebb6cc51`.
- [x] Current-head GitHub checks were verified.
- [x] Module catalogue impact was recorded as none because no reusable code interface was added or changed.
- [x] Changelog impact was recorded as none because runtime behavior and architecture were unchanged.
- [x] Program queue/handoff impact was recorded as none; the active CrystalServer comparison program remained read-only.
- [x] Cross-repository impact was read-only evidence only.
- [x] Autonomous merge gate was satisfied.

# Confirmed context

- The only writable repository was `blakinio/canary`.
- `opentibiabr/canary`, `zimbadev/crystalserver`, OTLand, TibiaMaps and all other external sources remained read-only.
- Root policy forbids committing or modifying `.otbm`, `items.otb`, client assets or generated large reports.
- Existing deterministic OTBM tools were documented for reuse rather than duplicated.
- Active PR #299 owned the next OTBM tooling phase and PR #297 shared the CrystalServer comparison program record; neither overlapping path was modified.
- Feature branch was refreshed from `main` `c9b607bdc5b9253f3eaf75b0f4a513877b8a42d7` before PR creation.
- Local checkout and worktree inspection were unavailable in the connector-only environment; GitHub diff, workflow and PR state supplied the execution evidence.

# Existing work reused

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Unified OTBM World Index | Exact tiles, stacks, item IDs, AID/UID, house doors and teleports | `tools/ai-agent/otbm_world_index*` | Canonical binary evidence cache; no second OTBM parser. |
| Quest Map Validator | Correlate quest source facts with bounded map evidence | `tools/ai-agent/quest_map_validation*` | Prevents treating a donor map placement as proof of a working quest. |
| OTBM reachability | Validate walkability, teleports and reviewed floor transitions | `tools/ai-agent/otbm_reachability*` | Prevents visual-only route assumptions. |
| OTBM spawn/NPC validation | Correlate XML, definitions, dynamic creations and map geometry | `tools/ai-agent/otbm_spawn_npc*` | Required for region donors and companion XML. |
| Script-resolution audit | Resolve AID/UID/item/position handlers | `tools/ai-agent/otbm_script_resolution*` | Keeps unresolved mechanics explicit. |
| CrystalServer comparison program | Read-only implementation-difference evidence | `docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md` | Crystal code is a candidate source, not an authority over Canary. |

# Ownership and overlap check

- Program record: none; standalone documentation task.
- Open PRs inspected: all open PRs returned on 2026-07-14, especially #299 and #297.
- Active tasks inspected: `ACTIVE_WORK.md`, live PR metadata and task/program diffs exposed by overlapping PRs.
- Ownership checker: workflow run `29289449528`, `Validate active ownership`, succeeded on final head.
- Exclusive claims: the evidence registry and the active task record only.
- Shared claims: none.
- Read-only dependencies: governance docs, OTBM roadmap and CrystalServer comparison program.
- Overlaps: none for exclusive paths.
- Resolution: no active roadmap, catalogue or program file was changed.

# Delivered result

PR #300 added `docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md`, a durable 579-line registry covering:

- evidence-dimension-specific precedence;
- the exact supplied baseline map hash and observed counts;
- the correction that the baseline is pre-Targuna rather than proven Tibia 15.15;
- official Tibia and official-client-derived evidence boundaries;
- TibiaMaps geometry/pathfinding usage and limitations;
- OpenTibiaBR Canary upstream usage;
- CrystalServer `data-global`, Targuna and Newhaven provenance and audit rules;
- verified public OTLand candidates for Blue Valley, Canary 14.12, Azzilon, Candia, Rise of Podzilla, Rotten Blood and Oskayaat;
- an explicit watch/unverified classification for the inaccessible Winter Update 2026 thread;
- wiki and claim-only source boundaries;
- mandatory provenance, quarantine, compatibility, map, mechanics, reachability, spawn/NPC, asset, rendering and runtime evidence workflow;
- machine-readable audit-output expectations, lifecycle classifications and priority queue.

No runtime, datapack, map, item, asset, protocol, schema or production configuration changed.

# Work log

## 2026-07-14T00:13:22+02:00

- Changed: created `docs/real-tibia-evidence-sources` and claimed two unique documentation paths.
- Learned: active PR #299 owned OTBM roadmap work and PR #297 owned a narrow CrystalServer runtime candidate plus shared program updates.
- Failed/blocked: local Git/worktree inspection was unavailable.
- Result: a non-overlapping documentation-only path was selected.

## 2026-07-14T00:15:49+02:00

- Changed: refreshed the unpublished branch from `3290da23c18f378f124928e9a83019b187791e3f` to current `main` `c9b607bdc5b9253f3eaf75b0f4a513877b8a42d7`.
- Learned: `main` advanced during source research.
- Failed/blocked: none; no PR or branch consumer existed yet.
- Result: avoided an unnecessary merge commit.

## 2026-07-14T00:17:54+02:00

- Changed: added the evidence registry and opened draft PR #300.
- Learned: evidence must be ranked by dimension; no single public source proves geometry, mechanics, spawns and runtime parity together.
- Failed/blocked: OTLand Winter Update 2026 thread body remained inaccessible, so it was classified as watch/unverified.
- Result: exact two-file diff reviewed and PR moved to ready.

## 2026-07-14T00:26:32+02:00

- Changed: verified final CI, reviews and diff, then squash-merged PR #300.
- Learned: repository CI emitted the full Linux Release even for this documentation-only change.
- Failed/blocked: none.
- Result: registry merged as `de89067565bddc59768cfd043062e7957db0d7a9`.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Create a standalone registry under `docs/agents/` | It is durable agent memory and avoided active roadmap/program conflicts. | none |
| Rank evidence by dimension rather than one global source order | A minimap can support geometry but not AID/UID, quest logic or spawn timing. | none |
| Record OTLand packages as audit candidates only | Thread labels and screenshots do not prove completeness, compatibility or Real Tibia parity. | none |
| Describe the current map as pre-Targuna rather than definitively 15.15 | OTBM has no trustworthy semantic release label and no independent provenance proved 15.15. | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Final status |
|---|---|---|---|
| `docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md` | exclusive | Durable external evidence/source registry and agent workflow | merged |
| `docs/agents/tasks/active/CAN-20260714-real-tibia-evidence-sources.md` | exclusive | Task ownership, decisions, validation and handoff | moved to archive |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `af338e2abb9a515774d35ee29c69aaaaebb6cc51` | final changed-file and content review | passed | Exactly two claimed documentation files; 791 additions and no deletions before squash. |
| `af338e2abb9a515774d35ee29c69aaaaebb6cc51` | forbidden-path review | passed | No `.otbm`, `items.otb`, asset, active datapack, runtime or production path changed. |
| `af338e2abb9a515774d35ee29c69aaaaebb6cc51` | Agent Task Ownership run `29289449528` | passed | `Validate active ownership` completed successfully. |
| `af338e2abb9a515774d35ee29c69aaaaebb6cc51` | CI run `29289451204` | passed | Detect Build Scope, Fast Checks, Lua Tests, Linux Release and Required succeeded. |
| `af338e2abb9a515774d35ee29c69aaaaebb6cc51` | PR reviews and threads | passed | No reviews requesting changes and zero unresolved review threads. |

# Failed approaches and dead ends

- Repository code search was not indexed for `blakinio/canary`; exact files and live PR metadata were used instead.
- The OTLand Winter Update 2026 thread returned a cache miss through the available reader; only forum-index metadata and the exact thread URL were recorded.

# Risks and compatibility

- Runtime: none; documentation only.
- Data/migration: none; no binaries or datapack files changed.
- Security: external archives remain untrusted; the registry requires quarantine, hashes and content inventory.
- Backward compatibility: none.
- Cross-repo rollout: none; external repositories remain read-only.
- Rollback: revert merge commit `de89067565bddc59768cfd043062e7957db0d7a9`.

# Remaining work

None for this task. New discoveries should update the registry through separate bounded tasks and PRs.

# Handoff

## Start here

Read `docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md` before proposing any Real Tibia map/datapack import or parity task.

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

- Final status: merged
- PR: #300
- Final reviewed head: `af338e2abb9a515774d35ee29c69aaaaebb6cc51`
- Merge commit: `de89067565bddc59768cfd043062e7957db0d7a9`
- Program record updated: not applicable
- Catalogue updated: not required
- Changelog updated: not required
- Archived at: `docs/agents/tasks/archive/CAN-20260714-real-tibia-evidence-sources.md`
