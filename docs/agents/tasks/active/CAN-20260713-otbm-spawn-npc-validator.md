---
task_id: CAN-20260713-otbm-spawn-npc-validator
program_id: ""
coordination_id: "OTS-OTBM-VALIDATION"
status: ready_for_review_pending_ci
agent: "GPT-5.6 Thinking"
branch: feat/otbm-spawn-npc-validator
base_branch: main
created: 2026-07-13T22:00:00+02:00
updated: 2026-07-13T23:05:00+02:00
last_verified_commit: "818b8d39f95609230bfbc80dffaa948164e8dbf4"
risk: medium
related_issue: ""
related_pr: "#286"
depends_on:
  - "merged and archived Unified OTBM World Index #219/#223"
  - "merged and archived Quest Map Validator #225/#236"
  - "merged and archived OTBM reachability validator #274/#277"
  - "merged OTBM script-resolution audit #104"
blocks:
  - "OTBM storage dependency graph phase"
  - "quest-specific spawn/NPC repair tasks requiring map evidence"
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_spawn_npc.py
    - tools/ai-agent/otbm_spawn_npc_validation.py
    - tools/ai-agent/otbm_spawn_npc_tool.py
    - tools/ai-agent/test_otbm_spawn_npc_validation.py
    - tools/ai-agent/test_otbm_spawn_npc_runtime_semantics.py
    - docs/ai-agent/OTBM_SPAWN_NPC_VALIDATION.md
    - docs/ai-agent/OTBM_SPAWN_NPC_EVIDENCE.schema.json
    - docs/ai-agent/OTBM_SPAWN_NPC_VALIDATION.schema.json
    - .github/workflows/otbm-spawn-npc-validation.yml
    - docs/agents/decisions/ADR-20260713-otbm-spawn-npc-evidence-boundary.md
    - docs/agents/tasks/active/CAN-20260713-otbm-spawn-npc-validator.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
    - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
  read_only:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/ACTIVE_WORK.md
    - tools/ai-agent/otbm_world_index.py
    - tools/ai-agent/otbm_reachability.py
    - tools/ai-agent/otbm_reachability_types.py
    - tools/ai-agent/otbm_reachability_transition.py
    - tools/ai-agent/otbm_reachability_graph.py
    - tools/ai-agent/otbm_reachability_analysis.py
    - src/creatures/monsters/spawns/spawn_monster.cpp
    - src/creatures/npcs/spawns/spawn_npc.cpp
    - src/creatures/monsters/monsters.cpp
    - data-otservbr-global/world/otservbr-monster.xml
    - data-otservbr-global/world/otservbr-npc.xml
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

# Goal

Deliver Phase 4 of the OTBM tooling roadmap: deterministic static evidence and bounded map correlation for active monster spawns, runtime Bosstiary bosses, NPC placements and literal dynamic creature creation without executing Lua, changing gameplay or creating another OTBM parser/pathfinder.

# Acceptance criteria

- [x] Start only after Phase 3 feature and lifecycle PRs are merged.
- [x] Use one explicit active datapack root and explicit companion spawn XML files.
- [x] Reject source path traversal, symlink escapes, DTD/entity XML and unbounded inputs.
- [x] Implement current runtime coordinate semantics from the C++ loaders: child x/y offsets and centerz floor.
- [x] Validate radius relationships using Canary's inclusive-square spawn zone.
- [x] Resolve active monster/NPC definition names conservatively and detect missing/conflicting definitions.
- [x] Keep `rewardBoss` evidence separate from runtime `MonsterType::isBoss()` Bosstiary classification.
- [x] Treat monster spawntime above one day as rate-dependent before the runtime clamp.
- [x] Inventory literal `Game.createMonster` / `Game.createNpc` calls and preserve dynamic calls as unresolved.
- [x] Correlate exact static/dynamic overlaps and mark quest-source dynamic evidence.
- [x] Consume World Index for exact tile existence.
- [x] Consume `canary-otbm-reachability-v1` for strict/optimistic walkability; do not duplicate geometry.
- [x] Fail closed when Phase 3 tile diagnostics are truncated.
- [x] Validate group centers, static placements and literal dynamic positions in one explicit bounded region.
- [x] Keep unpositioned dynamic calls explicitly global to the selected active datapack.
- [x] Produce versioned evidence and validation schemas, deterministic atomic JSON and bounded samples.
- [x] Add focused tests, dedicated CI, real active-datapack source scan, docs and ADR.
- [x] Publish implementation in draft PR #286 and inspect initial and corrected source evidence.
- [x] Build the canonical WIDX from the supplied private map and run two bounded Phase 3/4 smoke validations without committing private artifacts.
- [x] Update catalogue, changelog and authoritative roadmap.
- [ ] Final-head Phase 4, ownership, AI tools, map tools and repository CI pass.
- [ ] Refresh onto current main if required, confirm zero review threads and mergeability.
- [ ] Merge and archive this task in a separate lifecycle PR.

