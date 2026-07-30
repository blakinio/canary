---
task_id: CAN-20260730-tcr-010-evidence-gateway
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: TCR-010
status: implementing
agent: chatgpt
branch: feat/CAN-20260730-tcr-010-evidence-gateway
base_branch: main
created: 2026-07-30T08:14:00+02:00
updated: 2026-07-30T08:14:00+02:00
last_verified_commit: "6c7bdb8817d2010620d119a9a1f6b944895bc73d"
risk: low
related_issue: ""
related_pr: ""
depends_on:
  - TCR-005 stable canary-otbm-house-reference-parity-v1
  - TCR-006 stable canary-tibia-content-reference-correlation-v1
  - TCR-007 stable canary-tibia-proficiency-reference-correlation-v1
  - TCR-009 stable canary-tibia-client-reference-drift-v1
  - OTBM-QA-018 stable canary-otbm-evidence-gateway-manifest-v1 and canary-otbm-evidence-bundle-v1
blocks:
  - TCR-011
  - OWA-003
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260730-tcr-010-evidence-gateway.md
    - tools/ai-agent/tibia_client_reference_evidence_gateway.py
    - tools/ai-agent/tibia_client_reference_evidence_gateway_tool.py
    - tools/ai-agent/test_tibia_client_reference_evidence_gateway.py
    - tools/ai-agent/test_tibia_client_reference_evidence_gateway_output_safety.py
    - tools/ai-agent/test_tibia_client_reference_evidence_gateway_schema.py
    - docs/ai-agent/TIBIA_CLIENT_REFERENCE_EVIDENCE_GATEWAY.md
    - docs/ai-agent/TIBIA_CLIENT_REFERENCE_EVIDENCE_BINDINGS.schema.json
    - docs/ai-agent/TIBIA_CLIENT_REFERENCE_EVIDENCE_GATEWAY.schema.json
    - .github/workflows/tibia-client-reference-evidence-gateway.yml
  shared:
    - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/otbm_evidence_gateway.py
    - tools/ai-agent/otbm_evidence_gateway_tool.py
    - exact TCR-005, TCR-006, TCR-007 and TCR-009 reports retained outside Git
modules_touched:
  - OTBM Compact Evidence Gateway
  - Tibia client-reference evidence gateway integration
reuses:
  - canary-otbm-evidence-gateway-manifest-v1
  - canary-otbm-evidence-bundle-v1
  - canary-otbm-house-reference-parity-v1
  - canary-tibia-content-reference-correlation-v1
  - canary-tibia-proficiency-reference-correlation-v1
  - canary-tibia-client-reference-drift-v1
public_interfaces:
  - canary-tibia-client-reference-evidence-bindings-v1
  - canary-tibia-client-reference-evidence-gateway-v1
cross_repo_tasks: []
---

# Goal

Add the smallest read-only TCR-010 integration that resolves one exact reviewed binding and delegates all source/hash/format/path/pointer extraction to the existing QA-018 Compact Evidence Gateway.

# Acceptance criteria

- [ ] Support exact reviewed bindings for house, content, proficiency and drift evidence.
- [ ] Delegate extraction only to `otbm_evidence_gateway.build_evidence_bundle()`.
- [ ] Pin every source by safe relative path, exact SHA-256 and exact stable report format.
- [ ] Permit only bounded reviewed JSON Pointer extracts and exact binding IDs.
- [ ] Fail closed on duplicate IDs, wrong kind/format, stale binding hash, changed source hash, unsafe paths, symlinks, missing pointers and oversized extracts.
- [ ] Perform no client/OTBM parsing, semantic reinterpretation, fuzzy selection, mutation, E2E execution, acceptance or routing decision.
- [ ] Add deterministic plan/execution, schema and output-safety tests.
- [ ] Reconcile programme, catalogue and changelog; pass final-head CI; merge and archive.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T08:14:00+02:00
head: 6c7bdb8817d2010620d119a9a1f6b944895bc73d
branch: feat/CAN-20260730-tcr-010-evidence-gateway
pr: null
status: implementing
context_routes:
  - agent-governance
  - otbm
  - real-tibia-parity
owned_paths:
  - tools/ai-agent/tibia_client_reference_evidence_gateway.py
  - tools/ai-agent/tibia_client_reference_evidence_gateway_tool.py
  - docs/ai-agent/TIBIA_CLIENT_REFERENCE_EVIDENCE_GATEWAY.md
proven:
  - TCR-009 merged in PR 1018 as c678d90483af945b3bbf0a40f6d6b9ce99da4a3f.
  - Programme main 6c7bdb8817d2010620d119a9a1f6b944895bc73d marks TCR-010 ready.
  - QA-018 exposes exact source SHA/format pins, safe relative paths, JSON Pointer confinement and bounded extracts.
  - No open TCR-010 PR or branch exists and no open PR owns the proposed implementation paths.
derived:
  - A reviewed-binding adapter can satisfy TCR-010 without adding another extractor or parser.
unknown:
  - Exact implementation PR number and final-head CI evidence.
conflicts: []
first_failure:
  marker: none
  evidence: Dependencies are stable and ownership is clear.
rejected_hypotheses:
  - Add a second generic evidence gateway.
  - Search source reports by fuzzy content or inferred identifiers.
  - Reparse client files or OTBM inputs.
changed_paths:
  - docs/agents/tasks/active/CAN-20260730-tcr-010-evidence-gateway.md
validation: []
blockers: []
next_action: open a draft PR, implement exact reviewed-binding plan/execution over QA-018, and add focused tests and schemas.
```
