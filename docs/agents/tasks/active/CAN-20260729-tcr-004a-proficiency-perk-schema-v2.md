---
task_id: CAN-20260729-tcr-004a-proficiency-perk-schema-v2
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: TCR-004A-PROFICIENCY-PERK-SCHEMA-V2
status: implementing
agent: chatgpt
branch: fix/CAN-20260729-tcr-004a-proficiency-perk-schema-v2
base_branch: main
created: 2026-07-29T21:20:00+02:00
updated: 2026-07-29T21:20:00+02:00
last_verified_commit: "e81a1daf3e32448047118bf07f22b941658128a4"
risk: medium
related_issue: ""
related_pr: ""
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
    - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX.md
    - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX.schema.json
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
    - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
    - .github/workflows/tibia-client-reference.yml
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

Extend the existing TCR-004 producer for the reviewed proficiency perk shape present in exact client snapshot `15.31.69f220` without inventing a missing `Value`, weakening unknown-field rejection, reparsing appearances, or changing gameplay/runtime state.

# Acceptance criteria

- [ ] Preserve legacy `Value` perks.
- [ ] Preserve reviewed `MissileId`, `Multiplier`, and `Probability` fields.
- [ ] Represent source perks that omit `Value` without synthesizing one.
- [ ] Require `Type` and at least one finite numeric effect field.
- [ ] Publish an explicit schemaVersion 2 contract while keeping the format name stable.
- [ ] Keep TCR-007 able to consume exact schemaVersion 1 and 2 indexes.
- [ ] Add focused malformed, determinism, schema and real external-file tests.
- [ ] Regenerate both retained TCR-009 snapshots outside Git after merge.
- [ ] Pass exact final-head CI and complete merge/archive lifecycle.

# Confirmed context

- `main` was verified at `e81a1daf3e32448047118bf07f22b941658128a4`.
- Snapshot A proficiency SHA-256 is `1a915dffd9265cd1c18d39e55da7ede691b2e58add534bc186238ae028a73f22`; the existing producer accepts it.
- Snapshot B proficiency SHA-256 is `97e59f4c247c6a64884ecbbfcceb2ba6dbad82f4fe52749f035b6b3d01c84ee1`.
- Snapshot B contains 22 reviewed perks with `Type=32`, `ElementId`, `MissileId`, `Multiplier`, and `Probability`, and no `Value`.
- The current producer fails closed first on unsupported new fields and then on missing `Value`.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Use schemaVersion 2 | Making `value` optional is a material schema change; parser revision alone is not an adequate schema contract. | none |
| Do not synthesize `value` | The exact source does not contain it. | none |
| Do not infer numeric ranges for probability or multiplier | Available evidence establishes finite numeric fields, not gameplay semantics. | none |

# Validation and CI

Never record a pass without exact command or workflow evidence.

# Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T21:20:00+02:00
head: e81a1daf3e32448047118bf07f22b941658128a4
branch: fix/CAN-20260729-tcr-004a-proficiency-perk-schema-v2
pr: none
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
  - otbm
owned_paths:
  - tools/ai-agent/tibia_proficiency_reference_index.py
  - tools/ai-agent/test_tibia_proficiency_reference_index_schema_v2.py
  - tools/ai-agent/tibia_proficiency_reference_resolver.py
  - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX.md
  - docs/ai-agent/TIBIA_PROFICIENCY_REFERENCE_INDEX.schema.json
  - .github/workflows/tibia-client-reference.yml
proven:
  - Snapshot B exact proficiency input contains 22 Type 32 perks with MissileId, Multiplier and Probability and no Value.
  - Existing TCR-004 rejects that exact source.
derived:
  - A versioned producer/schema extension is required before TCR-009 can obtain two complete compatible snapshots.
unknown: []
conflicts: []
first_failure:
  marker: TCR004_UNSUPPORTED_REVIEWED_PROJECTILE_PERK_SHAPE
  evidence: Exact snapshot B fails at proficiencies[422].Levels[3].Perks[2].
rejected_hypotheses:
  - Ignore unknown fields.
  - Synthesize Value from Multiplier or Probability.
  - Treat snapshot B as malformed without reviewing its repeated deterministic shape.
changed_paths:
  - docs/agents/tasks/active/CAN-20260729-tcr-004a-proficiency-perk-schema-v2.md
validation:
  - command: local focused schema-v2 tests against reconstructed exact main producer
    result: PASS
    evidence: 4 tests passed; exact snapshot A and B normalized with 420/443 records respectively.
blockers: []
next_action: open the draft PR, implement the versioned producer/schema/consumer changes, and run focused plus exact real-file validation.
```
