---
task_id: CAN-20260724-tcr-004-proficiency-reference-index
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/tcr-004-proficiency-reference-index
base_branch: main
created: 2026-07-24T09:15:00+02:00
updated: 2026-07-24T09:25:00+02:00
last_verified_commit: "dc4720ad43ddd098a8ab88d9cf30fa7fae841dc4"
risk: medium
related_issue: ""
related_pr: 858
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
updated_at: 2026-07-24T09:25:00+02:00
head: dc4720ad43ddd098a8ab88d9cf30fa7fae841dc4
branch: feat/tcr-004-proficiency-reference-index
pr: 858
status: validating
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
  - Current implementation base is main 734351a48249d51df7d740521c34b4d563a92c5c and PR 858 is the sole TCR-004 owner.
  - The supplied file proficiencies-1a915dffd9265cd1c18d39e55da7ede691b2e58add534bc186238ae028a73f22.json remains outside Git, is 462453 bytes and has SHA-256 1a915dffd9265cd1c18d39e55da7ede691b2e58add534bc186238ae028a73f22.
  - The supplied file is byte-identical to current data/items/proficiencies.json with Git blob SHA 49ec7edc6dacdee4a055fc0f3a9544f15eafabdd.
  - The supplied file contains 420 unique proficiency IDs, 2052 ordered levels and 3287 ordered perks with zero XpRequired records.
  - The pinned read-only research source beats-dh/Beats-Assets-Editor@ed827be34c279d1279ad3dde3af434b148ac05c7 confirms optional XpRequired and the reviewed perk fields.
  - Current WeaponProficiency runtime loading consumes IDs, levels and perks but drops Name and Version and silently overwrites duplicate IDs, so it is not the planned manifest-bound deterministic reference index.
  - The producer, CLI, schema, documentation, focused tests and dedicated workflow integration are implemented on PR 858.
  - Fixture-only validation passed 15 tests with one opt-in real-file test skipped; exact real-file validation passed all 15 tests.
  - Real-file output has 420 definitions, 2052 levels, 3287 perks, zero duplicate IDs, zero duplicate names and zero XpRequired records.
  - Python bytecode compilation, JSON schema syntax, representative Draft 2020-12 validation and CLI construction passed locally.
  - Tibia Client Reference and repository CI passed on head dc4720ad43ddd098a8ab88d9cf30fa7fae841dc4.
derived:
  - TCR-004 remains a distinct definition-only evidence producer even though the selected external bytes currently equal the Canary runtime JSON.
  - Appearance and runtime correlation belong to TCR-007 and must not be folded into this producer.
unknown:
  - Exact client build identity remains unknown unless separately proven by the stable manifest.
  - Whether later client proficiency files introduce fields beyond the independently reviewed JSON shape.
conflicts: []
first_failure:
  marker: Agent Task Ownership changed-task checkpoint validation on dc4720ad43ddd098a8ab88d9cf30fa7fae841dc4
  evidence: related_pr was empty after draft PR 858 existed; implementation and dedicated workflow checks were already green
rejected_hypotheses:
  - Reuse WeaponProficiency::loadFromJson as the TCR-004 index: it is runtime registration, not manifest-bound reference evidence, and does not retain the complete source contract.
  - Reparse appearances in TCR-004: the canonical appearance index already preserves proficiency IDs and TCR-007 owns correlation.
changed_paths:
  - .github/workflows/tibia-client-reference.yml
  - docs/agents/tasks/active/CAN-20260724-tcr-004-proficiency-reference-index.md
  - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX.md
  - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX.schema.json
  - tools/ai-agent/test_tibia_proficiency_reference_index.py
  - tools/ai-agent/tibia_proficiency_reference_index.py
  - tools/ai-agent/tibia_proficiency_reference_index_tool.py
validation:
  - command: python -m unittest discover -s tools/ai-agent -p test_tibia_proficiency_reference_index.py -v
    result: PASS
    evidence: 15 passed; 1 opt-in test skipped
  - command: CANARY_TIBIA_PROFICIENCY_FILE=<external-file> python -m unittest discover -s tools/ai-agent -p test_tibia_proficiency_reference_index.py -v
    result: PASS
    evidence: 15 passed; exact source SHA-256 1a915dffd9265cd1c18d39e55da7ede691b2e58add534bc186238ae028a73f22
  - command: python -m py_compile tools/ai-agent/tibia_proficiency_reference_index.py tools/ai-agent/tibia_proficiency_reference_index_tool.py tools/ai-agent/test_tibia_proficiency_reference_index.py
    result: PASS
    evidence: local Python compilation completed without output
  - command: python -m json.tool docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX.schema.json
    result: PASS
    evidence: schema syntax valid and representative real-file payload validates under Draft 2020-12
  - command: python tools/ai-agent/tibia_proficiency_reference_index_tool.py --help
    result: PASS
    evidence: CLI construction completed without output
  - command: GitHub Tibia Client Reference workflow on dc4720ad43ddd098a8ab88d9cf30fa7fae841dc4
    result: PASS
    evidence: run 30074698335
  - command: GitHub CI workflow on dc4720ad43ddd098a8ab88d9cf30fa7fae841dc4
    result: PASS
    evidence: run 30074698446
blockers: []
next_action: Register canary-tibia-proficiency-index-v1 in MODULE_CATALOG, verify all checks on the resulting exact head, then apply ci:final-gate and merge PR 858 if green.
```
