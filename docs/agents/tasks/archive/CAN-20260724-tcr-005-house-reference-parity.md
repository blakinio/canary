---
task_id: CAN-20260724-tcr-005-house-reference-parity
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: completed
agent: "GPT-5.6 Thinking"
branch: feat/tcr-005-house-reference-parity
base_branch: main
created: 2026-07-24T10:35:00+02:00
updated: 2026-07-24T16:05:00+02:00
last_verified_commit: "5641a7ac2420f5a3d512325423088890e92ac3cb"
risk: medium
related_issue: ""
related_pr: 868
depends_on:
  - TCR-001 merged stable canary-tibia-client-reference-manifest-v1
  - TCR-002/TCR-002A merged stable canary-tibia-staticdata-index-v1 schemaVersion 2
  - TCR-003 merged stable canary-tibia-staticmapdata-index-v1
  - Unified OTBM World Index merged stable canary-otbm-world-index-v1
blocks: []
owned_paths:
  exclusive: []
  shared: []
  read_only: []
modules_touched:
  - OTBM Tibia client reference architecture
  - OTBM house evidence correlation
reuses:
  - canary-tibia-client-reference-manifest-v1
  - canary-tibia-staticdata-index-v1 schemaVersion 2 houseFieldOrder contract
  - canary-tibia-staticmapdata-index-v1
  - canary-otbm-world-index-v1 and WorldIndex reader
public_interfaces:
  - canary-otbm-house-id-resolver-v1
  - canary-otbm-house-reference-parity-v1
cross_repo_tasks: []
---

# Goal

Deliver and merge the bounded, deterministic, read-only TCR-005 house reference parity consumer without adding a second OTBM parser, pathfinder, geometry engine or mutation path.

# Completion

- Final status: completed.
- Delivery PR: #868.
- Delivery merge commit: `5641a7ac2420f5a3d512325423088890e92ac3cb`.
- Delivery final head: `5bae2cfc1e93e7c4c312736a60eb9f3b207c3def`.
- TCR-002A prerequisite PR #870 merged as `c0911f7755aac65c176be69070fb7ec07045baff`.
- `ci:final-gate` was applied before the final checkpoint.
- Protected ready-state CI passed without macOS.
- Lifecycle/discovery closure PR: #874.
- Lifecycle/discovery closure branch: `docs/tcr-005-lifecycle-closure-20260724`.
- Programme queue and stable-contract state are updated by PR #874.
- Archived at: `docs/agents/tasks/archive/CAN-20260724-tcr-005-house-reference-parity.md`.

# Delivered

- stable `canary-otbm-house-id-resolver-v1` with exact cross-input provenance binding;
- stable `canary-otbm-house-reference-parity-v1` read-only consumer;
- explicit reviewed registry-position resolver using canonical World Index house IDs only;
- 995 client house records, 993 one-to-one mappings, two unresolved client houses and zero resolver conflicts;
- separate StaticData registry position/declared-size, StaticMapData layout and OTBM observed house evidence;
- exact World Index house-door grouping, including 42 orphan house-door placements as review evidence;
- 993 mismatch review rows and two `unresolved-id-space` rows without automatic gameplay-defect classification;
- fail-closed stale provenance, duplicate mapping, unknown identifier and unsupported-method handling;
- TCR-002A schemaVersion 2 and reviewed `houseFieldOrder` enforcement;
- JSON schemas, CLI, documentation, module-catalog registration and 14 focused tests;
- no proprietary inputs or generated exact reports committed;
- no `staticmapdata.object_id` equivalence claim, OTBM mutation, pathfinding, geometry recomputation, runtime claim or gameplay conclusion.

# Final delivery validation evidence

Exact final delivery PR head: `5bae2cfc1e93e7c4c312736a60eb9f3b207c3def`.

- Fixture-focused validation: PASS, 14 tests passed and one exact-input opt-in test skipped.
- Exact-input validation: PASS, all 14 tests passed.
- Exact resolver summary: 995 client houses, 993 mappings, two unresolved and zero conflicts.
- Exact parity summary: 995 rows, 993 mismatch rows, two unresolved-ID-space rows and 42 orphan house-door placements.
- Agent Task Ownership: PASS, run `30090940066`.
- Tibia Client Reference: PASS, run `30090940106`.
- OTBM Map Tools: PASS, run `30090940057`.
- AI Agent Tools: PASS, run `30090940073`.
- Final-checkpoint repository CI/Required: PASS, run `30090940301`.
- Protected ready-state milestone CI: PASS, run `30091318089`.
- Autofix: PASS with no changes, run `30091317881`.
- Squash merge: `5641a7ac2420f5a3d512325423088890e92ac3cb`.

# Stable contract state

`canary-otbm-house-id-resolver-v1` and `canary-otbm-house-reference-parity-v1` are `stable/merged` as exact, provenance-pinned house identifier-resolution and cross-reference evidence contracts. They do not prove that StaticData declared size, StaticMapData dimensions and OTBM tile population are identical gameplay concepts; they do not resolve `staticmapdata.object_id`; and they do not prove runtime ownership, rent, access or gameplay behavior.

# Preserved unknowns and conflicts

- UNKNOWN: exact client build identity unless separately proven by the stable manifest.
- UNKNOWN: mapping from `staticmapdata.object_id` to OTBM/server/appearance identifiers.
- UNKNOWN: whether registry declared size and OTBM house-tile population are intended to be identical gameplay concepts for every house.
- UNKNOWN: whether TCR-006 content registries have explicit stable identifier resolvers for every target subsystem.
- CONFLICTS: none.

# Next package

After this lifecycle closure merges, TCR-006 — Global Content Registry Correlation is the next programme candidate only after a fresh ownership/PR/reuse/identifier-resolution preflight. It must start as a separate bounded task, branch and PR; this closure does not implement TCR-006 or TCR-007.
