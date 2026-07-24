---
task_id: CAN-20260724-tcr-005-house-reference-parity
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/tcr-005-house-reference-parity
base_branch: main
created: 2026-07-24T10:35:00+02:00
updated: 2026-07-24T13:49:00+02:00
last_verified_commit: "48c03907e313776360e7e13a1c26fb771889a827"
risk: medium
related_issue: ""
related_pr: 868
depends_on:
  - TCR-001 merged stable canary-tibia-client-reference-manifest-v1
  - TCR-002/TCR-002A merged stable canary-tibia-staticdata-index-v1 schemaVersion 2
  - TCR-003 merged stable canary-tibia-staticmapdata-index-v1
  - Unified OTBM World Index merged stable canary-otbm-world-index-v1
blocks:
  - TCR-010
  - TCR-011
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-tcr-005-house-reference-parity.md
    - tools/ai-agent/otbm_house_reference_parity.py
    - tools/ai-agent/otbm_house_reference_parity_tool.py
    - tools/ai-agent/test_otbm_house_reference_parity.py
    - docs/ai-agent/OTBM_HOUSE_REFERENCE_PARITY.md
    - docs/ai-agent/OTBM_HOUSE_REFERENCE_PARITY.schema.json
    - docs/ai-agent/OTBM_HOUSE_ID_RESOLVER.schema.json
  shared:
    - .github/workflows/tibia-client-reference.yml
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - tools/ai-agent/otbm_world_index.py
    - tools/ai-agent/otbm_item_audit_scan.cpp
    - tools/ai-agent/tibia_staticdata_reference_index.py
    - tools/ai-agent/tibia_staticmapdata_reference_index.py
    - docs/ai-agent/OTBM_WORLD_INDEX.md
    - docs/ai-agent/TIBIA_STATICDATA_REFERENCE_INDEX.md
    - docs/ai-agent/TIBIA_STATICMAPDATA_REFERENCE_INDEX.md
    - docs/ai-agent/OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md
    - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
modules_touched:
  - OTBM Tibia client reference architecture
  - OTBM house evidence correlation
reuses:
  - canary-tibia-client-reference-manifest-v1
  - canary-tibia-staticdata-index-v1 schemaVersion 2 houseFieldOrder contract
  - canary-tibia-staticmapdata-index-v1
  - canary-otbm-world-index-v1 and WorldIndex reader
  - existing Geometry / Critical Access / Reachability evidence only as optional future inputs, without recomputation
public_interfaces:
  - canary-otbm-house-reference-parity-v1
  - canary-otbm-house-id-resolver-v1
cross_repo_tasks: []
---

# Goal

Implement the bounded, deterministic, read-only TCR-005 `canary-otbm-house-reference-parity-v1` consumer. Correlate exact StaticData house registry evidence, StaticMapData house-layout evidence and canonical OTBM World Index house evidence only through one explicit provenance-pinned `canary-otbm-house-id-resolver-v1` input. Preserve object-ID uncertainty and emit review findings only.

# Acceptance criteria

- Exact manifest, StaticData index, StaticMapData index, World Index binary/manifest and resolver provenance are validated.
- No direct client-reference house-ID to OTBM house-ID equality is assumed without the explicit resolver.
- Resolver supports reviewed exact-identity binding for one pinned evidence pair and explicit one-to-one mappings; ambiguous, duplicate, conflicting, stale or unbound mappings fail closed or remain explicit findings.
- StaticData registry presence, position and reviewed declared-size semantics remain distinct from StaticMapData layout origin/dimensions/floors and OTBM observed house-tile bounds/counts/floors.
- TCR-002A schemaVersion 2 `houseFieldOrder` is mandatory; unresolved raw field 5/7 evidence never becomes semantic `size`/`beds` inside this consumer.
- Exact OTBM house-door placements are grouped using the existing World Index reader.
- StaticMapData `object_id` remains unresolved and is never compared to OTBM/server item IDs.
- Findings use bounded review states including conforming, reference-only, otbm-only, mismatch, partial, unresolved-id-space, conflicting and stale-evidence.
- No OTBM parser, pathfinder, geometry recomputation, mutation, gameplay conclusion or proprietary input is added.
- Focused tests, bytecode compilation, schema syntax/validation, CLI construction, dedicated workflow and final repository gate pass.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T13:49:00+02:00
head: 48c03907e313776360e7e13a1c26fb771889a827
branch: feat/tcr-005-house-reference-parity
pr: 868
status: validating
context_routes:
  - agent-governance
  - otbm
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-tcr-005-house-reference-parity.md
  - tools/ai-agent/otbm_house_reference_parity.py
  - tools/ai-agent/otbm_house_reference_parity_tool.py
  - tools/ai-agent/test_otbm_house_reference_parity.py
  - docs/ai-agent/OTBM_HOUSE_REFERENCE_PARITY.md
  - docs/ai-agent/OTBM_HOUSE_REFERENCE_PARITY.schema.json
  - docs/ai-agent/OTBM_HOUSE_ID_RESOLVER.schema.json
  - .github/workflows/tibia-client-reference.yml
  - docs/agents/MODULE_CATALOG.md
proven:
  - TCR-002A PR 870 merged as c0911f7755aac65c176be69070fb7ec07045baff and removes the HouseData field-order blocker.
  - Draft PR 868 remains the sole current TCR-005 owner and is a clean one-commit, nine-path diff based directly on main 13ec3077babba0ac81bb1e30e79f0ea4827ae2fe.
  - Exact user OTBM SHA-256 a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2 reproduces the canonical World Index with 17972761 tiles, 23359571 placements, 9339 mechanic placements and zero unknown attribute tails.
  - Exact user StaticData SHA-256 0bd51e1660f9d58594eb10000c35ea51113fc668aa3ee416c8c6b7ebb59b78ff produces 995 houses under reviewed newer HouseData field ordering in schemaVersion 2.
  - Exact user StaticMapData SHA-256 0967af2eacdd8f2a608e738b9042362676167d6c6455e60d08db7ae16cf7ea53 produces 995 houses, 117716 rows, 188014 tile records and zero duplicate/missing/dimension findings.
  - Exact registry-position resolver maps 993 client house IDs to 993 unique OTBM house IDs using only the exact StaticData position tile and canonical World Index houseId; there are zero collisions and no unmapped OTBM house IDs.
  - Client house IDs 101 and 102 remain unresolved because positions 31966,31911,7 and 31940,31886,7 have no OTBM tile.
  - The consumer requires StaticData schemaVersion 2 or later and matching source/category/policy houseFieldOrder declarations; resolved orders require reviewed evidence.
  - Unresolved StaticData HouseData records preserve raw houseField5/houseField7 and skip declared-size comparison.
  - Resolver validation rejects stale provenance, unknown IDs, duplicate client/OTBM IDs and unsupported mapping methods.
  - Fixture validation passes 14 focused tests with one exact-input opt-in skipped; exact-input validation passes all 14 tests.
  - Exact resolver summary is 995 client houses, 993 mappings, two unresolved and zero conflicts.
  - Exact parity summary is 995 rows, 993 mismatch rows, two unresolved-id-space rows, 42 orphan house-door placements and zero conforming rows.
  - MODULE_CATALOG contains exactly one reusable TCR-005 contract row and preserves all concurrent catalogue entries.
  - Agent Task Ownership, Tibia Client Reference, OTBM Map Tools, AI Agent Tools and repository CI/Required passed on exact implementation head 74fbae108dc4a0461351f31515f6b1108311c027.
  - The ci:final-gate label was applied before this final checkpoint commit; no further implementation or documentation changes are planned before ready-state validation.
derived:
  - Registry position is a viable explicit one-to-one resolver method for this exact evidence pair; it does not use names, proximity or numeric identity.
  - Corrected `size` semantics still differ from observed OTBM house-tile population for all 993 resolved houses; these are review findings, not automatic gameplay defects.
  - StaticMapData layout origin/dimensions also produce independent review mismatches for a subset of houses and must remain separate from registry-size findings.
unknown:
  - Exact client build identity unless separately proven by the stable client-reference manifest.
  - Mapping from staticmapdata.object_id to OTBM/server/appearance identifiers.
  - Whether registry declared size and OTBM house-tile population are intended to be identical gameplay concepts for every house.
conflicts: []
first_failure:
  marker: initial exact TCR-005 run before TCR-002A
  evidence: legacy top-level schema incorrectly determined nested HouseData field order; fixed by merged PR 870 before publishing this consumer
rejected_hypotheses:
  - Build another OTBM parser or scan the OTBM directly in TCR-005: forbidden because World Index is canonical.
  - Join houses by name or proximity: forbidden heuristic mapping.
  - Treat client and OTBM house IDs as numerically identical: unproven without a resolver.
  - Treat staticmapdata.object_id as OTBM itemId: explicitly unproven.
  - Reinterpret unresolved StaticData field 5/7 inside TCR-005: TCR-002A owns that semantic boundary.
changed_paths:
  - .github/workflows/tibia-client-reference.yml
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260724-tcr-005-house-reference-parity.md
  - docs/ai-agent/OTBM_HOUSE_ID_RESOLVER.schema.json
  - docs/ai-agent/OTBM_HOUSE_REFERENCE_PARITY.md
  - docs/ai-agent/OTBM_HOUSE_REFERENCE_PARITY.schema.json
  - tools/ai-agent/otbm_house_reference_parity.py
  - tools/ai-agent/otbm_house_reference_parity_tool.py
  - tools/ai-agent/test_otbm_house_reference_parity.py
validation:
  - command: python -m unittest discover -s tools/ai-agent -p test_otbm_house_reference_parity.py -v
    result: PASS
    evidence: 14 tests passed; one exact-input opt-in skipped
  - command: CANARY_TCR005_EXACT_DIR=<outside-git> CANARY_TCR005_STATICDATA_INDEX=<reviewed-index> python -m unittest discover -s tools/ai-agent -p test_otbm_house_reference_parity.py -v
    result: PASS
    evidence: all 14 tests passed against exact OTBM/StaticData/StaticMapData/World Index evidence
  - command: python -m py_compile tools/ai-agent/otbm_house_reference_parity.py tools/ai-agent/otbm_house_reference_parity_tool.py tools/ai-agent/test_otbm_house_reference_parity.py
    result: PASS
    evidence: local compilation completed without output
  - command: Draft 2020-12 schema validation of exact resolver and parity outputs
    result: PASS
    evidence: zero validation errors for both generated reports
  - command: GitHub Agent Task Ownership workflow on 74fbae108dc4a0461351f31515f6b1108311c027
    result: PASS
    evidence: run 30090576047
  - command: GitHub Tibia Client Reference workflow on 74fbae108dc4a0461351f31515f6b1108311c027
    result: PASS
    evidence: run 30090576041
  - command: GitHub OTBM Map Tools workflow on 74fbae108dc4a0461351f31515f6b1108311c027
    result: PASS
    evidence: run 30090576018
  - command: GitHub AI Agent Tools workflow on 74fbae108dc4a0461351f31515f6b1108311c027
    result: PASS
    evidence: run 30090575965
  - command: GitHub repository CI/Required workflow on 74fbae108dc4a0461351f31515f6b1108311c027
    result: PASS
    evidence: run 30090576191
blockers: []
next_action: Verify every workflow on the exact corrected checkpoint head, then mark PR 868 ready and enable auto-merge if all required checks are green.
```
