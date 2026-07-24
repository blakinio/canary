---
task_id: CAN-20260724-tcr-007-proficiency-reference-correlation
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: completed
agent: "GPT-5.6 Thinking"
branch: feat/tcr-007-proficiency-reference-correlation
base_branch: main
created: 2026-07-24T21:25:00+02:00
updated: 2026-07-24T21:31:25Z
last_verified_commit: "89acb51d3f3c3b4d6de5c7c8a4557b2d931f88ed"
risk: medium
related_issue: ""
related_pr: 898
depends_on:
  - TCR-001 merged stable canary-tibia-client-reference-manifest-v1
  - TCR-004 merged stable canary-tibia-proficiency-index-v1
blocks:
  - TCR-010
  - TCR-011
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-tcr-007-proficiency-reference-correlation.md
    - tools/ai-agent/tibia_proficiency_reference_common.py
    - tools/ai-agent/tibia_proficiency_reference_inventory.py
    - tools/ai-agent/tibia_proficiency_reference_resolver.py
    - tools/ai-agent/tibia_proficiency_reference_correlation.py
    - tools/ai-agent/tibia_proficiency_reference_correlation_tool.py
    - tools/ai-agent/tibia_proficiency_reference_test_support.py
    - tools/ai-agent/test_tibia_proficiency_reference_correlation.py
    - tools/ai-agent/test_tibia_proficiency_reference_inventory.py
    - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_CORRELATION.md
    - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_CORRELATION.schema.json
    - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_RESOLVER.schema.json
  shared:
    - .github/workflows/tibia-client-reference.yml
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - tools/ai-agent/tibia_proficiency_reference_index.py
    - tools/ai-agent/otbm_appearances.py
    - tools/ai-agent/otbm_asset_compatibility.py
    - tools/ai-agent/weapon_proficiency_forbidden_build_validation.py
    - src/items/items.cpp
    - src/creatures/players/components/weapon_proficiency.cpp
    - data/items/proficiencies.json
    - data/items/items.xml
    - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX.md
    - docs/ai-agent/OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md
    - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
modules_touched:
  - OTBM Tibia client reference architecture
  - proficiency reference correlation
reuses:
  - canary-tibia-client-reference-manifest-v1
  - canary-tibia-proficiency-index-v1
  - canary-appearances-index-v1
  - existing Weapon Proficiency runtime and persistence evidence
  - existing Weapon Proficiency achievement audit evidence
public_interfaces:
  - canary-tibia-proficiency-reference-resolver-v1
  - canary-tibia-proficiency-reference-correlation-v1
cross_repo_tasks: []
completed: 2026-07-24T21:31:25Z
---

# Goal

Implement the bounded, deterministic, read-only TCR-007 proficiency reference correlation consumer. Correlate exact TCR-004 proficiency definitions with canonical appearance object/proficiency bindings and explicitly selected Canary definition/runtime evidence through provenance-pinned reviewed resolver records. Preserve definition, appearance binding, item binding, runtime, persistence, protocol/client, automated behavior and Physical E2E as separate evidence dimensions.

# Acceptance criteria

- Consume only stable TCR-001/TCR-004 evidence and the canonical `canary-appearances-index-v1`; never reparse the user-supplied proficiency source or add another appearance parser.
- Require exact SHA-256 provenance and explicit reviewed mappings for `client-reference.proficiency-id`, `appearance.proficiency-id`, `appearance.object-id` and `canary.item-id` joins.
- Reuse the proven Canary loader relation where appearance object IDs populate `ItemType.id` and appearance proficiency flags populate `ItemType.proficiencyId` only when the loaded proficiency definition exists.
- Keep client definition presence, appearance binding, Canary item binding, definition semantics, runtime support, persistence, protocol/client, automated behavior and Physical E2E independent.
- Matching numeric IDs are candidate evidence only unless the resolver records reviewed equivalence and exact support.
- Duplicate, stale, ambiguous, conflicting, missing and many-to-one mappings fail closed or remain explicit findings.
- Do not write `items.xml`, `proficiencies.json`, appearances, datapack/runtime/protocol/client files or claim gameplay parity.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T21:31:25Z
head: 89acb51d3f3c3b4d6de5c7c8a4557b2d931f88ed
feature_head: b4c6240c05a0b5e0e52a7f2c6de501ba5bbe0144
branch: feat/tcr-007-proficiency-reference-correlation
pr: 898
status: ready
context_routes:
  - agent-governance
  - real-tibia-parity
  - cpp-runtime
owned_paths:
  - .github/workflows/tibia-client-reference.yml
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260724-tcr-007-proficiency-reference-correlation.md
  - tools/ai-agent/tibia_proficiency_reference_common.py
  - tools/ai-agent/tibia_proficiency_reference_inventory.py
  - tools/ai-agent/tibia_proficiency_reference_resolver.py
  - tools/ai-agent/tibia_proficiency_reference_correlation.py
  - tools/ai-agent/tibia_proficiency_reference_correlation_tool.py
  - tools/ai-agent/tibia_proficiency_reference_test_support.py
  - tools/ai-agent/test_tibia_proficiency_reference_correlation.py
  - tools/ai-agent/test_tibia_proficiency_reference_inventory.py
  - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_CORRELATION.md
  - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_CORRELATION.schema.json
  - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_RESOLVER.schema.json
proven:
  - PR 898 squash-merged into blakinio/canary main as 89acb51d3f3c3b4d6de5c7c8a4557b2d931f88ed at 2026-07-24T21:31:25Z; feature head was b4c6240c05a0b5e0e52a7f2c6de501ba5bbe0144.
  - The stable public contracts are canary-tibia-proficiency-reference-resolver-v1 and canary-tibia-proficiency-reference-correlation-v1; the compact intermediate owner evidence is canary-tcr007-canary-evidence-v1.
  - Materialized-source validation run 30125619953 passed 16 focused tests, bytecode compilation, both JSON schemas, CLI construction and byte-identical repeated Canary inventory generation.
  - Permanent Tibia Client Reference run 30126848538 passed all existing reference suites plus both TCR-007 suites, compilation, schemas, CLI and deterministic inventory.
  - Agent Task Ownership run 30126848565, AI Agent Tools run 30126848547 and repository pre-ready CI run 30126848662 passed on feature head b4c6240c05a0b5e0e52a7f2c6de501ba5bbe0144.
  - Protected final-gate CI run 30127006507 passed Fast Checks, Lua, Linux release/debug, Windows CMake/Solution, Docker and Required on the unchanged feature head.
  - Final PR diff contained exactly 14 durable paths; temporary payload, diagnostics and helper workflows were absent.
  - The resolver requires exact input hashes, unique reviewed mappings and loader-backed object/item bindings; numeric equality alone never closes a namespace join.
  - Correlation output preserves definition, appearance, item, runtime, persistence, protocol/client, automated behavior and Physical E2E as separate evidence dimensions.
derived:
  - TCR-007 is stable/merged within its exact read-only provenance and reviewed identifier-resolution boundaries.
  - Static agreement does not prove perk execution, persistence correctness, protocol/UI behavior, automated behavior, Physical E2E or gameplay parity.
unknown:
  - A future concrete client snapshot still determines the exact count and uniqueness of appearance proficiency bindings for that evidence set.
  - Optional runtime, protocol/client, automated behavior and Physical E2E evidence remain separately selected subsystem-owned inputs.
conflicts: []
first_failure:
  marker: resolved-staged-payload-transport
  evidence: Early materialization runs failed closed before extraction; exact Git blobs were then materialized directly and the normal source tree passed the complete validation chain.
rejected_hypotheses:
  - Build a second appearance parser: canonical canary-appearances-index-v1 already preserves object IDs and proficiency flags.
  - Treat numeric proficiency equality as automatic equivalence: architecture requires explicit resolver evidence.
  - Parse items.xml as the general proficiency binding authority: current proficiency bindings originate from protobuf appearance flags; items.xml is not the general binding owner.
  - Treat static correlation as runtime or gameplay proof: those dimensions remain separately owned and evidence-gated.
changed_paths:
  - .github/workflows/tibia-client-reference.yml
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260724-tcr-007-proficiency-reference-correlation.md
  - tools/ai-agent/tibia_proficiency_reference_common.py
  - tools/ai-agent/tibia_proficiency_reference_inventory.py
  - tools/ai-agent/tibia_proficiency_reference_resolver.py
  - tools/ai-agent/tibia_proficiency_reference_correlation.py
  - tools/ai-agent/tibia_proficiency_reference_correlation_tool.py
  - tools/ai-agent/tibia_proficiency_reference_test_support.py
  - tools/ai-agent/test_tibia_proficiency_reference_correlation.py
  - tools/ai-agent/test_tibia_proficiency_reference_inventory.py
  - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_CORRELATION.md
  - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_CORRELATION.schema.json
  - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_RESOLVER.schema.json
validation:
  - command: python -m unittest discover -s tools/ai-agent -p "test_tibia_proficiency_reference_*.py" -v
    result: PASS
    evidence: 16 focused tests passed in run 30125619953 and the permanent workflow run 30126848538.
  - command: Python bytecode, schema syntax, CLI construction and deterministic repeated inventory
    result: PASS
    evidence: passed in runs 30125619953 and 30126848538.
  - command: Agent Task Ownership / AI Agent Tools / repository CI / protected Required
    result: PASS
    evidence: runs 30126848565, 30126848547, 30126848662 and 30127006507 succeeded on final feature head b4c6240c05a0b5e0e52a7f2c6de501ba5bbe0144.
blockers: []
next_action: No further action in TCR-007; select a later package only through a fresh evidence and ownership preflight.
```

## Automated lifecycle completion

- Feature PR: #898.
- Feature head: `b4c6240c05a0b5e0e52a7f2c6de501ba5bbe0144`.
- Merge commit: `89acb51d3f3c3b4d6de5c7c8a4557b2d931f88ed`.
- Merged at: `2026-07-24T21:31:25Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle closeout.
