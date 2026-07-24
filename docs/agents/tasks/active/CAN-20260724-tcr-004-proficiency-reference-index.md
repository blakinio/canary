---
task_id: CAN-20260724-tcr-004-proficiency-reference-index
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/tcr-004-proficiency-reference-index
base_branch: main
created: 2026-07-24T09:15:00+02:00
updated: 2026-07-24T09:15:00+02:00
last_verified_commit: "734351a48249d51df7d740521c34b4d563a92c5c"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - TCR-001 merged stable canary-tibia-client-reference-manifest-v1
  - TCR-003 lifecycle closure merged as 734351a48249d51df7d740521c34b4d563a92c5c
blocks:
  - TCR-007
  - TCR-009
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-tcr-004-proficiency-reference-index.md
    - tools/ai-agent/tibia_proficiency_reference_index.py
    - tools/ai-agent/tibia_proficiency_reference_index_tool.py
    - tools/ai-agent/test_tibia_proficiency_reference_index.py
    - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX.md
    - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX.schema.json
  shared:
    - .github/workflows/tibia-client-reference.yml
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - data/items/proficiencies.json
    - src/creatures/players/components/weapon_proficiency.cpp
    - tools/ai-agent/weapon_proficiency_achievement_audit.py
    - tools/ai-agent/otbm_appearances.py
    - tools/ai-agent/tibia_client_reference_manifest.py
    - tools/ai-agent/tibia_staticmapdata_reference_index.py
    - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
    - docs/ai-agent/OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md
modules_touched:
  - OTBM Tibia client reference architecture
  - official-client proficiency reference evidence
reuses:
  - canary-tibia-client-reference-manifest-v1 exact provenance contract
  - TCR-003 stable-file, bounded-compression and deterministic-output safety patterns
  - canary-appearances-index-v1 as the future appearance-correlation authority, not reparsed here
public_interfaces:
  - canary-tibia-proficiency-index-v1
cross_repo_tasks: []
---

# Goal

Implement the bounded, read-only `canary-tibia-proficiency-index-v1` producer for one explicit manifest-bound proficiency JSON file. Preserve definition IDs, names, optional versions, ordered levels, optional `XpRequired` values and ordered perk records deterministically while keeping client definitions separate from appearance, Canary runtime, persistence, protocol and gameplay proof.

# Acceptance criteria

- Exact manifest and source provenance, byte size and SHA-256 are retained.
- `ProficiencyId`, `Name`, optional `Version`, ordered levels, optional `XpRequired` and all reviewed perk fields are preserved deterministically.
- Duplicate proficiency IDs are explicit findings rather than silently overwritten.
- Malformed JSON, duplicate JSON object keys, unsupported fields, invalid numeric values and configured bounds fail closed.
- The identifier namespace is explicitly `client-reference.proficiency-id`.
- No appearance file is reparsed; any future appearance join must reuse `canary-appearances-index-v1` in TCR-007.
- No `items.xml` write behavior, runtime mutation, protocol claim, gameplay conclusion or proprietary source file is added.
- Focused unit tests, Python bytecode compilation, JSON schema validation, CLI construction and the dedicated client-reference workflow pass on the final head.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T09:15:00+02:00
head: 734351a48249d51df7d740521c34b4d563a92c5c
branch: feat/tcr-004-proficiency-reference-index
pr: none
status: investigating
context_routes:
  - agent-governance
  - otbm
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-tcr-004-proficiency-reference-index.md
  - tools/ai-agent/tibia_proficiency_reference_index.py
  - tools/ai-agent/tibia_proficiency_reference_index_tool.py
  - tools/ai-agent/test_tibia_proficiency_reference_index.py
  - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX.md
  - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX.schema.json
  - .github/workflows/tibia-client-reference.yml
  - docs/agents/MODULE_CATALOG.md
proven:
  - Current main is 734351a48249d51df7d740521c34b4d563a92c5c and marks TCR-004 as the next candidate after a fresh preflight.
  - No open PR or branch owns TCR-004 or canary-tibia-proficiency-index-v1.
  - The supplied file proficiencies-1a915dffd9265cd1c18d39e55da7ede691b2e58add534bc186238ae028a73f22.json remains outside Git, is 462453 bytes and has the SHA-256 embedded in its filename.
  - The supplied file is byte-identical to current data/items/proficiencies.json with Git blob SHA 49ec7edc6dacdee4a055fc0f3a9544f15eafabdd.
  - The supplied file contains 420 unique proficiency IDs, 2052 ordered levels and 3287 ordered perks with the reviewed field set.
  - The pinned read-only research source at beats-dh/Beats-Assets-Editor@ed827be34c279d1279ad3dde3af434b148ac05c7 confirms optional XpRequired and the reviewed perk fields.
  - Current WeaponProficiency runtime loading consumes IDs, levels and perks but drops Name and Version and silently overwrites duplicate IDs, so it is not the planned manifest-bound deterministic reference index.
derived:
  - TCR-004 remains a distinct definition-only evidence producer even though the selected external bytes currently equal the Canary runtime JSON.
  - Appearance and runtime correlation belong to TCR-007 and must not be folded into this producer.
unknown:
  - Exact client build identity remains unknown unless separately proven by the stable manifest.
  - Whether later client proficiency files introduce fields beyond the independently reviewed JSON shape.
conflicts: []
first_failure:
  marker: none
  evidence: no current blocker or failed validation; implementation has not started
rejected_hypotheses:
  - Reuse WeaponProficiency::loadFromJson as the TCR-004 index: it is runtime registration, not manifest-bound reference evidence, and does not retain the complete source contract.
  - Reparse appearances in TCR-004: the canonical appearance index already preserves proficiency IDs and TCR-007 owns correlation.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-tcr-004-proficiency-reference-index.md
validation:
  - command: GitHub open PR and branch search for TCR-004 ownership
    result: PASS
    evidence: no exact TCR-004 or canary-tibia-proficiency-index-v1 owner found
  - command: external-file inventory and JSON shape analysis
    result: PASS
    evidence: 420 records, 2052 levels, 3287 perks, zero duplicate IDs; exact SHA-256 1a915dffd9265cd1c18d39e55da7ede691b2e58add534bc186238ae028a73f22
blockers: []
next_action: Create the early draft PR, then implement and locally validate only the bounded canary-tibia-proficiency-index-v1 producer on the claimed paths.
```
