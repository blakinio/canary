---
task_id: CAN-20260713-otbm-storage-dependency-graph
program_id: ""
coordination_id: "OTS-OTBM-VALIDATION"
status: completed
agent: "GPT-5.6 Thinking"
branch: feat/otbm-storage-dependency-graph
base_branch: main
created: 2026-07-13T23:55:00+02:00
updated: 2026-07-14T08:54:00+02:00
completed: 2026-07-14T08:54:00+02:00
last_verified_commit: "b1e19e179eb32199cc6e14e68becd9cc99c91fca"
risk: medium
related_issue: ""
related_pr: "#299"
depends_on:
  - "merged Quest Map Validator #225/#236"
  - "merged OTBM reachability validator #274/#277"
  - "merged OTBM spawn/NPC validator #286/#290"
blocks: []
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_storage_graph.py
    - tools/ai-agent/otbm_storage_graph_types.py
    - tools/ai-agent/otbm_storage_graph_calls.py
    - tools/ai-agent/otbm_storage_graph_parser.py
    - tools/ai-agent/otbm_storage_graph_analysis.py
    - tools/ai-agent/otbm_storage_graph_tool.py
    - tools/ai-agent/test_otbm_storage_graph.py
    - docs/ai-agent/OTBM_STORAGE_GRAPH.md
    - docs/ai-agent/OTBM_STORAGE_GRAPH.schema.json
    - docs/agents/decisions/ADR-20260713-otbm-storage-evidence-boundary.md
    - .github/workflows/otbm-storage-graph.yml
    - docs/agents/tasks/archive/CAN-20260713-otbm-storage-dependency-graph.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
    - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
  read_only:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/ACTIVE_WORK.md
    - tools/ai-agent/quest_map_validation.py
    - tools/ai-agent/quest_map_validation_tool.py
    - tools/ai-agent/otbm_spawn_npc.py
    - tools/ai-agent/otbm_spawn_npc_validation.py
    - tools/ai-agent/otbm_reachability.py
    - tools/ai-agent/otbm_script_resolution.py
modules_touched:
  - OTBM storage dependency graph
reuses:
  - canary-quest-map-evidence-v1
  - canary-quest-map-validation-v1
  - canary-otbm-spawn-npc-evidence-v1
  - canary-otbm-spawn-npc-validation-v1
  - canary-otbm-reachability-v1
public_interfaces:
  - canary-otbm-storage-graph-v1
  - OTBM storage graph CLI
cross_repo_tasks: []
---

# Goal

Deliver Phase 5 as deterministic read-only storage dependency analysis over the existing Phase 2 selected source set, with optional Phase 3/4 context and no inferred runtime order.

# Completion state

Phase 5 feature PR #299 was squash-merged into `main`.

- Final feature head: `b1e19e179eb32199cc6e14e68becd9cc99c91fca`.
- Squash merge: `c7ecb321681d6c4dd80b23b380bd211062f52c90`.
- Feature branch: `feat/otbm-storage-dependency-graph` (historical; do not continue).
- Review threads on #299: zero.
- Rollback: revert squash merge `c7ecb321681d6c4dd80b23b380bd211062f52c90`; no persistence or map cleanup is required.
- Lifecycle cleanup branch: `docs/archive-otbm-storage-dependency-graph`.
- Lifecycle cleanup PR: pending creation in this branch; update before merge.

# Delivered behavior

`canary-otbm-storage-graph-v1` revalidates every selected source SHA-256 and path, inventories normalized operations, emits per-namespace nodes and directly proven transitions, preserves unresolved expressions, and optionally attaches handler/map/actor/geometry context. Missing selected-scope readers/writers are informational. Backward literal transitions and incompatible outputs for the same exact prerequisite are warnings.

The implementation does not create another OTBM parser, pathfinder, renderer or broad source selector. Lua, callbacks and persisted state are not executed or simulated.

# Final changed files in PR #299

