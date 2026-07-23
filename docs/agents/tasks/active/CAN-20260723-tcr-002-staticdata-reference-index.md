---
task_id: CAN-20260723-tcr-002-staticdata-reference-index
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: active
agent: "GPT-5.6 Thinking"
branch: feat/tcr-002-staticdata-reference-index-20260723
base_branch: main
created: 2026-07-23T19:05:00+02:00
updated: 2026-07-23T22:05:00+02:00
last_verified_commit: "a50823b41a784894cf5c1abf5b22f36cbf987d86"
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
- Shared discovery/changelog status is updated only after the producer actually merges and becomes stable; feature PR #827 does not publish premature `merged/stable` catalogue state.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T22:05:00+02:00
head: a50823b41a784894cf5c1abf5b22f36cbf987d86
branch: feat/tcr-002-staticdata-reference-index-20260723
pr: 827
status: validating
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
  - Existing MODULE_CATALOG keeps one otbm-tooling/TCR discovery owner and forbids a second OTBM parser, World Index, pathfinder, renderer, Script Resolution engine or E2E platform; pinned research schemas define legacy top-level creatures=1 titles=2 houses=3 bosses=4 quests=5 and newer monsters=1 monster_classes=2 achievements=3 houses=4 bosses=5 quests=6.
  - Pinned research source confirms raw protobuf plus XZ/LZMA handling and documents Tibia LZMA streams with an incorrect 8-byte uncompressed-size header field; source code is not copied.
  - `canary-tibia-staticdata-index-v1` independently implements bounded protobuf wire parsing with strict legacy/newer field validation, explicit discriminators and fail-closed ambiguous/conflicting/unsupported schema handling.
  - The indexer requires one explicit source file and exact stable-manifest selected-input ID, size and SHA-256 agreement before parsing; local absolute paths are not emitted.
  - Raw protobuf, XZ, LZMA-alone and the reviewed Tibia LZMA header variant are supported under explicit encoded/decompressed/record bounds.
  - Output preserves source-family categories, deterministic ordering and source ordinals; findings expose duplicate IDs, missing id/name fields and duplicate singular fields.
  - Quest records are intentionally ID/name inventory only and policy.gameplayConclusions is false.
  - Nineteen focused StaticData tests pass locally; the opt-in real-file test is skipped unless CANARY_TIBIA_STATICDATA_FILE is explicitly supplied.
  - Private opt-in validation against the user-supplied external StaticData file outside Git selected legacy schema, parsed 2700 top-level records (812 creatures, 356 titles, 995 houses, 438 bosses, 99 quests) and reported zero duplicate-ID, missing-required-field or duplicate-singular-field findings; no proprietary bytes or record dump is committed.
  - Draft head 2a622199e57bb90578d7d14ffece1ab6b4c97ca2 passed repository CI run 30028730076, AI Agent Tools run 30028729754, Agent Task Ownership run 30028729771 and Tibia Client Reference run 30028729701.
  - An attempted shared MODULE_CATALOG status update was fully removed before finalization after detecting an unrelated stale-line replacement; PR #827 is back to exactly seven intended feature/task/workflow files and current main drift is non-overlapping.
  - First final-gate head 961e4dad1d7c50bd736d4ec6c6f800e06abc178b passed Tibia Client Reference but Agent Task Ownership rejected only checkpoint status `review`; the checkpoint now uses accepted `validating` status.
  - Final-gate metadata corrections then reduced `proven` from 17 to 16 and restored the active task record's top-level `status: active`; these changes are task-record-only and do not alter the implementation.
derived:
  - The stable v1 output schema is now the committed `docs/ai-agent/TIBIA_STATICDATA_REFERENCE_INDEX.schema.json` plus the producer implementation and documentation in this PR.
  - Strict structural candidate validation plus schema-specific discriminators avoids the external implementation's permissive unknown-field/round-trip heuristic while remaining independently implemented.
  - Stable manifest hash binding is sufficient for exact selected-input provenance without duplicating the TCR-001 package-root traversal implementation.
  - Legacy title and newer achievement categories remain separately named; legacy/newer house field ordering is normalized only after exact schema selection.
  - StaticData registry agreement can later feed bounded TCR correlation packages but cannot by itself prove Canary gameplay/runtime parity.
