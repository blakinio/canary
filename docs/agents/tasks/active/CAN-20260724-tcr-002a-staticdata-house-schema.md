---
task_id: CAN-20260724-tcr-002a-staticdata-house-schema
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: implementing
agent: "GPT-5.6 Thinking"
branch: fix/tcr-002a-staticdata-house-schema
base_branch: main
created: 2026-07-24T11:38:00+02:00
updated: 2026-07-24T12:10:00+02:00
last_verified_commit: "fc493be73a0dcce2467659d13ba37b0a78f7d4ad"
risk: medium
related_issue: ""
related_pr: 870
depends_on:
  - TCR-001 merged stable canary-tibia-client-reference-manifest-v1
  - TCR-002 merged stable canary-tibia-staticdata-index-v1
blocks:
  - CAN-20260724-tcr-005-house-reference-parity
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-tcr-002a-staticdata-house-schema.md
    - tools/ai-agent/tibia_staticdata_reference_index.py
    - tools/ai-agent/tibia_staticdata_reference_index_tool.py
    - tools/ai-agent/test_tibia_staticdata_reference_index.py
    - docs/ai-agent/TIBIA_STATICDATA_REFERENCE_INDEX.md
    - docs/ai-agent/TIBIA_STATICDATA_REFERENCE_INDEX.schema.json
  shared:
    - .github/workflows/tibia-client-reference.yml
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - docs/agents/tasks/active/CAN-20260724-tcr-005-house-reference-parity.md
    - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
    - docs/ai-agent/OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md
modules_touched:
  - official-client StaticData reference evidence
  - OTBM Tibia client reference architecture
reuses:
  - existing canary-tibia-staticdata-index-v1 parser and exact manifest binding
  - pinned read-only Beats Assets Editor legacy/newer protobuf evidence
public_interfaces:
  - canary-tibia-staticdata-index-v1 schemaVersion 2
cross_repo_tasks: []
---

# Goal

Correct TCR-002 HouseData normalization for hybrid StaticData files where the top-level category layout and nested house field ordering do not belong to the same reviewed schema family. Preserve field 5/7 values without guessing when unresolved, and require explicit reviewed field-order evidence before emitting semantic `size` and `beds` labels.

# Acceptance criteria

- Top-level StaticData schema-family selection remains independent and deterministic.
- House field ordering is represented separately as `legacy`, `newer` or `unresolved`.
- `unresolved` preserves raw field-5 and field-7 values and omits semantic `size`/`beds` labels.
- `legacy` maps field 5 to `size` and field 7 to `beds` only with explicit reviewed evidence metadata.
- `newer` maps field 5 to `beds` and field 7 to `size` only with explicit reviewed evidence metadata.
- The exact selected file SHA-256 `0bd51e1660f9d58594eb10000c35ea51113fc668aa3ee416c8c6b7ebb59b78ff` validates as legacy top-level plus reviewed newer house ordering.
- Existing non-house record normalization, fail-closed protobuf handling, provenance binding, output safety and deterministic ordering remain unchanged.
- The public format remains `canary-tibia-staticdata-index-v1` with schemaVersion 2 and explicit migration documentation.
- No client files or generated exact-file output are committed.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T12:10:00+02:00
head: fc493be73a0dcce2467659d13ba37b0a78f7d4ad
branch: fix/tcr-002a-staticdata-house-schema
pr: 870
status: final-gate
context_routes:
  - agent-governance
  - otbm
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-tcr-002a-staticdata-house-schema.md
  - tools/ai-agent/tibia_staticdata_reference_index.py
  - tools/ai-agent/tibia_staticdata_reference_index_tool.py
  - tools/ai-agent/test_tibia_staticdata_reference_index.py
  - docs/ai-agent/TIBIA_STATICDATA_REFERENCE_INDEX.md
  - docs/ai-agent/TIBIA_STATICDATA_REFERENCE_INDEX.schema.json
  - docs/agents/MODULE_CATALOG.md
proven:
  - Draft PR 870 is the sole TCR-002A owner; TCR-005 PR 868 remains intentionally blocked and read-only toward this producer.
  - PR 870 is synchronized with main b1d24ec362ec52652886f6be6129234ff44e7d4d and preserves the concurrent E2E module-catalogue registration.
  - Pinned legacy proto at beats-dh/Beats-Assets-Editor@ed827be34c279d1279ad3dde3af434b148ac05c7 defines HouseData field 5=size and field 7=beds.
  - Pinned newer proto at the same commit defines House field 5=beds and field 7=size.
  - Exact StaticData SHA-256 0bd51e1660f9d58594eb10000c35ea51113fc668aa3ee416c8c6b7ebb59b78ff selects the legacy top-level category layout but exhibits newer-style nested house values.
  - Exact field-5 values range 0..34 with median 2; exact field-7 values range 5..750 with median 26 across 995 houses.
  - Existing schemaVersion 1 normalizes Spiritkeep as size=23,beds=382 and Sunset Homes Flat 01 as size=1,beds=13, proving that top-level schema selection cannot safely determine nested house semantics.
  - schemaVersion 2 separates source.schemaFamily from source.houseFieldOrder.
  - Default unresolved mode emits houseField5 and houseField7, omits semantic size/beds, records one unresolvedHouseFieldOrder finding and forbids claimed review metadata.
  - Reviewed legacy/newer modes require non-empty reviewId and statement; no distribution or numeric heuristic is used.
  - Reviewed newer exact-file output normalizes Spiritkeep as beds=23,size=382 and Sunset Homes Flat 01 as beds=1,size=13.
  - Module catalogue explicitly warns consumers not to use semantic house size/beds unless houseFieldOrder is reviewed.
  - Durable PR diff contains exactly seven expected task, parser, CLI, tests, docs, schema and catalogue paths; all temporary workflows are absent.
  - Agent Task Ownership, Tibia Client Reference, repository CI/Required and AI Agent Tools passed on implementation head fc493be73a0dcce2467659d13ba37b0a78f7d4ad.
  - The ci:final-gate label was applied before this final checkpoint commit.
