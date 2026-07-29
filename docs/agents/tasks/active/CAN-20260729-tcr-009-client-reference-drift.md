---
task_id: CAN-20260729-tcr-009-client-reference-drift
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: TCR-009
status: ready
agent: chatgpt
branch: feat/CAN-20260729-tcr-009-client-reference-drift
base_branch: main
created: 2026-07-29T23:36:00+02:00
updated: 2026-07-30T00:30:00+02:00
last_verified_commit: "e2890929f157e71959c8a203e3dd53d0f4c04f88"
risk: medium
related_issue: ""
related_pr: "1018"
depends_on:
  - TCR-002 merged stable canary-tibia-staticdata-index-v1
  - TCR-003 merged stable canary-tibia-staticmapdata-index-v1
  - TCR-004/TCR-004A merged stable canary-tibia-proficiency-index-v1 schemaVersion 2
  - RTREQ-TCR-ITEM-DEFINITIONS-0002 consumed exact retained A/B evidence
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
    - docs/agents/real-tibia/evidence/modules/item-definitions/records/RT-ITEM-DEFINITIONS-0003.yaml
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

Implement deterministic, read-only TCR-009 client-reference drift over two complete exact retained manifest/index snapshot sets, consume `RTREQ-TCR-ITEM-DEFINITIONS-0002`, and unblock the next programme stages without reparsing or mutating client files.

# Acceptance criteria

- [x] Consume exact final and bootstrap manifests plus StaticData, StaticMapData and proficiency reports for baseline A and current B.
- [x] Validate manifest/report format, schema, parser revision, hash closure and source bindings fail closed.
- [x] Emit deterministic input-component and record-level findings with bounded field changes.
- [x] Emit explicit StaticData schema-family drift and skip cross-family record comparison.
- [x] Compute dependency-scoped staleness without timestamp freshness.
- [x] Keep appearances/assets under existing owners and make no gameplay or mutation claims.
- [x] Add focused malformed, determinism, compatibility, boundedness and retained-evidence smoke coverage.
- [x] Fulfil and consume the owner request through the canonical lifecycle and generated indexes.
- [x] Reconcile programme, catalogue and changelog.
- [x] Pass the complete read-only implementation-head workflow set on current `main`.
- [ ] Pass the exact final checkpoint head, merge and archive.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T00:30:00+02:00
head: e2890929f157e71959c8a203e3dd53d0f4c04f88
branch: feat/CAN-20260729-tcr-009-client-reference-drift
pr: 1018
status: ready
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
  - docs/agents/real-tibia/evidence/modules/item-definitions/records/RT-ITEM-DEFINITIONS-0003.yaml
proven:
  - Final retained A/B manifests and all six reports use parser revision b68fbf7bf26b57f0cf716abffb52cfa951fa66ce and were independently hash-closed.
  - Snapshot A manifest SHA-256 is 6096b021ca21d911165f89bfc714f558fc7efde0a455855caed071852ccfcee1.
  - Snapshot B manifest SHA-256 is 54646c3f71cc98c53049c63a49a331ec08acb71a37c551f5c592f55645be7e53.
  - Retained evidence summary SHA-256 is 6224a175fab73931627c1ea36545e4b5f1bc4c29068fa337049130ee777a3431.
  - Retained drift smoke produced 27 findings and SHA-256 be0593cb260cc717b2d8e9e1a19a565f958e85935fde4ac09ce8fb5bbb853b31.
  - Nine focused deterministic and fail-closed producer tests pass and synthetic output validates against the published Draft 2020-12 schema.
  - Workflow 30494786511 used the canonical owner-request tool and committed the exact consumed request plus generated evidence indexes.
  - RTREQ-TCR-ITEM-DEFINITIONS-0002 is consumed by accepted evidence RT-ITEM-DEFINITIONS-0003.
  - Workflow 30495080685 reconciled the programme queue, module catalogue and changelog.
  - Branch was synchronized with main commit 8e21a33325d6bd8ddbb647e7c967f940dfd54516 before the final read-only candidate.
  - Agent Task Ownership 30495664559 passed on e2890929f157e71959c8a203e3dd53d0f4c04f88.
  - Real Tibia Evidence Contracts 30495664561 passed on e2890929f157e71959c8a203e3dd53d0f4c04f88.
  - Universal E2E Stability Certification 30495664573 passed on e2890929f157e71959c8a203e3dd53d0f4c04f88.
  - Tibia Client Reference Drift 30495664579 passed on e2890929f157e71959c8a203e3dd53d0f4c04f88.
  - AI Agent Tools 30495664574 passed on e2890929f157e71959c8a203e3dd53d0f4c04f88.
  - Upstream Intelligence 30495664601 passed on e2890929f157e71959c8a203e3dd53d0f4c04f88.
  - CI 30495664834 passed on e2890929f157e71959c8a203e3dd53d0f4c04f88.
  - Real Tibia Module Registry 30495664580 passed on e2890929f157e71959c8a203e3dd53d0f4c04f88.
derived:
  - TCR-010, TCR-011 and OWA-003 can start after merge and lifecycle closure.
unknown:
  - Exact final checkpoint commit SHA, its forced final-gate results and merge commit.
conflicts: []
first_failure:
  marker: ACTIVE_TASK_FRONTMATTER_STATUS
  evidence: Agent Task Ownership 30495171598 rejected frontmatter status validating under tasks/active; frontmatter was corrected and ownership passed on e2890929f157e71959c8a203e3dd53d0f4c04f88.
rejected_hypotheses:
  - Reparse client packages inside the drift producer.
  - Compare StaticData records across legacy and newer schema families.
  - Use timestamps as freshness evidence.
  - Commit proprietary inputs or retained reports.
  - Hand-edit generated evidence indexes.
changed_paths:
  - .github/workflows/tibia-client-reference-drift.yml
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
  - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
  - docs/agents/real-tibia/evidence/modules/item-definitions/EVIDENCE_INDEX.yaml
  - docs/agents/real-tibia/evidence/modules/item-definitions/records/RT-ITEM-DEFINITIONS-0003.yaml
  - docs/agents/real-tibia/evidence/requests/tcr/RTREQ-TCR-ITEM-DEFINITIONS-0002.yaml
  - docs/agents/tasks/active/CAN-20260729-tcr-009-client-reference-drift.md
  - docs/ai-agent/TIBIA_CLIENT_REFERENCE_DRIFT.md
  - docs/ai-agent/TIBIA_CLIENT_REFERENCE_DRIFT.schema.json
  - tools/ai-agent/test_tibia_client_reference_drift.py
  - tools/ai-agent/tibia_client_reference_drift.py
validation:
  - command: python -m unittest -v test_tibia_client_reference_drift.py
    result: PASS
    evidence: Nine deterministic positive and fail-closed tests passed.
  - command: Draft 2020-12 validation of synthetic drift output
    result: PASS
    evidence: The published schema accepts the producer output.
  - command: canonical owner-request lifecycle
    result: PASS
    evidence: The official lifecycle moved RTREQ-TCR-ITEM-DEFINITIONS-0002 through owner acceptance, planning, active result publication and consumption into RT-ITEM-DEFINITIONS-0003.
  - command: complete workflow set on e2890929f157e71959c8a203e3dd53d0f4c04f88
    result: PASS
    evidence: Ownership, evidence, module registry, upstream, dedicated drift, AI tools, Universal E2E Stability and full CI all succeeded.
blockers: []
next_action: apply ci:final-gate, verify every forced workflow on the checkpoint commit, inspect reviews and mergeability, mark ready, and squash-merge the exact green head.
```
