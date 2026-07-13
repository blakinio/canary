---
task_id: CAN-20260713-otbm-storage-dependency-graph
program_id: ""
coordination_id: "OTS-OTBM-VALIDATION"
status: active
agent: "GPT-5.6 Thinking"
branch: feat/otbm-storage-dependency-graph
base_branch: main
created: 2026-07-13T23:55:00+02:00
updated: 2026-07-13T23:55:00+02:00
last_verified_commit: "7cc47983cc78e06587fee09d1dcc5cc597836ade"
risk: medium
related_issue: ""
related_pr: "pending"
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

- [ ] Consume `canary-quest-map-evidence-v1` rather than creating another broad quest/source scanner.
- [ ] Optionally consume `canary-quest-map-validation-v1`, `canary-otbm-spawn-npc-evidence-v1`, `canary-otbm-spawn-npc-validation-v1` and `canary-otbm-reachability-v1` as correlation evidence.
- [ ] Inventory player storage reads, writes, comparisons and exact same-key increments/decrements.
- [ ] Separate player storage, account storage, player KV, account KV, global storage and database namespaces.
- [ ] Represent literal/symbolic keys and literal values deterministically; keep dynamic keys/values as `unresolved`.
- [ ] Emit explicit transition edges only where one source construct proves both prerequisite and resulting value.
- [ ] Never infer execution order from line order or source proximity.
- [ ] Detect read-only/write-only keys, unproven prerequisite values, backward literal transitions and conflicting literal writers conservatively.
- [ ] Preserve exact file/line/context provenance and source SHA-256 evidence.
- [ ] Bound input documents, source files, findings, nodes and edge samples while retaining exact counts.
- [ ] Add atomic JSON output, overwrite protection and symlink rejection.
- [ ] Add JSON Schema, documentation, ADR, focused tests and a dedicated workflow/artifact.
- [ ] Update module catalogue, changelog and authoritative roadmap.
- [ ] Confirm no map, WIDX, appearances binary, client asset, generated full report, gameplay, active datapack, protocol, persistence schema or production configuration is changed.
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
| Quest Map Validator | selected source files, hashes, canonical storage keys, read/write evidence and quest map classifications | Phase 5 may inspect only those already selected files for operation syntax missing from v1 evidence; it must not broaden source selection silently. |
| Spawn/NPC validator | creature/NPC definition, placement and literal dynamic-creation evidence | Provides actor/placement context only; it does not prove a storage handler executes. |
| Reachability validator | bounded geometry classifications | Optional contextual evidence only; reachable geometry is not storage progression proof. |
| Script resolver | handler/event registration evidence already embedded by Phase 2 | Dynamic registrations remain unresolved. |

# Planned report contract

`canary-otbm-storage-graph-v1` will contain:

- input provenance and hashes;
- selected source files;
- normalized storage operations;
- per-namespace/key nodes;
- explicit prerequisite-to-result transitions;
- actor/event/map correlation where directly evidenced;
- conservative findings and exact summary counts;
- unresolved dynamic expressions.

# Evidence policy

- A read without a selected-scope writer is `external-or-unproven`, not automatically a defect.
- A write without a selected-scope read is `write-only-in-scope`, not proof that the key is unused globally.
- A numeric decrease is reported only when the same proven transition reads/comparisons one literal value and writes a lower literal value.
- Writers conflict only when the same exact prerequisite state has incompatible literal outputs; unrelated branches or source files are not automatically conflicting.
- Source proximity, lexical order and function order do not imply runtime order.
- Lua is never executed.

# Work log

## 2026-07-13T23:55:00+02:00

- Changed: created current-main task branch and claimed Phase 5 paths.
- Learned: authoritative roadmap requires Phase 5 to consume Phase 2 and Phase 4 evidence; no overlapping live OTBM PR was found.
- Failed/blocked: local Git DNS resolution is unavailable; no local checkout/build/test result is claimed.
- Next: publish the draft PR, inspect exact evidence schemas and implement the smallest complete graph contract.

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence |
|---|---|---|---|
| | focused Python tests | not-run | implementation pending |
| | Python compilation | not-run | implementation pending |
| | schema validation | not-run | implementation pending |
| | dedicated workflow | not-run | implementation pending |
| | repository required checks | not-run | implementation pending |

# Risks and compatibility

- Runtime/gameplay: none; offline read-only tooling.
- Persistence/database: no writes or migrations.
- Source parsing: static pattern evidence can miss dynamic abstractions; misses remain unresolved.
- Compatibility: existing Phase 2–4 contracts remain unchanged.
- Rollback: squash-revert the feature PR; no persistent cleanup required.
- Cross-repository rollout: none.

# Remaining work

1. Open the early draft PR.
2. Implement report library and CLI.
3. Add focused tests/schema/docs/workflow.
4. Run and inspect current-head CI.
5. Merge and archive Phase 5 before starting Phase 6.

# Completion

- Final status: active
- PR: pending
- Final head:
- Merge commit:
- Cleanup PR:
- Archived at:
