---
task_id: CAN-20260730-tcr-010-evidence-gateway
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: TCR-010
status: merged
agent: chatgpt
branch: main
base_branch: main
created: 2026-07-30T08:14:00+02:00
updated: 2026-07-30T09:45:00+02:00
last_verified_commit: "34a2a3750f20c318ecc07aa7407ca0b9a9311834"
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
    - docs/agents/tasks/archive/CAN-20260730-tcr-010-evidence-gateway.md
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
- [x] Pass exact-final-head CI, merge and archive.

# Feature result

- Feature PR: `#1027`.
- Exact final head: `38826ff475c4631ee42c7fd8dc2e246dedab2a25`.
- Squash merge: `34a2a3750f20c318ecc07aa7407ca0b9a9311834`.
- Readiness/final-gate CI: run `30522402785`, conclusion `success` including Linux release/debug, Docker image/quickstart and `Required`.
- Public formats: `canary-tibia-client-reference-evidence-bindings-v1` and `canary-tibia-client-reference-evidence-gateway-v1`.
- Focused suite: 19 tests; canonical QA-018 regression suite passed.
- No proprietary input/report, OTBM, datapack, runtime, E2E, acceptance or mutation authority was added.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T09:45:00+02:00
head: 34a2a3750f20c318ecc07aa7407ca0b9a9311834
branch: main
pr: 1027
status: merged
context_routes:
  - agent-governance
  - otbm
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/archive/CAN-20260730-tcr-010-evidence-gateway.md
  - tools/ai-agent/tibia_client_reference_evidence_gateway.py
  - tools/ai-agent/tibia_client_reference_evidence_gateway_tool.py
  - docs/ai-agent/TIBIA_CLIENT_REFERENCE_EVIDENCE_GATEWAY.md
proven:
  - Exact reviewed house, content, proficiency and drift bindings delegate extraction to canonical QA-018.
  - Paths, SHA-256, formats, pointers, extract bounds and output confinement fail closed.
  - Feature head 38826ff475c4631ee42c7fd8dc2e246dedab2a25 and readiness run 30522402785 passed all required checks.
  - PR 1027 squash-merged as 34a2a3750f20c318ecc07aa7407ca0b9a9311834 with no reviews, comments, threads or base drift.
derived:
  - TCR-011 is dependency-ready but remains a separate read-only routing package.
unknown: []
conflicts: []
first_failure:
  marker: TCR010_SCHEMA_AND_GLOBAL_SUITE_COMPATIBILITY
  evidence: Truncated schema and optional jsonschema import failures were repaired before final gate.
rejected_hypotheses:
  - Add a second parser or generic evidence gateway.
  - Grant acceptance, E2E, routing execution or mutation authority.
changed_paths:
  - docs/agents/tasks/archive/CAN-20260730-tcr-010-evidence-gateway.md
  - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
  - docs/agents/MODULE_CATALOG.md
validation:
  - command: readiness and ci:final-gate run 30522402785
    result: PASS
    evidence: Linux release/debug, Docker image/quickstart and Required completed success on 38826ff475c4631ee42c7fd8dc2e246dedab2a25.
blockers: []
next_action: Start one bounded TCR-011 Reviewed Adoption Router task; do not implement OWA-003 before TCR-011 is stable/merged.
```
