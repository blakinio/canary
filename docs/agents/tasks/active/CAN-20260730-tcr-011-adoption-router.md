---
task_id: CAN-20260730-tcr-011-adoption-router
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: TCR-011
status: validating
agent: chatgpt
branch: feat/CAN-20260730-tcr-011-adoption-router
base_branch: main
created: 2026-07-30T10:30:00+02:00
updated: 2026-07-30T11:10:00+02:00
last_verified_commit: "3d46961067d8e43dd78a5e0811d50046288bb7ca"
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
updated_at: 2026-07-30T11:10:00+02:00
head: 3d46961067d8e43dd78a5e0811d50046288bb7ca
branch: feat/CAN-20260730-tcr-011-adoption-router
pr: 1029
status: validating
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
  - PR 1029 exists on the dedicated branch and no open PR overlaps the exclusive paths.
  - OTBM-QA-003 remains the sole supported map-repair capability classifier; TCR-011 never addresses writers/materializers directly.
  - The router validates the exact executed gateway report and embedded evidence bundle hashes, covers every extract exactly once and binds file hashes to the same bytes parsed by the CLI.
  - The fixed code/schema target inventory excludes direct Phase 8 and area-materializer writer capabilities.
  - Programme, module catalogue and changelog describe TCR-011 as active/in-review without promoting it to stable before merge.
derived:
  - The bounded implementation and documentation package is complete; only final-gate evidence, readiness and merge remain.
unknown:
  - Exact final implementation head and final-gate workflow evidence are not yet available.
conflicts: []
first_failure:
  marker: Agent Task Ownership / Validate changed active task checkpoints
  evidence: run 30528225261 job 90824075575; related_pr was empty while the current PR is 1029.
rejected_hypotheses:
  - TCR-011 should derive mutation targets from TCR fragments: rejected because TCR-005/006/007/009/010 preserve review evidence and grant no target-state or mutation authority.
  - The first CI failure indicates a router implementation defect: rejected because the dedicated router, CI and AI Agent Tools workflows passed; only task related_pr metadata failed.
  - Parsing and hashing inputs in separate reads is sufficient: rejected because a path could change between reads; the CLI now hashes the exact bytes it parsed and rejects non-finite JSON numbers.
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
  - command: Tibia Reference Adoption Router workflow
    result: PASS
    evidence: run 30528222169 on 8845e58e1bb18340ad1eaa52b22c49d858fee1f3; later exact-head validation pending.
  - command: CI
    result: PASS
    evidence: run 30528222229 on 8845e58e1bb18340ad1eaa52b22c49d858fee1f3; later exact-head validation pending.
  - command: AI Agent Tools
    result: PASS
    evidence: run 30528221999 on 8845e58e1bb18340ad1eaa52b22c49d858fee1f3; later exact-head validation pending.
  - command: Agent Task Ownership
    result: PASS
    evidence: run 30529014358 after related_pr correction; later exact-head validation pending.
blockers: []
next_action: Apply the ci:final-gate label, write one final checkpoint commit with its exact parent evidence, then make no further commits before merge.
```
