---
task_id: CAN-20260724-tcr-006-content-reference-correlation
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/tcr-006-content-reference-correlation
base_branch: main
created: 2026-07-24T17:00:00+02:00
updated: 2026-07-24T17:39:06+02:00
last_verified_commit: "77c38568fe02b55798d0710318c4f82c8d1fd3d8"
risk: medium
related_issue: ""
related_pr: 880
depends_on:
  - TCR-001 merged stable canary-tibia-client-reference-manifest-v1
  - TCR-002/TCR-002A merged stable canary-tibia-staticdata-index-v1 schemaVersion 2
blocks:
  - TCR-010
  - TCR-011
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-tcr-006-content-reference-correlation.md
    - tools/ai-agent/tibia_content_reference_correlation.py
    - tools/ai-agent/tibia_content_reference_correlation_tool.py
    - tools/ai-agent/test_tibia_content_reference_correlation.py
    - docs/ai-agent/TIBIA_CONTENT_REFERENCE_CORRELATION.md
    - docs/ai-agent/TIBIA_CONTENT_REFERENCE_CORRELATION.schema.json
    - docs/ai-agent/TIBIA_CONTENT_REFERENCE_RESOLVER.schema.json
  shared:
    - .github/workflows/tibia-client-reference.yml
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - tools/ai-agent/tibia_staticdata_reference_index.py
    - tools/ai-agent/achievement_validation.py
    - tools/ai-agent/cyclopedia_validation.py
    - tools/ai-agent/otbm_spawn_npc.py
    - tools/ai-agent/otbm_spawn_npc_validation.py
    - tools/ai-agent/quest_map_validation.py
    - tools/ai-agent/otbm_storage_graph.py
    - tools/ai-agent/otbm_quest_state_reachability.py
    - docs/ai-agent/TIBIA_STATICDATA_REFERENCE_INDEX.md
    - docs/ai-agent/OTBM_SPAWN_NPC_VALIDATION.md
    - docs/ai-agent/QUEST_MAP_VALIDATION.md
    - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
modules_touched:
  - OTBM Tibia client reference architecture
  - content reference correlation
reuses:
  - canary-tibia-client-reference-manifest-v1
  - canary-tibia-staticdata-index-v1 schemaVersion 2
  - canary-achievement-audit-v2
  - existing Cyclopedia Bestiary/Bosstiary evidence
  - canary-otbm-spawn-npc-evidence-v1
  - canary-quest-map-evidence-v1
  - existing Storage Dependency Graph and Quest State Reachability evidence
public_interfaces:
  - canary-tibia-content-reference-resolver-v1
  - canary-tibia-content-reference-correlation-v1
cross_repo_tasks: []
---

# Goal

Implement the bounded, deterministic, read-only TCR-006 content reference correlation consumer. Correlate exact StaticData creature/monster, boss, title/achievement and quest registry evidence only through existing subsystem-owned evidence plus explicit provenance-pinned identifier-resolution records. Preserve source-family vocabulary and fail closed on ambiguous or unavailable joins.

# Acceptance criteria

- Consume only a stable TCR-001 manifest and TCR-002/TCR-002A `canary-tibia-staticdata-index-v1` schemaVersion 2 report; never reparse StaticData.
- Preserve `legacy` categories (`creatures`, `titles`) and `newer` categories (`monsters`, `monsterClasses`, `achievements`) without silent relabeling.
- Exclude houses because TCR-005 owns house correlation.
- Keep creature/monster, monster-class, boss, title/achievement and quest evidence as separate dimensions.
- Reuse existing Achievement, Cyclopedia, Spawn/Boss/NPC, Quest Map, Storage Graph and Quest State Reachability owners; do not create replacement scanners or validators.
- Require exact target-report provenance and an explicit reviewed resolver for every cross-namespace mapping.
- Numeric equality, normalized name agreement and outfit agreement are candidate evidence only unless the resolver explicitly records the reviewed mapping method and supporting target evidence.
- Quest mappings require explicit reviewed source selection/evidence ownership; name similarity alone never selects quest globs, AID/UID, storage or map evidence.
- Duplicate, stale, conflicting, unknown and many-to-one mappings fail closed or remain explicit findings.
- Emit deterministic review states including `confirmed-reference`, `reference-only`, `target-only`, `partial`, `unresolved-id-space`, `conflicting` and `stale-evidence`.
- No source/datapack/map mutation, Lua execution, runtime claim, gameplay conclusion, automatic repair, TCR-007 work or proprietary client input is committed.
- Focused tests, schemas, bytecode compilation, dedicated workflow and repository final gate pass.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T17:39:06+02:00
head: 77c38568fe02b55798d0710318c4f82c8d1fd3d8
branch: feat/tcr-006-content-reference-correlation
pr: 880
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
  - content-reference
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-tcr-006-content-reference-correlation.md
  - tools/ai-agent/tibia_content_reference_correlation.py
  - tools/ai-agent/tibia_content_reference_correlation_tool.py
  - tools/ai-agent/test_tibia_content_reference_correlation.py
  - docs/ai-agent/TIBIA_CONTENT_REFERENCE_CORRELATION.md
  - docs/ai-agent/TIBIA_CONTENT_REFERENCE_CORRELATION.schema.json
  - docs/ai-agent/TIBIA_CONTENT_REFERENCE_RESOLVER.schema.json
  - .github/workflows/tibia-client-reference.yml
  - docs/agents/MODULE_CATALOG.md
