---
task_id: CAN-20260724-tcr-006-content-reference-correlation
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/tcr-006-content-reference-correlation
base_branch: main
created: 2026-07-24T17:00:00+02:00
updated: 2026-07-24T17:05:00+02:00
last_verified_commit: "7872bcede1712a2ed9e4874326741477000634f4"
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
updated_at: 2026-07-24T17:05:00+02:00
head: 7872bcede1712a2ed9e4874326741477000634f4
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
  - TCR-005 lifecycle PR 874 merged as ced1c2f449d7c20f30cc236f8d6641f311c0a9e8 and advances the programme to TCR-006.
  - No open TCR-006 PR or branch and no existing canary-tibia-content-reference-correlation-v1 contract were found in the fresh preflight.
  - Draft PR 880 is the sole current TCR-006 owner.
  - StaticData schemaVersion 2 preserves legacy creatures/titles and newer monsters/monsterClasses/achievements as different source categories.
  - The exact outside-Git StaticData input is legacy with 812 creatures, 356 titles, 438 bosses, 99 quests and zero duplicate/missing-field findings.
  - Achievement Validation owns stable Canary achievement IDs/names and static handler/persistence evidence through canary-achievement-audit-v2.
  - Cyclopedia Validation owns Bestiary/Bosstiary technical ID and active monster-definition evidence.
  - OTBM Spawn/Boss/NPC Validator owns selected active-datapack definition/spawn evidence and name-based definition resolution.
  - Quest Map Validator owns explicit selected quest-source AID/UID/item/position/storage evidence and does not expose a shared client quest-ID namespace.
  - Quest/storage progression and reachability remain owned by Storage Dependency Graph and Quest State Reachability.
derived:
  - Each category needs its own target namespace and reviewed mapping policy; one universal numeric-ID equality rule would be unsound.
  - Legacy titles may be correlated to achievement-owner evidence only as source titles; they must not be renamed achievements in the source layer.
  - Quest name agreement can produce a review candidate but cannot automatically bind source globs, storage paths or map mechanics.
unknown:
  - Exact equivalence between client creature IDs and Canary Bestiary race IDs.
  - Exact equivalence between client boss IDs and Canary Bosstiary IDs.
  - Exact equivalence between legacy title IDs and Canary achievement IDs.
  - Reviewed client quest-ID to selected Canary quest-source mappings.
conflicts: []
first_failure: null
rejected_hypotheses:
  - Reparse StaticData inside TCR-006: forbidden because TCR-002 owns parsing.
  - Treat all equal numeric IDs as equivalent: unproven across namespaces.
  - Rename legacy titles to achievements: violates source-family vocabulary.
  - Select quest files by fuzzy name matching: unsupported and unsafe.
  - Build second achievement, Cyclopedia, spawn/boss or quest validator: duplicates existing owners.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-tcr-006-content-reference-correlation.md
validation:
  - command: fresh open-PR and branch ownership search
    result: PASS
    evidence: no prior TCR-006 owner or equivalent contract found; draft PR 880 now owns the package
blockers: []
next_action: Generate compact exact owner inventories for Achievement, Bestiary/Bosstiary, Spawn/Boss definitions and quest evidence boundaries before selecting reviewed resolver methods.
```
