---
task_id: CAN-20260729-tcr-009-client-reference-drift
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: TCR-009
status: implementing
agent: chatgpt
branch: feat/CAN-20260729-tcr-009-client-reference-drift
base_branch: main
created: 2026-07-29T23:36:00+02:00
updated: 2026-07-29T23:36:00+02:00
last_verified_commit: "20b4d6c98a6893d90281216487437a61c8e0aa66"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - TCR-002 merged stable canary-tibia-staticdata-index-v1
  - TCR-003 merged stable canary-tibia-staticmapdata-index-v1
  - TCR-004/TCR-004A merged stable canary-tibia-proficiency-index-v1 schemaVersion 2
  - RTREQ-TCR-ITEM-DEFINITIONS-0002 exact retained A/B evidence satisfied outside Git
blocks:
  - TCR-010
  - TCR-011
  - OWA-003
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260729-tcr-009-client-reference-drift.md
    - tools/ai-agent/tibia_client_reference_drift.py
    - tools/ai-agent/test_tibia_client_reference_drift.py
    - docs/ai-agent/TIBIA_CLIENT_REFERENCE_DRIFT.md
    - docs/ai-agent/TIBIA_CLIENT_REFERENCE_DRIFT.schema.json
    - .github/workflows/tibia-client-reference-drift.yml
  shared:
    - docs/agents/real-tibia/evidence/requests/tcr/RTREQ-TCR-ITEM-DEFINITIONS-0002.yaml
    - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
    - docs/agents/real-tibia/evidence/modules/item-definitions/EVIDENCE_INDEX.yaml
    - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - exact user-supplied official-client packages outside Git
    - owner-retained generated TCR reports outside Git
    - tools/ai-agent/tibia_client_reference_manifest.py
    - tools/ai-agent/tibia_staticdata_reference_index.py
    - tools/ai-agent/tibia_staticmapdata_reference_index.py
    - tools/ai-agent/tibia_proficiency_reference_index.py
modules_touched:
  - Tibia client-reference drift
  - Real Tibia owner-request lifecycle
reuses:
  - canary-tibia-client-reference-manifest-v1
  - canary-tibia-staticdata-index-v1
  - canary-tibia-staticmapdata-index-v1
  - canary-tibia-proficiency-index-v1
  - canary-real-tibia-owner-request-v1
public_interfaces:
  - canary-tibia-client-reference-drift-v1
cross_repo_tasks: []
---

# Goal

Implement the deterministic, read-only TCR-009 client-reference drift producer over two complete exact retained manifest/index snapshot sets, fulfil and consume `RTREQ-TCR-ITEM-DEFINITIONS-0002`, and unblock the next programme stages without reparsing or mutating client files.

# Acceptance criteria

- [ ] Consume exact final and bootstrap manifests plus StaticData, StaticMapData and proficiency reports for baseline A and current B.
- [ ] Validate manifest/report format, schema, parser revision, hash closure and source bindings fail closed.
- [ ] Emit deterministic input-component and record-level findings with bounded field changes.
- [ ] Emit explicit StaticData schema-family drift and skip cross-family record comparison.
- [ ] Compute dependency-scoped staleness without timestamp freshness.
- [ ] Keep appearances/assets under existing owners and make no gameplay or mutation claims.
- [ ] Add focused malformed, determinism, compatibility, boundedness and real-retained smoke tests.
- [ ] Fulfil and consume the owner request through the canonical lifecycle and generated indexes.
- [ ] Reconcile programme, catalogue and changelog, pass exact-final-head CI, merge and archive.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T23:36:00+02:00
head: 20b4d6c98a6893d90281216487437a61c8e0aa66
branch: feat/CAN-20260729-tcr-009-client-reference-drift
pr: null
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
  - otbm
owned_paths:
  - tools/ai-agent/tibia_client_reference_drift.py
  - tools/ai-agent/test_tibia_client_reference_drift.py
  - docs/ai-agent/TIBIA_CLIENT_REFERENCE_DRIFT.md
  - docs/ai-agent/TIBIA_CLIENT_REFERENCE_DRIFT.schema.json
  - .github/workflows/tibia-client-reference-drift.yml
proven:
  - PR 1014 merged proficiency schemaVersion 2 as b68fbf7bf26b57f0cf716abffb52cfa951fa66ce.
  - Final retained A/B manifests and all six reports were regenerated with that parser revision and independently hash-closed.
  - Snapshot A manifest SHA-256 is 6096b021ca21d911165f89bfc714f558fc7efde0a455855caed071852ccfcee1.
  - Snapshot B manifest SHA-256 is 54646c3f71cc98c53049c63a49a331ec08acb71a37c551f5c592f55645be7e53.
  - Retained evidence summary SHA-256 is 6224a175fab73931627c1ea36545e4b5f1bc4c29068fa337049130ee777a3431.
  - A retained drift smoke produced 27 findings and SHA-256 be0593cb260cc717b2d8e9e1a19a565f958e85935fde4ac09ce8fb5bbb853b31.
derived:
  - RTREQ-TCR-ITEM-DEFINITIONS-0002 is no longer blocked by missing snapshot evidence.
unknown:
  - Exact implementation PR number and final-head CI evidence.
conflicts: []
first_failure:
  marker: none
  evidence: The former external-evidence blocker is satisfied; implementation has not yet been published.
rejected_hypotheses:
  - Reparse client packages inside the drift producer.
  - Compare StaticData records across legacy and newer schema families.
  - Use timestamps as freshness evidence.
  - Commit proprietary inputs or retained reports.
changed_paths:
  - docs/agents/tasks/active/CAN-20260729-tcr-009-client-reference-drift.md
validation: []
blockers: []
next_action: open the draft PR, implement and validate the bounded drift producer, then record the owner result with stable external-report hashes.
```