# Delivered behavior

- public facade `otbm_spawn_npc.py` over the bounded source scanner and Phase 3/World Index correlator;
- explicit active XML and definition source manifests with SHA-256;
- exact group center, child offset, runtime position, radius and interval evidence;
- missing/conflicting type definitions;
- separate literal `rewardBoss` and non-empty Bosstiary-class evidence;
- unresolved dynamic calls preserved without execution;
- exact literal static/dynamic overlap evidence;
- strict/optimistic tile classification from Phase 3 only;
- global-vs-bounded scope made explicit for dynamic calls without coordinates;
- atomic output, overwrite protection, symlink rejection and bounded inputs;
- schemas, CLI, focused tests, dedicated workflow, docs and ADR.

# Corrected active-datapack evidence

Head `818b8d39f95609230bfbc80dffaa948164e8dbf4`:

- OTBM Spawn and NPC Validation `29282539729`: success; job `86927034480` succeeded;
- Agent Task Ownership `29282539719`: success;
- AI Agent Tools `29282539775`: success;
- OTBM Map Tools `29282539774`: success;
- repository CI `29282539976`: success;
- artifact `8291860094`, digest `sha256:f11ee0dfe7d864357d52554bd86bd5ad96ad0deb037cc54806578623fe29a4be`.

The real read-only scan of explicit `data-otservbr-global` companion files observed:

- 2 spawn XML files;
- 2,692 definition files and 2,688 resolved definitions;
- 52,903 spawn groups;
- 84,294 static placements: 83,286 monsters and 1,008 NPCs;
- 1,781 dynamic-source files;
- 461 dynamic creation calls: 151 literal and 310 unresolved;
- 318 findings: 2 errors and 316 warnings;
- 356 literal reward-boss definitions;
- 0 literal non-empty Bosstiary-class spawn-boss definitions in the selected sources.

The two errors are one underlying duplicate active NPC type: canonical `harlow` in `npc/harlow.lua` and `npc/harlow_trade.lua`, causing the static Harlow placement at `32836,31364,7` to resolve to two definitions. This remains review evidence and no gameplay repair is included.

One exact static/dynamic overlap was confirmed for `bone capsule` at `33485,32333,14`; nonliteral calls remain unresolved.

# Private-map bounded smoke

External/private artifacts only:

- map SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`;
- WIDX SHA-256 `6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a`;
- WIDX size 842,280,592 bytes;
- 17,972,761 tiles, 23,359,571 placements and 9,339 mechanic placements;
- build wall time 31.65 seconds; peak RSS 417,512 KiB.

Harlow bounds `32820,31350,7` through `32850,31380,7`:

- the exact Harlow tile exists and is strict/optimistic walkable;
- the placement remains `conflicting-definition`, solely because both active Harlow sources resolve;
- nine other placements in the same region were confirmed;
- Phase 3 also found seven map teleports targeting `0,0,0`; these are separate unresolved map-mechanic findings and were not changed.

Bone Capsule bounds `33470,32320,14` through `33500,32350,14`:

- the static placement at `33485,32333,14` is confirmed;
- the literal quest-side dynamic creation at the same position is confirmed;
- the target tile exists and is strict/optimistic walkable;
- the Phase 3 report is valid with no transition/mechanic errors in the bounded region.

The private OTBM, WIDX, appearances and client assets were not committed.

# Safety boundary

- Dynamic Lua is never executed.
- Non-literal names/positions remain unresolved.
- Static source/map evidence is not runtime gameplay proof.
- No map, spawn XML, creature definition, quest script, protocol, database or production configuration is modified.
- No `.otbm`, `.widx`, appearances binary, client asset, generated report or render is committed.
- Upstream repositories remain read-only.
- `docs/agents/ACTIVE_WORK.md` is not edited.

# Remaining work

1. Publish the final facade/test/docs update and inspect every current-head workflow.
2. Refresh against current `main` if behind.
3. Check exact changed files, reviews, review threads and mergeability.
4. Mark ready and squash-merge with an exact expected-head guard.
5. Archive this task in a separate documentation-only lifecycle PR.

# Completion

- Final status: ready_for_review_pending_ci
- Feature PR: #286
- Merge commit:
- Archived at:
