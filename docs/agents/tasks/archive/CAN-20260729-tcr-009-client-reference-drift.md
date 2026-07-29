---
task_id: CAN-20260729-tcr-009-client-reference-drift
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: TCR-009
status: completed
agent: chatgpt
branch: feat/CAN-20260729-tcr-009-client-reference-drift
base_branch: main
created: 2026-07-29T23:36:00+02:00
updated: 2026-07-30T00:56:08+02:00
last_verified_commit: "c678d90483af945b3bbf0a40f6d6b9ce99da4a3f"
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
    - docs/agents/tasks/archive/CAN-20260729-tcr-009-client-reference-drift.md
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
completed: 2026-07-30T00:56:08+02:00
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
- [x] Add focused malformed, determinism, compatibility, boundedness and retained-evidence coverage.
- [x] Fulfil and consume the owner request through the canonical lifecycle and generated indexes.
- [x] Reconcile programme, catalogue and changelog.
- [x] Pass exact-final-head and readiness-triggered full CI.
- [x] Squash-merge and archive the lifecycle.

# Completion evidence

- Feature PR: #1018.
- Feature head: `b71de781c1623b44134682abcfc9db585bb8d130`.
- Merge commit: `c678d90483af945b3bbf0a40f6d6b9ce99da4a3f`.
- Merged at: `2026-07-29T22:56:08Z`.
- Snapshot A final manifest SHA-256: `6096b021ca21d911165f89bfc714f558fc7efde0a455855caed071852ccfcee1`.
- Snapshot B final manifest SHA-256: `54646c3f71cc98c53049c63a49a331ec08acb71a37c551f5c592f55645be7e53`.
- Retained evidence summary SHA-256: `6224a175fab73931627c1ea36545e4b5f1bc4c29068fa337049130ee777a3431`.
- Retained drift SHA-256: `be0593cb260cc717b2d8e9e1a19a565f958e85935fde4ac09ce8fb5bbb853b31` with 27 findings.
- `RTREQ-TCR-ITEM-DEFINITIONS-0002` is consumed by accepted evidence `RT-ITEM-DEFINITIONS-0003`.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T00:56:08+02:00
head: b71de781c1623b44134682abcfc9db585bb8d130
branch: feat/CAN-20260729-tcr-009-client-reference-drift
pr: 1018
status: completed
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
  - The producer consumes existing manifests and indexes only and never reparses proprietary client files.
  - StaticData legacy-to-newer drift is explicit and cross-family record comparison is skipped.
  - Findings and field changes are deterministic and bounded; nine focused tests pass.
  - Published synthetic output validates against the Draft 2020-12 schema.
  - The canonical owner-request lifecycle consumed RTREQ-TCR-ITEM-DEFINITIONS-0002 into RT-ITEM-DEFINITIONS-0003.
  - Programme queue, module catalogue and changelog were reconciled.
  - Final-head workflows 30496191170, 30496191189, 30496191154, 30496191244, 30496191213, 30496191172, 30496191194 and 30496191295 passed.
  - Readiness-triggered full CI 30496550577 passed Linux debug/release, Docker build, Docker quickstart and Required aggregation.
  - PR 1018 had no comments, reviews or review threads and squash-merged as c678d90483af945b3bbf0a40f6d6b9ce99da4a3f.
derived:
  - TCR-010 Evidence Gateway Integration is the next independently mergeable programme stage.
unknown: []
conflicts: []
first_failure:
  marker: none
  evidence: Checkpoint status and compactness validation issues were corrected before the exact final head; all final gates passed.
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
  - docs/ai-agent/TIBIA_CLIENT_REFERENCE_DRIFT.md
  - docs/ai-agent/TIBIA_CLIENT_REFERENCE_DRIFT.schema.json
  - tools/ai-agent/test_tibia_client_reference_drift.py
  - tools/ai-agent/tibia_client_reference_drift.py
validation:
  - command: complete final-head workflow set
    result: PASS
    evidence: Ownership, evidence, module registry, upstream, drift, AI tools, Universal E2E Stability and CI succeeded on b71de781c1623b44134682abcfc9db585bb8d130.
  - command: readiness-triggered CI 30496550577
    result: PASS
    evidence: Fast checks, Lua tests, Linux debug/release, Docker image, Docker quickstart and Required aggregator all succeeded.
blockers: []
next_action: Start TCR-010 Evidence Gateway Integration as a separate bounded task and PR.
```

## Automated lifecycle completion

This record was moved from `tasks/active` to `tasks/archive` after PR #1018 merged and its exact final evidence was preserved.