proven:
  - PR 880 is the sole open TCR-006 owner; it is draft, mergeable and targets blakinio/canary main from feat/tcr-006-content-reference-correlation.
  - Live PR head is 77c38568fe02b55798d0710318c4f82c8d1fd3d8; current diff contains only the active task and temporary Tibia Client Reference workflow helper.
  - Exact legacy StaticData inventory contains 812 creatures, 356 titles, 438 bosses and 99 quests with no duplicate or missing required-field findings.
  - Owner inventory workflow 30103563037 succeeded and published artifact 8600662164 with digest sha256:041b0d357e6e5df4ecfeb186aa4611d58ecbe3533a6e7a47ae9f32b64bc53f4a.
  - Reviewed resolver candidates retain 739 creature, 236 boss and 349 title identity mappings; shared target IDs and all quest joins remain unresolved.
  - Exact correlation contains 1705 source rows with 1324 confirmed-reference, 119 partial, 160 reference-only, 102 unresolved-id-space and zero conflicts.
  - Local fixture and exact focused suites pass 20 tests; Python bytecode and both Draft 2020-12 schemas validate against exact resolver/correlation outputs.
  - Exact resolver SHA-256 is f1472c23 and exact correlation SHA-256 is 477c9ffa; full reports remain outside Git.
  - Verified implementation payload is Git blob f0446001244d636ccc8745a821b67cedc5fb9577 and unattached staging commit e6ca779f47182d95cfadd052833c30af935dc582 adds only .tcr006-stage/payload.zip.
  - Current-main catalogue helper run 30104916300 succeeded and published artifact 8601260482 with digest sha256:baf821bcc9fdc8f0bfa0df8bdcc8ceeac83a59f55979e1cee311228260776ff8.
  - Repository CI run 30104916625 and Tibia Client Reference run 30104916300 succeeded on live head 77c38568fe02b55798d0710318c4f82c8d1fd3d8.
derived:
  - A fresh staging commit must be rebuilt on the post-checkpoint branch head before materialization because e6ca779f47182d95cfadd052833c30af935dc582 is based on the prior live head.
  - Final PR history must remove the temporary workflow helper and staged ZIP while retaining only task, implementation, schemas, documentation, workflow validation and catalogue changes.
unknown:
  - Whether the materialization helper will produce byte-identical target files after rebasing the staged payload onto the new checkpoint head.
  - Final clean implementation commit SHA and final-head CI results.
conflicts: []
first_failure:
  marker: Agent Task Ownership run 30104916248 / Validate changed active task checkpoints
  evidence: CHANGED_TASK_VALIDATION.txt reports first_failure must be a YAML mapping because the prior checkpoint used first_failure null.
rejected_hypotheses:
  - Reparse StaticData inside TCR-006: TCR-002 owns parsing and TCR-006 consumes only schemaVersion 2 output.
  - Treat equal numeric IDs or normalized names as automatic equivalence: cross-namespace identity requires reviewed resolver evidence.
  - Rename legacy titles to achievements or select quest files by fuzzy name: both violate source vocabulary and fail-closed quest ownership.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-tcr-006-content-reference-correlation.md
  - .github/workflows/tibia-client-reference.yml
  - tools/ai-agent/tibia_content_reference_correlation.py
  - tools/ai-agent/tibia_content_reference_correlation_tool.py
  - tools/ai-agent/test_tibia_content_reference_correlation.py
  - docs/ai-agent/TIBIA_CONTENT_REFERENCE_CORRELATION.md
  - docs/ai-agent/TIBIA_CONTENT_REFERENCE_CORRELATION.schema.json
  - docs/ai-agent/TIBIA_CONTENT_REFERENCE_RESOLVER.schema.json
  - docs/agents/MODULE_CATALOG.md
validation:
  - command: python -m unittest -v tools/ai-agent/test_tibia_content_reference_correlation.py
    result: PASS
    evidence: 20 fixture and exact-input tests passed locally.
  - command: python -m py_compile tools/ai-agent/tibia_content_reference_correlation.py tools/ai-agent/tibia_content_reference_correlation_tool.py tools/ai-agent/test_tibia_content_reference_correlation.py
    result: PASS
    evidence: local verified implementation payload.
  - command: Draft 2020-12 schema validation on exact resolver and correlation reports
    result: PASS
    evidence: resolver f1472c23; correlation 477c9ffa.
  - command: Tibia Client Reference workflow 30104916300
    result: PASS
    evidence: current-main catalogue artifact 8601260482 produced successfully.
  - command: Repository CI workflow 30104916625
    result: PASS
    evidence: completed successfully on live head 77c38568fe02b55798d0710318c4f82c8d1fd3d8.
  - command: Agent Task Ownership workflow 30104916248
    result: FAIL
    evidence: prior checkpoint serialized first_failure as null instead of required mapping; corrected in this checkpoint.
blockers: []
next_action: Rebuild the staged payload commit on the current checkpoint head from Git blob f0446001244d636ccc8745a821b67cedc5fb9577, attach it to PR 880, and run the existing materialization helper to produce the six verified implementation files.
```
