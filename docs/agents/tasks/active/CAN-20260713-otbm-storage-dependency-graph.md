---
task_id: CAN-20260713-otbm-storage-dependency-graph
program_id: ""
coordination_id: "OTS-OTBM-VALIDATION"
status: active
agent: "GPT-5.6 Thinking"
branch: feat/otbm-storage-dependency-graph
base_branch: main
created: 2026-07-13T23:55:00+02:00
updated: 2026-07-14T00:15:00+02:00
last_verified_commit: "1b045453886b9cedb8e039d2b0b2511db2772c22"
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

Deliver Phase 5 of the OTBM tooling programme: a deterministic read-only storage dependency graph that consumes the existing Quest Map Validator and spawn/NPC evidence, inventories exact storage operations and explicit stage transitions, preserves unresolved dynamic expressions, and never infers execution order from source proximity.

# Acceptance criteria

- [x] Consume `canary-quest-map-evidence-v1` rather than creating another broad quest/source scanner.
- [x] Optionally consume `canary-quest-map-validation-v1`, `canary-otbm-spawn-npc-evidence-v1`, `canary-otbm-spawn-npc-validation-v1` and `canary-otbm-reachability-v1` as correlation evidence.
- [x] Inventory player storage reads, writes, comparisons and exact same-key increments/decrements.
- [x] Separate player storage, account storage, player KV, account KV, global storage and database namespaces.
- [x] Represent literal/symbolic keys and literal values deterministically; keep dynamic keys/values as `unresolved`.
- [x] Emit explicit transition edges only where one source construct proves both prerequisite and resulting value.
- [x] Never infer execution order from line order or source proximity.
- [x] Detect read-only/write-only keys, unproven prerequisite values, backward literal transitions and conflicting literal writers conservatively.
- [x] Preserve exact file/line/context provenance and source SHA-256 evidence.
- [x] Bound input documents, source files, findings, nodes and edge samples while retaining exact counts.
- [x] Add atomic JSON output, overwrite protection and symlink rejection.
- [x] Add JSON Schema, documentation, ADR, focused tests and a dedicated workflow/artifact.
- [ ] Update module catalogue, changelog and authoritative roadmap.
- [x] Confirm no map, WIDX, appearances binary, client asset, generated full report, gameplay, active datapack, protocol, persistence schema or production configuration is changed.
- [ ] All final-head required checks pass, no review threads remain, and the PR is squash-merged.
- [ ] Archive this task in a separate lifecycle PR.

# Confirmed context

- Write target is exactly `blakinio/canary`; every `opentibiabr/*` repository is read-only.
- Branch base is current `main` commit `7cc47983cc78e06587fee09d1dcc5cc597836ade`.
- Open PR searches for OTBM storage graph, semantic diff, geometry audit and patch writer found no overlapping owner.
- Phases 1–4 are merged and archived; Phase 4 cleanup #290 is present on `main`.
- `docs/agents/ACTIVE_WORK.md` is read-only for this normal feature branch.
- Local Git access was attempted with `git ls-remote https://github.com/blakinio/canary.git HEAD` and failed with `Could not resolve host: github.com`; repository mutations use the GitHub API and this limitation does not count as local validation.

# Architecture and reuse

| Existing contract | Reuse in Phase 5 | Boundary |
|---|---|---|
| Quest Map Validator | selected source files, hashes, canonical storage keys, read/write evidence and quest map classifications | Phase 5 inspects only those already selected files for operation syntax missing from v1 evidence; it does not broaden source selection. |
| Spawn/NPC validator | creature/NPC definition, placement and literal dynamic-creation evidence | Provides actor/placement context only; it does not prove a storage handler executes. |
| Reachability validator | bounded geometry classifications | Optional contextual evidence only; reachable geometry is not storage progression proof. |
| Script resolver | handler/event registration evidence already embedded by Phase 2 | Dynamic registrations remain unresolved. |

# Delivered contract and behavior

`canary-otbm-storage-graph-v1` contains:

- input provenance and SHA-256 hashes;
- Phase 2 selected source files with hash revalidation and path confinement;
- normalized operations across player/account/global storage, player/account/global KV and narrow literal SQL evidence;
- per-namespace/key nodes;
- explicit same-key equality prerequisite-to-literal/delete/delta transitions;
- optional actor, handler, map and geometry correlation;
- conservative selected-scope findings and exact summary counts;
- unresolved dynamic keys/values;
- atomic output, overwrite protection and symlink rejection.

The implementation is split into evidence types, call inventory, branch/parser analysis, graph orchestration and a public facade. It does not create a second OTBM parser, pathfinder or source-selection system.

# Evidence policy

- A read without a selected-scope writer is `external-or-unproven`, not automatically a defect.
- A write without a selected-scope read is `write-only-in-selected-scope`, not proof that the key is unused globally.
- A numeric decrease is reported only when the same proven transition compares one literal value and writes a lower literal value.
- Writers conflict only when the same exact prerequisite state has incompatible literal outputs.
- Source proximity, lexical order and function order do not imply runtime order.
- Lua is never executed.

# Work log

## 2026-07-13T23:55:00+02:00

- Changed: created current-main task branch and draft PR #299; claimed Phase 5 paths.
- Learned: authoritative roadmap requires Phase 5 to consume Phase 2 and Phase 4 evidence; no overlapping live OTBM PR was found.
- Failed/blocked: local Git DNS resolution is unavailable; no local checkout/build/test result is claimed.

## 2026-07-14T00:15:00+02:00

- Changed: implemented the versioned graph library/facade, CLI, schema, docs, evidence ADR, 19 focused tests and dedicated workflow.
- Changed: split the implementation into bounded internal modules for evidence types, operation calls, branch parsing and graph analysis.
- Learned: exact transition evidence must remain narrower than Phase 2 storage inventory; only one enclosing exact same-key equality can authorize an edge.
- Validated: isolated 19-test suite passed; Python compilation passed; schema syntax and a representative `jsonschema` validation passed.
- Not claimed: current-main checkout, repository full suite or live gameplay, because local Git DNS remains unavailable.
- Next: inspect GitHub CI, repair failures, update shared documentation, run the final-head gate, merge and archive.

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence |
|---|---|---|---|
| isolated files | `python -m unittest -v test_otbm_storage_graph.py` | passed | 19 tests; 0 failures |
| isolated files | `python -m py_compile otbm_storage_graph*.py test_otbm_storage_graph.py` | passed | no compiler output |
| isolated files | `python -m json.tool OTBM_STORAGE_GRAPH.schema.json` | passed | valid JSON syntax |
| isolated synthetic report | `jsonschema.validate(report, schema)` | passed | 1 file, 2 operations, 1 node, 1 transition |
| current PR head | OTBM Storage Graph workflow | pending | GitHub Actions |
| current PR head | repository required checks | pending | GitHub Actions |

# Risks and compatibility

- Runtime/gameplay: none; offline read-only tooling.
- Persistence/database: no writes or migrations.
- Source parsing: static pattern evidence can miss dynamic abstractions; misses remain unresolved.
- Compatibility: existing Phase 2–4 contracts remain unchanged.
- Rollback: squash-revert the feature PR; no persistent cleanup required.
- Cross-repository rollout: none.

# Remaining work

1. Inspect and repair current-head CI.
2. Update module catalogue, changelog and authoritative roadmap.
3. Run final ready-head checks, inspect review threads and merge.
4. Archive Phase 5 in a separate lifecycle PR.
5. Start Phase 6 only from then-current `main` after a fresh overlap search.

# Completion

- Final status: active
- PR: #299
- Final head:
- Merge commit:
- Cleanup PR:
- Archived at:
