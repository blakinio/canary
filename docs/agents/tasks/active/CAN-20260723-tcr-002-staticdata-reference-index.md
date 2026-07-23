---
task_id: CAN-20260723-tcr-002-staticdata-reference-index
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/tcr-002-staticdata-reference-index-20260723
base_branch: main
created: 2026-07-23T19:05:00+02:00
updated: 2026-07-23T19:10:00+02:00
last_verified_commit: "ef68b42b8a116695ff8449abf1bc282a80763ad7"
risk: medium
related_issue: ""
related_pr: "827"
depends_on:
  - TCR-001 merged stable canary-tibia-client-reference-manifest-v1
blocks:
  - TCR-005
  - TCR-006
  - TCR-009
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-tcr-002-staticdata-reference-index.md
    - tools/ai-agent/tibia_staticdata_reference_index.py
    - tools/ai-agent/tibia_staticdata_reference_index_tool.py
    - tools/ai-agent/test_tibia_staticdata_reference_index.py
    - docs/ai-agent/TIBIA_STATICDATA_REFERENCE_INDEX.md
    - docs/ai-agent/TIBIA_STATICDATA_REFERENCE_INDEX.schema.json
    - .github/workflows/tibia-client-reference.yml
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
    - docs/ai-agent/OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md
    - tools/ai-agent/tibia_client_reference_manifest.py
modules_touched:
  - OTBM analysis tooling
  - official-client reference evidence
reuses:
  - canary-tibia-client-reference-manifest-v1 exact provenance contract
  - existing otbm-tooling discovery ownership
  - existing Tibia Client Reference validation workflow
  - Python standard-library deterministic JSON and bounded file handling conventions
public_interfaces:
  - canary-tibia-staticdata-index-v1
cross_repo_tasks: []
---

# Goal

Deliver exactly TCR-002 StaticData Reference Index: a deterministic, read-only `canary-tibia-staticdata-index-v1` producer that consumes exact stable TCR-001 manifest provenance, independently handles the verified legacy/newer StaticData schema families, fails closed on ambiguous or unsupported schema, bounds raw/XZ/LZMA input expansion, preserves source categories/schema, emits duplicate-ID and missing-field findings, and never upgrades registry presence into gameplay proof.

# Scope boundaries

- No TCR-003 StaticMapData implementation.
- No TCR-004 proficiency implementation.
- No OWA-003 implementation.
- No OTBM parsing, map mutation, runtime mutation, protocol mutation or client mutation.
- No proprietary Tibia client files or derived large dumps committed to Git.
- External `beats-dh/Beats-Assets-Editor@ed827be34c279d1279ad3dde3af434b148ac05c7` remains read-only format/interoperability research only; implementation is independent.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T19:10:00+02:00
head: ef68b42b8a116695ff8449abf1bc282a80763ad7
branch: feat/tcr-002-staticdata-reference-index-20260723
pr: 827
status: implementing
context_routes:
  - agent-governance
  - otbm
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-tcr-002-staticdata-reference-index.md
  - tools/ai-agent/tibia_staticdata_reference_index.py
  - tools/ai-agent/tibia_staticdata_reference_index_tool.py
  - tools/ai-agent/test_tibia_staticdata_reference_index.py
  - docs/ai-agent/TIBIA_STATICDATA_REFERENCE_INDEX.md
  - docs/ai-agent/TIBIA_STATICDATA_REFERENCE_INDEX.schema.json
  - .github/workflows/tibia-client-reference.yml
proven:
  - TCR-001 feature PR 809 merged as 3227ee1e3b5f323656b101a601f873ae21b61f27 and lifecycle closure PR 812 merged as ea2b465967d4f96e38982b42db466dae4766c619.
  - Current programme queue marks TCR-002 StaticData Reference Index as the first dependency-satisfied next candidate and forbids bundling TCR-003.
  - Fresh open-PR and branch searches found no TCR-002 or StaticData-index owner before this task branch was created.
  - Existing MODULE_CATALOG keeps one otbm-tooling/TCR discovery owner; no second OTBM parser World Index pathfinder renderer Script Resolution engine or E2E platform is permitted.
  - Pinned research schemas define legacy top-level fields creatures=1 titles=2 houses=3 bosses=4 quests=5 and newer fields monsters=1 monster_classes=2 achievements=3 houses=4 bosses=5 quests=6.
  - Pinned research source confirms raw protobuf plus XZ/LZMA handling and documents Tibia LZMA streams with an incorrect 8-byte uncompressed-size header field; source code is not copied.
  - A user-supplied external assets ZIP outside Git contains one staticdata DAT whose filename hash matches SHA-256 0bd51e1660f9d58594eb10000c35ea51113fc668aa3ee416c8c6b7ebb59b78ff and whose bytes begin as raw protobuf; it is available only for opt-in local validation and must not be committed.
  - Draft PR 827 exists for this task at exact ownership head ef68b42b8a116695ff8449abf1bc282a80763ad7.
  - Existing .github/workflows/tibia-client-reference.yml is the reusable validation workflow for this programme; TCR-002 will extend it instead of adding a second workflow.
derived:
  - The smallest complete implementation can remain Python 3.12 standard-library only by parsing the bounded protobuf wire format independently and using stdlib lzma for XZ/LZMA containers.
  - Schema selection should use explicit top-level/category wire-shape discriminators and candidate structural validation; if both known schemas remain plausible without discriminating evidence, the tool must fail as ambiguous rather than apply a round-trip-length tie-breaker.
  - The indexer can consume stable manifest provenance without duplicating package-root path confinement by requiring an explicit source file and verifying its exact size/SHA-256 against one selectedInputs entry from the manifest.
  - Legacy title and newer achievement categories must remain separately named in output; quest records stay ID/name inventory only.
unknown:
  - Exact final output schema fields until the first implementation/test pass is reviewed against deterministic fixtures and the external real StaticData sample.
  - Whether Python stdlib LZMA-alone decoding with the independently reproduced Tibia header correction covers the exact user-supplied compressed variant; focused synthetic tests will cover standard XZ/LZMA and external validation will remain fail-closed.
conflicts: []
first_failure:
  marker: none
  evidence: fresh preflight found no ownership or dependency blocker
rejected_hypotheses:
  - Reuse the external Rust parser implementation directly; licensing boundary requires independent implementation.
  - Use successful protobuf decoding alone as schema proof; unknown fields can be skipped and silently relabel categories.
  - Treat static registry agreement as gameplay runtime quest or map parity proof.
  - Add a second dedicated StaticData workflow; the existing Tibia Client Reference workflow is the correct programme validation owner.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-tcr-002-staticdata-reference-index.md
validation:
  - command: fresh main/open-PR/branch/programme/module-catalog preflight
    result: PASS
    evidence: TCR-002 unowned unblocked dependency-satisfied and no canonical StaticData index found
  - command: early draft PR ownership publication
    result: PASS
    evidence: PR 827 opened from feat/tcr-002-staticdata-reference-index-20260723 to blakinio/canary main
blockers: []
next_action: Independently implement the bounded StaticData index library CLI tests schema docs and extend the existing Tibia Client Reference workflow; validate Canary-owned legacy/new fixtures plus the opt-in user-supplied real file outside Git before final-gate readiness.
```