derived:
  - StaticData schema-family and HouseData field-order evidence are independent dimensions.
  - Default unresolved preservation is safer than silently applying either proto ordering.
  - TCR-005 may consume semantic size/beds only from a reviewed resolved schemaVersion 2 index.
unknown:
  - Exact client build identity unless separately proven by the stable manifest.
  - Whether additional nested submessage hybrids exist in later StaticData files.
conflicts:
  - schemaVersion 1 labels field 5/7 semantically from top-level schema family and is unsafe for hybrid files; schemaVersion 2 is the corrective migration.
first_failure:
  marker: exact TCR-005 declared-size parity preflight
  evidence: all 993 resolved houses became size mismatches under schemaVersion 1 labels; pinned proto comparison and exact field distributions identify hybrid HouseData ordering
rejected_hypotheses:
  - Infer house order automatically from distributions: rejected as an undocumented heuristic.
  - Swap fields only in TCR-005: rejected because producer normalization owns this semantic boundary.
  - Treat all legacy top-level files as legacy HouseData forever: disproven by the exact selected file.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-tcr-002a-staticdata-house-schema.md
  - docs/agents/MODULE_CATALOG.md
  - tools/ai-agent/tibia_staticdata_reference_index.py
  - tools/ai-agent/tibia_staticdata_reference_index_tool.py
  - tools/ai-agent/test_tibia_staticdata_reference_index.py
  - docs/ai-agent/TIBIA_STATICDATA_REFERENCE_INDEX.md
  - docs/ai-agent/TIBIA_STATICDATA_REFERENCE_INDEX.schema.json
validation:
  - command: python -m unittest discover -s tools/ai-agent -p test_tibia_staticdata_reference_index.py -v
    result: PASS
    evidence: 22 fixture tests passed; one opt-in exact-file test skipped
  - command: CANARY_TIBIA_STATICDATA_FILE=<exact-file> python -m unittest discover -s tools/ai-agent -p test_tibia_staticdata_reference_index.py -v
    result: PASS
    evidence: 22 tests passed against exact SHA-256 0bd51e1660f9d58594eb10000c35ea51113fc668aa3ee416c8c6b7ebb59b78ff
  - command: python -m py_compile tools/ai-agent/tibia_staticdata_reference_index.py tools/ai-agent/tibia_staticdata_reference_index_tool.py tools/ai-agent/test_tibia_staticdata_reference_index.py
    result: PASS
    evidence: local compilation completed without output
  - command: python -m json.tool docs/ai-agent/TIBIA_STATICDATA_REFERENCE_INDEX.schema.json
    result: PASS
    evidence: schema syntax and representative Draft 2020-12 unresolved/reviewed payload validation passed
  - command: python tools/ai-agent/tibia_staticdata_reference_index_tool.py --help
    result: PASS
    evidence: CLI construction completed without output
  - command: exact unresolved output
    result: PASS
    evidence: 995 houses; SHA-256 cde03439e05f49d973a929189c56754b63df6ee1b08a5bb02478402a2bf48a5c; generated outside Git
  - command: exact reviewed-newer output
    result: PASS
    evidence: 995 houses; SHA-256 0d07a36cd5bff13b73e46bfffed278c8499599ad18032e2b9d58a4bfe9222813; generated outside Git
  - command: GitHub Agent Task Ownership on fc493be73a0dcce2467659d13ba37b0a78f7d4ad
    result: PASS
    evidence: run 30084990463
  - command: GitHub Tibia Client Reference on fc493be73a0dcce2467659d13ba37b0a78f7d4ad
    result: PASS
    evidence: run 30084990631
  - command: GitHub CI/Required on fc493be73a0dcce2467659d13ba37b0a78f7d4ad
    result: PASS
    evidence: run 30084990646
  - command: GitHub AI Agent Tools on fc493be73a0dcce2467659d13ba37b0a78f7d4ad
    result: PASS
    evidence: run 30084990555
blockers: []
next_action: Verify every final-gate workflow on the exact new checkpoint head, then mark PR 870 ready and enable auto-merge if green.
```
