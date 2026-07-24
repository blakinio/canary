---
task_id: CAN-20260724-tcr-006-content-reference-correlation
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/tcr-006-content-reference-correlation
base_branch: main
created: 2026-07-24T17:00:00+02:00
updated: 2026-07-24T18:15:59+02:00
last_verified_commit: "fcb8edf1be084511b4e4926808009b54884b597a"
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
updated_at: 2026-07-24T18:15:59+02:00
head: fcb8edf1be084511b4e4926808009b54884b597a
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
  - PR 880 remains the sole open TCR-006 owner; it is draft, mergeable and targets blakinio/canary main from feat/tcr-006-content-reference-correlation.
  - Exact legacy StaticData inventory contains 812 creatures, 356 titles, 438 bosses and 99 quests with no duplicate or missing required-field findings.
  - Owner inventory workflow 30103563037 succeeded and published artifact 8600662164 with digest sha256:041b0d357e6e5df4ecfeb186aa4611d58ecbe3533a6e7a47ae9f32b64bc53f4a.
  - Reviewed resolver candidates retain 739 creature, 236 boss and 349 title identity mappings; shared target IDs and all quest joins remain unresolved.
  - Exact correlation contains 1705 source rows with 1324 confirmed-reference, 119 partial, 160 reference-only, 102 unresolved-id-space and zero conflicts.
  - Exact resolver SHA-256 is f1472c23 and exact correlation SHA-256 is 477c9ffa; full reports remain outside Git.
  - Verified payload blob f0446001244d636ccc8745a821b67cedc5fb9577 was rebuilt on the live branch and materialized without byte changes into the six implementation files.
  - Materialization workflow 30107920417 passed all extraction, 20 focused-test, bytecode, schema-syntax, diff and commit steps and produced implementation commit 5a37f276bed62cadadb0c039b80536ed69a2acbb.
  - Finalization workflow 30108347547 passed focused tests, bytecode, schema syntax and CLI construction, added the module catalogue entry and removed all temporary staging paths.
  - Live implementation head fcb8edf1be084511b4e4926808009b54884b597a contains exactly the task, six implementation/docs/schema files, final Tibia Client Reference workflow and module catalogue entry; no staged ZIP or diagnostic file remains in the PR diff.
  - Tibia Client Reference workflow 30108460292 passed on fcb8edf1be084511b4e4926808009b54884b597a.
  - Repository CI workflow 30108460520 passed on fcb8edf1be084511b4e4926808009b54884b597a.
  - Agent Task Ownership workflow 30108460223 passed on fcb8edf1be084511b4e4926808009b54884b597a.
  - AI Agent Tools workflow 30108460221 job 89531656374 passed all unit, index-generation, reference-validation, schema, realistic-content-pack and artifact steps on fcb8edf1be084511b4e4926808009b54884b597a.
derived:
  - The implementation acceptance surface is complete; only the final task-checkpoint head validation and PR lifecycle action remain.
  - Static correlation evidence does not prove runtime or gameplay parity and does not authorize source, datapack or map mutation.
unknown:
  - Exact workflow conclusions on the task-checkpoint commit created after fcb8edf1be084511b4e4926808009b54884b597a.
  - Final squash-merge commit SHA.
conflicts: []
first_failure:
  marker: Agent Task Ownership run 30104916248 / Validate changed active task checkpoints
  evidence: CHANGED_TASK_VALIDATION.txt reports first_failure must be a YAML mapping because the prior checkpoint used first_failure null.
rejected_hypotheses:
  - Reparse StaticData inside TCR-006: TCR-002 owns parsing and TCR-006 consumes only schemaVersion 2 output.
  - Treat equal numeric IDs or normalized names as automatic equivalence: cross-namespace identity requires reviewed resolver evidence.
  - Rename legacy titles to achievements or select quest files by fuzzy name: both violate source vocabulary and fail-closed quest ownership.
  - Treat the first materialization failure as an implementation defect: run 30107352531 failed because the helper omitted tools/ai-agent from PYTHONPATH; the identical payload passed after the helper environment was corrected.
  - Push the final workflow rewrite from GITHUB_TOKEN: workflow-file mutation was separated from bot-authored catalogue/staging cleanup and applied through the authorized GitHub connector.
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
  - command: python -m unittest discover -s tools/ai-agent -p "test_tibia_content_reference_correlation.py" -v
    result: PASS
    evidence: 20 fixture and exact-input tests passed in materialization run 30107920417 and finalization run 30108347547.
  - command: python -m py_compile tools/ai-agent/tibia_content_reference_correlation.py tools/ai-agent/tibia_content_reference_correlation_tool.py tools/ai-agent/test_tibia_content_reference_correlation.py
    result: PASS
    evidence: passed in materialization run 30107920417 and finalization run 30108347547.
  - command: Draft 2020-12 schema validation on exact resolver and correlation reports
    result: PASS
    evidence: resolver f1472c23; correlation 477c9ffa.
  - command: Tibia Client Reference workflow 30108460292
    result: PASS
    evidence: completed successfully on fcb8edf1be084511b4e4926808009b54884b597a.
  - command: Repository CI workflow 30108460520
    result: PASS
    evidence: completed successfully on fcb8edf1be084511b4e4926808009b54884b597a.
  - command: Agent Task Ownership workflow 30108460223
    result: PASS
    evidence: completed successfully on fcb8edf1be084511b4e4926808009b54884b597a.
  - command: AI Agent Tools workflow 30108460221 / job 89531656374
    result: PASS
    evidence: all unit and generated-content validation steps completed successfully on fcb8edf1be084511b4e4926808009b54884b597a.
blockers: []
next_action: Verify the ci:final-gate workflows on the task-checkpoint commit, then mark PR 880 ready and squash-merge it if all required checks remain green.
```
