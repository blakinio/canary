---
task_id: CAN-20260730-owa-003c-executed-evidence
program_id: CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
coordination_id: OWA-003C
status: active
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260730-owa-003c-executed-evidence
base_branch: main
created: 2026-07-30T22:35:00+02:00
updated: 2026-07-30T22:35:00+02:00
last_verified_commit: "9704087e3d6fc7b434938b343a546c14a23a447e"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - TCR-009 stable retained exact snapshot A/B and drift identities
  - TCR-010 stable evidence gateway contracts
  - TCR-011 stable adoption routing contracts
  - OWA-003A stable freshness impact contracts
  - QA-016 stable release provenance contracts
blocks:
  - OWA-003 downstream QA-008/002/007/006 evaluation
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260730-owa-003c-executed-evidence.md
    - .github/workflows/owa-003c-executed-evidence.yml
    - docs/ai-agent/OTBM_TCR_QA_EXECUTED_EVIDENCE.md
  shared:
    - docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md
    - docs/ai-agent/OTBM_WORLD_ASSURANCE_OPERATIONS_ROADMAP.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/tibia_client_reference_manifest.py
    - tools/ai-agent/tibia_staticdata_reference_index.py
    - tools/ai-agent/tibia_staticmapdata_reference_index.py
    - tools/ai-agent/tibia_proficiency_reference_index.py
    - tools/ai-agent/tibia_client_reference_drift.py
    - tools/ai-agent/tibia_client_reference_evidence_gateway.py
    - tools/ai-agent/tibia_reference_adoption_router.py
    - tools/ai-agent/otbm_release_provenance.py
    - tools/ai-agent/otbm_tcr_qa_freshness.py
    - exact official-client inputs and generated reports retained outside Git
modules_touched:
  - OTBM World Assurance Operations
  - OTBM TCR-to-QA Freshness Impact
reuses:
  - canary-tibia-client-reference-manifest-v1
  - canary-tibia-client-reference-drift-v1
  - canary-tibia-client-reference-evidence-gateway-v1
  - canary-tibia-reference-adoption-routing-v1
  - canary-otbm-release-provenance-v1
  - canary-otbm-tcr-qa-freshness-impact-v1
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Produce and retain one real executed OWA-003A freshness impact with exact TCR-011, QA-016, BOM, reviewer mapping, invocation and artifact identities, then evaluate the canonical downstream chain only in its required order.

# Acceptance criteria

- [ ] Revalidate exact current `main`, ownership, open PRs and branches.
- [ ] Recover or deterministically rematerialize the exact retained TCR input/report chain without committing proprietary client payloads.
- [ ] Execute TCR-010 and TCR-011 over exact retained real evidence, preserving unsupported and blocked outcomes.
- [ ] Author one explicit reviewed route/component/dimension mapping from exact evidence only; no name/proximity/ID guessing.
- [ ] Execute QA-016 and OWA-003A with full hash closure and retain the impact in GitHub Actions.
- [ ] Record artifact ID, workflow run ID, byte size, file SHA-256, report SHA-256, manifest/routing/provenance/BOM identities and review statement.
- [ ] Evaluate QA-008, Semantic Diff, QA-002, owning validators, Physical E2E, QA-007 and QA-006 only when each earlier canonical input exists.
- [ ] Preserve a precise first external-evidence blocker if the chain still cannot be completed legally.
- [ ] Pass exact-final-head checks, squash-merge, then complete a separate lifecycle archive PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T22:35:00+02:00
head: 9704087e3d6fc7b434938b343a546c14a23a447e
branch: feat/CAN-20260730-owa-003c-executed-evidence
pr: null
status: active
context_routes:
  - agent-governance
  - otbm
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260730-owa-003c-executed-evidence.md
  - .github/workflows/owa-003c-executed-evidence.yml
  - docs/ai-agent/OTBM_TCR_QA_EXECUTED_EVIDENCE.md
proven:
  - Current main is 9704087e3d6fc7b434938b343a546c14a23a447e and no open OWA/TCR/QA PR or OWA/candidate branch owns this scope.
  - TCR-009 completed two exact retained snapshots and drift: A manifest 6096b021..., B manifest 54646c3f..., retained summary 6224a175..., drift be0593cb... with 27 findings.
  - TCR-010, TCR-011 and OWA-003A contracts are stable, but their exact-head workflows retained no executed operational artifacts.
  - The previously supplied snapshot B was version 15.31.69f220 with package SHA-256 95093b15462573cc413fc7752d99ab258f97b58734bc59a8f6ef34cc1921a0f8; its local binary is not mounted in the current runtime.
  - The supplied OTBM SHA-256 a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2 is the current OWA-001 map, not an OWA-006 candidate.
derived:
  - A trusted repository workflow can rematerialize official current package inputs and execute existing producers while keeping proprietary payloads outside Git.
unknown:
  - Whether the official current package still resolves byte-identically to retained snapshot B.
  - Whether exact retained TCR-005/006/007 inputs required for a complete operational TCR-010 route can be recovered or reproduced.
conflicts: []
first_failure:
  marker: pending-rematerialization
  evidence: no retained executed canary-otbm-tcr-qa-freshness-impact-v1 is currently available.
rejected_hypotheses:
  - Treat stable code, schemas or unit-test fixtures as executed operational evidence.
  - Use the current map as an OWA-006 candidate.
  - Infer reviewer mappings from names, visual proximity or guessed identifier equivalence.
validation: []
blockers: []
next_action: Open the draft PR, bind its number into this task, then add a trusted exact-input rematerialization workflow and inspect its retained artifact.
```
