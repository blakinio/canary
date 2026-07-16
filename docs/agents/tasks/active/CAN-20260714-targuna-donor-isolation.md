---
task_id: CAN-20260714-targuna-donor-isolation
program_id: CAN-PROGRAM-CRYSTALSERVER-COMPARISON
coordination_id: REAL-TIBIA-TARGUNA-DONOR
status: implementing
agent: "GPT-5.5 Thinking"
branch: audit/targuna-donor-isolation
base_branch: main
created: 2026-07-14T10:15:00+02:00
updated: 2026-07-16T20:57:00+02:00
last_verified_commit: "d88e7f354eb5b33068cdded7696e9cdb89b05268"
risk: low
related_issue: ""
related_pr: "316"
depends_on:
  - CAN-20260714-crystal-global-map-comparison
blocks: []
owned_paths:
  exclusive:
    - .github/workflows/targuna-donor-isolation-audit.yml
    - .github/scripts/targuna_donor_isolation_audit.py
    - docs/ai-agent/REAL_TIBIA_TARGUNA_DONOR_AUDIT.md
    - docs/ai-agent/REAL_TIBIA_TARGUNA_DONOR_AUDIT.json
    - docs/agents/tasks/active/CAN-20260714-targuna-donor-isolation.md
  shared: []
  read_only:
    - AGENTS.md
    - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
    - docs/ai-agent/REAL_TIBIA_CRYSTAL_MAP_AUDIT.md
    - docs/ai-agent/REAL_TIBIA_CRYSTAL_MAP_AUDIT.json
    - docs/ai-agent/OTBM_SEMANTIC_DIFF.md
    - docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md
    - docs/ai-agent/OTBM_SPAWN_NPC_VALIDATION.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md
    - tools/ai-agent/otbm_item_audit_scan.cpp
    - tools/ai-agent/otbm_world_index_tool.py
    - tools/ai-agent/otbm_semantic_diff_tool.py
    - tools/ai-agent/otbm_spawn_npc_tool.py
modules_touched:
  - bounded Targuna donor evidence audit
reuses:
  - Unified OTBM World Index
  - Semantic OTBM Diff
  - OTBM spawn and NPC evidence scanner
  - Crystal global-map comparison report
public_interfaces: []
cross_repo_tasks:
  - repository: zimbadev/crystalserver
    mode: read-only
    ref: fc0d53b9f9965463b6082c07e6d3d482294541a7
---

# Goal

Isolate the CrystalServer Targuna donor into deterministic spatial clusters and produce bounded semantic map, quest, NPC, monster/spawn, house and source-dependency evidence without writing or importing any OTBM content.

# Acceptance criteria

- [ ] Pin the exact Canary and CrystalServer revisions and both logical OTBM hashes.
- [ ] Discover Targuna source files, literal positions, NPC names and monster definitions from the pinned Crystal datapack.
- [ ] Correlate selected Targuna NPC and monster names with the explicit Crystal companion XML files.
- [ ] Derive deterministic spatial clusters from source, house and actor anchors; keep disconnected regions separate.
- [ ] Run the merged Semantic OTBM Diff for each selected bounded cluster.
- [ ] Inventory exact map mechanics in each cluster and preserve unresolved evidence.
- [ ] Record script registrations, storages, item IDs, actor definitions and engine/API dependencies without executing Lua.
- [ ] Identify which clusters are Targuna island, Aragonia, Crimson Court, Hidden Lizard Temple or external/main-continent dependencies where evidence supports the label.
- [ ] Produce concise Markdown and machine-readable JSON reports.
- [ ] Remove every temporary workflow and audit script before merge.
- [ ] Commit no OTBM, WIDX, archive, asset, render or large raw report.
- [ ] Verify final CI, review state and autonomous merge gate.

# Confirmed context

- Writable repository: `blakinio/canary` only.
- Canary task-start main: `d88e7f354eb5b33068cdded7696e9cdb89b05268`.
- CrystalServer is read-only and pinned to `fc0d53b9f9965463b6082c07e6d3d482294541a7`.
- Baseline OTBM SHA-256: `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`.
- Decompressed Crystal OTBM SHA-256: `4b2099f38df05d4be68d1ba1265754e9fd6da09742025d92644fa4b1a12eb120`.
- PR #311 merged the reusable Semantic OTBM Diff. This task must reuse it rather than implement another map comparator.
- PR #313 proved that the full Crystal map is not safe for wholesale replacement; this task is bounded evidence only.
- PR #319 merged the exact multi-area World Index ordering fix for the failure originally reproduced by PR #316.
- No map writing, item substitution, datapack mixing or direct import is authorized.

# Existing work to reuse

| Existing work | Reuse | Boundary |
|---|---|---|
| `REAL_TIBIA_CRYSTAL_MAP_AUDIT.*` | Exact global provenance and rejection of whole-map replacement | Do not repeat the global comparison. |
| Unified OTBM World Index | Exact bounded tile/item/mechanic records | Generated indexes stay outside Git. |
| Semantic OTBM Diff | Exact bounded before/after structural and mechanic evidence | No duplicate diff implementation. |
| Spawn/NPC evidence scanner | Explicit selected datapack and companion XML evidence | No dynamic Lua execution or mixed datapacks. |
| Script-resolution methodology | Preserve exact registrations and unresolved dynamic behavior | This task does not claim live handler execution. |

# Ownership and overlap check

