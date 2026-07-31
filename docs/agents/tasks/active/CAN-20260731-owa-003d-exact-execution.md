---
task_id: CAN-20260731-owa-003d-exact-execution
program_id: CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
coordination_id: OWA-003D
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260731-owa-003d-exact-execution
base_branch: main
created: 2026-07-31T09:15:00+02:00
updated: 2026-07-31T09:25:00+02:00
last_verified_commit: "11c42faace4b70247387f57e22f8d16875bc52f3"
risk: high
related_issue: ""
related_pr: "1044"
depends_on:
  - TCR-009 merged stable client-reference drift producer
  - TCR-010 merged stable evidence gateway
  - TCR-011 merged stable adoption router
  - OWA-003A merged stable TCR-to-QA freshness integration
  - exact snapshot A package version 15.25.bd5a04 supplied outside Git
  - exact snapshot B package version 15.31.69f220 supplied outside Git
blocks:
  - OWA-003 downstream QA-008/002/007/006 assurance
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260731-owa-003d-exact-execution.md
    - docs/ai-agent/OTBM_TCR_QA_EXECUTED_EVIDENCE.md
    - docs/ai-agent/OTBM_TCR_QA_OPERATIONAL_EXECUTION.md
    - .github/workflows/owa-003d-exact-execution.yml
  shared:
    - docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md
    - docs/ai-agent/OTBM_WORLD_ASSURANCE_OPERATIONS_ROADMAP.md
  read_only:
    - exact user-supplied client packages outside Git
    - tools/ai-agent/tibia_client_reference_*.py
    - tools/ai-agent/tibia_reference_adoption_*.py
    - tools/ai-agent/otbm_tcr_qa_freshness*.py
    - docs/ai-agent/TIBIA_CLIENT_REFERENCE_*.schema.json
    - docs/ai-agent/TIBIA_REFERENCE_ADOPTION_*.schema.json
    - docs/ai-agent/OTBM_TCR_QA_FRESHNESS*.schema.json
modules_touched:
  - Tibia client-reference operational evidence
  - OTBM TCR-to-QA freshness operational evidence
reuses:
  - canary-tibia-client-reference-manifest-v1
  - canary-tibia-staticdata-index-v1
  - canary-tibia-staticmapdata-index-v1
  - canary-tibia-proficiency-index-v1
  - canary-tibia-client-reference-drift-v1
  - canary-tibia-client-reference-evidence-gateway-v1
  - canary-tibia-reference-adoption-routing-v1
  - canary-otbm-release-provenance-v1
  - canary-otbm-tcr-qa-freshness-impact-v1
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Use the exact externally supplied snapshot-B package to deterministically rematerialize the accepted TCR-009 evidence chain, execute the existing TCR-010 and TCR-011 owners, and produce one real retained OWA-003A freshness-impact artifact without committing proprietary client payloads or replacing any existing parser, router, provenance owner or QA engine.

# Acceptance criteria

- [ ] Verify snapshot A and B package identities, versions and bounded package contents.
- [ ] Reproduce the accepted TCR-009 final manifest identities and all six generated indexes with parser revision `b68fbf7bf26b57f0cf716abffb52cfa951fa66ce`.
- [ ] Reproduce deterministic TCR-009 drift identity and finding count, or record the first exact incompatibility without guessing.
- [ ] Execute one exact reviewed TCR-010 evidence gateway report.
- [ ] Execute one exact reviewed TCR-011 adoption-routing report.
- [ ] Resolve compatible current/previous QA-016 BOM and release-provenance evidence.
- [ ] Execute OWA-003A with a reviewer-authored exact mapping and retain file/report/manifest/routing/provenance/BOM identities.
- [ ] Keep proprietary packages and generated client indexes outside Git; commit only non-proprietary metadata and exact durable references.
- [ ] Evaluate the first downstream OWA-003 evidence requirement only after the real impact exists.
- [ ] Pass exact-head checks, squash-merge, then complete lifecycle in a separate PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-31T09:25:00+02:00
head: 11c42faace4b70247387f57e22f8d16875bc52f3
branch: feat/CAN-20260731-owa-003d-exact-execution
pr: 1044
status: implementing
context_routes:
  - agent-governance
  - otbm
  - real-tibia-parity
  - testing
owned_paths:
  - docs/agents/tasks/active/CAN-20260731-owa-003d-exact-execution.md
  - docs/ai-agent/OTBM_TCR_QA_EXECUTED_EVIDENCE.md
  - docs/ai-agent/OTBM_TCR_QA_OPERATIONAL_EXECUTION.md
  - .github/workflows/owa-003d-exact-execution.yml
proven:
  - Current main is 95b276db311cf6e9acd58b847f1fb0ca6697b137.
  - Draft PR 1044 targets blakinio/canary main from the same repository task branch.
  - No open OWA, TCR, QA-016 or Semantic Diff PR overlaps this bounded scope.
  - Supplied snapshot B SHA-256 is 95093b15462573cc413fc7752d99ab258f97b58734bc59a8f6ef34cc1921a0f8.
  - Supplied snapshot B package version is 15.31.69f220.
  - These values exactly match the accepted TCR-009 snapshot-B identity recorded by the prior lifecycle.
  - Supplied snapshot A remains available outside Git as version 15.25.bd5a04.
  - Temporary workflow run 30612690907 owns a read-only export of current and accepted-parser owner sources; proprietary packages are not uploaded.
derived:
  - The OWA003C missing-snapshot-B blocker is no longer valid for this runtime.
unknown:
  - Whether current-main producers reproduce every accepted TCR-009 byte identity from the exact package pair.
  - The exact reviewer-authored TCR-010 binding and TCR-011 routing requests retained outside Git.
  - The first compatible QA-016 current/previous provenance pair and OWA-003A mapping.
conflicts: []
first_failure:
  marker: none
  evidence: Exact package identity is present; source export and operational rematerialization are in progress.
rejected_hypotheses:
  - Commit proprietary package bytes.
  - Replace the existing client-reference parser, drift producer, gateway, router or freshness tool.
  - Treat hashes or task prose as report payloads.
  - Infer route, component or dimension IDs heuristically.
changed_paths:
  - .github/workflows/owa-003d-exact-execution.yml
  - docs/agents/tasks/active/CAN-20260731-owa-003d-exact-execution.md
validation:
  - command: sha256sum and package.json inspection of supplied snapshot B
    result: PASS
    evidence: SHA-256 and version exactly match accepted snapshot-B identity.
blockers: []
next_action: Download the owner-source artifact from workflow 30612690907 and execute the existing producers locally against the exact A/B packages.
```
