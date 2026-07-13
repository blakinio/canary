---
task_id: CAN-20260713-quest-map-validator
coordination_id: "OTS-OTBM-VALIDATION"
status: merged
agent: "GPT-5.6 Thinking"
branch: feat/quest-map-validator
base_branch: main
created: 2026-07-13T00:18:00+02:00
updated: 2026-07-13T09:35:00+02:00
last_verified_commit: "857985c8c0849fa2b86d8c1d688fbe663d0018fa"
risk: medium
related_issue: ""
related_pr: "#225"
depends_on:
  - "merged Unified OTBM World Index #219"
  - "merged OTBM script-resolution audit #104"
blocks:
  - "teleport/pathfinding validation phase"
  - "storage dependency graph phase"
  - "quest repair evidence bundles"
owned_paths:
  - tools/ai-agent/quest_map_validation.py
  - tools/ai-agent/quest_map_validation_tool.py
  - tools/ai-agent/test_quest_map_validation.py
  - docs/ai-agent/QUEST_MAP_VALIDATION.md
  - docs/ai-agent/QUEST_MAP_VALIDATION.schema.json
  - .github/workflows/quest-map-validation.yml
modules_touched:
  - Unified OTBM World Index
  - OTBM script-resolution audit
reuses:
  - tools/ai-agent/otbm_world_index.py
  - tools/ai-agent/otbm_script_resolution.py
public_interfaces:
  - "canary-quest-map-evidence-v1"
  - "canary-quest-map-validation-v1"
  - "Quest Map Validator CLI"
cross_repo_tasks: []
---

# Goal

Create a deterministic read-only Quest Map Validator that extracts static quest evidence from explicitly selected active Lua/XML sources and correlates AID/UID, item IDs, exact positions and teleport destinations with the merged OTBM World Index and optional script-resolution report.

# Completion summary

PR #225 was merged at `b23c8a353b09c066e72de178b8e86f0309740211` after all required checks passed.

Delivered behavior:

- explicit source-root and include/exclude selection;
- deterministic file hashes, evidence IDs, source lines and contexts;
- static AID, UID, item, position, teleport and storage read/write evidence;
- direct symbolic `Storage` alias expansion without Lua execution;
- bounded `.widx` correlation and optional script-resolution reuse;
- `confirmed`, `map-only`, `script-only`, `unresolved` and `conflicting` classifications;
- conservative handling of item IDs absent from static OTBM and generic missing positions;
- bounded regional map-only mechanic reporting;
- atomic JSON output with symlink rejection;
- JSON Schema, focused tests, documentation and dedicated CI artifacts.

No map, `.widx`, asset, generated report, datapack, runtime, database, protocol or OTClient behavior was committed or changed.

# Acceptance criteria

- [x] Source selection is explicit and deterministic.
- [x] Static evidence is extracted without executing Lua or guessing dynamic expressions.
- [x] World Index and script-resolution are reused rather than duplicated.
- [x] Placement samples and region volume are bounded while exact totals are retained.
- [x] Dynamic and insufficient evidence remains unresolved.
- [x] Source-only evidence and a local-correlation toolkit are published by CI.
- [x] Real-map correlation was completed outside Git.
- [x] Schema, documentation, catalogue and changelog are current.
- [x] Final file list and review threads were clear.
- [x] Required CI passed and the autonomous merge gate was satisfied.

# Key decisions

| Decision | Reason |
|---|---|
| Separate repository evidence from private-map correlation | CI can audit source code without uploading `.otbm` or `.widx`. |
| Require explicit quest globs | Automatically grouping a datapack would create false associations. |
| Reuse script-resolution | Prevents competing handler semantics. |
| Treat static map absence conservatively | Rewards, inventory items, dynamic creation and area coordinates are not proven broken by OTBM absence alone. |
| Keep storage progression for a later phase | This validator inventories reads/writes but does not infer stage reachability. |

# Validation evidence

Final head `857985c8c0849fa2b86d8c1d688fbe663d0018fa`:

- Quest Map Validator run `29232010971`: success;
- Agent Task Ownership run `29232010980`: success;
- AI Agent Tools run `29232010964`: success;
- final CI run `29232043337`: success, including Linux compile and nested `Required`.

Real-map evidence:

```text
map SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
source size: 184,776,037 bytes
index size: 842,280,592 bytes
index build: 40.21 s
peak RSS: 418,956 KiB
tiles: 17,972,761
placements: 23,359,571
used item IDs: 23,852
mechanics: 9,339
unknown attribute tails: 0
Zirella source evidence: 12
source unresolved: 0
confirmed: 6
map-only region mechanics: 10
script-only: 0
unresolved storage semantics: 6
conflicting: 0
```

The ten regional map-only entries are review candidates, not proven defects. The six unresolved entries are storage semantics intentionally deferred to the Storage Dependency Graph phase.

# Corrections made during implementation

- Removed a temporary `/mnt/data` dependency from the tests.
- Fixed the CLI import to reuse the canonical World Index position parser.
- Changed overconfident missing-item and generic-position classifications to unresolved.
- Added direct Storage alias support, atomic output and symlink rejection.
- Isolated an ambiguous test fixture where a generic position was lexically adjacent to a teleport call.

# Handoff

Reuse `quest_map_validation.py`, `otbm_world_index.py` and `otbm_script_resolution.py` for future quest audits. Do not create another OTBM parser, commit `.otbm`/`.widx`, promote unresolved evidence to handled, or treat regional map-only findings as automatic repair authorization.

Recommended next independent phases:

1. teleport/stairs/walkability validator;
2. storage dependency graph;
3. spawn/NPC index;
4. semantic OTBM diff.

# Completion

- Final status: merged
- PR: #225
- Merge commit: `b23c8a353b09c066e72de178b8e86f0309740211`
- Catalogue updated: yes
- Changelog updated: yes
- Archived at: `docs/agents/tasks/archive/CAN-20260713-quest-map-validator.md`
