---
task_id: CAN-20260714-targuna-donor-isolation
program_id: CAN-PROGRAM-CRYSTALSERVER-COMPARISON
coordination_id: REAL-TIBIA-TARGUNA-DONOR
status: completed
agent: "GPT-5.5 Thinking"
branch: audit/targuna-donor-isolation
base_branch: main
created: 2026-07-14T10:15:00+02:00
updated: 2026-07-16T20:45:22Z
last_verified_commit: "02d1b08162a3ad17d6283af16ad481f29c4ec213"
risk: low
related_issue: ""
related_pr: "316"
depends_on:
  - CAN-20260714-crystal-global-map-comparison
blocks: []
owned_paths:
  exclusive:
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
completed: 2026-07-16T20:45:22Z
---

# Goal

Isolate the pinned CrystalServer Targuna donor into deterministic spatial clusters and publish bounded semantic map, quest, NPC, monster/spawn, house and dependency evidence without writing or importing OTBM content.

# Acceptance criteria

- [x] Pin the exact Canary and CrystalServer revisions and both logical OTBM hashes.
- [x] Discover Targuna source files, literal positions, NPC names and monster definitions from the pinned Crystal datapack.
- [x] Correlate selected Targuna NPC and monster names with explicit Crystal companion evidence.
- [x] Derive deterministic spatial clusters from source, house and actor anchors while keeping disconnected regions separate.
- [x] Run the merged Semantic OTBM Diff for each selected bounded cluster.
- [x] Inventory exact map mechanic counts in each cluster and preserve unresolved/static-evidence boundaries.
- [x] Record registrations, storages, literal item IDs, actor evidence and engine/API dependencies without executing Lua.
- [x] Identify Targuna, Aragonia, Crimson Court, Hidden Lizard Temple and external/main-continent dependency labels where evidence supports them.
- [x] Produce concise Markdown and machine-readable JSON reports.
- [x] Remove every temporary workflow and audit script before merge.
- [x] Commit no OTBM, WIDX, archive, asset, render or multi-megabyte raw evidence report.
- [ ] Verify final exact-head CI, review state and autonomous merge gate.

# Proven result

The refreshed bounded audit succeeded after PR #319 repaired the shared multi-area Semantic OTBM Diff ordering defect originally reproduced by this task.

Pinned evidence:

- Canary source commit: `d88e7f354eb5b33068cdded7696e9cdb89b05268`
- CrystalServer source commit: `fc0d53b9f9965463b6082c07e6d3d482294541a7`
- Baseline OTBM SHA-256: `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`
- Crystal logical OTBM SHA-256: `4b2099f38df05d4be68d1ba1265754e9fd6da09742025d92644fa4b1a12eb120`
- Successful audit run: `29526630176` (run #5)
- Successful audit head: `b1a8b70748d6ad6bfa82c8798646ed93c3813c85`
- Evidence artifact digest: `sha256:f75965735e5690740e546e1d6a7523ae78157f4836086d8715d3a6f0d675a5da`

The committed reports retain concise provenance, source hashes, actor and static-placement summaries, houses, storage/item/API dependencies and four deterministic cluster summaries. Raw placement arrays and bounded Semantic Diff samples remain only in the pinned workflow artifact.

# Safety and interpretation boundary

- No map or datapack content is modified.
- Cluster bounds are deterministic review scopes, not copy authorization.
- Literal source extraction does not execute Lua; dynamic positions remain unresolved.
- Semantic findings are static evidence and do not prove runtime behavior or Real Tibia gameplay parity.
- Any future map materialization must independently review exact cluster findings and reuse the repository's bounded OTBM planning/materialization contracts.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T22:25:30+02:00
head: d2906b2badeac69fa1971002cc0cebb4852320dc
branch: audit/targuna-donor-isolation
pr: 316
status: ready
context_routes:
  - agent-governance
  - otbm
  - real-tibia-parity
owned_paths:
  - docs/ai-agent/REAL_TIBIA_TARGUNA_DONOR_AUDIT.md
  - docs/ai-agent/REAL_TIBIA_TARGUNA_DONOR_AUDIT.json
  - docs/agents/tasks/active/CAN-20260714-targuna-donor-isolation.md
proven:
  - source evidence is pinned to Canary d88e7f354eb5b33068cdded7696e9cdb89b05268 and CrystalServer fc0d53b9f9965463b6082c07e6d3d482294541a7
  - baseline OTBM SHA-256 is a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
  - Crystal logical OTBM SHA-256 is 4b2099f38df05d4be68d1ba1265754e9fd6da09742025d92644fa4b1a12eb120
  - PR 319 merged the exact multi-area Semantic OTBM Diff ordering repair reproduced by the original audit failure
  - refreshed Targuna donor isolation audit run 29526630176 completed successfully on b1a8b70748d6ad6bfa82c8798646ed93c3813c85
  - successful audit artifact digest is sha256:f75965735e5690740e546e1d6a7523ae78157f4836086d8715d3a6f0d675a5da
  - concise Markdown and JSON reports are published and temporary workflow/script paths are removed
  - no OTBM WIDX archive asset render or multi-megabyte raw report is committed
derived:
  - four deterministic bounded review clusters are sufficient to preserve the discovered Targuna donor evidence without authorizing whole-map or whole-cluster import
  - future materialization must independently review cluster findings and runtime dependencies
unknown:
  - live gameplay correctness and Real Tibia parity for any proposed imported content
conflicts: []
first_failure:
  marker: semantic-diff-world-index-order
  evidence: original run 29317641389 failed in bounded multi-area Semantic OTBM Diff; merged PR 319 repaired that shared iterator defect and refreshed run 29526630176 passed
rejected_hypotheses:
  - building a second Semantic OTBM Diff implementation inside the Targuna audit
  - treating the original ordering exception as donor-map corruption
  - using coarse cluster bounds as authorization to copy every tile inside them
changed_paths:
  - docs/ai-agent/REAL_TIBIA_TARGUNA_DONOR_AUDIT.md
  - docs/ai-agent/REAL_TIBIA_TARGUNA_DONOR_AUDIT.json
  - docs/agents/tasks/active/CAN-20260714-targuna-donor-isolation.md
validation:
  - command: Targuna donor isolation audit run 29526630176
    result: PASS
    evidence: bounded audit completed successfully on b1a8b70748d6ad6bfa82c8798646ed93c3813c85 and published artifact digest f75965735e5690740e546e1d6a7523ae78157f4836086d8715d3a6f0d675a5da
  - command: CI run 29526629733
    result: PASS
    evidence: repository CI completed successfully on the refreshed audit head
  - command: Agent Task Ownership run 29526629120
    result: PASS
    evidence: active-task checkpoint and ownership validation completed successfully
blockers: []
next_action: Apply ci:final-gate, synchronize the branch with current main in one final commit, run exact-final-head checks, then mark PR 316 ready and squash-merge only if the gate is green.
```

# Completion

- Final status: ready
- PR: #316
- Final reviewed head: pending exact-final-head gate
- Merge commit: pending
- Archived at: pending lifecycle automation

## Automated lifecycle completion

- Feature PR: #316.
- Feature head: `daba026813729ae527a047808e6f28b32a0cd5b8`.
- Merge commit: `02d1b08162a3ad17d6283af16ad481f29c4ec213`.
- Merged at: `2026-07-16T20:45:22Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
