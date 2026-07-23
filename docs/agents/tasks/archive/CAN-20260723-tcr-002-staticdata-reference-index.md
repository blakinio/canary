---
task_id: CAN-20260723-tcr-002-staticdata-reference-index
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: completed
agent: "GPT-5.6 Thinking"
branch: feat/tcr-002-staticdata-reference-index-20260723
base_branch: main
created: 2026-07-23T19:05:00+02:00
updated: 2026-07-23T23:27:11+02:00
last_verified_commit: "24d106b5eea40371833ce20de96184b55cd9b661"
risk: medium
related_issue: ""
related_pr: "827"
depends_on:
  - TCR-001 merged stable canary-tibia-client-reference-manifest-v1
blocks: []
owned_paths:
  exclusive: []
  shared: []
  read_only: []
modules_touched:
  - OTBM analysis tooling
  - official-client reference evidence
reuses:
  - canary-tibia-client-reference-manifest-v1 exact provenance contract
  - existing Tibia Client Reference validation workflow
public_interfaces:
  - canary-tibia-staticdata-index-v1
cross_repo_tasks: []
---

# Goal

Deliver and merge TCR-002 StaticData Reference Index as deterministic, fail-closed, read-only `canary-tibia-staticdata-index-v1` evidence bound to exact stable TCR-001 manifest provenance.

# Completion

- Final status: completed
- Delivery PR: #827
- Delivery merge commit: `24d106b5eea40371833ce20de96184b55cd9b661`
- Delivery final head: `218e1a78f0294ec9fc64b286e5677532ca581e1c`
- Lifecycle closure branch: `docs/tcr-002-lifecycle-closure-20260723`
- Archived at: `docs/agents/tasks/archive/CAN-20260723-tcr-002-staticdata-reference-index.md`

# Delivered

- `canary-tibia-staticdata-index-v1` library and CLI;
- exact manifest selected-input ID, size and SHA-256 binding;
- bounded legacy/newer StaticData protobuf parsing with fail-closed schema ambiguity;
- bounded raw, XZ, LZMA-alone and reviewed Tibia LZMA-header handling;
- deterministic category-preserving output with explicit duplicate and missing-field findings;
- quest ID/name inventory only and no gameplay conclusions;
- create-new/no-clobber output safety and atomic explicit overwrite;
- JSON schema, documentation and 19 focused tests;
- no client input data committed and no OTBM/runtime/protocol/client mutation.

# Final delivery validation evidence

Exact final delivery PR head: `218e1a78f0294ec9fc64b286e5677532ca581e1c`.

- Tibia Client Reference: PASS, run `30044951259`.
- Agent Task Ownership: PASS, run `30044951383`.
- AI Agent Tools: PASS, run `30044951401`.
- Repository CI exact-final-gate: PASS, run `30044951822`.
- Protected post-ready full repository CI: PASS, run `30045095498`.
- Squash merge: `24d106b5eea40371833ce20de96184b55cd9b661`.

# Stable producer contract state

`canary-tibia-staticdata-index-v1` is `stable/merged` as exact StaticData registry/reference evidence bound to the stable client-reference manifest. It does not prove Canary gameplay, runtime, map geometry or OTBM parity.

The StaticMapData, proficiency, parity/correlation, drift, evidence-gateway and adoption-routing outputs remain planned until their own bounded packages merge.

# Next package

After this lifecycle closure merges, TCR-003 — StaticMapData House Index is the next programme candidate only after a fresh ownership/PR/reuse preflight. It must start as a separate bounded task/branch/PR and is not implemented by this closure.
