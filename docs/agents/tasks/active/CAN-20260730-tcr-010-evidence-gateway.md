---
task_id: CAN-20260730-tcr-010-evidence-gateway
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: TCR-010
status: ready
agent: chatgpt
branch: feat/CAN-20260730-tcr-010-evidence-gateway
base_branch: main
created: 2026-07-30T08:14:00+02:00
updated: 2026-07-30T09:10:00+02:00
last_verified_commit: "193428b3e6a42308ceb684cf271b568609de4aeb"
risk: low
related_issue: ""
related_pr: "1027"
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

- [x] Support exact reviewed bindings for house, content, proficiency and drift evidence.
- [x] Delegate extraction only to `otbm_evidence_gateway.build_evidence_bundle()`.
- [x] Pin every source by safe relative path, exact SHA-256 and exact stable report format.
- [x] Permit only bounded reviewed JSON Pointer extracts and exact binding IDs.
- [x] Fail closed on duplicate IDs, wrong kind/format, stale binding hash, changed source hash, unsafe paths, symlinks, missing pointers and oversized extracts.
- [x] Perform no client/OTBM parsing, semantic reinterpretation, fuzzy selection, mutation, E2E execution, acceptance or routing decision.
- [x] Add deterministic plan/execution, schema and output-safety tests.
- [x] Reconcile programme, catalogue and changelog.
- [ ] Pass exact-final-head CI, merge and archive.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T09:10:00+02:00
head: 193428b3e6a42308ceb684cf271b568609de4aeb
branch: feat/CAN-20260730-tcr-010-evidence-gateway
pr: 1027
status: ready
context_routes:
  - agent-governance
  - otbm
  - real-tibia-parity
owned_paths:
  - tools/ai-agent/tibia_client_reference_evidence_gateway.py
  - tools/ai-agent/tibia_client_reference_evidence_gateway_tool.py
  - tools/ai-agent/test_tibia_client_reference_evidence_gateway.py
  - tools/ai-agent/test_tibia_client_reference_evidence_gateway_output_safety.py
  - tools/ai-agent/test_tibia_client_reference_evidence_gateway_schema.py
  - docs/ai-agent/TIBIA_CLIENT_REFERENCE_EVIDENCE_GATEWAY.md
  - docs/ai-agent/TIBIA_CLIENT_REFERENCE_EVIDENCE_BINDINGS.schema.json
  - docs/ai-agent/TIBIA_CLIENT_REFERENCE_EVIDENCE_GATEWAY.schema.json
  - .github/workflows/tibia-client-reference-evidence-gateway.yml
proven:
  - TCR-009 and QA-018 dependencies are stable and reused without modification.
  - Exact reviewed binding IDs support one bounded house, content, proficiency or drift source.
  - QA-018 exclusively enforces source path, SHA-256, format, pointer and serialized-size constraints.
  - Plan and execution are deterministic and pin both raw and canonical binding hashes.
  - Direct and CLI output paths reject symlinks, symlink parents, escapes and input/source collisions.
  - Dedicated schema validation passed with jsonschema; the repository-wide stdlib suite safely skips only the optional Draft 2020-12 runtime validation when that package is absent.
  - Nineteen focused tests and canonical QA-018 regression tests pass.
  - Programme, module catalogue and changelog reflect TCR-009 stable and TCR-010 in review.
  - Exact head 193428b3e6a42308ceb684cf271b568609de4aeb passed TCR-010, TCR-009 regression, Agent Task Ownership, AI Agent Tools, Universal E2E Stability and full CI.
derived:
  - Stable TCR reports can be exposed as compact reviewed evidence without expanding parser, assurance or mutation ownership.
unknown:
  - Exact final checkpoint commit SHA and its final-gate workflow results.
conflicts: []
first_failure:
  marker: TCR010_SCHEMA_AND_GLOBAL_SUITE_COMPATIBILITY
  evidence: The first dedicated run exposed a truncated schema JSON; the first global AI Agent Tools run exposed an unconditional optional jsonschema import. Both root causes were repaired and the exact implementation head is green.
rejected_hypotheses:
  - Add a second generic evidence gateway or parser.
  - Search source reports by fuzzy content or inferred identifiers.
  - Grant acceptance, adoption-routing, E2E or mutation authority.
changed_paths:
  - .github/workflows/tibia-client-reference-evidence-gateway.yml
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260730-tcr-010-evidence-gateway.md
  - docs/ai-agent/TIBIA_CLIENT_REFERENCE_EVIDENCE_BINDINGS.schema.json
  - docs/ai-agent/TIBIA_CLIENT_REFERENCE_EVIDENCE_GATEWAY.md
  - docs/ai-agent/TIBIA_CLIENT_REFERENCE_EVIDENCE_GATEWAY.schema.json
  - tools/ai-agent/test_tibia_client_reference_evidence_gateway.py
  - tools/ai-agent/test_tibia_client_reference_evidence_gateway_output_safety.py
  - tools/ai-agent/test_tibia_client_reference_evidence_gateway_schema.py
  - tools/ai-agent/tibia_client_reference_evidence_gateway.py
  - tools/ai-agent/tibia_client_reference_evidence_gateway_tool.py
validation:
  - command: focused TCR-010 plus QA-018 regression suites
    result: PASS
    evidence: 19 TCR-010 tests and all canonical QA-018 tests passed.
  - command: exact implementation-head workflow set
    result: PASS
    evidence: runs 30521828020, 30521828043, 30521828080, 30521828086, 30521828103 and 30521828260 succeeded on 193428b3e6a42308ceb684cf271b568609de4aeb.
blockers: []
next_action: verify the full ci:final-gate workflow set on this checkpoint commit, inspect reviews and base drift, mark PR ready, verify the readiness-triggered gate, and squash-merge.
```
