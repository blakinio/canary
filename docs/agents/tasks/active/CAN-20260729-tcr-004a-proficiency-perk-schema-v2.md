---
task_id: CAN-20260729-tcr-004a-proficiency-perk-schema-v2
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: TCR-004A-PROFICIENCY-PERK-SCHEMA-V2
status: final-gate
agent: chatgpt
branch: fix/CAN-20260729-tcr-004a-proficiency-perk-schema-v2
base_branch: main
created: 2026-07-29T21:20:00+02:00
updated: 2026-07-29T22:20:00+02:00
last_verified_commit: "92d497115333608349dface60abf7f03b34dd8b8"
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
- [x] Publish an explicit schemaVersion 2 contract while keeping the format name stable.
- [x] Keep the single existing TCR-007 resolver able to consume exact schemaVersion 1 and 2 indexes.
- [x] Add focused malformed, determinism, schema and real external-file tests.
- [x] Prove both complete TCR-009 snapshot sets can be generated with this producer outside Git.
- [ ] Pass exact final-head CI, merge, regenerate retained reports with the merge revision, and archive the lifecycle.

# Confirmed context

- Draft PR #1014 targets `blakinio/canary:main` from the dedicated branch.
- Snapshot A proficiency SHA-256 is `1a915dffd9265cd1c18d39e55da7ede691b2e58add534bc186238ae028a73f22`.
- Snapshot B proficiency SHA-256 is `97e59f4c247c6a64884ecbbfcceb2ba6dbad82f4fe52749f035b6b3d01c84ee1`.
- Snapshot B contains 443 definitions, 2211 levels, 3671 perks and 22 reviewed `Type=32` perks with `ElementId`, `MissileId`, `Multiplier`, and `Probability`, and no `Value`.
- The former producer rejected that exact repeated shape; schema 2 preserves it without inferring gameplay meaning.
- Pre-merge full A/B generation succeeded for manifest, StaticData, StaticMapData and proficiency evidence.
- StaticData changes from schema family `legacy` in A to `newer` in B while format, schemaVersion and parser revision remain compatible. TCR-009 must emit the explicit schema-family-change finding and scope record comparison accordingly.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Use schemaVersion 2 | Making `value` optional is a material schema change; parser revision alone is not an adequate schema contract. | none |
| Do not synthesize `value` | The exact source does not contain it. | none |
| Keep the format name stable | The producer remains the same TCR-004 evidence family; consumers must inspect schemaVersion. | none |
| Accept schema 1 and 2 in the existing TCR-007 resolver | Historical retained reports remain valid while unknown future versions fail closed. | none |
| Keep one resolver | A temporary compatibility wrapper plus copied legacy resolver was removed before final gate to avoid parallel semantics. | none |
| Do not infer numeric ranges for probability or multiplier | Available evidence establishes finite numeric fields, not gameplay semantics. | none |
| Reconcile programme/catalogue/changelog in TCR-009 activation | Their queue/status evidence depends on final retained report hashes and the merged parser revision, which do not exist before this PR merges. | none |

# Validation and CI

Never record a pass without exact command or workflow evidence.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T22:20:00+02:00
head: 92d497115333608349dface60abf7f03b34dd8b8
branch: fix/CAN-20260729-tcr-004a-proficiency-perk-schema-v2
pr: 1014
status: final-gate
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
  - Snapshot B exact proficiency input contains 22 Type 32 perks with MissileId, Multiplier and Probability and no Value.
  - Schema 2 preserves exact reviewed fields and does not synthesize Value.
  - The single TCR-007 resolver accepts only schema versions 1 and 2 and rejects future versions.
  - Complete pre-merge A and B manifests plus all three required index families were generated outside Git.
  - StaticData family changes from legacy to newer and is an explicit TCR-009 drift family rather than malformed evidence.
  - Tibia Client Reference workflow 30487311955 passed on 92d497115333608349dface60abf7f03b34dd8b8.
  - Agent Task Ownership workflow 30487311984 passed on 92d497115333608349dface60abf7f03b34dd8b8.
  - Tibia Proficiency Schema v2 workflow 30487312006 passed on 92d497115333608349dface60abf7f03b34dd8b8.
  - AI Agent Tools workflow 30487311966 passed on 92d497115333608349dface60abf7f03b34dd8b8.
  - CI workflow 30487312101 passed on 92d497115333608349dface60abf7f03b34dd8b8.
derived:
  - Merging this producer extension is required before final retained snapshot hashes and owner-result evidence can be recorded.
unknown:
  - Exact final checkpoint commit SHA and its forced final-gate CI results.
conflicts: []
first_failure:
  marker: TCR004_UNSUPPORTED_REVIEWED_PROJECTILE_PERK_SHAPE
  evidence: The former producer failed closed at snapshot B proficiency 422 level 3 perk 2 before schema 2 support was added.
rejected_hypotheses:
  - Ignore unknown fields.
  - Synthesize Value from Multiplier or Probability.
  - Keep a copied legacy resolver behind a wrapper.
  - Treat snapshot B as malformed without reviewing its repeated deterministic shape.
changed_paths:
  - .github/workflows/tibia-proficiency-schema-v2.yml
  - docs/agents/tasks/active/CAN-20260729-tcr-004a-proficiency-perk-schema-v2.md
  - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX_SCHEMA_V2.md
  - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX_V2.schema.json
  - tools/ai-agent/test_tibia_proficiency_reference_index_schema_v2.py
  - tools/ai-agent/tibia_proficiency_reference_index.py
  - tools/ai-agent/tibia_proficiency_reference_resolver.py
validation:
  - command: CANARY_TIBIA_PROFICIENCY_CURRENT_FILE=<snapshot-b> PYTHONPATH=.:local_stubs python -m unittest -v test_tibia_proficiency_reference_index_schema_v2.py
    result: PASS
    evidence: Five tests passed with exact snapshot B, including 443 definitions and 22 reviewed no-Value projectile perks.
  - command: python -m py_compile tibia_proficiency_reference_index.py tibia_proficiency_reference_resolver.py test_tibia_proficiency_reference_index_schema_v2.py
    result: PASS
    evidence: Final single-resolver source compiled locally.
  - command: python -m json.tool TIBIA_PROFICIENCY_REFERENCE_INDEX_V2.schema.json
    result: PASS
    evidence: Schema syntax passed locally and in workflow 30487312006.
  - command: pre-merge exact A/B retained-snapshot generation
    result: PASS
    evidence: Both manifests and all six index reports were generated and hash-closed outside Git; expected StaticData legacy-to-newer family change was detected.
  - command: GitHub workflow set on 92d497115333608349dface60abf7f03b34dd8b8
    result: PASS
    evidence: Required workflows 30487311955, 30487311984, 30487312006, 30487311966 and 30487312101 all succeeded.
blockers: []
next_action: verify forced final-gate CI on the checkpoint commit, inspect review state, mark PR ready, and squash-merge exact final head.
```
