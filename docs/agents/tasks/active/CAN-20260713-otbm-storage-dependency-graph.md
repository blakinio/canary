---
task_id: CAN-20260713-otbm-storage-dependency-graph
program_id: ""
coordination_id: "OTS-OTBM-VALIDATION"
status: ready-for-review
agent: "GPT-5.6 Thinking"
branch: feat/otbm-storage-dependency-graph
base_branch: main
created: 2026-07-13T23:55:00+02:00
updated: 2026-07-14T00:45:00+02:00
last_verified_commit: "28897bcc4171e9a057621b2c89e2802df9fd0162"
risk: medium
related_issue: ""
related_pr: "#299"
depends_on:
  - "merged Quest Map Validator #225/#236"
  - "merged OTBM reachability validator #274/#277"
  - "merged OTBM spawn/NPC validator #286/#290"
blocks:
  - "Phase 6 semantic OTBM diff"
  - "Phase 7 geometry and consistency audit"
  - "Phase 8 safe bounded OTBM patch writer"
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
    - docs/agents/tasks/active/CAN-20260713-otbm-storage-dependency-graph.md
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
- [x] Refresh onto latest reviewed `main` while retaining concurrent achievement/evidence-source work.
- [ ] Final contents-API head checks pass, no review threads remain, and #299 is squash-merged.
- [ ] Archive the task in a separate lifecycle PR.

# Delivered behavior

`canary-otbm-storage-graph-v1` revalidates every selected source SHA-256 and path, inventories normalized operations, emits per-namespace nodes and directly proven transitions, preserves unresolved expressions, and optionally attaches handler/map/actor/geometry context. Missing selected-scope readers/writers are informational. Backward literal transitions and incompatible outputs for the same exact prerequisite are warnings.

The implementation does not create another OTBM parser, pathfinder, renderer or broad source selector. Lua, callbacks and persisted state are not executed or simulated.

# Validation

## Isolated checks

- 19 focused unit tests: passed.
- Python compilation: passed.
- schema syntax and representative `jsonschema` validation: passed.

These are isolated-file checks, not a local repository checkout or gameplay proof. Local Git remains unavailable because `github.com` cannot be resolved from the shell.

## GitHub-validated heads

Head `e0dcc7f80eedcb15f5a4d9c7d37fd66a613235e3`:

- OTBM Storage Graph `29289762803`: success;
- Agent Task Ownership `29289762881`: success;
- AI Agent Tools `29289762840`: success;
- OTBM Map Tools `29289762813`: success;
- repository CI `29289763132`: success.

Ready head `b1a2c2fe5d2478cf94d55fcb9b589baf5f4d439a`:

- OTBM Storage Graph `29289866801`: success;
- Agent Task Ownership `29289866798`: success;
- AI Agent Tools `29289866811`: success;
- OTBM Map Tools `29289866866`: success;
- autofix.ci `29289905094`: success;
- repository CI `29289905234`: success;
- Linux Release job `86951199888`: success;
- Required job `86952155215`: success;
- review threads: zero.

The branch was refreshed onto `main` `752595ae22dc4b8f1ff70d07bae489ceb559b14c`, preserving unrelated current-main ConditionLight, achievement and evidence-source work. Merge head `28897bcc4171e9a057621b2c89e2802df9fd0162` was ahead and behind by 0. This contents-API-only task update triggers the final required-status gate over that tree plus this record.

Representative The Beginning/Zirella contract smoke:

```text
files: 1
operations: 23
nodes: 2
transitions: 0
unresolved: 0
findings: 1 informational write-only-in-selected-scope
ok: true
complete: true
sourceDigest: e995eeaa2916ffb6aee8f8867d97674d8812fe83b77f9f0e77e69b127bfa3d7c
```

Artifact ID `8294353648`, digest `sha256:ad9a3fd6b8627c58159f81187b4f725a0dbe5a02f54f7bb0a9a7b038ed205e02`.

# Work log

- 2026-07-13: claimed Phase 5 after overlap searches and opened draft #299.
- 2026-07-14: implemented the graph, tests, schema, docs, ADR and workflow; repaired the catalogue after an intermediate API overwrite before any merge; verified the final 15-file diff; refreshed as concurrent `main` advanced; preserved all unrelated current-main files.

# Risks and compatibility

- Offline read-only tooling only; no runtime/data migration.
- Dynamic abstractions can be missed and remain unresolved.
- Phase 2–4 contracts remain backward compatible.
- Rollback is a squash revert with no persistent cleanup.
- No cross-repository rollout.

# Remaining work

1. Verify this final head and zero review threads.
2. Squash-merge #299 with an expected-head guard.
3. Archive Phase 5 separately.
4. Start Phase 6 from then-current `main` after fresh overlap checks.

# Completion

- Final status: ready-for-review
- PR: #299
- Final feature head: pending final contents-API checks
- Merge commit:
- Cleanup PR:
- Archived at:
