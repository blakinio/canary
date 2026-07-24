---
task_id: CAN-20260724-tcr-007-proficiency-reference-correlation
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: active
agent: "GPT-5.6 Thinking"
branch: feat/tcr-007-proficiency-reference-correlation
base_branch: main
created: 2026-07-24T21:25:00+02:00
updated: 2026-07-24T22:52:15+02:00
last_verified_commit: "0ee846353119ffa49413a4cd86df668389263fc3"
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
---

# Goal

Implement the bounded, deterministic, read-only TCR-007 proficiency reference correlation consumer. Correlate exact TCR-004 proficiency definitions with the canonical appearance object/proficiency bindings and explicitly selected Canary definition/runtime evidence through provenance-pinned reviewed resolver records. Preserve definition, appearance, item binding, runtime, persistence, protocol/client, automated behavior and Physical E2E as separate evidence dimensions.

# Acceptance criteria

- Consume only a stable TCR-001 manifest-bound `canary-tibia-proficiency-index-v1`; never reparse the user-supplied proficiency source.
- Consume only the canonical `canary-appearances-index-v1`; never add another appearance parser.
- Require exact SHA-256 provenance for every input report and explicit reviewed mappings for `client-reference.proficiency-id`, `appearance.proficiency-id`, `appearance.object-id` and `canary.item-id` joins.
- Reuse the proven Canary loader relation where appearance object IDs populate `ItemType.id` and appearance proficiency flags populate `ItemType.proficiencyId` only when the loaded proficiency definition exists.
- Keep client definition presence, appearance binding, Canary item binding, definition semantics, runtime support, persistence, protocol/client, automated behavior and Physical E2E as independent dimensions.
- Matching numeric IDs are candidate evidence only unless the resolver records the reviewed equivalence and exact supporting evidence.
- Duplicate, stale, ambiguous, conflicting, missing and many-to-one mappings fail closed or remain explicit findings.
- Emit deterministic states including `confirmed-reference`, `partial`, `reference-only`, `target-only`, `unresolved-id-space`, `conflicting` and `stale-evidence`.
- Do not write `items.xml`, `proficiencies.json`, appearances, datapack/runtime/protocol/client files or claim gameplay parity.
- Focused tests, schemas, bytecode compilation, dedicated workflow and repository final gate pass.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T22:52:15+02:00
head: 0ee846353119ffa49413a4cd86df668389263fc3
branch: feat/tcr-007-proficiency-reference-correlation
pr: 898
status: validating
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
  - Main at 93413bd53e9a40f0ff3c4f55986036b10be44e0f contains the merged TCR-006 lifecycle closure and selects TCR-007 as the next dependency-satisfied candidate.
  - No open PR, branch or repository implementation was found for TCR-007 or canary-tibia-proficiency-reference-correlation-v1 during the fresh preflight.
  - TCR-004 is stable/merged and its report preserves client-reference.proficiency-id as definition-only without asserting appearance or runtime equivalence.
  - The canonical canary-appearances-index-v1 exposes object appearance id and flags.proficiency.id without requiring a second parser.
  - Canary Items::loadFromProtobuf assigns appearance object.id to ItemType.id and assigns the appearance proficiency ID to ItemType.proficiencyId only when WeaponProficiency definitions already contain that ID.
  - WeaponProficiency loads data/items/proficiencies.json by ProficiencyId and persists per-player state under the weapon-proficiency KV scope keyed by weapon item ID.
  - TCR-004 exact development evidence contained 420 definitions, 2052 levels, 3287 perks and zero duplicate ID/name findings for source SHA-256 1a915dffd9265cd1c18d39e55da7ede691b2e58add534bc186238ae028a73f22.
  - Materialized source validation run 30125619953 passed 16 focused tests, bytecode compilation, both JSON schemas, CLI construction and byte-identical repeated Canary evidence inventory generation.
  - Temporary staged payload and helper workflow were removed before durable discovery finalization.
derived:
  - TCR-007 can reuse the canonical appearance object rows as factual item/proficiency binding candidates while still requiring a reviewed resolver before declaring cross-namespace equivalence.
  - Static agreement does not prove perk execution, persistence correctness, protocol/UI behavior, automated behavior or Physical E2E parity.
unknown:
  - Exact count and uniqueness of appearance proficiency bindings in the selected canonical appearance index used for TCR-007 validation.
  - Exact selected evidence format for optional runtime, persistence, protocol/client, automated behavior and Physical E2E dimensions.
conflicts: []
first_failure:
  marker: resolved-staged-payload-transport
  evidence: Early materialization runs failed closed before extraction; exact Git blobs were then materialized directly and run 30125619953 validated the normal source tree successfully.
rejected_hypotheses:
  - Build a second appearance parser: canonical canary-appearances-index-v1 already preserves object IDs and proficiency flags.
  - Treat numeric proficiency equality as automatic equivalence: architecture requires explicit resolver evidence.
  - Parse items.xml as the general proficiency binding authority: current proficiency bindings originate from protobuf appearance flags; items.xml is not the general binding owner.
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
  - command: Fresh ownership/reuse/implementation preflight
    result: PASS
    evidence: no TCR-007 owner/branch/implementation found; canonical TCR-004, appearance and runtime paths identified.
  - command: TCR-007 Validate Materialized Sources run 30125619953
    result: PASS
    evidence: 16 focused tests, bytecode compilation, schema syntax, CLI construction and deterministic repeated Canary inventory passed on implementation head 0ee846353119ffa49413a4cd86df668389263fc3.
blockers: []
next_action: Run exact-final-head ownership, Tibia Client Reference, AI Agent Tools and repository Required gates, then mark PR #898 ready and squash-merge when green.
```
