---
task_id: CAN-20260724-tcr-003-staticmapdata-house-index
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: completed
agent: "GPT-5.6 Thinking"
branch: feat/tcr-003-staticmapdata-house-index
base_branch: main
created: 2026-07-24T07:18:23+02:00
updated: 2026-07-24T08:17:00+02:00
last_verified_commit: "e8f825cb15fa4fd3b253018d98b4dc78e4a966a9"
risk: medium
related_issue: ""
related_pr: 851
depends_on:
  - TCR-001 merged stable canary-tibia-client-reference-manifest-v1
  - TCR-002 merged stable canary-tibia-staticdata-index-v1
blocks: []
owned_paths:
  exclusive: []
  shared: []
  read_only: []
modules_touched:
  - OTBM Tibia client reference architecture
  - official-client reference evidence
reuses:
  - canary-tibia-client-reference-manifest-v1 exact provenance contract
  - TCR-002 bounded stable-file, compression, protobuf-wire and deterministic-output patterns
public_interfaces:
  - canary-tibia-staticmapdata-index-v1
cross_repo_tasks: []
---

# Goal

Deliver and merge TCR-003 StaticMapData House Index as deterministic, fail-closed, read-only `canary-tibia-staticmapdata-index-v1` evidence bound to exact stable TCR-001 manifest provenance.

# Completion

- Final status: completed.
- Delivery PR: #851.
- Delivery merge commit: `e8f825cb15fa4fd3b253018d98b4dc78e4a966a9`.
- Delivery final head: `e8d7fb2a5938b8f386caa9e752a6bebf2f7a7268`.
- `ci:final-gate` was applied before the protected ready-state full repository gate.
- Lifecycle/discovery closure PR: #855.
- Lifecycle/discovery closure branch: `docs/tcr-003-lifecycle-closure-20260724`.
- Programme queue and stable-contract state are updated by PR #855.
- Archived at: `docs/agents/tasks/archive/CAN-20260724-tcr-003-staticmapdata-house-index.md`.

# Delivered

- `canary-tibia-staticmapdata-index-v1` library and CLI;
- exact manifest selected-input ID, size and SHA-256 binding;
- independently implemented bounded protobuf-wire parsing for house IDs, layout origin, dimensions, floors, ordered rows and tile object/wall/door evidence;
- bounded raw protobuf, XZ, LZMA-alone and reviewed Tibia LZMA-header handling;
- deterministic source ordinals and explicit duplicate-house, missing-required-field, duplicate-singular-field and dimension findings;
- encoded-cell-span validation using preserved source rows and flags without assigning stronger unresolved flag semantics;
- explicit unresolved `staticmapdata.object_id` namespace with no OTBM/server/appearance ID equivalence claim;
- create-new/no-clobber output safety and atomic explicit overwrite;
- JSON schema, documentation and 15 focused fixture tests plus one opt-in real-file test;
- no proprietary client input or generated real-file report committed;
- no OTBM parsing/writing, map/runtime/protocol/client mutation or gameplay conclusion.

# Final delivery validation evidence

Exact final delivery PR head: `e8d7fb2a5938b8f386caa9e752a6bebf2f7a7268`.

- Fixture-only focused validation: PASS, 15 tests passed and one opt-in real-file test skipped.
- External opt-in validation: PASS, all 16 tests passed against source SHA-256 `0967af2eacdd8f2a608e738b9042362676167d6c6455e60d08db7ae16cf7ea53` outside Git.
- Real-file evidence summary: 995 houses, 117716 rows, 188014 tile records and zero duplicate-house, missing-field, duplicate-singular-field or dimension findings.
- Tibia Client Reference: PASS, run `30070296904`.
- Agent Task Ownership: PASS, run `30070296910`.
- AI Agent Tools: PASS, run `30070296921`.
- Pre-ready repository CI: PASS, run `30070297022`.
- Protected post-ready full repository CI: PASS, run `30070389385`.
- Autofix: PASS, run `30070389245`.
- Squash merge: `e8f825cb15fa4fd3b253018d98b4dc78e4a966a9`.

# Stable producer contract state

`canary-tibia-staticmapdata-index-v1` is `stable/merged` as exact manifest-bound StaticMapData house-layout reference evidence. It does not prove OTBM item-ID equivalence, full item stacks, AID/UID/mechanics, map authority, runtime house access, ownership/rent state or gameplay parity.

# Preserved unknowns and conflicts

- UNKNOWN: exact client build identity unless separately proven by the stable manifest.
- UNKNOWN: broader `row.flags` semantics beyond the proven encoded-cell-span consistency relationship.
- UNKNOWN: mapping from `staticmapdata.object_id` to OTBM/server/appearance identifiers.
- CONFLICTS: none.

# Next package

After this lifecycle closure merges, TCR-004 — Proficiency Reference Index is the next programme candidate only after a fresh ownership/PR/reuse/source-format preflight. It must start as a separate bounded task, branch and PR; this closure does not implement TCR-004 or TCR-005.