- Open PRs inspected on 2026-07-16.
- Final intended paths are two new reports and this task record.
- Temporary workflow/script paths are exclusive and must be deleted before merge.
- PR #426 owns separate bounded materializer paths and does not overlap this read-only Targuna evidence audit.
- No shared paths and no edits to `ACTIVE_WORK.md`, roadmap, module catalogue or comparison program record.

# Plan

1. Add a temporary PR-only workflow and audit script.
2. Acquire and verify both exact maps outside Git, build canonical indexes and scan the pinned Crystal datapack.
3. Derive actor/source/house anchor clusters and run bounded semantic diffs.
4. Publish small reports, remove temporary workflow/script and update this task.
5. Verify final-head checks, merge and archive the task lifecycle.

# Current state

The original audit run reproduced a multi-area Semantic OTBM Diff ordering failure. PR #319 later fixed that exact failure and added regression coverage. The audit branch has now merged current `main` so the existing temporary workflow can rerun with the repaired shared Semantic OTBM Diff while retaining the original pinned Canary map and CrystalServer evidence inputs.

# Validation and CI

| Commit/run | Check | Result | Notes |
|---|---|---|---|
| `dfa7ffe8` / `29317641389` | bounded Targuna audit | FAIL | Failed at bounded Semantic OTBM Diff with `World Index tile iteration is not strictly ordered`; PR #319 subsequently fixed this exact failure class. |
| `8307dafb` / `29525880083` | CI | PASS | Repository CI passed after merging current main. |
| `8307dafb` / `29525879790` | Agent Task Ownership | FAIL | Legacy task lacked the now-required `## Context checkpoint`; this checkpoint update repairs governance only. |
| `8307dafb` / `29525879706` | bounded Targuna audit | running | Rerun uses current main tooling including merged PR #319 while preserving exact pinned source evidence. |

# Safety and rollback

- Runtime impact: none; evidence reports only.
- Data impact: none; no map/datapack modification.
- External inputs: pinned, read-only and kept outside Git.
- Rollback: revert report commits.

# Remaining work

Complete the refreshed bounded audit, inspect its generated evidence, publish only concise Markdown/JSON reports, remove the temporary workflow/script, then run the final merge gate.

# Handoff

Read the exact global audit first. Do not expand this task into whole-map replacement, Newhaven implementation or map writing.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T20:57:00+02:00
head: 8307dafb4b3a92564ef5eba56c4f91d7776bf0d4
branch: audit/targuna-donor-isolation
pr: 316
status: validating
context_routes:
  - agent-governance
  - otbm
  - real-tibia-parity
owned_paths:
  - .github/workflows/targuna-donor-isolation-audit.yml
  - .github/scripts/targuna_donor_isolation_audit.py
  - docs/ai-agent/REAL_TIBIA_TARGUNA_DONOR_AUDIT.md
  - docs/ai-agent/REAL_TIBIA_TARGUNA_DONOR_AUDIT.json
  - docs/agents/tasks/active/CAN-20260714-targuna-donor-isolation.md
proven:
  - source evidence remains pinned to Canary task-start d88e7f354eb5b33068cdded7696e9cdb89b05268 and CrystalServer fc0d53b9f9965463b6082c07e6d3d482294541a7
  - original audit run 29317641389 failed only after maps indexes and spawn NPC evidence were built successfully
  - original failure was World Index tile iteration is not strictly ordered during bounded multi-area Semantic OTBM Diff
  - merged PR 319 explicitly fixes the PR 316 multi-area Semantic OTBM Diff ordering failure
  - branch merge commit 8307dafb4b3a92564ef5eba56c4f91d7776bf0d4 includes current main while retaining only the three audit-owned changed paths
  - repository CI run 29525880083 passed on 8307dafb4b3a92564ef5eba56c4f91d7776bf0d4
derived:
  - rerunning the unchanged bounded audit on current main is the smallest repair because the failure belonged to shared Semantic OTBM Diff and is already fixed by PR 319
unknown:
  - refreshed bounded Targuna audit final result and generated cluster evidence
conflicts: []
rejected_hypotheses:
  - building a second Semantic OTBM Diff implementation inside the Targuna audit
  - treating the multi-area ordering exception as donor map corruption
changed_paths:
  - .github/workflows/targuna-donor-isolation-audit.yml
  - .github/scripts/targuna_donor_isolation_audit.py
  - docs/agents/tasks/active/CAN-20260714-targuna-donor-isolation.md
blockers: []
first_failure:
  marker: semantic-diff-world-index-order
  evidence: run 29317641389 failed at cluster 01 bounds 31488,31488,4 to 32255,32255,10 with World Index tile iteration is not strictly ordered; PR 319 merged the exact k-way area iterator fix
validation:
  - command: Targuna donor isolation audit run 29317641389
    result: FAIL
    evidence: source maps indexes and actor spawn evidence succeeded before bounded multi-area Semantic OTBM Diff ordering failed
  - command: CI run 29525880083
    result: PASS
    evidence: repository CI passed after merging current main into the audit branch
  - command: Agent Task Ownership run 29525879790
    result: FAIL
    evidence: changed-task validation reported only missing Context checkpoint on the legacy task record
  - command: Targuna donor isolation audit run 29525879706
    result: NOT_RUN
    evidence: refreshed audit was still in progress when this checkpoint was written
next_action: Let refreshed Targuna donor isolation audit run 29525879706 finish, then inspect its bounded artifact and publish only the concise final reports if the evidence is complete.
```

# Completion

- Final status: validating
- PR: #316
- Final reviewed head:
- Merge commit:
- Archived at:
