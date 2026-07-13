---
task_id: CAN-20260713-otbm-storage-dependency-graph
program_id: ""
coordination_id: "OTS-OTBM-VALIDATION"
status: ready-for-review
agent: "GPT-5.6 Thinking"
branch: feat/otbm-storage-dependency-graph
base_branch: main
created: 2026-07-13T23:55:00+02:00
updated: 2026-07-14T00:30:00+02:00
last_verified_commit: "e0dcc7f80eedcb15f5a4d9c7d37fd66a613235e3"
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

Deliver Phase 5 of the OTBM tooling programme: a deterministic read-only storage dependency graph that consumes the existing Quest Map Validator and optional Phase 3/4 evidence, inventories exact storage operations and explicit stage transitions, preserves unresolved dynamic expressions, and never infers execution order from source proximity.

# Acceptance criteria

- [x] Consume `canary-quest-map-evidence-v1` rather than creating another broad source scanner.
- [x] Optionally consume Phase 2 validation, Phase 3 reachability and Phase 4 spawn/NPC reports as correlation evidence.
- [x] Inventory player storage reads, writes, comparisons and exact same-key increments/decrements.
- [x] Separate player storage, account storage, player KV, account KV, global storage, global KV and database namespaces.
- [x] Represent literal/symbolic keys and literal values deterministically; preserve dynamic keys/values as `unresolved`.
- [x] Emit explicit transition edges only where one enclosing source construct proves both prerequisite and resulting value.
- [x] Never infer execution order from line order, source proximity or file order.
- [x] Detect selected-scope read/write gaps, unproven prerequisite values, backward literal transitions and conflicting literal writers conservatively.
- [x] Preserve exact file/line/context provenance and source SHA-256 evidence.
- [x] Bound selected files/source bytes, operations, nodes, transitions, unresolved expressions and output samples.
- [x] Add atomic JSON output, overwrite protection and symlink rejection.
- [x] Add JSON Schema, documentation, ADR, focused tests and a dedicated workflow/artifact.
- [x] Update module catalogue, changelog and authoritative roadmap.
- [x] Confirm no map, WIDX, appearances binary, client asset, generated full report, gameplay, active datapack, protocol, persistence schema or production configuration is changed.
- [x] Refresh onto current `main` without losing concurrent achievement work.
- [ ] Final task-record-head required checks pass, no review threads remain, and the PR is squash-merged.
- [ ] Archive this task in a separate lifecycle PR.

# Confirmed context

- Write target is exactly `blakinio/canary`; every `opentibiabr/*` repository is read-only.
- Initial branch base was `7cc47983cc78e06587fee09d1dcc5cc597836ade`.
- The reviewed implementation was refreshed onto current `main` `c9b607bdc5b9253f3eaf75b0f4a513877b8a42d7` through merge head `e0dcc7f80eedcb15f5a4d9c7d37fd66a613235e3`; compare state was ahead and behind by 0.
- Open PR searches found no competing Phase 5–8 OTBM owner.
- `docs/agents/ACTIVE_WORK.md` remains untouched.
- Local Git access failed with `Could not resolve host: github.com`; repository mutations and current-head validation use GitHub APIs/Actions. No local checkout/full-suite claim is made.

# Delivered contract and behavior

`canary-otbm-storage-graph-v1` contains:

- input provenance and SHA-256 hashes;
- Phase 2 selected-source revalidation with path confinement and symlink rejection;
- normalized operations across player/account/global storage, player/account/global KV and narrow literal SQL evidence;
- per-namespace/key nodes;
- explicit same-key equality prerequisite-to-literal/delete/delta transitions;
- optional actor, handler, map and geometry correlation;
- conservative selected-scope findings and exact summary counts;
- unresolved dynamic keys/values;
- atomic output, overwrite protection and bounded samples.

The implementation is split into evidence types, call inventory, branch parsing, graph analysis, a public facade and CLI. It does not create a second OTBM parser, pathfinder, renderer or broad quest scanner.

# Evidence policy

- A read without a selected-scope writer is `external-or-unproven`, not automatically a defect.
- A write without a selected-scope read is `write-only-in-selected-scope`, not proof that the key is globally unused.
- A numeric decrease is warned only when one proven transition compares one literal value and writes a lower literal value.
- Writers conflict only when the same exact namespace/key/prerequisite has incompatible literal outputs.
- Inequalities, `else` negation, dynamic values and source proximity do not create exact edges.
- Lua, callbacks and persisted state are never executed or simulated.

# Validation and CI

## Isolated implementation checks

- `python -m unittest -v test_otbm_storage_graph.py`: 19 tests passed.
- `python -m py_compile otbm_storage_graph*.py test_otbm_storage_graph.py`: passed.
- schema JSON syntax and representative `jsonschema.validate`: passed.

These are isolated-file checks, not a repository checkout or gameplay proof.

## Validated current-main refresh head

Head `e0dcc7f80eedcb15f5a4d9c7d37fd66a613235e3`:

- OTBM Storage Graph `29289762803`: success;
- Agent Task Ownership `29289762881`: success;
- AI Agent Tools `29289762840`: success;
- OTBM Map Tools `29289762813`: success;
- repository CI `29289763132`: success;
- compare against `main`: ahead, behind by 0;
- changed files: exactly 15 expected workflow/source/schema/documentation/task paths;
- review threads before this task-only finalization: zero.

The dedicated workflow runs the focused suite, Python compilation, schema syntax, a real repository Phase 2 evidence scan, a representative Phase 5 graph, contract assertions, `jsonschema` validation and toolkit upload.

Artifact from prior validated head:

- name `otbm-storage-graph`;
- artifact ID `8294353648`;
- digest `sha256:ad9a3fd6b8627c58159f81187b4f725a0dbe5a02f54f7bb0a9a7b038ed205e02`.

Representative The Beginning/Zirella smoke:

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

This is a contract smoke, not a full-world progression audit.

# Work log

## 2026-07-13T23:55:00+02:00

- Created the current-main task branch and draft PR #299 after overlap searches.
- Recorded the unavailable local Git/DNS environment.

## 2026-07-14T00:15:00+02:00

- Implemented the graph library/facade, CLI, schema, documentation, evidence ADR, 19 focused tests and dedicated workflow.
- Split the implementation into bounded internal modules.
- Verified isolated tests, compilation and schema validation.

## 2026-07-14T00:30:00+02:00

- Updated catalogue, changelog and authoritative roadmap.
- Reviewed the exact 15-file feature diff and removed the temporary roadmap-edit workflow from the final diff.
- Refreshed the branch onto current `main` while preserving concurrent achievement files.
- Confirmed all workflows on refreshed head `e0dcc7f80eedcb15f5a4d9c7d37fd66a613235e3` passed and the branch is behind by 0.
- This task-only finalization commit triggers the final merge gate; its result must be checked before merge.

# Risks and compatibility

- Runtime/gameplay: none; offline read-only tooling.
- Persistence/database: no writes or migrations.
- Source parsing: dynamic helper abstractions can be missed; they remain unresolved.
- Compatibility: existing Phase 2–4 contracts remain unchanged.
- Cross-repository rollout: none.
- Rollback: squash-revert PR #299; no persistent cleanup is required.

# Remaining work

1. Verify final task-record-head workflows and zero review threads.
2. Mark PR #299 ready and squash-merge with an expected-head guard.
3. Archive Phase 5 in a separate lifecycle PR.
4. Start Phase 6 only from then-current `main` after a fresh overlap search.

# Completion

- Final status: ready-for-review
- PR: #299
- Final feature head: pending final task-record-head checks
- Merge commit:
- Cleanup PR:
- Archived at:
