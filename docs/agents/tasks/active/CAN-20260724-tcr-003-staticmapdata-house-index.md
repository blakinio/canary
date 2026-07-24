---
task_id: CAN-20260724-tcr-003-staticmapdata-house-index
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: active
agent: "GPT-5.6 Thinking"
branch: feat/tcr-003-staticmapdata-house-index
base_branch: main
created: 2026-07-24T07:18:23+02:00
updated: 2026-07-24T07:18:23+02:00
last_verified_commit: "879fbfaff75b4255b4164b5132a0987e9aec8358"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - TCR-001 merged stable canary-tibia-client-reference-manifest-v1
  - TCR-002 merged stable canary-tibia-staticdata-index-v1
blocks:
  - TCR-005
  - TCR-009
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-tcr-003-staticmapdata-house-index.md
    - tools/ai-agent/tibia_staticmapdata_reference_index.py
    - tools/ai-agent/tibia_staticmapdata_reference_index_tool.py
    - tools/ai-agent/test_tibia_staticmapdata_reference_index.py
    - docs/ai-agent/TIBIA_STATICMAPDATA_REFERENCE_INDEX.md
    - docs/ai-agent/TIBIA_STATICMAPDATA_REFERENCE_INDEX.schema.json
  shared:
    - .github/workflows/tibia-client-reference.yml
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
    - docs/ai-agent/OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/tibia_client_reference_manifest.py
    - tools/ai-agent/tibia_staticdata_reference_index.py
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

Implement the bounded, read-only `canary-tibia-staticmapdata-index-v1` producer for one explicit manifest-bound Tibia `staticmapdata` file. Preserve house/layout evidence deterministically, validate encoded cell spans against declared dimensions, keep `staticmapdata.object_id` unresolved and separate from OTBM/server IDs, and never parse or write OTBM.

# Acceptance criteria

- Exact manifest and source provenance, byte size and SHA-256 are retained.
- House IDs, layout origins, dimensions, row order, row flags and tile/object/wall/door records are preserved deterministically.
- Duplicate house IDs, missing required fields, duplicate singular fields and invalid dimension/encoded-cell-span relationships are explicit findings or fail-closed errors.
- `staticmapdata.object_id` is emitted only in its own unresolved namespace and is never equated with an OTBM/server item ID.
- Raw protobuf and reviewed bounded compression variants reuse the TCR-002 safety model.
- No proprietary source bytes, generated real-file report, OTBM parser, OTBM writer or gameplay conclusion is added.
- Focused unit tests, Python bytecode compilation, JSON schema validation and the dedicated client-reference workflow pass on the final head.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T07:18:23+02:00
head: UNKNOWN
branch: feat/tcr-003-staticmapdata-house-index
pr: none
status: implementing
context_routes:
  - agent-governance
  - otbm
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-tcr-003-staticmapdata-house-index.md
  - tools/ai-agent/tibia_staticmapdata_reference_index.py
  - tools/ai-agent/tibia_staticmapdata_reference_index_tool.py
  - tools/ai-agent/test_tibia_staticmapdata_reference_index.py
  - docs/ai-agent/TIBIA_STATICMAPDATA_REFERENCE_INDEX.md
  - docs/ai-agent/TIBIA_STATICMAPDATA_REFERENCE_INDEX.schema.json
  - .github/workflows/tibia-client-reference.yml
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
  - docs/ai-agent/OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md
  - docs/agents/CHANGELOG.md
proven:
  - Current implementation base is main 879fbfaff75b4255b4164b5132a0987e9aec8358.
  - PR 844 is a checkpoint-only draft with no implementation and is seven main commits behind at the preflight observation.
  - No other open TCR-003 or StaticMapData implementation owner was found.
  - The pinned research schema is beats-dh/Beats-Assets-Editor@ed827be34c279d1279ad3dde3af434b148ac05c7 and is read-only format evidence; source copying is excluded.
  - The exact user-supplied StaticMapData input remains outside Git, is 1469283 bytes, and has SHA-256 0967af2eacdd8f2a608e738b9042362676167d6c6455e60d08db7ae16cf7ea53.
  - The reviewed real file is raw protobuf with 995 house records, no duplicate house IDs and no invalid declared dimension or encoded-cell-span relationships.
  - For every reviewed house, encoded row count plus the sum of row flags equals width multiplied by height multiplied by floors.
derived:
  - Row flags must be preserved as source evidence and may support deterministic encoded-cell-span validation without inventing OTBM coordinates or item mappings.
unknown:
  - Exact client build identity remains unknown unless separately proven by the stable manifest.
  - The semantic meaning of each row flag beyond its observed encoded-cell-span contribution remains unresolved and must not be renamed into stronger semantics.
conflicts: []
first_failure:
  marker: none
  evidence: implementation has not started on this fresh branch
rejected_hypotheses:
  - Reuse an existing Canary StaticMapData index: no canonical implementation or differently named equivalent surfaced in current repository, catalogue, task or PR searches.
  - Copy the external Rust/protobuf implementation: programme licensing and architecture boundaries require an independent Canary implementation.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-tcr-003-staticmapdata-house-index.md
validation:
  - command: GitHub ownership/reuse/current-main preflight
    result: PASS
    evidence: no overlapping owner; fresh branch created from main 879fbfaff75b4255b4164b5132a0987e9aec8358
  - command: bounded independent real-file wire-shape analysis outside Git
    result: PASS
    evidence: 995 houses; source SHA-256 0967af2eacdd8f2a608e738b9042362676167d6c6455e60d08db7ae16cf7ea53; all encoded cell spans match declared dimensions
blockers: []
next_action: Open the bounded TCR-003 implementation draft PR from this fresh branch, then implement the independently defined producer and focused tests on the claimed paths.
```
