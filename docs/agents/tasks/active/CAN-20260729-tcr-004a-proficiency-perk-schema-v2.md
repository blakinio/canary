---
task_id: CAN-20260729-tcr-004a-proficiency-perk-schema-v2
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: TCR-004A-PROFICIENCY-PERK-SCHEMA-V2
status: ready
agent: chatgpt
branch: fix/CAN-20260729-tcr-004a-proficiency-perk-schema-v2
base_branch: main
created: 2026-07-29T21:20:00+02:00
updated: 2026-07-29T22:25:00+02:00
last_verified_commit: "7d12562bf33e57c84f7803938209c1fa96a720c3"
risk: medium
related_issue: ""
related_pr: "1014"
depends_on: []
blocks:
  - CAN-20260729-tcr-009-client-reference-drift
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260729-tcr-004a-proficiency-perk-schema-v2.md
    - tools/ai-agent/tibia_proficiency_reference_index.py
    - tools/ai-agent/test_tibia_proficiency_reference_index_schema_v2.py
  shared:
    - tools/ai-agent/tibia_proficiency_reference_resolver.py
    - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX_SCHEMA_V2.md
    - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX_V2.schema.json
    - .github/workflows/tibia-proficiency-schema-v2.yml
  read_only:
    - exact user-supplied official-client packages outside Git
    - owner-retained generated TCR reports outside Git
modules_touched:
  - Tibia client-reference proficiency index
  - Tibia proficiency reference correlation
reuses:
  - canary-tibia-proficiency-index-v1
  - TCR-007 proficiency reference validator
public_interfaces:
  - canary-tibia-proficiency-index-v1 schemaVersion 2
cross_repo_tasks: []
---

# Goal

Extend the existing TCR-004 producer for the reviewed proficiency perk shape present in exact client snapshot `15.31.69f220` without inventing a missing `Value`, weakening unknown-field rejection, reparsing appearances, duplicating the resolver, or changing gameplay/runtime state.

# Acceptance criteria

- [x] Preserve legacy `Value` perks.
- [x] Preserve reviewed `MissileId`, `Multiplier`, and `Probability` fields.
- [x] Represent source perks that omit `Value` without synthesizing one.
- [x] Require `Type` and at least one finite numeric effect field.
- [x] Publish explicit schemaVersion 2 while keeping the format name stable.
- [x] Keep the single TCR-007 resolver compatible with exact schema versions 1 and 2.
- [x] Add malformed, determinism, schema and exact external-file tests.
- [x] Prove complete A/B snapshot generation outside Git.
- [ ] Pass exact final-head CI, merge, regenerate retained reports using the merge revision, and archive.

# Confirmed evidence

- Snapshot A proficiency SHA-256: `1a915dffd9265cd1c18d39e55da7ede691b2e58add534bc186238ae028a73f22`.
- Snapshot B proficiency SHA-256: `97e59f4c247c6a64884ecbbfcceb2ba6dbad82f4fe52749f035b6b3d01c84ee1`.
- Snapshot B contains 443 definitions, 2211 levels, 3671 perks and 22 reviewed `Type=32` perks with `ElementId`, `MissileId`, `Multiplier`, and `Probability`, without `Value`.
- Complete pre-merge A/B manifests and all three index families were generated and hash-closed outside Git.
- StaticData changes from `legacy` in A to `newer` in B; this is an explicit TCR-009 drift family, not malformed evidence.

# Decisions

| Decision | Reason |
|---|---|
| Use schemaVersion 2 | Optional `value` is a material schema change. |
| Do not synthesize `value` | The exact source omits it. |
| Keep one resolver | Parallel copied resolver semantics are forbidden. |
| Accept only schema 1 and 2 in TCR-007 | Historical evidence remains usable; future versions fail closed. |
| Reconcile shared programme/catalogue/changelog in TCR-009 | Their final state depends on merged parser revision and final retained hashes. |

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T22:25:00+02:00
head: 7d12562bf33e57c84f7803938209c1fa96a720c3
branch: fix/CAN-20260729-tcr-004a-proficiency-perk-schema-v2
pr: 1014
status: ready
context_routes:
  - agent-governance
  - real-tibia-parity
  - otbm
owned_paths:
  - tools/ai-agent/tibia_proficiency_reference_index.py
  - tools/ai-agent/test_tibia_proficiency_reference_index_schema_v2.py
  - tools/ai-agent/tibia_proficiency_reference_resolver.py
  - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX_SCHEMA_V2.md
  - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX_V2.schema.json
  - .github/workflows/tibia-proficiency-schema-v2.yml
proven:
  - Schema 2 preserves exact reviewed fields and never synthesizes Value.
  - The single TCR-007 resolver accepts schema versions 1 and 2 and rejects future versions.
  - Exact snapshot B tests passed with 443 definitions and 22 reviewed no-Value projectile perks.
  - Complete pre-merge A/B manifest and index generation passed outside Git.
  - Workflows 30487311955, 30487311984, 30487312006, 30487311966 and 30487312101 passed on 92d497115333608349dface60abf7f03b34dd8b8.
derived:
  - Final retained snapshot hashes must use the eventual merge revision.
unknown:
  - Exact final checkpoint-fix commit SHA and its final-gate workflow results.
conflicts: []
first_failure:
  marker: FINAL_GATE_CHECKPOINT_STATUS_ENUM
  evidence: Workflow 30487681879 rejected unsupported checkpoint status final-gate; repository enum requires ready.
rejected_hypotheses:
  - Ignore unknown fields.
  - Synthesize Value from Multiplier or Probability.
  - Keep a copied legacy resolver.
changed_paths:
  - .github/workflows/tibia-proficiency-schema-v2.yml
  - docs/agents/tasks/active/CAN-20260729-tcr-004a-proficiency-perk-schema-v2.md
  - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX_SCHEMA_V2.md
  - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX_V2.schema.json
  - tools/ai-agent/test_tibia_proficiency_reference_index_schema_v2.py
  - tools/ai-agent/tibia_proficiency_reference_index.py
  - tools/ai-agent/tibia_proficiency_reference_resolver.py
validation:
  - command: exact external-file schema-v2 unit suite
    result: PASS
    evidence: Five tests passed; 443 definitions, 2211 levels, 3671 perks and 22 reviewed Type 32 no-Value perks.
  - command: pre-merge exact A/B snapshot generation
    result: PASS
    evidence: Both manifests and all six index reports generated and hash-closed outside Git.
  - command: final-gate workflow set on 7d12562bf33e57c84f7803938209c1fa96a720c3
    result: FAIL
    evidence: Only Agent Task Ownership failed because final-gate is not a supported checkpoint status; changed to ready in this commit.
blockers: []
next_action: verify all forced final-gate workflows on this checkpoint-fix commit, inspect reviews, mark PR ready, and squash-merge the exact green head.
```
