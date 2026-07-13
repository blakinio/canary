---
task_id: CAN-20260713-otbm-spawn-npc-validator
program_id: ""
coordination_id: "OTS-OTBM-VALIDATION"
status: completed
agent: "GPT-5.6 Thinking"
branch: feat/otbm-spawn-npc-validator
cleanup_branch: docs/archive-otbm-spawn-npc-validator
base_branch: main
created: 2026-07-13T22:00:00+02:00
completed: 2026-07-13T22:54:00+02:00
last_verified_commit: "40ce55b791e11b2344a7c9662675ab4e3e15f31f"
merge_commit: "360d79ebad5802edd4d89e99d0f210ab19b36b60"
risk: medium
related_issue: ""
related_pr: "#286"
cleanup_pr: "pending"
owned_paths: []
modules_touched:
  - OTBM spawn, boss and NPC validator
reuses:
  - Unified OTBM World Index
  - canary-otbm-reachability-v1
  - active monster/NPC type registrations
public_interfaces:
  - canary-otbm-spawn-npc-evidence-v1
  - canary-otbm-spawn-npc-validation-v1
  - OTBM spawn/NPC CLI
cross_repo_tasks: []
---

# Result

Phase 4 of the OTBM tooling programme was implemented and squash-merged through PR #286. The result is a deterministic read-only validator for explicit active monster/NPC companion XML, creature definitions, literal dynamic creation evidence and bounded map geometry correlation.

It reuses the existing World Index and Phase 3 reachability report. It does not introduce another OTBM parser, pathfinder, resolver, renderer or map writer.

# Final feature state

- Repository: `blakinio/canary`.
- Feature branch: `feat/otbm-spawn-npc-validator`.
- Feature PR: #286.
- Final feature head: `40ce55b791e11b2344a7c9662675ab4e3e15f31f`.
- Squash merge: `360d79ebad5802edd4d89e99d0f210ab19b36b60`.
- Base immediately before merge: `ded1830b143388d65c895ad30918faf128df66ed`.
- Final compare state: ahead, behind by 0.
- Final changed files: 14.
- Review threads: zero.
- Submitted reviews: zero.
- `docs/agents/ACTIVE_WORK.md`: not edited.

# Delivered contracts and behavior

- source evidence format `canary-otbm-spawn-npc-evidence-v1`;
- bounded map report `canary-otbm-spawn-npc-validation-v1`;
- explicit active datapack root and companion XML selection;
- source path/symlink confinement, DTD/entity rejection and bounded inputs;
- runtime coordinate policy `centerx + x`, `centery + y`, `centerz`;
- inclusive-square radius checks;
- conservative monster/NPC definition resolution;
- separate `rewardBoss` and literal non-empty Bosstiary spawn-boss evidence;
- NPC runtime interval rejection and rate-dependent monster interval evidence;
- literal `Game.createMonster` / `Game.createNpc` inventory without Lua execution;
- dynamic calls without literal positions remain unresolved and explicitly global to the selected datapack;
- exact static/dynamic overlap evidence;
- World Index tile-existence correlation;
- Phase 3 strict/optimistic geometry reuse;
- fail-closed handling of truncated Phase 3 diagnostics;
- atomic output, overwrite protection and symlink rejection;
- public facade, CLI, schemas, 18 focused tests, documentation, ADR and dedicated workflow.

# Final source-scan evidence

The selected active `data-otservbr-global` scan observed:

- 2 explicit spawn XML files;
- 2,692 definition files and 2,688 resolved definitions;
- 52,903 spawn groups;
- 84,294 static placements: 83,286 monsters and 1,008 NPCs;
- 1,781 dynamic-source files;
- 461 dynamic creation calls: 151 literal and 310 unresolved;
- 318 findings: 2 errors and 316 warnings;
- 356 literal reward-boss definitions;
- 0 literal non-empty Bosstiary-class spawn-boss definitions.

The two errors are one underlying duplicate active NPC type: canonical `harlow` in `npc/harlow.lua` and `npc/harlow_trade.lua`, causing static Harlow at `32836,31364,7` to resolve to both definitions. This remains evidence for a separate gameplay review; Phase 4 did not delete or rewrite either source.

One exact static/dynamic overlap was recorded for `bone capsule` at `33485,32333,14`. Nonliteral calls remain unresolved.

# Private-map bounded smoke

External artifacts only:

- map SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`;
- WIDX SHA-256 `6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a`;
- WIDX size 842,280,592 bytes;
- 17,972,761 tiles, 23,359,571 placements and 9,339 mechanic placements;
- build wall time 31.65 seconds; peak RSS 417,512 KiB.

Harlow bounds `32820,31350,7` through `32850,31380,7`:

- exact Harlow tile exists and is strict/optimistic walkable;
- placement is `conflicting-definition` solely because both active Harlow sources resolve;
- nine other static placements are confirmed;
- Phase 3 separately found seven indexed teleports targeting `0,0,0`; no map change was authorized.

Bone Capsule bounds `33470,32320,14` through `33500,32350,14`:

- static placement and literal quest-side dynamic creation at `33485,32333,14` are confirmed;
- target tile is strict/optimistic walkable;
- bounded Phase 3 report contains no transition/mechanic errors.

No private map, WIDX, appearances binary, client asset or generated report was committed.

# Final-head workflow evidence

Head `40ce55b791e11b2344a7c9662675ab4e3e15f31f`:

- OTBM Spawn and NPC Validation `29283580455`: success; job `86930499868` succeeded;
- Agent Task Ownership `29283580606`: success;
- AI Agent Tools `29283580631`: success;
- OTBM Map Tools `29283580582`: success;
- ready-state autofix.ci `29283719806`: success;
- ready-state repository CI `29283719990`: success;
  - Detect Build Scope `86930966443`: success;
  - Fast Checks `86930966539`: success;
  - Lua Tests `86930966552`: success;
  - Linux Release `86931249627`: success;
  - Required `86932589537`: success.

Runtime/database/C++ test execution was skipped by path scope. No live gameplay proof is claimed.

# Safety boundary

- Dynamic Lua was never executed.
- Nonliteral names and positions remain unresolved.
- Static source/map matches are not runtime gameplay proof.
- No map, spawn XML, creature definition, quest script, protocol, database or production configuration was modified.
- No `.otbm`, `.widx`, appearances binary, client asset, generated report or render was committed.
- Upstream repositories were not modified.

# Compatibility and rollback

- Runtime/data migration: none.
- World Index, Quest Map Validator, script-resolution and Phase 3 contracts remain backward compatible.
- Cross-repository rollout: none.
- Rollback: squash-revert merge `360d79ebad5802edd4d89e99d0f210ab19b36b60`; no map or production cleanup is required.

# Durable programme state

- Phase 1: merged and archived through #219/#223.
- Phase 2: merged and archived through #225/#236.
- Phase 3: merged and archived through #274/#277.
- Phase 4: merged through #286; this record is its lifecycle archive.
- Phases 5–7: not started.
- Phase 8: blocked by semantic-diff and geometry safety gates.

The next programme task may start Phase 5 only from current `main`, after a fresh PR/task ownership search. It must consume Phase 2 quest evidence and Phase 4 creature/source evidence rather than creating another source scanner.

# Completion

- Final status: completed
- Feature PR: #286
- Final feature head: `40ce55b791e11b2344a7c9662675ab4e3e15f31f`
- Merge commit: `360d79ebad5802edd4d89e99d0f210ab19b36b60`
- Cleanup PR: pending
- Archived at: `docs/agents/tasks/archive/CAN-20260713-otbm-spawn-npc-validator.md`
