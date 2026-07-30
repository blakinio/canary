---
task_id: CAN-20260730-tcr-011-adoption-router
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: TCR-011
status: ready
agent: chatgpt
branch: feat/CAN-20260730-tcr-011-adoption-router
base_branch: main
created: 2026-07-30T10:30:00+02:00
updated: 2026-07-30T11:15:00+02:00
last_verified_commit: "b2e40a6997ad90b2cef74e534e648f57435f96a8"
risk: medium
related_issue: ""
related_pr: "1029"
depends_on:
  - TCR-005 stable canary-otbm-house-reference-parity-v1
  - TCR-006 stable canary-tibia-content-reference-correlation-v1
  - TCR-007 stable canary-tibia-proficiency-reference-correlation-v1
  - TCR-009 stable canary-tibia-client-reference-drift-v1
  - TCR-010 stable canary-tibia-client-reference-evidence-gateway-v1
blocks:
  - OWA-003
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260730-tcr-011-adoption-router.md
    - tools/ai-agent/tibia_reference_adoption_router.py
    - tools/ai-agent/tibia_reference_adoption_router_tool.py
    - tools/ai-agent/test_tibia_reference_adoption_router.py
    - tools/ai-agent/test_tibia_reference_adoption_router_output_safety.py
    - tools/ai-agent/test_tibia_reference_adoption_router_schema.py
    - docs/ai-agent/TIBIA_REFERENCE_ADOPTION_ROUTER.md
    - docs/ai-agent/TIBIA_REFERENCE_ADOPTION_ROUTING_REQUEST.schema.json
    - docs/ai-agent/TIBIA_REFERENCE_ADOPTION_ROUTING.schema.json
    - .github/workflows/tibia-reference-adoption-router.yml
  shared:
    - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/tibia_client_reference_evidence_gateway.py
    - tools/ai-agent/otbm_repair_recommendation.py
    - exact retained TCR-005, TCR-006, TCR-007, TCR-009 and TCR-010 reports outside Git
modules_touched:
  - OTBM Tibia client reference architecture
  - Tibia reference adoption router
reuses:
  - canary-tibia-client-reference-evidence-gateway-v1
  - canary-otbm-repair-recommendation-v1
  - existing Achievement, Cyclopedia, Spawn/Boss/NPC, Quest/Storage and Weapon Proficiency owners
public_interfaces:
  - canary-tibia-reference-adoption-routing-request-v1
  - canary-tibia-reference-adoption-routing-v1
cross_repo_tasks: []
---

# Goal

Add the smallest deterministic read-only TCR-011 router that consumes one exact executed TCR-010 report plus one explicit reviewed routing request and classifies each selected extract to an existing owner/capability or an explicit unsupported outcome.

# Acceptance criteria

- [x] Require an executed `canary-tibia-client-reference-evidence-gateway-v1` report with valid canonical hashes.
- [x] Pin every route to exact binding ID, kind, extract ID, source ID, JSON Pointer and extract value SHA-256.
- [x] Permit only fixed existing owner/capability pairs appropriate to `house`, `content`, `proficiency` and `drift` evidence.
- [x] Route map-affecting work only to the existing OTBM Repair Recommendation capability; never directly to a writer/materializer.
- [x] Preserve `unsupported` and `blocked` outcomes without expanding a writer or inventing a target state.
- [x] Reject duplicate routes, stale report/request hashes, missing extracts, cross-kind owner/capability pairs and unreviewed free-form capabilities.
- [x] Generate no approval, mutation request, writer execution, deployment, E2E or gameplay claim.
- [x] Add deterministic core, CLI, schema, output-safety and schema-inventory evidence.
- [x] Reconcile programme, module catalogue and changelog.
- [ ] Pass exact-final-head workflow evidence and merge.

# Design boundary

