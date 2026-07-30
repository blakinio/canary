---
task_id: CAN-20260730-tcr-011-adoption-router
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: TCR-011
status: implementing
agent: chatgpt
branch: feat/CAN-20260730-tcr-011-adoption-router
base_branch: main
created: 2026-07-30T10:30:00+02:00
updated: 2026-07-30T10:30:00+02:00
last_verified_commit: "4b2d6f432d92628c42bde1d95daed6ae0d0eb88f"
risk: medium
related_issue: ""
related_pr: ""
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

- [ ] Require an executed `canary-tibia-client-reference-evidence-gateway-v1` report with valid canonical hashes.
- [ ] Pin every route to exact binding ID, kind, extract ID, source ID, JSON Pointer and extract value SHA-256.
- [ ] Permit only fixed existing owner/capability pairs appropriate to `house`, `content`, `proficiency` and `drift` evidence.
- [ ] Route map-affecting work only to the existing OTBM Repair Recommendation capability; never directly to a writer/materializer.
- [ ] Preserve `unsupported` and `blocked` outcomes without expanding a writer or inventing a target state.
- [ ] Reject duplicate routes, stale report/request hashes, missing extracts, cross-kind owner/capability pairs and unreviewed free-form capabilities.
- [ ] Generate no approval, mutation request, writer execution, deployment, E2E or gameplay claim.
- [ ] Add deterministic core, CLI, schema, output-safety and exact-head workflow evidence.
- [ ] Reconcile programme, module catalogue and changelog.

# Design boundary

The request is reviewer-authored and exact-hash pinned. The router does not infer the route from names, numeric IDs, source proximity or free-form source semantics. A routed result means only that an existing owner/capability is the correct next review boundary. It does not mean the finding is a defect, technically supported by a writer, approved, implemented or gameplay-correct.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T10:30:00+02:00
head: 4b2d6f432d92628c42bde1d95daed6ae0d0eb88f
branch: feat/CAN-20260730-tcr-011-adoption-router
pr: none
status: implementing
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
  - docs/ai-agent/TIBIA_REFERENCE_ADOPTION_ROUTER.md
  - docs/ai-agent/TIBIA_REFERENCE_ADOPTION_ROUTING_REQUEST.schema.json
  - docs/ai-agent/TIBIA_REFERENCE_ADOPTION_ROUTING.schema.json
  - .github/workflows/tibia-reference-adoption-router.yml
  - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - TCR-005, TCR-006, TCR-007, TCR-009 and TCR-010 are stable/merged on main 4b2d6f432d92628c42bde1d95daed6ae0d0eb88f.
  - No open TCR-011 issue, branch or PR existed at preflight; no open PR overlaps the exclusive paths.
  - OTBM-QA-003 is the existing review-only classifier for supported map repair/materialization families and does not generate approval or execute writers.
derived:
  - TCR-011 should route map-affecting evidence to QA-003 rather than duplicate its capability classification or address writers directly.
unknown:
  - Exact final implementation head and workflow evidence are not yet available.
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - TCR-011 should derive mutation targets from TCR fragments: rejected because TCR-005/006/007/009/010 preserve review evidence and grant no target-state or mutation authority.
changed_paths:
  - docs/agents/tasks/active/CAN-20260730-tcr-011-adoption-router.md
validation:
  - command: repository and ownership preflight
    result: PASS
    evidence: main 4b2d6f432d92628c42bde1d95daed6ae0d0eb88f; no TCR-011 branch/PR/task or overlapping open PR found before branch creation.
blockers: []
next_action: Create the early draft PR, then implement the exact reviewed request and routing report contracts without adding parser, writer, approval or execution authority.
```
