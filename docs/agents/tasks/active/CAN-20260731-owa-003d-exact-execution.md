---
task_id: CAN-20260731-owa-003d-exact-execution
program_id: CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
coordination_id: OWA-003D
status: blocked
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260731-owa-003d-exact-execution
base_branch: main
created: 2026-07-31T09:15:00+02:00
updated: 2026-07-31T10:00:00+02:00
last_verified_commit: "a68ee8c032415591a07334e663affee930764d35"
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

- [x] Verify snapshot A and B package identities, versions and bounded package contents.
- [x] Rematerialize exact package-bound manifests and all six generated indexes with parser revision `b68fbf7bf26b57f0cf716abffb52cfa951fa66ce`; preserve the missing historical reviewer-authored manifest bytes as not recovered.
- [x] Reproduce the accepted deterministic 27-finding TCR-009 semantic result without guessing historical payload bytes.
- [x] Execute one exact reviewed TCR-010 evidence gateway report.
- [x] Execute one exact reviewed TCR-011 adoption-routing report.
- [x] Resolve compatible current/previous QA-016 BOM and release-provenance evidence.
- [x] Execute OWA-003A with a reviewer-authored exact mapping and retain file/report/manifest/routing/provenance/BOM identities.
- [x] Keep proprietary packages and generated client indexes outside Git; commit only non-proprietary metadata and exact durable references.
- [x] Evaluate the first downstream OWA-003 evidence requirement without synthesizing a map change.
- [ ] Pass exact-head checks, squash-merge, then complete lifecycle in a separate PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-31T10:00:00+02:00
head: a68ee8c032415591a07334e663affee930764d35
branch: feat/CAN-20260731-owa-003d-exact-execution
pr: 1044
status: blocked
context_routes:
  - agent-governance
  - otbm
  - real-tibia-parity
  - testing
owned_paths:
  - docs/agents/tasks/active/CAN-20260731-owa-003d-exact-execution.md
  - docs/ai-agent/OTBM_TCR_QA_EXECUTED_EVIDENCE.md
  - docs/ai-agent/OTBM_TCR_QA_OPERATIONAL_EXECUTION.md
  - docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md
  - docs/ai-agent/OTBM_WORLD_ASSURANCE_OPERATIONS_ROADMAP.md
proven:
  - Snapshot B SHA-256 95093b15462573cc413fc7752d99ab258f97b58734bc59a8f6ef34cc1921a0f8 and version 15.31.69f220 exactly match accepted TCR-009 identity.
  - Existing owners reproduced the accepted 27-finding semantic TCR-009 result from exact snapshot A/B package bytes and parser revision b68fbf7bf26b57f0cf716abffb52cfa951fa66ce.
  - TCR-010 selected four exact reviewed fragments and TCR-011 routed two to existing owners while preserving two targetless unsupported StaticData routes.
  - QA-016 exact BOM/provenance comparison and reviewer-authored OWA-003A mapping produced two exact stale dimensions.
  - Workflow run 30614565219 artifact 8786807858 retains the exact freshness impact and associated execution identities for 90 days.
  - Ninety-five focused existing-owner tests pass and all operational producer reruns are deterministic.
  - No proprietary archive, selected client input, generated index, map, runtime state or database state was committed or mutated.
derived:
  - OWA003C_NO_RECOVERABLE_EXACT_TCR009_SNAPSHOT_B_PAYLOAD_OR_RETAINED_REPORT_CHAIN is superseded for this execution.
  - Client-reference drift cannot be promoted into map authority, a no-op Semantic Diff or an OWA-006 candidate.
unknown:
  - A reviewer-authored QA-008 graph root compatible with this exact impact and QA-001/QA-002.
  - One distinct reviewed real before/after OTBM change chain for canonical Semantic Diff and downstream regression evidence.
conflicts: []
first_failure:
  marker: OWA003D_NO_REVIEWED_QA008_ROOT_AND_CANONICAL_MAP_CHANGE_CHAIN
  evidence: QA-008 requires a reviewed graph and compatible QA-001/QA-002; no distinct reviewed map change exists, so Semantic Diff and later owners cannot execute without fabrication.
rejected_hypotheses:
  - Commit proprietary package bytes or full generated client-reference reports.
  - Replace existing parser, drift producer, gateway, router, provenance or freshness owners.
  - Reconstruct historical report bytes from hashes or task prose.
  - Guess route, component, dimension or dependency-edge mappings.
  - Treat current map as both before and candidate or generate a no-op Semantic Diff.
  - Promote unsupported StaticData routes into handled evidence.
changed_paths:
  - docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260731-owa-003d-exact-execution.md
  - docs/ai-agent/OTBM_TCR_QA_EXECUTED_EVIDENCE.md
  - docs/ai-agent/OTBM_TCR_QA_OPERATIONAL_EXECUTION.md
  - docs/ai-agent/OTBM_WORLD_ASSURANCE_OPERATIONS_ROADMAP.md
validation:
  - command: exact snapshot SHA-256/version and selected-input closure
    result: PASS
    evidence: Both archives and all eight selected package inputs match declared exact identities.
  - command: existing TCR-009/010/011, QA-016 and OWA-003A owner execution plus deterministic rerun
    result: PASS
    evidence: All before/after output hashes are identical; TCR-009 contains exactly 27 findings.
  - command: focused existing-owner tests
    result: PASS
    evidence: 95 tests pass, including malformed input, no-clobber, exact coverage and output-safety cases.
  - command: retained Actions artifact verification
    result: PASS
    evidence: Run 30614565219 artifact 8786807858 digest and embedded SHA256SUMS independently verify.
  - command: downstream QA-008 / Semantic Diff preflight
    result: BLOCKED
    evidence: No reviewed QA-008 root and no distinct canonical map-change chain exist; later stages remain unevaluated/not-refreshed.
blockers:
  - OWA003D_NO_REVIEWED_QA008_ROOT_AND_CANONICAL_MAP_CHANGE_CHAIN
next_action: Remove the temporary workflow, pass exact-head feature gates, merge PR 1044 and archive the blocked terminal lifecycle in a separate PR.
```