unknown:
  - The user-supplied real sample is raw protobuf; compressed real-client variants are covered by independent synthetic XZ/LZMA/Tibia-header fixtures but not by a second proprietary real compressed sample.
conflicts: []
first_failure:
  marker: active-record-status
  evidence: exact-head Agent Task Ownership run 30044538094 rejected only top-level status validating for a record under tasks/active; checkpoint status remains validating while the task record itself is restored to active in this commit
rejected_hypotheses:
  - Reuse the external Rust parser implementation directly; licensing boundary requires independent implementation.
  - Use successful protobuf decoding alone as schema proof; unknown fields can be skipped and silently relabel categories.
  - Use a round-trip encoded-length tie-breaker when both schemas remain plausible; ambiguity must fail closed.
  - Treat static registry agreement as gameplay runtime quest or map parity proof.
  - Add a second dedicated StaticData workflow; the existing Tibia Client Reference workflow is the correct programme validation owner.
  - Keep the accidental broad MODULE_CATALOG replacement; it was reverted completely rather than risking unrelated shared-file regression.
changed_paths:
  - .github/workflows/tibia-client-reference.yml
  - docs/agents/tasks/active/CAN-20260723-tcr-002-staticdata-reference-index.md
  - docs/ai-agent/TIBIA_STATICDATA_REFERENCE_INDEX.md
  - docs/ai-agent/TIBIA_STATICDATA_REFERENCE_INDEX.schema.json
  - tools/ai-agent/test_tibia_staticdata_reference_index.py
  - tools/ai-agent/tibia_staticdata_reference_index.py
  - tools/ai-agent/tibia_staticdata_reference_index_tool.py
validation:
  - command: fresh main/open-PR/branch/programme/module-catalog preflight
    result: PASS
    evidence: TCR-002 was unowned, unblocked and dependency-satisfied; no canonical StaticData index existed
  - command: python -m unittest discover -s tools/ai-agent -p test_tibia_staticdata_reference_index.py -v
    result: PASS
    evidence: 19 focused tests pass; one opt-in real-file test is skipped without CANARY_TIBIA_STATICDATA_FILE
  - command: CANARY_TIBIA_STATICDATA_FILE=/mnt/data/staticdata-user.dat python -m unittest discover -s tools/ai-agent -p test_tibia_staticdata_reference_index.py -v
    result: PASS
    evidence: private external real-file validation completed without committing proprietary input or record data
  - command: GitHub Actions draft-head validation for 2a622199e57bb90578d7d14ffece1ab6b4c97ca2
    result: PASS
    evidence: CI 30028730076; AI Agent Tools 30028729754; Agent Task Ownership 30028729771; Tibia Client Reference 30028729701
  - command: GitHub Actions first final-gate validation for 961e4dad1d7c50bd736d4ec6c6f800e06abc178b
    result: FAIL
    evidence: Agent Task Ownership 30030157959 rejected only unsupported checkpoint status review; Tibia Client Reference 30030158023 passed
  - command: GitHub Actions compactness-corrected final-gate validation for a50823b41a784894cf5c1abf5b22f36cbf987d86
    result: FAIL
    evidence: Agent Task Ownership 30044538094 rejected only top-level task status validating under tasks/active; repository CI 30044538353 and Tibia Client Reference 30044538140 passed, with AI Agent Tools still non-failing at inspection time
  - command: compare current main drift against PR base ownership paths
    result: PASS
    evidence: current main advance adds only bounty/weekly forum evidence paths and does not overlap TCR-002 owned paths
blockers: []
next_action: Validate all required workflows on the corrected immutable exact final head produced by this checkpoint commit under ci:final-gate; if green, mark PR 827 ready, require protected ready-state Required PASS, perform atomic head/review/main-drift checks, then squash-merge and close TCR-002 lifecycle in a separate bounded documentation PR.
```