The request is reviewer-authored and exact-hash pinned. The router does not infer the route from names, numeric IDs, source proximity or free-form source semantics. A routed result means only that an existing owner/capability is the correct next review boundary. It does not mean the finding is a defect, technically supported by a writer, approved, implemented or gameplay-correct.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T11:15:00+02:00
head: b2e40a6997ad90b2cef74e534e648f57435f96a8
branch: feat/CAN-20260730-tcr-011-adoption-router
pr: 1029
status: ready
context_routes:
  - agent-governance
  - otbm
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260730-tcr-011-adoption-router.md
  - tools/ai-agent/tibia_reference_adoption_router.py
  - tools/ai-agent/tibia_reference_adoption_router_tool.py
  - tools/ai-agent/test_tibia_reference_adoption_router.py
  - tools/ai-agent/test_tibia_reference_adoption_router_output_safety.py
  - tools/ai-agent/test_tibia_reference_adoption_router_schema.py
  - docs/ai-agent/TIBIA_REFERENCE_ADOPTION_ROUTER.md
  - docs/ai-agent/TIBIA_REFERENCE_ADOPTION_ROUTING_REQUEST.schema.json
  - docs/ai-agent/TIBIA_REFERENCE_ADOPTION_ROUTING.schema.json
  - .github/workflows/tibia-reference-adoption-router.yml
  - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - TCR-005, TCR-006, TCR-007, TCR-009 and TCR-010 are stable/merged on main 4b2d6f432d92628c42bde1d95daed6ae0d0eb88f.
  - PR 1029 exists on the dedicated branch, carries ci:final-gate and no open PR overlaps the exclusive paths.
  - OTBM-QA-003 remains the sole supported map-repair capability classifier; TCR-011 never addresses writers/materializers directly.
  - The router validates the exact executed gateway report and embedded evidence bundle hashes, covers every extract exactly once and binds file hashes to the same bytes parsed by the CLI.
  - The fixed code/schema target inventory excludes direct Phase 8 and area-materializer writer capabilities.
  - Programme, module catalogue and changelog describe TCR-011 as active/in-review without promoting it to stable before merge.
  - On parent head b2e40a6997ad90b2cef74e534e648f57435f96a8, CI 30529582618, TCR drift 30529582207 and TCR evidence gateway 30529582231 passed.
derived:
  - The bounded implementation and documentation package is complete; the current commit must pass the exact-final-head gate before readiness and merge.
unknown:
  - Exact current-head workflow conclusions and squash-merge SHA are not yet available.
conflicts: []
first_failure:
  marker: Agent Task Ownership / active-task frontmatter status
  evidence: run 30529582329 job 90828462746 rejected status validating in tasks/active; corrected to ready in this final checkpoint commit.
rejected_hypotheses:
  - TCR-011 should derive mutation targets from TCR fragments: rejected because TCR-005/006/007/009/010 preserve review evidence and grant no target-state or mutation authority.
  - The first CI failure indicates a router implementation defect: rejected because the dedicated router, CI and AI Agent Tools workflows passed; only task related_pr metadata failed.
  - Parsing and hashing inputs in separate reads is sufficient: rejected because a path could change between reads; the CLI now hashes the exact bytes it parsed and rejects non-finite JSON numbers.
  - Frontmatter validating is an active-task status: rejected by Agent Task Ownership run 30529582329; active task readiness uses status ready while the checkpoint retains exact validation state.
changed_paths:
  - docs/agents/tasks/active/CAN-20260730-tcr-011-adoption-router.md
  - tools/ai-agent/tibia_reference_adoption_router.py
  - tools/ai-agent/tibia_reference_adoption_router_tool.py
  - tools/ai-agent/test_tibia_reference_adoption_router.py
  - tools/ai-agent/test_tibia_reference_adoption_router_output_safety.py
  - tools/ai-agent/test_tibia_reference_adoption_router_schema.py
  - docs/ai-agent/TIBIA_REFERENCE_ADOPTION_ROUTER.md
  - docs/ai-agent/TIBIA_REFERENCE_ADOPTION_ROUTING_REQUEST.schema.json
  - docs/ai-agent/TIBIA_REFERENCE_ADOPTION_ROUTING.schema.json
  - .github/workflows/tibia-reference-adoption-router.yml
  - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
validation:
  - command: focused router tests, schema validation, Python compilation and CLI smoke
    result: PASS
    evidence: Tibia Reference Adoption Router run 30529402211 completed the implementation and exact-input hardening package successfully.
  - command: CI
    result: PASS
    evidence: run 30529582618 on parent b2e40a6997ad90b2cef74e534e648f57435f96a8.
  - command: TCR drift and evidence gateway compatibility
    result: PASS
    evidence: runs 30529582207 and 30529582231 on parent b2e40a6997ad90b2cef74e534e648f57435f96a8.
  - command: exact-final-head workflow set
    result: NOT_RUN
    evidence: this final checkpoint commit must emit and pass the full ci:final-gate workflow set before merge.
blockers: []
next_action: Verify every required workflow on the exact current head, then mark PR 1029 ready and squash-merge without creating another commit.
```