1. `.github/workflows/otbm-storage-graph.yml`
2. `docs/agents/CHANGELOG.md`
3. `docs/agents/MODULE_CATALOG.md`
4. `docs/agents/decisions/ADR-20260713-otbm-storage-evidence-boundary.md`
5. `docs/agents/tasks/active/CAN-20260713-otbm-storage-dependency-graph.md`
6. `docs/ai-agent/OTBM_STORAGE_GRAPH.md`
7. `docs/ai-agent/OTBM_STORAGE_GRAPH.schema.json`
8. `docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md`
9. `tools/ai-agent/otbm_storage_graph.py`
10. `tools/ai-agent/otbm_storage_graph_analysis.py`
11. `tools/ai-agent/otbm_storage_graph_calls.py`
12. `tools/ai-agent/otbm_storage_graph_parser.py`
13. `tools/ai-agent/otbm_storage_graph_tool.py`
14. `tools/ai-agent/otbm_storage_graph_types.py`
15. `tools/ai-agent/test_otbm_storage_graph.py`

# Validation

## Isolated checks recorded by the feature task

- 19 focused unit tests: passed.
- Python compilation: passed.
- Schema syntax and representative `jsonschema` validation: passed.

These were isolated-file checks, not a local repository checkout or gameplay proof.

## Final feature-head GitHub workflows

Head `b1e19e179eb32199cc6e14e68becd9cc99c91fca`:

- OTBM Storage Graph run `29290869243`: success; job `86953920605` (`Validate storage dependency evidence`): success.
- Agent Task Ownership run `29290869213`: success.
- AI Agent Tools run `29290869239`: success.
- OTBM Map Tools run `29290869222`: success.
- autofix.ci run `29290869265`: success.
- repository CI run `29290869312`: success.
- Fast Checks job `86953937224`: success.
- Lua Tests job `86953937225`: success.
- Linux Release job `86954215612`: success.
- Required job `86955262538`: success.
- Review threads: zero.

Green CI proves only the checks executed for this commit; it is not live gameplay proof.

# Local checkout and DNS limitation

- Local checkout: unavailable.
- Command: `git ls-remote https://github.com/blakinio/canary.git HEAD`.
- Exact result: `fatal: unable to access 'https://github.com/blakinio/canary.git/': Could not resolve host: github.com`.
- After this confirmed failure, clone/fetch/pull/ls-remote were not repeated.
- Repository, PR, file, commit, workflow, job and review-thread verification used GitHub API.

# Acceptance criteria

- [x] Reuse `canary-quest-map-evidence-v1` source selection and hashes.
- [x] Optionally correlate Phase 2 validation, Phase 3 reachability and Phase 4 spawn/NPC evidence.
- [x] Inventory reads, writes, deletes, comparisons and exact same-key increments/decrements.
- [x] Keep player/account/global storage, KV and narrow database namespaces separate.
- [x] Preserve dynamic keys and values as unresolved.
- [x] Emit exact edges only for one enclosing same-key equality and one literal/delete/delta result.
- [x] Never infer callback/file/line execution order from proximity.
- [x] Emit conservative selected-scope findings and exact counts.
- [x] Preserve path, line, context and SHA-256 provenance.
- [x] Bound source bytes, operations, nodes, edges, unresolved expressions and samples.
- [x] Add atomic output, overwrite protection and symlink rejection.
- [x] Add schema, documentation, ADR, 19 focused tests and dedicated CI/artifact.
- [x] Update catalogue, changelog and authoritative roadmap.
- [x] Confirm no map, WIDX, asset, active datapack, gameplay, protocol, database schema or production configuration change.
- [x] PR #299 squash-merged.
- [x] Feature review threads resolved (zero).
- [x] Task moved from `tasks/active` to `tasks/archive` in a separate lifecycle branch.

# Work log

- 2026-07-13: claimed Phase 5 after overlap searches and opened draft #299.
- 2026-07-14: implemented the graph, tests, schema, docs, ADR and workflow; verified the 15-file scope; refreshed against advancing `main`; preserved unrelated work.
- 2026-07-14: verified #299 merged, its final head and merge commit, final workflows/jobs, zero review threads, exact changed files and presence on current `main`.
- 2026-07-14: moved this record to archive and prepared the lifecycle-only cleanup branch.

# Handoff

Phase 5 is complete. Do not reopen #299 or continue its historical branch. Phase 6 may start only after the lifecycle cleanup PR is merged and a fresh current-main/open-PR/active-task/ownership preflight is complete.
