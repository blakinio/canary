---
task_id: CAN-20260729-tcr-004a-proficiency-perk-schema-v2
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: TCR-004A-PROFICIENCY-PERK-SCHEMA-V2
status: completed
agent: chatgpt
branch: fix/CAN-20260729-tcr-004a-proficiency-perk-schema-v2
base_branch: main
created: 2026-07-29T21:20:00+02:00
updated: 2026-07-29T22:43:28+02:00
last_verified_commit: "b68fbf7bf26b57f0cf716abffb52cfa951fa66ce"
risk: medium
related_issue: ""
related_pr: "1014"
depends_on: []
blocks:
  - CAN-20260729-tcr-009-client-reference-drift
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260729-tcr-004a-proficiency-perk-schema-v2.md
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
completed: 2026-07-29T22:43:28+02:00
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
- [x] Pass exact final-head CI, merge, regenerate retained reports using the merge revision, and archive.

# Completion evidence

- Feature PR: #1014.
- Feature head: `422b3c288f9083ff06d27769241483eff50a1e72`.
- Merge commit: `b68fbf7bf26b57f0cf716abffb52cfa951fa66ce`.
- Merged at: `2026-07-29T20:43:28Z`.
- Snapshot A final manifest SHA-256: `6096b021ca21d911165f89bfc714f558fc7efde0a455855caed071852ccfcee1`.
- Snapshot B final manifest SHA-256: `54646c3f71cc98c53049c63a49a331ec08acb71a37c551f5c592f55645be7e53`.
- Final retained evidence summary SHA-256: `6224a175fab73931627c1ea36545e4b5f1bc4c29068fa337049130ee777a3431`.
- Exact final drift smoke SHA-256: `be0593cb260cc717b2d8e9e1a19a565f958e85935fde4ac09ce8fb5bbb853b31`.

# Decisions

| Decision | Reason |
|---|---|
| Use schemaVersion 2 | Optional `value` is a material schema change. |
| Do not synthesize `value` | The exact source omits it. |
| Keep one resolver | Parallel copied resolver semantics are forbidden. |
| Accept only schema 1 and 2 in TCR-007 | Historical evidence remains usable; future versions fail closed. |
| Leave TCR-009 programme reconciliation to its own task | That lifecycle owns the stable drift contract and owner evidence consumption. |

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T22:43:28+02:00
head: 422b3c288f9083ff06d27769241483eff50a1e72
branch: fix/CAN-20260729-tcr-004a-proficiency-perk-schema-v2
pr: 1014
status: completed
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
  - All final-head workflow runs passed on 422b3c288f9083ff06d27769241483eff50a1e72, including the readiness-triggered CI run 30488072169.
  - PR 1014 squash-merged as b68fbf7bf26b57f0cf716abffb52cfa951fa66ce.
  - Final retained A/B manifests and all six index reports were regenerated with parser revision b68fbf7bf26b57f0cf716abffb52cfa951fa66ce and independently revalidated.
derived:
  - TCR-009 can now consume two complete exact retained snapshot sets.
unknown: []
conflicts: []
first_failure:
  marker: none
  evidence: The former unsupported reviewed projectile shape and checkpoint enum issue were corrected before merge; final-head checks and post-merge retained generation passed.
rejected_hypotheses:
  - Ignore unknown fields.
  - Synthesize Value from Multiplier or Probability.
  - Keep a copied legacy resolver.
changed_paths:
  - .github/workflows/tibia-proficiency-schema-v2.yml
  - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX_SCHEMA_V2.md
  - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX_V2.schema.json
  - tools/ai-agent/test_tibia_proficiency_reference_index_schema_v2.py
  - tools/ai-agent/tibia_proficiency_reference_index.py
  - tools/ai-agent/tibia_proficiency_reference_resolver.py
validation:
  - command: final-head GitHub workflow set
    result: PASS
    evidence: Agent Task Ownership, Tibia Client Reference, Tibia Proficiency Schema v2, AI Agent Tools, base CI, and readiness-triggered CI passed on 422b3c288f9083ff06d27769241483eff50a1e72.
  - command: CANARY_MERGE_REVISION=b68fbf7... generate_snapshots_final.py
    result: PASS
    evidence: Both final manifests and all six reports were generated and hash-closed outside Git.
  - command: independent retained binding verification
    result: PASS
    evidence: Archive payload hashes, selected input sizes, report source bindings, bootstrap manifest hashes, and generated-index closure all matched.
  - command: exact retained TCR-009 drift test suite
    result: PASS
    evidence: 7 of 7 tests passed against final retained snapshot roots.
blockers: []
next_action: Fulfil RTREQ-TCR-ITEM-DEFINITIONS-0002 through the official owner-request lifecycle, then activate TCR-009.
```

## Automated lifecycle completion

This record was moved from `tasks/active` to `tasks/archive` after the feature PR merged and final retained report generation completed.
